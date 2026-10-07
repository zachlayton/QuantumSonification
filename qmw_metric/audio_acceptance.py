"""Deterministic isolated A/B audio acceptance for the Quantum Metric Field."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import wave

import numpy as np

from .authoritative_state import DensityMatrixEngineMetricAdapter
from .config import LorentzConfig, MetricConfig, PotentialConfig, QuantumMetricConfig, ResonatorConfig
from .curved_lorentz import ParticleState
from .engine import QuantumMetricEngine


@dataclass(frozen=True)
class AudioAcceptanceConfig:
    sample_rate: int = 24_000
    seconds: float = 3.2
    control_hz: float = 100.0
    field_hz: float = 10.0
    grid_size: int = 16
    mode_count: int = 8
    trajectory_gain: float = 600_000.0
    strike_gain: float = 650_000.0


@dataclass(frozen=True)
class RenderEvidence:
    peak: float
    rms: float
    spectral_centroid_hz: float
    max_sample_delta: float
    mode_boundary_delta: float
    mode_boundary_ratio: float
    mode_tracking_click_free: bool
    mode_updates: int
    trajectory_distance: float
    trajectory_pan_range: float
    trajectory_drive_fraction: float
    strike_count: int
    audition_monitor: str
    measurement_event: dict[str, object] | None = None


def _base_config(config: AudioAcceptanceConfig, **changes: object) -> QuantumMetricConfig:
    value = QuantumMetricConfig(
        grid_size=(config.grid_size, config.grid_size),
        mode_count=config.mode_count,
        potential=PotentialConfig(coupling=1.6, screening_length=.28),
        metric=MetricConfig(
            spatial_strength=18.0,
            lapse_strength=5.0,
            sigma_limit=1.25,
            lapse_exponent_limit=1.25,
        ),
        lorentz=LorentzConfig(topography_mode="explicit_force"),
        resonator=ResonatorConfig(
            sample_rate=float(config.sample_rate),
            frequency_floor_hz=55.0,
            frequency_scale_hz=62.0,
            default_damping_ratio=.018,
            retune_time_seconds=.035,
        ),
        metric_update_hz=config.field_hz,
        mode_update_hz=5.0,
    )
    return replace(value, **changes)


def _seed_particle() -> ParticleState:
    return ParticleState(np.array((-.72, -.31)), np.array((.58, .39)))


def _analyse(
    audio: np.ndarray,
    sample_rate: int,
    mode_boundaries: list[int],
    trajectory: np.ndarray,
    measurement_event: dict[str, object] | None = None,
    *,
    trajectory_drive_energy: float = 0.0,
    strike_drive_energy: float = 0.0,
    strike_count: int = 0,
    audition_monitor: str = "mono_modal",
) -> RenderEvidence:
    signal = np.asarray(audio, dtype=np.float64)
    channels = signal[:, None] if signal.ndim == 1 else signal
    delta = np.max(np.abs(np.diff(channels, axis=0, prepend=channels[:1])), axis=1)
    window = np.hanning(channels.shape[0])[:, None]
    spectrum = np.mean(np.abs(np.fft.rfft(channels * window, axis=0)), axis=1)
    frequencies = np.fft.rfftfreq(channels.shape[0], 1.0 / sample_rate)
    centroid = float(np.sum(frequencies * spectrum) / max(np.sum(spectrum), 1e-15))
    boundary_delta = max((float(delta[min(index, delta.size - 1)]) for index in mode_boundaries), default=0.0)
    background = float(np.percentile(delta, 99.5)) if delta.size else 0.0
    ratio = boundary_delta / max(background, 1e-12)
    distance = float(np.sum(np.linalg.norm(np.diff(trajectory, axis=0), axis=1))) if len(trajectory) > 1 else 0.0
    pan_range = float(np.ptp(np.clip(trajectory[:, 0], -1.0, 1.0))) if len(trajectory) else 0.0
    total_drive_energy = trajectory_drive_energy + strike_drive_energy
    return RenderEvidence(
        peak=float(np.max(np.abs(signal))),
        rms=float(np.sqrt(np.mean(signal**2))),
        spectral_centroid_hz=centroid,
        max_sample_delta=float(np.max(delta)),
        mode_boundary_delta=boundary_delta,
        mode_boundary_ratio=ratio,
        mode_tracking_click_free=bool(ratio <= 1.5 and boundary_delta <= .12),
        mode_updates=len(mode_boundaries),
        trajectory_distance=distance,
        trajectory_pan_range=pan_range,
        trajectory_drive_fraction=trajectory_drive_energy / max(total_drive_energy, 1e-30),
        strike_count=strike_count,
        audition_monitor=audition_monitor,
        measurement_event=measurement_event,
    )


def _render(
    engine: QuantumMetricEngine,
    initial_rho: np.ndarray,
    config: AudioAcceptanceConfig,
    *,
    state_source: DensityMatrixEngineMetricAdapter | None = None,
    continuously_update: bool = False,
    measurement_time: float | None = None,
    trajectory_drive: bool = True,
    include_strikes: bool = True,
    stereo_trajectory: bool = False,
) -> tuple[np.ndarray, RenderEvidence]:
    block_size = int(round(config.sample_rate / config.control_hz))
    step_count = int(round(config.seconds * config.control_hz))
    field_stride = max(1, int(round(config.control_hz / config.field_hz)))
    engine.set_particle(_seed_particle())
    engine.update_quantum_frame(initial_rho, 0.0, force_modes=True, source_revision=0)
    audio: list[np.ndarray] = []
    positions: list[np.ndarray] = []
    mode_boundaries: list[int] = []
    previous_mode_time = engine.mode_frame.time
    measurement_record = None
    measured = False
    strike_position = np.array((-.42, .18))
    weights = np.asarray(engine.grid.sample(engine.mode_frame.modes, strike_position))
    weights /= max(float(np.linalg.norm(weights)), 1e-15)
    trajectory_drive_energy = 0.0
    strike_drive_energy = 0.0
    strike_count = 0
    previous_pan = float(np.clip((_seed_particle().position[0] + 1.0) * .5, 0.0, 1.0))
    for index in range(step_count):
        time = index / config.control_hz
        if state_source is not None:
            snapshot = state_source.advance(1.0 / config.control_hz)
            if measurement_time is not None and not measured and time >= measurement_time:
                snapshot, event = state_source.measure(basis="X", request_id=701)
                engine.apply_measurement_quench(snapshot.rho, time)
                measurement_record = {
                    "event_id": int(event.event_id),
                    "basis": event.basis,
                    "outcome": int(event.outcome),
                    "bitstring": event.bitstring,
                    "probability": float(event.probability),
                    "trace_distance": float(event.trace_distance),
                    "revision_before": int(event.revision_before),
                    "revision_after": int(event.revision_after),
                }
                measured = True
            elif continuously_update and index % field_stride == 0:
                engine.update_quantum_frame(
                    snapshot.rho,
                    time,
                    source_revision=max(snapshot.revision, engine.system_frame.source_revision),
                )
        trajectory = engine.process_control_step(1.0 / config.control_hz)
        positions.append(trajectory.position.copy())
        trajectory_component = (
            engine.modal_excitation * config.trajectory_gain
            if trajectory_drive else np.zeros(config.mode_count)
        )
        strike_component = np.zeros(config.mode_count)
        if include_strikes and index in (
            int(round(.12 * config.control_hz)),
            int(round(1.72 * config.control_hz)),
        ):
            strike_component = config.strike_gain * weights
            strike_count += 1
        trajectory_drive_energy += float(np.dot(trajectory_component, trajectory_component))
        strike_drive_energy += float(np.dot(strike_component, strike_component))
        drive = trajectory_component + strike_component
        if engine.mode_frame.time != previous_mode_time:
            mode_boundaries.append(index * block_size)
            previous_mode_time = engine.mode_frame.time
        block = engine.resonator.process_block(drive, block_size)
        if stereo_trajectory:
            pan = float(np.clip((trajectory.position[0] + 1.0) * .5, 0.0, 1.0))
            angles = .5 * np.pi * np.linspace(previous_pan, pan, block_size, endpoint=True)
            block = np.column_stack((block * np.cos(angles), block * np.sin(angles)))
            previous_pan = pan
        audio.append(block)
    signal = np.concatenate(audio)
    trajectory_array = np.asarray(positions)
    return signal, _analyse(
        signal,
        config.sample_rate,
        mode_boundaries,
        trajectory_array,
        measurement_record,
        trajectory_drive_energy=trajectory_drive_energy,
        strike_drive_energy=strike_drive_energy,
        strike_count=strike_count,
        audition_monitor="stereo_actual_trajectory" if stereo_trajectory else "mono_modal",
    )


def _write_wav(path: Path, signal: np.ndarray, sample_rate: int, gain: float) -> None:
    pcm = np.asarray(np.clip(signal * gain, -1.0, 1.0) * 32767.0, dtype="<i2")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1 if pcm.ndim == 1 else pcm.shape[1])
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(pcm.tobytes())


def _comparison_metrics(a: np.ndarray, b: np.ndarray, sample_rate: int) -> dict[str, float | bool]:
    scale_a = max(float(np.sqrt(np.mean(a**2))), 1e-15)
    scale_b = max(float(np.sqrt(np.mean(b**2))), 1e-15)
    matched_a = a / scale_a
    matched_b = b / scale_b
    difference = float(np.sqrt(np.mean((matched_a - matched_b) ** 2)))
    channels_a = matched_a[:, None] if matched_a.ndim == 1 else matched_a
    channels_b = matched_b[:, None] if matched_b.ndim == 1 else matched_b
    window = np.hanning(len(a))[:, None]
    spectrum_a = np.mean(np.abs(np.fft.rfft(channels_a * window, axis=0)), axis=1) + 1e-12
    spectrum_b = np.mean(np.abs(np.fft.rfft(channels_b * window, axis=0)), axis=1) + 1e-12
    spectral_distance = float(np.sqrt(np.mean((20.0 * np.log10(spectrum_a / spectrum_b)) ** 2)))
    active_floor = 1e-3 * max(float(np.max(spectrum_a)), float(np.max(spectrum_b)))
    active = np.maximum(spectrum_a, spectrum_b) >= active_floor
    active_spectral_distance = float(
        np.sqrt(np.mean((20.0 * np.log10(spectrum_a[active] / spectrum_b[active])) ** 2))
    )
    correlation = float(
        np.dot(matched_a.ravel(), matched_b.ravel())
        / max(np.linalg.norm(matched_a) * np.linalg.norm(matched_b), 1e-15)
    )
    rms_ratio_db = float(20.0 * np.log10(scale_b / scale_a))
    return {
        "level_matched_waveform_distance": difference,
        "spectral_distance_db_rms": spectral_distance,
        "active_band_spectral_distance_db_rms": active_spectral_distance,
        "waveform_correlation": correlation,
        "rms_ratio_b_over_a": scale_b / scale_a,
        "rms_ratio_db": rms_ratio_db,
        "objectively_distinct": bool(
            active_spectral_distance >= 3.0
            and (correlation <= .9 or abs(rms_ratio_db) >= 3.0)
        ),
    }


def _save_pair(
    output: Path,
    name: str,
    label_a: str,
    label_b: str,
    a: np.ndarray,
    b: np.ndarray,
    evidence_a: RenderEvidence,
    evidence_b: RenderEvidence,
    sample_rate: int,
) -> dict[str, object]:
    maximum = max(float(np.max(np.abs(a))), float(np.max(np.abs(b))), 1e-12)
    gain = .82 / maximum
    silence_shape = (int(.55 * sample_rate),) if a.ndim == 1 else (int(.55 * sample_rate), a.shape[1])
    silence = np.zeros(silence_shape)
    files = {
        "a": f"{name}__A_{label_a}.wav",
        "b": f"{name}__B_{label_b}.wav",
        "ab": f"{name}__AB.wav",
    }
    _write_wav(output / files["a"], a, sample_rate, gain)
    _write_wav(output / files["b"], b, sample_rate, gain)
    _write_wav(output / files["ab"], np.concatenate((a, silence, b)), sample_rate, gain)
    return {
        "name": name,
        "A": label_a,
        "B": label_b,
        "files": files,
        "shared_output_gain": gain,
        "evidence_A": asdict(evidence_a),
        "evidence_B": asdict(evidence_b),
        "difference": _comparison_metrics(a, b, sample_rate),
    }


def render_isolated_audio_acceptance(
    output_directory: str | Path,
    config: AudioAcceptanceConfig = AudioAcceptanceConfig(),
) -> dict[str, object]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    authority = DensityMatrixEngineMetricAdapter.create_offline(measurement_seed=29)
    authoritative = authority.snapshot()
    rho = authoritative.rho
    comparisons: list[dict[str, object]] = []

    audition_metric = MetricConfig(
        spatial_strength=60.0,
        lapse_strength=5.0,
        sigma_limit=2.5,
        lapse_exponent_limit=1.25,
    )
    flat = _base_config(
        config,
        potential=PotentialConfig(coupling=0.0, screening_length=.28),
        metric=audition_metric,
    )
    curved = _base_config(config, metric=audition_metric)
    a, ea = _render(QuantumMetricEngine(flat), rho, config, trajectory_drive=False)
    b, eb = _render(QuantumMetricEngine(curved), rho, config, trajectory_drive=False)
    comparisons.append(_save_pair(output, "01_flat_vs_curved_modes", "flat", "curved", a, b, ea, eb, config.sample_rate))
    comparisons[-1]["controlled_change"] = "potential coupling 0.0 -> 1.6; all modal-audition settings fixed"
    comparisons[-1]["common_excitation"] = "two localized spatial impulses projected onto eigenmodes"

    explicit = _base_config(config, lorentz=LorentzConfig(topography_mode="explicit_force"))
    geodesic = _base_config(config, lorentz=LorentzConfig(topography_mode="geodesic"))
    a, ea = _render(QuantumMetricEngine(explicit), rho, config, include_strikes=False, stereo_trajectory=True)
    b, eb = _render(QuantumMetricEngine(geodesic), rho, config, include_strikes=False, stereo_trajectory=True)
    comparisons.append(_save_pair(output, "02_explicit_vs_geodesic", "explicit_slope", "geodesic", a, b, ea, eb, config.sample_rate))
    comparisons[-1]["controlled_change"] = "topography_mode explicit_force -> geodesic"
    comparisons[-1]["common_excitation"] = "trajectory-force modal overlap only; stereo pan = actual x position"

    circulation_off = _base_config(config, lorentz=LorentzConfig(topography_mode="explicit_force", circulation_enabled=False))
    circulation_on = _base_config(
        config,
        lorentz=LorentzConfig(
            topography_mode="explicit_force",
            circulation_enabled=True,
            circulation_gain=.015,
        ),
    )
    a, ea = _render(QuantumMetricEngine(circulation_off), rho, config, include_strikes=False, stereo_trajectory=True)
    b, eb = _render(QuantumMetricEngine(circulation_on), rho, config, include_strikes=False, stereo_trajectory=True)
    comparisons.append(_save_pair(output, "03_circulation_off_vs_on", "off", "on", a, b, ea, eb, config.sample_rate))
    comparisons[-1]["controlled_change"] = "circulation disabled -> enabled at analysis gain 0.015"
    comparisons[-1]["common_excitation"] = "trajectory-force modal overlap only; stereo pan = actual x position"

    static_source = DensityMatrixEngineMetricAdapter.create_offline(measurement_seed=29)
    dynamic_source = DensityMatrixEngineMetricAdapter.create_offline(measurement_seed=29)
    a, ea = _render(QuantumMetricEngine(explicit), static_source.snapshot().rho, config, include_strikes=False, stereo_trajectory=True)
    b, eb = _render(QuantumMetricEngine(explicit), dynamic_source.snapshot().rho, config, state_source=dynamic_source, continuously_update=True, include_strikes=False, stereo_trajectory=True)
    comparisons.append(_save_pair(output, "04_static_vs_changing_geometry", "static", "continuous", a, b, ea, eb, config.sample_rate))
    comparisons[-1]["controlled_change"] = "fixed initial rho -> continuous authoritative rho evolution"
    comparisons[-1]["common_excitation"] = "trajectory-force overlap plus antisymmetric moving-mode connection"

    continuous_source = DensityMatrixEngineMetricAdapter.create_offline(measurement_seed=29)
    quench_source = DensityMatrixEngineMetricAdapter.create_offline(measurement_seed=29)
    a, ea = _render(QuantumMetricEngine(explicit), continuous_source.snapshot().rho, config, state_source=continuous_source, continuously_update=True, include_strikes=False, stereo_trajectory=True)
    b, eb = _render(QuantumMetricEngine(explicit), quench_source.snapshot().rho, config, state_source=quench_source, continuously_update=True, measurement_time=config.seconds * .5, include_strikes=False, stereo_trajectory=True)
    comparisons.append(_save_pair(output, "05_continuous_vs_measurement_quench", "continuous", "measurement_quench", a, b, ea, eb, config.sample_rate))
    comparisons[-1]["controlled_change"] = "continuous evolution -> owner-declared X-basis collapse at midpoint"
    comparisons[-1]["common_excitation"] = "trajectory-force overlap; smoothed modal position and velocity transfer"

    report = {
        "contract": "qmw_metric.isolated_audio_acceptance.v1",
        "status": "revised after listener rejection; human re-audition pending",
        "authoritative_source": {
            "source": authoritative.source,
            "basis_order": authoritative.basis_order,
            "initial_revision": authoritative.revision,
            "initial_time": authoritative.time,
            "observer_mutates_rho": False,
        },
        "config": asdict(config),
        "comparisons": comparisons,
        "all_objectively_distinct": all(item["difference"]["objectively_distinct"] for item in comparisons),
        "all_auditions_source_isolated": all(
            (item["evidence_A"]["trajectory_drive_fraction"] == 0.0
             and item["evidence_B"]["trajectory_drive_fraction"] == 0.0)
            if item["name"] == "01_flat_vs_curved_modes"
            else (item["evidence_A"]["trajectory_drive_fraction"] > .999
                  and item["evidence_B"]["trajectory_drive_fraction"] > .999)
            for item in comparisons
        ),
        "all_mode_tracking_click_free": all(
            item[side]["mode_tracking_click_free"]
            for item in comparisons for side in ("evidence_A", "evidence_B")
        ),
    }
    (output / "acceptance_report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (output / "LISTENING_ORDER.md").write_text(
        "# Isolated QMW Metric listening order\n\n"
        "Use headphones or full-range stereo at a conservative level. Each AB file is A, 550 ms silence, then B.\n\n"
        "Pair 1 uses two broad modal impulses only. Pairs 2-5 remove those shared strikes and monitor actual trajectory overlap in stereo; horizontal trajectory position controls equal-power pan.\n\n"
        + "\n".join(
            f"{index}. `{item['files']['ab']}` — A: {item['A']}; B: {item['B']}"
            for index, item in enumerate(comparisons, start=1)
        )
        + "\n\nConfirm separately whether the relationship is unmistakable and whether any click occurs at continuous mode changes.\n"
    )
    return report
