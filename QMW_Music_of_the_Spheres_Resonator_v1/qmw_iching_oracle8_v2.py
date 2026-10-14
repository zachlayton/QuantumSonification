#!/usr/bin/env python3
"""QMW eight-qubit I Ching oracle V2.

Qubits 0..2 are the lower trigram, 3..5 the upper trigram, and 6..7
the change register.  The 81 Pauli words are a separate operator field.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import asdict, dataclass

import numpy as np

NQ, DIM = 8, 256
LOWER_QUBITS, UPPER_QUBITS, CHANGE_QUBITS = (0, 1, 2), (3, 4, 5), (6, 7)
PAULI_QUBITS = (0, 2, 3, 5)
P = {
    "X": np.array([[0, 1], [1, 0]], complex),
    "Y": np.array([[0, -1j], [1j, 0]], complex),
    "Z": np.array([[1, 0], [0, -1]], complex),
}
H = (P["X"] + P["Z"]) / math.sqrt(2)
TRI = {7: ("Qian", "Heaven"), 6: ("Dui", "Lake"), 5: ("Li", "Fire"),
       4: ("Zhen", "Thunder"), 3: ("Xun", "Wind"), 2: ("Kan", "Water"),
       1: ("Gen", "Mountain"), 0: ("Kun", "Earth")}
LINE_NAMES = {(0, 1): (6, "old yin"), (1, 0): (7, "young yang"),
              (0, 0): (8, "young yin"), (1, 1): (9, "old yang")}


def bit(value, q): return (value >> q) & 1


def apply1(psi, gate, q):
    out = psi.copy(); step = 1 << q
    for base in range(0, DIM, step << 1):
        for j in range(step):
            i0, i1 = base + j, base + j + step; a, b = psi[i0], psi[i1]
            out[i0] = gate[0, 0] * a + gate[0, 1] * b
            out[i1] = gate[1, 0] * a + gate[1, 1] * b
    return out


def ry(theta):
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -s], [s, c]], complex)


def rz(theta): return np.diag([np.exp(-.5j * theta), np.exp(.5j * theta)])


def cz(psi, a, b, theta):
    out = psi.copy(); phase = np.exp(1j * theta)
    for i in range(DIM):
        if bit(i, a) and bit(i, b): out[i] *= phase
    return out


def expect(psi, ops):
    transformed = psi
    for q, pauli in ops.items(): transformed = apply1(transformed, P[pauli], q)
    return float(np.vdot(psi, transformed).real)


def build(seed, depth=3):
    rng = np.random.default_rng(seed); psi = np.zeros(DIM, complex); psi[0] = 1
    for q in range(NQ):
        psi = apply1(psi, H, q)
        psi = apply1(psi, ry(rng.uniform(-math.pi, math.pi)), q)
        psi = apply1(psi, rz(rng.uniform(-math.pi, math.pi)), q)
    edges = [(0,1),(1,2),(2,0),(3,4),(4,5),(5,3),(0,3),(1,4),(2,5),
             (6,0),(6,2),(6,4),(7,1),(7,3),(7,5),(6,7)]
    for _ in range(max(1, depth)):
        rng.shuffle(edges)
        for a, b in edges: psi = cz(psi, a, b, rng.uniform(.15 * math.pi, math.pi))
        for q in range(NQ):
            psi = apply1(apply1(psi, ry(rng.uniform(-.45, .45)), q),
                         rz(rng.uniform(-.45, .45)), q)
    return psi / np.linalg.norm(psi)


def reduced_density_matrix(psi, qubits):
    """Trace out all but ``qubits``; returned basis follows the given order."""
    qubits = tuple(qubits)
    axes = tuple(7 - q for q in qubits)
    rest = tuple(a for a in range(NQ) if a not in axes)
    matrix = psi.reshape((2,) * NQ).transpose(axes + rest).reshape(2 ** len(qubits), -1)
    return matrix @ matrix.conj().T


def von_neumann_entropy(rho, tol=1e-12):
    vals = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    vals = vals[vals > tol]
    return float(-np.sum(vals * np.log2(vals)))


def density_diagnostics(psi):
    rho = np.outer(psi, psi.conj())
    reduced = {"rho_L": reduced_density_matrix(psi, LOWER_QUBITS),
               "rho_U": reduced_density_matrix(psi, UPPER_QUBITS),
               "rho_C": reduced_density_matrix(psi, CHANGE_QUBITS),
               "rho_LU": reduced_density_matrix(psi, LOWER_QUBITS + UPPER_QUBITS)}
    entropies = {name.replace("rho_", "S_"): von_neumann_entropy(value)
                 for name, value in reduced.items()}
    entropies["I_L_U"] = max(0.0, entropies["S_L"] + entropies["S_U"] - entropies["S_LU"])
    return rho, reduced, entropies


def moving_probs(psi):
    result = []
    for q in range(6):
        correlations = [abs(expect(psi, {q:"Z", 6:"X"})),
                        abs(expect(psi, {q:"X", 7:"Z"})),
                        abs(expect(psi, {q:"Y", 6:"Y"}))]
        result.append(float(np.clip(sum(correlations) / 1.5, 0, 1)))
    return result


def line_ontology(polarity, moving):
    value, name = LINE_NAMES[(int(polarity), int(moving))]
    return {"polarity": int(polarity), "moving": int(moving),
            "value": value, "state": name}


def apply_moving_mask(primary, moving_mask): return primary ^ moving_mask


def pauli81(psi):
    field = {}
    for letters in itertools.product("XYZ", repeat=4):
        word = "".join(letters)
        field[word] = expect(psi, dict(zip(PAULI_QUBITS, letters)))
    winner = max(field, key=lambda word: abs(field[word]))
    return winner, field[winner], field


def hval(lines): return sum(int(value) << i for i, value in enumerate(lines))
def trival(lines): return (lines[2] << 2) | (lines[1] << 1) | lines[0]


@dataclass
class Reading:
    seed: int; measured_8bit: str; primary_binary: int; primary_lines: list
    lower_trigram: str; upper_trigram: str; change_register: int
    moving_mask: int; moving_lines: list; moving_probabilities: list; line_states: list
    transformed_binary: int; transformed_lines: list; purity: float; coherence_l1: float
    entropy_L_bits: float; entropy_U_bits: float; entropy_C_bits: float
    entropy_LU_bits: float; mutual_information_L_U_bits: float
    pauli81_operator: str; pauli81_expectation: float


def consult(seed=None, depth=3):
    if seed is None: seed = int(np.random.SeedSequence().entropy) & 0xffffffff
    psi = build(seed, depth); rng = np.random.default_rng(seed ^ 0x1C41C41C)
    measured = int(rng.choice(DIM, p=np.abs(psi) ** 2))
    lines = [bit(measured, q) for q in range(6)]; primary = hval(lines)
    change = (measured >> 6) & 3; probabilities = moving_probs(psi)
    moving_bits = [int(rng.random() < probability) for probability in probabilities]
    mask = hval(moving_bits); transformed = apply_moving_mask(primary, mask)
    changed_lines = [bit(transformed, q) for q in range(6)]
    line_states = [line_ontology(lines[i], moving_bits[i]) for i in range(6)]
    lower, upper = TRI[trival(lines[:3])], TRI[trival(lines[3:])]
    winner, expectation, field = pauli81(psi)
    rho, reduced, entropy = density_diagnostics(psi)
    rd = Reading(seed, format(measured, "08b"), primary, lines,
                 f"{lower[0]} / {lower[1]}", f"{upper[0]} / {upper[1]}", change,
                 mask, [i + 1 for i, moving in enumerate(moving_bits) if moving],
                 [round(x, 6) for x in probabilities], line_states, transformed,
                 changed_lines, float(np.trace(rho @ rho).real),
                 float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho)))),
                 entropy["S_L"], entropy["S_U"], entropy["S_C"], entropy["S_LU"],
                 entropy["I_L_U"], winner, expectation)
    return rd, psi, rho, reduced, field


def complex_matrix_json(matrix):
    return {"real": matrix.real.tolist(), "imag": matrix.imag.tolist()}


def export_json(path, rd, psi, rho, reduced, field):
    payload = {"reading": asdict(rd), "pauli81": field,
               "statevector_real": psi.real.tolist(), "statevector_imag": psi.imag.tolist(),
               "density_matrix": complex_matrix_json(rho),
               "reduced_density_matrices": {k: complex_matrix_json(v) for k, v in reduced.items()}}
    with open(path, "w", encoding="utf-8") as handle: json.dump(payload, handle, indent=2)


def send_osc(rd, host, port):
    try: from pythonosc.udp_client import SimpleUDPClient
    except ImportError as exc: raise SystemExit("OSC requested: pip install python-osc") from exc
    client = SimpleUDPClient(host, port); data = asdict(rd); root = "/qmw/iching/"
    for path, key in [("primary","primary_binary"),("transformed","transformed_binary"),
                      ("lines","primary_lines"),("moving_prob","moving_probabilities"),
                      ("entanglement","entropy_L_bits")]:
        client.send_message(root + path, data[key])  # V1-compatible addresses
    client.send_message(root + "moving", data["moving_lines"] or [0])
    client.send_message(root + "moving_mask", data["moving_mask"])
    client.send_message(root + "change_register", data["change_register"])
    client.send_message(root + "mutual_information", data["mutual_information_L_U_bits"])
    client.send_message(root + "pauli81/operator", data["pauli81_operator"])
    client.send_message(root + "pauli81/expectation", data["pauli81_expectation"])


def render(lines, moving):
    return "\n".join(f"{i+1}: " + ("---------" if lines[i] else "---   ---") +
                     ("  *" if i + 1 in moving else "") for i in range(5, -1, -1))


def main():
    parser = argparse.ArgumentParser(description="QMW 8-qubit I Ching oracle V2")
    parser.add_argument("--seed", type=int); parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--json"); parser.add_argument("--osc", action="store_true")
    parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=7400)
    args = parser.parse_args(); rd, psi, rho, reduced, field = consult(args.seed, args.depth)
    print("\nQMW I CHING QUANTUM ORACLE V2 — 8 QUBITS\n" + "=" * 46)
    print(render(rd.primary_lines, rd.moving_lines)); print("lower:", rd.lower_trigram)
    print("upper:", rd.upper_trigram); print("64-space primary:", rd.primary_binary)
    print("change register:", rd.change_register); print("moving mask:", rd.moving_mask)
    print("line values:", [line["value"] for line in rd.line_states])
    print("transformed:", rd.transformed_binary)
    print(f"S(L)={rd.entropy_L_bits:.4f}  S(U)={rd.entropy_U_bits:.4f}  "
          f"S(C)={rd.entropy_C_bits:.4f}  I(L:U)={rd.mutual_information_L_U_bits:.4f} bits")
    print(f"81-space Pauli operator: {rd.pauli81_operator}  <P>={rd.pauli81_expectation:+.4f}")
    print("seed:", rd.seed)
    if args.json: export_json(args.json, rd, psi, rho, reduced, field)
    if args.osc: send_osc(rd, args.host, args.port)


if __name__ == "__main__": main()
