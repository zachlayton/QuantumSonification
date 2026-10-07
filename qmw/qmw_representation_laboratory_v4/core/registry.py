"""Metadata-bearing registry for state-transform plug-ins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .state_transform import StateTransform


TransformFactory = Callable[..., StateTransform]


def _normalize(name: str) -> str:
    value = str(name).strip().lower().replace("-", "_").replace(" ", "_")
    if not value:
        raise ValueError("transform name must not be empty")
    return value


@dataclass(frozen=True)
class TransformRegistration:
    name: str
    description: str
    kind: str
    factory: TransformFactory
    aliases: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
            "aliases": list(self.aliases),
            "parameters": list(self.parameters),
        }


class TransformRegistry:
    def __init__(self) -> None:
        self._registrations: dict[str, TransformRegistration] = {}
        self._lookup: dict[str, str] = {}

    def register(
        self,
        name: str,
        factory: TransformFactory,
        *,
        description: str,
        kind: str = "basis",
        aliases: tuple[str, ...] = (),
        parameters: tuple[str, ...] = (),
    ) -> TransformRegistration:
        canonical = _normalize(name)
        normalized_aliases = tuple(_normalize(value) for value in aliases)
        keys = (canonical, *normalized_aliases)
        if len(set(keys)) != len(keys):
            raise ValueError("registration repeats its own name or alias")
        occupied = [key for key in keys if key in self._lookup]
        if occupied:
            raise ValueError(
                "transform registry name already registered: "
                + ", ".join(occupied)
            )
        registration = TransformRegistration(
            canonical,
            str(description),
            str(kind),
            factory,
            normalized_aliases,
            tuple(str(value) for value in parameters),
        )
        self._registrations[canonical] = registration
        for key in keys:
            self._lookup[key] = canonical
        return registration

    def resolve(self, name: str) -> TransformRegistration:
        canonical = self._lookup.get(_normalize(name))
        if canonical is None:
            raise KeyError(
                f"unknown transform {name!r}; choices: {', '.join(self.names())}"
            )
        return self._registrations[canonical]

    def create(self, name: str, **parameters: Any) -> StateTransform:
        transform = self.resolve(name).factory(**parameters)
        if not isinstance(transform, StateTransform):
            raise TypeError("transform factory did not return StateTransform")
        return transform

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._registrations))

    def describe(self) -> list[dict[str, Any]]:
        return [self._registrations[name].metadata() for name in self.names()]


def build_default_registry() -> TransformRegistry:
    from ..transforms import (
        EpistropheBasis,
        FloquetOperator,
        GraphLaplacianBasis,
        GroverAmplifiedBasis,
        HadamardOperator,
        HamiltonianEigenbasis,
        IdentityOperator,
        QFTOperator,
        transverse_ising_hamiltonian,
    )

    registry = TransformRegistry()
    registry.register(
        "identity",
        IdentityOperator,
        description=IdentityOperator.description,
        aliases=("computational", "none"),
    )
    registry.register(
        "hadamard",
        HadamardOperator,
        description=HadamardOperator.description,
        aliases=("h",),
    )
    registry.register("qft", QFTOperator, description=QFTOperator.description)
    registry.register(
        "inverse_qft",
        lambda: QFTOperator(inverse=True),
        description="Inverse quantum Fourier representation.",
        aliases=("iqft",),
    )
    registry.register(
        "hamiltonian",
        lambda hamiltonian=None, n_qubits=4: HamiltonianEigenbasis(
            transverse_ising_hamiltonian(n_qubits)
            if hamiltonian is None
            else hamiltonian
        ),
        description=HamiltonianEigenbasis.description,
        aliases=("energy", "hamiltonian_eigenbasis"),
        parameters=("hamiltonian", "n_qubits"),
    )
    registry.register(
        "graph_laplacian",
        GraphLaplacianBasis,
        description=GraphLaplacianBasis.description,
        aliases=("graph", "laplacian"),
        parameters=("adjacency", "normalized", "graph_name"),
    )
    registry.register(
        "floquet",
        FloquetOperator,
        description=FloquetOperator.description,
        kind="dynamics",
        parameters=("period_unitary", "steps", "period"),
    )
    registry.register(
        "grover_amplified",
        GroverAmplifiedBasis,
        description=GroverAmplifiedBasis.description,
        kind="amplification",
        aliases=("grover",),
        parameters=("marked_states", "iterations"),
    )
    registry.register(
        "epistrophe",
        EpistropheBasis,
        description=EpistropheBasis.description,
        parameters=("return_unitary", "returns", "definition"),
    )
    return registry


DEFAULT_TRANSFORMS = build_default_registry()
