# Living Spectral Geometry OSC v1

This is a publication-only adapter. It does not solve operators or mutate
geometry. It watches an atomically published `current_state.json` or subscribes
directly to an in-process `LivingSpectralGeometry` instance.

```bash
python living_spectral_geometry_osc_v1.py \
  output/living_surface/current_state.json \
  --out-port 7460 \
  --ack-port 7461 \
  --crossfade-ms 250
```

Spectral playback defaults can be set with `--spectral-blur-width`,
`--spectral-transition`, and `--spectral-freeze`.

## Two-phase IR activation

```text
Python publishes candidate(version, path, crossfade_ms)
→ Max loads the inactive convolution engine
→ Max sends /living/ir/ready version
→ Python sends /living/ir/crossfade/start version crossfade_ms
→ Max performs the crossfade
→ Max sends /living/ir/committed version
→ Python marks that revision active
```

If loading or crossfading fails, Max sends:

```text
/living/ir/failed version "reason"
```

Only one candidate is active at a time. New living revisions arriving during
load or crossfade are coalesced; after commit or failure, only the newest
queued revision is published. Stale, out-of-order, and commit-before-ready
acknowledgments are rejected on `/living/ir/ack/error`.

Published addresses:

```text
/living/publication/begin
/living/version
/living/revision
/living/model
/living/ir/path
/living/ir/crossfade_ms
/living/ir/candidate
/living/ir/status
/living/ir/queued
/living/ir/crossfade/start
/living/ir/active/revision
/living/ir/active/path
/living/ir/ack/error
/living/spectrum/eigenvalues
/living/spectrum/frequencies
/living/spectral/history/shape
/living/spectral/history/revisions
/living/spectral/history/magnitudes
/living/spectral/history/phase_deltas
/living/spectral/history/frequencies_hz
/living/spectral/history/decay_seconds
/living/spectral/history/transients
/living/spectral/history/phase_domain
/living/spectral/playback/blur_width
/living/spectral/playback/transition
/living/spectral/playback/freeze
/living/spectral/control/error
/living/quantum/probabilities
/living/timing/entropy_bits
/living/timing/participation
/living/timing/mode_count
/living/timing/decay_seconds
/living/timing/damping_rates
/living/timing/mode_weights
/living/state/path
/living/publication/end
```

History matrices are flattened in row-major order after the `shape` message
`frames modes`. The following messages may be sent to the acknowledgment port:

```text
/living/spectral/control/blur_width frames
/living/spectral/control/transition value_0_to_1
/living/spectral/control/freeze 0_or_1
```

The publisher echoes the effective state on `/living/spectral/playback/*`.
Freeze is a downstream spectral-playback hold; it does not stop living geometry
from computing and atomically publishing new revisions.

Max should stage incoming values after `begin`. The matching `end` means the
candidate description is complete; it does not authorize a crossfade. The
crossfade begins only after Max has sent `ready(version)` and received the
matching `/living/ir/crossfade/start` response.

## Max coordinator

Use `js living_spectral_ir_ack_v1.js` as the transaction guard:

```text
inlet 0  candidate / crossfade_start from OSC
inlet 1  ready or failed from the inactive convolution loader
inlet 2  committed from the completed crossfade

outlet 0 load revision path → inactive convolution engine
outlet 1 start revision ms → crossfade controller
outlet 2 ready|committed|failed → OSC acknowledgments
outlet 3 transaction status
```

Route outlet 2 through:

```text
[route ready committed failed]
  → [oscformat living ir ready]
  → [oscformat living ir committed]
  → [oscformat living ir failed]
  → [udpsend 127.0.0.1 7461]
```

The JS never generates `ready` from a timer: the inactive loader must report
that its IR is actually loaded. Likewise, `committed` must come from the
crossfader's completion notification.
