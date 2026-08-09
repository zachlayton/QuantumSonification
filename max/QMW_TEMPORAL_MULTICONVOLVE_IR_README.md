# QMW temporal multiconvolve IR abstraction

Instantiate `qmw_temporal_multiconvolve_ir~` in a Max patch.

- inlet 1: mono excitation signal (`click~` is ideal)
- inlet 2: equal-power morph, `0` = Tanglecube and `1` = Heart
- inlet 3: wet output gain, `0..1` (default `0.35`)
- outlets 1/2: wet stereo convolution

Minimal patch:

```text
[button]
|
[click~]
|
[*~ 0.05]
|
[qmw_temporal_multiconvolve_ir~]
|                              |
[ezdac~ left]                  [ezdac~ right]
```

The abstraction owns unique `#0` buffers and loads two repository IR assets,
then installs their left/right channels into `multiconvolve~ 1 4 medium`.
It requires the HISSTools Impulse Response Toolbox already used elsewhere in
this workspace. The outputs are wet-only; mix the original click separately
if a dry component is wanted.
