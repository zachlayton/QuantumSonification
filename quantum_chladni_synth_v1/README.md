# QMW Quantum Chladni Synth v1

This instrument combines finite-register Quantum Phase Estimation with a
playable Laplace–Beltrami modal resonator in Max 9. The simulated four-qubit
density matrix supplies the QPE trial-state weights. Surface eigenvalues become
unitary eigenphases, and measuring the phase register conditions the surface
eigenmode superposition heard and seen in Max.

```text
exact four-qubit statevector → density matrix rho
                                 |
                                 v
quantum features → trial weights |c_j|²
                                 |
surface eigenvalues λ_j → U=exp(2πi·0.875H/λmax) → finite-register QPE
                                 |
                    measured y/2^m → P(j|y) → complex amplitudes a
                                             |
surface eigenbasis V ------------------------+
                    Max: jit.la.mult computes V a
                                             |
surface coordinates → jit.bfg deformation → jit.gl.mesh
                                             |
modal Jitter matrix → resonators~ boundary → stereo audio
```

## Run

From the repository root, start the controller:

```bash
python -m quantum_chladni_synth_v1.quantum_chladni_controller_v1
```

Then open:

```text
quantum_chladni_synth_v1/max/QMW_Quantum_Chladni_Synth_v1_5.maxpat
```

Turn on audio, then press **STRIKE**. A local 24-mode resonator model loads
automatically, so the strike is audible even before Python connects. The local
demo button reloads that fallback model. It does not supply a surface
eigenvector matrix; the Python controller does.

The same audible eight-resonance fallback is embedded directly in each
`resonators~` object's constructor. Therefore basic STRIKE sound does not
depend on OSC, JavaScript, Jitter, or Python initialization.

The default controller loads the committed Tanglecube surface-material and
spectral-geometry packets. If those files are unavailable, it constructs the
analytical Laplacian modes of a rectangular membrane. Use another compatible
packet with:

```bash
python -m quantum_chladni_synth_v1.quantum_chladni_controller_v1 \
  --modal-packet path/to/surface_material.npz \
  --modes 24 --visual-samples 768
```

The material packet must sit beside a `spectral_geometry.npz` containing
`vertices` and `eigenvectors`. Geometry is sampled once for visualization;
the authoritative modal frequencies and decays are not downsampled.

## Jitter matrices

| Matrix | Shape | Meaning |
|---|---:|---|
| `qchladni_modes` | 6 planes × 24 × 1 | frequency, decay, material weight, probability, phase, pan |
| `qchladni_amplitudes` | 2 planes × 1 × 24 | complex quantum-conditioned amplitude vector |
| `qchladni_eigenvectors` | 2 planes × 24 × samples | complex surface eigenbasis |
| `qchladni_coordinates` | 3 planes × 1 × samples | normalized surface coordinates |

`jit.la.mult` performs the complex matrix product `V a`. `jit.bfg` evaluates a
shallow procedural deformation at the same three-dimensional coordinates.
That procedural layer is visually and conceptually distinct from the actual
Laplace–Beltrami eigenfield. `jit.spill` extracts the probability plane for the
Max multislider; the modal matrix remains the shared source of truth.

## Controls

- **QUANTUM** controls probability contrast. At zero, gains follow only the
  material spectrum. At one, normalized quantum probabilities are raised to a
  sixth-power contrast curve, producing selective modes and full quantum pan.
  Bank energy is compensated so the result changes timbre more than volume.
- **DECAY** scales all material decay constants.
- **FREQ SCALE** transposes the modal spectrum without changing its ratios.
- **STRIKE** sends a floating-point impulse amplitude directly to both
  `resonators~` banks, using the object's native impulse method. It enables
  DSP immediately before sending the impulse.
- **MEASURE** sends a measurement gesture to the Python simulator and strikes
  the resonator with the resulting state change.
- **QPE REGISTER QUBITS** selects 2–10 estimation qubits. Low precision leaves
  multiple spectrally compatible modes in the conditional field; high
  precision approaches a single eigenmode when phases are resolvable.
- **RUN** pauses or resumes quantum-frame publication.

OSC output uses the conductor's canonical UDP 7400 bus under `/qmw/chladni`;
Max control messages return on the instrument-private UDP 7473 port.
Each exact 16×16 density frame is also forwarded to the temporal machine on
its established private state port 7444. Its relational Bures-distance pulses
return on 7400 and automatically strike the resonator bank.
The patch follows the established QMW 7400 convention: the `FullPacket` outlet
of `udpreceive 7400` feeds `OSC-route` directly. Outgoing controls are encoded
with `o.pack`. It does not use
`oscparse` or `oscformat`.
On load, Max requests the geometry matrices from the controller, so reopening
the patch does not require restarting Python merely to recover the eigenbasis.
The `OSC REV` and `GEOMETRY N` number boxes are connected before JavaScript:
the revision must count upward and the geometry count should become 768. The
loopback button beside the transport controls sends `/qmw/chladni/status` through
the same UDP 7400 decoder for transport-only diagnosis.

## Requirements

- Max 9 with Jitter;
- CNMAT `resonators~`;
- Python packages already used by the workspace: NumPy, SciPy, and python-osc.

## SuperCollider resonant body

The native SuperCollider front end is
`supercollider/qmw_qpe_chladni_resonator_v1.scd`. Evaluate the complete file
after booting the SuperCollider server, then point the controller at the
sclang language port printed in the post window:

```bash
python -m quantum_chladni_synth_v1.quantum_chladni_controller_v1 \
  --out-port 57120 --control-port 7473 --modes 24 --qpe-bits 5
```

The SuperCollider instrument receives complete `/begin`, `/mode`, and `/end`
transactions before changing the DSP graph. It also buffers the transmitted
surface geometry. For every mode it evaluates

```text
gain_j = sqrt(P(j|y)) * material_j
         * V_j(strike point) * V_j(pickup point)
```

with separate left and right pickup locations. Consequently, moving the strike
onto a nodal line suppresses that mode, while moving the pickups changes the
stereo image through the signed eigenvector field rather than an arbitrary pan
law. The GUI exposes strike X/Y, pickup spread, QPE register width, measurement,
strike, and master level. Evaluate `~qpeChladniStatus.()` for transport state or
`~qpeChladniStop.()` to remove the synth and OSC responders.

Rebuild the patch after editing its generator:

```bash
python quantum_chladni_synth_v1/build_quantum_chladni_synth_v1.py
```

## Scientific boundary

The circuit evolution and QPE distributions are exact local calculations,
followed by the explicitly declared mixed-state contribution. This is a
simulator, not a hardware measurement. QPE uses the finite-register
Dirichlet-kernel law and Bayes-conditions the system register after measuring
the phase register; it does not round eigenvalues by hand. The surface
eigenvectors are genuine numerical Laplace–Beltrami modes. `jit.bfg` supplies
an additional procedural deformation and is not an eigenmode solver.
