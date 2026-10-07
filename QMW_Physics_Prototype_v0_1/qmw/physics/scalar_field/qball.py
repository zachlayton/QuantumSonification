"""A checked one-dimensional stationary sextic profile, not a 3-D Q-ball claim."""
from __future__ import annotations
import numpy as np
from ...core.domain import Domain
from ...core.operators import laplacian
from .potentials import PolynomialPotential


def checked_qball_profile(domain: Domain, potential: PolynomialPotential,
                         omega: float = .95, tolerance: float = 1e-5) -> tuple[np.ndarray, dict]:
    """Periodize the analytic line profile and check its spatial equation numerically.

    For phi=f(x) exp(i omega t), f''=(m²-omega²)f-a f³+b f⁵.
    With mu=m²-omega², f²=4mu/[a+sqrt(a²-16b*mu/3) cosh(2sqrt(mu)x)].
    The infinite-line solution is summed over periodic images; nonlinear image
    overlap introduces an error and therefore acceptance requires an actual
    Fourier-grid residual check. Too-short/coarse domains are rejected.
    """
    domain.require_periodic_space()
    if not np.isfinite([omega, tolerance]).all() or omega <= 0 or tolerance <= 0:
        raise ValueError("Q-ball frequency and tolerance must be finite and positive")
    m2, a, b = potential.mass_squared, potential.attraction, potential.repulsion
    if min(m2, a, b) <= 0:
        raise ValueError("Checked sextic profile requires positive m², attraction and repulsion")
    lower = m2 - 3*a*a/(16*b)
    if lower <= 0 or not lower < omega*omega < m2:
        raise ValueError(f"Q-ball requires {max(0.0, lower):.6g} < omega² < {m2:.6g} and positive U(s)")
    mu = m2 - omega*omega
    discriminant = np.sqrt(a*a - 16*b*mu/3)
    alpha = 2*np.sqrt(mu)
    field = np.zeros(domain.shape, dtype=float)
    # Finite sum determined by the exponential tail, avoiding a fixed image count.
    count = max(2, int(np.ceil(32/(np.sqrt(mu)*domain.length))))
    for image in range(-count, count+1):
        argument = alpha*np.abs(domain.coordinates + image*domain.length)
        # logaddexp keeps the analytic expression finite for distant images.
        log_cosh = np.logaddexp(argument, -argument) - np.log(2)
        log_denominator = np.logaddexp(np.log(a), np.log(discriminant)+log_cosh)
        field += np.exp(.5*(np.log(4*mu)-log_denominator))
    residual = laplacian(field, domain) - 2*potential.derivative_s(field**2)*field + omega*omega*field
    scale = max(float(np.max((m2+omega*omega)*field)), 1e-15)
    relative_residual = float(np.max(np.abs(residual))/scale)
    if not np.isfinite(relative_residual) or relative_residual > tolerance:
        raise ValueError(
            f"1-D Q-ball profile residual {relative_residual:.3g} exceeds {tolerance:.3g}; "
            "increase spatial length/resolution or choose a better-resolved frequency"
        )
    return field.astype(complex), {
        "dimension": 1, "initializer": "checked-periodized-1d-qball",
        "stationary_relative_residual": relative_residual,
        "profile_equation": "f'' = (m²-omega²) f - a f³ + b f⁵",
        "omega": float(omega), "periodic_images_each_side": count,
    }
