# Molecular Geometry Layer v1

Three-module foundation for the QuantumSonification Natural Geometry Library.

## Files
- `spectral_geometry_packet_v1.py` — common NPZ/JSON interchange format.
- `molecular_geometry_layer_v1.py` — curated molecular geometries and mass-weighted graph spectra.
- `molecular_geometry_osc_v1.py` — live OSC output; control 7440, output 7441.

## Dependencies
`numpy`; OSC bridge additionally requires `python-osc`.

## Generate methane
```bash
python molecular_geometry_layer_v1.py --molecule methane --output methane_molecular_spectrum_v1.npz --json methane_molecular_spectrum_v1.json
```
The NPZ is directly readable by `quantum_eigenfield_engine_v1.py` because it includes column-oriented `eigenvectors` plus `eigenvalues`.

## OSC
```bash
python molecular_geometry_osc_v1.py --molecule methane --out-port 7441
```
Control messages include `/molecular/set water`, `/molecular/base_frequency 55`, `/molecular/distance_power 1`, `/molecular/mass_weighted 1`, `/molecular/normalized 0`, `/molecular/send 1`, and `/molecular/quit 1`.

## PubChem molecular loader v1

`pubchem_molecular_loader_v1.py` imports real PubChem Compound records through PUG REST and converts them to `MolecularGeometry` and `SpectralGeometryPacket` objects.

Examples:

```bash
python pubchem_molecular_loader_v1.py --name caffeine \
  --output caffeine_spectrum_v1.npz \
  --json caffeine_spectrum_v1.json

python pubchem_molecular_loader_v1.py --cid 2519 --output caffeine_cid2519.npz
python pubchem_molecular_loader_v1.py --smiles "c1ccccc1" --output benzene_from_smiles.npz
```

The loader requests a PubChem 3D record first and can fall back to a 2D record. Raw responses are cached in `pubchem_cache/` to make repeated runs deterministic and reduce API traffic. Use `--refresh` to retrieve a fresh record or `--no-2d-fallback` to require 3D coordinates.

Each packet records provenance, CID, query, coordinate dimension, coordinate units, retrieval time, and cache path. PubChem coordinates should be understood as database conformers rather than automatically equated with experimentally measured equilibrium geometries.

The molecular layer now recognizes common elements through krypton plus iodine, covering typical organic, biomolecular, and many inorganic structures. Unsupported elements produce an explicit error rather than a silent mass approximation.
