"""Geometry-aware constrained quantum optimization on the Wilson Hexany."""

from .experiment import ExperimentResult, run_comparison
from .feedback import AcousticFeedbackFrame, FeedbackControls
from .model import HexanyOptimizationModel, HexanyProblem, build_hexany_problem
from .optimizers import OptimizationStep, OptimizationTrace, ProbeRecord

__all__ = [
    "AcousticFeedbackFrame",
    "ExperimentResult",
    "FeedbackControls",
    "HexanyOptimizationModel",
    "HexanyProblem",
    "OptimizationStep",
    "OptimizationTrace",
    "ProbeRecord",
    "build_hexany_problem",
    "run_comparison",
]
