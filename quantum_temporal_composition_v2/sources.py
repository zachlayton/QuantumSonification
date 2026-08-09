"""Quantum density-state inputs for the v2 relational clock."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Protocol

import numpy as np


class QuantumStateSource(Protocol):
    def read(self, observation: int, dt: float) -> tuple[np.ndarray, str]: ...


class DeterministicFallbackSource:
    def __init__(self, seed: int = 23) -> None:
        self.offset = (seed % 997) / 997.0 * math.tau

    def read(self, observation: int, dt: float) -> tuple[np.ndarray, str]:
        theta = self.offset + observation * (math.sqrt(5.0) - 1.0) * 0.17
        psi = np.array(
            [1.0, 0.35, 0.35 * np.exp(0.5j * theta), np.exp(1j * theta)],
            dtype=np.complex128,
        )
        psi /= np.linalg.norm(psi)
        return np.outer(psi, psi.conj()), "deterministic-fallback"


class DensityFileSource:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self, observation: int, dt: float) -> tuple[np.ndarray, str]:
        path = self._resolve(self.path)
        if path.suffix == ".npy":
            rho = np.load(path)
        elif path.suffix == ".npz":
            payload = np.load(path)
            key = next(
                (key for key in ("rho", "density_matrix", "density") if key in payload.files),
                None,
            )
            if key is None:
                raise ValueError(f"{path} has no density matrix array")
            rho = payload[key]
        else:
            data = json.loads(path.read_text())
            raw = data.get("rho", data.get("density_matrix"))
            if raw is None:
                raise ValueError(f"{path} has no rho or density_matrix field")
            array = np.asarray(raw)
            rho = (
                array[..., 0].astype(float) + 1j * array[..., 1].astype(float)
                if array.ndim == 3 and array.shape[-1] == 2
                else array.astype(np.complex128)
            )
        return np.asarray(rho, dtype=np.complex128), f"density-file:{path}"

    @staticmethod
    def _resolve(path: Path) -> Path:
        if path.name != "current_state.json":
            return path
        data = json.loads(path.read_text())
        for key in ("density_state", "quantum_state", "state_path", "npz_path"):
            if key in data:
                target = Path(data[key])
                return target if target.is_absolute() else path.parent / target
        return path


class StateBusSource:
    def __init__(self, bus: Any, fallback: QuantumStateSource | None = None) -> None:
        self.bus = bus
        self.fallback = fallback or DeterministicFallbackSource()

    def read(self, observation: int, dt: float) -> tuple[np.ndarray, str]:
        frame = getattr(self.bus, "latest", None)
        if frame is None:
            return self.fallback.read(observation, dt)
        return np.asarray(frame.rho, dtype=np.complex128), f"state-bus:{frame.source_name or 'quantum-engine'}"


class ExistingEngineSource:
    def __init__(self, engine: Any, advance: bool = True) -> None:
        self.engine = engine
        self.advance = advance

    def read(self, observation: int, dt: float) -> tuple[np.ndarray, str]:
        value = None
        if self.advance and hasattr(self.engine, "step"):
            try:
                value = self.engine.step(dt)
            except TypeError:
                value = self.engine.step()
        rho = self._extract(value)
        if rho is None:
            rho = self._extract(self.engine)
        if rho is None and hasattr(self.engine, "circuit"):
            from qiskit.quantum_info import Statevector

            psi = np.asarray(
                Statevector.from_instruction(self.engine.circuit).data,
                dtype=np.complex128,
            )
            rho = np.outer(psi, psi.conj())
        if rho is None and hasattr(self.engine, "density_adapter"):
            rho = self.engine.density_adapter.step(dt)
        if rho is None:
            raise TypeError("engine exposes no density matrix, state frame, circuit, or density adapter")
        return np.asarray(rho, dtype=np.complex128), f"existing-engine:{type(self.engine).__name__}"

    @staticmethod
    def _extract(value: Any) -> Any | None:
        if value is None:
            return None
        if isinstance(value, np.ndarray) and value.ndim == 2:
            return value
        if hasattr(value, "rho"):
            return value.rho
        if isinstance(value, dict):
            return value.get("rho", value.get("density_matrix"))
        return None


def make_source(kind: str, path: str | None, seed: int) -> QuantumStateSource:
    if kind == "fallback":
        return DeterministicFallbackSource(seed)
    if kind in {"file", "density-file"}:
        if not path:
            raise ValueError("source=file requires state_path")
        return DensityFileSource(path)
    raise ValueError(f"unknown source {kind!r}")
