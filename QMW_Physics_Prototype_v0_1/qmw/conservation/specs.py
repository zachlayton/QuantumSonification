from qmw.core.spec import ModuleSpec, PortSpec


def module_specs() -> tuple[ModuleSpec, ...]:
    return (ModuleSpec(
        "conservation", "Conservation and Numerical Diagnostics",
        r"R_p=\partial_t p+\partial_x j,\quad R_E=\partial_t\mathcal E+\partial_x S_E,\quad\delta E=E-E_0-W-E_{\rm env}",
        "R_p = d_t p + d_x j; R_E = d_t e + d_x S; delta_E = E - E0 - work - environment",
        inputs=(PortSpec("observables", "instantaneous rates, currents and integrals", "model-specific", "model domain"),),
        outputs=(PortSpec("diagnostics", "continuity RMS, drift and matrix invariant errors", "model-specific", "scalar"),),
        description="Energy drift subtracts signed work and environment increments; local rates hold controls fixed. Matrix diagnostics include trace, Hermiticity and positivity without state correction.",
        destinations=("Telemetry", "Inspector", "Recording"),
        assumptions=("Positive source ledgers denote energy added to the system.",
                     "Continuity diagnostics are absolute RMS in scaled units.",
                     "Error magnitudes never divide by an initial energy or charge."),
    ),)
