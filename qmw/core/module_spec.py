"""Self-describing module metadata, so a GUI can show the equation behind each node."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PortSpec:
    name: str
    description: str


@dataclass(frozen=True)
class ModuleSpec:
    id: str
    title: str
    equation_latex: str
    inputs: tuple[PortSpec, ...] = ()
    outputs: tuple[PortSpec, ...] = ()
    description: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)
