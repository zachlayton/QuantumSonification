from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from qmw.flucoma import (
    DescriptorCorpus,
    QuantumDescriptorExtractor,
    build_audio_corpus,
    density_matrix_to_activation_sequences,
    density_matrix_to_mosaic_tiles,
    quantum_descriptor_to_audio_query,
    summarize_density_mosaic,
)
from qmw.core import QuantumStateFrame


X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)


class FluCoMaView:
    """Publish normalized OSC controls for FluCoMa corpus navigation in Max."""

    def __init__(
        self,
        corpus_size: int = 512,
        mosaic_tiles: int = 8,
        mosaic_sequences: int = 4,
        control_interval: float = 0.2,
        mosaic_interval: float = 2.0,
        explanation_interval: float = 1.0,
        audio_corpus_folder: str | Path | None = "materials",
        audio_lookup_interval: float = 2.0,
        audio_analysis_duration: float = 2.0,
        enable_mosaic_stream: bool = False,
        send_descriptor_arrays: bool = False,
    ) -> None:
        self._previous: dict[int, tuple[float, float, float]] = {}
        self.extractor = QuantumDescriptorExtractor()
        self.corpus = DescriptorCorpus(max_items=corpus_size)
        self.mosaic_tiles = int(mosaic_tiles)
        self.mosaic_sequences = int(mosaic_sequences)
        self.control_interval = float(control_interval)
        self.mosaic_interval = float(mosaic_interval)
        self.explanation_interval = float(explanation_interval)
        self.audio_lookup_interval = float(audio_lookup_interval)
        self.enable_mosaic_stream = bool(enable_mosaic_stream)
        self.send_descriptor_arrays = bool(send_descriptor_arrays)
        self._last_control_time = -1.0e9
        self._last_mosaic_time = -1.0e9
        self._last_descriptor_array_time = -1.0e9
        self._last_explanation_time = -1.0e9
        self._last_audio_lookup_time = -1.0e9
        self._last_audio_identifier: str | None = None
        self.audio_corpus = self._load_audio_corpus(
            audio_corpus_folder,
            audio_analysis_duration,
        )
        self._sent_schema = False

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        rho = np.asarray(frame.rho, dtype=np.complex128)
        n_qubits = self._infer_n_qubits(rho)
        if n_qubits <= 0:
            return

        now = float(frame.t)
        if now - self._last_control_time < self.control_interval:
            return
        self._last_control_time = now

        descriptor = self.extractor.extract(frame)
        audio_query = quantum_descriptor_to_audio_query(descriptor)
        projection_x, projection_y = self.corpus.projection(descriptor)
        nearest_before_add = self.corpus.nearest(descriptor, exclude_self=False)
        novelty = self.corpus.novelty(descriptor)
        self.corpus.add(descriptor)

        dt = max(float(frame.dt), 1e-9)
        cursors: list[tuple[float, float]] = []
        depths: list[float] = []
        purities: list[float] = []
        entropies: list[float] = []
        speeds: list[float] = []

        for qubit in range(n_qubits):
            reduced = self._partial_trace(rho, (qubit,), n_qubits)
            bx, by, bz = self._bloch(reduced)
            vector = (bx, by, bz)
            previous = self._previous.get(qubit)
            raw_speed = 0.0 if previous is None else math.dist(vector, previous) / dt
            self._previous[qubit] = vector

            cursor_x = self._unit(bx)
            cursor_y = self._unit(bz)
            y_depth = self._unit(by)
            speed = self._speed_unit(raw_speed)
            purity = float(np.clip(np.trace(reduced @ reduced).real, 0.0, 1.0))
            entropy = float(np.clip(self._entropy(reduced), 0.0, 1.0))
            radius = float(np.clip(math.sqrt(bx * bx + bz * bz), 0.0, 1.0))

            cursors.append((cursor_x, cursor_y))
            depths.append(y_depth)
            purities.append(purity)
            entropies.append(entropy)
            speeds.append(speed)

            payloads = {
                f"/qmw/flucoma/q{qubit}/cursor": [cursor_x, cursor_y],
                f"/qmw/flucoma/q{qubit}/x": cursor_x,
                f"/qmw/flucoma/q{qubit}/y": cursor_y,
                f"/qmw/flucoma/q{qubit}/depth": y_depth,
                f"/qmw/flucoma/q{qubit}/radius": radius,
                f"/qmw/flucoma/q{qubit}/purity": purity,
                f"/qmw/flucoma/q{qubit}/entropy": entropy,
                f"/qmw/flucoma/q{qubit}/speed": speed,
                f"/qmw/flucoma/q{qubit}/raw_bloch": [bx, by, bz],
            }
            self._send_payloads(payloads, osc)

        mean_cursor_x = float(np.mean([cursor[0] for cursor in cursors]))
        mean_cursor_y = float(np.mean([cursor[1] for cursor in cursors]))
        global_payloads = {
            "/qmw/flucoma/cursor": [mean_cursor_x, mean_cursor_y],
            "/qmw/flucoma/projection": [projection_x, projection_y],
            "/qmw/flucoma/depth": float(np.mean(depths)),
            "/qmw/flucoma/stability": float(np.mean(purities)),
            "/qmw/flucoma/scatter": float(np.mean(entropies)),
            "/qmw/flucoma/rate": float(np.mean(speeds)),
            "/qmw/flucoma/novelty": novelty,
            "/qmw/flucoma/corpus/size": len(self.corpus.items),
        }
        if (
            self.send_descriptor_arrays
            and now - self._last_descriptor_array_time >= self.mosaic_interval
        ):
            global_payloads.update(
                {
                    "/qmw/flucoma/descriptor/values": descriptor.values.tolist(),
                    "/qmw/flucoma/audio_query/values": audio_query.values.tolist(),
                }
            )
            self._last_descriptor_array_time = now
        if not self._sent_schema:
            global_payloads.update(
                {
                    "/qmw/flucoma/descriptor/names": list(descriptor.names),
                    "/qmw/flucoma/audio_query/names": list(audio_query.names),
                }
            )
            self._sent_schema = True
        if nearest_before_add is not None:
            global_payloads.update(
                {
                    "/qmw/flucoma/nearest/id": nearest_before_add.identifier,
                    "/qmw/flucoma/nearest/index": nearest_before_add.index,
                    "/qmw/flucoma/nearest/distance": nearest_before_add.distance,
                }
            )
        if (
            self.audio_corpus is not None
            and now - self._last_audio_lookup_time >= self.audio_lookup_interval
        ):
            nearest_audio = self.audio_corpus.nearest(audio_query, exclude_self=False)
            self._last_audio_lookup_time = now
            if nearest_audio is not None:
                path = nearest_audio.metadata.get("path", "")
                changed = nearest_audio.identifier != self._last_audio_identifier
                self._last_audio_identifier = nearest_audio.identifier
                global_payloads.update(
                    {
                        "/qmw/flucoma/audio/nearest/distance": nearest_audio.distance,
                        "/qmw/flucoma/audio/nearest/changed": 1 if changed else 0,
                        "/qmw/flucoma/audio/nearest/id": nearest_audio.identifier,
                        "/qmw/flucoma/audio/nearest/path": path,
                    }
                )
        self._send_payloads(global_payloads, osc)
        if (
            self.enable_mosaic_stream
            and now - self._last_mosaic_time >= self.mosaic_interval
        ):
            include_explanations = now - self._last_explanation_time >= self.explanation_interval
            self._send_density_mosaic(
                rho,
                osc,
                include_explanations=include_explanations,
            )
            self._last_mosaic_time = now
            if include_explanations:
                self._last_explanation_time = now

    @staticmethod
    def _send_payloads(payloads: dict[str, Any], osc: Any) -> None:
        for address, value in payloads.items():
            osc.send_message(address, value)

    @staticmethod
    def _load_audio_corpus(
        folder: str | Path | None,
        analysis_duration: float,
    ) -> DescriptorCorpus | None:
        if folder is None:
            return None
        root = Path(__file__).resolve().parents[2]
        path = Path(folder)
        if not path.is_absolute():
            path = root / path
        if not path.exists():
            return None
        try:
            corpus = build_audio_corpus(
                path,
                max_duration=analysis_duration,
                max_items=128,
            )
        except Exception as exc:
            print(f"FluCoMa audio corpus unavailable: {exc}")
            return None
        if not corpus.items:
            return None
        print(f"FluCoMa audio corpus loaded: {len(corpus.items)} files from {path}")
        return corpus

    def _send_density_mosaic(
        self,
        rho: np.ndarray,
        osc: Any,
        *,
        include_explanations: bool,
    ) -> None:
        tiles = density_matrix_to_mosaic_tiles(rho, max_tiles=self.mosaic_tiles)
        sequences = density_matrix_to_activation_sequences(
            rho,
            max_sequences=self.mosaic_sequences,
        )
        payloads: dict[str, Any] = {
            "/qmw/flucoma/mosaic/count": len(tiles),
            "/qmw/flucoma/mosaic/summary": [
                value
                for tile in tiles
                for value in tile.osc_summary()
            ],
            "/qmw/flucoma/mosaic/sequence/count": len(sequences),
            "/qmw/flucoma/mosaic/sequence/summary": [
                value
                for sequence in sequences
                for value in sequence.osc_summary()
            ],
        }
        if include_explanations:
            payloads["/qmw/flucoma/mosaic/explanation"] = summarize_density_mosaic(
                tiles[:4],
                sequences[:2],
            )
        for index, tile in enumerate(tiles):
            base = f"/qmw/flucoma/mosaic/tile/{index}"
            payloads.update(
                {
                    f"{base}/cell": [tile.row, tile.column],
                    f"{base}/basis": [tile.basis_from, tile.basis_to],
                    f"{base}/salience": tile.salience,
                    f"{base}/amplitude": tile.amplitude,
                    f"{base}/phase": tile.phase,
                    f"{base}/phase_unit": tile.phase_unit,
                    f"{base}/probability": tile.probability,
                    f"{base}/coherence": tile.coherence,
                    f"{base}/distance": tile.distance,
                    f"{base}/role": tile.role,
                    f"{base}/reason_codes": tile.reason_codes,
                }
            )
            if include_explanations and index < 4:
                payloads[f"{base}/explanation"] = tile.explanation
            if index < 4:
                payloads[f"{base}/audio_query"] = tile.query.values.tolist()
        for index, sequence in enumerate(sequences):
            base = f"/qmw/flucoma/mosaic/sequence/{index}"
            payloads.update(
                {
                    f"{base}/direction": sequence.direction,
                    f"{base}/start": [sequence.start_row, sequence.start_column],
                    f"{base}/end": [sequence.end_row, sequence.end_column],
                    f"{base}/basis": [sequence.basis_start, sequence.basis_end],
                    f"{base}/length": sequence.length,
                    f"{base}/salience": sequence.salience,
                    f"{base}/amplitude": sequence.amplitude,
                    f"{base}/phase_unit": sequence.phase_unit,
                    f"{base}/phase_slope": sequence.phase_slope,
                    f"{base}/probability": sequence.probability,
                    f"{base}/coherence": sequence.coherence,
                    f"{base}/distance": sequence.distance,
                    f"{base}/continuity": sequence.continuity,
                    f"{base}/role": sequence.role,
                    f"{base}/reason_codes": sequence.reason_codes,
                }
            )
            if include_explanations and index < 2:
                payloads[f"{base}/explanation"] = sequence.explanation
            if index < 2:
                payloads[f"{base}/audio_query"] = sequence.query.values.tolist()
        self._send_payloads(payloads, osc)

    @staticmethod
    def _unit(value: float) -> float:
        return float(np.clip((value + 1.0) * 0.5, 0.0, 1.0))

    @staticmethod
    def _speed_unit(value: float) -> float:
        return float(np.clip(value / 8.0, 0.0, 1.0))

    @staticmethod
    def _infer_n_qubits(rho: np.ndarray) -> int:
        if rho.ndim != 2 or rho.shape[0] != rho.shape[1] or rho.shape[0] < 2:
            return 0
        n_qubits = int(round(math.log2(rho.shape[0])))
        return n_qubits if 2**n_qubits == rho.shape[0] else 0

    @staticmethod
    def _partial_trace(rho: np.ndarray, keep: tuple[int, ...], n_qubits: int) -> np.ndarray:
        keep = tuple(sorted(keep))
        tensor = rho.reshape((2,) * (2 * n_qubits))
        input_labels = list(range(n_qubits))
        for qubit in range(n_qubits):
            input_labels.append(qubit + n_qubits if qubit in keep else qubit)
        output_labels = list(keep) + [qubit + n_qubits for qubit in keep]
        reduced = np.einsum(tensor, input_labels, output_labels)
        dim = 2 ** len(keep)
        return reduced.reshape(dim, dim)

    @staticmethod
    def _bloch(rho_single: np.ndarray) -> tuple[float, float, float]:
        return (
            float(np.trace(rho_single @ X).real),
            float(np.trace(rho_single @ Y).real),
            float(np.trace(rho_single @ Z).real),
        )

    @staticmethod
    def _entropy(rho: np.ndarray) -> float:
        values = np.clip(np.linalg.eigvalsh(rho).real, 0.0, 1.0)
        values = values[values > 1e-12]
        return float(-np.sum(values * np.log2(values))) if values.size else 0.0
