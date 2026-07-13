"""
shadow_mutator.py

Non-invasive shadow-aware wrapper for the QuantumSonification Hamiltonian mutator.

Design constraints
------------------
- Does NOT edit, duplicate, or replace `mutator.py`.
- Delegates every existing mutation operation to the preferred source mutator:
  `mutator_quantum_sources_v1.py`.
- Falls back to `mutator.py` only if the newer source module is unavailable.
- Emits compact, reproducible metadata describing the mutation and a proposed
  randomized local-Pauli measurement basis for a downstream shadow sampler.
- Does NOT perform measurement, collapse, density-matrix evolution, OSC, or
  Pauli-string estimation. Those belong in the density engine / shadow sampler.

Typical use
-----------
    from hamiltonian.shadow_mutator import ShadowMutator

    self.mutator = ShadowMutator(
        excitation_kind="audio",
        shadow_seed=1234,
    )

    self.hamiltonian = self.mutator.mutate_from_audio(
        self.hamiltonian,
        audio_features,
    )

    shadow_context = self.mutator.latest_shadow_context
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib
import time
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np


PAULI_BASES: Tuple[str, str, str] = ("X", "Y", "Z")


@dataclass(frozen=True)
class ShadowMutationContext:
    """One non-destructive record of a Hamiltonian mutation event."""

    timestamp: float
    source_method: str
    excitation_kind: str
    dt: Optional[float]
    n_qubits: Optional[int]
    local_bases: Tuple[str, ...]
    mutation_norm_before: Optional[float]
    mutation_norm_after: Optional[float]
    mutation_delta_norm: Optional[float]
    extra: Dict[str, Any]


class ShadowMutator:
    """
    Shadow-aware adapter around the existing Hamiltonian mutator.

    The wrapped mutator remains the single source of truth for Hamiltonian
    mutation. This class only observes call context and proposes a randomized
    local-Pauli basis for the later shadow-acquisition layer.
    """

    def __init__(
        self,
        *args: Any,
        n_qubits: Optional[int] = None,
        shadow_seed: Optional[int] = None,
        shadow_enabled: bool = True,
        shadow_history_size: int = 256,
        source_module: str = "hamiltonian.mutator_quantum_sources_v1",
        source_class: str = "HamiltonianMutator",
        **kwargs: Any,
    ) -> None:
        self.n_qubits = int(n_qubits) if n_qubits is not None else None
        self.shadow_enabled = bool(shadow_enabled)
        self.shadow_history_size = max(1, int(shadow_history_size))
        self._rng = np.random.default_rng(shadow_seed)
        self._history: list[ShadowMutationContext] = []
        self._latest_shadow_context: Optional[ShadowMutationContext] = None

        mutator_type = self._load_mutator_type(
            preferred_module=source_module,
            class_name=source_class,
        )
        self._delegate = mutator_type(*args, **kwargs)

    @staticmethod
    def _load_mutator_type(preferred_module: str, class_name: str) -> type:
        """
        Prefer mutator_quantum_sources_v1, with the legacy mutator as fallback.

        No import from this module's own name is attempted, avoiding circular
        self-imports.
        """
        candidates = (
            preferred_module,
            "hamiltonian.mutator",
            "mutator_quantum_sources_v1",
            "mutator",
        )
        failures: list[str] = []

        for module_name in candidates:
            try:
                module = importlib.import_module(module_name)
                mutator_type = getattr(module, class_name)
                return mutator_type
            except (ImportError, AttributeError) as exc:
                failures.append(f"{module_name}: {exc}")

        details = "\n  ".join(failures)
        raise ImportError(
            f"Could not load {class_name}. Tried:\n  {details}"
        )

    @property
    def delegate(self) -> Any:
        """The untouched existing mutator instance."""
        return self._delegate

    @property
    def latest_shadow_context(self) -> Optional[Dict[str, Any]]:
        """Most recent metadata record, serialized for engine / OSC use."""
        if self._latest_shadow_context is None:
            return None
        return asdict(self._latest_shadow_context)

    @property
    def shadow_history(self) -> Tuple[Dict[str, Any], ...]:
        """Immutable snapshot of recent mutation metadata."""
        return tuple(asdict(record) for record in self._history)

    def clear_shadow_history(self) -> None:
        self._history.clear()
        self._latest_shadow_context = None

    def set_shadow_enabled(self, enabled: bool) -> None:
        self.shadow_enabled = bool(enabled)

    def set_shadow_seed(self, seed: Optional[int]) -> None:
        """Reset randomized-basis generation reproducibly."""
        self._rng = np.random.default_rng(seed)

    def set_n_qubits(self, n_qubits: int) -> None:
        n_qubits = int(n_qubits)
        if n_qubits < 1:
            raise ValueError("n_qubits must be at least 1.")
        self.n_qubits = n_qubits

    def set_excitation_kind(self, excitation_kind: str) -> None:
        """Delegate source selection without redefining source semantics."""
        setter = getattr(self._delegate, "set_excitation_kind", None)
        if setter is None:
            raise AttributeError(
                "The wrapped mutator has no set_excitation_kind method."
            )
        setter(excitation_kind)

    def mutate_from_audio(
        self,
        hamiltonian: np.ndarray,
        audio: Any,
        *,
        dt: Optional[float] = None,
        n_qubits: Optional[int] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """Delegate audio mutation and publish shadow-ready context."""
        return self._mutate(
            method_name="mutate_from_audio",
            hamiltonian=hamiltonian,
            args=(audio,),
            dt=dt,
            n_qubits=n_qubits,
            extra={"source": "audio"},
            kwargs=kwargs,
        )

    def mutate_from_physics_source(
        self,
        hamiltonian: np.ndarray,
        dt: float,
        *,
        n_qubits: Optional[int] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """Delegate quantum/physics-source mutation and publish context."""
        return self._mutate(
            method_name="mutate_from_physics_source",
            hamiltonian=hamiltonian,
            args=(dt,),
            dt=dt,
            n_qubits=n_qubits,
            extra={"source": "physics"},
            kwargs=kwargs,
        )

    def mutate(
        self,
        hamiltonian: np.ndarray,
        *args: Any,
        method_name: str = "mutate",
        dt: Optional[float] = None,
        n_qubits: Optional[int] = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """
        Generic escape hatch for any existing mutation method.

        Example:
            H = shadow_mutator.mutate(
                H, field, method_name="mutate_from_custom_field", dt=dt
            )
        """
        return self._mutate(
            method_name=method_name,
            hamiltonian=hamiltonian,
            args=args,
            dt=dt,
            n_qubits=n_qubits,
            extra={"source": "generic"},
            kwargs=kwargs,
        )

    def _mutate(
        self,
        *,
        method_name: str,
        hamiltonian: np.ndarray,
        args: Sequence[Any],
        dt: Optional[float],
        n_qubits: Optional[int],
        extra: Dict[str, Any],
        kwargs: Dict[str, Any],
    ) -> np.ndarray:
        before = np.asarray(hamiltonian, dtype=np.complex128)
        before_norm = float(np.linalg.norm(before))

        method = getattr(self._delegate, method_name, None)
        if method is None:
            raise AttributeError(
                f"Wrapped mutator has no '{method_name}' method. "
                "Use a method name that exists in mutator_quantum_sources_v1."
            )

        mutated = method(hamiltonian, *args, **kwargs)
        after = np.asarray(mutated, dtype=np.complex128)
        after_norm = float(np.linalg.norm(after))
        delta_norm = float(np.linalg.norm(after - before))

        if self.shadow_enabled:
            resolved_qubits = self._resolve_n_qubits(
                matrix_dimension=after.shape[0],
                explicit_n_qubits=n_qubits,
            )
            context = ShadowMutationContext(
                timestamp=time.monotonic(),
                source_method=method_name,
                excitation_kind=str(
                    getattr(self._delegate, "excitation_kind", "unknown")
                ),
                dt=None if dt is None else float(dt),
                n_qubits=resolved_qubits,
                local_bases=self._draw_local_pauli_bases(resolved_qubits),
                mutation_norm_before=before_norm,
                mutation_norm_after=after_norm,
                mutation_delta_norm=delta_norm,
                extra=extra,
            )
            self._append_context(context)

        return mutated

    def _resolve_n_qubits(
        self,
        *,
        matrix_dimension: int,
        explicit_n_qubits: Optional[int],
    ) -> Optional[int]:
        if explicit_n_qubits is not None:
            return int(explicit_n_qubits)
        if self.n_qubits is not None:
            return self.n_qubits

        if matrix_dimension > 0:
            candidate = int(round(np.log2(matrix_dimension)))
            if 2**candidate == matrix_dimension:
                return candidate
        return None

    def _draw_local_pauli_bases(
        self, n_qubits: Optional[int]
    ) -> Tuple[str, ...]:
        if n_qubits is None or n_qubits < 1:
            return ()
        indices = self._rng.integers(0, len(PAULI_BASES), size=n_qubits)
        return tuple(PAULI_BASES[int(index)] for index in indices)

    def _append_context(self, context: ShadowMutationContext) -> None:
        self._latest_shadow_context = context
        self._history.append(context)
        overflow = len(self._history) - self.shadow_history_size
        if overflow > 0:
            del self._history[:overflow]

    def __getattr__(self, name: str) -> Any:
        """
        Transparently expose legacy mutator fields and methods.

        This preserves existing code such as `self.mutator.amount = ...` and
        access to specialized mutation methods not yet explicitly wrapped.
        """
        return getattr(self._delegate, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Keep adapter settings local; forward unknown writable attributes to the
        original mutator when it already owns them.
        """
        local_names = {
            "n_qubits",
            "shadow_enabled",
            "shadow_history_size",
            "_rng",
            "_history",
            "_latest_shadow_context",
            "_delegate",
        }
        if name in local_names or "_delegate" not in self.__dict__:
            object.__setattr__(self, name, value)
        elif hasattr(self._delegate, name):
            setattr(self._delegate, name, value)
        else:
            object.__setattr__(self, name, value)
