import numpy as np
import pytest

from qmw_metric.config import LorentzConfig
from qmw_metric.config import QuantumMetricConfig
from qmw_metric.curved_lorentz import CurvedLorentzEngine, ParticleState
from qmw_metric.engine import QuantumMetricEngine
from qmw_metric.frames import MetricFieldFrame
from qmw_metric.grid import Grid2D


def field_with_vorticity(grid, vorticity=2.0):
    zeros = np.zeros(grid.shape)
    ones = np.ones(grid.shape)
    identity = np.zeros((2, 2, *grid.shape))
    identity[0, 0] = identity[1, 1] = 1.0
    return MetricFieldFrame(
        time=0.0,
        density=ones / (ones.sum() * grid.cell_area),
        potential=zeros,
        sigma=zeros,
        lapse=ones,
        metric=identity,
        inverse_metric=identity,
        determinant=ones,
        sqrt_g=ones,
        inverse_metric_factor=ones,
        grad_potential=np.zeros((2, *grid.shape)),
        grad_sigma=np.zeros((2, *grid.shape)),
        potential_laplacian=zeros,
        hessian=np.zeros((2, 2, *grid.shape)),
        christoffel=np.zeros((2, 2, 2, *grid.shape)),
        curvature=zeros,
        current=np.zeros((2, *grid.shape)),
        flow_velocity=np.zeros((2, *grid.shape)),
        vorticity=np.full(grid.shape, vorticity),
    )


def test_magnetic_like_force_does_no_direct_work():
    grid = Grid2D.periodic((8, 8))
    engine = CurvedLorentzEngine(
        grid, LorentzConfig(topography_mode="none", circulation_enabled=True)
    )
    particle = ParticleState(np.array((0.1, 0.2)), np.array((0.7, -0.3)), charge=1.4)
    force = engine.force(particle, field_with_vorticity(grid))
    np.testing.assert_allclose(np.dot(force, particle.velocity), 0.0, atol=1e-14)


def test_force_switches_are_independent():
    grid = Grid2D.periodic((8, 8))
    particle = ParticleState(np.zeros(2), np.array((1.0, 0.0)))
    off = CurvedLorentzEngine(grid, LorentzConfig(topography_mode="none"))
    circulation = CurvedLorentzEngine(
        grid, LorentzConfig(topography_mode="none", circulation_enabled=True)
    )
    field = field_with_vorticity(grid)
    assert np.allclose(off.force(particle, field), 0.0)
    assert not np.allclose(circulation.force(particle, field), 0.0)


def test_hybrid_topography_requires_explicit_double_counting_opt_in():
    with pytest.raises(ValueError, match="double-count"):
        LorentzConfig(topography_mode="hybrid")
    with pytest.warns(RuntimeWarning, match="double-count"):
        config = LorentzConfig(topography_mode="hybrid", allow_hybrid=True)
    assert config.topography_mode == "hybrid"
    with pytest.raises(ValueError, match="unknown"):
        LorentzConfig(topography_mode="spacetime")


def test_geodesic_force_matches_negative_christoffel_contraction():
    grid = Grid2D.periodic((8, 8))
    field = field_with_vorticity(grid, vorticity=0.0)
    # Install a constant grad(sigma) and its conformal Christoffels.
    grad = np.zeros((2, *grid.shape))
    grad[0] = 0.3
    christoffel = np.zeros((2, 2, 2, *grid.shape))
    for i in range(2):
        for j in range(2):
            for k in range(2):
                christoffel[i, j, k] = (
                    (i == j) * grad[k] + (i == k) * grad[j] - (j == k) * grad[i]
                )
    values = dict(field.__dict__)
    values["grad_sigma"] = grad
    values["christoffel"] = christoffel
    field = MetricFieldFrame(**values)
    particle = ParticleState(np.zeros(2), np.array((0.4, -0.2)), mass=1.7)
    engine = CurvedLorentzEngine(grid, LorentzConfig(topography_mode="geodesic"))
    geodesic_acceleration = engine.force(particle, field) / particle.mass
    gamma_at_particle = np.asarray(grid.sample(field.christoffel, particle.position))
    expected = -np.einsum("ijk,j,k->i", gamma_at_particle, particle.velocity, particle.velocity)
    assert np.allclose(geodesic_acceleration, expected)


def test_topography_modes_select_exact_force_components():
    grid = Grid2D.periodic((8, 8))
    base = field_with_vorticity(grid, vorticity=1.25)
    values = dict(base.__dict__)
    grad_phi = np.zeros((2, *grid.shape))
    grad_phi[0], grad_phi[1] = 0.4, -0.2
    values["grad_potential"] = grad_phi
    gamma = np.zeros((2, 2, 2, *grid.shape))
    gamma[0, 0, 0] = 0.3
    gamma[1, 1, 1] = -0.15
    values["christoffel"] = gamma
    field = MetricFieldFrame(**values)
    particle = ParticleState(
        position=np.zeros(2), velocity=np.array((0.5, -0.25)), mass=2.0, charge=1.5
    )

    probe = CurvedLorentzEngine(grid, LorentzConfig(topography_mode="none"))
    terms = probe.force_components(particle, field)
    none_force = probe.force(particle, field)
    circulation_only = CurvedLorentzEngine(
        grid, LorentzConfig(topography_mode="none", circulation_enabled=True)
    ).force(particle, field)
    explicit = CurvedLorentzEngine(
        grid, LorentzConfig(topography_mode="explicit_force")
    ).force(particle, field)
    geodesic = CurvedLorentzEngine(
        grid, LorentzConfig(topography_mode="geodesic")
    ).force(particle, field)
    with pytest.warns(RuntimeWarning, match="double-count"):
        hybrid_config = LorentzConfig(topography_mode="hybrid", allow_hybrid=True)
    hybrid = CurvedLorentzEngine(grid, hybrid_config).force(particle, field)

    assert np.allclose(none_force, 0.0)
    assert np.allclose(circulation_only, terms["circulation"])
    assert np.allclose(explicit, terms["slope"])
    assert np.allclose(geodesic, terms["geodesic"])
    assert np.allclose(hybrid, terms["slope"] + terms["geodesic"])


def test_static_explicit_potential_approximately_conserves_trajectory_energy():
    config = QuantumMetricConfig(
        grid_size=(24, 24),
        mode_count=4,
        lorentz=LorentzConfig(topography_mode="explicit_force"),
    )
    observer = QuantumMetricEngine(config)
    rho = np.zeros((16, 16), dtype=np.complex128)
    rho[5, 5] = 1.0
    field = observer.update_quantum_frame(rho, time=0.0)
    particle = ParticleState(
        position=np.array((0.1, 0.1)), velocity=np.array((0.12, 0.05))
    )
    total_energy = []
    kinetic = []
    potential = []
    dt = 1e-4
    for step in range(1_000):
        particle, frame = observer.lorentz.step(
            particle, field, dt, time=(step + 1) * dt
        )
        kinetic.append(frame.kinetic_energy)
        potential.append(frame.potential_energy)
        total_energy.append(frame.kinetic_energy + frame.potential_energy)
    drift = np.ptp(total_energy)
    resolved_energy_scale = max(kinetic) + np.ptp(potential)
    assert drift / resolved_energy_scale < 0.01
