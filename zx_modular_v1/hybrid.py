"""Paired Max/VCV host profiles for one semantics-authoritative ZX graph."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .compiler import ModularPatchPlan, compile_modular_plan
from .model import ZXDiagram


@dataclass(frozen=True)
class HostModuleBinding:
    semantic_module_id: str
    host_object: str
    implementation_status: str
    signal_format: str
    parameter_routes: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_module_id": self.semantic_module_id,
            "host_object": self.host_object,
            "implementation_status": self.implementation_status,
            "signal_format": self.signal_format,
            "parameter_routes": self.parameter_routes,
        }


@dataclass(frozen=True)
class HostCableBinding:
    semantic_cable_id: str
    endpoint_a: str
    endpoint_b: str
    host_cable_type: str
    channels: int
    transform: str
    required_adapter: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_cable_id": self.semantic_cable_id,
            "endpoint_a": self.endpoint_a,
            "endpoint_b": self.endpoint_b,
            "host_cable_type": self.host_cable_type,
            "channels": self.channels,
            "transform": self.transform,
            "required_adapter": self.required_adapter,
        }


@dataclass(frozen=True)
class HostRealizationPlan:
    host: str
    target_version: str
    role: str
    modules: tuple[HostModuleBinding, ...]
    cables: tuple[HostCableBinding, ...]
    capabilities: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "target_version": self.target_version,
            "role": self.role,
            "capabilities": self.capabilities,
            "modules": [module.to_dict() for module in self.modules],
            "cables": [cable.to_dict() for cable in self.cables],
        }


@dataclass(frozen=True)
class HybridMaxVCVPlan:
    revision: str
    semantic_plan: ModularPatchPlan
    max_plan: HostRealizationPlan
    vcv_plan: HostRealizationPlan
    synchronization: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "qmw.zx-hybrid-max-vcv.v1",
            "revision": self.revision,
            "semantic_plan": self.semantic_plan.to_dict(),
            "realizations": {
                "max": self.max_plan.to_dict(),
                "vcv_rack": self.vcv_plan.to_dict(),
            },
            "synchronization": self.synchronization,
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


MAX_OBJECTS = {
    "boundary_input": "qmw.zx.boundary.in.mc~",
    "boundary_output": "qmw.zx.boundary.out.mc~",
    "phase_coherent_spider": "qmw.zx.zspider.mc~",
    "basis_mixing_spider": "qmw.zx.xspider.mc~",
}

VCV_OBJECTS = {
    "boundary_input": "QMW-ZX:BoundaryInput",
    "boundary_output": "QMW-ZX:BoundaryOutput",
    "phase_coherent_spider": "QMW-ZX:ZSpider",
    "basis_mixing_spider": "QMW-ZX:XSpider",
}


def _module_bindings(
    plan: ModularPatchPlan,
    host_objects: dict[str, str],
    signal_format: str,
) -> tuple[HostModuleBinding, ...]:
    return tuple(
        HostModuleBinding(
            semantic_module_id=module.module_id,
            host_object=host_objects[module.module_type],
            implementation_status="planned",
            signal_format=signal_format,
            parameter_routes=(
                {
                    "phase_radians": (
                        f"/qmw/zx/module/{module.module_id}/phase"
                    )
                }
                if module.module_type
                in {"phase_coherent_spider", "basis_mixing_spider"}
                else {}
            ),
        )
        for module in plan.modules
    )


def _cable_bindings(
    plan: ModularPatchPlan,
    *,
    cable_type: str,
    hadamard_adapter: str,
) -> tuple[HostCableBinding, ...]:
    return tuple(
        HostCableBinding(
            semantic_cable_id=cable.cable_id,
            endpoint_a=cable.endpoint_a,
            endpoint_b=cable.endpoint_b,
            host_cable_type=cable_type,
            channels=4,
            transform=cable.transform,
            required_adapter=(
                hadamard_adapter if cable.transform == "hadamard" else None
            ),
        )
        for cable in plan.cables
    )


def compile_hybrid_max_vcv_plan(diagram: ZXDiagram) -> HybridMaxVCVPlan:
    """Create synchronized Max and VCV realization profiles for one diagram."""
    semantic_plan = compile_modular_plan(diagram)
    canonical = semantic_plan.to_json(indent=0).encode("utf-8")
    revision = hashlib.sha256(canonical).hexdigest()[:16]

    max_plan = HostRealizationPlan(
        host="Max",
        target_version="9.0.5",
        role=(
            "semantic laboratory: editing, animated rewrites, MC tensor DSP, "
            "analysis, visualization, and QMW orchestration"
        ),
        modules=_module_bindings(
            semantic_plan,
            MAX_OBJECTS,
            "4-channel MC: Re(0), Im(0), Re(1), Im(1)",
        ),
        cables=_cable_bindings(
            semantic_plan,
            cable_type="MC signal patch cord",
            hadamard_adapter="qmw.zx.hadamard.mc~",
        ),
        capabilities={
            "dynamic_patching": "v8/thispatcher create-delete-connect",
            "high_dimensional_media": ["MC", "Jitter", "GL", "dictionary"],
            "topology_port": 7480,
            "control_port": 7481,
        },
    )
    vcv_plan = HostRealizationPlan(
        host="VCV Rack",
        target_version="2.4.1 Free",
        role=(
            "performance surface: tactile modules, polyphonic CV, clocks, "
            "sequencing, modulation, and Eurorack-style exploration"
        ),
        modules=_module_bindings(
            semantic_plan,
            VCV_OBJECTS,
            "4-channel poly CV: Re(0), Im(0), Re(1), Im(1)",
        ),
        cables=_cable_bindings(
            semantic_plan,
            cable_type="4-channel polyphonic cable",
            hadamard_adapter="QMW-ZX:HTransform",
        ),
        capabilities={
            "control_bridge_now": "OSCelot 2.0.0 fader/button mapping",
            "native_modules": "requires Rack SDK and QMW-ZX plugin",
            "topology_port": 7000,
            "feedback_port": 7001,
        },
    )
    return HybridMaxVCVPlan(
        revision=revision,
        semantic_plan=semantic_plan,
        max_plan=max_plan,
        vcv_plan=vcv_plan,
        synchronization={
            "semantic_authority": "Python / PennyLane / PyZX",
            "transaction": [
                "begin revision expected_parent",
                "publish complete topology and bound parameters",
                "validate host realization",
                "commit atomically between audio blocks",
                "acknowledge active revision",
            ],
            "edit_policy": (
                "Max and VCV submit edit proposals; the conductor validates "
                "and republishes one canonical revision to both hosts"
            ),
            "control_transport": "OSC over localhost UDP",
            "audio_transport": (
                "host-local by default; optional virtual-audio loopback. "
                "Semantic synchronization does not require cross-host audio."
            ),
            "clock_policy": (
                "one elected performance clock; the other host follows epoch, "
                "tempo, beat, and revision messages"
            ),
        },
    )
