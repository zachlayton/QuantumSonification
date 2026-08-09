# QMW Laplace/LCHS Sonification v1

An offline, auditable response to arXiv:2512.17980. It renders both the direct
Laplace response and the paper-inspired binary SELECT structure, but does not
claim to simulate a quantum circuit or establish a quantum advantage.

```bash
python qmw_laplace_lchs_sonification_v1/qmw_laplace_lchs_sonification_v1.py
```

The default output directory contains:

- `laplace_response.npz`: canonical numerical samples, analytic reference, and error;
- `qmw_laplace_lchs_render.wav`: stereo perceptual rendering;
- `descriptor.json`: configuration, mapping contract, and validation values.

The probe is `g(t) = exp(-a t) sin(w t)`. Evaluation points are an arithmetic
progression `s_j = (sigma_0 + j delta_sigma) + i(omega_0 + j delta_omega)`.
Magnitude controls finite-burst amplitude, phase controls pan/phase, real(s)
controls decay, imaginary(s) controls modal frequency, and each active binary
time-bit / k-bit pair produces a separate brief relation burst.

Run the tests with:

```bash
python -m unittest qmw_laplace_lchs_sonification_v1.test_qmw_laplace_lchs_sonification_v1
```
