"""
classical_shadow_4q.py

Local-Pauli classical-shadow sampler for a four-qubit density matrix.

This module is deliberately separate from:
    - hamiltonian/mutator.py
    - hamiltonian/shadow_mutator.py
    - density/density_matrix_engine_4q.py

It performs no Hamiltonian mutation and no density-matrix evolution.

Workflow
--------
1. The density engine evolves rho.
2. ShadowMutator optionally proposes a randomized local basis, e.g. ("X","Z","Y","X").
3. ClassicalShadowSampler4Q samples a bit outcome in that basis from rho.
4. The sampler appends the record to a rolling archive.
5. The engine asks for Pauli-string estimates from that archive.

The estimator implemented here is the standard local-Pauli unbiased estimator:

    E[P] = mean_s [ 3^w(P) * indicator(bases_s match P)
                    * product_j eigenvalue(outcome_s,j) ]

where:
    - P is a Pauli string such as "XZIY",
    - w(P) is the number of non-identity factors,
    - matching means every non-I Pauli factor equals the sampled basis,
    - measurement bit 0 maps to eigenvalue +1 and bit 1 maps to -1.

This is ideal for an initial expressive/performative implementation. For hardware
execution, feed it real shot outcomes after basis rotations rather than sampling
from a simulated rho.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import math
import time
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

import numpy as np


PAULI_LABELS: Tuple[str, str, str] = ("X", "Y", "Z")
IDENTITY = "I"

PAULI_MATRICES: Dict[str, np.ndarray] = {
    "I": np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.complex128),
    "X": np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128),
    "Y": np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128),
    "Z": np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128),
}

# Columns are eigenvectors ordered by computational outcome:
# bit 0 -> +1 eigenstate, bit 1 -> -1 eigenstate.
MEASUREMENT_EIGENVECTORS: Dict[str, np.ndarray] = {
    "Z": np.array(
        [[1.0, 0.0], [0.0, 1.0]],
        dtype=np.complex128,
    ),
    "X": np.array(
        [[1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)],
         [1.0 / math.sqrt(2.0), -1.0 / math.sqrt(2.0)]],
        dtype=np.complex128,
    ),
    "Y": np.array(
        [[1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)],
         [1.0j / math.sqrt(2.0), -1.0j / math.sqrt(2.0)]],
        dtype=np.complex128,
    ),
}


@dataclass(frozen=True)
class ShadowRecord:
    """One local-Pauli measurement snapshot."""

    timestamp: float
    bases: Tuple[str, ...]
    outcomes: Tuple[int, ...]
    probabilities: Tuple[float, ...]
    n_qubits: int
    context: Dict[str, Any]


@dataclass(frozen=True)
class PauliEstimate:
    """A rolling-archive estimate of one Pauli observable."""

    pauli_string: str
    estimate: float
    standard_error: float
    matching_samples: int
    total_samples: int
    support_fraction: float
    minimum_support: float
    is_supported: bool
    weight: int


class ClassicalShadowSampler4Q:
    """
    Rolling local-Pauli classical-shadow sampler.

    The class defaults to four qubits but remains valid for any small n-qubit
    density matrix whose dimension is 2**n.
    """

    def __init__(
        self,
        n_qubits: int = 4,
        archive_size: int = 256,
        seed: Optional[int] = None,
    ) -> None:
        self.n_qubits = self._validate_n_qubits(n_qubits)
        self.archive_size = max(1, int(archive_size))
        self._rng = np.random.default_rng(seed)
        self.archive: deque[ShadowRecord] = deque(maxlen=self.archive_size)

    # ------------------------------------------------------------------
    # Public archive / configuration controls
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Discard all prior shadow records."""
        self.archive.clear()

    def set_seed(self, seed: Optional[int]) -> None:
        """Reset randomized basis/outcome sampling reproducibly."""
        self._rng = np.random.default_rng(seed)

    def set_archive_size(self, archive_size: int) -> None:
        """Resize the rolling archive while retaining the most recent records."""
        archive_size = max(1, int(archive_size))
        self.archive_size = archive_size
        self.archive = deque(self.archive, maxlen=archive_size)

    @property
    def records(self) -> Tuple[Dict[str, Any], ...]:
        """Serializable, immutable snapshot of the current archive."""
        return tuple(asdict(record) for record in self.archive)

    @property
    def latest_record(self) -> Optional[Dict[str, Any]]:
        """Most recent record, suitable for debugging or OSC serialization."""
        if not self.archive:
            return None
        return asdict(self.archive[-1])

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    def sample(
        self,
        rho: np.ndarray,
        *,
        bases: Optional[Sequence[str]] = None,
        context: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Sample one local-Pauli shadow record from density matrix rho.

        Parameters
        ----------
        rho:
            A normalized 2**n by 2**n density matrix.
        bases:
            Optional explicit local basis tuple/list, e.g. ("X","Z","Y","X").
            When omitted, each qubit independently receives random X/Y/Z.
            Supply `ShadowMutator.latest_shadow_context["local_bases"]` here
            to preserve the mutator's proposed basis.
        context:
            Optional lightweight metadata such as mutation source, purity,
            circuit step, or the ShadowMutator context.
        timestamp:
            Optional monotonic or engine time. Defaults to time.monotonic().

        Returns
        -------
        dict
            Serialized ShadowRecord.
        """
        rho = self._validated_density_matrix(rho)

        resolved_bases = (
            self.random_local_bases()
            if bases is None
            else self._validate_bases(bases)
        )

        rotated_rho = self._rotate_density_into_measurement_frame(
            rho,
            resolved_bases,
        )
        probabilities = self._computational_probabilities(rotated_rho)
        outcome_index = int(
            self._rng.choice(len(probabilities), p=probabilities)
        )
        outcomes = self._index_to_bits(outcome_index, self.n_qubits)

        record = ShadowRecord(
            timestamp=float(time.monotonic() if timestamp is None else timestamp),
            bases=resolved_bases,
            outcomes=outcomes,
            probabilities=tuple(float(value) for value in probabilities),
            n_qubits=self.n_qubits,
            context=dict(context or {}),
        )
        self.archive.append(record)
        return asdict(record)

    def sample_from_shadow_context(
        self,
        rho: np.ndarray,
        shadow_context: Optional[Mapping[str, Any]],
        *,
        context: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Sample using a basis proposed by ShadowMutator when it is compatible.

        This method is the intended bridge between `ShadowMutator` and the
        density engine. If the context is absent or has no usable basis, a
        fresh random local-Pauli basis is drawn.
        """
        merged_context: Dict[str, Any] = {}
        if shadow_context:
            merged_context["shadow_mutator"] = dict(shadow_context)
        if context:
            merged_context.update(dict(context))

        candidate_bases = None
        if shadow_context:
            raw_bases = shadow_context.get("local_bases")
            if raw_bases is not None:
                try:
                    candidate_bases = self._validate_bases(raw_bases)
                except (TypeError, ValueError):
                    candidate_bases = None

        return self.sample(
            rho,
            bases=candidate_bases,
            context=merged_context,
            timestamp=timestamp,
        )

    def random_local_bases(self) -> Tuple[str, ...]:
        """Draw an independent X/Y/Z basis for each qubit."""
        values = self._rng.choice(PAULI_LABELS, size=self.n_qubits)
        return tuple(str(value) for value in values)

    # ------------------------------------------------------------------
    # Estimation
    # ------------------------------------------------------------------

    def estimate_pauli(
        self,
        pauli_string: str,
        *,
        records: Optional[Iterable[ShadowRecord]] = None,
        minimum_support: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Estimate <P> from the rolling local-Pauli archive.

        The returned `standard_error` is an empirical standard error for the
        full unbiased sample estimator. It is useful musically as a confidence/
        instability control, but should not be treated as a rigorous finite-
        sample confidence interval for all experimental settings.
        """
        pauli = self._validate_pauli_string(pauli_string)
        selected_records = (
            tuple(self.archive) if records is None else tuple(records)
        )
        total_samples = len(selected_records)
        weight = sum(label != IDENTITY for label in pauli)
        minimum_support = float(minimum_support)
        if not 0.0 <= minimum_support <= 1.0:
            raise ValueError("minimum_support must be between 0.0 and 1.0.")

        if total_samples == 0:
            return asdict(
                PauliEstimate(
                    pauli_string=pauli,
                    estimate=0.0,
                    standard_error=float("inf"),
                    matching_samples=0,
                    total_samples=0,
                    support_fraction=0.0,
                    minimum_support=minimum_support,
                    is_supported=False,
                    weight=weight,
                )
            )

        scale = float(3**weight)
        contributions = np.zeros(total_samples, dtype=np.float64)
        matching_samples = 0

        for index, record in enumerate(selected_records):
            contribution = self._single_record_contribution(record, pauli, scale)
            contributions[index] = contribution
            if contribution != 0.0:
                matching_samples += 1

        estimate = float(np.mean(contributions))
        if total_samples > 1:
            standard_error = float(
                np.std(contributions, ddof=1) / math.sqrt(total_samples)
            )
        else:
            standard_error = float("inf")

        support_fraction = float(matching_samples / total_samples)
        is_supported = support_fraction >= minimum_support

        return asdict(
            PauliEstimate(
                pauli_string=pauli,
                estimate=estimate,
                standard_error=standard_error,
                matching_samples=matching_samples,
                total_samples=total_samples,
                support_fraction=support_fraction,
                minimum_support=minimum_support,
                is_supported=is_supported,
                weight=weight,
            )
        )

    def estimate_bank(
        self,
        pauli_strings: Iterable[str],
        *,
        minimum_support: float = 0.0,
    ) -> Dict[str, Dict[str, Any]]:
        """Estimate a curated bank of Pauli observables from one archive."""
        return {
            pauli_string: self.estimate_pauli(
                pauli_string,
                minimum_support=minimum_support,
            )
            for pauli_string in pauli_strings
        }

    def rank_pauli_bank(
        self,
        pauli_strings: Iterable[str],
        *,
        top_k: Optional[int] = None,
        minimum_support: float = 0.0,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Rank a bank by absolute estimated magnitude.

        `minimum_support` prevents musically salient but poorly sampled
        high-weight strings from constantly taking priority.
        """
        estimates = list(
            self.estimate_bank(
                pauli_strings,
                minimum_support=minimum_support,
            ).values()
        )
        filtered = [
            estimate for estimate in estimates if bool(estimate["is_supported"])
        ]
        ranked = sorted(
            filtered,
            key=lambda estimate: abs(float(estimate["estimate"])),
            reverse=True,
        )
        if top_k is not None:
            ranked = ranked[: max(0, int(top_k))]
        return tuple(ranked)

    @staticmethod
    def default_musical_bank() -> Tuple[str, ...]:
        """
        A readable initial 4-qubit observable bank.

        - 4 local operators
        - 12 pair operators
        - 4 three-body operators
        - 4 global four-body operators

        These are intentionally curated rather than an indiscriminate list of
        all 255 non-identity strings.
        """
        return (
            # Local tendencies
            "ZIII", "IZII", "IIZI", "IIIZ",
            # Pairwise correlations
            "ZZII", "ZIZI", "ZIIZ", "IZZI", "IZIZ", "IIZZ",
            "XXII", "XIXI", "XIIX",
            "YYII", "YIYI", "YIIY",
            # Three-body structures
            "XXZI", "XZYI", "YZZI", "IZXY",
            # Global structures
            "XXXX", "ZZZZ", "XZYX", "YXXZ",
        )

    # ------------------------------------------------------------------
    # Direct exact reference utilities
    # ------------------------------------------------------------------

    def exact_pauli_expectation(
        self,
        rho: np.ndarray,
        pauli_string: str,
    ) -> float:
        """
        Direct Tr(rho P) reference value.

        Use this for validation during simulation, not as the live shadow
        estimate in performance. On actual hardware the direct density matrix
        is unavailable, whereas the shadow estimate remains available.
        """
        rho = self._validated_density_matrix(rho)
        pauli = self._validate_pauli_string(pauli_string)
        operator = self._pauli_operator(pauli)
        value = np.trace(rho @ operator)
        return float(np.real_if_close(value, tol=1_000))

    # ------------------------------------------------------------------
    # Internal implementation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_n_qubits(n_qubits: int) -> int:
        n_qubits = int(n_qubits)
        if n_qubits < 1:
            raise ValueError("n_qubits must be at least 1.")
        return n_qubits

    def _validated_density_matrix(self, rho: np.ndarray) -> np.ndarray:
        matrix = np.asarray(rho, dtype=np.complex128)
        dimension = 2**self.n_qubits

        if matrix.shape != (dimension, dimension):
            raise ValueError(
                f"Expected a {dimension}x{dimension} density matrix for "
                f"{self.n_qubits} qubits, received shape {matrix.shape}."
            )

        if not np.allclose(matrix, matrix.conj().T, atol=1e-8):
            raise ValueError("rho must be Hermitian.")

        trace = np.trace(matrix)
        if not np.isclose(trace, 1.0, atol=1e-7):
            raise ValueError(
                f"rho must be trace-normalized; received trace={trace!r}."
            )

        return matrix

    def _validate_bases(self, bases: Sequence[str]) -> Tuple[str, ...]:
        if len(bases) != self.n_qubits:
            raise ValueError(
                f"Expected {self.n_qubits} measurement bases, received "
                f"{len(bases)}."
            )

        normalized = tuple(str(label).upper() for label in bases)
        invalid = [label for label in normalized if label not in PAULI_LABELS]
        if invalid:
            raise ValueError(
                f"Bases must use only X, Y, or Z; invalid labels: {invalid}."
            )
        return normalized

    def _validate_pauli_string(self, pauli_string: str) -> str:
        pauli = str(pauli_string).upper().replace(" ", "")
        if len(pauli) != self.n_qubits:
            raise ValueError(
                f"Expected a {self.n_qubits}-character Pauli string, "
                f"received {pauli_string!r}."
            )

        allowed = set(PAULI_LABELS) | {IDENTITY}
        invalid = [label for label in pauli if label not in allowed]
        if invalid:
            raise ValueError(
                "Pauli strings may use only I, X, Y, Z; "
                f"invalid labels: {invalid}."
            )
        return pauli

    def _rotate_density_into_measurement_frame(
        self,
        rho: np.ndarray,
        bases: Tuple[str, ...],
    ) -> np.ndarray:
        """
        Rotate rho so computational-basis measurement samples each chosen
        local Pauli eigenbasis.

        If U columns are the target basis eigenvectors, then:
            rho_measurement = U^† rho U.
        """
        unitary = self._kron_all(
            tuple(MEASUREMENT_EIGENVECTORS[label] for label in bases)
        )
        return unitary.conj().T @ rho @ unitary

    @staticmethod
    def _computational_probabilities(
        rotated_rho: np.ndarray,
    ) -> np.ndarray:
        diagonal = np.real_if_close(np.diag(rotated_rho), tol=1_000).real
        probabilities = np.clip(
            np.asarray(diagonal, dtype=float),
            0.0,
            None,
        )

        total = float(np.sum(probabilities))
        if total <= 0.0:
            raise ValueError(
                "Measurement probabilities have zero total weight. "
                "Check rho for physicality."
            )

        return probabilities / total

    @staticmethod
    def _index_to_bits(index: int, n_qubits: int) -> Tuple[int, ...]:
        return tuple(
            (int(index) >> (n_qubits - 1 - qubit)) & 1
            for qubit in range(n_qubits)
        )

    @staticmethod
    def _kron_all(matrices: Sequence[np.ndarray]) -> np.ndarray:
        output = np.array([[1.0]], dtype=np.complex128)
        for matrix in matrices:
            output = np.kron(output, matrix)
        return output

    def _pauli_operator(self, pauli_string: str) -> np.ndarray:
        return self._kron_all(
            tuple(PAULI_MATRICES[label] for label in pauli_string)
        )

    def _single_record_contribution(
        self,
        record: ShadowRecord,
        pauli_string: str,
        scale: float,
    ) -> float:
        product = 1.0
        matches = True

        for pauli, basis, outcome in zip(
            pauli_string,
            record.bases,
            record.outcomes,
        ):
            if pauli == IDENTITY:
                continue
            if pauli != basis:
                matches = False
                break

            # outcome 0 corresponds to +1, outcome 1 to -1.
            product *= 1.0 if int(outcome) == 0 else -1.0

        return scale * product if matches else 0.0


if __name__ == "__main__":
    # Small reproducible smoke test: |0000><0000|.
    sampler = ClassicalShadowSampler4Q(n_qubits=4, archive_size=512, seed=7)
    ket_zero = np.zeros(16, dtype=np.complex128)
    ket_zero[0] = 1.0
    rho_zero = np.outer(ket_zero, ket_zero.conj())

    for _ in range(512):
        sampler.sample(rho_zero)

    for observable in ("ZIII", "ZZII", "XXXX", "ZZZZ"):
        estimate = sampler.estimate_pauli(observable)
        exact = sampler.exact_pauli_expectation(rho_zero, observable)
        print(
            f"{observable}: estimate={estimate['estimate']:+.3f}, "
            f"exact={exact:+.3f}, "
            f"support={estimate['support_fraction']:.3f}"
        )

    def supported_estimate(
        self,
        pauli_string: str,
        *,
        minimum_support: float,
    ) -> Dict[str, Any]:
        """
        Return a live-safe estimate.

        The raw shadow estimate is preserved in `raw_estimate`. When archive
        support is below the requested threshold, `estimate` is set to 0.0 so
        sparse high-weight observables cannot continuously drive audio-rate or
        control-rate mappings.
        """
        result = self.estimate_pauli(
            pauli_string,
            minimum_support=minimum_support,
        )
        result["raw_estimate"] = result["estimate"]
        if not result["is_supported"]:
            result["estimate"] = 0.0
        return result