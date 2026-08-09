# MuBu granular audio smoke test

Open `QMW_MuBu_Granular_Audio_Test_v1.maxpat` in Max 9 and click the `ezdac~` speaker.

Expected behavior:

1. `cherokee.aif` loads from Max's standard media folder.
2. The status changes to `AUDIO LOADED — MuBu should now play`.
3. `mubu.granular~` starts a stereo grain every 180 ms.
4. Both meters move and audio is heard.

The manual grain button sends a direct `bang` to `mubu.granular~`. This patch intentionally excludes the Pauli scheduler, generated atlas, MC routing, and MuBu corpus tracks.
