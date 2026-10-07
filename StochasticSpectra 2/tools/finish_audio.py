from pathlib import Path
import numpy as np
from scipy.io import wavfile
root = Path(__file__).resolve().parents[1]
audio = root/'audio'
raw = audio/'cycle_raw.f64'
if raw.exists():
    cycle = np.fromfile(raw, dtype=np.float64)
    assert cycle.size == 8192 and np.isfinite(cycle).all()
    wavfile.write(audio/'stochastic_cycle_8192_float.wav', 48000, cycle.astype(np.float32))
    raw.unlink()
for name in ('stochastic_spectra_demo.wav', 'matched_wavetable_L_modal_R.wav'):
    sr, data = wavfile.read(audio/name)
    assert sr == 48000 and data.dtype == np.int32
    x = data.astype(np.float64)/2147483648
    assert np.isfinite(x).all() and np.max(np.abs(x)) < 1
    print(name, 'frames=',len(x), 'peak=',np.max(np.abs(x)), 'RMS=',np.sqrt(np.mean(x*x)))
    if x.ndim==2:
        residual=np.sqrt(np.mean((x[:,0]-x[:,1])**2))
        print('Stereo residual RMS:',residual)
