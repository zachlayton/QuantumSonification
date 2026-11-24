"""1-D Schrödinger field on a 2048-point grid.

    i hbar dpsi/dt = [ -hbar^2/(2m) d^2/dx^2 + V(x) - i W(x) ] psi

Integrator: Crank–Nicolson (Cayley form), which is exactly unitary for Hermitian H,
conserves <H> for static V, and works for both Dirichlet (fixed ends, like a string)
and periodic boundaries. Split-step Fourier was not used because it forces periodic
boundaries. W(x) >= 0 is an optional complex absorbing potential.

Discretisation is chosen so the observables obey exact discrete conservation laws:

    probability current on links   j_{n+1/2} = (hbar/m) Im( psi_n^* (psi_{n+1} - psi_n)/dx )
    continuity                     d rho_n/dt = -(j_{n+1/2} - j_{n-1/2})/dx - (2/hbar) W_n rho_n

and Crank–Nicolson satisfies the continuity equation to round-off when the current is
evaluated at the midpoint state (psi^t + psi^{t+dt})/2. Kinetic energy density uses the
|grad psi|^2 convention, ((hbar^2/2m)|grad psi|^2 + V|psi|^2); it integrates exactly to
<H>, and differs from the -Re(psi^* Laplacian psi) convention only by a divergence.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.sparse import diags, identity
from scipy.sparse.linalg import splu

from qmw.core.domain import Boundary, Domain
from qmw.core.field_frame import ConservationData, ObservableData, StateData
from qmw.core.module_spec import ModuleSpec, PortSpec


@dataclass
class SchrodingerConfig:
    n: int = 2048
    x_min: float = -50.0
    x_max: float = 50.0
    boundary: Boundary = "dirichlet"
    hbar: float = 1.0
    mass: float = 1.0
    potential: np.ndarray | None = None      # V(x); zeros if None
    absorber: np.ndarray | None = None       # W(x) >= 0; none if None
    initial_psi: np.ndarray | None = None    # normalised Gaussian at 0 if None


SPECS = {
    "schrodinger": ModuleSpec(
        "schrodinger", "Schrödinger evolution",
        r"i\hbar\,\partial_t\psi = \left[-\tfrac{\hbar^2}{2m}\partial_x^2 + V(x) - iW(x)\right]\psi",
        (PortSpec("psi", "complex field"), PortSpec("V", "potential (control)")),
        (PortSpec("psi", "complex field, next tick"),),
        "Crank–Nicolson; unitary when W = 0."),
    "probability_density": ModuleSpec(
        "probability_density", "Probability density", r"\rho = |\psi|^2",
        (PortSpec("psi", "complex field"),), (PortSpec("rho", "density per unit length"),)),
    "probability_current": ModuleSpec(
        "probability_current", "Probability current",
        r"j = \tfrac{\hbar}{m}\,\mathrm{Im}(\psi^*\partial_x\psi)",
        (PortSpec("psi", "complex field"),), (PortSpec("j", "probability flow"),),
        "Evaluated on links between grid points so continuity holds exactly."),
    "energy_density": ModuleSpec(
        "energy_density", "Energy density",
        r"\mathcal{E} = \tfrac{\hbar^2}{2m}|\partial_x\psi|^2 + V|\psi|^2",
        (PortSpec("psi", "complex field"), PortSpec("V", "potential")),
        (PortSpec("E_K", "kinetic"), PortSpec("E_V", "potential"), PortSpec("E", "total"))),
    "energy_flux": ModuleSpec(
        "energy_flux", "Energy flux",
        r"S = -\tfrac{\hbar^2}{m}\,\mathrm{Re}(\dot\psi^*\,\partial_x\psi)",
        (PortSpec("psi", "complex field"),), (PortSpec("S", "energy flow"),),
        "Pairs with the |grad psi|^2 energy density: dE/dt + dS/dx = (dV/dt) rho."),
}


class SchrodingerModel:
    model_id = "schrodinger_1d"
    specs = SPECS

    def __init__(self, config: SchrodingerConfig | None = None):
        self.config = c = config or SchrodingerConfig()
        self.domain = Domain.line(c.n, c.x_min, c.x_max, c.boundary)
        self.x = self.domain.coordinates
        self.dx = self.domain.dx
        self.hbar, self.mass = c.hbar, c.mass
        self.V = np.zeros(c.n) if c.potential is None else np.asarray(c.potential, float).copy()
        self.W = np.zeros(c.n) if c.absorber is None else np.asarray(c.absorber, float).copy()
        if self.V.shape != (c.n,) or self.W.shape != (c.n,):
            raise ValueError("potential and absorber must have shape (n,)")
        if np.any(self.W < 0):
            raise ValueError("absorber W(x) must be non-negative")
        self._kin = self.hbar**2 / (2 * self.mass * self.dx**2)
        self._factor_dt: float | None = None
        self.last_midpoint: np.ndarray | None = None

    # ------------------------------------------------------------------ operators
    @property
    def periodic(self) -> bool:
        return self.domain.boundary == "periodic"

    def hamiltonian(self, include_absorber: bool = True):
        n, k = self.config.n, self._kin
        diag = 2 * k + self.V - (1j * self.W if include_absorber else 0)
        H = diags([np.full(n - 1, -k), diag, np.full(n - 1, -k)], [-1, 0, 1], format="lil", dtype=complex)
        if self.periodic:
            H[0, n - 1] = -k
            H[n - 1, 0] = -k
        return H.tocsc()

    def apply_h(self, psi, include_absorber=False):
        if self.periodic:
            lap = np.roll(psi, 1) + np.roll(psi, -1) - 2 * psi
        else:
            lap = -2 * psi
            lap[1:] += psi[:-1]
            lap[:-1] += psi[1:]
        out = -self._kin * lap + self.V * psi
        return out - 1j * self.W * psi if include_absorber else out

    def link_gradient(self, psi):
        """(left value, forward difference) on every link; Dirichlet adds the two wall links."""
        if self.periodic:
            return psi, (np.roll(psi, -1) - psi) / self.dx
        padded = np.concatenate([[0], psi, [0]])
        return padded[:-1], np.diff(padded) / self.dx

    def links_to_nodes(self, e):
        if self.periodic:
            return 0.5 * (e + np.roll(e, 1))
        node = 0.5 * (e[:-1] + e[1:])
        node[0] += 0.5 * e[0]
        node[-1] += 0.5 * e[-1]
        return node

    def divergence(self, links):
        return (links - np.roll(links, 1)) / self.dx if self.periodic else np.diff(links) / self.dx

    def current_links(self, psi):
        left, d = self.link_gradient(psi)
        return (self.hbar / self.mass) * np.imag(np.conj(left) * d)

    # ------------------------------------------------------------------ protocol
    def initialize(self) -> StateData:
        psi = self.config.initial_psi
        if psi is None:
            from qmw.physics.schrodinger.states import gaussian_packet
            psi = gaussian_packet(self.x, 0.0, 2.0, 0.0)
        psi = np.asarray(psi, complex).copy()
        if psi.shape != (self.config.n,):
            raise ValueError("initial_psi must have shape (n,)")
        return StateData(psi=psi)

    def apply_controls(self, state: StateData, controls) -> float:
        work = 0.0
        if controls is not None and controls.potential is not None:
            newV = np.asarray(controls.potential, float)
            work = float(np.sum((newV - self.V) * np.abs(state.psi) ** 2) * self.dx)
            self.V = newV.copy()
            self._factor_dt = None
        if controls is not None and "absorber" in controls.params:
            self.W = np.asarray(controls.params["absorber"], float).copy()
            self._factor_dt = None
        return work

    def step(self, state: StateData, dt: float) -> StateData:
        if self._factor_dt != dt:
            A = identity(self.config.n, dtype=complex, format="csc") + (0.5j * dt / self.hbar) * self.hamiltonian()
            self._lu = splu(A)
            self._factor_dt = dt
        psi = state.psi
        rhs = psi - (0.5j * dt / self.hbar) * self.apply_h(psi, include_absorber=True)
        nxt = self._lu.solve(rhs)
        self.last_midpoint = 0.5 * (psi + nxt)
        return StateData(psi=nxt)

    def compute_observables(self, state: StateData) -> ObservableData:
        psi, dx, hb, m = state.psi, self.dx, self.hbar, self.mass
        rho = np.abs(psi) ** 2
        left, d = self.link_gradient(psi)
        j_links = (hb / m) * np.imag(np.conj(left) * d)
        ek = self.links_to_nodes((hb**2 / (2 * m)) * np.abs(d) ** 2)
        ev = self.V * rho
        hpsi = self.apply_h(psi)
        psidot = -1j * hpsi / hb
        grad_nodes = self.links_to_nodes(d) if self.periodic else 0.5 * (d[:-1] + d[1:])
        S = -(hb**2 / m) * np.real(np.conj(psidot) * grad_nodes)
        norm = float(rho.sum() * dx)
        xm = float(np.sum(self.x * rho) * dx / norm) if norm > 0 else 0.0
        xs = float(np.sqrt(max(np.sum((self.x - xm) ** 2 * rho) * dx / norm, 0))) if norm > 0 else 0.0
        K, U = float(ek.sum() * dx), float(ev.sum() * dx)
        return ObservableData(
            probability_density=rho, phase=np.angle(psi),
            probability_current=self.links_to_nodes(j_links), probability_current_edges=j_links,
            kinetic_energy_density=ek, potential_energy_density=ev, total_energy_density=ek + ev,
            energy_flux=S, norm=norm, total_energy=K + U, kinetic_energy=K, potential_energy=U,
            position_mean=xm, position_spread=xs)

    def conserved_quantities(self, state, observables) -> ConservationData:
        return ConservationData(norm=observables.norm, energy=observables.total_energy)

    def absorption_rate(self, psi) -> float:
        """Probability per unit time removed by the absorber, -dN/dt from W."""
        return float((2 / self.hbar) * np.sum(self.W * np.abs(psi) ** 2) * self.dx)

    def continuity_residual(self, before: StateData, after: StateData, dt: float) -> float:
        """max |d rho/dt + div j + (2/hbar) W rho| / max |d rho/dt|, all at the CN midpoint."""
        mid = 0.5 * (before.psi + after.psi)
        drho = (np.abs(after.psi) ** 2 - np.abs(before.psi) ** 2) / dt
        res = drho + self.divergence(self.current_links(mid)) + (2 / self.hbar) * self.W * np.abs(mid) ** 2
        scale = max(np.abs(drho).max(), 1e-300)
        return float(np.abs(res).max() / scale)

    def energy_continuity_residual(self, before: StateData, after: StateData, dt: float) -> float:
        """Approximate: max |dE/dt + dS/dx| / max |dE/dt| away from absorbers, with S at the
        midpoint and central differences, so expect O(dx^2 + dt^2), not round-off."""
        eb = self.compute_observables(before).total_energy_density
        ea = self.compute_observables(after).total_energy_density
        S = self.compute_observables(StateData(psi=0.5 * (before.psi + after.psi))).energy_flux
        if self.periodic:
            divS = (np.roll(S, -1) - np.roll(S, 1)) / (2 * self.dx)
        else:
            divS = np.gradient(S, self.dx)
        dE = (ea - eb) / dt
        mask = self.W == 0
        mask[:2] = mask[-2:] = False
        res = (dE + divS)[mask]
        return float(np.abs(res).max() / max(np.abs(dE[mask]).max(), 1e-300))
