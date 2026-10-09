# QMW PhysicsFrame Granular v1

The canonical four-qubit density engine now drives granular synthesis through
the shared QMW state architecture. No standalone XY reference model is in the
live audio path.

```text
DensityMatrixEngine
      |
      v
QuantumStateFrame (one authoritative engine tick)
      |
      +--> StateBus --> QuantumFrameAccumulator --> PhysicsFrame[2048]
      |
      +--> QuantumGranularProjector --> /qmw/grain UDP 7405
```

The same `QuantumGranularProjector` can process a complete accumulated block:

```python
frame = engine.physics_frame()
controls = engine.granular_controls()
```

## Mapping

The current mapping uses transport quantities already published by the live
four-qubit engine:

- local excitation center -> buffer position
- normalized entropy of the four local excitation weights -> grain duration
- signed nearest-neighbor probability-current direction -> playback rate
- strongest local excitation probability -> amplitude
- spatial center of current activity -> stereo pan
- total nearest-neighbor current activity -> grain density

The transforms use physical bounds or saturating mappings and therefore do not
need future samples for live normalization. These are explicit musical
projections; they are not claims that audio parameters are quantum observables.

## OSC

Default destination: `127.0.0.1:7405`

```text
/qmw/grain
revision
simulation_time
position
duration_ms
rate
amplitude
pan
density_hz
```

The output is enabled by default in `DensityMatrixEngine`. It can be disabled
for headless/test use:

```python
engine = DensityMatrixEngine(enable_granular_output=False)
```

or redirected:

```python
engine = DensityMatrixEngine(
    granular_osc_host="127.0.0.1",
    granular_osc_port=7405,
)
```

## SuperCollider

Evaluate:

```text
supercollider/qmw_physics_frame_granular_v1.scd
```

The receiver uses `GrainBuf` and the standard SuperCollider example sound by
default. Point `~qmwGranularSource` at another buffer to hear the same quantum
trajectory traverse different material.
