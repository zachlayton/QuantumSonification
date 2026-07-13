from pythonosc.udp_client import SimpleUDPClient
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def bv_circuit(secret):
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

    return qc

secret = "10110110"

sim = AerSimulator()
qc = bv_circuit(secret)
compiled = transpile(qc, sim)
result = sim.run(compiled, shots=1024).result()
counts = result.get_counts()
measured = max(counts, key=counts.get)

print("Hidden string:", secret)
print("Measured:     ", measured)
print("Counts:       ", counts)

client = SimpleUDPClient("127.0.0.1", 7400)

client.send_message("/qmw/bv/bitstring", measured)
client.send_message("/qmw/material/mode_family", int(measured[0:2], 2))
client.send_message("/qmw/material/decay", 0.15 + 0.75 * (int(measured[2:4], 2) / 3))
client.send_message("/qmw/material/brightness", 0.2 + 0.7 * int(measured[4]))
client.send_message("/qmw/material/damping", 0.2 + 0.6 * int(measured[5]))
client.send_message("/qmw/material/density", 0.1 + 0.8 * int(measured[6]))
client.send_message("/qmw/material/space", 0.1 + 0.8 * int(measured[7]))

print("OSC sent to Max on port 7400")
