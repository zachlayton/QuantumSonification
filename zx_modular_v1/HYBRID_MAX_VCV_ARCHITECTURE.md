# A hybrid Max + VCV Rack ZX instrument

## Recommendation

Do not translate a Max patch into a Rack patch or make one application the
master copy of the other. Keep one semantics-authoritative ZX graph in the
Python/PennyLane conductor and render two synchronized views.

```text
                    PennyLane circuit
                           |
                     qml.to_zx / PyZX
                           |
              canonical ZX graph + revision
                    /                 \
           Max realization       VCV realization
          semantic laboratory    performance surface
```

## Why both hosts belong

Max 9 is the stronger semantic laboratory. Its patcher can create, delete, and
connect objects programmatically, and one MC patch cord can carry the four real
channels of a dual-rail complex ZX wire. It also already contains the QMW
density, geometry, spatialization, visualization, and OSC ecosystem.

VCV Rack is the stronger embodied performance surface. A Rack polyphonic cable
can carry up to 16 voltage channels, so a four-channel ZX wire fits naturally.
Rack's sequencers, clocks, modulation sources, scopes, and module-browser
workflow invite exploratory patching in a way worth preserving.

## Shared wire protocol

Both renderers use one visible thick cable:

```text
1  Re(amplitude 0)
2  Im(amplitude 0)
3  Re(amplitude 1)
4  Im(amplitude 1)
```

Max renders this as MC(4). Rack renders it as a four-channel polyphonic cable.
A Hadamard edge is not merely a differently colored cord: each host inserts an
explicit normalized mixing adaptor so the transformation remains audible and
inspectable.

## Division of labor

### Max

- edit and visualize the full diagram;
- animate rewrite transactions and show before/after semantic error;
- host tensor contractions, analysis, QMW material descriptors, Jitter, and GL;
- generate or repair host realizations dynamically;
- act as the detailed laboratory and compositional score.

### VCV Rack

- expose phases and interpretation parameters as knobs and CV inputs;
- supply clocks, gates, LFOs, sequencers, random sources, and tactile control;
- host performant audio-rate realizations of accepted modules;
- make rewrites performable with triggers while leaving validation to Python;
- act as the playable instrument panel.

### Python / PennyLane / PyZX

- own the canonical graph and monotonic revision;
- execute circuits and calculate gradients;
- simplify and rewrite graphs;
- reject edits that change semantics when equivalence is required;
- publish an atomic, host-neutral manifest to Max and Rack.

## Synchronization

Both applications may propose edits, but neither mutates canonical state
directly. An edit includes its expected parent revision. The conductor validates
it, creates a new revision, and sends the complete topology to both hosts. Each
host builds a candidate off the audio path and acknowledges it before the
revision becomes active.

Only one performance clock is elected at a time. The follower receives epoch,
tempo, beat, and graph revision rather than attempting to infer timing from
asynchronous control messages.

## Audio connection

Semantic synchronization uses OSC and does not require audio to travel between
applications. With the currently installed Rack Free, optional cross-host audio
can use a virtual audio device. A later Rack Pro setup could instead host Rack
as a plug-in inside Max, but the architecture does not depend on that purchase.

## Current local status

- Max 9.0.5 is installed.
- VCV Rack 2.4.1 Free is installed.
- OSCelot 2.0.0 is present and provides the immediate control bridge.
- PennyLane 0.45.1 and PyZX 0.10.4 are installed in the `music` environment.
- The Rack SDK is not present, so native `QMW-ZX` Rack modules remain the next
  compiled-host milestone.
- `hybrid.py` already emits the paired host manifest and stable revision ID.
