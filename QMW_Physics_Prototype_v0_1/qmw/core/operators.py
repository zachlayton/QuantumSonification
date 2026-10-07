"""Uniform periodic Fourier derivatives; never applied to time/basis arrays."""
import numpy as np
from .domain import Domain


def wavenumbers(domain: Domain) -> np.ndarray:
    domain.require_periodic_space()
    return 2*np.pi*np.fft.fftfreq(domain.size, d=domain.spacing[0])


def derivative(values: np.ndarray, domain: Domain, order: int = 1) -> np.ndarray:
    domain.require_periodic_space()
    a = np.asarray(values)
    if a.shape != domain.shape or order not in (1, 2):
        raise ValueError("Invalid derivative shape or order")
    result = np.fft.ifft((1j*wavenumbers(domain))**order*np.fft.fft(a))
    return result.real if np.isrealobj(a) else result


def laplacian(values: np.ndarray, domain: Domain) -> np.ndarray:
    return derivative(values, domain, order=2)


def spectral_tail_fraction(values: np.ndarray, domain: Domain) -> float:
    domain.require_periodic_space()
    spectrum = np.abs(np.fft.fft(values))**2
    k = np.abs(wavenumbers(domain))
    return float(spectrum[k > (2/3)*k.max()].sum()/max(spectrum.sum(), 1e-30))
