# QMW Spat Master Control Room

Open **`QMW_SPAT_MASTER_CONTROL_ROOM.maxpat`** for normal use.

This is the canonical Max entry point for the current instrument. It combines:

- the v5.6 sonification rack and four qubit audio buses;
- Bloch-sphere and spherical-harmonic OSC control;
- four-source Spat5 binaural rendering;
- modal-spectrum and regenerative geometry-reverb control;
- a dedicated Spat output trim, meters, and `ezdac~`.

The numbered Control Room, Rack, Surface Reverb, and adapter patches are retained as
implementation history and reusable modules. They are not separate starting points.

## Signal path

`qmw_qubit_0..3` → embedded Bloch/Harmonic Spat adapter → output trim → binaural `ezdac~`

The surface reverb remains available in the main control-room area and receives the
same `/qmw/acoustics/reverb/*` and `/qmw/acoustics/modal/*` control family.

## Rebuild

Run:

```sh
python3 max/build_qmw_spat_master_control_room.py
```

The builder reads the current v5.6 control room and embeds the corrected Spat adapter,
so the master patch remains reproducible.
