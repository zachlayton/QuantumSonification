"""Run silent availability checks against the installed legacy VNF adapter.

The script compiles the addon without executing it. Control senders, frames and
views are explicit in-memory test fixtures; no running instrument is contacted.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'worktrees/qmw-v3-runtime/Quantum_Resonant_Membrane_v1/supercollider'
SCLANG = Path('/Applications/SuperCollider.app/Contents/MacOS/sclang')
STARTUP = Path.home() / 'Library/Application Support/SuperCollider/startup.scd'
EXPECTED_STARTUP = 'f9107b86b8fb8ef92dc61eda35e86949f2bcb800c20697b80508773a7194e28c'


def main():
    if not STARTUP.is_file() or hashlib.sha256(STARTUP.read_bytes()).hexdigest() != EXPECTED_STARTUP:
        raise SystemExit('Review the changed host startup before running this silent language test.')
    for folder in [STARTUP.parent, Path('/Library/Application Support/SuperCollider')]:
        if (folder / 'startup.rtf').exists():
            raise SystemExit('Review the deprecated startup.rtf before running this test.')
    source = RUNTIME / 'QMWQuantumFrameResonatorAddonV2.scd'
    env = dict(os.environ, QMW_VNF_CONTROL_PORT='18990',
               QMW_VNF_TEST_SOURCE=str(source),
               QMW_ACCEPTANCE_TEST_SOURCE=str(ROOT / 'tests/routed_live_acceptance.scd'))
    result = subprocess.run([
        str(SCLANG), '-D', '-i', 'none', '-u', '0', '-l',
        str(RUNTIME / 'sclang_core_macos.yaml'),
        str(ROOT / 'tests/qmw_vnf_availability_regression.scd'),
    ], env=env, text=True, capture_output=True, timeout=20)
    output = result.stdout + result.stderr
    passed = result.returncode == 0 and 'checks=73 failures=0' in output
    print(json.dumps({'passed': passed, 'checks': 73,
                      'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                      'running_session_contacted': False,
                      'audio_servers_booted_or_stopped': False}, indent=2))
    if not passed:
        print(output)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
