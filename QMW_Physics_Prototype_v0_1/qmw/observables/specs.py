"""Equations and port semantics for the inspector, shared with actual code."""
from qmw.core.spec import ModuleSpec, PortSpec


def module_specs() -> tuple[ModuleSpec, ...]:
    wave = PortSpec("psi", "complex spatial wavefunction", "scaled amplitude", "space_1d")
    scalar = PortSpec("phi,pi", "complex field and time derivative", "scaled field", "space_1d")
    spatial_assumptions = ("Periodic 1-D Fourier grid; quadrature includes dx.",
                           "Local Fourier product aliasing is measured by continuity diagnostics.")
    return (
        ModuleSpec(
            "probability_density", "Probability Density and Phase",
            r"p=|\psi|^2,\quad\theta=\arg\psi",
            "p = |psi|²; theta = arg(psi)",
            inputs=(wave,), outputs=(PortSpec("probability_density", "probability per spatial length", "1/scaled length", "space_1d"),
                                     PortSpec("phase", "wrapped phase", "radians", "space_1d")),
            description="Density integrates to wavefunction norm; phase is undefined at zero density.",
            destinations=("RegionProjector", "ModalProjector", "ConservationMonitor"),
            assumptions=spatial_assumptions,
        ),
        ModuleSpec(
            "probability_current", "Probability Current",
            r"j=\frac{\hbar}{m}\operatorname{Im}(\psi^*\partial_x\psi)",
            "j = (hbar/m) Im(conj(psi) d_x psi)",
            inputs=(wave,), outputs=(PortSpec("probability_current", "probability flux", "1/simulation time", "space_1d"),),
            description="Current transports probability; it is independent of any audio pitch mapping.",
            destinations=("RegionProjector", "ConservationMonitor"),
            assumptions=spatial_assumptions,
        ),
        ModuleSpec(
            "schrodinger_energy", "Schrödinger Energy Density",
            r"\mathcal E=\frac{\hbar^2}{2m}|\partial_x\psi|^2+V|\psi|^2",
            "e = hbar²/(2m) |d_x psi|² + V |psi|²",
            inputs=(wave, PortSpec("V", "real potential", "scaled energy", "space_1d")),
            outputs=(PortSpec("total_energy_density", "local energy density", "scaled energy/scaled length", "space_1d"),),
            description="Kinetic and potential channels sum to local energy; the integral equals the Hamiltonian expectation.",
            destinations=("RegionProjector", "ConservationMonitor"),
            assumptions=spatial_assumptions,
        ),
        ModuleSpec(
            "schrodinger_energy_flux", "Schrödinger Energy Flux",
            r"S_E=-\frac{\hbar^2}{m}\operatorname{Re}((\partial_t\psi)^*\partial_x\psi)",
            "S_E = -hbar²/m Re(conj(d_t psi) d_x psi)",
            inputs=(wave,), outputs=(PortSpec("energy_flux", "energy crossing a point per time", "scaled energy/simulation time", "space_1d"),),
            description="d_t psi comes from the instantaneous Hamiltonian. Regional incoming flux is minus integrated divergence.",
            destinations=("RegionProjector", "FluxEventDetector", "ConservationMonitor"),
            assumptions=spatial_assumptions + ("Controls held fixed for instantaneous continuity; work is recorded separately.",),
        ),
        ModuleSpec(
            "scalar_energy", "Scalar Field Energy and Flux",
            r"\mathcal E=\tfrac12|\Pi|^2+\tfrac12|\partial_x\Phi|^2+U(|\Phi|^2),\quad S=-\operatorname{Re}(\Pi^*\partial_x\Phi)",
            "e = ½|pi|² + ½|d_x phi|² + U; S = -Re(conj(pi) d_x phi)",
            inputs=(scalar,), outputs=(PortSpec("total_energy_density", "scalar field energy density", "scaled energy/scaled length", "space_1d"),
                                      PortSpec("energy_flux", "scalar energy flux", "scaled energy/simulation time", "space_1d")),
            description="Temporal kinetic, spatial gradient and potential energy are separate channels.",
            destinations=("RegionProjector", "ConservationMonitor"), assumptions=spatial_assumptions,
        ),
        ModuleSpec(
            "scalar_charge", "U(1) Charge and Current",
            r"q=\operatorname{Im}(\Phi^*\Pi),\quad j_Q=-\operatorname{Im}(\Phi^*\partial_x\Phi)",
            "q = Im(conj(phi) pi); j_Q = -Im(conj(phi) d_x phi)",
            inputs=(scalar,), outputs=(PortSpec("charge_density", "Noether charge density", "scaled charge/scaled length", "space_1d"),
                                      PortSpec("charge_current", "Noether charge current", "scaled charge/simulation time", "space_1d")),
            description="Charge is conserved by U(1)-symmetric dynamics; field intensity is not probability.",
            destinations=("RegionProjector", "ConservationMonitor"), assumptions=spatial_assumptions,
        ),
    )
