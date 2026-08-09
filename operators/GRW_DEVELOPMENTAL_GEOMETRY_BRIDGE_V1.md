# GRW developmental geometry bridge v1

This bridge connects salient, committed GRW events to the existing living
geometry and acoustic-IR pipeline. It does not move collapse ownership out of
the density engine, and it does not regenerate a mesh for every hit.

## Event flow

```text
authoritative GRW event
  -> complete rho_after + delta_rho render frame
  -> salience floor
  -> bounded accumulation batch
  -> pre/post quantum-to-geometric channel projection
  -> strengthened geometric modal drive
  -> smoothed normal-direction developmental perturbation
  -> one asynchronous living mesh/spectrum/material/acoustic revision
  -> inactive IR candidate
  -> ready acknowledgment
  -> crossfade
  -> committed acknowledgment
```

The bridge loads `channel_isometry` and `geometric_eigenvectors` from the
current quantum-eigenfield NPZ. For every accepted GRW event it computes:

```text
rho_before = rho_after - delta_rho
p_before = diag(channel(rho_before))
p_after  = diag(channel(rho_after))
delta_p  = p_after - p_before
```

Current quantum-channel archives use that exact channel projection. Older
living archives created before `channel_isometry` was persisted remain usable:
the bridge detects their saved `coupling_matrix`, reconstructs the original
normalized quantum feature vector and temperature mapping, and compares their
pre/post modal softmax distributions. This migration path does not rewrite the
old archive.

Positive modal changes are projected through the geometric eigenvectors to
form a scalar developmental field. The field is spatially smoothed, retained
with bounded persistence, and applied along mesh vertex normals. The original
topology is preserved.

## Batching and slow regeneration

Defaults are intentionally slow:

```text
salience floor             0.002
batch salience threshold   0.12
minimum events             2
maximum events             32
maximum batch latency      12 seconds
minimum regeneration gap   30 seconds
```

A batch becomes eligible after the regeneration gap when any of these is
true:

- at least two events exceed the accumulated salience threshold;
- the oldest accepted event reaches the maximum latency;
- the maximum pending-event count is reached.

`rho_after` and the deformed mesh are staged before one scheduled living
revision. Spectral geometry, material modes, the quantum eigenfield, timing
snapshot, and acoustic IR are therefore regenerated once per batch.

## Crossfaded IR replacement

The bridge attaches the established `LivingSpectralGeometryOSCPublisher` to
the in-process living geometry. It does not replace or bypass its transaction:

```text
/living/ir/candidate revision path crossfade_ms
/living/ir/ready revision
/living/ir/crossfade/start revision crossfade_ms
/living/ir/committed revision
```

New revisions arriving while an IR is loading or crossfading are already
coalesced by that publisher. Geometry is never made active merely because its
files finished rendering.

## Run

Start from an existing living `current_state.json`:

```bash
python -m operators.grw_developmental_geometry_bridge_v1 \
  algebraic_surfaces/tanglecube_v1/living/current_state.json \
  --grw-port 7462 \
  --out-port 7460 \
  --ack-port 7461 \
  --crossfade-ms 1500 \
  --salience-threshold 0.12 \
  --batch-latency 12 \
  --regeneration-interval 30
```

The main resonator conductor mirrors complete GRW frames to port `7462` by
default. Disable only that mirror with:

```text
--grw-geometry-port -1
```

Bridge status is published alongside living geometry:

```text
/living/grw/pending/events
/living/grw/pending/salience
/living/grw/batch
```

The batch packet contains batch ID, event count, accumulated salience,
strongest mode, strongest modal gain, scheduled living revision, displacement
RMS, and displacement peak.
