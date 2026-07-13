from dataclasses import dataclass
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from pythonosc.udp_client import SimpleUDPClient
from descriptors.quantum_material_descriptor import QuantumMaterialDescriptor




class QuantumBackend:
    def __init__(self, shots=1024):
        self.shots = shots
        self.simulator = AerSimulator()

    def bernstein_vazirani(self, secret):
        n = len(secret)
        qc = QuantumCircuit(n + 1, n)
        answer = n

        qc.x(answer)
        qc.h(answer)

        for q in range(n):
            qc.h(q)

        for q, bit in enumerate(reversed(secret)):
            if bit == "1":
                qc.cx(q, answer)

        for q in range(n):
            qc.h(q)
            qc.measure(q, q)

        compiled = transpile(qc, self.simulator)
        counts = self.simulator.run(compiled, shots=self.shots).result().get_counts()
        measured = max(counts, key=counts.get)

        return measured, counts


def descriptor_from_bv(bitstring, counts):
    bits = [int(b) for b in bitstring]

    while len(bits) < 8:
        bits.append(0)

    hamming_weight = sum(bits)
    balance = hamming_weight / len(bits)

    transition_count = 0
    for a, b in zip(bits[:-1], bits[1:]):
        if a != b:
            transition_count += 1
            

    transition_density = transition_count / (len(bits) - 1)

    return QuantumMaterialDescriptor(
        algorithm="bernstein_vazirani",
        bitstring=bitstring,

        mode_family=bits[0] * 2 + bits[1],
        brightness=0.2 + 0.7 * bits[4],
        damping=0.2 + 0.6 * bits[5],
        density=0.1 + 0.8 * bits[6],
        space=0.1 + 0.8 * bits[7],
        decay=0.15 + 0.75 * ((bits[2] * 2 + bits[3]) / 3),

        hamming_weight=hamming_weight,
        balance=balance,
        transition_count=transition_count,
        transition_density=transition_density,

        counts=counts,
    )


class OSCMaterialSender:
    def __init__(self, host="127.0.0.1", port=7400):
        self.client = SimpleUDPClient(host, port)

    def send_descriptor(self, descriptor):
        self.client.send_message("/qmw/algorithm", descriptor.algorithm)
        self.client.send_message("/qmw/bv/bitstring", descriptor.bitstring)
        self.client.send_message("/qmw/material/mode_family", descriptor.mode_family)
        self.client.send_message("/qmw/material/decay", descriptor.decay)
        self.client.send_message("/qmw/material/brightness", descriptor.brightness)
        self.client.send_message("/qmw/material/damping", descriptor.damping)
        self.client.send_message("/qmw/material/density", descriptor.density)
        self.client.send_message("/qmw/material/space", descriptor.space)