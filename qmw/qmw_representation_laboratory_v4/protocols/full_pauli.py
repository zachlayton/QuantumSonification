"""Full Pauli protocol with explicit stochastic sampling policy."""

from __future__ import annotations

from typing import Any

from ..adapters import Full4QSynthesisAdapter
from ..core import (
    MeasurementProtocol,
    MeasurementRecord,
    SamplingPolicy,
    SamplingResolution,
)


class FullPauliTomography(MeasurementProtocol):
    name = "full4q_pauli_tomography"
    description = (
        "Four-qubit X/Y/Z tomography with 81 settings and 255 "
        "non-identity Pauli observables."
    )

    def __init__(
        self,
        *,
        sampling: SamplingPolicy | None = None,
        adapter: Full4QSynthesisAdapter | None = None,
    ) -> None:
        super().__init__(sampling)
        self.adapter = adapter or Full4QSynthesisAdapter()

    def measure(
        self,
        rho: Any,
        *,
        preset: str,
        representation: str,
        shots: int,
        sampling: SamplingResolution,
        source: str,
    ) -> MeasurementRecord:
        output = self.adapter.run(
            rho,
            preset=preset,
            representation=representation,
            shots=shots,
            seed=sampling.resolved_seed,
            source=source,
        )
        return MeasurementRecord(
            observable_estimates={
                item.label: float(item.expectation)
                for item in output.paulis
            },
            total_shots=output.total_shots,
            output=output,
            metadata={
                "settings": len(output.settings),
                "observables": len(output.paulis) - 1,
                "shots_per_setting": shots,
                "shot_semantics": "shots_per_setting",
            },
            sampling=sampling,
        )

    def metadata(self) -> dict[str, Any]:
        metadata = super().metadata()
        metadata.update(
            dimension=16,
            setting_count=81,
            non_identity_observable_count=255,
            axes=["X", "Y", "Z"],
            sampling_mode=self.sampling_policy.mode.value,
            shot_semantics="shots_per_setting",
        )
        return metadata
