# QMW ZX Density Matrix Engine v1

This Max companion turns the Processing discard-ZX density frame into a stable
Max/Jitter/audio engine. It does not use `oscparse`; it follows the project's
installed CNMAT `udpreceive` + `OSC-route` convention.

## Start it

1. Start the bridge:

   ```sh
   cd /Users/zlayton/QuantumSonification
   conda activate music
   python -m zx_modular_v1.examples.processing_density_bridge
   ```

2. Open `QMW_ZX_Density_Matrix_Engine_v1.maxpat`.
3. Run the Processing ZX sketch.
4. Press `Q` in Processing for the mixed-state example, `2` for Bell, or any
   digit `1` through `8` for a generalized cat-state preset. You can instead
   construct or import any valid one- through eight-qubit ZX state/map. Keep
   the density inspector open with `D`.
5. Click Max's `ezdac~` after the first revision appears.

The bridge sends identical frames to Processing `7497` and Max `7498`.

The presets are only shortcuts. `2` produces the natural 4×4 Bell density
matrix, `3` produces the natural 8×8 GHZ₃ matrix, and `8` produces the exact
256×256 eight-output matrix. Hand-built and circuit-derived ZX diagrams use
the same evaluator. Only an explicit Return commit to the separate fixed
four-qubit resonator embeds a smaller matrix into 16×16.

## Atomic frame behavior

Max reads the announced dimension and stages all 2 through 256 complex rows
under a revision number. It updates nothing downstream until the matching
`/end` arrives and every row is present. An incomplete or mismatched frame is
rejected, so audio and Jitter consumers never observe a half-written matrix.

Every committed frame produces:

- a two-plane complex Jitter matrix;
- separate real, imaginary, normalized-magnitude, and phase/π matrices;
- `2^N` basis probabilities;
- trace, purity, ℓ₁ coherence, entropy, minimum eigenvalue, and success weight;
- `N` reduced-qubit Bloch vectors, local purities, and local entropies.

The Jitter streams are available through:

```text
receive qmw.zx.rho.complex.matrix
receive qmw.zx.rho.real.matrix
receive qmw.zx.rho.imag.matrix
receive qmw.zx.rho.magnitude.matrix
receive qmw.zx.rho.phase.matrix
```

Exact flat lists are sent through the following buses through dimension 128:

```text
receive qmw.zx.density.real
receive qmw.zx.density.imag
receive qmw.zx.density.magnitude
receive qmw.zx.density.phase
receive qmw.zx.density.probabilities
receive qmw.zx.density.metrics
```

At dimension 256 the full 65,536-cell data remains available through the
Jitter matrix buses; oversized flat lists are suppressed to avoid Max atom-list
limits. The current dimension and qubit count are available through
`receive qmw.zx.density.dimension` and
`receive qmw.zx.density.qubits`. These names make the density matrix a reusable
Max engine rather than data trapped inside the companion patch.

## Active Pauli gadget

The same port also accepts the visual gadget messages:

```text
/qmw/zx/pauli/verified label weight theta verified error message
/qmw/zx/pauli/score_verified count verified error message
/qmw/zx/pauli/active gadget_id label theta verified
/qmw/zx/pauli/live revision label weight expectation theta verified
```

The JavaScript receiver republishes the live tuple through
`receive qmw.zx.pauli.live` and exposes individual sends for
`qmw.zx.pauli.label`, `qmw.zx.pauli.weight`,
`qmw.zx.pauli.expectation`, and `qmw.zx.pauli.theta`. These are the exact
values needed by a synthesis or tomography patch; no matrix parsing is
required downstream. The receiver also recomputes the active expectation from
every later `engine_evolution` density frame, so the coefficient continues at
the resonator's 10 Hz matrix rate after a Processing preview is committed.

The complete-score result is also available as
`receive qmw.zx.pauli.score.verified`, while the currently selected visual
macro is published through `receive qmw.zx.pauli.active`.

## Euler decomposition

Verified Processing Euler-lens results arrive on the same port:

```text
/qmw/zx/euler/result request source qubit basis
  theta phi lambda gamma zx_scalar_phase verified error
```

The JavaScript receiver publishes:

```text
receive qmw.euler.result
receive qmw.euler.theta
receive qmw.euler.phi
receive qmw.euler.lambda
receive qmw.euler.gamma
receive qmw.euler.zx_scalar_phase
receive qmw.euler.verified
receive qmw.euler.theta_pi
receive qmw.euler.phi_pi
receive qmw.euler.lambda_pi
receive qmw.euler.gamma_pi
receive qmw.euler.zx_scalar_phase_pi
receive qmw.euler.pi_result
```

These buses use the shared `qmw.euler` convention also emitted by the
conductor/QAC circuit workflow.

The main patch now includes a visible Euler panel. It separates the Processing
request counter and source metadata from the numerical decomposition, shows
theta, phi, lambda, gamma, and the ZX scalar phase in radians, and provides a
compact second readout normalized by π. Once Processing verifies an Euler
selection, its live-lens phase edits refresh this panel automatically; the
changing request number identifies each verified refresh.

## Audible engine

The built-in 16-voice MC instrument is deliberately transparent. It represents
the first 16 basis rows directly and folds higher-dimensional rows modulo 16:

- each diagonal population controls its basis oscillator's amplitude;
- off-diagonal coherence adds excitation;
- the circular phase of each matrix row produces slight frequency detuning.

The audio continues between matrix revisions. Processing diagram edits are
debounced briefly and then become new atomic frames, producing continuous
matrix-controlled sound without unnecessary UDP flooding.

After Return commits the diagram to `resonator_v9`, the resonator takes over
the same atomic stream and publishes its genuinely evolving post-commit matrix
at 10 Hz. Thus Max first previews the visual ZX state and then follows the
Hamiltonian/noise/memory evolution of that state. The rate is configurable:

```sh
python quantum_population_osc_v9_resonator.py \
  --zx-density-matrix-port 7498 \
  --zx-density-matrix-hz 10
```

Use `--zx-density-matrix-port -1` to disable the post-commit stream.

The speaker is off by default.
