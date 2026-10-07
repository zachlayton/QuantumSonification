"""Numerical error measurements with explicit external energy ledgers."""
from __future__ import annotations

import numpy as np

from qmw.core.domain import Domain
from qmw.core.frame import ConservationData, Diagnostics, ObservableData, StateData
from qmw.core.operators import derivative, spectral_tail_fraction


class ConservationMonitor:
    """Track a model's invariants and evaluate local instantaneous continuity.

    Positive work and positive environmental energy mean energy added to the
    system. Each ledger is cumulative; only its change since the reference counts.
    Drift/error channels report absolute magnitudes in scaled physical units,
    never divide by a near-zero reference, and never renormalize or clip state.
    Initial normalized pure/density states should have norm/trace one.
    """

    def __init__(self, domain: Domain):
        self.domain = domain
        self.reset()

    def reset(self):
        """Discard the reference before starting a different physical run."""
        self._reference: ConservationData | None = None
        self._state_kind: str | None = None

    def initialize(
        self,
        state: StateData,
        observables: ObservableData,
        cumulative_work: float = 0.0,
        cumulative_environment_energy: float = 0.0,
    ) -> tuple[ConservationData, Diagnostics]:
        """Set a new reference and report its current normalization/continuity."""
        self.reset()
        return self.evaluate(state, observables, cumulative_work,
                             cumulative_environment_energy)

    def _residual(self, rate, flux) -> float | None:
        if rate is None or flux is None:
            return None
        self.domain.require_periodic_space()
        residual = np.asarray(rate) + derivative(np.asarray(flux), self.domain)
        return float(np.sqrt(self.domain.integrate(np.abs(residual)**2) / self.domain.length))

    def evaluate(
        self,
        state: StateData,
        observables: ObservableData,
        cumulative_work: float = 0.0,
        cumulative_environment_energy: float = 0.0,
    ) -> tuple[ConservationData, Diagnostics]:
        """Return integrated quantities and diagnostics; first call sets reference.

        ``energy_rate`` represents the frozen-control PDE. Consequently local
        residuals check transport at this instant, while ledger-corrected energy
        drift checks the evolution and externally induced energy changes.
        """
        state.validate(self.domain)
        if not np.isfinite([cumulative_work, cumulative_environment_energy,
                            observables.source_power]).all():
            raise ValueError("Energy ledgers and source power must be finite")
        kind = "psi" if state.psi is not None else "rho" if state.rho is not None else "scalar"
        if self._state_kind is not None and self._state_kind != kind:
            raise ValueError("Reset the conservation monitor before switching state kind")

        # Recompute normalization from the actual state so a faulty observable
        # producer cannot conceal a normalization error by reporting norm=1.
        norm = None
        if state.psi is not None:
            norm = float(self.domain.integrate(np.abs(state.psi)**2))
        elif state.rho is not None:
            norm = float(np.trace(state.rho).real)
        energy = observables.total_energy
        if observables.total_energy_density is not None:
            energy = float(self.domain.integrate(observables.total_energy_density))
        charge = observables.total_charge
        if observables.charge_density is not None:
            charge = float(self.domain.integrate(observables.charge_density))
        for value in (norm, energy, charge):
            if value is not None and not np.isfinite(value):
                raise ValueError("Integrated conservation quantities must be finite")

        conservation = ConservationData(norm=norm, energy=energy, charge=charge,
                                        cumulative_work=float(cumulative_work),
                                        cumulative_environment_energy=float(cumulative_environment_energy),
                                        source_power=float(observables.source_power))
        if self._reference is None:
            self._reference = ConservationData(**vars(conservation))
            self._state_kind = kind
        reference = self._reference
        drift = None
        if energy is not None and reference.energy is not None:
            drift = abs(energy - reference.energy
                        - (cumulative_work - reference.cumulative_work)
                        - (cumulative_environment_energy - reference.cumulative_environment_energy))
        charge_drift = None
        if charge is not None and reference.charge is not None:
            charge_drift = abs(charge - reference.charge)

        diagnostics = Diagnostics(
            norm_error=abs(norm - 1.0) if norm is not None else None,
            energy_drift=float(drift) if drift is not None else None,
            charge_drift=float(charge_drift) if charge_drift is not None else None,
            probability_continuity_error=self._residual(
                observables.probability_rate, observables.probability_current),
            energy_continuity_error=self._residual(
                observables.energy_rate, observables.energy_flux),
            charge_continuity_error=self._residual(
                observables.charge_rate, observables.charge_current),
        )
        if state.rho is not None:
            rho = np.asarray(state.rho, dtype=complex)
            diagnostics.trace_error = float(abs(np.trace(rho) - 1.0))
            diagnostics.hermiticity_error = float(np.linalg.norm(rho - rho.conj().T, ord="fro"))
            # The Hermitian part permits an eigenvalue diagnostic even when the
            # input has a Hermiticity error. The original state is not modified.
            eigenvalues = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T))
            diagnostics.positivity_error = float(max(0.0, -eigenvalues.min()))
            if diagnostics.hermiticity_error > 1e-12:
                diagnostics.notes.append("Positivity measured on the Hermitian part; input state unchanged.")
        elif self.domain.kind == "space_1d":
            fields = [state.psi] if state.psi is not None else [state.phi, state.pi]
            diagnostics.spectral_tail_fraction = max(
                spectral_tail_fraction(field, self.domain) for field in fields)
            if diagnostics.spectral_tail_fraction > 1e-6:
                diagnostics.notes.append("Resolved field has a high-frequency tail; local product aliasing may affect continuity.")
        return conservation, diagnostics
