"""Compile a ZX diagram into a modular, Max-friendly tensor patch plan."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Any

import numpy as np

from .model import ZXDiagram
from .semantics import IDENTITY, HADAMARD, spider_tensor


@dataclass(frozen=True)
class ModularModule:
    module_id: str
    module_type: str
    label: str
    ports: tuple[str, ...]
    parameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.module_id,
            "type": self.module_type,
            "label": self.label,
            "ports": list(self.ports),
            "parameters": self.parameters,
        }


@dataclass(frozen=True)
class PatchCable:
    cable_id: str
    endpoint_a: str
    endpoint_b: str
    transform: str
    rail_count: int = 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.cable_id,
            "endpoint_a": self.endpoint_a,
            "endpoint_b": self.endpoint_b,
            "transform": self.transform,
            "rail_count": self.rail_count,
        }


@dataclass(frozen=True)
class ModularPatchPlan:
    name: str
    modules: tuple[ModularModule, ...]
    cables: tuple[PatchCable, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "qmw.zx-modular-plan.v1",
            "name": self.name,
            "metadata": self.metadata,
            "modules": [module.to_dict() for module in self.modules],
            "cables": [cable.to_dict() for cable in self.cables],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _complex_tensor_payload(tensor: np.ndarray) -> dict[str, Any]:
    values = np.asarray(tensor, dtype=np.complex128)
    return {
        "shape": list(values.shape),
        "real": [float(value) for value in values.real.reshape(-1)],
        "imag": [float(value) for value in values.imag.reshape(-1)],
    }


def compile_modular_plan(diagram: ZXDiagram) -> ModularPatchPlan:
    """Compile exact ZX tensors and two-rail wires into a neutral patch plan.

    Each wire has two complex rails, one for each computational-basis value.
    This is a faithful control/tensor representation, not yet an assertion that
    ordinary audio fan-out physically implements quantum cloning.
    """
    diagram.validate()
    modules: list[ModularModule] = []

    for node in sorted(diagram.nodes.values(), key=lambda item: item.node_id):
        incident = diagram.incident_edges(node.node_id)
        ports = tuple(f"edge:{edge.edge_id}" for edge in incident)
        if node.kind == "boundary":
            module_type = f"boundary_{node.boundary_role}"
            parameters: dict[str, Any] = {
                "index": int(node.boundary_index or 0),
                "representation": "complex_dual_rail",
            }
            label = node.label or f"{node.boundary_role} {node.boundary_index}"
        else:
            module_type = (
                "phase_coherent_spider"
                if node.kind == "z"
                else "basis_mixing_spider"
            )
            tensor = spider_tensor(node, len(incident))
            parameters = {
                "color": node.kind,
                "phase_radians": float(node.phase),
                "phase_turns": float(node.phase) / (2.0 * math.pi),
                "arity": len(incident),
                "representation": "complex_dual_rail_tensor",
                "tensor": _complex_tensor_payload(tensor),
            }
            label = node.label or f"{node.kind.upper()}({node.phase:.4g})"
        modules.append(
            ModularModule(
                module_id=node.node_id,
                module_type=module_type,
                label=label,
                ports=ports,
                parameters=parameters,
            )
        )

    cables = tuple(
        PatchCable(
            cable_id=edge.edge_id,
            endpoint_a=f"{edge.source}.edge:{edge.edge_id}",
            endpoint_b=f"{edge.target}.edge:{edge.edge_id}",
            transform=edge.kind,
        )
        for edge in sorted(diagram.edges.values(), key=lambda item: item.edge_id)
    )
    return ModularPatchPlan(
        name=f"{diagram.name}__modular",
        modules=tuple(modules),
        cables=cables,
        metadata={
            "wire_representation": "two complex rails per ZX wire",
            "vcv_polyphony": {
                "channels_per_wire": 4,
                "channel_order": ["Re(0)", "Im(0)", "Re(1)", "Im(1)"],
                "nominal_voltage_range": "-5V..+5V",
            },
            "basis_ordering": "|q[n-1] ... q1 q0>; boundary 0 is LSB",
            "global_scalar": {
                "real": float(diagram.scalar.real),
                "imag": float(diagram.scalar.imag),
                "rack_policy": "preserve, ignore, or sonify against a reference",
            },
            "plain_wire_tensor": _complex_tensor_payload(IDENTITY),
            "hadamard_wire_tensor": _complex_tensor_payload(HADAMARD),
            "evaluation": "undirected tensor network",
            "realtime_policy": (
                "choose a contraction schedule or input/output orientation "
                "in the host; audio feedback remains a separate sonic relation"
            ),
        },
    )
