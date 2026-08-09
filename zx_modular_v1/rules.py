"""Typed catalog for the ZX and ZXH rules exposed by the visual instrument."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


RuleCalculus = Literal["ZX", "ZXH"]
RuleKind = Literal["rewrite", "macro", "generator"]
RuleStatus = Literal[
    "live_verified",
    "core_verified",
    "pyzx_ready",
    "planned",
]


@dataclass(frozen=True)
class ZXRuleSpec:
    rule_id: str
    label: str
    calculus: RuleCalculus
    kind: RuleKind
    status: RuleStatus
    selection: str
    condition: str
    backend: str
    gesture: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


ZX_RULE_CATALOG: tuple[ZXRuleSpec, ...] = (
    ZXRuleSpec(
        "spider_fusion",
        "Spider fusion",
        "ZX",
        "rewrite",
        "live_verified",
        "two connected spiders",
        "same color; one plain connecting wire",
        "zx_modular_v1.fuse_spiders",
        "F",
        "Phases add modulo 2π; Processing receives an exact error report.",
    ),
    ZXRuleSpec(
        "identity_removal",
        "Identity removal",
        "ZX",
        "rewrite",
        "live_verified",
        "one spider",
        "zero phase; degree two; both wires plain",
        "zx_modular_v1.remove_identity_spider / pyzx.id_simp",
        "I",
    ),
    ZXRuleSpec(
        "pi_copy",
        "π-copy / Pauli push",
        "ZX",
        "rewrite",
        "live_verified",
        "a π spider and an opposite-color neighbor",
        "phase is π modulo 2π",
        "pyzx.push_pauli_rewrite / pyzx.pi_commute_rewrite",
        "P",
        "Pulling through negates the opposite-color phase.",
    ),
    ZXRuleSpec(
        "state_copy",
        "State copy",
        "ZX",
        "rewrite",
        "live_verified",
        "a basis-state spider and an opposite-color spider",
        "state phase is an integer multiple of π",
        "pyzx.copy_simp",
        "K",
    ),
    ZXRuleSpec(
        "bialgebra",
        "Bialgebra",
        "ZX",
        "rewrite",
        "live_verified",
        "a compatible opposite-color spider pattern",
        "phaseless product/coproduct pattern",
        "pyzx.bialg_simp",
        "A",
    ),
    ZXRuleSpec(
        "hopf",
        "Hopf",
        "ZX",
        "rewrite",
        "live_verified",
        "two opposite-color spiders with parallel interaction",
        "Hopf pattern matcher succeeds",
        "pyzx.hopf_simp",
        "O",
    ),
    ZXRuleSpec(
        "color_change",
        "Color change / Fourier",
        "ZX",
        "rewrite",
        "live_verified",
        "one spider",
        "insert/remove Hadamards on every incident leg",
        "pyzx.color_change_rewrite",
        "G",
    ),
    ZXRuleSpec(
        "local_complementation",
        "Local complementation",
        "ZX",
        "rewrite",
        "live_verified",
        "one interior Z spider",
        "phase ±π/2; all incident wires Hadamard; Z neighbors",
        "pyzx.lcomp with scalar-aware whole-tensor verification",
        "w",
        "Deletes the selected Clifford spider and complements its neighborhood.",
    ),
    ZXRuleSpec(
        "pivot",
        "Pivot",
        "ZX",
        "rewrite",
        "live_verified",
        "two connected interior Z spiders",
        "Pauli phases; selected connection and internal legs Hadamard",
        "pyzx.pivot with scalar-aware whole-tensor verification",
        "Shift-W",
        "Deletes the selected pair and toggles connectivity across neighbor sets.",
    ),
    ZXRuleSpec(
        "cnot",
        "CNOT",
        "ZX",
        "macro",
        "live_verified",
        "canvas insertion point",
        "Z spider on control; X spider on target",
        "Processing macro / PennyLane-PyZX import",
        "N",
        "CNOT is not a new generator; the UI expands it to its ZX form.",
    ),
    ZXRuleSpec(
        "hadamard",
        "Hadamard",
        "ZX",
        "generator",
        "live_verified",
        "canvas insertion point",
        "degree-two yellow box or Hadamard edge",
        "Processing H node / zx_modular_v1 hadamard edge",
        "H",
    ),
    ZXRuleSpec(
        "h_box",
        "H-box",
        "ZXH",
        "generator",
        "live_verified",
        "canvas insertion point",
        "arbitrary arity with complex label a",
        "PyZX H_BOX plus scalar-aware tensor verification",
        "Y",
    ),
    ZXRuleSpec(
        "absorb",
        "Absorb",
        "ZXH",
        "rewrite",
        "live_verified",
        "an H-box and matching spider/state pattern",
        "ZXH absorb matcher succeeds",
        "scalar-aware PyZX tensor verifier",
        "U",
        "This is intentionally not treated as a plain ZX rule.",
    ),
    ZXRuleSpec(
        "toffoli",
        "Toffoli",
        "ZXH",
        "macro",
        "live_verified",
        "canvas insertion point",
        "three Z spiders and three H-boxes",
        "PyZX/PennyLane macro plus ZXH tensor verifier",
        "T",
    ),
)


def rule_catalog() -> list[dict[str, str | None]]:
    return [rule.to_dict() for rule in ZX_RULE_CATALOG]


def get_rule(rule_id: str) -> ZXRuleSpec:
    for rule in ZX_RULE_CATALOG:
        if rule.rule_id == rule_id:
            return rule
    raise KeyError(f"unknown ZX rule: {rule_id}")
