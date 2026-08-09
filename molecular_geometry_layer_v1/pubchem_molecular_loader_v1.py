#!/usr/bin/env python3
"""PubChem molecular loader v1 for the QuantumSonification geometry pipeline.

Downloads a PubChem Compound record through PUG REST, extracts a conformer,
converts it to MolecularGeometry, and optionally exports a SpectralGeometryPacket.
Only the Python standard library and NumPy are required.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import numpy as np

from molecular_geometry_layer_v1 import (
    ATOMIC_DATA,
    MolecularGeometry,
    molecule_to_packet,
)

PUG_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
USER_AGENT = "QuantumSonification-PubChemLoader/1.0"
ELEMENT_BY_Z = {number: symbol for symbol, (number, _mass) in ATOMIC_DATA.items()}


@dataclass(frozen=True)
class PubChemQuery:
    namespace: str
    value: str

    def __post_init__(self) -> None:
        if self.namespace not in {"name", "cid", "smiles"}:
            raise ValueError("namespace must be name, cid, or smiles")
        if not str(self.value).strip():
            raise ValueError("query value cannot be empty")

    @property
    def slug(self) -> str:
        clean = re.sub(r"[^A-Za-z0-9._-]+", "_", str(self.value)).strip("_")[:60]
        digest = hashlib.sha1(f"{self.namespace}:{self.value}".encode()).hexdigest()[:10]
        return f"{self.namespace}_{clean or 'query'}_{digest}"


def build_record_url(query: PubChemQuery, record_type: str = "3d") -> str:
    encoded = quote(str(query.value), safe="" if query.namespace != "smiles" else "")
    return f"{PUG_BASE}/compound/{query.namespace}/{encoded}/JSON?record_type={record_type}"


def fetch_json(url: str, timeout: float = 30.0, retries: int = 3) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries):
        req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last_error = exc
            if exc.code in {400, 404}:
                raise RuntimeError(f"PubChem did not find a matching compound ({exc.code}).") from exc
            if exc.code not in {429, 500, 502, 503, 504}:
                raise RuntimeError(f"PubChem request failed with HTTP {exc.code}.") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
        if attempt + 1 < retries:
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Unable to retrieve PubChem data after {retries} attempts: {last_error}")


def _first_compound(record: dict[str, Any]) -> dict[str, Any]:
    compounds = record.get("PC_Compounds", [])
    if not compounds:
        raise ValueError("PubChem response contains no PC_Compounds records")
    return compounds[0]


def _cid(compound: dict[str, Any]) -> int | None:
    try:
        return int(compound["id"]["id"]["cid"])
    except (KeyError, TypeError, ValueError):
        return None


def _coordinates(compound: dict[str, Any], atom_ids: list[int]) -> tuple[np.ndarray, str, dict[str, Any]]:
    coords_blocks = compound.get("coords", [])
    if not coords_blocks:
        raise ValueError("PubChem record has no coordinate block")
    block = coords_blocks[0]
    conformers = block.get("conformers", [])
    if not conformers:
        raise ValueError("PubChem coordinate block has no conformers")
    conformer = conformers[0]
    x = np.asarray(conformer.get("x", []), dtype=float)
    y = np.asarray(conformer.get("y", []), dtype=float)
    z_values = conformer.get("z")
    coordinate_type = "3d" if z_values is not None and len(z_values) == len(x) else "2d"
    z = np.asarray(z_values if coordinate_type == "3d" else np.zeros_like(x), dtype=float)
    coord_ids = list(block.get("aid", atom_ids))
    if not (len(x) == len(y) == len(z) == len(coord_ids)):
        raise ValueError("coordinate array lengths do not match atom IDs")
    by_id = {int(aid): np.array([xv, yv, zv], float) for aid, xv, yv, zv in zip(coord_ids, x, y, z)}
    try:
        positions = np.vstack([by_id[int(aid)] for aid in atom_ids])
    except KeyError as exc:
        raise ValueError(f"missing coordinates for atom ID {exc.args[0]}") from exc
    conformer_meta = {k: v for k, v in conformer.items() if k not in {"x", "y", "z"}}
    return positions, coordinate_type, conformer_meta


def pubchem_record_to_molecule(record: dict[str, Any], query: PubChemQuery | None = None) -> MolecularGeometry:
    compound = _first_compound(record)
    atoms = compound.get("atoms", {})
    atom_ids = [int(v) for v in atoms.get("aid", [])]
    atomic_numbers = [int(v) for v in atoms.get("element", [])]
    if not atom_ids or len(atom_ids) != len(atomic_numbers):
        raise ValueError("invalid or missing PubChem atom table")
    try:
        elements = [ELEMENT_BY_Z[z] for z in atomic_numbers]
    except KeyError as exc:
        raise ValueError(f"element with atomic number {exc.args[0]} is not yet supported") from exc
    positions, coordinate_type, conformer_meta = _coordinates(compound, atom_ids)
    atom_index = {aid: index for index, aid in enumerate(atom_ids)}
    bond_block = compound.get("bonds", {})
    aid1 = bond_block.get("aid1", [])
    aid2 = bond_block.get("aid2", [])
    orders = bond_block.get("order", [1] * len(aid1))
    if not (len(aid1) == len(aid2) == len(orders)):
        raise ValueError("invalid PubChem bond table")
    bonds = np.array([[atom_index[int(a)], atom_index[int(b)]] for a, b in zip(aid1, aid2)], dtype=int)
    bond_orders = np.asarray(orders, dtype=float)

    charges = np.zeros(len(elements), dtype=float)
    for charge_entry in atoms.get("charge", []) or []:
        aid = int(charge_entry.get("aid", -1))
        if aid in atom_index:
            charges[atom_index[aid]] = float(charge_entry.get("value", 0.0))

    cid = _cid(compound)
    title = f"pubchem_cid_{cid}" if cid is not None else "pubchem_compound"
    metadata = {
        "source": "PubChem PUG REST",
        "source_id": f"CID:{cid}" if cid is not None else "unknown",
        "pubchem_cid": cid,
        "query_namespace": query.namespace if query else None,
        "query_value": query.value if query else None,
        "structure_type": f"PubChem {coordinate_type.upper()} conformer",
        "coordinate_dimension": coordinate_type,
        "coordinate_units": "angstrom",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "conformer_metadata": conformer_meta,
        "atomic_numbers": atomic_numbers,
    }
    return MolecularGeometry(title, elements, positions, bonds, bond_orders, charges=charges, metadata=metadata)


def load_pubchem_molecule(
    query: PubChemQuery,
    cache_dir: str | Path = "pubchem_cache",
    use_cache: bool = True,
    refresh: bool = False,
    allow_2d_fallback: bool = True,
    timeout: float = 30.0,
) -> MolecularGeometry:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{query.slug}_3d.json"
    record: dict[str, Any]
    if use_cache and cache_path.exists() and not refresh:
        record = json.loads(cache_path.read_text())
    else:
        try:
            record = fetch_json(build_record_url(query, "3d"), timeout=timeout)
        except RuntimeError:
            if not allow_2d_fallback:
                raise
            record = fetch_json(build_record_url(query, "2d"), timeout=timeout)
            cache_path = cache_dir / f"{query.slug}_2d.json"
        cache_path.write_text(json.dumps(record, indent=2))
    molecule = pubchem_record_to_molecule(record, query)
    molecule.metadata["cache_file"] = str(cache_path)
    return molecule


def main() -> None:
    parser = argparse.ArgumentParser(description="Load a real molecular structure from PubChem.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--name")
    group.add_argument("--cid")
    group.add_argument("--smiles")
    parser.add_argument("--cache-dir", default="pubchem_cache")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--no-2d-fallback", action="store_true")
    parser.add_argument("--output", help="Output SpectralGeometryPacket NPZ")
    parser.add_argument("--json", help="Optional packet JSON output")
    parser.add_argument("--modes", type=int)
    parser.add_argument("--base-frequency", type=float, default=55.0)
    parser.add_argument("--distance-power", type=float, default=1.0)
    parser.add_argument("--unweighted", action="store_true")
    parser.add_argument("--normalized", action="store_true")
    args = parser.parse_args()

    if args.name is not None:
        query = PubChemQuery("name", args.name)
    elif args.cid is not None:
        query = PubChemQuery("cid", args.cid)
    else:
        query = PubChemQuery("smiles", args.smiles)

    molecule = load_pubchem_molecule(
        query,
        cache_dir=args.cache_dir,
        refresh=args.refresh,
        allow_2d_fallback=not args.no_2d_fallback,
    )
    packet = molecule_to_packet(
        molecule,
        n_modes=args.modes,
        base_frequency_hz=args.base_frequency,
        distance_power=args.distance_power,
        mass_weighted=not args.unweighted,
        normalized=args.normalized,
    )
    packet.metadata.update(molecule.metadata)
    output = args.output or f"{query.slug}_spectrum_v1.npz"
    packet.save_npz(output)
    if args.json:
        packet.save_json(args.json, include_eigenvectors=True)

    print("PubChem Molecular Loader v1")
    print(f"  query:          {query.namespace}={query.value}")
    print(f"  source:         {molecule.metadata.get('source_id')}")
    print(f"  coordinates:    {molecule.metadata.get('coordinate_dimension')}")
    print(f"  atoms/bonds:    {len(molecule.elements)}/{len(molecule.bonds)}")
    print(f"  elements:       {' '.join(sorted(set(molecule.elements)))}")
    print(f"  modes:          {packet.n_modes}")
    print(f"  spectral gap:   {packet.metadata['spectral_gap']:.6f}")
    print(f"  packet:         {output}")


if __name__ == "__main__":
    main()
