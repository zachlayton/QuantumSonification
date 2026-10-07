#!/usr/bin/env python3
"""Generate a mono shoebox room IR without a fixed reflection-order cutoff.

Install: python -m pip install numpy scipy pyroomacoustics matplotlib
Run:     python room_ir_generator.py --room 20 30 8 --plot

By default the wall ENERGY absorption stays at 0.2 as the room changes.
Use --rt60 to instead choose an approximate decay time and change absorption.
Source and microphone coordinates are in meters unless fractions are supplied.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pyroomacoustics as pra
from scipy.io import wavfile


def arguments():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--room", nargs=3, type=float, default=[7, 9, 3.5],
                   metavar=("X", "Y", "Z"), help="Room dimensions in meters")
    source = p.add_mutually_exclusive_group()
    source.add_argument("--source", nargs=3, type=float, help="Source coordinates in meters")
    source.add_argument("--source-fraction", nargs=3, type=float,
                        help="Source coordinates as fractions of room dimensions (0 to 1)")
    mic = p.add_mutually_exclusive_group()
    mic.add_argument("--mic", nargs=3, type=float, help="Microphone coordinates in meters")
    mic.add_argument("--mic-fraction", nargs=3, type=float,
                     help="Microphone coordinates as fractions of room dimensions (0 to 1)")
    decay = p.add_mutually_exclusive_group()
    decay.add_argument("--absorption", type=float, default=0.2,
                       help="Uniform wall energy absorption; default 0.2")
    decay.add_argument("--rt60", type=float,
                       help="Approximate target RT60 in seconds; overrides fixed absorption")
    p.add_argument("--fs", type=int, default=44100, help="Sample rate; default 44100 Hz")
    p.add_argument("--seed", type=int, default=42, help="Randomized ISM seed; default 42")
    p.add_argument("--exact-ism", action="store_true",
                   help="Disable small image displacements for exact specular geometry")
    p.add_argument("--no-air", action="store_true", help="Disable frequency-dependent air absorption")
    p.add_argument("--no-normalize", action="store_true", help="Preserve simulated amplitudes")
    p.add_argument("--max-images", type=int, default=2_000_000,
                   help="Safety limit on image sources; never silently reduces reflection order")
    p.add_argument("--output", type=Path, default=Path("3d_room_impulse_response.wav"))
    p.add_argument("--plot", action="store_true", help="Also save a waveform and decay plot")
    p.add_argument("--force", action="store_true", help="Allow overwriting existing outputs")
    return p, p.parse_args()


def position(meters, fraction, default, dims, name):
    xyz = np.asarray(fraction, dtype=float) * dims if fraction is not None else np.asarray(
        default if meters is None else meters, dtype=float)
    if not np.all(np.isfinite(xyz)) or np.any(xyz <= 0) or np.any(xyz >= dims):
        raise ValueError(f"{name} must be strictly inside the room; got {xyz.tolist()}")
    return xyz


def decay_diagnostics(rir, fs):
    """Broadband Schroeder energy decay; T30 extrapolation is only a diagnostic."""
    energy = np.cumsum(np.square(rir)[::-1], dtype=np.float64)[::-1]
    edc_db = 10 * np.log10(np.maximum(energy / energy[0], np.finfo(float).tiny))
    time = np.arange(len(rir)) / fs
    fit = (edc_db <= -5) & (edc_db >= -35)
    stats = {"t30_extrapolated_rt60_s": None, "t30_fit_r_squared": None}
    if np.count_nonzero(fit) >= 20 and np.ptp(time[fit]) > 0:
        slope, intercept = np.polyfit(time[fit], edc_db[fit], 1)
        residual = np.sum((edc_db[fit] - (slope * time[fit] + intercept)) ** 2)
        total = np.sum((edc_db[fit] - np.mean(edc_db[fit])) ** 2)
        if slope < 0 and total > 0:
            stats = {"t30_extrapolated_rt60_s": float(-60 / slope),
                     "t30_fit_r_squared": float(1 - residual / total)}
    tail_samples = min(len(rir), max(1, round(0.020 * fs)))
    stats["last_20ms_energy_fraction_db"] = float(10 * np.log10(
        max(float(np.sum(rir[-tail_samples:] ** 2) / energy[0]), np.finfo(float).tiny)))
    return time, edc_db, stats


def main():
    parser, args = arguments()
    dims = np.asarray(args.room, dtype=float)
    try:
        if not np.all(np.isfinite(dims)) or np.any(dims <= 0):
            raise ValueError("Room dimensions must be finite and positive.")
        if args.fs < 8000:
            raise ValueError("Use a sample rate of at least 8000 Hz.")
        if args.seed < 0 or args.seed >= 2**32:
            raise ValueError("Seed must be between 0 and 2**32 - 1.")
        if args.max_images < 1:
            raise ValueError("--max-images must be positive.")
        src = position(args.source, args.source_fraction, [2, 3.5, 1.8], dims, "Source")
        mic = position(args.mic, args.mic_fraction, [4.5, 6, 1.5], dims, "Microphone")
        distance = float(np.linalg.norm(mic - src))
        if distance < 0.01:
            raise ValueError("Separate source and microphone by at least 1 cm.")

        # Use the same sound speed for Sabine estimation and the room simulation.
        c = float(pra.constants.get("c"))
        volume = float(np.prod(dims))
        surface = float(2 * (dims[0]*dims[1] + dims[0]*dims[2] + dims[1]*dims[2]))
        sabine_factor = 24 * np.log(10) / c
        if args.rt60 is not None:
            if not np.isfinite(args.rt60) or args.rt60 <= 0:
                raise ValueError("RT60 must be finite and positive.")
            design_rt60 = args.rt60
            absorption, max_order = pra.inverse_sabine(design_rt60, dims, c=c)
            mode = "target_rt60"
        else:
            absorption = args.absorption
            if not np.isfinite(absorption) or not 0 < absorption < 1:
                raise ValueError("Absorption must be strictly between 0 and 1.")
            # Preserve the material, allowing a larger room to have a longer decay.
            design_rt60 = float(sabine_factor * volume / (surface * absorption))
            _, max_order = pra.inverse_sabine(design_rt60, dims, c=c)
            mode = "fixed_absorption"

        # Number of integer image-room coordinates with |x|+|y|+|z| <= max_order.
        n = int(max_order)
        images = (4*n**3 + 6*n**2 + 8*n + 3) // 3
        if images > args.max_images:
            raise ValueError(f"Order {n} needs about {images:,} image sources. "
                             "Increase absorption, shorten --rt60, or explicitly raise --max-images.")
        if args.output.suffix.lower() != ".wav":
            raise ValueError("Output filename must end in .wav.")
        metadata_path = args.output.with_suffix(".json")
        plot_path = args.output.with_suffix(".png")
        outputs = [args.output, metadata_path] + ([plot_path] if args.plot else [])
        for path in outputs:
            if path.exists() and not args.force:
                raise ValueError(f"Output already exists: {path}. Choose another name or use --force.")
        if args.plot:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
    except (ValueError, ImportError) as error:
        parser.error(str(error))

    print(f"Room: {dims.tolist()} m; wall energy absorption: {absorption:.4f}")
    print(f"Sabine design RT60 (approximate, excludes air): {design_rt60:.3f} s")
    print(f"Reflection order: {n}; image sources: approximately {images:,}", flush=True)

    # Seed both native and NumPy randomness on current pyroomacoustics releases.
    pra.random.seed(args.seed)
    room = pra.ShoeBox(dims, fs=args.fs, materials=pra.Material(absorption),
                       max_order=n, air_absorption=not args.no_air,
                       use_rand_ism=not args.exact_ism, max_rand_disp=0.05)
    room.c = c
    room.add_source(src)
    room.add_microphone_array(mic[:, None])
    room.compute_rir()
    rir = np.asarray(room.rir[0][0], dtype=np.float64)
    if rir.size == 0 or not np.all(np.isfinite(rir)):
        raise RuntimeError("Simulation produced an empty or non-finite impulse response.")
    peak = float(np.max(np.abs(rir)))
    if peak == 0:
        raise RuntimeError("Simulation produced a silent impulse response.")

    time, edc_db, stats = decay_diagnostics(rir, args.fs)
    # Keep propagation delay and the entire calculated tail. No hard crop or fade.
    gain = float(10 ** (-1 / 20) / peak) if not args.no_normalize else 1.0
    exported = (rir * gain).astype(np.float32)
    if not np.all(np.isfinite(exported)):
        raise RuntimeError("Output amplitudes exceed the float32 range.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(args.output), args.fs, exported)

    metadata = {"pyroomacoustics_version": pra.__version__, "sample_rate_hz": args.fs,
                "room_dimensions_m": dims.tolist(), "source_position_m": src.tolist(),
                "microphone_position_m": mic.tolist(), "design_mode": mode,
                "wall_energy_absorption": float(absorption), "sabine_design_rt60_s": design_rt60,
                "max_order": n, "image_source_count_estimate": images,
                "air_absorption": not args.no_air, "randomized_ism": not args.exact_ism,
                "max_random_displacement_m": 0.0 if args.exact_ism else 0.05, "seed": args.seed,
                "speed_of_sound_m_s": c, "source_receiver_distance_m": distance,
                "geometric_direct_arrival_s": distance/c,
                "note": "RIR includes simulator filter delay in addition to geometric propagation.",
                "samples": len(rir), "duration_s": len(rir)/args.fs,
                "normalization_gain": gain, "raw_peak": peak,
                "export_peak": float(np.max(np.abs(exported))), **stats}
    metadata_path.write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n")

    if args.plot:
        fig, axes = plt.subplots(2, 1, figsize=(9, 6), constrained_layout=True)
        axes[0].plot(time, exported, linewidth=0.6)
        axes[0].set(xlabel="Time (seconds)", ylabel="Amplitude", title="Exported mono impulse response")
        axes[1].plot(time, edc_db, linewidth=1)
        axes[1].axhline(-5, color="gray", linestyle="--", linewidth=0.6)
        axes[1].axhline(-35, color="gray", linestyle="--", linewidth=0.6)
        axes[1].set(xlabel="Time (seconds)", ylabel="Remaining energy (dB)", ylim=(-80, 1),
                    title="Schroeder decay; dashed lines bound the T30 fit")
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)

    print(f"Saved: {args.output} ({len(rir)/args.fs:.3f} seconds, mono float32 WAV)")
    print(f"Geometric direct arrival: {1000*distance/c:.2f} ms, plus simulator filter delay")
    measured = stats["t30_extrapolated_rt60_s"]
    if measured is not None:
        print(f"Broadband T30-extrapolated RT60: {measured:.3f} s "
              f"(fit R-squared: {stats['t30_fit_r_squared']:.3f}; diagnostic only)")
        if stats["t30_fit_r_squared"] < 0.9:
            print("Warning: decay is irregular; a single RT60 number is a poor description.")
    if stats["last_20ms_energy_fraction_db"] > -45:
        print("Warning: appreciable energy remains near the endpoint; inspect the decay plot.")
    print(f"Settings and diagnostics: {metadata_path}")


if __name__ == "__main__":
    main()
