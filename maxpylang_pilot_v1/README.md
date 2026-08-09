# QMW MaxPyLang pilot v1

This directory is a contained evaluation of `maxpylang==0.1.1`. It generates a
four-mode, dependency-light Max 9 oscillator bank through MaxPyLang's object and
inlet/outlet API.

## Rebuild

```sh
python3 -m venv .venv
.venv/bin/python -m pip install maxpylang==0.1.1
.venv/bin/python maxpylang_pilot_v1/build_qmw_maxpylang_modal_bank_v1.py
.venv/bin/python -m unittest maxpylang_pilot_v1.test_maxpylang_pilot_v1
```

Open `QMW_MaxPyLang_Modal_Bank_v1.maxpat` in Max 9 and click `ezdac~` to start
DSP. The four fixed modes are attenuated before summing, with a meter and scope
for visual confirmation.

## Pilot findings

MaxPyLang substantially clarifies repetitive object construction and wiring.
The connection expressions name actual Python objects and their inlets/outlets,
so there are no manually maintained Max object IDs in the source.

Version 0.1.1 still needs a compatibility boundary:

- Its bundled empty template identifies Max 8.1; this builder updates the saved
  document to Max 9 metadata.
- It emits `"midpoints": [null]` for straight patch cords; this builder removes
  those placeholders.
- It serializes comment content with a leading `comment ` token; this builder
  strips it.
- Its existing-patch importer fails on valid UI/comment boxes that omit explicit
  `text`, `numinlets`, or `numoutlets` fields. It therefore should not yet be used
  to round-trip production QMW patches.
- Max for Live objects and third-party externals are often unknown to its object
  catalog. Production adoption would require explicit QMW object specifications
  or upstream MaxPyLang improvements.

The safe near-term use is generation of new, dependency-light, regular graphs.
Direct Max JSON remains the appropriate fallback for elaborate presentation
layouts, embedded patchers, and external-heavy instruments.
