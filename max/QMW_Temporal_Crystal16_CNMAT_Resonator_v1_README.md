# QMW Temporal Crystal 16 → CNMAT Resonant Body v1

This Max instrument extends the stable density-to-CNMAT resonator with a
parallel `/qmw/time/*` receiver. It remains the only patch that should bind
UDP port `7400` during the test.

The density model and its excitation are click-latched:

- `/qmw/cnmat/density_resonator/begin`, `/row`, and `/end` atomically stage
  the newest 256-resonance model without changing the sounding bank;
- the staged model is committed immediately before the next `click~`
  excitation;
- the 256-slot multislider displays the corresponding live gain vector in
  row-major order when that click commits it, so relation `(m,n)` appears at
  zero-based index `16*m+n`;
- `/qmw/time/chronos/tick` produces one fixed, bounded `trigger 0.45`;
- `/qmw/cnmat/density_resonator/trigger` remains the canonical
  threshold-qualified resonance event;
- the legacy `/qmw/temporal-mechanics/v1/density-clock/pulse` route remains
  available but is not required;
- the manual and local-test impulses work without Python.

The resonator output passes through an adjustable makeup stage initialized to
`500`, then through `clip~ -0.98 0.98` before `live.gain~`. This matches the
observed level required by the CNMAT impulse response while bounding unexpected
peaks. Use `live.gain~` for listening level and lower `MAKEUP ×` if the clip
becomes audible.

`GLOBAL RESONANCE FREQUENCY ×` scales every resonance frequency while leaving
its gain and decay unchanged. Changes are click-latched, so the sounding bank
does not move until the next excitation. The `0.5` preset drops the complete
body one octave and `0.25` drops it two octaves; `1.` restores the canonical
frequencies. The control accepts ratios from `0.03125` through `8`.

## Parallel sinusoidal rendering

The same click-latched model also drives `sinusoids~ bwe` in parallel with
`resonators~`. The JavaScript adapter converts each resonance triple
`[frequency, gain, decay]` into the sinusoidal format
`[scaled_frequency, 0.35*gain, 0]`. The final zero requests a clean sinusoid
instead of mistakenly treating resonance decay as bandwidth enhancement.

`SINE BLEND` controls this sustained layer independently from `MAKEUP ×`,
which applies only to the impulse-driven resonators. It initializes to `0.25`;
set it to zero for resonators alone or raise it toward one for a clearer
pitched body.

## First live test: observer mode

Close every other Max patch that receives UDP `7400`, then open
`QMW_Temporal_Crystal16_CNMAT_Resonator_v1.maxpat`. Raise `live.gain~`, enable
`ezdac~`, and run:

```bash
python quantumsonification_conductor.py \
  --with-temporal-crystal \
  --temporal-crystal-mode observer \
  --temporal-crystal-rate 2
```

The resonant model follows the newest canonical density frame only when the
two-Hz Chronos clock excites it; model changes cannot retune a ringing body
between clicks.

## Floquet test

Stop the conductor and restart it with:

```bash
python quantumsonification_conductor.py \
  --with-temporal-crystal \
  --temporal-crystal-mode floquet \
  --temporal-crystal-rate 2
```

Now each logical tick both applies the repeated Floquet map to canonical
`rho` and excites the newly retuned resonant body.

The patch also displays temporal enable state, mode, rate, revision, protocol,
Chronos tick/index/phase, LFSR state, SPQT macrocycle position, Kairos events,
and Aion fields when those messages are published. Click the local `test`
button to populate all 256 sliders without starting Python.

## Switching modes from Max

While the conductor is running, click `observer`, `floquet`, `lfsr`, or
`pythagorean` in the `LIVE TEMPORAL MODE` section. Max sends
`/qmw/time/control/mode` to the existing engine control receiver on UDP `7402`.
The engine swaps protocols under its density-state lock and immediately
publishes `/qmw/time/mode` back to Max as acknowledgement. The new protocol
starts with a fresh logical clock; Python does not need to be stopped.
