"""Continuous quantum-matrix manifolds and sampling utilities."""

from qmw.manifolds.basis_path import BasisPath, BasisPathDiagnostics
from qmw.manifolds.interpolation_types import InterpolationType, BranchConvention
from qmw.manifolds.manifold_gradient import ManifoldGradient
from qmw.manifolds.quantum_matrix_manifold import QuantumMatrixManifold

__all__ = [
    "BasisPath",
    "BasisPathDiagnostics",
    "BranchConvention",
    "InterpolationType",
    "ManifoldGradient",
    "QuantumMatrixManifold",
]

