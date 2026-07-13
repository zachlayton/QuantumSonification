from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from pythonosc.udp_client import SimpleUDPClient


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

        # Oracle
        for q, bit in enumerate(reversed(secret)):
            if bit == "1":
                qc.cx(q, answer)

        for q in range(n):
            qc.h(q)
            qc.measure(q, q)

        compiled = transpile(qc, self.simulator)

        job = self.simulator.run(compiled, shots=self.shots)

        counts = job.result().get_counts()

        measured = max(counts, key=counts.get)

        return measured, counts


class OSCMaterialSender:

    def __init__(self,
                 host="127.0.0.1",
                 port=7400):

        self.client = SimpleUDPClient(host, port)

    def send(self, bitstring):

        bits = [int(b) for b in bitstring]

        while len(bits) < 8:
            bits.append(0)

        mode_family = bits[0] * 2 + bits[1]

        decay = 0.15 + 0.75 * (
            (bits[2] * 2 + bits[3]) / 3
        )

        brightness = 0.2 + 0.7 * bits[4]

        damping = 0.2 + 0.6 * bits[5]

        density = 0.1 + 0.8 * bits[6]

        space = 0.1 + 0.8 * bits[7]

        self.client.send_message(
            "/qmw/bv/bitstring",
            bitstring
        )

        self.client.send_message(
            "/qmw/material/mode_family",
            mode_family
        )

        self.client.send_message(
            "/qmw/material/decay",
            decay
        )

        self.client.send_message(
            "/qmw/material/brightness",
            brightness
        )

        self.client.send_message(
            "/qmw/material/damping",
            damping
        )

        self.client.send_message(
            "/qmw/material/density",
            density
        )

        self.client.send_message(
            "/qmw/material/space",
            space
        )
