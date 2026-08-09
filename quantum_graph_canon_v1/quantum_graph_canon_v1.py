"""Command-line score, audio, and manifest generator for Quantum Graph Canon."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
from typing import Sequence

from procedural_notation_v1 import write_musicxml
from quantum_graph_canon_v1.core import (
    QuantumGraphCanonConfig,
    build_default_experiment,
    build_quantum_graph_canon_score,
    experiment_manifest,
)
from quantum_graph_canon_v1.qnn import (
    QuantumGraphQNNConfig,
    QuantumGraphQNNExperiment,
    build_qnn_conditioned_experiment,
    build_qnn_conditioned_score,
    qnn_experiment_manifest,
)
from quantum_graph_canon_v1.wavetable_audio import (
    ArticulatedDensityWavetableConfig,
    DensityWavetableRenderConfig,
    articulated_density_wavetable_manifest,
    density_wavetable_manifest,
    graph_qnn_voice_offsets,
    render_articulated_density_wavetable_bank,
    render_density_wavetable_bank,
    write_density_wavetable_wav,
)


DEFAULT_OUTPUT_DIRECTORY = Path(__file__).parent / "output"


def generate_experiment(
    config: QuantumGraphCanonConfig,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
) -> tuple[Path, Path]:
    """Write one MusicXML score and its JSON research manifest."""
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    mode = "entangled" if config.entangled else "local_control"
    experiment = build_default_experiment(config)
    score_path = output / f"quartic_torus_quantum_graph_canon_14_{mode}.musicxml"
    manifest_path = output / f"quartic_torus_quantum_graph_canon_14_{mode}.json"
    write_musicxml(build_quantum_graph_canon_score(experiment), score_path)
    manifest_path.write_text(
        json.dumps(experiment_manifest(experiment), indent=2) + "\n",
        encoding="utf-8",
    )
    return score_path, manifest_path


def generate_qnn_experiment(
    canon_config: QuantumGraphCanonConfig,
    qnn_config: QuantumGraphQNNConfig,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
    weights: Sequence[float] | None = None,
    weight_provenance: str | None = None,
) -> tuple[Path, Path]:
    """Write one QNN-conditioned MusicXML score and research manifest."""
    experiment = build_qnn_conditioned_experiment(
        canon_config=canon_config,
        qnn_config=qnn_config,
        weights=weights,
        weight_provenance=weight_provenance,
    )
    return _write_qnn_score_experiment(experiment, output_directory)


def generate_qnn_wavetable_experiment(
    canon_config: QuantumGraphCanonConfig,
    qnn_config: QuantumGraphQNNConfig,
    audio_config: DensityWavetableRenderConfig,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
    weights: Sequence[float] | None = None,
    weight_provenance: str | None = None,
) -> tuple[Path, Path]:
    """Write direct density-derived WAV audio and its research manifest."""
    experiment = build_qnn_conditioned_experiment(
        canon_config=canon_config,
        qnn_config=qnn_config,
        weights=weights,
        weight_provenance=weight_provenance,
    )
    return _write_qnn_wavetable_experiment(
        experiment,
        audio_config,
        output_directory,
    )


def generate_qnn_articulated_wavetable_experiment(
    canon_config: QuantumGraphCanonConfig,
    qnn_config: QuantumGraphQNNConfig,
    audio_config: ArticulatedDensityWavetableConfig,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
    weights: Sequence[float] | None = None,
    weight_provenance: str | None = None,
) -> tuple[Path, Path]:
    """Write an articulated density-derived WAV and its research manifest."""
    experiment = build_qnn_conditioned_experiment(
        canon_config=canon_config,
        qnn_config=qnn_config,
        weights=weights,
        weight_provenance=weight_provenance,
    )
    return _write_qnn_articulated_wavetable_experiment(
        experiment,
        audio_config,
        output_directory,
    )


def _write_qnn_score_experiment(
    experiment: QuantumGraphQNNExperiment,
    output_directory: str | Path,
) -> tuple[Path, Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    stem = f"quartic_torus_quantum_graph_canon_15_qnn_{_qnn_weight_mode(experiment)}"
    score_path = output / f"{stem}.musicxml"
    manifest_path = output / f"{stem}.json"
    write_musicxml(build_qnn_conditioned_score(experiment), score_path)
    manifest_path.write_text(
        json.dumps(qnn_experiment_manifest(experiment), indent=2) + "\n",
        encoding="utf-8",
    )
    return score_path, manifest_path


def _write_qnn_wavetable_experiment(
    experiment: QuantumGraphQNNExperiment,
    audio_config: DensityWavetableRenderConfig,
    output_directory: str | Path,
) -> tuple[Path, Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    stem = (
        "quartic_torus_quantum_graph_canon_15_qnn_"
        f"{_qnn_weight_mode(experiment)}_density_16voice_wavetable"
    )
    wav_path = output / f"{stem}.wav"
    manifest_path = output / f"{stem}.json"
    densities = experiment.canon_experiment.density_snapshots
    render = render_density_wavetable_bank(densities, audio_config)
    write_density_wavetable_wav(wav_path, render)
    manifest = qnn_experiment_manifest(experiment)
    manifest["audio"] = density_wavetable_manifest(
        render,
        audio_config,
        densities,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return wav_path, manifest_path


def _write_qnn_articulated_wavetable_experiment(
    experiment: QuantumGraphQNNExperiment,
    audio_config: ArticulatedDensityWavetableConfig,
    output_directory: str | Path,
) -> tuple[Path, Path]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    stem = (
        "quartic_torus_quantum_graph_canon_15_qnn_"
        f"{_qnn_weight_mode(experiment)}_density_16voice_wavetable_articulated"
    )
    wav_path = output / f"{stem}.wav"
    manifest_path = output / f"{stem}.json"
    densities = experiment.canon_experiment.density_snapshots
    voice_offsets = graph_qnn_voice_offsets(
        experiment.qnn_model.graph_edges,
        experiment.qnn_result.selected_mask,
    )
    probabilities = experiment.qnn_result.probabilities
    render = render_articulated_density_wavetable_bank(
        densities,
        audio_config,
        voice_offsets=voice_offsets,
        qnn_probabilities=probabilities,
    )
    write_density_wavetable_wav(wav_path, render)
    manifest = qnn_experiment_manifest(experiment)
    manifest["audio"] = articulated_density_wavetable_manifest(
        render,
        audio_config,
        densities,
        qnn_probabilities=probabilities,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return wav_path, manifest_path


def _qnn_weight_mode(experiment: QuantumGraphQNNExperiment) -> str:
    return (
        "untrained"
        if experiment.qnn_result.weight_provenance == "seeded_untrained"
        else "external"
    )


def main(argv: Sequence[str] | None = None) -> tuple[Path, ...]:
    parser = argparse.ArgumentParser(
        description=(
            "Generate graph-conditioned four-qubit notation and direct audio "
            "experiments."
        )
    )
    parser.add_argument(
        "--mode",
        choices=(
            "entangled",
            "local",
            "both",
            "qnn",
            "wav",
            "wav-articulated",
            "all",
        ),
        default="entangled",
        help="Generate base controls, QNN notation, direct WAV audio, or all.",
    )
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--partition-seed", type=int, default=17)
    parser.add_argument("--entanglement-scale", type=float, default=0.85)
    parser.add_argument("--dephasing", type=float, default=0.12)
    parser.add_argument("--coherence-threshold", type=float, default=0.08)
    parser.add_argument("--qnn-feature-reps", type=int, default=2)
    parser.add_argument("--qnn-ansatz-reps", type=int, default=2)
    parser.add_argument("--qnn-shots", type=int, default=4096)
    parser.add_argument("--qnn-sampler-seed", type=int, default=17)
    parser.add_argument("--qnn-weight-seed", type=int, default=23)
    parser.add_argument("--qnn-untrained-weight-scale", type=float, default=0.15)
    parser.add_argument(
        "--qnn-input-mapping",
        choices=("hybrid", "eigenfield"),
        default="hybrid",
    )
    parser.add_argument("--qnn-activation-floor", type=float, default=0.20)
    parser.add_argument(
        "--qnn-weights",
        type=Path,
        help="Optional JSON list, or object with a 'weights' list, from a later trainer.",
    )
    parser.add_argument("--wav-duration", type=float)
    parser.add_argument("--wav-sample-rate", type=int, default=48_000)
    parser.add_argument("--wav-control-rate", type=float, default=60.0)
    parser.add_argument("--wav-base-frequency", type=float, default=55.0)
    parser.add_argument("--wav-output-ceiling", type=float, default=0.85)
    parser.add_argument("--wav-tempo", type=float, default=92.0)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    args = parser.parse_args(argv)

    base = QuantumGraphCanonConfig(
        layers=args.layers,
        partition_seed=args.partition_seed,
        entanglement_scale=args.entanglement_scale,
        dephasing=args.dephasing,
        coherence_threshold=args.coherence_threshold,
    )
    configurations = []
    if args.mode in ("entangled", "both", "all"):
        configurations.append(replace(base, entangled=True))
    if args.mode in ("local", "both", "all"):
        configurations.append(replace(base, entangled=False))

    written: list[Path] = []
    for config in configurations:
        score_path, manifest_path = generate_experiment(config, args.output_directory)
        written.extend((score_path, manifest_path))
        print(score_path)
        print(manifest_path)

    if args.mode in ("qnn", "wav", "wav-articulated", "all"):
        qnn_config = QuantumGraphQNNConfig(
            feature_reps=args.qnn_feature_reps,
            ansatz_reps=args.qnn_ansatz_reps,
            shots=args.qnn_shots,
            sampler_seed=args.qnn_sampler_seed,
            weight_seed=args.qnn_weight_seed,
            untrained_weight_scale=args.qnn_untrained_weight_scale,
            input_mapping=args.qnn_input_mapping,
            activation_floor=args.qnn_activation_floor,
        )
        qnn_weights = _load_qnn_weights(args.qnn_weights) if args.qnn_weights else None
        provenance = str(args.qnn_weights) if args.qnn_weights else None
        qnn_experiment = build_qnn_conditioned_experiment(
            canon_config=replace(base, entangled=True),
            qnn_config=qnn_config,
            weights=qnn_weights,
            weight_provenance=provenance,
        )
        if args.mode in ("qnn", "all"):
            score_path, manifest_path = _write_qnn_score_experiment(
                qnn_experiment,
                args.output_directory,
            )
            written.extend((score_path, manifest_path))
            print(score_path)
            print(manifest_path)
        if args.mode in ("wav", "all"):
            audio_config = DensityWavetableRenderConfig(
                sample_rate=args.wav_sample_rate,
                duration_seconds=args.wav_duration or 16.0,
                control_rate_hz=args.wav_control_rate,
                base_frequency_hz=args.wav_base_frequency,
                output_ceiling=args.wav_output_ceiling,
            )
            wav_path, audio_manifest_path = _write_qnn_wavetable_experiment(
                qnn_experiment,
                audio_config,
                args.output_directory,
            )
            written.extend((wav_path, audio_manifest_path))
            print(wav_path)
            print(audio_manifest_path)
        if args.mode in ("wav-articulated", "all"):
            articulated_config = ArticulatedDensityWavetableConfig(
                sample_rate=args.wav_sample_rate,
                duration_seconds=args.wav_duration or 24.0,
                control_rate_hz=args.wav_control_rate,
                base_frequency_hz=args.wav_base_frequency,
                output_ceiling=args.wav_output_ceiling,
                tempo_bpm=args.wav_tempo,
            )
            wav_path, audio_manifest_path = (
                _write_qnn_articulated_wavetable_experiment(
                    qnn_experiment,
                    articulated_config,
                    args.output_directory,
                )
            )
            written.extend((wav_path, audio_manifest_path))
            print(wav_path)
            print(audio_manifest_path)
    return tuple(written)


def _load_qnn_weights(path: Path) -> tuple[float, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get("weights") if isinstance(payload, dict) else payload
    if not isinstance(values, list):
        raise ValueError("QNN weights JSON must be a list or an object containing 'weights'")
    return tuple(float(value) for value in values)


if __name__ == "__main__":
    main()
