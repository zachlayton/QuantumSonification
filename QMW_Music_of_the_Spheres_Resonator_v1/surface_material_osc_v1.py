#!/usr/bin/env python3
"""OSC controller for the canonical surface-material model registry."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import argparse
import threading
from typing import Any

import numpy as np
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from surface_material_models_v1 import (
    MODEL_ORDER,
    SurfaceMaterialConfig,
    SurfaceModalPacket,
    create_surface_model,
    damping_rate_from_t60,
    export_packet,
    load_spectral_npz,
    t60_from_damping_rate,
)


PARAMETER_FIELDS = {
    "tension": "surface_tension",
    "density": "surface_density",
    "stiffness": "bending_stiffness",
    "damping": "damping_base",
    "t60": "damping_base",
    "wave_speed": "effective_wave_speed",
    "conductivity_gain": "conductivity_gain",
    "leakage": "leakage_base",
}


class SurfaceMaterialOSCController:
    def __init__(
        self,
        spectral_packet: str | Path | dict[str, np.ndarray],
        config: SurfaceMaterialConfig = SurfaceMaterialConfig(),
        output_prefix: str | Path | None = None,
        client: Any | None = None,
        voltage: np.ndarray | None = None,
        conductivity: np.ndarray | None = None,
        leakage: np.ndarray | None = None,
    ) -> None:
        self.spectral = (
            load_spectral_npz(spectral_packet)
            if isinstance(spectral_packet, (str, Path))
            else dict(spectral_packet)
        )
        self.config = config
        self.output_prefix = None if output_prefix is None else Path(output_prefix)
        self.client = client
        self.fields: dict[str, np.ndarray] = {}
        if voltage is not None:
            self.fields["voltage"] = np.asarray(voltage, dtype=np.float64)
        if conductivity is not None:
            self.fields["conductivity"] = np.asarray(
                conductivity, dtype=np.float64
            )
        if leakage is not None:
            self.fields["leakage"] = np.asarray(leakage, dtype=np.float64)
        self.packet: SurfaceModalPacket | None = None
        self.revision = 0
        self.lock = threading.RLock()

    def _send(self, address: str, value: Any) -> None:
        if self.client is not None:
            self.client.send_message(address, value)

    def _model_name(self, value: Any) -> str:
        if isinstance(value, str) and value in MODEL_ORDER:
            return value
        try:
            return MODEL_ORDER[int(float(value)) % len(MODEL_ORDER)]
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"model must be one of {MODEL_ORDER} or an index"
            ) from exc

    def set_model(self, value: Any) -> None:
        with self.lock:
            self.config = replace(self.config, model=self._model_name(value))
        self.send_state()

    def set_parameter(self, name: str, value: Any) -> None:
        if name not in PARAMETER_FIELDS:
            raise ValueError(f"unknown surface parameter {name!r}")
        number = float(value)
        if name in {"density", "wave_speed"} and number <= 0:
            raise ValueError(f"{name} must be positive")
        if name == "t60" and number <= 0:
            raise ValueError("t60 must be positive")
        if name not in {"density", "wave_speed"} and number < 0:
            raise ValueError(f"{name} cannot be negative")
        stored_number = (
            damping_rate_from_t60(number) if name == "t60" else number
        )
        with self.lock:
            self.config = replace(
                self.config, **{PARAMETER_FIELDS[name]: stored_number}
            )
        self._send(f"/surface/state/{name}", number)

    def recalculate(self) -> SurfaceModalPacket:
        with self.lock:
            model = create_surface_model(
                vertices=self.spectral["vertices"],
                faces=self.spectral["faces"],
                eigenvalues=self.spectral["eigenvalues"],
                eigenvectors=self.spectral["eigenvectors"],
                config=self.config,
            )
            fields = dict(self.fields)
            if self.config.model == "bioelectric_surface" and "voltage" not in fields:
                fields["voltage"] = np.zeros(
                    len(self.spectral["vertices"]), dtype=np.float64
                )
            self.packet = model.solve(**fields)
            self.revision += 1
            if self.output_prefix is not None:
                export_packet(self.packet, self.config, self.output_prefix)

        self.send_packet()
        self.send_state()
        return self.packet

    def send_packet(self) -> None:
        if self.packet is None:
            return
        packet = self.packet
        self._send("/surface/modal/model", packet.model)
        self._send("/surface/modal/revision", self.revision)
        self._send("/surface/modal/count", len(packet.eigenvalues))
        self._send("/surface/modal/eigenvalues", packet.eigenvalues.tolist())
        self._send("/surface/modal/frequencies_hz", packet.frequencies_hz.tolist())
        self._send(
            "/surface/modal/angular_frequencies",
            packet.angular_frequencies.tolist(),
        )
        self._send(
            "/surface/modal/decay_times_seconds",
            packet.decay_times_seconds.tolist(),
        )
        self._send("/surface/modal/t60_seconds", packet.t60_seconds.tolist())
        self._send(
            "/surface/modal/damping_rates", packet.damping_rates.tolist()
        )
        self._send("/surface/modal/mode_weights", packet.mode_weights.tolist())

    def send_state(self) -> None:
        self._send("/surface/state/model", self.config.model)
        self._send("/surface/state/model_index", MODEL_ORDER.index(self.config.model))
        self._send("/surface/state/revision", self.revision)
        for osc_name, field_name in PARAMETER_FIELDS.items():
            value = float(getattr(self.config, field_name))
            if osc_name == "t60":
                value = float(t60_from_damping_rate(value))
            self._send(
                f"/surface/state/{osc_name}",
                value,
            )

    def handle_osc(self, address: str, *args: Any) -> None:
        try:
            command = address.removeprefix("/surface/")
            if command == "model":
                self.set_model(args[0])
            elif command in PARAMETER_FIELDS:
                self.set_parameter(command, args[0])
            elif command == "recalculate":
                self.recalculate()
            elif command == "status":
                self.send_state()
                self.send_packet()
            else:
                raise ValueError(f"unknown OSC address {address}")
        except Exception as exc:
            self._send("/surface/error", str(exc))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spectrum", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=7450)
    parser.add_argument("--out-host", default="127.0.0.1")
    parser.add_argument("--out-port", type=int, default=7400)
    parser.add_argument("--model", choices=MODEL_ORDER, default=MODEL_ORDER[0])
    parser.add_argument("--modes", type=int, default=32)
    parser.add_argument("--voltage", type=Path)
    args = parser.parse_args()

    client = SimpleUDPClient(args.out_host, args.out_port)
    controller = SurfaceMaterialOSCController(
        args.spectrum,
        SurfaceMaterialConfig(model=args.model, n_modes=args.modes),
        output_prefix=args.output,
        client=client,
        voltage=None if args.voltage is None else np.load(args.voltage),
    )
    controller.recalculate()
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(controller.handle_osc)
    server = ThreadingOSCUDPServer(
        (args.listen_host, args.listen_port), dispatcher
    )
    print("Surface Material OSC v1")
    print(f"  model:   {controller.config.model}")
    print(f"  control: {args.listen_host}:{args.listen_port}")
    print(f"  output:  {args.out_host}:{args.out_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
