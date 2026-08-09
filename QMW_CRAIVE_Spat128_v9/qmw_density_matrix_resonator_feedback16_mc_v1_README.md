# QMW Density-Matrix Resonator Feedback 16 MC v1

This Max abstraction inserts the complete complex density-matrix operator into a sixteen-branch MC feedback network surrounding the existing direct-basis resonator bank.

The source GenExpr remains unchanged. Cross-channel coupling occurs outside the replicated `mc.gen~ @chans 16`, because separate MC instances cannot directly read one another's state.

## Signal model

```text
s(t) = x(t) + d(t)
z(t) = Hilbert{s(t)} = I(t) + iQ(t)
y(t) = rho z(t)
p_i(t) = cos(theta_i) y_re,i(t) - sin(theta_i) y_im,i(t)
d_i(t) = g_i Delay_i{p_i(t)}
```

Here:

- `x` is the unchanged 16-channel output of the existing basis-state resonator.
- `s` is the internally coupled resonator state.
- `rho` supplies complete cross-basis complex coupling.
- `theta_i` is a quantum phase projection for feedback branch `i`.
- `g_i` is a non-negative branch feedback magnitude, hard-limited below unity.
- `Delay_i` is the explicit causal memory required by the feedback loop.

No oscillator, LFO, random walk, or autonomous modulation is introduced by this abstraction.

## Files

- `qmw_density_matrix_resonator_feedback16_mc_v1.maxpat`
- `qmw_feedback_branch_controls16_v1.js`
- `qmw_density_matrix_hilbert_operator16_mc_v1.maxpat`
- `qmw_density_matrix16_to_mcs_matrix_v1.js`

Keep all four files in the same Max project or search path.

## Inlets

1. Raw 16-channel MC resonator-bank output
2. `Re(rho)`: exactly 256 row-major floats
3. `Im(rho)`: exactly 256 row-major floats
4. Sixteen projection phases `theta[0..15]` in radians
5. Sixteen feedback gains `g[0..15]`
6. Sixteen feedback delays in milliseconds
7. Control messages

## Outlets

1. Selected output: exact RAW in mode 1, internally coupled state in mode 2
2. Internally coupled 16-channel state `s`
3. Bounded delayed-feedback return immediately before it is summed into the state
4. Density-operator real output `y_re`
5. Density-operator imaginary output `y_im`
6. Combined validation/status messages

The patch starts in mode 1 with every feedback gain at zero and matrix autocommit disabled. Mode 1 also closes a signal-rate return gate, so the feedback loop cannot build up invisibly while the exact resonator baseline is being monitored.

## Controls

```text
mode 1                  exact RAW output (default)
mode 2                  coupled-state output
clear                   clear delay and Hilbert histories; preserve rho
safe                    set all branch feedback gains to zero
panic                   close return immediately, zero gains, and clear delay/Hilbert histories
identity                set rho to complex identity
matrixclear             set both parts of rho to zero
commit                  commit stored Re/Im matrix parts
autocommit 0|1          synchronized or immediate matrix updating; default 0 here
threshold value         density coefficient output threshold; default 0
matrixramp milliseconds density-matrix interpolation time
ceiling 0..0.98         hard maximum for every feedback gain; default 0.92
delayrange min max      branch-delay safety range; default 2..2000 ms
tune f0 h0 ... h15      derive delays as 1000/(f0*hi)
status                  request matrix and feedback diagnostics
```

The controls `ceiling`, `delayrange`, `tune`, `setphase`, `setgain`, and `setdelay` are passed to the branch-control router. Indices for the `set...` messages are zero-based.

## Phase projection

For each branch, feedback is the real projection of a rotated complex output:

```text
Re{exp(i theta_i) y_i}
    = cos(theta_i) y_re,i - sin(theta_i) y_im,i
```

At `theta=0`, feedback uses `y_re`. At `theta=pi/2`, it uses `-y_im`. The phase list must come from quantum data or an explicit test state; the patch does not animate it.

The control router unwraps each new phase onto the nearest equivalent angle, so interpolation follows the short arc across the `-pi/pi` boundary. The sixteen radian values then become one smoothed MC phase signal. `mc.cosx~` and `mc.sinx~` derive both rotation components from that same signal, preserving `cos²(theta)+sin²(theta)=1` throughout a phase transition.

## Delay tuning

To align a feedback branch to the period of the corresponding basis oscillator, send:

```text
tune fundamental_hz h0 h1 ... h15
```

The control router calculates:

```text
delay_i_ms = 1000 / (fundamental_hz * h_i)
```

Values are clipped to the declared delay range. The default 2 ms minimum is above one 64-sample vector at common 44.1/48 kHz rates; increase it if the audio vector size or sample-rate configuration requires a longer causal delay.

## Stability contract

For a physical density matrix, `rho` is Hermitian positive semidefinite with trace one, so its largest eigenvalue is at most one. That makes the density operator non-expansive in the Euclidean norm. The matrix router also accepts arbitrary matrices, for which this guarantee does not hold. Before opening the loop, require negligible `hermitian_error`, `trace_re` near one, `trace_im` near zero, and `frobenius_sq` no greater than one.

Version 1 therefore:

- clamps every branch gain to `[0, ceiling]`;
- caps the ceiling at `0.98`;
- starts with all gains at zero;
- applies gain after the delay so stored feedback follows the current gain rather than its earlier write gain;
- closes the return gate whenever mode 1 is selected;
- provides an immediate `panic` gate in addition to `safe` and `clear`;
- reports density-matrix Hermitian error and branch gain/delay ranges;
- adds no hidden limiter or nonlinear saturation to the coupled path.

The absence of hidden saturation is deliberate: instability remains measurable rather than being silently converted into distortion. Begin below `0.3`, validate the matrix, and raise gains slowly. After `panic`, send `mode 2` again to reopen the return gate.

This is a `real -> analytic -> complex coupling -> real projection` operation on every round trip. It does not preserve an independent complex state inside the delay. A later true-complex version would require separate real and imaginary delay banks.

## Validation sequence

1. Leave mode at 1 and invert/sum outlet 1 against the input. It should null.
2. Select mode 2 while gains remain zero. The coupled state should equal the source.
3. With `autocommit 0`, send both matrix parts and then `commit`. Start with `identity`, phases all zero, and equal low gains such as `0.1`. Each branch should feed itself without cross-basis transfer.
4. Use a real diagonal density matrix. Feedback persistence should follow the diagonal weights.
5. Add a single Hermitian off-diagonal pair. Energy should transfer only between the chosen basis branches.
6. Add nonzero imaginary coherence and compare phase projections at `0` and `pi/2`.
7. Use `tune` with the current fundamental and harmonic-ratio list.
8. Only after frozen-state stability is established should the Hilbert phase-clock update phases or matrix trajectories.

The tuned delay is an initial resonant estimate, not an exact frequency equation: `mc.hilbert~` contributes frequency-dependent phase and `mc.tapout~` has a minimum causal delay determined by the signal-vector configuration.

## Existing resonator connection

Connect the unsummed output of the `mc.gen~ @chans 16` instance loaded with `qmw_density_field_quantum_resonator16_mc_v1.genexpr` directly to inlet 1. Keep any monitoring mixdown after this abstraction. Do not feed a stereo or mono fold-down into the coupling network.
