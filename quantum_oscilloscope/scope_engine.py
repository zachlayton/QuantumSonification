from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from qmw.core import QuantumStateFrame
from quantum_oscilloscope.resilient_udp import ResilientSimpleUDPClient
from quantum_oscilloscope.views import (
    BlochView,
    BohmView,
    CircuitDiagnosticsView,
    DensityMatrixView,
    EntanglementView,
    FluCoMaView,
    HamiltonianView,
    MeasurementView,
    MemoryView,
    PauliView,
    SpinView,
    TrajectoryView,
    VisualFieldView,
    WavepacketView,
)


class OscilloscopeView(Protocol):
    def send(
        self,
        frame: QuantumStateFrame,
        osc,
        visual_osc,
        config: "QuantumOscilloscopeConfig",
    ) -> None:
        ...


@dataclass
class QuantumOscilloscopeConfig:
    osc_host: str = "127.0.0.1"
    osc_port: int = 7400
    visual_osc_port: int = 7401
    send_density_rows: bool = True
    send_wavepacket: bool = True
    send_pauli_aliases: bool = False
    density_namespace: str = "/qmw/density"
    source_namespace: str = "/qmw/source"
    views: list[OscilloscopeView] = field(default_factory=list)


class QuantumOscilloscope:
    """OSC instrument that observes QMW state frames."""

    def __init__(self, config: QuantumOscilloscopeConfig | None = None) -> None:
        self.config = config or QuantumOscilloscopeConfig()
        self.osc = ResilientSimpleUDPClient(
            self.config.osc_host,
            self.config.osc_port,
        )
        self.visual_osc = ResilientSimpleUDPClient(
            self.config.osc_host,
            self.config.visual_osc_port,
        )
        self.views = self.config.views or [
            HamiltonianView(),
            BlochView(),
            SpinView(),
            FluCoMaView(),
            EntanglementView(),
            MeasurementView(),
            CircuitDiagnosticsView(),
            MemoryView(),
            TrajectoryView(),
            BohmView(),
            PauliView(),
            VisualFieldView(),
            DensityMatrixView(),
            WavepacketView(),
        ]

    def observe(self, frame: QuantumStateFrame) -> None:
        for view in self.views:
            view.send(frame, self.osc, self.visual_osc, self.config)
