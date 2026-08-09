# QuantumSonification Conductor Guide

## Overview

The **QuantumSonification Conductor** is the master orchestrator for your entire quantum sonification system. It launches and manages the canonical engine, geometry pipelines, circuit UI, and Max patches from a single entry point.

## What It Does

Instead of manually running multiple scripts, the Conductor:

- **Launches** the canonical quantum engine as a subprocess
- **Manages** optional geometry/spectral pipelines
- **Coordinates** the interactive circuit builder UI
- **Routes** OSC signals between components and Max
- **Monitors** process health and uptime
- **Saves/Loads** configurations for reproducible workflows
- **Provides** a unified control interface

## Quick Start

### Option 1: Minimal Setup (Engine Only)

The simplest way to replace your current workflow:

```bash
python quantumsonification_conductor.py
```

This:
- Starts the canonical engine (currently backed by `resonator_v9`)
- Opens interactive shell for control
- Sends OSC to Max on port 7400
- Monitors all processes

Then in the interactive shell:
```
conductor> status          # See what's running
conductor> shutdown        # Stop everything gracefully
```

### Option 2: Full Setup (All Subsystems)

```bash
python quantumsonification_conductor.py --with-geometry --with-circuit-ui
```

This additionally:
- Starts the geometry/spectral pipeline
- Launches the circuit builder UI (Tkinter window)
- Coordinates between all components

### Option 3: Daemon Mode (No Interactive Shell)

For automated workflows or launching in background:

```bash
python quantumsonification_conductor.py --daemon
```

Leave running; press Ctrl+C to stop.

## Using Presets

Presets are pre-configured settings saved as JSON files.

### Load a Preset

```bash
python quantumsonification_conductor.py --config presets/resonator_full.json
```

### Available Presets

| Preset | What It Does |
|--------|-------------|
| `resonator_minimal.json` | Just the canonical engine (smallest footprint) |
| `resonator_full.json` | Engine + geometry + circuit UI (complete system) |
| `resonator_geometry_focus.json` | Engine with low update rate + geometry focus |

### Create Your Own Preset

```bash
# Configure and save in one command
python quantumsonification_conductor.py \
  --engine-hz 50 \
  --with-geometry \
  --audio-path materials/my_audio.wav \
  --save-config presets/my_workflow.json
```

Then load anytime with:
```bash
python quantumsonification_conductor.py --config presets/my_workflow.json
```

## Command-Line Options

### Networking
```bash
--osc-host 127.0.0.1           # OSC server address
--osc-engine-port 7400         # Port for canonical engine output
```

### Engine Configuration
```bash
--engine-implementation resonator_v9  # Replaceable versioned backend
--engine-protocol qmw-osc-v1          # Stable OSC contract
--engine-hz 100                # Quantum simulation frequency
--density-field-hz 30          # Density-field OSC frequency
--diagnostics-hz 20            # Dashboard and /mi frequency
--profile full                 # OSC profile (full; use resonator for lean DSP-only output)
--audio-path materials/test.wav  # Audio file for feedback
```

### Subsystems
```bash
--with-geometry               # Enable spectral pipelines
--with-circuit-ui            # Enable circuit builder UI
--with-qac-bridge           # Enable QAC/OpenQASM circuit analysis
--euler-basis ZXZ           # Shared one-qubit decomposition basis
--euler-processing-port 7497 # Mirror circuit Euler data to Processing
--no-euler                  # Disable Euler reporting
--with-temporal-crystal      # Enable the in-process temporal layer
--temporal-crystal-mode observer  # observer, floquet, lfsr, or pythagorean
--temporal-crystal-rate 2.0  # Logical steps/second, independent of engine Hz
```

When the QAC bridge is enabled, every accepted numeric one-qubit circuit
instruction is decomposed and verified through `qmw.euler`. The normal Max
stream receives `/qmw/circuit/euler/{begin,gate,end}` on port `7400`, while the
Processing ZX instrument receives the same transaction on `7497`. Entanglers,
measurements, and unresolved symbolic gates are recorded as skipped rather
than silently approximated. See `docs/EULER_WORKFLOW.md`.

### Modes
```bash
--daemon                       # Run without interactive shell
--verbose                      # Detailed logging
--quiet                        # Suppress output
```

### Configuration
```bash
--config presets/my.json       # Load configuration from file
--save-config my_config.json   # Save current config and exit
```

## Interactive Commands

Once running, the conductor provides an interactive shell:

```
conductor> status              # Show all processes and uptime
conductor> shutdown            # Gracefully stop everything
conductor> restart             # Restart all processes
conductor> help                # Show commands
conductor> quit                # Exit (alias for shutdown)
```

## Architecture

### Earlier Version-Specific Workflow

```
        ┌──────────────────┐
        │ Max/MSP (OSC UI) │
        └────────┬─────────┘
                 ↑
            [OSC port 7400]
                 ↑
        ┌──────────────────┐
        │ Versioned Engine │  ← Started manually
        │  (quantum sim)   │
        └──────────────────┘
                 ↓
        materials/test.wav
```

### With Conductor

```
    ┌─────────────────────────────────┐
    │   Conductor (Master Process)    │  ← Single entry point
    └──┬──────────────┬────────────┬──┘
       │              │            │
       ↓              ↓            ↓
    ┌─────────┐  ┌──────────┐  ┌────────┐
    │Canonical│  │ Geometry │  │Circuit │
    │ (py)    │  │ Pipeline │  │Builder │
    │         │  │ (py)     │  │(tkinter)
    └────┬────┘  └────┬─────┘  └────┬───┘
         │            │             │
         └────────────┼─────────────┘
                      ↓
              [OSC routing layer]
                      ↓
         ┌────────────────────────┐
         │  Max/MSP OSC Output    │
         │  port 7400, 7401, etc. │
         └────────────────────────┘
```

## Use Cases

### 1. Interactive Real-Time Sonification
```bash
python quantumsonification_conductor.py
# Then play with Max patches while the engine generates metrics
```

### 2. Generate Spectral Surfaces + Sonify
```bash
python quantumsonification_conductor.py --with-geometry
# Geometry pipeline runs in background; the engine generates sounds
```

### 3. Multi-Preset Performance
```bash
# Start with preset 1
python quantumsonification_conductor.py --config presets/resonator_full.json

# In shell: switch presets by editing and reloading
conductor> shutdown
# Then restart with different config
```

### 4. Unattended Recording Session
```bash
python quantumsonification_conductor.py \
  --daemon \
  --engine-hz 100 \
  --with-geometry
# Run in background; Ctrl+C when done
```

### 5. Lightweight Testing (Just the Engine)
```bash
python quantumsonification_conductor.py \
  --quiet \
  --daemon
# Minimum overhead; Max can control via OSC
```

### 6. Temporal Crystal 16

Start with observer mode to confirm `/qmw/time/*` OSC traffic without mutating
the canonical density matrix:

```bash
python quantumsonification_conductor.py \
  --with-temporal-crystal \
  --temporal-crystal-mode observer \
  --temporal-crystal-rate 2
```

After that check, replace `observer` with `floquet`, `lfsr`, or
`pythagorean`. These state-changing modes remain opt-in.

## Configuration Files

### Structure

Presets are JSON files with this structure:

```json
{
  "osc": {
    "host": "127.0.0.1",
    "engine_port": 7400,
    "visual_port": 7401,
    "control_port": 7402
  },
  "engine": {
    "enabled": true,
    "hz": 100,
    "profile": "resonator",
    "audio_path": "materials/test.wav"
  },
  "geometry": {
    "enabled": false,
    "mode": "noncommutative"
  },
  "circuit_ui": {
    "enabled": false
  },
  "temporal_crystal": {
    "enabled": true,
    "mode": "observer",
    "rate_hz": 2.0
  }
}
```

### Editing Presets

You can manually edit preset JSON files to change:
- OSC ports (if Max is on different port)
- Engine frequency
- Which subsystems are enabled
- Audio input file path

## Troubleshooting

### "Failed to start quantum engine"
- Check that `quantumsonification_engine.py` exists in the repo root
- Check Python dependencies: `pip install numpy scipy soundfile pythonosc`
- Run the canonical engine directly to debug: `python quantumsonification_engine.py --verbose`
- Inspect its backend: `python quantumsonification_engine.py --describe-implementation`

### "No module named 'operators'"
- Make sure you're running from the repo root
- Check that reorganization completed (see README after recent cleanup)

### OSC not reaching Max
- Verify Max is listening on port 7400
- Check firewall settings
- Run conductor with `--verbose` to see OSC activity

### One subprocess crashes
- Conductor will warn but keep others running
- Run `conductor> status` to see which died
- Run `conductor> restart` to relaunch everything

## Comparison: Before vs After

### Before (Manual Workflow)
```bash
# Terminal 1
python quantumsonification_engine.py

# Terminal 2
python qmw_circuit_builder_controller.py

# Terminal 3
python operators/operator_ecology_controller_v1.py

# Terminal 4
# Monitor nothing, hope everything works
```

### After (Conductor)
```bash
# One command, everything managed
python quantumsonification_conductor.py --with-geometry --with-circuit-ui

# Interactive shell
conductor> status           # See everything at once
conductor> shutdown         # Clean shutdown of all
```

## Next Steps

1. **Try it**: Start with the minimal setup
   ```bash
   python quantumsonification_conductor.py
   ```

2. **Create a preset**: Save your configuration
   ```bash
   python quantumsonification_conductor.py \
     --engine-hz 100 \
     --save-config presets/my_performance.json
   ```

3. **Integrate with Max**: Update your Max patches to use the new orchestrated setup
   - OSC still comes from port 7400 (or your configured port)
   - Everything is coordinated automatically

4. **Scale up**: Add subsystems gradually
   ```bash
   python quantumsonification_conductor.py --with-geometry
   ```

## Architecture for Future Expansion

### Shared eigenfield conductor track

The canonical engine publishes an eight-lane spatial representation of the
moving density-matrix eigenfield on the main OSC port:

- `/qmw/conductor/eigenfield/layout`
- `/qmw/conductor/eigenfield/lanes`

The layout is eight x-axis sectors. Every lane contains five values in this
order: normalized local density, circular-mean phase, y centroid, mean motion
speed, and particle occupancy. The lanes message is therefore a fixed list of
40 floats. Audio, geometry, visualization, and control patches should derive
their local behavior from this shared track instead of independently reducing
the field to one global scalar. Empty lanes remain zero, which preserves holes
and asymmetry in the field shape.

GrainFlow additionally receives per-stream events derived from these lanes at
`/qmw/conductor/grainflow/event`. Those messages are a renderer-specific view
of the general eigenfield track, not the canonical representation itself.

The conductor also publishes a multiresolution grid pyramid:

- `/qmw/conductor/eigenfield/grid/4`
- `/qmw/conductor/eigenfield/grid/8`
- `/qmw/conductor/eigenfield/grid/16`

Each row-major cell contains normalized density, phase divided by pi, and
particle occupancy. Renderers may switch among 4x4, 8x8, and 16x16 at runtime:
4x4 emphasizes large stable masses, 8x8 exposes mesoscopic structure, and
16x16 retains the full density-matrix field. All levels describe the same
frame, so resolution changes do not interrupt the conductor or quantum engine.

The Conductor is designed to be extended. Future capabilities:

- **MIDI input** → route to engine parameters or circuit UI
- **Audio analysis** → capture energy from input, feed to geometry
- **Parameter morphing** → smoothly transition between presets over time
- **Session recording** → capture all OSC, parameters, audio for playback
- **External clock** → sync the engine to MIDI beat clock or external clock
- **Max remote control** → send commands to conductor from Max patches

## Questions?

Check out:
- `README.md` — Project overview
- `quantumsonification_engine.py` — Stable engine entry point used by the conductor
- `quantum_population_osc_v9_resonator.py` — Current versioned implementation
- `operators/` — Available geometry and spectral modules
- `max/` — Max/MSP patches and control scripts
