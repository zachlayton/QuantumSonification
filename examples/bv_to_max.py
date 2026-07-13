# qmw/backend/osc_sender.py

from pythonosc.udp_client import SimpleUDPClient


class OSCSender:
    def __init__(self, host="127.0.0.1", port=7400):
        self.client = SimpleUDPClient(host, port)

    def send_bv_material(self, bitstring: str):
        """
        Map BV hidden string to Max/Elements-style resonator controls.
        """
        bits = [int(b) for b in bitstring]

        # Pad if needed
        while len(bits) < 8:
            bits.append(0)

        mode_family = bits[0] * 2 + bits[1]
        decay = 0.15 + 0.75 * ((bits[2] * 2 + bits[3]) / 3)
        brightness = 0.2 + 0.7 * bits[4]
        damping = 0.2 + 0.6 * bits[5]
        density = 0.1 + 0.8 * bits[6]
        space = 0.1 + 0.8 * bits[7]

        self.client.send_message("/qmw/bv/bitstring", bitstring)
        self.client.send_message("/qmw/material/mode_family", mode_family)
        self.client.send_message("/qmw/material/decay", decay)
        self.client.send_message("/qmw/material/brightness", brightness)
        self.client.send_message("/qmw/material/damping", damping)
        self.client.send_message("/qmw/material/density", density)
        self.client.send_message("/qmw/material/space", space)
