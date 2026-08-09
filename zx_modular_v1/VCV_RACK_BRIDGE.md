# PennyLane + ZX + VCV Rack bridge

## The connection

The useful relationship is deeper than visual resemblance:

| ZX calculus | VCV Rack realization |
|---|---|
| open diagram | patch |
| boundary | external input/output module |
| Z spider | phase-coherent tensor junction |
| X spider | Hadamard-basis tensor junction |
| plain edge | four-channel identity cable |
| Hadamard edge | normalized 2-by-2 mixing stage |
| spider phase | CV-addressable phase parameter |
| rewrite | topology-changing performance gesture |
| equivalent diagrams | audibly different realizations of one linear map |

A logical ZX wire contains two complex amplitudes. Rack voltages are real, so
the faithful cable representation is one four-channel polyphonic cable:

```text
channel 1 = Re(amplitude 0)
channel 2 = Im(amplitude 0)
channel 3 = Re(amplitude 1)
channel 4 = Im(amplitude 1)
```

## Two-stage implementation

### Stage A: OSCelot control bridge

Python owns PennyLane execution, PyZX conversion, semantic verification, and
control-rate descriptors. OSCelot maps `/fader` messages with integer control
ID and normalized float value onto arbitrary Rack parameters or exposes them
as CV through OSCelotExpander. The companion Max stream uses the namespaced
address `/qmw/zx/fader`.

This stage is already implemented by `rack_osc.py` and
`examples/pennylane_vcv_live_demo.py`. It deliberately does not send anything
unless `--send` is supplied.

### Stage B: native QMW-ZX Rack plugin

The eventual Rack plugin should contain:

1. `ZX Boundary` — four-channel dual-rail I/O and wire-order display;
2. `Z Spider` — variable arity, phase knob/CV, exact tensor coefficients;
3. `X Spider` — the corresponding Hadamard-basis junction;
4. `H Transform` — explicit four-channel Hadamard cable adaptor;
5. `ZX Conductor` — imports patch-plan JSON and performs rewrite transactions;
6. `ZX Scope` — amplitude, phase, norm, and semantic-error monitoring.

Rack 2 plugins are C++ modules built with the Rack SDK. The SDK is not
currently present locally, so Stage B should begin only after installing the
SDK matching Rack 2.4.1.

## Real-time boundary

PennyLane and graph simplification must never execute in Rack's audio thread.
The Python process publishes immutable topology revisions and smoothed
control-rate frames. Rack acknowledges a complete revision, swaps it between
audio blocks, and owns all sample-rate processing.

Audio feedback also remains distinct from a closed ZX wire. Feedback requires
an explicit delayed sonic edge; tensor contraction does not supply that delay.

## Global phase

PennyLane's `RZ(theta)` and a ZX Z-phase spider can differ by a quantum-global
phase. A quantum backend may discard it, but a modular instrument can reveal it
by interference with a reference oscillator. The bridge therefore carries the
PyZX scalar and leaves three explicit realization policies:

- preserve it in the four-channel signal;
- ignore it as physically global;
- sonify it against a reference.
