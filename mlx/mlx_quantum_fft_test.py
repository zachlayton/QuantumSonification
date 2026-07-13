from __future__ import annotations

import math
import time
from collections import deque

import mlx.core as mx
import numpy as np
from pythonosc.udp_client import SimpleUDPClient

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import threading


OSC_HOST = "127.0.0.1"
OSC_PORT = 7400

WINDOW_SIZE = 256
UPDATE_HZ = 40.0

client = SimpleUDPClient(OSC_HOST, OSC_PORT)

# This stands in for a quantum-derived control stream.
# Later we will feed it actual qubit z, purity, coherence, etc.
history = deque(maxlen=WINDOW_SIZE)
history_lock = threading.Lock()


def receive_q0z(address, value):
    with history_lock:
        history.append(float(value))


def start_quantum_receiver():
    dispatcher = Dispatcher()
    dispatcher.map("/quantum/q0z", receive_q0z)

    server = ThreadingOSCUDPServer(
        ("127.0.0.1", 7402),
        dispatcher,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    print("Listening for quantum data on 127.0.0.1:7402")
    return server


def make_control_sample() -> float:
    global phase_a, phase_b

    phase_a += 0.041
    phase_b += 0.013

    sample = (
        0.55 * math.sin(phase_a)
        + 0.28 * math.sin(phase_b)
        + 0.12 * math.sin(phase_a * 0.31 + phase_b)
    )

    return float(sample)


def mlx_spectrum(values: list[float]) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns normalized magnitude and phase & derivative from an MLX real FFT.
    """
    x = mx.array(values, dtype=mx.float32)
    x = x - mx.mean(x)
    x = x[1:] - x[:-1]

    # Hann-like window, built in MLX.
    n = x.shape[0]
    indices = mx.arange(n, dtype=mx.float32)
    window = 0.5 - 0.5 * mx.cos(
        2.0 * math.pi * indices / float(n - 1)
    )

    spectrum = mx.fft.rfft(x * window)

    magnitude = mx.abs(spectrum)
    phase = mx.arctan2(
    mx.imag(spectrum),
    mx.real(spectrum),
)

    # Force evaluation and move only small final arrays to NumPy.
    magnitude_np = np.array(magnitude)
    phase_np = np.array(phase)

    peak = float(np.max(magnitude_np))

    if peak > 1e-12:
        magnitude_np = magnitude_np / peak

    return magnitude_np, phase_np

server = start_quantum_receiver()
print("MLX FFT control engine running.")
print("Sending to 127.0.0.1:7400")

while True:
    with history_lock: 
        values = list(history)

    if len(values) == WINDOW_SIZE:
        magnitude, phase = mlx_spectrum(values)

        # Send selected spectral bins as OSC control values.
        for bin_index in range(1, 17):
            client.send_message(
                f"/mlx/fft/bin/{bin_index}/magnitude",
                float(magnitude[bin_index]),
            )

            client.send_message(
     "/mlx/fft/phase_frame",
    [
        float(phase[index])
        for index in range(1, 17)
    ],
)
            client.send_message(
                f"/mlx/fft/bin/{bin_index}/phase",
                float(phase[bin_index]),
            )

        # Send the frame (vector of selected magnitudes)
        client.send_message(
            f"/mlx/fft/frame",
            [float(magnitude[index]) for index in range(1, 17)],
        )

        


        # Useful summary controls.
        spectral_centroid = float(
            np.sum(
                np.arange(len(magnitude)) * magnitude
            )
            / max(np.sum(magnitude), 1e-12)
        )

        spectral_flux = float(
            np.mean(np.abs(np.diff(magnitude)))
        )

        client.send_message(
            "/mlx/fft/centroid",
            spectral_centroid,
        )
        
        client.send_message(
            "/mlx/fft/frame",
            	[
                    float(magnitude[index])
                    for index in range(1, 17)
            	],
        )
        
        client.send_message(
            "/mlx/fft/flux",
            spectral_flux,
        )

        print(
            f"centroid={spectral_centroid:.2f} "
            f"flux={spectral_flux:.4f}"
        )

    time.sleep(1.0 / UPDATE_HZ)
