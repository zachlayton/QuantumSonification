# QMW Polyphonic Complex Hilbert Instrument v6.1

Open `QMW_Polyphonic_Complex_Hilbert_Instrument_v6_1.maxpat`. It opens directly
in Presentation Mode. Keep every bundled dependency in the same folder.

v6.1 replaces the cached v1/v2 matrix-feedback chain with newly named,
outlet-safe components:

- `qmw_density_matrix_hilbert_operator16_mc_v2.maxpat`
- `qmw_density_matrix_dualrail_feedback16_mc_v3.maxpat`

The diagnostic outlet is physically and explicitly after all audio outlets.
Consequently, valid `qmw.rho16.status` reports cannot enter `mc.gen~`,
`mc.tapin~`, `mc.unpack~`, or `mc.*~`.

## First sound

1. Start the conductor and wait for the density-frame indicator.
2. Turn on DSP in the lower-right Output panel.
3. Play the onscreen keyboard, a MIDI keyboard, or the chord-on message.
4. The instrument initializes to **ANALYTIC ROTATION**, Analytic Wet `1`,
   Hilbert Depth `1`, Phase Depth `1.5`, and Harmonic Phase Spread `0.08`.

It also initializes Harmonic Lock `1`, Motion Drive `0.1`, Reference Tone
`0.2`, and the excitation floor to `0.0002`, so a fresh open is audible without
manually reconstructing the previous musical state.

Use **RAW** for the baseline, **FULL MATRIX WET** for the complete rho action,
**MATRIX DELTA** to isolate the matrix contribution, and **COMPLEX FEEDBACK**
for the bounded bamboo-like recursive field.

## Field Detection controls

The Presentation interface exposes the three event-detection parameters:

- **Motion Threshold**: minimum density-field speed treated as motion. Lower
  values detect smaller movements. Default `0.025`; try `0.01`.
- **Population Transient Sensitivity**: gain applied to changes in basis
  population. Default `14`; try `18` for more responsive strikes.
- **Phase-Change Sensitivity**: excitation caused by phase discontinuities.
  Default `0.02`; try `0.04` for a more audible phase response.

These are detection controls. **Motion Drive** remains a separate control that
scales sustained excitation after motion has crossed the threshold.

If an old `status` error reappears, quit Max and open this v6.1 host from its
own bundle. Do not substitute the older v1 Hilbert operator or v2 feedback
abstraction.
