# QMW Operator Ecology Lab v1

`QMW_Operator_Ecology_Lab_v1.maxpat` is a four-candidate impulse-response
audition and comparison interface for Max 9.

## Requirements

- Max 9
- HISSTools Impulse Response Toolbox (HIRT), already installed on this system
- CNMAT Externals (`OSC-route` and `OpenSoundControl`), already installed
- Stereo IR files (WAV, AIFF, or FLAC)

The audio core is one `multiconvolve~ 2 8 medium` matrix. Two live inputs feed
four independent stereo candidate paths. `medium` mode uses HIRT's efficient
512-sample latency option and supports dynamically sized long IRs.

## First use

1. Open `QMW_Operator_Ecology_Lab_v1.maxpat`.
2. Click the `ezdac~` speaker control to enable audio.
3. Run a QMW resonator patch, or click **IMPULSE TEST**.
4. Move X/Y to interpolate among A–D, or click a slot's **audition** button.
5. Drag another stereo IR onto any candidate slot to replace it.

Slots A and B preload the current Tanglecube and Heart IRs. Slots C and D are
available for new candidates.

The excitation source defaults to **QUANTUM GENEXPR**. Connect the 16-channel
output of `qmw_density_field_quantum_resonator16_mc_v1.genexpr` to
`qmw_quantum_mc_to_ecology_bus_v1`. The adapter applies
`mc.mixdown~ 2 @autogain 1` and publishes `qmw_spectral_L/R`; this lab receives
those signals before convolution. Choose **AUDIO INPUT** only when an interface
or microphone should excite the IRs. The impulse test is mixed into either
source for diagnostics.

The Max connection is:

```text
[mc.gen~ @chans 16]
          |
[qmw_quantum_mc_to_ecology_bus_v1]
```

The X/Y field uses equal-power bilinear interpolation: A/B occupy the lower
edge, C/D the upper edge, and the four candidate power weights sum to one.

## Living pipeline handshake

- Max receives OSC on port `7460`.
- Max sends acknowledgments to `127.0.0.1:7461`.
- Incoming packets use `udpreceive 7460 cnmat → OpenSoundControl → OSC-route`.
- Acknowledgments use `OpenSoundControl → udpsend`; no `oscparse` or
  `oscformat` objects are required.
- The **LIVE TARGET** menu chooses which slot receives the next
  `/living/ir/candidate`.
- **AUTO C/D** is the safe default. It alternates completed live revisions
  between C and D, mutes the inactive destination before replacement, then
  crossfades only after the new buffer is ready.
- A candidate is acknowledged `ready` only after `buffer~` finishes reading it
  and its stereo channels have been installed in the convolution matrix.
- It is acknowledged `committed` only after the requested gain ramp completes.

Each candidate panel displays its current gain. These values expose both manual
X/Y interpolation and OSC-authorized crossfades.

The controller is `qmw_operator_ecology_lab_v1.js`; the patch itself is
generated deterministically by `build_qmw_operator_ecology_lab_v1.py`.
