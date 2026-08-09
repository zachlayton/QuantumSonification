# Bloch Harmonics Resonator OSC + IR + Spat5 v5

Open `QMW_Bloch_Harmonics_GenExpr_OSC_IR_Spat_v5.maxpat` with the files in this directory kept together.

## Spatial mapping

- Azimuth: `atan2(Bloch Y, Bloch X)`, in degrees.
- Elevation: `90° - Bloch theta`.
- Distance: `1 + 1.5 * (1 - Bloch radius)` metres.
- Aperture: `20° + 140° * (1 - normalized purity) + manual trim`, clipped to 0–180°.
- Yaw: Bohmian local phase, converted from radians to degrees, plus a manual trim and wrapped to ±180°.
- Spatial amount: equal-power crossfade between the original stereo signal and the Spat5 binaural rendering.

The convolution stereo pair is collapsed to one mono signal only inside the fully spatialized branch, so `spat5.oper` displays one honest global source (`s1`). The bypass branch remains stereo. The aperture and yaw output displays are read-only OSC-derived results; use **Aperture trim** and **Yaw trim** to offset them.

The Max patch receives Bloch and density data on UDP port 7400. Yaw uses the added OSC message `/qmw/bohm/phase`; restart the conductor after updating `quantum_population_osc_v9_resonator.py` so the running engine publishes it.

## Requirements

- Max 9
- Spat5 (`spat5.oper` and `spat5.spat~`)
- `multiconvolve~`
- `dcblocker~`
