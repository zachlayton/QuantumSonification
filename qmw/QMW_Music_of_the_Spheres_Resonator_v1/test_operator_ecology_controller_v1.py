from __future__ import annotations

from pathlib import Path

import numpy as np

from living_spectral_geometry_osc_v1 import (
    LivingOSCConfig,
    LivingSpectralGeometryOSCPublisher,
)
from living_spectral_geometry_v1 import LivingSpectralGeometry
from operator_ecology_controller_v1 import (
    GeometryMutationEvent,
    MaterialMutationEvent,
    MeasurementEvent,
    QuantumOperatorEcologyController,
    QuantumStateEvent,
    RecalculationEvent,
)
from test_living_spectral_geometry_v1 import grid_mesh, living_config


def bell_density_matrix() -> np.ndarray:
    state = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.complex128)
    state /= np.linalg.norm(state)
    return np.outer(state, state.conj())


class FakeOSCClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, object]] = []

    def send_message(self, address: str, value: object) -> None:
        self.messages.append((address, value))


def test_controller_emits_exact_typed_events() -> None:
    controller = QuantumOperatorEcologyController()
    observed = []
    controller.subscribe(observed.append)
    batch = controller.process_circuit(
        bell_density_matrix(),
        gates=("H(0)", "CX(0,1)"),
        circuit_id="bell",
        dispatch=False,
    )
    assert batch.event_types() == (
        "MaterialMutationEvent",
        "GeometryMutationEvent",
        "QuantumStateEvent",
        "RecalculationEvent",
    )
    assert isinstance(batch.events[0], MaterialMutationEvent)
    assert isinstance(batch.events[1], GeometryMutationEvent)
    assert isinstance(batch.events[2], QuantumStateEvent)
    assert isinstance(batch.events[3], RecalculationEvent)
    assert batch.snapshot.purity > 0.999999
    assert batch.snapshot.entropy_bits < 1e-10
    assert abs(batch.snapshot.mean_mutual_information - 2.0) < 1e-9
    assert abs(batch.snapshot.mean_concurrence - 1.0) < 1e-9
    assert batch.snapshot.context["circuit_id"] == "bell"
    assert observed == [batch]


def test_controller_dispatches_one_atomic_living_revision(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    config = living_config(debounce_ms=10.0)
    config = type(config)(
        spectral=config.spectral,
        material=type(config.material)(
            **{
                **config.material.__dict__,
                "model": "elastic_shell",
                "surface_tension": 100.0,
                "surface_density": 1.0,
                "bending_stiffness": 1.0,
            }
        ),
        quantum=config.quantum,
        acoustic=config.acoustic,
        debounce_ms=config.debounce_ms,
    )
    with LivingSpectralGeometry(
        vertices, faces, tmp_path, config=config
    ) as living:
        initial = living.recompute_now()
        controller = QuantumOperatorEcologyController(living)
        batch = controller.process_circuit(
            bell_density_matrix(),
            gates=("H", "CX"),
        )
        updated = living.wait(timeout=5.0)
        assert updated.revision == initial.revision + 1
        assert updated.reason == "circuit state update"
        assert updated.material_model == "elastic_shell"
        assert abs(updated.descriptors["quantum"]["purity"] - 1.0) < 1e-9
        material = next(
            event for event in batch.events if isinstance(event, MaterialMutationEvent)
        )
        with np.load(updated.paths["bundle_npz"], allow_pickle=False) as bundle:
            assert np.all(np.isfinite(bundle["frequencies_hz"]))
            assert len(bundle["mode_probabilities"]) == updated.mode_count
        assert material.resolved_changes["surface_tension"] > 3000.0


def test_measurement_emits_measurement_and_recalculation_events() -> None:
    controller = QuantumOperatorEcologyController()
    collapsed = np.diag([1.0, 0.0, 0.0, 0.0]).astype(np.complex128)
    batch = controller.process_measurement(
        collapsed,
        outcome="00",
        basis="ZZ",
        probability=0.5,
        strength=0.8,
        dispatch=False,
    )
    assert batch.event_types() == (
        "MaterialMutationEvent",
        "GeometryMutationEvent",
        "MeasurementEvent",
        "RecalculationEvent",
    )
    measurement = next(
        event for event in batch.events if isinstance(event, MeasurementEvent)
    )
    assert measurement.outcome == "00"
    assert measurement.basis == "ZZ"
    assert measurement.probability == 0.5
    assert measurement.hardening == 0.8


def test_living_osc_publishes_complete_revision(tmp_path: Path) -> None:
    vertices, faces = grid_mesh()
    client = FakeOSCClient()
    publisher = LivingSpectralGeometryOSCPublisher(
        client,
        LivingOSCConfig(
            crossfade_ms=375.0,
            activation_timeout_seconds=0.0,
        ),
    )
    with LivingSpectralGeometry(
        vertices, faces, tmp_path, config=living_config()
    ) as living:
        state = living.recompute_now()
        publisher.attach(living)
        addresses = {address for address, _ in client.messages}
        required = {
            "/living/version",
            "/living/revision",
            "/living/model",
            "/living/ir/path",
            "/living/ir/crossfade_ms",
            "/living/ir/candidate",
            "/living/ir/status",
            "/living/spectrum/eigenvalues",
            "/living/spectrum/frequencies",
            "/living/quantum/probabilities",
            "/living/timing/entropy_bits",
            "/living/timing/participation",
            "/living/timing/mode_count",
            "/living/timing/decay_seconds",
            "/living/timing/damping_rates",
            "/living/timing/mode_weights",
            "/living/publication/begin",
            "/living/publication/end",
        }
        assert required <= addresses
        assert publisher.last_revision == state.revision
        message_map = dict(client.messages)
        assert message_map["/living/ir/path"] == state.paths["ir_wav"]
        assert message_map["/living/ir/crossfade_ms"] == 375.0
        before = len(client.messages)
        assert not publisher.publish_state_file(tmp_path / "current_state.json")
        assert len(client.messages) == before
        publisher.handle_ready("/living/ir/ready", state.revision)
        assert publisher.candidate is not None
        assert publisher.candidate.status == "ready"
        publisher.handle_committed("/living/ir/committed", state.revision)
        assert publisher.candidate is None
        assert publisher.active is not None
        assert publisher.active.revision == state.revision
        publisher.detach()


def test_ir_activation_serializes_ready_crossfade_commit(
    tmp_path: Path,
) -> None:
    vertices, faces = grid_mesh()
    client = FakeOSCClient()
    publisher = LivingSpectralGeometryOSCPublisher(
        client,
        LivingOSCConfig(
            crossfade_ms=200.0,
            activation_timeout_seconds=0.0,
        ),
    )
    with LivingSpectralGeometry(
        vertices, faces, tmp_path, config=living_config()
    ) as living:
        first = living.recompute_now()
        publisher.attach(living)
        assert publisher.candidate is not None
        assert publisher.candidate.revision == first.revision

        publisher.handle_committed("/living/ir/committed", first.revision)
        assert publisher.active is None
        assert any(
            address == "/living/ir/ack/error"
            for address, _ in client.messages
        )

        publisher.handle_ready("/living/ir/ready", first.revision)
        assert publisher.candidate is not None
        assert publisher.candidate.status == "ready"
        assert any(
            address == "/living/ir/crossfade/start"
            and value == [first.revision, 200.0]
            for address, value in client.messages
        )

        living.update_material(schedule=False, damping_base=0.61)
        second = living.recompute_now("queued while crossfading")
        assert second.revision == first.revision + 1
        assert publisher.candidate is not None
        assert publisher.candidate.revision == first.revision
        assert any(
            address == "/living/ir/queued" and value == second.revision
            for address, value in client.messages
        )

        publisher.handle_committed("/living/ir/committed", first.revision)
        assert publisher.active is not None
        assert publisher.active.revision == first.revision
        assert publisher.candidate is not None
        assert publisher.candidate.revision == second.revision

        publisher.handle_ready("/living/ir/ready", second.revision)
        publisher.handle_committed("/living/ir/committed", second.revision)
        assert publisher.candidate is None
        assert publisher.active is not None
        assert publisher.active.revision == second.revision
        assert publisher.active.path == second.paths["ir_wav"]
        assert publisher.wait_for_commit(second.revision, timeout=0.1).revision == (
            second.revision
        )

        living.update_material(schedule=False, damping_base=0.73)
        third = living.recompute_now("candidate that fails to load")
        assert publisher.candidate is not None
        assert publisher.candidate.revision == third.revision
        publisher.handle_failed(
            "/living/ir/failed", third.revision, "buffer load failed"
        )
        assert publisher.candidate is None
        assert publisher.active is not None
        assert publisher.active.revision == second.revision
        assert any(
            address == "/living/ir/status"
            and value == ["failed", third.revision, "buffer load failed"]
            for address, value in client.messages
        )
        publisher.close()
