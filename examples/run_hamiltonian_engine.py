from pathlib import Path
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

print("Current working directory:", os.getcwd())
print("Project root:", ROOT)

from engine.hamiltonian_engine import HamiltonianEngine

engine = HamiltonianEngine(
    audio_path=ROOT / "materials" / "test.wav",
    mutation_amount=0.5,
    interval=1.0,
)

engine.run()