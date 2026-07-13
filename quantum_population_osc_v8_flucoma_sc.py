from pathlib import Path

from pythonosc.udp_client import SimpleUDPClient

from quantum_oscilloscope.osc_control import start_visual_control_server
from quantum_population_osc_v7 import MLXQuantumEngine


class OscFanout:
    """Send the same OSC message to several UDP ports."""

    def __init__(self, host: str, ports: list[int]) -> None:
        self.clients = [SimpleUDPClient(host, int(port)) for port in ports]

    def send_message(self, address, value) -> None:
        for client in self.clients:
            client.send_message(address, value)


if __name__ == "__main__":
    host = "127.0.0.1"
    max_port = 7400
    processing_port = 7401
    control_port = 7402
    supercollider_port = 57120

    qmw = MLXQuantumEngine(
        audio_path=Path(
            "/Users/zlayton/QuantumSonification/materials/test.wav"
        ),
        osc_host=host,
        osc_port=max_port,
        visual_osc_port=processing_port,
    )

    main_osc = OscFanout(host, [max_port, supercollider_port])
    qmw.osc = main_osc
    qmw.oscilloscope.osc = main_osc

    print("Starting QMW control server on 7402...")
    print("Main OSC fanout:")
    print(f"  Max/router:       {host}:{max_port}")
    print(f"  SuperCollider:   {host}:{supercollider_port}")
    print(f"  Processing:      {host}:{processing_port}")

    control_server = start_visual_control_server(
        qmw,
        host=host,
        port=control_port,
    )

    qmw.run()
