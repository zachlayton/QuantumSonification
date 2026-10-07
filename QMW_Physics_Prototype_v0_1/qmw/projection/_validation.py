"""Shared shape and domain checks; projections never modify the physics state."""
import numpy as np
from qmw.core import Domain, PhysicsFrame


def require_frame_domain(frame: PhysicsFrame, domain: Domain) -> None:
    other = frame.domain
    if (other.kind != domain.kind or other.shape != domain.shape or
            other.spacing != domain.spacing or other.boundary != domain.boundary or
            other.coordinate_unit != domain.coordinate_unit or
            not np.array_equal(other.coordinates, domain.coordinates)):
        raise ValueError("Frame domain differs from the projector domain")
    frame.validate()


def require_count(count: int, size: int) -> None:
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= size:
        raise ValueError("Projection count must be an integer between 1 and domain size")


def real_values(values, shape: tuple[int, ...], quantity: str) -> np.ndarray:
    a = np.asarray(values)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError(f"Invalid {quantity} shape or values")
    if np.iscomplexobj(a) and not np.allclose(a.imag, 0.0, atol=1e-12, rtol=0.0):
        raise ValueError(f"{quantity} must be real")
    return a.real


def require_density_matrix(rho, size: int) -> np.ndarray:
    a = np.asarray(rho)
    if a.shape != (size, size) or not np.isfinite(a).all():
        raise ValueError("Invalid density matrix shape or values")
    if not np.allclose(a, a.conj().T, atol=1e-12, rtol=1e-10):
        raise ValueError("Density-matrix projection requires a Hermitian matrix")
    return a
