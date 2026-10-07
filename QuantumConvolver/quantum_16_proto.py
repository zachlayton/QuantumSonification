import time
import random
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 7400)

BPM = 120
SUBDIVISIONS = 4

step_duration = 60.0 / BPM / SUBDIVISIONS

# 16 probability weights, one per voice
weights = [
    0.20, 0.15, 0.12, 0.10,
    0.08, 0.07, 0.06, 0.05,
    0.04, 0.035, 0.03, 0.025,
    0.02, 0.015, 0.01, 0.005
]

voices = list(range(16))
step = 0

print("Sending stochastic 16-voice pulses to Max on port 7400.")
print("Press Ctrl+C to stop.")

try:
    while True:
        voice = random.choices(voices, weights=weights, k=1)[0]

        amp = weights[voice] * 4.0
        phase = random.random()
        duration = random.choice([100, 150, 250, 500])

        client.send_message("/voice", [voice, amp, phase, duration, step])

        print(f"voice={voice} amp={amp:.3f} phase={phase:.3f} dur={duration} step={step}")

        step += 1
        time.sleep(step_duration)

except KeyboardInterrupt:
    print("\nStopped.")
