import sys
from analysis.audio_descriptors import analyze_audio_file

if len(sys.argv) < 2:
    print("Usage: python analyze_file.py path/to/audio.wav")
    sys.exit(1)

path = sys.argv[1]
results = analyze_audio_file(path)

print()
print("Audio analysis:")
print(results)
print()
