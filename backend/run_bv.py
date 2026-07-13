from backend.qmw_backend import QuantumBackend
from backend.qmw_backend import OSCMaterialSender
from backend.qmw_backend import descriptor_from_bv

secret = "10110110"

backend = QuantumBackend()
osc = OSCMaterialSender()

measured, counts = backend.bernstein_vazirani(secret)
descriptor = descriptor_from_bv(measured, counts)

print()
print(descriptor)
print()

osc.send_descriptor(descriptor)

print("OSC sent.")