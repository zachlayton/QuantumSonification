#!/usr/bin/env python3
"""
Graph Laplacian quantum walk -> OSC trigger stream, for driving an external
WFS synthesis/spatialization engine (Max or SuperCollider) over a rectangular
128-channel array.

Math, from Knill, "Calculus on Wave Fronts" (2026):
  - Graph Laplacian L, Dirac spectrum omega_j = sqrt(lambda_j)
  - Quantum walk density matrix rho(t) = |psi(t)><psi(t)|, psi(t) = exp(-i D t) psi(0)
  - rho_ii(t) = per-node excitation probability -> drives trigger timing
  - Each trigger's audio grain is shaped (in the receiving synth) by the
    deformed-derivative envelope t*phi_{q+2}(omega*t) from Definition 1,
    with q as the click(sharp)-vs-wake(ringing) decay-rate knob (see section 1.9).

This script only computes the *score* (trigger times/positions/parameters)
and streams it as OSC. Actual audio synthesis and the 128-channel WFS
delay/gain matrix live in the receiving Max/SC patch (see sc_receiver.scd).
"""
import argparse
import time

import numpy as np
from pythonosc.udp_client import SimpleUDPClient
from scipy.signal import find_peaks


def barbell_graph(clique_size=4):
    n = clique_size * 2
    A = np.zeros((n, n))
    for block in (range(0, clique_size), range(clique_size, n)):
        for i in block:
            for j in block:
                if i != j:
                    A[i, j] = 1
    A[clique_size - 1, clique_size] = A[clique_size, clique_size - 1] = 1
    return A


def laplacian_eig(A):
    deg = np.diag(A.sum(axis=1))
    L = deg - A
    lam, V = np.linalg.eigh(L)
    lam = np.clip(lam, 0, None)
    return lam, V


def fiedler_positions(V, margin=0.15):
    x, y = V[:, 1], V[:, 2]

    def norm(v):
        v = v - v.min()
        v = v / (v.max() - v.min() + 1e-12)
        return margin + v * (1 - 2 * margin)

    return norm(x), norm(y)


def quantum_walk_populations(lam, V, psi0_node, t):
    omega = np.sqrt(lam)
    psi0 = np.zeros(len(lam))
    psi0[psi0_node] = 1.0
    c = V.T @ psi0                            # modal coefficients
    phase = np.exp(-1j * np.outer(omega, t))  # (modes, time)
    psi_t = V @ (c[:, None] * phase)          # (nodes, time)
    return np.abs(psi_t) ** 2                 # rho_ii(t), shape (nodes, time)


def find_triggers(pop, t, height=0.08, distance_s=0.15, sr_ctrl=200):
    events = []
    dist = max(1, int(distance_s * sr_ctrl))
    for i in range(pop.shape[0]):
        peaks, _ = find_peaks(pop[i], height=height, distance=dist)
        for p in peaks:
            events.append((t[p], i, float(pop[i, p])))
    events.sort(key=lambda e: e[0])
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=57120,
                     help="57120 = SuperCollider default; use your Max [udpreceive] port instead")
    ap.add_argument("--duration", type=float, default=20.0)
    ap.add_argument("--pluck-node", type=int, default=0)
    ap.add_argument("--q", type=float, default=5.0,
                     help="Bessel dimension parameter: low (e.g. 1) = ringing/sustained, high (e.g. 15) = percussive")
    ap.add_argument("--f-base", type=float, default=110.0)
    ap.add_argument("--f-span-oct", type=float, default=3.0)
    ap.add_argument("--realtime", action="store_true",
                     help="pace OSC sends to wall-clock time instead of dumping instantly")
    args = ap.parse_args()

    A = barbell_graph(clique_size=4)
    lam, V = laplacian_eig(A)
    n = len(lam)
    xs, ys = fiedler_positions(V)

    client = SimpleUDPClient(args.host, args.port)
    client.send_message("/wf/init", [n, args.duration, args.q])
    for i in range(n):
        client.send_message("/wf/node", [i, float(xs[i]), float(ys[i])])

    sr_ctrl = 200
    t = np.linspace(0, args.duration, int(args.duration * sr_ctrl))
    pop = quantum_walk_populations(lam, V, args.pluck_node, t)
    events = find_triggers(pop, t, sr_ctrl=sr_ctrl)

    omega = np.sqrt(lam)
    omega_max = omega.max() if omega.max() > 0 else 1.0

    print(f"{len(events)} trigger events over {args.duration}s "
          f"(graph: barbell, {n} nodes, pluck node {args.pluck_node}, q={args.q})")

    t0 = time.time()
    for (ev_t, node, amp) in events:
        if args.realtime:
            wait = ev_t - (time.time() - t0)
            if wait > 0:
                time.sleep(wait)
        weights = V[node] ** 2
        centroid = float(np.sum(weights * omega) / (np.sum(weights) + 1e-12))
        freq = args.f_base * (2 ** (args.f_span_oct * centroid / omega_max))
        client.send_message("/wf/trigger",
                             [node, float(xs[node]), float(ys[node]),
                              float(amp), float(args.q), float(freq)])
        print(f"t={ev_t:6.2f}s  node={node}  amp={amp:.3f}  "
              f"freq={freq:6.1f}Hz  pos=({xs[node]:.2f},{ys[node]:.2f})")

    client.send_message("/wf/end", [])


if __name__ == "__main__":
    main()
