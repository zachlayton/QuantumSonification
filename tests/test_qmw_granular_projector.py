from __future__ import annotations

import numpy as np

from qmw.core import PhysicsFrame, QuantumStateFrame, StateBus
from qmw.io import GranularOSCPublisher, LiveGranularBridge
from qmw.projectors import QuantumGranularProjector


class RecordingClient:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


def test_projector_maps_live_transport_without_future_normalization():
    projector = QuantumGranularProjector()
    rho = np.zeros((16, 16), dtype=complex)
    rho[8, 8] = 1.0

    frame = QuantumStateFrame(
        t=0.5,
        dt=0.01,
        rho=rho,
        arrays={
            "site_populations": np.array([1.0, 0.0, 0.0, 0.0]),
            "edge_currents": np.array([0.0, 0.0, 0.0]),
        },
        metadata={"state_revision": 17},
    )

    control = projector.project_state(frame)

    assert control.index == 17
    assert control.time == 0.5
    assert control.position == 0.0
    assert control.duration_ms == projector.duration_min_ms
    assert np.isclose(control.rate, 1.0)
    assert np.isclose(control.amplitude, projector.amplitude_max)
    assert control.pan == 0.0
    assert control.density_hz == projector.density_min_hz


def test_projector_uses_current_direction_center_and_activity():
    projector = QuantumGranularProjector(current_scale=1.0)
    rho = np.zeros((16, 16), dtype=complex)
    rho[8, 8] = 1.0

    frame = QuantumStateFrame(
        t=1.0,
        dt=0.01,
        rho=rho,
        arrays={
            "site_populations": np.array([0.25, 0.25, 0.25, 0.25]),
            "edge_currents": np.array([0.0, 0.0, 2.0]),
        },
    )

    control = projector.project_state(frame)

    assert np.isclose(control.position, 0.5)
    assert np.isclose(control.duration_ms, projector.duration_max_ms)
    assert np.isclose(control.rate, projector.rate_max)
    assert control.pan > 0.0
    assert control.density_hz > projector.density_min_hz


def test_projector_maps_complete_physics_frame():
    samples = 8
    t = np.linspace(0.0, 1.0, samples)
    rho = np.zeros((samples, 16, 16), dtype=complex)
    rho[:, 0, 0] = 1.0

    populations = np.zeros((samples, 4))
    populations[:, 0] = np.linspace(1.0, 0.0, samples)
    populations[:, 3] = np.linspace(0.0, 1.0, samples)
    currents = np.zeros((samples, 3))
    currents[:, 1] = np.linspace(-1.0, 1.0, samples)

    frame = PhysicsFrame(
        t=t,
        rho=rho,
        observables={
            "site_populations": populations,
            "edge_currents": currents,
        },
    )

    controls = QuantumGranularProjector().project(frame)

    assert controls.position.shape == (samples,)
    assert controls.duration_ms.shape == (samples,)
    assert controls.rate.shape == (samples,)
    assert controls.amplitude.shape == (samples,)
    assert controls.pan.shape == (samples,)
    assert controls.density_hz.shape == (samples,)
    assert controls.position[0] < controls.position[-1]


def test_live_bridge_publishes_state_bus_ticks_as_qmw_grain_osc():
    bus = StateBus()
    client = RecordingClient()
    publisher = GranularOSCPublisher(client=client)
    bridge = LiveGranularBridge(bus, publisher)

    rho = np.zeros((16, 16), dtype=complex)
    rho[8, 8] = 1.0
    frame = QuantumStateFrame(
        t=2.0,
        dt=0.01,
        rho=rho,
        arrays={
            "site_populations": np.array([1.0, 0.0, 0.0, 0.0]),
            "edge_currents": np.array([0.25, 0.0, 0.0]),
        },
        metadata={"state_revision": 23},
    )

    bus.publish(frame)

    assert len(client.messages) == 1
    address, payload = client.messages[0]
    assert address == "/qmw/grain"
    assert payload[0] == 23
    assert payload[1] == 2.0
    assert len(payload) == 8
    assert bridge.last_control is not None

    bridge.close()
