# QMW Bloch Harmonics — Four-Qubit Spat v6 Portable Package

This folder contains every project-specific asset needed by the v6 Max demonstration. The bundled loader resolves the jweb HTML file from the main patch's absolute location, so the visualization does not depend on the original computer's path.

## Install on another computer

1. Install Max 8 or Max 9 and these Max packages:
   - Spat5
   - CNMAT Externals
   - jasch objects
2. Copy this entire folder into `Documents/Max 8/Packages/` (or the corresponding `Max 9/Packages/` folder).
3. Restart Max so it indexes the package.
4. Open `patchers/QMW_Bloch_Harmonics_Four_Qubit_Spat_v6.maxpat`.
5. Run the QuantumSonification conductor and make sure no second Max patch is also listening on UDP 7400.

## Bundled contents

- Main presentation patch
- Four-qubit jweb viewer and its portable loader
- Four independent Gen voices and Spat-control abstractions
- Bundled local-voice and global-field `.gendsp` sources loaded by standard `gen~` objects; the Max-level `gen.codebox~` object is not required
- Four-source Spat5 renderer abstraction
- Independent 180 ms Bloch-vector slews for all four sources before AED, aperture and yaw mapping
- Presentation-mode `Spat rate (Hz)` control, adjustable from 5–60 Hz and defaulting to 50 Hz
- Read-only live OSC monitors for normalized purity, entropy, and coherence; legacy manual overrides removed
- Live per-qubit Z-basis marginals plus all sixteen four-qubit computational-basis probabilities from `/qmw/density/populations`
- Dual convolution-IR abstraction
- Universal Intel/Apple-Silicon `multiconvolve~` external from HIRT 2.1.1, with its redistribution license
- Tanglecube and Heart stereo impulse responses

The Python density engine is not bundled because it belongs to the QuantumSonification repository/environment. Spat5 and the remaining external Max packages are machine-specific dependencies and must be installed through Max's Package Manager or their normal installers.

If `multiconvolve~` is still red after installation, confirm that the entire package—not only the `patchers` folder—was copied, restart Max, and choose **File > Show File Browser** to let Max finish indexing the package.
