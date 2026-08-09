from __future__ import annotations

import threading
from typing import Any

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from density.density_state_injection import AtomicDensityStateReceiver


def start_visual_control_server(
    engine: Any,
    host: str = "127.0.0.1",
    port: int = 7402,
) -> BlockingOSCUDPServer:
    """Start the oscilloscope control OSC receiver.

    Expected engine surface:
        engine.set_visual_perturb(axis, value)
        engine.density_engine.set_excitation_source(source)
    """
    dispatcher = Dispatcher()

    density_receiver = AtomicDensityStateReceiver(engine.commit_density_state)

    def density_guard(action):
        try:
            action()
        except Exception as exc:
            if hasattr(engine, "report_density_state_error"):
                engine.report_density_state_error(str(exc))
            else:
                print(f"Density state rejected: {exc}")
        # OSC dispatcher treats any non-None callback result as a reply.
        return None

    def set_excitation_source(address, *args):
        if not args:
            return

        source = str(args[0])
        try:
            engine.density_engine.set_excitation_source(source)
            print(f"QMW excitation source set to: {source}")
        except Exception as exc:
            print(f"Could not set excitation source {source}: {exc}")

    def set_born_species(address, *args):
        if not args:
            return
        species = str(args[0])
        try:
            engine.set_born_species(species)
            print(f"QMW Born species set to: {species}")
        except Exception as exc:
            print(f"Could not set Born species {species}: {exc}")

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

    def request_engine_tick(address, *args):
        if not hasattr(engine, "request_external_tick"):
            return
        interval_ms = args[0] if args else None
        engine.request_external_tick(interval_ms=interval_ms)

    def set_temporal_crystal_mode(address, *args):
        if not args or not hasattr(engine, "set_temporal_crystal_mode"):
            return
        mode = str(args[0]).strip().lower()
        try:
            engine.set_temporal_crystal_mode(mode)
        except Exception as exc:
            print(f"Could not set temporal-crystal mode {mode}: {exc}")

    def apply_live_gate(address, event_id, gate, *args):
        if not hasattr(engine, "apply_live_density_gate"):
            raise RuntimeError("Engine does not expose live density gates")
        values = list(args)
        source_order = "q0_lsb"
        if values and isinstance(values[-1], str):
            source_order = str(values.pop())
        if not values:
            raise ValueError("Live gate requires at least one qubit")
        engine.apply_live_density_gate(event_id, gate, values, source_order)

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
    dispatcher.map("/qmw/excitation/born/species", set_born_species)
    dispatcher.map("/qmw/engine/tick", request_engine_tick)
    dispatcher.map("/qmw/time/control/mode", set_temporal_crystal_mode)
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
    dispatcher.map(
        "/qmw/state/begin",
        lambda address, revision, n_qubits, source_order="q0_lsb": density_guard(
            lambda: density_receiver.begin(revision, n_qubits, str(source_order))
        ),
    )
    dispatcher.map(
        "/qmw/state/rho/real",
        lambda address, revision, *values: density_guard(
            lambda: density_receiver.set_real(revision, values)
        ),
    )
    dispatcher.map(
        "/qmw/state/rho/imag",
        lambda address, revision, *values: density_guard(
            lambda: density_receiver.set_imag(revision, values)
        ),
    )
    dispatcher.map(
        "/qmw/state/commit",
        lambda address, revision: density_guard(
            lambda: density_receiver.commit(revision)
        ),
    )
    dispatcher.map(
        "/qmw/state/gate",
        lambda address, event_id, gate, *args: density_guard(
            lambda: apply_live_gate(address, event_id, gate, *args)
        ),
    )

    # A single handler thread preserves the ordered begin/real/imag/commit
    # transaction sent from one QAC UDP socket.
    server = BlockingOSCUDPServer((host, port), dispatcher)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    if not getattr(engine, "quiet", False):
        print(f"Visual control OSC listening on {host}:{port}")
    return server
