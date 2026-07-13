QMW Density Field Quantum Resonator 16 MC v1
==================================================

Purpose
-------
Preserve the sixteen density-field resonances as sixteen independent MC audio
streams for Spat or other multichannel spatial rendering.

Recommended Max structure
-------------------------

    55.
    |
    sig~
    |
    mc.gen~ @chans 16
    |
    mc.live.gain~ / mc.meter~ / Spat input

Load the supplied GenExpr code into the mc.gen~ patcher's codebox.

Channel mapping
---------------

    MC 1  = basis 0  = |0000>
    MC 2  = basis 1  = |0001>
    ...
    MC 16 = basis 15 = |1111>

Control messages
----------------

Send these named messages to mc.gen~:

    m0 ... m15      magnitude / excitation
    ph0 ... ph15    phase
    s0 ... s15      speed / decay time
    h0 ... h15      frequency ratios

Global messages:

    purity
    entropy
    coherence
    amp
    default_freq
    attack_ms
    slow_decay_ms
    fast_decay_ms
    phase_smooth_ms
    magnitude_smooth_ms
    harmonic_smooth_ms
    brightness
    output_ceiling

Monitoring
----------

To hear a stereo or mono monitor mix without changing the sixteen source
streams:

    mc.gen~
    |
    mc.mixdown~ 2 @autogain 1
    |
    gain~
    |
    ezdac~

Keep the unsummed mc.gen~ outlet connected separately to Spat.

First test
----------

1. Send `m0 1`.
2. Set the input frequency to 55 Hz.
3. Verify that only MC channel 1 carries audio.
4. Send `m0 0, m1 1`.
5. Verify that channel 2 carries the second partial at 110 Hz.

If all sound appears on channel 1, inspect the `mc_channel` numbering in your
Max version. The code assumes channel numbering starts at 1.
