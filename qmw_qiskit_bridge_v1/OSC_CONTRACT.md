# QMW real-time comparison OSC contract

Root: `/qmw/qiskit_compare`. State destination: UDP `17670`. Python control
listener: UDP `17671`. Qubit order is q0-LSB, displayed as `|q3 q2 q1 q0>`.

## Atomic state frame

Every payload begins with the same integer revision. Receivers stage all values
and apply them only when the matching `/frame/end` arrives.

```text
/frame/begin       revision tick period_count transformed_route
/exact/z           revision z0 z1 z2 z3
/transformed/z     revision z0 z1 z2 z3
/difference/z      revision dz0 dz1 dz2 dz3
/exact/zz          revision zz01 zz12 zz23
/transformed/zz    revision zz01 zz12 zz23
/difference/zz     revision dzz01 dzz12 dzz23
/metrics           revision trace_distance exact_purity transformed_purity
/frame/end         revision
```

## Python performance controls, UDP 17671

```text
/control/start
/control/stop
/control/reset
/control/route         aer_noisy | qiskit_trotter_order_1 | qiskit_trotter_order_2 | qiskit_statevector_exact
/control/period        seconds
/control/noise_scale   nonnegative multiplier
```

Noise scale is staged and becomes active only at reset or the next loop
boundary. This prevents one audible trajectory from mixing experimental noise
conditions.

## SuperCollider mix controls, UDP 17670

```text
/mix               reference transformed difference master
/difference/mix    local_z bond_zz trace_distance
/panic
```
