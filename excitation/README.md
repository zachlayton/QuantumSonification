# Born Transition Engine

`BornTransitionEngine` is a transition-centred hydrogen source for QMW. It
implements the first practical layer suggested by Max Born's account of atomic
spectra:

```text
energy difference       -> photon frequency
E1 selection rules      -> allowed line set
radial dipole overlap   -> relative line strength
frequency^3 * strength -> spontaneous-emission branching
initial population      -> event probability
relative state phase    -> compact phase descriptor
state lifetime          -> physical and sonic linewidth
fixed global scaling   -> ratio-faithful audible frequency
```

Run a deterministic demonstration:

```bash
python examples/born_transition_demo.py
```

The default mapping anchors the hydrogen ionization-limit frequency to
1760 Hz and applies that single scale factor to every transition. Frequency
ordering and all ratios are therefore preserved exactly and reproducibly.

Compare the legacy per-line octave-folded mapping:

```bash
python examples/born_transition_demo.py --mapping octave_fold
```

Run population-weighted stochastic selection:

```bash
python examples/born_transition_demo.py --stochastic --steps 24
```

Use it in the canonical resonator engine:

```bash
python quantumsonification_engine.py \
  --implementation resonator_v9 \
  --excitation-source born_transition
```

Choose an isotope preset at startup:

```bash
python quantumsonification_engine.py \
  --implementation resonator_v9 \
  --excitation-source born_transition \
  --born-species He-4+
```

Available one-electron presets are `H-1`, `H-2`, `H-3`, `He-3+`, `He-4+`,
`Li-6++`, and `Li-7++`. The energy model includes the isotope reduced-mass
correction. The lifetime demonstration applies the leading hydrogenic
`1 / Z^4` scaling, so the helium and lithium ions move much faster than
hydrogen while isotopes of the same element differ mainly by a small pitch
shift.

Each new lifetime-scaled event publishes:

```text
/qmw/excitation/born/transition
    event_id index initial_label final_label audio_frequency_hz probability
    duration_ms linewidth_hz relative_phase_rad photon_frequency_hz
    wavelength_nm delta_energy_ev frequency_mapping audio_scale_factor

/qmw/excitation/born/audio_frequency_hz
/qmw/excitation/born/probability
/qmw/excitation/born/duration_ms
/qmw/excitation/born/linewidth_hz
/qmw/excitation/born/active_index    event_id index
```

The complete 14-row catalog is also repeated every five seconds so a display
opened after the engine starts can recover without waiting through the event
sequence:

```text
/qmw/excitation/born/catalog/begin  revision count species mapping
/qmw/excitation/born/catalog/row    index species initial final audio_hz
    probability duration_ms linewidth_hz photon_thz wavelength_nm
    delta_energy_ev branching_probability
/qmw/excitation/born/catalog/end    revision count
```

Open `max/QMW_Born_Transition_Catalog_v1.maxpat` for the table, aligned
frequency/probability/duration multisliders, active-event marker, and isotope
menu. Its inlet expects the output after this routing chain:

```text
udpreceive 7400 -> OSC-route /qmw -> OSC-route /excitation -> OSC-route /born
```

The menu sends `/qmw/excitation/born/species` to control port 7402 and the
engine immediately publishes a fresh catalog.

## Scientific boundary

- Photon frequencies are computed from `delta_E / h`.
- The presets are hydrogenic one-electron systems. `He-3+`/`He-4+` and
  `Li-6++`/`Li-7++` are ions, not neutral many-electron helium or lithium.
- `H-3` is radioactive metadata, but beta decay is a nuclear process and is
  not synthesized by this electronic E1 transition engine.
- Only basic electric-dipole rules are included: `|delta_l| = 1`,
  `|delta_m| <= 1`, and unchanged spin.
- Hydrogen radial dipole integrals are numerically evaluated. The angular
  factor is a polarization-averaged proxy; Zeeman, hyperfine, polarization,
  and relativistic structure are not yet resolved.
- Demo populations, coherences, and phases describe a deliberately excited
  coherent ensemble. They are controls, not a thermal-equilibrium model.
- Optical frequencies use one fixed global scale by default. The hydrogen
  ionization limit maps to 1760 Hz, preserving transition ordering and ratios.
  Audio frequency remains a transposition, not literal atomic sound.
- Legacy per-line octave folding is available with `--mapping octave_fold` for
  artistic comparison, but it intentionally discards absolute register.
- Physical lifetimes are time-scaled into playable durations. Both the
  physical linewidth and the time-scaled sonic linewidth are retained.
- `QuantumDescriptor.topology` and `.curvature` are compatibility projections
  for the existing Hamiltonian translator, not claims about physical topology
  or spacetime curvature.
