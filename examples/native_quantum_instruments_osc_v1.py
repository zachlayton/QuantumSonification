#!/usr/bin/env python3
"""Stream native spinor, EPR, and exchange-symmetric quantum frames over OSC."""

from __future__ import annotations

import argparse
from pathlib import Path
import queue
import sys
import threading
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

from excitation.native_quantum_instrument_osc_v1 import (
    NativeInstrumentOSCConfig,
    NativeQuantumInstrumentOSCAdapter,
)
from excitation.wavefunction_sonification_adapter_v1 import (
    WavefunctionGrainConfig,
    WavefunctionSonificationAdapter,
)
from excitation.wavefunction_sources_v1 import WavefunctionFrame
from excitation.quantum_frames_v1 import DiracSpinorFieldFrame, RelativisticLevelFrame
from excitation.quantum_instrument_registry_v1 import create_quantum_instrument


CONTROL_SELECTIONS = (
    "all",
    "all_native",
    "spin_1_2_precession",
    "quantum_entanglement_epr",
    "identical_particles_boson",
    "identical_particles_fermion",
    "morse_potential",
    "aharonov_bohm_effect",
    "landau_levels",
    "hydrogen_zeeman",
    "hydrogen_stark",
    "helium_variational_two_electron",
    "delta_function_shell",
    "dirac_hydrogen_fine_structure",
    "dirac_step_klein",
)


def create_sources(selection: str, args: argparse.Namespace) -> dict[str, object]:
    if selection not in CONTROL_SELECTIONS:
        raise ValueError(f"unknown control selection {selection!r}")
    sources: dict[str, object] = {}
    if selection in ("all", "all_native", "spin_1_2_precession"):
        sources["spin_1_2_precession"] = create_quantum_instrument(
            "spin_1_2_precession",
            magnetic_field=args.magnetic_field,
            gyromagnetic_ratio=args.gyromagnetic_ratio,
        )
    if selection in ("all", "all_native", "identical_particles_boson", "identical_particles_fermion"):
        statistics = (
            "fermion" if selection == "identical_particles_fermion" else args.statistics
        )
        if selection == "identical_particles_boson":
            statistics = "boson"
        sources["identical_particles_fermion_boson"] = create_quantum_instrument(
            "identical_particles_fermion_boson",
            statistics=statistics,
            n_points=args.grid,
        )
    if selection in ("all", "all_native", "quantum_entanglement_epr"):
        sources["quantum_entanglement_epr"] = create_quantum_instrument(
            "quantum_entanglement_epr",
            bell_state=args.bell_state,
        )
    if selection in (
        "morse_potential",
        "aharonov_bohm_effect",
        "landau_levels",
        "hydrogen_zeeman",
        "hydrogen_stark",
        "helium_variational_two_electron",
        "delta_function_shell",
    ):
        parameters: dict[str, object] = {"grid_shape": args.field_grid}
        if selection == "landau_levels":
            parameters["magnetic_field"] = args.landau_field
        elif selection in ("hydrogen_zeeman", "hydrogen_stark"):
            parameters["field_strength"] = args.hydrogen_field
        if selection == "delta_function_shell":
            parameters["grid_shape"] = max(args.field_grid, 64)
        sources[selection] = create_quantum_instrument(selection, **parameters)
    if selection == "dirac_hydrogen_fine_structure":
        sources[selection] = create_quantum_instrument(
            selection,
            time_scale=args.relativistic_time_scale,
        )
    if selection == "dirac_step_klein":
        sources[selection] = create_quantum_instrument(
            selection,
            n_points=args.dirac_grid,
            extent=args.dirac_extent,
            packet_center=args.dirac_packet_center,
            packet_width=args.dirac_packet_width,
        )
    return sources


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--instrument",
        choices=(
            "all",
            "all_native",
            "spin_1_2_precession",
            "identical_particles_fermion_boson",
            "quantum_entanglement_epr",
            "morse_potential",
            "aharonov_bohm_effect",
            "landau_levels",
            "hydrogen_zeeman",
            "hydrogen_stark",
            "helium_variational_two_electron",
            "delta_function_shell",
            "dirac_hydrogen_fine_structure",
            "dirac_step_klein",
        ),
        default="all_native",
    )
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--duration", type=float, default=0.0)
    parser.add_argument("--grid", type=int, default=96)
    parser.add_argument("--statistics", choices=("boson", "fermion"), default="boson")
    parser.add_argument("--bell-state", choices=("phi_plus", "phi_minus", "psi_plus", "singlet"), default="singlet")
    parser.add_argument("--magnetic-field", nargs=3, type=float, default=(0.0, 0.0, 1.0))
    parser.add_argument("--gyromagnetic-ratio", type=float, default=6.283185307179586)
    parser.add_argument("--pair-samples", type=int, default=24)
    parser.add_argument("--field-grid", type=int, default=32)
    parser.add_argument("--landau-field", type=float, default=1.0)
    parser.add_argument("--hydrogen-field", type=float, default=0.08)
    parser.add_argument("--field-grains", type=int, default=12)
    parser.add_argument("--relativistic-time-scale", type=float, default=10000.0)
    parser.add_argument("--dirac-grid", type=int, default=512)
    parser.add_argument("--dirac-samples", type=int, default=32)
    parser.add_argument("--dirac-extent", type=float, default=40.0)
    parser.add_argument("--dirac-packet-center", type=float, default=-6.0)
    parser.add_argument("--dirac-packet-width", type=float, default=1.5)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--max-port", type=int, default=7482)
    parser.add_argument("--processing-port", type=int, default=7402)
    parser.add_argument("--sc-port", type=int, default=57120)
    parser.add_argument("--control-port", type=int, default=7483)
    parser.add_argument("--cloud-max-port", type=int, default=7480)
    parser.add_argument("--cloud-processing-port", type=int, default=7401)
    args = parser.parse_args()
    if args.fps <= 0.0:
        raise SystemExit("--fps must be positive")

    initial_selection = args.instrument
    if initial_selection == "identical_particles_fermion_boson":
        initial_selection = f"identical_particles_{args.statistics}"
    sources = create_sources(initial_selection, args)

    ports = tuple(dict.fromkeys((args.max_port, args.processing_port, args.sc_port)))
    clients = tuple(SimpleUDPClient(args.host, port) for port in ports)
    adapter = NativeQuantumInstrumentOSCAdapter(
        clients,
        NativeInstrumentOSCConfig(
            pair_samples_per_frame=args.pair_samples,
            dirac_samples_per_frame=args.dirac_samples,
        ),
    )
    cloud_ports = tuple(dict.fromkeys((args.cloud_max_port, args.cloud_processing_port, args.sc_port)))
    cloud_clients = tuple(SimpleUDPClient(args.host, port) for port in cloud_ports)
    cloud_adapter = WavefunctionSonificationAdapter(
        cloud_clients,
        WavefunctionGrainConfig(
            grains_per_frame=args.field_grains,
            decay_ms=5.0,
            adaptive_rate=False,
        ),
    )
    selections: queue.SimpleQueue[str] = queue.SimpleQueue()
    dispatcher = Dispatcher()

    def select_from_osc(_address: str, value: object) -> None:
        selections.put(str(value))

    dispatcher.map("/qmw/instrument/control/select", select_from_osc)
    control_server = ThreadingOSCUDPServer((args.host, args.control_port), dispatcher)
    control_thread = threading.Thread(target=control_server.serve_forever, daemon=True)
    control_thread.start()

    def announce_selection(selection: str) -> None:
        for client in clients:
            client.send_message("/qmw/instrument/control/selected", selection)

    announce_selection(initial_selection)
    dt = 1.0 / args.fps
    started = time.monotonic()
    deadline = started
    frame_id = 0
    print(
        f"Streaming {args.instrument} at {args.fps:g} fps to "
        f"{', '.join(map(str, ports))}; Max control on {args.control_port}"
    )
    try:
        while args.duration <= 0.0 or time.monotonic() - started < args.duration:
            try:
                requested = selections.get_nowait()
            except queue.Empty:
                requested = None
            if requested is not None:
                if requested in CONTROL_SELECTIONS:
                    sources = create_sources(requested, args)
                    initial_selection = requested
                    announce_selection(requested)
                    print(f"\nselected from OSC: {requested}")
                else:
                    print(f"\nignored unknown OSC selection: {requested}")
            frames = {name: source.frame(dt) for name, source in sources.items()}
            for frame in frames.values():
                adapter.publish(frame)
                if isinstance(frame, WavefunctionFrame):
                    cloud_adapter.publish_frame(frame)
            if frame_id % max(1, int(args.fps)) == 0:
                statuses = []
                if (frame := frames.get("spin_1_2_precession")) is not None:
                    status = f"bloch={tuple(round(v, 3) for v in frame.bloch_vector)}"
                    statuses.append(status)
                if (frame := frames.get("quantum_entanglement_epr")) is not None:
                    statuses.append(
                        f"EPR concurrence={frame.concurrence:.3f} CHSH={frame.chsh_maximum:.3f}"
                    )
                if (frame := frames.get("identical_particles_fermion_boson")) is not None:
                    statuses.append(
                        f"symmetry={frame.exchange_symmetry} swap={frame.swap_expectation:+.3f} "
                        f"coincidence={frame.coincidence_probability:.5f}"
                    )
                field_frame = next(
                    (value for value in frames.values() if isinstance(value, WavefunctionFrame)),
                    None,
                )
                if field_frame is not None:
                    statuses.append(
                        f"field={field_frame.source} E={field_frame.metadata.get('expectation_energy', 0.0):.3f}"
                    )
                relativistic_frame = next(
                    (value for value in frames.values() if isinstance(value, RelativisticLevelFrame)),
                    None,
                )
                if relativistic_frame is not None:
                    statuses.append(
                        f"Dirac-H fs={relativistic_frame.fine_structure_splitting:.8f}"
                    )
                dirac_frame = next(
                    (value for value in frames.values() if isinstance(value, DiracSpinorFieldFrame)),
                    None,
                )
                if dirac_frame is not None:
                    statuses.append(
                        f"Klein L/R={dirac_frame.left_probability:.3f}/{dirac_frame.right_probability:.3f}"
                    )
                simulation_time = next(iter(frames.values())).time
                print(
                    f"\rframe={frame_id} t={simulation_time:.3f} {' | '.join(statuses)}",
                    end="",
                    flush=True,
                )
            frame_id += 1
            deadline += dt
            time.sleep(max(0.0, deadline - time.monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        control_server.shutdown()
        control_server.server_close()
        control_thread.join(timeout=1.0)
        print("\nNative quantum instrument stream stopped.")


if __name__ == "__main__":
    main()
