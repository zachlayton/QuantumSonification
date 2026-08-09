# QMW Density-Matrix Feedback → CRAIVE Spat 128 — v9

This bundle combines the v8 sixteen-lane complex density-matrix feedback system with a new CRAIVE-aware IRCAM Spat renderer.

The signal path is:

1. a raw sixteen-channel MC resonator state enters the existing feedback engine;
2. the full complex density matrix couples all sixteen basis channels;
3. the selected raw/coupled sixteen-channel state remains unsummed;
4. MC channels 1–16 become Spat sources 1–16;
5. `spat5.wfs~` renders them to the exact CRAIVE perimeter loudspeaker coordinates;
6. the first outlet emits CRAIVE hardware channels 1–128 as one MC signal.

No equal-temperament pitch quantization, noise-source substitution, pre-spatial fold-down, duplicate OSC receiver, or autonomous source motion is introduced.

## Requirements

- Cycling '74 Max 9
- IRCAM Spat 5.3.7 or another compatible Spat 5 release containing `spat5.wfs~` and `spat5.viewer`
- A sixteen-channel MC source matching the existing QMW basis order
- For room playback, CRAIVE's configured 128-channel output device or facility hardware sink

Keep every file in this directory together, or add the directory to Max's search path.

## Start here

Open:

`qmw_density_matrix_craive_spat128_v9.maxpat`

The top-level abstraction has nine inlets:

| Inlet | Data |
|---:|---|
| 1 | Raw sixteen-channel MC resonator output |
| 2 | `Re(rho)`, 256 row-major values |
| 3 | `Im(rho)`, 256 row-major values |
| 4 | Sixteen quantum projection phases, radians |
| 5 | Sixteen feedback gains |
| 6 | Sixteen feedback delays, milliseconds |
| 7 | Feedback controls such as `mode 2`, `safe`, `clear`, or `status` |
| 8 | Spatial tuple or supported OSC spatial message |
| 9 | CRAIVE renderer controls |

It has eight outlets:

| Outlet | Data |
|---:|---|
| 1 | CRAIVE WFS feeds, 128-channel MC signal for hardware channels 1–128 |
| 2 | Two-channel MC monitor fold-down made **after** WFS |
| 3 | Selected sixteen-channel state entering Spat |
| 4 | Coupled sixteen-channel state |
| 5 | Sixteen-channel feedback return |
| 6 | `Re(rho z)`, sixteen-channel MC signal |
| 7 | `Im(rho z)`, sixteen-channel MC signal |
| 8 | Feedback and spatial diagnostics |

The feedback engine still starts safely in mode 1 with zero feedback gains. Send `mode 2` to inlet 7 when the density-coupled state should enter Spat. Retain the existing gain, delay, matrix, and safety workflow from v8.

For CRAIVE playback, connect outlet 1 to the facility's 128-channel sink. The reference CRAIVE project uses `spat5.mc.dac128~`. Outlet 2 is only a convenience monitor and is not the room render.

## Spatial messages

Inlet 8 accepts the tuple used by the earlier QMW/Qiskit bridge:

`voice azimuth elevation distance spread`

Example:

`0 -30. 12. 2.5 0.4`

The default mapping is:

- QMW voices `0...15`
- Spat sources `1...16`
- azimuth and elevation in degrees
- distance in metres
- IRCAM coordinate convention, with `+Y` as front

The example becomes:

`/source/1/aed -30. 12. 2.5`

Send `indexbase 1` to inlet 8 if the upstream system already numbers voices `1...16`.

The router also accepts:

- `/qks/spat voice azimuth elevation distance spread`
- `/qqt/spat voice azimuth elevation distance spread`
- `/qmw/spat voice azimuth elevation distance spread`
- native `/source/...` and `/listener/...` Spat messages
- `ring radius elevation` for an explicit, deterministic sixteen-source ring
- `dump`, `clear`, `distancerange min max`, and `status`

The fifth `spread` value is preserved in the diagnostics as metadata. It is not automatically mapped into `/source/N/window/size`. CRAIVE's reference WFS configuration fixes that aperture at 100, and the upstream spread scale does not define an equivalent WFS aperture. If the composition needs that coupling, send explicit native window-size messages after choosing the intended mapping.

## Existing OSC ingress

This bundle intentionally contains no `udpreceive`.

Branch the already decoded `/qks/spat`, `/qqt/spat`, or `/qmw/spat` messages from the existing system ingress into inlet 8. This avoids a second receiver competing for the same UDP port.

## Renderer controls

Inlet 9 accepts:

- `layout` — reload exact CRAIVE speaker XYZ and the official wall-direction groups;
- `defaults` — reload source/speaker counts and CRAIVE WFS defaults;
- `viewer <Spat message>` — send a message through `spat5.viewer`;
- `wfs <Spat message>` — send a message directly to `spat5.wfs~`;
- `source <voice azimuth elevation distance spread>` — send a tuple through the router;
- `status` — query the source router;
- an unmatched native Spat message — send it to the viewer.

On load, the renderer sets:

- `/speaker/number 128`
- `/source/number 16`
- the official 128 CRAIVE perimeter XYZ triplets
- the four wall orientation groups from the CRAIVE reference patch
- `/source/*/window/size 100`
- `/source/*/blend/method focus+nonfocus`

It does not place or move sources on load. The `ring 2. 0.` message visible in the renderer is manual.

## CRAIVE channel scope

The implemented room renderer covers channels 1–128, documented by CRAIVE as the perimeter WFS/VBAP system.

Channels 129–134 are six ceiling loudspeakers used for HoA with assistance from selected perimeter channels. They are not generic extra outputs for the perimeter WFS stage. Their recovered XYZ and derived AED values are included only as reference in:

`qmw_craive_ceiling6_reference_v9.json`

Channels 135–136 are the separate frontal stereo pair and are also outside this renderer.

## Included files

- `qmw_density_matrix_craive_spat128_v9.maxpat` — complete v9 wrapper
- `qmw_craive_spat128_renderer16_v9.maxpat` — standalone sixteen-source CRAIVE renderer
- `qmw_craive_source_router16_v9.js` — validated tuple/OSC to Spat router
- `qmw_craive128_layout_v9.maxpat` — deterministic layout and direction loader
- `CRAIVE128.maxpat` — unmodified CRAIVE reference geometry
- `qmw_craive_ceiling6_reference_v9.json` — ceiling coordinate reference
- all eight v8 feedback, Hilbert, matrix, JavaScript, Gen, and README dependencies
- `LICENSE_CRAIVE.txt` — MIT license for the CRAIVE reference patch

## Geometry provenance

The perimeter coordinates and wall directions come from CRAIVE-Lab's official [`CRAIVE128.maxpat`](https://github.com/craive-lab/rois-special-asset-for-spatial-audio/blob/master/patchers/CRAIVE128.maxpat).

CRAIVE's channel roles are documented in the official [auditory display system documentation](https://github.com/craive-lab/docs/blob/Development/infrastructure/auditory-display-system.md).

The room model used to verify the acoustic origin and ceiling geometry is in the [CRAIVE infrastructure repository](https://github.com/craive-lab/infrastructure).

## Validation scope

The bundle is statically validated for JSON structure, patchline endpoint integrity, unique object IDs, JavaScript syntax, required dependency presence, and exactly 128 perimeter XYZ triplets. Final audio-device and loudspeaker verification must be performed in Max with IRCAM Spat and CRAIVE's active hardware configuration.
