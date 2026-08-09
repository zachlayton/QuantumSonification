#!/usr/bin/env python3
"""Analyze quantum organization and emit typed operator-ecology events."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import argparse
import json
import threading
import time
from typing import Any, Callable, Mapping

import numpy as np

if __package__:
    from .living_spectral_geometry_v1 import (
        LivingEventType,
        LivingOperatorEvent,
        LivingSpectralGeometry,
    )
else:  # Direct-script compatibility.
    from living_spectral_geometry_v1 import (
        LivingEventType,
        LivingOperatorEvent,
        LivingSpectralGeometry,
    )
from quantum_eigenfield_engine_v1 import (
    density_descriptors,
    infer_qubits,
    load_density_matrix,
    pauli_expectations,
    validate_density_matrix,
    von_neumann_entropy,
)


@dataclass(frozen=True)
class OperatorEcologyPolicy:
    tension_min: float = 0.4
    tension_max: float = 3200.0
    density_min: float = 0.5
    density_max: float = 2.0
    stiffness_min: float = 0.0
    stiffness_max: float = 24.0
    # Entropy maps from a long but typical 10 s T60 to a short 1 s T60.
    # These are damping rates, not hard limits; external material events may
    # deliberately exceed the normal musical range in either direction.
    damping_min: float = 0.6907755278982137
    damping_max: float = 6.907755278982137
    conductivity_min: float = 0.25
    conductivity_max: float = 2.5
    leakage_min: float = 0.001
    leakage_max: float = 0.12
    measurement_hardening: float = 0.40
    geometry_mutation_gain: float = 0.35


@dataclass(frozen=True)
class QuantumOrganizationSnapshot:
    revision: int
    created_at: float
    source: str
    dimension: int
    n_qubits: int | None
    purity: float
    entropy_bits: float
    entropy_normalized: float
    participation_ratio: float
    participation_normalized: float
    coherence_l1: float
    coherence_normalized: float
    dominant_population: float
    mean_local_z: float
    mean_pair_correlation: float
    mean_mutual_information: float
    max_mutual_information: float
    mean_concurrence: float
    max_concurrence: float
    pauli_expectations: Mapping[str, float]
    context: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pauli_expectations"] = dict(self.pauli_expectations)
        data["context"] = dict(self.context)
        return data


@dataclass(frozen=True)
class QuantumStateEvent:
    rho: np.ndarray
    purity: float
    entropy_normalized: float
    coherence_normalized: float
    source: str


@dataclass(frozen=True)
class MaterialMutationEvent:
    tension_order: float
    density_bias: float
    rigidity_order: float
    damping_disorder: float
    conductivity_order: float
    leakage_disorder: float
    resolved_changes: Mapping[str, float]


@dataclass(frozen=True)
class GeometryMutationEvent:
    growth_order: float
    roughness: float
    connectivity: float
    mutation_strength: float


@dataclass(frozen=True)
class MeasurementEvent:
    post_measurement_rho: np.ndarray
    outcome: Any
    basis: str
    probability: float | None
    hardening: float


@dataclass(frozen=True)
class RecalculationEvent:
    reason: str
    crossfade_ms: float = 250.0


OperatorEcologyEvent = (
    QuantumStateEvent
    | MaterialMutationEvent
    | GeometryMutationEvent
    | MeasurementEvent
    | RecalculationEvent
)


@dataclass(frozen=True)
class OperatorEventBatch:
    revision: int
    created_at: float
    source: str
    reason: str
    snapshot: QuantumOrganizationSnapshot
    events: tuple[OperatorEcologyEvent, ...]

    def event_types(self) -> tuple[str, ...]:
        return tuple(type(event).__name__ for event in self.events)


GeometryEventAdapter = Callable[
    [GeometryMutationEvent, LivingSpectralGeometry],
    LivingOperatorEvent | None,
]


def _lerp(low: float, high: float, phase: float) -> float:
    return low + (high - low) * float(np.clip(phase, 0.0, 1.0))


def reduced_density_matrix(rho: np.ndarray, keep: tuple[int, ...]) -> np.ndarray:
    rho = validate_density_matrix(rho)
    n_qubits = infer_qubits(rho.shape[0])
    if n_qubits is None:
        raise ValueError("reduced density matrices require a qubit dimension")
    keep = tuple(sorted(set(int(index) for index in keep)))
    if not keep or keep[0] < 0 or keep[-1] >= n_qubits:
        raise ValueError("keep contains an invalid qubit index")
    tensor = rho.reshape((2,) * (2 * n_qubits))
    current_qubits = n_qubits
    for qubit in sorted(set(range(n_qubits)).difference(keep), reverse=True):
        tensor = np.trace(
            tensor,
            axis1=qubit,
            axis2=qubit + current_qubits,
        )
        current_qubits -= 1
    dimension = 2 ** len(keep)
    return validate_density_matrix(tensor.reshape(dimension, dimension))


def two_qubit_concurrence(rho_pair: np.ndarray) -> float:
    rho_pair = validate_density_matrix(rho_pair)
    if rho_pair.shape != (4, 4):
        raise ValueError("concurrence requires a two-qubit density matrix")
    sigma_y = np.array([[0.0, -1j], [1j, 0.0]], dtype=np.complex128)
    spin_flip = np.kron(sigma_y, sigma_y)
    product = rho_pair @ spin_flip @ rho_pair.conj() @ spin_flip
    eigenvalues = np.linalg.eigvals(product)
    roots = np.sort(
        np.sqrt(np.maximum(np.real(eigenvalues), 0.0))
    )[::-1]
    return float(np.clip(roots[0] - np.sum(roots[1:]), 0.0, 1.0))


def pairwise_quantum_relations(
    rho: np.ndarray,
) -> tuple[list[float], list[float]]:
    n_qubits = infer_qubits(rho.shape[0])
    if n_qubits is None or n_qubits < 2:
        return [], []
    mutual_information: list[float] = []
    concurrence: list[float] = []
    singles = {
        index: reduced_density_matrix(rho, (index,))
        for index in range(n_qubits)
    }
    for first in range(n_qubits):
        for second in range(first + 1, n_qubits):
            pair = reduced_density_matrix(rho, (first, second))
            mutual_information.append(
                max(
                    0.0,
                    von_neumann_entropy(singles[first])
                    + von_neumann_entropy(singles[second])
                    - von_neumann_entropy(pair),
                )
            )
            concurrence.append(two_qubit_concurrence(pair))
    return mutual_information, concurrence


class QuantumOperatorEcologyController:
    """Convert quantum organization into semantic, typed events."""

    def __init__(
        self,
        living_geometry: LivingSpectralGeometry | None = None,
        policy: OperatorEcologyPolicy = OperatorEcologyPolicy(),
        geometry_adapter: GeometryEventAdapter | None = None,
    ) -> None:
        self.living_geometry = living_geometry
        self.policy = policy
        self.geometry_adapter = geometry_adapter
        self._revision = 0
        self._snapshot: QuantumOrganizationSnapshot | None = None
        self._batch: OperatorEventBatch | None = None
        self._listeners: list[Callable[[OperatorEventBatch], None]] = []
        self._lock = threading.RLock()

    @property
    def snapshot(self) -> QuantumOrganizationSnapshot | None:
        with self._lock:
            return self._snapshot

    @property
    def batch(self) -> OperatorEventBatch | None:
        with self._lock:
            return self._batch

    def subscribe(
        self, listener: Callable[[OperatorEventBatch], None]
    ) -> Callable[[], None]:
        with self._lock:
            self._listeners.append(listener)

        def unsubscribe() -> None:
            with self._lock:
                if listener in self._listeners:
                    self._listeners.remove(listener)

        return unsubscribe

    def analyze(
        self,
        rho: np.ndarray,
        *,
        source: str = "density_matrix",
        context: Mapping[str, Any] | None = None,
    ) -> QuantumOrganizationSnapshot:
        rho = validate_density_matrix(rho)
        descriptors = density_descriptors(rho)
        pauli = pauli_expectations(rho)
        entropy_normalized = descriptors.entropy_bits / max(
            descriptors.max_mixed_entropy_bits, 1e-15
        )
        participation = 1.0 / max(descriptors.purity, 1e-15)
        participation_normalized = (
            participation - 1.0
        ) / max(descriptors.dimension - 1.0, 1.0)
        coherence_normalized = descriptors.coherence_l1 / max(
            descriptors.dimension - 1.0, 1.0
        )

        n_qubits = descriptors.n_qubits
        local_z: list[float] = []
        pair_correlations: list[float] = []
        if n_qubits is not None:
            for qubit in range(n_qubits):
                label = ["I"] * n_qubits
                label[qubit] = "Z"
                local_z.append(pauli.get("".join(label), 0.0))
            for label, value in pauli.items():
                if sum(symbol != "I" for symbol in label) == 2:
                    pair_correlations.append(abs(value))
        mutual_information, concurrence = pairwise_quantum_relations(rho)

        with self._lock:
            self._revision += 1
            revision = self._revision
        snapshot = QuantumOrganizationSnapshot(
            revision=revision,
            created_at=time.time(),
            source=source,
            dimension=descriptors.dimension,
            n_qubits=n_qubits,
            purity=descriptors.purity,
            entropy_bits=descriptors.entropy_bits,
            entropy_normalized=float(np.clip(entropy_normalized, 0.0, 1.0)),
            participation_ratio=participation,
            participation_normalized=float(
                np.clip(participation_normalized, 0.0, 1.0)
            ),
            coherence_l1=descriptors.coherence_l1,
            coherence_normalized=float(
                np.clip(coherence_normalized, 0.0, 1.0)
            ),
            dominant_population=descriptors.dominant_population,
            mean_local_z=float(np.mean(local_z)) if local_z else 0.0,
            mean_pair_correlation=(
                float(np.mean(pair_correlations))
                if pair_correlations
                else 0.0
            ),
            mean_mutual_information=(
                float(np.mean(mutual_information))
                if mutual_information
                else 0.0
            ),
            max_mutual_information=(
                float(np.max(mutual_information))
                if mutual_information
                else 0.0
            ),
            mean_concurrence=(
                float(np.mean(concurrence)) if concurrence else 0.0
            ),
            max_concurrence=(
                float(np.max(concurrence)) if concurrence else 0.0
            ),
            pauli_expectations=pauli,
            context={} if context is None else dict(context),
        )
        with self._lock:
            self._snapshot = snapshot
        return snapshot

    def _material_intention(
        self,
        snapshot: QuantumOrganizationSnapshot,
        measurement_strength: float = 0.0,
    ) -> MaterialMutationEvent:
        policy = self.policy
        tension_order = snapshot.purity
        damping_disorder = snapshot.entropy_normalized
        rigidity_order = snapshot.coherence_normalized
        density_bias = float(np.clip(-snapshot.mean_local_z, -1.0, 1.0))
        density_phase = 0.5 * (density_bias + 1.0)
        conductivity_order = float(
            np.clip(snapshot.mean_mutual_information / 2.0, 0.0, 1.0)
        )
        leakage_disorder = snapshot.entropy_normalized
        hardening = float(np.clip(measurement_strength, 0.0, 1.0))
        hardening_gain = 1.0 + policy.measurement_hardening * hardening
        damping_gain = 1.0 - 0.5 * policy.measurement_hardening * hardening
        changes = {
            "surface_tension": _lerp(
                policy.tension_min, policy.tension_max, tension_order
            )
            * hardening_gain,
            "surface_density": _lerp(
                policy.density_min, policy.density_max, density_phase
            ),
            "bending_stiffness": _lerp(
                policy.stiffness_min, policy.stiffness_max, rigidity_order
            )
            * hardening_gain,
            "damping_base": _lerp(
                policy.damping_min, policy.damping_max, damping_disorder
            )
            * damping_gain,
            "conductivity_base": _lerp(
                policy.conductivity_min,
                policy.conductivity_max,
                conductivity_order,
            ),
            "leakage_base": _lerp(
                policy.leakage_min,
                policy.leakage_max,
                leakage_disorder,
            ),
        }
        return MaterialMutationEvent(
            tension_order=tension_order,
            density_bias=density_bias,
            rigidity_order=rigidity_order,
            damping_disorder=damping_disorder,
            conductivity_order=conductivity_order,
            leakage_disorder=leakage_disorder,
            resolved_changes=changes,
        )

    def _geometry_intention(
        self,
        snapshot: QuantumOrganizationSnapshot,
        measurement_strength: float = 0.0,
    ) -> GeometryMutationEvent:
        return GeometryMutationEvent(
            growth_order=float(
                np.clip(
                    snapshot.purity * snapshot.coherence_normalized,
                    0.0,
                    1.0,
                )
            ),
            roughness=snapshot.entropy_normalized,
            connectivity=float(
                np.clip(snapshot.mean_mutual_information / 2.0, 0.0, 1.0)
            ),
            mutation_strength=float(
                np.clip(
                    self.policy.geometry_mutation_gain
                    * (
                        measurement_strength
                        + (1.0 - snapshot.purity)
                    ),
                    0.0,
                    1.0,
                )
            ),
        )

    def create_batch(
        self,
        rho: np.ndarray,
        *,
        source: str = "density_matrix",
        reason: str = "quantum organization update",
        context: Mapping[str, Any] | None = None,
        measurement: Mapping[str, Any] | None = None,
    ) -> OperatorEventBatch:
        normalized_rho = validate_density_matrix(rho)
        snapshot = self.analyze(
            normalized_rho, source=source, context=context
        )
        measurement_strength = 0.0
        if measurement is not None:
            measurement_strength = float(
                np.clip(measurement.get("strength", 1.0), 0.0, 1.0)
            )
        events: list[OperatorEcologyEvent] = [
            self._material_intention(snapshot, measurement_strength),
            self._geometry_intention(snapshot, measurement_strength),
        ]
        if measurement is None:
            events.append(
                QuantumStateEvent(
                    rho=normalized_rho,
                    purity=snapshot.purity,
                    entropy_normalized=snapshot.entropy_normalized,
                    coherence_normalized=snapshot.coherence_normalized,
                    source=source,
                )
            )
        else:
            events.append(
                MeasurementEvent(
                    post_measurement_rho=normalized_rho,
                    outcome=measurement.get("outcome"),
                    basis=str(measurement.get("basis", "computational")),
                    probability=(
                        None
                        if measurement.get("probability") is None
                        else float(measurement["probability"])
                    ),
                    hardening=measurement_strength,
                )
            )
        events.append(RecalculationEvent(reason=reason))
        batch = OperatorEventBatch(
            revision=snapshot.revision,
            created_at=time.time(),
            source=source,
            reason=reason,
            snapshot=snapshot,
            events=tuple(events),
        )
        with self._lock:
            self._batch = batch
            listeners = list(self._listeners)
        for listener in listeners:
            listener(batch)
        return batch

    def dispatch(
        self,
        batch: OperatorEventBatch,
        living_geometry: LivingSpectralGeometry | None = None,
    ) -> int:
        living = living_geometry or self.living_geometry
        if living is None:
            raise ValueError("dispatch requires a LivingSpectralGeometry")
        should_recalculate = False
        recalculation_reason = batch.reason
        for event in batch.events:
            if isinstance(event, MaterialMutationEvent):
                living.update_material(
                    schedule=False,
                    reason=batch.reason,
                    **dict(event.resolved_changes),
                )
            elif isinstance(event, GeometryMutationEvent):
                if self.geometry_adapter is not None:
                    living_event = self.geometry_adapter(event, living)
                    if living_event is not None:
                        living.apply_event(living_event, schedule=False)
            elif isinstance(event, QuantumStateEvent):
                living.update_quantum_state(
                    event.rho,
                    schedule=False,
                    reason=batch.reason,
                )
            elif isinstance(event, MeasurementEvent):
                living.apply_event(
                    LivingOperatorEvent(
                        LivingEventType.MEASUREMENT,
                        {
                            "rho": event.post_measurement_rho,
                            "outcome": event.outcome,
                            "basis": event.basis,
                            "probability": event.probability,
                        },
                        batch.reason,
                    ),
                    schedule=False,
                )
            elif isinstance(event, RecalculationEvent):
                should_recalculate = True
                recalculation_reason = event.reason
        if not should_recalculate:
            raise ValueError("event batch contains no RecalculationEvent")
        return living.schedule_recompute(reason=recalculation_reason)

    def process_density_matrix(
        self,
        rho: np.ndarray,
        *,
        source: str = "density_matrix",
        reason: str = "quantum organization update",
        context: Mapping[str, Any] | None = None,
        dispatch: bool = True,
    ) -> OperatorEventBatch:
        batch = self.create_batch(
            rho,
            source=source,
            reason=reason,
            context=context,
        )
        if dispatch:
            self.dispatch(batch)
        return batch

    def process_circuit(
        self,
        rho: np.ndarray,
        *,
        gates: list[str] | tuple[str, ...] = (),
        circuit_id: str | None = None,
        dispatch: bool = True,
    ) -> OperatorEventBatch:
        return self.process_density_matrix(
            rho,
            source="circuit",
            reason="circuit state update",
            context={"gates": list(gates), "circuit_id": circuit_id},
            dispatch=dispatch,
        )

    def process_measurement(
        self,
        post_measurement_rho: np.ndarray,
        *,
        outcome: Any,
        basis: str = "computational",
        probability: float | None = None,
        strength: float = 1.0,
        context: Mapping[str, Any] | None = None,
        dispatch: bool = True,
    ) -> OperatorEventBatch:
        batch = self.create_batch(
            post_measurement_rho,
            source="measurement",
            reason=f"measurement outcome {outcome}",
            context=context,
            measurement={
                "outcome": outcome,
                "basis": basis,
                "probability": probability,
                "strength": strength,
            },
        )
        if dispatch:
            self.dispatch(batch)
        return batch

    def export_snapshot(self, path: str | Path) -> Path:
        with self._lock:
            if self._snapshot is None or self._batch is None:
                raise RuntimeError("no operator-ecology analysis is available")
            payload = {
                "controller": "operator_ecology_controller_v1",
                "snapshot": self._snapshot.to_dict(),
                "event_types": list(self._batch.event_types()),
                "policy": asdict(self.policy),
            }
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rho", type=Path)
    parser.add_argument("--rho-key", default="rho")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", default="density_matrix")
    args = parser.parse_args()
    rho = load_density_matrix(args.rho, args.rho_key)
    controller = QuantumOperatorEcologyController()
    batch = controller.process_density_matrix(
        rho, source=args.source, dispatch=False
    )
    controller.export_snapshot(args.output)
    print("Operator Ecology Controller v1")
    print(f"  revision:    {batch.revision}")
    print(f"  purity:      {batch.snapshot.purity:.6f}")
    print(f"  entropy:     {batch.snapshot.entropy_bits:.6f} bits")
    print(f"  events:      {', '.join(batch.event_types())}")
    print(f"  snapshot:    {args.output}")


if __name__ == "__main__":
    main()
