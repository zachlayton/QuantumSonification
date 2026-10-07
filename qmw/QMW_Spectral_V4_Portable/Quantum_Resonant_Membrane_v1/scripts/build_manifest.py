#!/usr/bin/env python3
"""Build deterministic SHA-256 hashes without including machine-local files."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MANIFEST.sha256"
EXCLUDED_PARTS = {".git", ".venv", ".pytest_cache", "__pycache__"}
EXCLUDED_NAMES = {OUTPUT.name, ".DS_Store"}


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return (
        path.is_file()
        and not any(part in EXCLUDED_PARTS for part in relative.parts)
        and path.name not in EXCLUDED_NAMES
        and not (relative.parts[:1] == ("presets",) and path.suffix == ".archive")
        and path.suffix not in {".pyc", ".pyo"}
    )


def main() -> int:
    lines = []
    for path in sorted(path for path in ROOT.rglob("*") if included(path)):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.name} with {len(lines)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
