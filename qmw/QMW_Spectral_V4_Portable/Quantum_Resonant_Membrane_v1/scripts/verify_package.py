#!/usr/bin/env python3
"""Verify integrity, imports, tests, and a bounded in-process engine run."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def verify_manifest() -> None:
    manifest = ROOT / "MANIFEST.sha256"
    if not manifest.exists():
        print("manifest: absent (integrity check skipped)")
        return
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"manifest file is missing: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"manifest mismatch: {relative}")
        checked += 1
    print(f"manifest: {checked} files verified")


def main() -> int:
    verify_manifest()
    from quantum_resonant_membrane.engine import QuantumResonantMembraneEngine

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    engine = QuantumResonantMembraneEngine(modes=20)
    for _ in range(60):
        frame = engine.step(1.0 / 120.0)
    assert frame.density.rho.shape == (4, 4)
    assert len(frame.membrane.modal_amplitudes) == 20
    print("engine smoke: 60 frames passed")
    print("package verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
