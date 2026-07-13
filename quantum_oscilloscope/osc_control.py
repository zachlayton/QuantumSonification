from __future__ import annotations

import threading
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer


def start_visual_control_server(
    engine: Any,
    host: str = "127.0.0.1",
    port: int = 7402,
) -> ThreadingOSCUDPServer:
    """Start the oscilloscope control OSC receiver.

    Expected engine surface:
        engine.set_visual_perturb(axis, value)
        engine.density_engine.set_excitation_source(source)
    """
    dispatcher = Dispatcher()

    def set_excitation_source(address, *args):
        if not args:
            return

        source = str(args[0])
        try:
            engine.density_engine.set_excitation_source(source)
            print(f"QMW excitation source set to: {source}")
        except Exception as exc:
            print(f"Could not set excitation source {source}: {exc}")

    def set_bohmian_parameter(address, parameter, value=None):
        if value is None:
            return

        if not hasattr(engine, "set_bohmian_parameter"):
            print("Engine does not expose Bohmian controls.")
            return

        try:
            engine.set_bohmian_parameter(parameter, value)
        except Exception as exc:
            print(f"Could not set Bohmian parameter {parameter}: {exc}")

    dispatcher.map(
        "/qmw/control/perturb/x",
        lambda address, value: engine.set_visual_perturb("x", value),
    )
    dispatcher.map(
        "/qmw/control/perturb/y",
        lambda address, value: engine.set_visual_perturb("y", value),
    )
    dispatcher.map(
        "/qmw/control/perturb/z",
        lambda address, value: engine.set_visual_perturb("z", value),
    )
    dispatcher.map(
        "/qmw/control/visual_gain",
        lambda address, value: engine.set_visual_perturb("gain", value),
    )

    dispatcher.map("/qmw/excitation", set_excitation_source)
    dispatcher.map("/excitation", set_excitation_source)
    dispatcher.map(
        "/qmw/bohm/mobility",
        lambda address, value: set_bohmian_parameter(address, "mobility", value),
    )
    dispatcher.map(
        "/qmw/bohm/damping",
        lambda address, value: set_bohmian_parameter(address, "damping", value),
    )
    dispatcher.map(
        "/qmw/bohm/field_smoothing",
        lambda address, value: set_bohmian_parameter(
            address,
            "field_smoothing",
            value,
        ),
    )
    dispatcher.map(
        "/qmw/bohm/smoothing",
        lambda address, value: set_bohmian_parameter(address, "smoothing", value),
    )

    server = ThreadingOSCUDPServer((host, port), dispatcher)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print(f"Visual control OSC listening on {host}:{port}")
    return server
