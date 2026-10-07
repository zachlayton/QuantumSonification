"""Run with python3 -m collider_001a; no pip install required."""

import argparse
import json
from pathlib import Path
import webbrowser

from .backend import ColliderBackend, DEFAULT_EDGES_GEV
from .io import load_dataset, save_dataset
from .report import render_report
from .synthetic import generate_synthetic


def main(argv=None):
    parser = argparse.ArgumentParser(description="CERN/QMW 001A: top-pair mass navigation")
    sub = parser.add_subparsers(dest="command", required=True)
    generate = sub.add_parser("generate", help="write a deterministic toy JSON dataset")
    demo = sub.add_parser("demo", help="generate, load, analyze and render an offline demo")
    analyze = sub.add_parser("analyze", help="analyze a normalized local JSON dataset")
    for command in (generate, demo):
        command.add_argument("--events", type=int, default=10_000)
        command.add_argument("--seed", type=int, default=1001)
    generate.add_argument("--output", type=Path, default=Path("toy_events.json"))
    for command in (demo, analyze):
        command.add_argument("--output", type=Path, default=Path("demo"))
        command.add_argument("--edges", default=",".join(map(str, DEFAULT_EDGES_GEV)),
                             help="comma-separated mass bin edges in GeV (c=1)")
        command.add_argument("--select-mass", type=float, help="initial selected mass in GeV")
        command.add_argument("--open", action="store_true", help="open the offline report")
    analyze.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            path = save_dataset(generate_synthetic(args.events, args.seed), args.output)
            print(f"Synthetic dataset: {path.resolve()}")
            return 0
        if args.command == "demo":
            dataset_path = save_dataset(generate_synthetic(args.events, args.seed),
                                        args.output / "toy_events.json")
        else:
            dataset_path = args.input
        # Do not let an output overwrite the input dataset.
        for name in ("summary.json", "index.html"):
            if (args.output / name).resolve() == dataset_path.resolve():
                raise ValueError(f"output {name} would overwrite the input dataset")
        backend = ColliderBackend(load_dataset(dataset_path),
                                  tuple(float(x.strip()) for x in args.edges.split(",")))
        if args.select_mass is not None:
            backend.select_mass(args.select_mass)
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "summary.json").write_text(
            json.dumps(backend.summary(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
        report = render_report(backend, args.output / "index.html")
        print(f"{len(backend.dataset.events):,} events; "
              f"{backend.underflow} underflow, {backend.overflow} overflow")
        print(f"Viewer: {report.resolve()}")
        if args.open:
            webbrowser.open(report.resolve().as_uri())
        return 0
    except (ValueError, OSError, OverflowError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
