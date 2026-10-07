"""Master coordinator for the first Quantum Metric Field vertical slice."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .config import QuantumMetricConfig
from .curved_lorentz import CurvedLorentzEngine, ParticleState
from .curved_modes import CurvedModeSolver
from .frames import CurvedModeFrame, MetricFieldFrame, QMWMetricFrame, TrajectoryFrame
from .grid import Grid2D, RealArray
from .metric_field import QuantumMetricField
from .modal_resonator import ModalResonator
from .mode_tracker import ModeTracker
from .potential_solver import ScreenedPoissonSolver
from .probability_current import ProbabilityCurrentProjector
from .quantum_projector import QuantumSpatialProjector, localized_gaussian_basis
from .quench import GeometryQuenchEngine
from .shader_bridge import MetricShaderBridge
from .trajectory_coupler import TrajectoryModeCoupler

ComplexArray = NDArray[np.complex128]


class QuantumMetricEngine:
    """Read-only observer of rho with named field, mode, trajectory, and audio seams."""

    def __init__(
        self,
        config: QuantumMetricConfig = QuantumMetricConfig(),
        basis: ComplexArray | None = None,
        basis_id: str | None = None,
        shader_bridge: MetricShaderBridge | None = None,
    ):
        self.config = config
        self.grid = Grid2D.periodic(config.grid_size, config.extent)
        if basis is None:
            basis_value = localized_gaussian_basis(self.grid, config.quantum_dimension)
            self.basis_id = basis_id or "localized_gaussians.v1"
        else:
            if not basis_id or not basis_id.strip():
                raise ValueError("a custom projection basis requires a nonempty basis_id")
            basis_value = basis
            self.basis_id = basis_id
        self.projector = QuantumSpatialProjector(basis_value, self.grid)
        self.potential_solver = ScreenedPoissonSolver(self.grid, config.potential)
        self.metric = QuantumMetricField(self.grid, config.metric)
        self.current_projector = ProbabilityCurrentProjector(basis_value, self.grid)
        self.mode_solver = CurvedModeSolver(
            self.grid,
            frequency_floor_hz=config.resonator.frequency_floor_hz,
            frequency_scale_hz=config.resonator.frequency_scale_hz,
            damping_ratio=config.resonator.default_damping_ratio,
        )
        self.mode_tracker = ModeTracker(self.grid)
        self.lorentz = CurvedLorentzEngine(self.grid, config.lorentz)
        self.coupler = TrajectoryModeCoupler(self.grid)
        self.resonator = ModalResonator(config.resonator)
        self.quench = GeometryQuenchEngine(self.grid)
        self.shader = shader_bridge or MetricShaderBridge(self.grid)
        self.field_frame: MetricFieldFrame | None = None
        self.mode_frame: CurvedModeFrame | None = None
        self.trajectory_frame: TrajectoryFrame | None = None
        self.particle = ParticleState(np.array((0.0, 0.0)), np.array((0.0, 0.2)))
        self.modal_excitation = np.zeros(config.mode_count, dtype=np.float64)
        self._last_mode_time = -np.inf
        self._last_mode_metric_weight: RealArray | None = None
        self._revision = 0
        self._source_revision = 0
        self._control_time = 0.0
        self.system_frame: QMWMetricFrame | None = None

    def _construct_field(self, rho: ComplexArray, time: float) -> tuple[MetricFieldFrame, dict[str, RealArray]]:
        density = self.projector.density(rho)
        potential = self.potential_solver.solve(density)
        metric_data = self.metric.construct(potential)
        current, velocity, vorticity = self.current_projector.current(rho, density)
        field = MetricFieldFrame(
            time=time,
            density=density,
            potential=potential,
            sigma=metric_data["sigma"],
            lapse=metric_data["lapse"],
            metric=metric_data["metric"],
            inverse_metric=metric_data["inverse_metric"],
            determinant=metric_data["determinant"],
            sqrt_g=metric_data["sqrt_g"],
            inverse_metric_factor=metric_data["inverse_metric_factor"],
            grad_potential=metric_data["grad_potential"],
            grad_sigma=metric_data["grad_sigma"],
            potential_laplacian=metric_data["potential_laplacian"],
            hessian=metric_data["hessian"],
            christoffel=metric_data["christoffel"],
            curvature=metric_data["curvature"],
            current=current,
            flow_velocity=velocity,
            vorticity=vorticity,
        )
        return field, metric_data

    def _publish_synchronized_frame(self, time: float) -> QMWMetricFrame:
        if self.field_frame is None or self.mode_frame is None:
            raise RuntimeError("field and mode frames must exist before publication")
        self._revision += 1
        shader = self.shader.publish(
            self.field_frame,
            self.mode_frame,
            self.trajectory_frame,
            revision=self._revision,
            source_revision=self._source_revision,
            time=time,
        )
        self.system_frame = QMWMetricFrame(
            revision=self._revision,
            source_revision=self._source_revision,
            time=time,
            field=self.field_frame,
            modes=self.mode_frame,
            trajectory=self.trajectory_frame,
            shader=shader,
            projection_basis=self.basis_id,
            potential_model="screened_poisson.periodic_fft.v1",
            metric_model="conformal_2d_plus_lapse.v1",
            topography_mode=self.config.lorentz.topography_mode,
        )
        return self.system_frame

    def update_quantum_frame(
        self,
        rho: ComplexArray,
        time: float,
        force_modes: bool = False,
        source_revision: int | None = None,
    ) -> MetricFieldFrame:
        """Observe continuous rho evolution; this method never modifies rho."""
        if self.field_frame is not None and time < self.field_frame.time:
            raise ValueError("quantum-frame time must be monotonic")
        if source_revision is not None:
            if source_revision < self._source_revision:
                raise ValueError("source_revision must be monotonic")
            self._source_revision = int(source_revision)
        field, metric_data = self._construct_field(rho, float(time))
        self.field_frame = field
        self._control_time = float(time)
        mode_period = 1.0 / self.config.mode_update_hz
        if self.mode_frame is None or force_modes or time - self._last_mode_time >= mode_period:
            candidate = self.mode_solver.solve(metric_data["sqrt_g"], self.config.mode_count, time)
            self.mode_frame = self.mode_tracker.match(
                self.mode_frame,
                candidate,
                metric_data["sqrt_g"],
                self._last_mode_metric_weight,
            )
            self.resonator.update_mode_frame(self.mode_frame)
            self._last_mode_time = float(time)
            self._last_mode_metric_weight = metric_data["sqrt_g"].copy()
        self._publish_synchronized_frame(float(time))
        return field

    def apply_measurement_quench(self, rho: ComplexArray, time: float) -> MetricFieldFrame:
        """Handle an upstream-declared discrete measurement intervention."""
        old_modes = self.mode_frame
        old_amplitudes = self.resonator.positions.copy()
        old_velocities = self.resonator.velocities.copy()
        field = self.update_quantum_frame(rho, time, force_modes=True)
        if old_modes is not None and self.mode_frame is not None and old_amplitudes.size:
            transferred = self.quench.transfer_energy(
                old_amplitudes, old_modes, self.mode_frame, self.field_frame.sqrt_g
            )
            transferred_velocities = self.quench.transfer_energy(
                old_velocities, old_modes, self.mode_frame, self.field_frame.sqrt_g
            )
            self.resonator.transition_state(transferred, transferred_velocities)
        return field

    def set_particle(self, particle: ParticleState) -> None:
        self.particle = particle

    def process_control_step(self, dt: float) -> TrajectoryFrame:
        if self.field_frame is None or self.mode_frame is None:
            raise RuntimeError("update_quantum_frame must be called first")
        self._control_time += dt
        self.particle, self.trajectory_frame = self.lorentz.step(
            self.particle, self.field_frame, dt, time=self._control_time
        )
        self.modal_excitation = self.coupler.excitation(
            self.trajectory_frame.position, self.trajectory_frame.force, self.mode_frame
        )
        self._publish_synchronized_frame(self._control_time)
        return self.trajectory_frame

    def process_audio_block(self, block_size: int) -> RealArray:
        return self.resonator.process_block(self.modal_excitation, block_size)
