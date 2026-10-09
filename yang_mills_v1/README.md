# QMW Yang–Mills modal excitation v1

An opt-in classical SU(2) lattice field excites the existing QMW sixteen-lane
harmonic-modal resonator. Gauge-invariant local energy controls participation
and field-energy motion controls sustained excitation. The first version keeps
the exact harmonic tuning and the resonator's own damping controls.

## Listen in Max

Requires Python 3.11+, NumPy, Max 8 with MC/Gen, and CNMAT's `OSC-route`.
Use the repository root as the Python working directory. This module runs
from source and needs no Qiskit, MLX, SciPy, or Python OSC dependency.

1. Open `QMW_Hilbert_Suite/QMW_Yang_Mills_Modal_Resonator_v1.maxpat`.
   Its adjacent existing `qmw_density_field_harmonic_modal_resonator16_mc_v4.gendsp`
   must be on Max's search path. The new receiver JS is in the same directory.
2. Start the field:

   ```bash
   python -m yang_mills_v1 --osc --steps 0
   ```

3. Enable the patch's DSP, then raise **Master** gradually from its initial zero.
   The fundamental starts at 55 Hz; receiver coupling starts at 1, multiplying
   the Python adapter's default coupling of 0.5. The sixteen bars show the
   committed energy-excitation magnitudes. The Max console reports energy,
   relative energy drift, Gauss residual, unitarity error and determinant error.
4. Adjust the fundamental and receiver coupling to listen. Use **MUTE** to
   return Master to zero. Ctrl-C releases field excitation; a 750 ms receiver
   watchdog also releases it if the stream disappears. Modes finish their
   acoustic decay after excitation is released.
5. Click **reset** before restarting the Python sender: each new sender starts
   its revision counter at zero, and the receiver rejects stale revisions.

The host owns dedicated UDP port **7416**, so the usual density-field receiver
on 7400 can continue running. Only one Yang–Mills host should own 7416.
The stable reference carrier and excitation floor are disabled in this host,
so a zero-energy field produces no continuing drive.

The adapter's output can also be connected to the parameter inlet of the same
modal DSP in a larger patch. It writes only `m0..m15` and `s0..s15`. To combine
quantum-state and Yang–Mills excitation, build an explicit blend before those
parameters; two independent parameter writers would overwrite one another.
No density-field route, density engine, conductor registration or feedback
matrix is changed by this experiment.

## SuperCollider with spatial deformation

The same field stream also drives the native SuperCollider instrument in
`supercollider/qmw_yang_mills_modal_v1.scd`. Send to its printed language port:

```bash
python -m yang_mills_v1 --osc --port 57120 --steps 0
```

Its `~qmwYMDeformation.(0..1)` control applies an area-preserving spatial flow
to the sixteen-lane excitation map while keeping modal frequencies fixed.
`~qmwYMCoupling.(0..1)` independently sets field-excitation gain. See
[`QMW_YANG_MILLS_MODAL_V1.md`](../supercollider/QMW_YANG_MILLS_MODAL_V1.md) for
loading, GUI controls, the conservation contract and native integration tests.

## Numerical model

This is source-free classical Hamiltonian Yang–Mills evolution in **2+1
dimensions**, on a periodic square spatial lattice in temporal gauge. Lattice
spacing and model time are dimensionless. With `T_a = sigma_a/2`, links and
their left electric fields obey

```text
U(x,i) in SU(2)
E(x,i) = E_a(x,i) T_a
H = 1/2 sum_links,a E_a^2 + beta sum_plaquettes (1 - Re tr(U_p)/2)
dot U = i E U
dot E_a = -left_derivative_a H_magnetic
```

`beta` is the positive magnetic weight in this stated normalization; no
physical unit calibration is implied. Plaquette products follow
`Ux(x) Uy(x+ex) Ux(x+ey)^dagger Uy(x)^dagger`. The force is the analytic
derivative of this potential. Evolution uses symmetric kick / exact SU(2)
exponential drift / kick substeps. There is no numerical reunitarization or
field damping. Initial links are seeded random exponentials; initial `E=0`
satisfies source-free Gauss's law for every initial link configuration.

Under independent site rotations `G(x)`:

```text
U(x,i) -> G(x) U(x,i) G(x+ei)^dagger
E(x,i) -> G(x) E(x,i) G(x)^dagger
Gauss(x) = sum_i [E(x,i) - U(x-ei,i)^dagger E(x-ei,i) U(x-ei,i)]
```

Electric energy, traced plaquette products and the resulting excitation
controls are gauge invariant. This remains a classical field module alongside
QMW's quantum engines; it does not quantize gauge links, simulate a QCD vacuum,
or establish confinement.

`SU2Lattice.covariant_laplacian()` provides a Hermitian positive-semidefinite
analysis operator on fundamental two-component test fields. Its eigenvalues
are gauge invariant. It is available for subsequent modal-spectrum work;
the v1 audio path does not retune from this spectrum or evolve matter fields.

## Excitation mapping

At each lattice site, local energy is the outgoing electric-link energy plus
the plaquette energy anchored at that site. Its sum is the Hamiltonian. A
fixed 4x4 spatial partition accumulates this energy into the sixteen modal
lanes. A 4x4 lattice has one site per lane; smaller lattices leave some lanes
empty, larger lattices group multiple sites per lane.

For each lane with energy `e` and rate `v = abs(delta e) / delta model_time`:

```text
magnitude_target = coupling * sqrt(e / (e + energy_scale))
speed_target = coupling * v / (v + motion_scale)
alpha = 1 - exp(-delta model_time / smoothing_seconds)
```

The adapter smooths magnitude and speed with `alpha` and returns separate
arrays. Calibration is absolute: lowering field energy lowers excitation,
rather than renormalizing every frame to full amplitude. The first frame has
zero speed. Coupling zero makes both arrays zero. These quantities are
artistic excitation controls, not quantum population probabilities or
probability current. No color component is presented as audible quantum phase.

The existing v4 DSP turns magnitude changes into strikes and speed into
noise-driven breath/bow excitation. It retains its own acoustic ring decay and
resonance Q. Phase, pitch ratios, purity, entropy and coherence are not written
by the adapter. This standalone host uses the DSP's constant defaults for
those values, locks exact harmonics, and disables raw spectral morphing.

## Reproducible runs

Dry numerical experiment (no OSC or pacing):

```bash
python -m yang_mills_v1 --seed 7 --size 4 --dt 0.01 --substeps 2 --steps 1000
```

Save a text-only experiment manifest to a new filename:

```bash
python -m yang_mills_v1 --steps 1000 --json output/yang_mills_v1/seed7_run001.json
```

The manifest records parameters, completed steps, initial/final energy and
peak drift/Gauss diagnostics. Existing manifests are never overwritten.

`--dt` is model time per step; `--substeps` subdivides it for integration.
`--model-rate` is model time per wall-clock second in OSC mode. `--fps` controls
wall-clock observation rate, from 2 to 120 Hz, independently of the model step;
the actual rate is also limited by integration cadence and machine throughput.
Smoothing and energy-rate calibration use model time. The default observation
rate is 30 Hz and the default model rate is 1. Numerical dry runs execute as
fast as possible. `--steps 0` runs until interrupted.

## Validation and limits

```bash
python -m unittest discover -s tests -p 'test_yang_mills_v1.py' -v
node tests/test_yang_mills_receiver_v1.js
```

The Python checks cover an independent finite-difference force calculation,
vacuum/pure-gauge stationarity, gauge-covariant trajectories, gauge-invariant
audio controls and Laplacian spectra, energy/constraint preservation,
second-order convergence, bounded excitation, real loopback UDP serialization
and Max patch wiring. The JS test executes the actual receiver with a mocked
Max runtime and checks incomplete/stale/invalid frame rejection, coupling,
watchdog release and sender reset.

Reference run: seed 7, 4x4 lattice, beta 1, amplitude 0.6, 1000 steps at
`dt=0.01`, two substeps. Peak relative energy drift was `5.90e-6` (about
0.00059%); peak Gauss residual was `9.26e-15`. These are finite-run diagnostics,
not a guarantee for arbitrary timesteps or initial amplitudes. Check timestep
convergence for each materially new experiment.

Max DSP compilation, CNMAT bundle decoding and audible playback still require
validation on the target Mac. The headless Python and mocked JS tests do not
establish those runtime results. This first stage provides a dedicated
resonator host; full instrument blending, spatial field visualization and
quantum gauge-field evolution are subsequent work.
