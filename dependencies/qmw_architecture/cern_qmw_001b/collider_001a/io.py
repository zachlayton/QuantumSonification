"""JSON adapter and a loader protocol for a later explicit ROOT branch mapping."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Protocol

from .model import (SCHEMA_VERSION, UNITS, ColliderDataset, ColliderEvent,
                    FourMomentum, Provenance)


class EventLoader(Protocol):
    """Adapters normalize source units/selection, retaining source entry indices."""

    def load(self, path: str | Path) -> ColliderDataset: ...


def _reject_constant(value):
    raise ValueError(f"non-finite JSON value: {value}")


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


class JsonEventLoader:
    def load(self, path: str | Path) -> ColliderDataset:
        path = Path(path).resolve()
        raw = path.read_bytes()
        try:
            obj = json.loads(raw, parse_constant=_reject_constant,
                             object_pairs_hook=_unique_object)
            if set(obj) != {"schema_version", "units", "provenance", "events"}:
                raise ValueError("expected schema_version, units, provenance, events")
            if obj["schema_version"] != SCHEMA_VERSION:
                raise ValueError(f"unsupported schema_version: {obj['schema_version']}")
            if obj["units"] != UNITS:
                raise ValueError(f"units must be explicitly normalized to {UNITS}")
            provenance = Provenance(**obj["provenance"])
            if not isinstance(obj["events"], list):
                raise ValueError("events must be a list")
            events = []
            for index, row in enumerate(obj["events"]):
                try:
                    values = dict(row)
                    for name in ("top", "antitop"):
                        if values.get(name) is not None:
                            values[name] = FourMomentum(**values[name])
                    events.append(ColliderEvent(**values))
                except (TypeError, ValueError, OverflowError) as exc:
                    raise ValueError(f"event row {index}: {exc}") from exc
            return ColliderDataset(provenance, tuple(events), str(path),
                                   hashlib.sha256(raw).hexdigest())
        except (TypeError, ValueError, KeyError, OverflowError) as exc:
            raise ValueError(f"invalid dataset {path.name}: {exc}") from exc


def save_dataset(dataset: ColliderDataset, path: str | Path) -> Path:
    path = Path(path)
    payload = {"schema_version": SCHEMA_VERSION, "units": dict(UNITS),
               "provenance": asdict(dataset.provenance),
               "events": [asdict(event) for event in dataset.events]}
    content = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")
    return path


def load_dataset(path: str | Path, loader: EventLoader | None = None) -> ColliderDataset:
    if loader is not None:
        return loader.load(path)
    if Path(path).suffix.lower() != ".json":
        raise ValueError("001A accepts normalized .json datasets. A ROOT/uproot adapter "
                         "must supply an explicit branch map, units and selection via EventLoader.")
    return JsonEventLoader().load(path)
