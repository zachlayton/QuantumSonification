"""Command line.

  python3 -m bell_sonification_v1 demo OUTDIR [--source ideal|aer]
      renders voices (entangled then independent), agreement (entangled then
      independent) and sweep (0 -> 180 degrees) as WAV files
  python3 -m bell_sonification_v1 stream [--source ideal|aer] [--kind entangled]
      [--theta 0] [--shots 256] [--host 127.0.0.1] [--port 7400] [--rate 8]
  python3 -m bell_sonification_v1 ibm ARCHIVE_DIR [--backend NAME] [--account NAME]
      [--shots 256] [--steps 9]   runs the sweep on hardware and archives it
  python3 -m bell_sonification_v1 replay ARCHIVE.json OUTDIR
      renders archived hardware shots (sweep and agreement)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from . import render, source


def _sweep_runs(src: str, steps: int, per: int, seed: int):
    return [source.sample(src, "entangled", float(t), per, seed + i)
            for i, t in enumerate(np.linspace(0, np.pi, steps))]


def demo(out: Path, src: str, seed: int = 1) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    ent = source.sample(src, "entangled", 0.0, 48, seed)
    ind = source.sample(src, "independent", 0.0, 48, seed + 1)
    paths = [
        render.write_wav(out / "bell_voices_entangled_then_independent.wav",
                         np.vstack([render.render_voices([ent]), render.render_voices([ind])])),
        render.write_wav(out / "bell_agreement_entangled_then_independent.wav",
                         np.vstack([render.render_agreement([ent]), render.render_agreement([ind])])),
        render.write_wav(out / "bell_sweep_0_to_180.wav",
                         render.render_sweep(_sweep_runs(src, 13, 16, seed + 10))),
    ]
    return paths


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="bell_sonification_v1")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo"); d.add_argument("outdir", type=Path); d.add_argument("--source", default="ideal")
    s = sub.add_parser("stream")
    for k, v in [("--source", "ideal"), ("--kind", "entangled"), ("--host", "127.0.0.1")]:
        s.add_argument(k, default=v)
    s.add_argument("--theta", type=float, default=0.0); s.add_argument("--shots", type=int, default=256)
    s.add_argument("--port", type=int, default=7400); s.add_argument("--rate", type=float, default=8.0)
    i = sub.add_parser("ibm"); i.add_argument("archive_dir", type=Path)
    i.add_argument("--backend"); i.add_argument("--account"); i.add_argument("--shots", type=int, default=256)
    i.add_argument("--steps", type=int, default=9)
    r = sub.add_parser("replay"); r.add_argument("archive", type=Path); r.add_argument("outdir", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "demo":
        for p in demo(a.outdir, a.source):
            print(p)
    elif a.cmd == "stream":
        from .osc import stream
        stream([source.sample(a.source, a.kind, a.theta, a.shots)], a.host, a.port, a.rate)
    elif a.cmd == "ibm":
        runs = source.sample_ibm("entangled", list(np.linspace(0, np.pi, a.steps)), a.shots,
                                 a.account, a.backend, a.archive_dir)
        for run in runs:
            print(f"theta={run.theta:.3f}  E={run.correlation:+.3f}  ({run.provenance['backend']}, {run.provenance['job_id']})")
    elif a.cmd == "replay":
        runs = source.load_archive(a.archive)
        a.outdir.mkdir(parents=True, exist_ok=True)
        print(render.write_wav(a.outdir / "bell_hardware_sweep.wav", render.render_sweep(runs)))
        print(render.write_wav(a.outdir / "bell_hardware_agreement.wav", render.render_agreement(runs[:1])))


if __name__ == "__main__":
    main()
