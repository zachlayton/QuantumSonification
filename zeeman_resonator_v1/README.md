# QMW Zeeman Resonator v1

**The Triplet Breaks** is a playable Max 9 instrument in which magnetic-field
strength moves spectral sidebands around a carrier. It begins with the normal
Zeeman triplet and expands into sodium-like anomalous D1 and D2 multiplets.

## Open the instrument

1. Run `python3 zeeman_resonator_v1/build_qmw_zeeman_resonator_v1.py` if the
   generated Max files need to be refreshed.
2. Open `QMW_Zeeman_Resonator_v1.maxpat` in Max.
3. Click `ezdac~`.
4. Click the `0., 5. 12000` message to open the magnetic field over 12 seconds.

The patch boots quietly at a 220 Hz carrier, 1 T field, 40 audible Hz/T, and a
conservative master level.

## Signal model

Each polyphonic bank voice is a quadrature pair of ring modulators:

```text
cos(fc)cos(fm) + sin(fc)sin(fm) = cos(fc - fm)  -> left
cos(fc)cos(fm) - sin(fc)sin(fm) = cos(fc + fm)  -> right
```

This isolates the two moving sidebands without replacing ring modulation with
ordinary additive oscillators. The left channel carries the negative Zeeman
displacement and the right carries the positive displacement. The dry carrier,
when present, is the central pi line.

The audible modulator frequency is

```text
fm = abs(shift_factor * B * audible_Hz_per_T)
```

where `shift_factor` retains the relative `g*m` geometry. The physical shift is
also represented in `zeeman_model.py` as

```text
physical_shift_Hz = (mu_B / h) * shift_factor * B
```

with `mu_B / h = 13.99624555 GHz/T`. The separate audible scale is deliberate:
it makes the line structure playable without pretending an optical-frequency
offset is directly audible.

## Presets

- `normal`: one ring voice plus the dry pi carrier, producing a triplet.
- `sodium_d1`: factors 2/3 and 4/3, producing an anomalous quartet.
- `sodium_d2`: factors 1/3, 1, and 5/3, producing an anomalous sextet.

Ring-bank gains use square roots of relative transition strengths followed by
constant-power normalization. Parameter changes are smoothed over 30 ms.

## Files

- `QMW_Zeeman_Resonator_v1.maxpat`: playable instrument.
- `qmw_zeeman_ring_voice_v1.maxpat`: quadrature poly~ voice.
- `qmw_zeeman_controller_v1.js`: field/preset/voice controller.
- `zeeman_model.py`: testable physical and perceptual model.
- `test_zeeman_model.py`: Landé-factor and line-geometry tests.
- `build_qmw_zeeman_resonator_v1.py`: deterministic Max patch generator.
- `render_zeeman_demo.py`: offline quadrature-ring audition renderer.
- `zeeman_resonator_demo.wav`: normal -> D1 -> D2 field-opening audition.
