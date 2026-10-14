#!/usr/bin/env python3
"""Add sample-rate-stable onset noise excitation to a Platonic reverb fork."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil


TAG = "noise_excitation_v1"
GENEXPR = "qmw_platonic_geometry_reverb_v1.genexpr"
BUILDER = "build_qmw_platonic_geometry_reverb_v1.py"
CONTROLLER = "qmw_platonic_geometry_controller_v1.js"
README = "qmw_platonic_geometry_reverb_v1_README.txt"


PARAM_ANCHOR = """Param input_gain(0.25);
Param output_gain(0.40);"""
PARAM_REPLACEMENT = """Param input_gain(0.25);

// Onset-sensitive broadband excitation.
Param noise_amount(0.22);
Param noise_decay_ms(22);
Param onset_threshold(0.012);
Param onset_sensitivity(10);
Param noise_color(0.72);
Param noise_floor(0);

Param output_gain(0.40);"""

GEN_HISTORY_ANCHOR = "History apz4(0);"
GEN_HISTORY_REPLACEMENT = """History apz4(0);
History onset_fast(0);
History onset_slow(0);
History noise_env(0);
History noise_lp(0);"""

BUILDER_HISTORY_ANCHOR = (
    "'History apz1(0);', 'History apz2(0);', "
    "'History apz3(0);', 'History apz4(0);',"
)
BUILDER_HISTORY_REPLACEMENT = """'History apz1(0);', 'History apz2(0);', 'History apz3(0);', 'History apz4(0);',
        'History onset_fast(0);', 'History onset_slow(0);',
        'History noise_env(0);', 'History noise_lp(0);',"""

INPUT_ANCHOR = "x = in1 * input_gain;"
INPUT_REPLACEMENT = """input_signal = in1 * input_gain;
input_abs = abs(input_signal);

// A fast-minus-slow envelope detector avoids per-sample derivative scaling,
// so the onset threshold remains comparable across sample rates.
onset_fast_samples = max(0.0015 * sr, 1);
onset_slow_samples = max(0.035 * sr, 1);
onset_fast_coeff = exp(-1 / onset_fast_samples);
onset_slow_coeff = exp(-1 / onset_slow_samples);
onset_fast = input_abs + onset_fast_coeff * (onset_fast - input_abs);
onset_slow = input_abs + onset_slow_coeff * (onset_slow - input_abs);
onset_strength = clamp(
    (onset_fast - onset_slow - max(onset_threshold, 0))
    * max(onset_sensitivity, 0),
    0,
    1
);

noise_decay_samples = max(noise_decay_ms, 0.1) * 0.001 * sr;
noise_decay_coeff = exp(-1 / max(noise_decay_samples, 1));
noise_env = max(noise_env * noise_decay_coeff, onset_strength);

raw_noise = noise();
noise_color_norm = clamp(noise_color, 0, 1);
noise_cut_hz = min(500 + 11500 * noise_color_norm, 0.45 * sr);
noise_cut_coeff = 1 - exp((-pi2 * noise_cut_hz) / sr);
noise_lp = noise_lp + noise_cut_coeff * (raw_noise - noise_lp);
colored_noise = mix(noise_lp, raw_noise, noise_color_norm);

burst_excitation =
    colored_noise
    * noise_env
    * clamp(noise_amount, 0, 1);
continuous_excitation =
    colored_noise
    * clamp(noise_floor, 0, 0.25);
excitation = input_signal + burst_excitation + continuous_excitation;

x = excitation;"""

OUT_ANCHOR = "OUT = Path('/tmp/platonic_out')"
OUT_REPLACEMENT = "OUT = Path(__file__).resolve().parent"

CONTROLLER_COMMENT_ANCHOR = "//   morph_slew_ms 750"
CONTROLLER_COMMENT_REPLACEMENT = """//   morph_slew_ms 750
//   noise_amount 0.22
//   noise_decay_ms 22
//   onset_threshold 0.012
//   onset_sensitivity 10
//   noise_color 0.72
//   noise_floor 0"""

CONTROLLER_FUNCTION_ANCHOR = (
    'function freeze(value) { forwardParameter("freeze", value); }'
)
CONTROLLER_FUNCTION_REPLACEMENT = """function freeze(value) { forwardParameter("freeze", value); }
function input_gain(value) { forwardParameter("input_gain", value); }
function output_gain(value) { forwardParameter("output_gain", value); }
function noise_amount(value) { forwardParameter("noise_amount", value); }
function noise_decay_ms(value) { forwardParameter("noise_decay_ms", value); }
function onset_threshold(value) { forwardParameter("onset_threshold", value); }
function onset_sensitivity(value) { forwardParameter("onset_sensitivity", value); }
function noise_color(value) { forwardParameter("noise_color", value); }
function noise_floor(value) { forwardParameter("noise_floor", value); }"""

README_CORE_ANCHOR = """topology 0..1
    0 = active-node Householder diffusion.
    1 = strict interpolated Platonic adjacency."""
README_CORE_REPLACEMENT = """topology 0..1
    0 = active-node Householder diffusion.
    1 = strict interpolated Platonic adjacency.

ONSET EXCITATION
----------------
noise_amount 0..1
    Gain of the onset-triggered broadband burst.

noise_decay_ms 0.1..200
    Exponential duration of each excitation burst.

onset_threshold 0..0.2
    Fast-minus-slow envelope difference required to excite noise.

onset_sensitivity 0..40
    Scales transient strength above the threshold.

noise_color 0..1
    0 = darker low-passed burst; 1 = full-band white burst.

noise_floor 0..0.25
    Optional continuous excitation. Leave at 0 for onset-only operation."""

README_START_ANCHOR = """input_gain 0.20
output_gain 0.35"""
README_START_REPLACEMENT = """input_gain 0.20
noise_amount 0.22
noise_decay_ms 22
onset_threshold 0.012
onset_sensitivity 10
noise_color 0.72
noise_floor 0
output_gain 0.35"""

README_TEST_ANCHOR = """D. Duality
   between cube octahedron, then move morph slowly from 0 to 1.
   Repeat with dodecahedron and icosahedron."""
README_TEST_REPLACEMENT = """D. Duality
   between cube octahedron, then move morph slowly from 0 to 1.
   Repeat with dodecahedron and icosahedron.

E. Onset excitation
   noise_amount 0.22; noise_decay_ms 22; noise_color 0.72
   onset_threshold 0.012; onset_sensitivity 10; noise_floor 0"""


@dataclass(frozen=True)
class Replacement:
    old: str
    new: str
    label: str


def replace_once(text: str, replacement: Replacement) -> tuple[str, bool]:
    # Several replacements deliberately retain their anchor as a prefix.
    # Check for the complete replacement first so repeat runs stay idempotent.
    if replacement.new in text:
        return text, False
    count = text.count(replacement.old)
    if count == 0:
        raise RuntimeError(f"Could not find patch anchor: {replacement.label}")
    if count != 1:
        raise RuntimeError(
            f"Expected one anchor for {replacement.label}, found {count}"
        )
    return text.replace(replacement.old, replacement.new, 1), True


def replacement_plan() -> dict[str, tuple[Replacement, ...]]:
    params = Replacement(PARAM_ANCHOR, PARAM_REPLACEMENT, "parameters")
    input_block = Replacement(INPUT_ANCHOR, INPUT_REPLACEMENT, "input block")
    comment = Replacement(
        CONTROLLER_COMMENT_ANCHOR,
        CONTROLLER_COMMENT_REPLACEMENT,
        "controller documentation",
    )
    functions = Replacement(
        CONTROLLER_FUNCTION_ANCHOR,
        CONTROLLER_FUNCTION_REPLACEMENT,
        "controller forwarding",
    )
    readme_controls = Replacement(
        README_CORE_ANCHOR, README_CORE_REPLACEMENT, "README controls"
    )
    readme_defaults = Replacement(
        README_START_ANCHOR, README_START_REPLACEMENT, "README defaults"
    )
    readme_test = Replacement(
        README_TEST_ANCHOR, README_TEST_REPLACEMENT, "README test"
    )
    return {
        BUILDER: (
            Replacement(OUT_ANCHOR, OUT_REPLACEMENT, "builder output"),
            params,
            Replacement(
                BUILDER_HISTORY_ANCHOR,
                BUILDER_HISTORY_REPLACEMENT,
                "builder histories",
            ),
            input_block,
            comment,
            functions,
            readme_controls,
            readme_defaults,
            readme_test,
        ),
        GENEXPR: (
            params,
            Replacement(
                GEN_HISTORY_ANCHOR,
                GEN_HISTORY_REPLACEMENT,
                "GenExpr histories",
            ),
            input_block,
        ),
        CONTROLLER: (comment, functions),
        README: (readme_controls, readme_defaults, readme_test),
    }


def preflight(target: Path) -> dict[Path, tuple[str, bool]]:
    planned: dict[Path, tuple[str, bool]] = {}
    for name, replacements in replacement_plan().items():
        path = target / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing required file: {path}")
        text = path.read_text(encoding="utf-8")
        changed = False
        for replacement in replacements:
            text, applied = replace_once(text, replacement)
            changed = changed or applied
        planned[path] = (text, changed)
    return planned


def apply_plan(
    planned: dict[Path, tuple[str, bool]], *, dry_run: bool
) -> None:
    changed_paths = [path for path, (_, changed) in planned.items() if changed]
    for path in planned:
        status = "would update" if path in changed_paths else "already updated"
        print(f"{status}: {path}")
    if dry_run:
        return

    for path in changed_paths:
        backup = path.with_name(path.name + f".pre_{TAG}")
        if not backup.exists():
            shutil.copy2(path, backup)
            print(f"backup: {backup}")
    for path in changed_paths:
        text = planned[path][0]
        temporary = path.with_name(path.name + f".{TAG}.tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
        print(f"updated: {path}")


def validate(target: Path) -> None:
    gen = (target / GENEXPR).read_text(encoding="utf-8")
    controller = (target / CONTROLLER).read_text(encoding="utf-8")
    builder = (target / BUILDER).read_text(encoding="utf-8")
    checks = {
        "20 delay declarations": gen.count("Delay dl") == 20,
        "20 delay writes": gen.count(".write(") == 20,
        "balanced GenExpr braces": gen.count("{") == gen.count("}"),
        "balanced controller braces": controller.count("{")
        == controller.count("}"),
        "noise amount parameter": "Param noise_amount(0.22);" in gen,
        "sample-rate-stable onset detector": "onset_fast - onset_slow" in gen,
        "pre-diffusion injection": "x = excitation;" in gen,
        "in-place generator output": OUT_REPLACEMENT in builder,
        "generator persistence": "Param noise_decay_ms(22);" in builder,
        "controller forwarding": "function noise_amount(value)" in controller,
    }
    failed = [name for name, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"{'PASS' if ok else 'FAIL'}: {name}")
    if failed:
        raise RuntimeError("Failed checks: " + ", ".join(failed))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        type=Path,
        help="Forked Platonic bundle directory to update explicitly.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preflight every patch anchor without writing files.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        raise NotADirectoryError(f"Target is not a directory: {target}")
    planned = preflight(target)
    apply_plan(planned, dry_run=args.dry_run)
    if not args.dry_run:
        validate(target)
        print(f"Noise excitation update complete: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
