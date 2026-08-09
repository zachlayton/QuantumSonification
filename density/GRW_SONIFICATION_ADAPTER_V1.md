# GRW sonification adapter v1

This layer renders committed four-qubit GRW events without changing the GRW
model or density matrix. One canonical frame is mirrored to Max, Processing,
and SuperCollider.

## Mapping

| Physics | Renderer operation |
| --- | --- |
| Trace distance | Internal hit/excitation amplitude |
| Fractional coherence loss | Resonator bandwidth and grain structure |
| Affected qubit | Resonator branch 0–3 |
| Dominant Pauli delta | Signed X/Y/Z coupling orientation |
| Post-event `rho` | Persistent branch levels, populations, complex resonant condition |
| `delta_rho` | Transient complex displacement/flash |

Trace distance is retained directly in the default amplitude mapping. Raw
coherence loss and its fraction of pre-event coherence are both retained; the
fraction drives renderer controls so GHZ-scale and partially coherent states
remain comparable. The post-event state is published before the compact event
packet, ensuring the final packet triggers an already-updated resonant body.

## OSC contract

Prefix: `/qmw/grw/sonification`

```text
/post/population       16 floats
/post/branch_levels    4 floats
/post/rho_real         256 floats
/post/rho_imag         256 floats
/post/rho_magnitude    256 normalized floats
/post/rho_phase        256 floats, -1..1 maps -pi..pi
/delta/real            256 floats
/delta/imag            256 floats
/delta/magnitude       256 normalized floats
/delta/phase           256 floats, -1..1 maps -pi..pi
/delta/peak            float, unnormalized peak |delta_rho|
/orientation           signed x y z
/pauli                 dominant_term axis signed_delta
/event                 id branch amplitude coherence_loss_fraction
                       bandwidth grain axis_code sign pauli_delta audible
```

Axis codes are `X=1`, `Y=2`, and `Z=3`. Qubit and branch numbers are zero
based. Low-salience events still update the continuing condition but carry
`audible=0`, so renderers can avoid an artificial transient.

## Receivers

- Max: `max/QMW_GRW_Resonator_v1.maxpat`, UDP 7400.
- Processing: `processing/QMW_GRW_Visualizer3D/`, UDP 7401.
- SuperCollider: `supercollider/qmw_grw_resonator_v1.scd`, language port 57120.

Start the standard resonator engine with its SuperCollider mirror:

```bash
python quantumsonification_engine.py --sc-osc-port 57120
```

The live engine publishes every event in `density_engine.grw_events` after the
authoritative step has committed `rho_after`.

## Deterministic first audition

Open the Max patch, run the Processing sketch, and evaluate the SuperCollider
file. Then send one projective GHZ hit to all three:

```bash
python examples/grw_sonification_demo_v1.py --qubit 2 --basis Z --strength 1
```

This bypasses only the Poisson waiting time; it uses the real GRW channel and
the same adapter as the live engine.

Render the deterministic first-listen experiment offline:

```bash
python examples/grw_ghz_sonification_v1.py \
  --output output/grw_ghz_sonification_v1.wav
```

The render contains a quiet pre-hit GHZ resonant condition followed by the
GRW excitation and continuing `rho_after` modal body.

For scheduled events, enable and configure the authoritative channel on its
internal circuit-control port (normally UDP 7403):

```text
/quantum/grw/enabled 1
/quantum/grw/rate_hz 1.0
/quantum/grw/width 0.25
/quantum/grw/basis Z
```

Configured rates are musically accelerated finite-dimensional analogues, not
claims about physical GRW parameters.

## Validation

```bash
python -m unittest \
  density.test_grw_sonification_adapter_v1 \
  density.test_grw_event_channel_v1
```
