"""Explicit interpolation semantics for quantum matrix manifolds."""

from __future__ import annotations

from enum import Enum


class InterpolationType(str, Enum):
    """Operations that must remain mathematically distinct.

    BASIS
        A fixed operator is represented in a moving orthonormal basis:
        ``U(eta)^dagger M U(eta)``. Spectrum and trace are invariant.
    STATE
        Two matrix states are mixed affinely. Spectra generally change.
    EIGENVALUES
        Ordered eigenvalues vary in one fixed eigenbasis.
    EIGENVECTORS
        A fixed spectrum is reconstructed in a moving eigenframe.
    """

    BASIS = "basis"
    STATE = "state"
    EIGENVALUES = "eigenvalues"
    EIGENVECTORS = "eigenvectors"


class BranchConvention(str, Enum):
    """Eigenphase convention used for a unitary logarithm."""

    PRINCIPAL = "principal_-pi_pi"
    EXPLICIT_SHIFTS = "principal_plus_2pi_integer_shifts"

