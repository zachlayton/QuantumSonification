"""Zero-copy-free shader publication of the authoritative effective fields."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .frames import CurvedModeFrame, MetricFieldFrame, MetricShaderFrame, TrajectoryFrame
from .grid import Grid2D, RealArray


class MetricShaderBridge:
    """Publish texture snapshots through an injected OpenGL/WebGL uploader."""

    FIELD_NAMES = (
        "density", "potential", "sigma", "lapse", "curvature",
        "determinant", "potential_laplacian", "vorticity",
    )
    MODEL_LABEL = "gravity-inspired effective metric observer; not literal spacetime gravity"

    def __init__(
        self,
        grid: Grid2D,
        upload_texture: Callable[[str, RealArray], None] | None = None,
        trajectory_history_length: int = 256,
    ):
        if trajectory_history_length < 1:
            raise ValueError("trajectory_history_length must be positive")
        self.grid = grid
        self._uploader = upload_texture
        self.trajectory_history_length = int(trajectory_history_length)
        self.textures: dict[str, RealArray] = {}
        self.last_time: float | None = None
        self.frame: MetricShaderFrame | None = None
        self._trajectory_history: list[RealArray] = []
        self._last_trajectory_time: float | None = None

    def publish(
        self,
        frame: MetricFieldFrame,
        modes: CurvedModeFrame,
        trajectory: TrajectoryFrame | None = None,
        *,
        revision: int = 0,
        source_revision: int = 0,
        time: float | None = None,
    ) -> MetricShaderFrame:
        for name in self.FIELD_NAMES:
            texture = np.asarray(getattr(frame, name), dtype=np.float32).copy()
            texture.setflags(write=False)
            self.textures[name] = texture
            if self._uploader is not None:
                self._uploader(name, texture)
        for component, texture in enumerate(frame.flow_velocity):
            name = f"phase_connection_{'xy'[component]}"
            texture32 = np.asarray(texture, dtype=np.float32).copy()
            texture32.setflags(write=False)
            self.textures[name] = texture32
            if self._uploader is not None:
                self._uploader(name, texture32)
        for vector_name in ("grad_potential", "current"):
            for component, texture in enumerate(getattr(frame, vector_name)):
                name = f"{vector_name}_{'xy'[component]}"
                texture32 = np.asarray(texture, dtype=np.float32).copy()
                texture32.setflags(write=False)
                self.textures[name] = texture32
                if self._uploader is not None:
                    self._uploader(name, texture32)
        for tensor_name in ("metric", "inverse_metric", "hessian"):
            tensor = getattr(frame, tensor_name)
            for row in range(2):
                for column in range(2):
                    name = f"{tensor_name}_{row}{column}"
                    texture32 = np.asarray(tensor[row, column], dtype=np.float32).copy()
                    texture32.setflags(write=False)
                    self.textures[name] = texture32
                    if self._uploader is not None:
                        self._uploader(name, texture32)
        if trajectory is not None and (
            self._last_trajectory_time is None
            or not np.isclose(trajectory.time, self._last_trajectory_time)
        ):
            self._trajectory_history.append(trajectory.position.copy())
            self._trajectory_history = self._trajectory_history[
                -self.trajectory_history_length:
            ]
            self._last_trajectory_time = trajectory.time
        published_time = frame.time if time is None else float(time)
        self.last_time = published_time
        self.frame = MetricShaderFrame(
            revision=revision,
            source_revision=source_revision,
            time=published_time,
            density=frame.density,
            potential=frame.potential,
            sigma=frame.sigma,
            lapse=frame.lapse,
            metric=frame.metric,
            inverse_metric=frame.inverse_metric,
            determinant=frame.determinant,
            grad_potential=frame.grad_potential,
            hessian=frame.hessian,
            curvature=frame.curvature,
            potential_laplacian=frame.potential_laplacian,
            probability_current=frame.current,
            phase_connection=frame.flow_velocity,
            vorticity=frame.vorticity,
            mode_shapes=modes.modes,
            trajectory_positions=(
                np.asarray(self._trajectory_history, dtype=np.float64)
                if self._trajectory_history else np.empty((0, 2), dtype=np.float64)
            ),
            model_label=self.MODEL_LABEL,
        )
        return self.frame

    def sample(self, name: str, position: RealArray) -> np.ndarray:
        if name not in self.textures:
            raise KeyError(f"texture {name!r} has not been published")
        return self.grid.sample(self.textures[name], position)
