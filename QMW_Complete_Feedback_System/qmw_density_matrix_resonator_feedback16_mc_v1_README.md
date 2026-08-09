# QMW Density-Matrix Resonator Feedback 16 MC v1

This abstraction inserts full complex density-matrix coupling into a safe,
causal sixteen-channel feedback field. It is designed to follow the existing
direct-basis resonator hosted as:

```text
mc.gen~ qmw_density_field_quantum_resonator16_mc_v1 @chans 16
```

The original GenExpr is not modified. Its sixteen-channel output becomes the
`raw` input to this abstraction.

## Required runtime files

Keep these four files together on Max's search path or in one Max Project:

- `qmw_density_matrix_resonator_feedback16_mc_v1.maxpat`
- `qmw_feedback_branch_controls16_v1.js`
- `qmw_density_matrix_hilbert_operator16_mc_v1.maxpat`
- `qmw_density_matrix16_to_mcs_matrix_v1.js`

The resonator host also needs:

- `qmw_density_field_quantum_resonator16_mc_v1.genexpr`

## Signal model

```text
state = raw + feedback
z = Hilbert(state) = I + iQ
y = rho z = y_re + i y_im
projected = cos(theta) y_re - sin(theta) y_im
feedback = gain * delay(projected)
```

`mc.tapin~` and `mc.tapout~` provide explicit causal memory. Phase, gain, and
delay are independently controlled for all sixteen branches. Phase lists are
unwrapped along the shortest arc before signal smoothing. Gain is clipped to
`0..0.92` by default, and delays are clipped to `1..2000 ms`.

The gain ceiling assumes `rho` is a valid density matrix, whose operator norm
does not exceed one. The matrix router reports Hermitian error and Frobenius
norm but does not silently repair invalid matrices.

## Inlets

1. 16-channel raw resonator audio
2. `Re(rho)`: exactly 256 floats, row-major
3. `Im(rho)`: exactly 256 floats, row-major
4. 16 projection phases in radians
5. 16 feedback gains
6. 16 delay times in milliseconds
7. control messages

## Outlets

1. audition output: exact raw input in mode 1, recursive state in mode 2
2. complex real field `y_re`
3. complex imaginary field `y_im`
4. matrix and feedback diagnostics

## Control messages

```text
mode 1              exact RAW output and hard-closed feedback gate (default)
mode 2              recursive state output and open feedback gate
panic               close gate, zero gains, and clear delay/Hilbert histories
safe                identity matrix, phase 0, gains 0, delays 10 ms, mode 1
identity            set rho to the complex identity
clear               zero rho
autocommit 0|1      synchronized or immediate matrix updates
commit              emit stored real and imaginary matrices together
threshold value     suppress only smaller matrix coefficients
ramp milliseconds   matrix coefficient interpolation time
ceiling value       feedback-gain ceiling, hard-limited below 1
delayrange min max  legal delay range in milliseconds
tune f r0 ... r15   set delays to 1000/(f*ratio), exactly sixteen ratios
status              report matrix and feedback diagnostics
hilbertclear        clear analytic-filter history
```

## First wiring

Do not mix the resonator down before the feedback abstraction.

```text
[mc.gen~ qmw_density_field_quantum_resonator16_mc_v1 @chans 16]
                              |
                              v
[qmw_density_matrix_resonator_feedback16_mc_v1]
                              |
                              v
[mc.mixdown~ 2 @autogain 1] -> [gain~] -> [ezdac~]
```

Use outlet 1 of the feedback abstraction for monitoring.

The abstraction boots in exact RAW mode with a closed loop. Before connecting
OSC, confirm that mode 1 sounds identical to the source. Then send:

```text
safe
status
```

For the first recursive test, send sixteen zeros to inlet 4, sixteen values of
`0.05` to inlet 5, then:

```text
tune 55 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
mode 2
```

Raise gains slowly. Send `panic` immediately if a matrix stream is invalid or
the feedback becomes unexpectedly loud.

## Density-matrix updates

Branch the already-decoded OSC messages from the conductor's existing ingress.
Do not bind a second receiver to the same UDP port.

For synchronized updates:

```text
autocommit 0
<256 real values to inlet 2>
<256 imaginary values to inlet 3>
commit
```

Both lists use the same row-major convention as the Hilbert operator:
`rho[row,column]` transfers input basis `column` into output basis `row`.
