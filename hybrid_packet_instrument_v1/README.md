# QMW Hybrid Gaussian Packet Instrument v1

A playable SuperCollider extension of the preserved Scalar Field v4.2b, with a
pure-state Hamiltonian projection backend and a Max/Spat adapter. Run it from
this repository branch: it depends on the preserved `qmw/QMW_Spectral_V4_Portable`
source tree, which is not present on the current main branch.

## What is implemented

- A shared Gaussian packet cloud with density, duration, carrier, spatial width,
  position, phase, AD density/coupling envelopes, and synthesis/Hamiltonian blend.
- A persistent 16-mode harmonic Ringz body, **derived from the existing resonator
  primitive**, with sine mode shapes. This is an added body; it does not replace
  or feed the internal excitation inlet of existing short-lived voice SynthDefs.
- The inherited ring modulation → warp/wavefold → fuzz DSP, reading the existing
  v4.2b control buses. Stereo output joins the existing source bus. A separate
  hybrid send feeds the existing parallel MiClouds and VST returns. Original seven
  source sends, factory files, and stored presets are unchanged.
- Genuine unitary evolution of a Gaussian state in a discretized box or harmonic
  potential, projected onto 16 sine modes. Both modes use Gaussian temporal packets.
- Sixteen optional dry displacement pickups and the existing CRAIVE 128-channel
  WFS renderer, plus an explicit processed-stereo routing alternative.

This first version is a hybrid excitation prototype, not a phonon many-body
simulation. It has no physical-temperature bath or anharmonic frequency shifts.
Excitation strength is `gain`; density controls emission, not thermodynamic
occupation. Those physics extensions can be added without changing the FX buses.

## Start on your Mac: stereo first

1. Extract the supplied ZIP into a new folder. It includes the preserved portable
   baseline and the addon; keep their relative folders intact. Alternatively use
   the `codex/hybrid-gaussian-packet-v1` branch once published. Keep your running
   instrument folder and local presets intact.
2. Use your existing SuperCollider installation and QMW extensions. MiClouds and
   VSTPlugin remain optional, just as in v4.2b; install/authorize your usual plugins
   on the Mac. Plugin binaries and personal VST state are not bundled.
3. Open `supercollider/StartHybrid.scd`, select the whole file, and evaluate.
   It opens the preserved v4.2b interface and the hybrid panel. Wait for the base
   audio status to become active, then press **Start** in the hybrid panel.
4. Defaults are a continuous sparse cloud: density 8/s, duration 80 ms, carrier
   165 Hz, f0 55 Hz, gain 0.03. Raise monitoring gradually. Base **Sound** must be on.
5. For an AD cloud, set `densityDepth=1` and/or `envelopeDepth=1`, then press
   **AD burst**. `attack` and `release` are the cloud attack/decay durations.
   The body continues ringing after the excitation fades.
6. Use the **existing** base ring/fold/fuzz controls. For Clouds or VST, increase
   hybrid `fxSend`, then raise/load the relevant return in the existing FX window.
   `fxSend=0` and return levels start dry.

To add to an already running **v4.2b** session, evaluate only
`supercollider/HybridPacketAddon.scd` and press Start. Do not reload the complete
base launcher over a performance you want to preserve. Closing the hybrid window
stops only this addon's nodes, buffers, and OSC handlers. Base audio rebuilds stop
this addon; press its Start again after the base reports ready.

## Hamiltonian mode

In a Python environment with NumPy:

```bash
python3 -m pip install -r hybrid_packet_instrument_v1/requirements.txt
python3 hybrid_packet_instrument_v1/python/hamiltonian_engine.py --diagnostics
```

Or double-click `StartBackend.command` after installing NumPy in that `python3`
environment. Set hybrid `blend=1`; intermediate values blend the excitation
forces. The hybrid status line reports live/stale stream status, norm, energy,
kinetic and potential energies. A stale stream fades new Hamiltonian force; body
resonances decay. The backend can be stopped with Ctrl-C.

The Python solver uses dimensionless hbar=m=1, hard walls at x=-1,+1 and 128
interior grid points. `potential=1` adds a harmonic potential inside those walls;
`potential=0` is a free particle in a box. Initial width is the Gaussian density
standard deviation, and momentum controls its spatial phase gradient. Quantum
controls are in the Max panel or OSC (see `python/README.md`). Changing preparation
parameters resets the state; changing `rate` changes only the model-time speed.

Thirty projection updates per second are a **control-rate sonification**, not
2048-sample waveform streaming. Re/Im overlaps modulate quadrature packet carriers.
Global phase therefore becomes audible by deliberate mapping; it is not claimed
to be an independently measurable quantum observable. Spatial frequency and model
energy are not automatically converted into audio Hz. Audio f0 and carrier remain
explicit performance controls. Extremely fast/high-energy settings may exceed the
control-rate representation even though finite-grid evolution remains unitary.

## Max / Spat / CRAIVE

Open `max/QMW_Hybrid_Packets_Spat.maxpat`. It includes the unchanged preserved
CRAIVE renderer and its required source/layout abstractions and license. It needs
Max with MC support and IRCAM Spat5, including `spat5.wfs~` and `spat5.viewer`.
The physical CRAIVE calibration and output mapping must be verified at the lab.

**Stereo FX path:** choose a loopback/aggregate device so SC outputs 1–2 reach Max
inputs 1–2. Select **processed stereo master** in the patch. This includes all
existing QMW audio and the hybrid with ring/fuzz/Clouds/VST. It occupies Spat sources
1 and 2; the other sources receive zero. Click the stereo position message to set
those two locations. It is intentionally a two-source spatialization.

**Distributed field path:** use a device with at least **20 outputs** on SC and
corresponding inputs on Max. With the SC server stopped, select the device and set:

```supercollider
~hybridEnableSpatial = true;
s.options.outDevice = "YOUR 20-OR-MORE-CHANNEL LOOPBACK DEVICE";
```

Then evaluate `StartHybrid.scd`. The wrapper sets 20 output channels before boot.
After base audio is ready, Start the hybrid and set `spatial=1`. Select **16 dry
field pickups** in Max. Click the 16-position message to place these pickups along
a four-metre playback line; this scale is independent of the dimensionless model
box. That message is a starting layout, not a claim of measured source geometry.

| SC output / Max input | Signal |
|---|---|
| 1–2 | Existing processed stereo master plus hybrid stereo and shared FX |
| 3–4 | Existing continuous-field stereo, untouched by addon |
| 5–20 | Hybrid dry displacement pickups at x=(p+1)/17, p=0…15 |

The dry 16-channel tap precedes the stereo nonlinear/Clouds/VST chain. Select one
input path; do not misinterpret the stereo return as 16 independently processed
field signals. Multi-source wet-return spatialization remains future work.

The preserved base's device-selection action caps its channel count at eight.
After using that action, stop the server and rerun the hybrid spatial launcher;
do not assume changing `s.options` on a running server changes the hardware layout.
The addon has a server-side output-count guard as well.

The Max patch starts with its input selector muted, array gain zero, and DSP off.
Configure Max's audio driver and CRAIVE output map, select the intended source
path, enable DSP, and raise array gain. The patch sends 128 discrete WFS outputs
through `mc.dac~`. It does not invent an audio network connection: a configured
loopback/aggregate/hardware link carries SC audio into Max. OSC carries controls.

## Controls and behavior

- UDP 17920: `/qmw/hybrid/start`, `/stop`, `/burst`, or
  `/qmw/hybrid/control/<name> value`.
- UDP 17921: `/qmw/hybrid/physics/<name> value` to Python.
- `blend`: 0 synthesis, 1 Hamiltonian, linear force blend between them.
- `density`: requested 0–4000 packets/s. Effective density is capped at
  256/duration, leaving headroom in each 512-grain pool. Stochastic bursts can
  still exhaust a pool; the grain UGen bounds allocation.
- `normalize`: coherent overlap compensation, not a universal constant-power
  guarantee. The carriers are phase-continuous and packets can overlap coherently.
- `phase`: shared carrier phase. `center` in synthesis spans 0–1; the Python
  preparation center spans -0.8–0.8 in the dimensionless model box.
- `width`: synthesis Gaussian overlap width; Python width is separately defined.
- `gain`: hybrid output level, independent of base source faders. Base Sound off
  stops new hybrid excitation; hybrid Stop immediately frees its ringing body.
- `fxSend`: additional hybrid send only; no eighth slot is inserted into the base
  seven-source preset array.
- The Max panel's right-hand numeric message boxes apply suggested defaults when
  clicked. Merely opening the patch does not overwrite active settings. It does
  not mirror values changed in the SC GUI.

## Validation

```bash
python3 -m unittest discover -s hybrid_packet_instrument_v1/tests -v
python3 hybrid_packet_instrument_v1/python/hamiltonian_engine.py --self-check
```

SuperCollider scripts:

- `CompileCheck.scd`: constructs stereo and spatial SynthDefs without booting audio.
- `ControlCheck.scd`: isolated OSC numeric/shape/order/restart checks.
- `RenderCheck.scd`: offline 20-channel WAV render, no hardware required. It tests
  synthesis, complex-projection excitation, density zero and tail decay. Output
  defaults to your OS temporary directory; `QMW_HYBRID_RENDER` can override it.
- `SmokeTest.scd`: a short low-gain audition after base audio is active.

Verified in this build: seven Python unit tests; actual local UDP backend streaming
and control; SuperCollider 3.13 SynthDef compilation and OSC checks; scsynth offline
render with finite audio in both modes, zero on reserved channels3–4, and tail decay;
Max JSON/object/patchcord checks. Max/Spat execution, third-party plugins, live audio
latency and the physical CRAIVE array are **not yet tested here**.

Original QMW sources and saved presets were not edited. `provenance.json` records
the exact source commit and initial parameters. Copied CRAIVE assets retain their
existing attribution in `max/LICENSE_CRAIVE.txt`.
