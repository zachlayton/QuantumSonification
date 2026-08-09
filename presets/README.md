# QuantumSonification Conductor Presets

Pre-configured workflows for common use cases.

## Loading a Preset

```bash
python quantumsonification_conductor.py --config presets/resonator_minimal.json
```

## Available Presets

### resonator_minimal.json
Canonical quantum engine only, currently using the `resonator_v9` backend,
with OSC output to Max.
- Lightest resource usage
- Best for real-time interaction
- Use when: testing, performance, interactive work

### resonator_full.json
Quantum engine + geometry pipeline + circuit UI.
- Complete ecosystem
- Use when: comprehensive exploration, generating spectral surfaces + sounds

### resonator_geometry_focus.json
Emphasizes geometry/spectral generation over real-time sonification.
- Use when: generating IRs, exploring surface morphologies

### resonator_recording.json
Records all parameters, OSC, and audio for reproducible sessions.
- Use when: creating compositions, documenting workflows

## Creating Custom Presets

```bash
# Edit parameters directly
python quantumsonification_conductor.py \
  --engine-hz 50 \
  --with-geometry \
  --save-config presets/my_custom.json
```

Then load with `--config presets/my_custom.json`
