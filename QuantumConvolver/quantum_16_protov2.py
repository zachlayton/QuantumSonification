import time
import random
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 7400)

BPM = 120
SUBDIVISIONS = 4
step_duration = 60.0 / BPM / SUBDIVISIONS

weights = [
    0.20, 0.15, 0.12, 0.10,
    0.08, 0.07, 0.06, 0.05,
    0.04, 0.035, 0.03, 0.025,
    0.02, 0.015, 0.01, 0.005
]

voices = list(range(16))
step = 0

try:
    while True:
        voice = random.choices(voices, weights=weights, k=1)[0]

        amp = min(weights[voice] * 4.0, 1.0)
        phase = random.random()
        duration = random.choice([80, 120, 160, 250, 500])

        # general message
        client.send_message("/voice", [voice, amp, phase, duration, step])

        # individual voice message
        client.send_message(f"/voice/{voice}", [amp, phase, duration, step])

        print(f"/voice/{voice}", amp, phase, duration, step)

        step += 1
        time.sleep(step_duration)

except KeyboardInterrupt:
    print("\nStopped.")
