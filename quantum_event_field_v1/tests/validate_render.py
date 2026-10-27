"""Validate RenderCheck's four-channel float WAV using only the standard library."""
from array import array
import json
import math
from pathlib import Path
import struct
import sys


def validate(path: Path, observables: bool = False) -> dict:
    raw = path.read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WAVE"
    offset, audio, fmt = 12, None, None
    while offset + 8 <= len(raw):
        kind, size = struct.unpack_from("<4sI", raw, offset)
        content = raw[offset + 8:offset + 8 + size]
        if kind == b"fmt ":
            fmt = struct.unpack_from("<HHIIHH", content)
        elif kind == b"data":
            audio = content
        offset += 8 + size + (size % 2)
    assert fmt is not None and audio is not None
    encoding, channels, rate, _, _, bits = fmt
    assert (encoding, channels, rate, bits) == (3, 4, 48000, 32), fmt
    values = array("f")
    values.frombytes(audio)
    if sys.byteorder != "little":
        values.byteswap()
    assert all(math.isfinite(v) for v in values), "nonfinite audio"
    peak = max(map(abs, values))
    assert 0.001 < peak < 0.0641, peak

    def segment(start, end, channel=0):
        return values[round(start * rate) * 4 + channel:round(end * rate) * 4:4]

    def rms(samples):
        return math.sqrt(sum(v * v for v in samples) / len(samples))

    starts = (0.2, 10.2, 20.2, 30.2, 40.2) if observables else (0.2, 10.2, 20.2)
    sections = [segment(start, start + 6) for start in starts]
    dry = sections[0]
    levels = [rms(a) for a in sections]
    assert min(levels) > 0.001, "silent section"
    differences = [rms([a - b for a, b in zip(dry, section)]) for section in sections[1:]]
    assert min(differences) > 0.0001, "inaudible/bypassed mapping or effect"
    restore_error = None
    if observables:
        restore_error = max(abs(a - b) for channel in (0, 1)
                            for a, b in zip(segment(5, 6, channel), segment(45, 46, channel)))
        assert restore_error < 1e-6, "live zero-depth bypass differs from baseline"
    send_error = max(abs(values[i + 2] - values[i] * 0.4)
                     for i in range(len(values)) if i % 4 < 2)
    assert send_error < 1e-7, "send differs from post-FX field"
    end_time = 50 if observables else 30
    for start, end in ((end_time + 0.5, end_time + 0.9), (end_time + 1.5, end_time + 1.7)):
        for channel in range(4):
            assert max(map(abs, segment(start, end, channel))) < 1e-7, "mute leaked"
    return {"sample_rate": rate, "channels": channels, "peak": peak,
            "sections": ["baseline", "brightness", "phase", "Dirac pan", "combined then bypass"] if observables else ["dry", "ring", "fuzz"],
            "left_rms": levels, "difference_from_baseline_rms": differences,
            "live_bypass_max_error": restore_error, "send_max_error": send_error,
            "sound_off_and_zero_gain_silent": True}


if __name__ == "__main__":
    print(json.dumps(validate(Path(sys.argv[1]), "--observables" in sys.argv[2:]), indent=2))
