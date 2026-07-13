import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.audio_descriptors import analyze_audio_material

if len(sys.argv) < 2:
    print("Usage: python examples/analyze_material.py path/to/audio.wav")
    sys.exit(1)

descriptor = analyze_audio_material(sys.argv[1])

print()
print(descriptor)
print()