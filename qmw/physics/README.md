# QMW physics core: stages 1–4

First slice of the typed physics architecture: Model → State → Observable → Conservation → Projection.
Nothing in this package produces sound parameters.

| Stage | Built | Where |
|---|---|---|
| 1 | 1-D Schrödinger field, 2048 points | `schrodinger/model.py` |
| 2 | ρ = \|ψ\|², phase, probability current j | `SchrodingerModel.compute_observables` |
| 3 | kinetic / potential / total energy density, energy flux S | same |
| 4 | 16-region projector with regional inflows | `qmw/projectors/regions.py` |
| – | conservation diagnostics (numerical vs physical) | `qmw/physics/engine.py` |

```python
from qmw.physics import FieldEngine, ControlState
from qmw.physics.schrodinger import SchrodingerConfig, SchrodingerModel, potentials, states
from qmw.projectors import RegionProjector

model = SchrodingerModel(SchrodingerConfig(boundary="dirichlet"))
engine = FieldEngine(model, dt=1/500, projector=RegionProjector(model.domain, regions=16))
frame = engine.step(ControlState(potential=potentials.harmonic(model.x, 0.2)))
frame.regions.energy          # (16,)
frame.diagnostics.norm_error  # round-off, absorption accounted separately
```

Demo: `python examples/schrodinger_field_demo_v1.py OUTDIR` (figure + 16-voice placeholder audio).
Tests: `python -m pytest qmw/physics`.

## Design decisions

- **Names.** The existing `PhysicsFrame` is a 2048-sample *time trajectory*; it keeps its name and gains
  the alias `PhysicsTrajectory`. The new per-tick spatial snapshot is `FieldFrame`
  (`qmw/core/field_frame.py`). Every field carries a `Domain`, and spatial operations refuse
  non-spatial domains.
- **Integrator.** Crank–Nicolson rather than split-step Fourier: it works with fixed ends
  (`dirichlet`, the string case) and `periodic`, is exactly unitary, and conserves ⟨H⟩ for static V.
  About 0.6 ms per step at N = 2048, so 500 Hz control rate fits with headroom.
- **Exact discrete continuity.** The current lives on links between grid points, so
  ∂ρ/∂t + ∇·j = −(2/ħ)Wρ holds to round-off for the Crank–Nicolson midpoint state. The engine
  reports this residual every tick (about 1e-12).
- **Energy convention.** ℰ = (ħ²/2m)|∇ψ|² + V|ψ|², with S = −(ħ²/m) Re(ψ̇*∇ψ). It integrates exactly
  to ⟨H⟩. The local energy-continuity check is approximate (O(dx², dt²), about 1%) and is off by
  default (`check_energy_continuity=True`).
- **Numerical vs physical.** An absorbing potential −iW(x) removes probability at the edges. The
  engine integrates that loss, so `norm_error = N + absorbed − N0` stays at round-off while N falls.
  Changing V(x) through `ControlState` counts as external work, so `energy_drift` stays at round-off
  during performance.
- **Not here yet.** Lindblad stays with the 4-qubit engines (ρ for a 2048-point field would be 4M
  entries per tick). Eigenmodes (stage 6) should use `scipy.linalg.eigh_tridiagonal` with a select
  range and track modes by overlap. Events (5), OSC (7) and GUI panels (8) consume `FieldFrame`.
  Each observable already has a `ModuleSpec` with its LaTeX equation for the GUI.
