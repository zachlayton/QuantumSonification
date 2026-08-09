"""Semantics-first bridge between ZX diagrams and modular synthesis graphs."""

from .compiler import ModularPatchPlan, compile_modular_plan
from .density_bridge import ZXDensityFrame, density_frame_from_visual_graph
from .hybrid import HybridMaxVCVPlan, compile_hybrid_max_vcv_plan
from .model import Edge, Node, ZXDiagram
from .pauli_gadget import (
    PauliGadgetSpec,
    PauliGadgetVerification,
    PauliScoreVerification,
    can_fuse_score_gadgets,
    fuse_score_gadgets,
    normalize_pauli_label,
    pauli_expectation,
    pauli_operator,
    pauli_rotation_matrix,
    pauli_score_matrix,
    pauli_strings_commute,
    pauli_weight,
    verify_visual_pauli_gadget,
    verify_visual_pauli_score,
)
from .pennylane_bridge import (
    PennyLaneModularResult,
    PyZXImportReport,
    import_pyzx_graph,
    pennylane_to_modular,
)
from .rewrite import (
    RewriteReport,
    SemanticMismatchError,
    fuse_spiders,
    remove_identity_spider,
)
from .rack_osc import (
    OSCelotControl,
    OSCelotPublisher,
    PennyLaneRackFrame,
    rack_frame_from_state,
)
from .rewrite_osc import (
    FusionVerification,
    RewriteOSCVerifier,
    VisualGraphMirror,
    VisualRewriteVerification,
)
from .rules import ZXRuleSpec, get_rule, rule_catalog
from .semantics import linear_map, normalized_state

__all__ = [
    "Edge",
    "HybridMaxVCVPlan",
    "ModularPatchPlan",
    "Node",
    "OSCelotControl",
    "OSCelotPublisher",
    "PennyLaneModularResult",
    "PennyLaneRackFrame",
    "PauliGadgetVerification",
    "PauliGadgetSpec",
    "PauliScoreVerification",
    "PyZXImportReport",
    "RewriteReport",
    "RewriteOSCVerifier",
    "SemanticMismatchError",
    "ZXDiagram",
    "ZXDensityFrame",
    "ZXRuleSpec",
    "FusionVerification",
    "VisualGraphMirror",
    "VisualRewriteVerification",
    "compile_modular_plan",
    "density_frame_from_visual_graph",
    "compile_hybrid_max_vcv_plan",
    "can_fuse_score_gadgets",
    "fuse_spiders",
    "fuse_score_gadgets",
    "get_rule",
    "import_pyzx_graph",
    "linear_map",
    "normalized_state",
    "normalize_pauli_label",
    "pauli_expectation",
    "pauli_operator",
    "pauli_rotation_matrix",
    "pauli_score_matrix",
    "pauli_strings_commute",
    "pauli_weight",
    "pennylane_to_modular",
    "rack_frame_from_state",
    "remove_identity_spider",
    "rule_catalog",
    "verify_visual_pauli_gadget",
    "verify_visual_pauli_score",
]
