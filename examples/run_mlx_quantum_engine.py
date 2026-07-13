from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.mlx_quantum_engine import MLXQuantumEngine

engine = MLXQuantumEngine(
    audio_path=ROOT / "materials" / "test.wav",
    mutation_amount=0.5,
    interval=0.5,
)

engine.run()