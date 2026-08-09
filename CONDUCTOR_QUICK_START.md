# QuantumSonification Conductor — Quick Start

## TL;DR

**Before:** You ran a versioned engine script manually.

**Now:** You run `python quantumsonification_conductor.py` and it manages everything.

## Try It Right Now (2 minutes)

```bash
cd /Users/zlayton/QuantumSonification

# Start the conductor with the canonical engine
python quantumsonification_conductor.py
```

You'll see:
```
2026-07-13 10:51:00 [QSConductor] INFO: QUANTUMSONIFICATION CONDUCTOR STARTUP
2026-07-13 10:51:00 [QSConductor] INFO: Starting Quantum-Engine...
2026-07-13 10:51:01 [QSConductor] INFO: Conductor started with 1 subprocess(es)

======================================================================
CONDUCTOR STATUS
======================================================================
Conductor running: True
...
  quantum_engine      ✓ RUNNING (PID: 12345) | Uptime: 2.5s
======================================================================

conductor> _
```

Then in the shell:
```
conductor> status        # See all running processes
conductor> shutdown      # Stop everything gracefully
```

That's it! Everything works exactly as before, but now coordinated.

## Use Cases

### Option 1: Just the Engine (What You're Doing Now)
```bash
python quantumsonification_conductor.py
```
- Minimal overhead
- Same as your current workflow
- Max listens on port 7400 (unchanged)

### Option 2: Everything (Engine + Geometry + Circuit UI)
```bash
python quantumsonification_conductor.py --with-geometry --with-circuit-ui
```
- Launches the canonical engine
- Launches geometry/spectral pipeline
- Launches circuit builder UI (Tkinter window)
- All coordinated automatically

### Temporal Mechanics in Max

```bash
python quantumsonification_conductor.py --with-temporal-mechanics
```

The conductor starts and monitors the temporal-mechanics publisher. The engine
sends its live density matrix privately to the temporal bridge; density-state
displacement, not a sequential index, generates clock records. It shares the
normal Max output port `7400`, so no additional UDP receiver is needed.
Messages arrive below `/qmw/temporal-mechanics/v1/density-clock/...`. Change
the Bures-angle distance per pulse with `--temporal-distance 0.04`.

### Temporal Crystal 16

First verify live clocks and OSC without changing the density matrix:

```bash
python quantumsonification_conductor.py \
  --with-temporal-crystal \
  --temporal-crystal-mode observer \
  --temporal-crystal-rate 2
```

Then enable a state-changing protocol:

```bash
python quantumsonification_conductor.py \
  --with-temporal-crystal \
  --temporal-crystal-mode floquet \
  --temporal-crystal-rate 2
```

Available modes are `observer`, `floquet`, `lfsr`, and `pythagorean`. The rate
is independent of the normal engine rate: a 2 Hz temporal layer advances twice
per second even when the canonical engine runs at 100 Hz. Messages use the
existing Max port `7400` under `/qmw/time/*`.

### Option 3: Use a Preset
```bash
python quantumsonification_conductor.py --config presets/resonator_full.json
```
- Pre-configured setups
- Save your own: `--save-config presets/my_workflow.json`

## Commands in Interactive Shell

```
conductor> status              # Show what's running & uptime
conductor> shutdown            # Stop everything gracefully
conductor> restart             # Restart all processes
conductor> help                # Show all commands
conductor> quit                # Exit (same as shutdown)
```

## What Is the Canonical Engine?

`quantumsonification_engine.py` is the stable launcher. It currently selects
the `resonator_v9` implementation, which continues to:

1. Reads audio from `materials/test.wav`
2. Simulates a 4-qubit quantum system
3. Computes metrics (harmonics, Pauli expectations, etc.)
4. Sends OSC to Max on port 7400
5. Listens for control from Max on port 7402

The conductor and Max depend on the stable `qmw-osc-v1` protocol, not the
versioned implementation filename.

## File Locations

```
/Users/zlayton/QuantumSonification/
├── quantumsonification_conductor.py     ← Run this (NEW)
├── quantumsonification_engine.py        ← Canonical engine launcher
├── quantum_population_osc_v9_resonator.py  ← Current implementation
├── CONDUCTOR_GUIDE.md                   ← Full documentation
├── presets/                             ← Workflow configs
│   ├── resonator_minimal.json           ← Just engine
│   ├── resonator_full.json              ← All subsystems
│   └── resonator_geometry_focus.json
└── ... (everything else)
```

## Common Commands

### Start Engine Only
```bash
python quantumsonification_conductor.py
```

### Start Everything
```bash
python quantumsonification_conductor.py --with-geometry --with-circuit-ui
```

### Run in Background (No Interactive Shell)
```bash
python quantumsonification_conductor.py --daemon
```

### Use Your Custom Audio File
```bash
python quantumsonification_conductor.py --audio-path materials/my_audio.wav
```

### Adjust Engine Speed (Hz)
```bash
python quantumsonification_conductor.py --engine-hz 50
```

### Save Configuration for Later
```bash
python quantumsonification_conductor.py \
  --engine-hz 100 \
  --with-geometry \
  --save-config presets/my_setup.json
```

## Troubleshooting

### "Quantum engine won't start"
- Make sure you're in the repo root directory
- Check: `python quantumsonification_engine.py --help` works directly
- Inspect the selected backend: `python quantumsonification_engine.py --describe-implementation`
- Check Python dependencies: `pip install numpy scipy soundfile pythonosc`

### "No module named 'operators'"
- Make sure you're in the repo root (not a subdirectory)
- Verify path: `ls operators/` should show files

### "Can't connect to Max"
- Max should listen on port 7400 (default)
- Check with: `conductor> status` shows `quantum_engine` running
- Try: `python conductor.py --verbose` to see OSC activity

## Is This Required?

**No!** If you prefer:
- You can run the canonical engine directly: `python quantumsonification_engine.py`
- Versioned implementations remain available for reproduction and debugging
- The conductor is optional but recommended for managing multiple subsystems

## Next Step: Read Full Guide

For more details, see `CONDUCTOR_GUIDE.md`:
```bash
less CONDUCTOR_GUIDE.md
```

---

**Questions?** Check the full guide or run `python quantumsonification_conductor.py --help`
