# QMW QuantumSonification Foundations Evaluator v1

Open `QMW_QuantumSonification_Foundations_Evaluator_v1.maxpat` in Max 9. The
patch receives CNMAT OSC on UDP port `7474` and evaluates the graph-density and
modal-subspace foundations without identifying `rho_Q`, `rho_G`, and `(K, M)`.

Run the included live publisher from the repository root:

```bash
python max/qmw_foundations_demo_sender_v1.py
```

Use `--frames 1` for a single snapshot or `--port` to match a modified patch.
The publisher imports the repository-local `quantumsonification_foundations_v1`
package by default; override its parent directory with `--foundations-parent`.

## OSC contract

- `/qsf/graph/dimension int`
- `/qsf/graph/rho_real float...` — flattened row-major matrix
- `/qsf/graph/rho_abs float...` — flattened row-major matrix
- `/qsf/graph/metrics entropy purity rank nullity component_count`
- `/qsf/graph/projection frobenius trace_distance imaginary rank_deficit`
- `/qsf/graph/negativity float`
- `/qsf/modal/count int`
- `/qsf/modal/eigenvalues float...`
- `/qsf/modal/stable_ids int...`
- `/qsf/modal/cluster_ids int...`
- `/qsf/modal/overlap float...`
- `/qsf/modal/angles float...` — radians
- `/qsf/modal/residuals float...`
- `/qsf/modal/revision int`
- `/qsf/status string`

The modal raster has one column per mode. Its six rows are eigenvalue, stable
mode ID, cluster ID, overlap confidence, principal-angle confidence, and
generalized-eigenpair residual quality.
