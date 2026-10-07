from dataclasses import dataclass, field, asdict


@dataclass(frozen=True)
class PortSpec:
    name: str
    quantity: str
    unit: str
    domain: str


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    label: str
    default: float
    minimum: float
    maximum: float
    unit: str
    description: str


@dataclass(frozen=True)
class ModuleSpec:
    id: str
    title: str
    equation_latex: str
    equation_text: str
    inputs: tuple[PortSpec, ...] = ()
    outputs: tuple[PortSpec, ...] = ()
    parameters: tuple[ParameterSpec, ...] = ()
    description: str = ""
    destinations: tuple[str, ...] = ()
    classification: str = "PHYSICAL"
    assumptions: tuple[str, ...] = ()

    def to_dict(self):
        return asdict(self)
