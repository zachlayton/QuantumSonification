"""Validate RenderCheck's four-channel float WAV using only the standard library."""
from array import array
import json
import math
from pathlib import Path
import struct
import sys


def validate(path: Path) -> dict:
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
        return values[int(start * rate) * 4 + channel:int(end * rate) * 4:4]

    def rms(samples):
        return math.sqrt(sum(v * v for v in samples) / len(samples))

    dry, ring, fuzz = (segment(start, start + 6) for start in (0.2, 10.2, 20.2))
    levels = [rms(a) for a in (dry, ring, fuzz)]
    assert min(levels) > 0.001, "silent section"
    assert rms([a - b for a, b in zip(dry, ring)]) > 0.001, "ring bypassed"
    assert rms([a - b for a, b in zip(dry, fuzz)]) > 0.001, "fuzz bypassed"
    send_error = max(abs(values[i + 2] - values[i] * 0.4)
                     for i in range(len(values)) if i % 4 < 2)
    assert send_error < 1e-7, "send differs from post-FX field"
    for start, end in ((30.5, 30.9), (31.5, 31.7)):
        for channel in range(4):
            assert max(map(abs, segment(start, end, channel))) < 1e-7, "mute leaked"
    return {"sample_rate": rate, "channels": channels, "peak": peak,
            "dry_ring_fuzz_left_rms": levels, "send_max_error": send_error,
            "sound_off_and_zero_gain_silent": True}


if __name__ == "__main__":
    print(json.dumps(validate(Path(sys.argv[1])), indent=2))
