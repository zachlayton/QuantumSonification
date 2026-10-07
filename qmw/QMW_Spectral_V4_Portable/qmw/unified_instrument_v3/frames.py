"""Immutable V3 frames after the authoritative :class:`QuantumFrame`.

The V3 chain is intentionally split into small, inspectable observers:

``QuantumFrame -> RelationalGeometryFrame -> TuningGeometryFrame
-> ModalResonanceFrame -> AcousticFieldFrame -> StereoObservationFrame``.

``QuantumFrame`` is supplied by :mod:`qmw.quantum.dynamics`.  V3's
``RelationalGeometryFrame`` is a distinct, explicit connected-correlation
contract; existing mutual-information geometry remains an optional diagnostic
observer, never an undocumented substitute for this contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


Array = np.ndarray
MODE_COUNT = 20
QUBIT_COUNT = 4
RELATIONAL_EDGE_PAIRS = tuple((left, right) for left in range(QUBIT_COUNT) for right in range(left + 1, QUBIT_COUNT))
_EPS = 1.0e-12


def _readonly(values: object, *, dtype: object) -> Array:
    result = np.array(values, dtype=dtype, copy=True)
    result.setflags(write=False)
    return result


def _revision(value: int, *, name: str) -> int:
    if int(value) != value or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer.")
    return int(value)


def _time(value: float) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("time must be finite.")
    return result


def _mode_ids(values: tuple[str, ...]) -> tuple[str, ...]:
    if len(values) != MODE_COUNT or len(set(values)) != MODE_COUNT or any(not str(item) for item in values):
        raise ValueError("mode_ids must be 20 unique nonempty stable identifiers.")
    return tuple(str(item) for item in values)


DEFAULT_MODE_IDS = tuple(f"mode_{index:02d}" for index in range(MODE_COUNT))


def _node_ids(values: tuple[str, ...]) -> tuple[str, ...]:
    if len(values) != QUBIT_COUNT or len(set(values)) != QUBIT_COUNT or any(not str(item) for item in values):
        raise ValueError("node_ids must be four unique nonempty stable identifiers.")
    return tuple(str(item) for item in values)


def _diagnostics(values: tuple[str, ...]) -> tuple[str, ...]:
    if any(not isinstance(item, str) or not item for item in values):
        raise ValueError("diagnostics must contain only nonempty strings.")
    return tuple(values)


def _provenance(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("provenance must be a nonempty string.")
    return value


@dataclass(frozen=True)
class RelationalGeometryFrame:
    """Immutable four-qubit geometry derived from connected Pauli correlations.

    ``connected_correlation_tensors[e, i, j]`` is the declared invariant
    quantity ``<sigma_i sigma_j> - <sigma_i><sigma_j>`` for the canonical edge
    in ``edge_pairs[e]``.  ``link_strength[e]`` must equal its Frobenius norm.
    Distances, embedding, and Laplacian are explicit derived-model values;
    they are not physical spacetime coordinates or a computation of LQG.
    """

    revision: int
    time: float
    quantum_revision: int
    node_ids: tuple[str, ...]
    edge_pairs: tuple[tuple[int, int], ...]
    connected_correlation_tensors: Array
    link_strength: Array
    adjacency: Array
    distances: Array
    vertices: Array
    face_area: Array
    volume: float
    laplacian: Array
    eigenvalues: Array
    eigenvectors: Array
    embedding_valid: bool
    diagnostics: tuple[str, ...] = ()
    provenance: str = "derived_connected_pauli_correlation_relational_geometry_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "quantum_revision", _revision(self.quantum_revision, name="quantum_revision"))
        object.__setattr__(self, "node_ids", _node_ids(self.node_ids))
        pairs = tuple((int(left), int(right)) for left, right in self.edge_pairs)
        if pairs != RELATIONAL_EDGE_PAIRS:
            raise ValueError("edge_pairs must use canonical ordered four-qubit pairs.")
        tensors = _readonly(self.connected_correlation_tensors, dtype=float)
        strength = _readonly(self.link_strength, dtype=float)
        adjacency = _readonly(self.adjacency, dtype=float)
        distances = _readonly(self.distances, dtype=float)
        vertices = _readonly(self.vertices, dtype=float)
        areas = _readonly(self.face_area, dtype=float)
        laplacian = _readonly(self.laplacian, dtype=float)
        values = _readonly(self.eigenvalues, dtype=float)
        vectors = _readonly(self.eigenvectors, dtype=float)
        if tensors.shape != (len(pairs), 3, 3) or strength.shape != (len(pairs),):
            raise ValueError("connected correlations require six 3x3 tensors and six strengths.")
        if adjacency.shape != (QUBIT_COUNT, QUBIT_COUNT) or distances.shape != adjacency.shape or laplacian.shape != adjacency.shape:
            raise ValueError("adjacency, distances, and Laplacian must be 4x4 matrices.")
        if vertices.shape != (QUBIT_COUNT, 3) or areas.shape != (QUBIT_COUNT,):
            raise ValueError("vertices must be 4x3 and face_area must have four entries.")
        if values.shape != (QUBIT_COUNT,) or vectors.shape != (QUBIT_COUNT, QUBIT_COUNT):
            raise ValueError("the four-node Laplacian requires four eigenvalues and a 4x4 eigenvector matrix.")
        if not all(np.all(np.isfinite(item)) for item in (tensors, strength, adjacency, distances, vertices, areas, laplacian, values, vectors)):
            raise ValueError("relational geometry values must be finite.")
        if np.any(strength < 0.0) or not np.allclose(strength, np.linalg.norm(tensors, axis=(1, 2)), atol=1.0e-10, rtol=1.0e-10):
            raise ValueError("link_strength must be the connected-correlation Frobenius norm.")
        if not np.allclose(adjacency, adjacency.T, atol=_EPS, rtol=0.0) or np.any(adjacency < 0.0) or not np.allclose(np.diag(adjacency), 0.0, atol=_EPS, rtol=0.0):
            raise ValueError("adjacency must be symmetric, nonnegative, and have zero diagonal.")
        if not np.allclose(distances, distances.T, atol=_EPS, rtol=0.0) or not np.allclose(np.diag(distances), 0.0, atol=_EPS, rtol=0.0) or np.any(distances[np.triu_indices(QUBIT_COUNT, 1)] <= 0.0):
            raise ValueError("distances must be symmetric with zero diagonal and positive edge lengths.")
        expected_laplacian = np.diag(np.sum(adjacency, axis=1)) - adjacency
        if not np.allclose(laplacian, expected_laplacian, atol=1.0e-10, rtol=1.0e-10):
            raise ValueError("laplacian must equal degree(adjacency) - adjacency.")
        if np.any(values < -1.0e-10) or np.any(np.diff(values) < -1.0e-10) or not np.allclose(laplacian @ vectors, vectors * values, atol=1.0e-8, rtol=1.0e-8):
            raise ValueError("eigenpairs must be ordered eigenpairs of the declared Laplacian.")
        volume = float(self.volume)
        if not math.isfinite(volume) or volume < 0.0 or np.any(areas < 0.0):
            raise ValueError("volume and face areas must be finite and nonnegative.")
        diagnostics = _diagnostics(self.diagnostics)
        if not bool(self.embedding_valid) and not diagnostics:
            raise ValueError("an invalid embedding must publish a diagnostic.")
        if self.embedding_valid:
            embedded_distances = np.linalg.norm(vertices[:, None, :] - vertices[None, :, :], axis=-1)
            if not np.allclose(embedded_distances, distances, atol=1.0e-8, rtol=1.0e-8):
                raise ValueError("valid vertices must realize the declared pairwise distances.")
        for name, value in (("connected_correlation_tensors", tensors), ("link_strength", strength), ("adjacency", adjacency), ("distances", distances), ("vertices", vertices), ("face_area", areas), ("laplacian", laplacian), ("eigenvalues", values), ("eigenvectors", vectors)):
            object.__setattr__(self, name, value)
        object.__setattr__(self, "edge_pairs", pairs)
        object.__setattr__(self, "volume", volume)
        object.__setattr__(self, "embedding_valid", bool(self.embedding_valid))
        object.__setattr__(self, "diagnostics", diagnostics)
        object.__setattr__(self, "provenance", _provenance(self.provenance))


@dataclass(frozen=True)
class GeometryBoundaryFrame:
    """A declared periodic contour and its 20-mode real boundary basis.

    The sampled contour belongs to the modeled relational geometry.  It never
    treats computational-basis indices as physical positions.
    """

    revision: int
    time: float
    geometry_revision: int
    mode_ids: tuple[str, ...]
    sample_parameter: Array
    contour_xyz: Array
    boundary_basis: Array
    basis_label: str
    orientation: str
    diagnostics: tuple[str, ...] = ()
    provenance: str = "derived_relational_geometry_boundary_basis_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "geometry_revision", _revision(self.geometry_revision, name="geometry_revision"))
        object.__setattr__(self, "mode_ids", _mode_ids(self.mode_ids))
        parameter = _readonly(self.sample_parameter, dtype=float)
        contour = _readonly(self.contour_xyz, dtype=float)
        basis = _readonly(self.boundary_basis, dtype=float)
        if parameter.ndim != 1 or parameter.size < 3 or contour.shape != (parameter.size, 3) or basis.shape != (parameter.size, MODE_COUNT):
            raise ValueError("boundary needs >=3 samples, Nx3 contour coordinates, and an Nx20 basis.")
        if not all(np.all(np.isfinite(item)) for item in (parameter, contour, basis)):
            raise ValueError("boundary values must be finite.")
        if np.any(np.diff(parameter) <= 0.0) or parameter[0] < 0.0 or parameter[-1] >= 1.0:
            raise ValueError("sample_parameter must be strictly increasing over the periodic interval [0, 1).")
        if not str(self.basis_label) or not str(self.orientation):
            raise ValueError("basis_label and orientation must be nonempty.")
        object.__setattr__(self, "sample_parameter", parameter)
        object.__setattr__(self, "contour_xyz", contour)
        object.__setattr__(self, "boundary_basis", basis)
        object.__setattr__(self, "diagnostics", _diagnostics(self.diagnostics))
        object.__setattr__(self, "provenance", _provenance(self.provenance))


@dataclass(frozen=True)
class TuningGeometryFrame:
    """One derived, geometry-tied modal tuning transaction.

    ``frequency_hz`` is the only pitch source V3 downstream resonance and IR
    adapters may use.  An optional Scala/Wilson equilibrium is represented by
    explicit diagnostics; it never silently overwrites the derived spectrum.
    """

    revision: int
    time: float
    geometry_revision: int
    mode_ids: tuple[str, ...]
    ratios: Array
    frequency_hz: Array
    reference_hz: float
    geometry_eigenvalues: Array
    geometry_ratios: Array | None = None
    equilibrium_label: str | None = None
    equilibrium_blend: float = 0.0
    equilibrium_ratios: Array | None = None
    spectrum_lift_label: str = "unspecified_geometry_spectrum_lift"
    diagnostics: tuple[str, ...] = ()
    provenance: str = "derived_geometry_tuning_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "geometry_revision", _revision(self.geometry_revision, name="geometry_revision"))
        object.__setattr__(self, "mode_ids", _mode_ids(self.mode_ids))
        reference = float(self.reference_hz)
        blend = float(self.equilibrium_blend)
        ratios = _readonly(self.ratios, dtype=float)
        frequencies = _readonly(self.frequency_hz, dtype=float)
        eigenvalues = _readonly(self.geometry_eigenvalues, dtype=float)
        geometry_ratios = ratios if self.geometry_ratios is None else _readonly(self.geometry_ratios, dtype=float)
        equilibrium_ratios = None if self.equilibrium_ratios is None else _readonly(self.equilibrium_ratios, dtype=float)
        if ratios.shape != (MODE_COUNT,) or frequencies.shape != (MODE_COUNT,) or geometry_ratios.shape != (MODE_COUNT,):
            raise ValueError("ratios, geometry_ratios, and frequency_hz must be finite 20-vectors.")
        if eigenvalues.ndim != 1 or eigenvalues.size == 0:
            raise ValueError("geometry_eigenvalues must be a nonempty finite vector.")
        if not all(np.all(np.isfinite(item)) for item in (ratios, geometry_ratios, frequencies, eigenvalues)):
            raise ValueError("tuning values must be finite.")
        if reference <= 0.0 or np.any(ratios <= 0.0) or np.any(geometry_ratios <= 0.0) or np.any(frequencies <= 0.0):
            raise ValueError("reference, ratios, geometry ratios, and frequencies must be positive.")
        if not math.isfinite(blend) or not 0.0 <= blend <= 1.0:
            raise ValueError("equilibrium_blend must lie in [0, 1].")
        if not np.allclose(frequencies, reference * ratios, atol=1.0e-9, rtol=1.0e-9):
            raise ValueError("frequency_hz must equal reference_hz * ratios.")
        if self.equilibrium_label is None:
            if blend != 0.0 or equilibrium_ratios is not None:
                raise ValueError("equilibrium label, ratios, and blend must be declared together.")
            if not np.allclose(ratios, geometry_ratios, atol=1.0e-10, rtol=1.0e-10):
                raise ValueError("without an equilibrium, ratios must equal geometry_ratios.")
        else:
            if equilibrium_ratios is None or equilibrium_ratios.shape != (MODE_COUNT,) or not np.all(np.isfinite(equilibrium_ratios)) or np.any(equilibrium_ratios <= 0.0):
                raise ValueError("a declared equilibrium requires positive finite 20-mode equilibrium_ratios.")
            expected = np.exp(((1.0 - blend) * np.log(geometry_ratios)) + (blend * np.log(equilibrium_ratios)))
            if not np.allclose(ratios, expected, atol=1.0e-10, rtol=1.0e-10):
                raise ValueError("equilibrium blending must be logarithmic between declared ratio sets.")
        if not str(self.spectrum_lift_label):
            raise ValueError("spectrum_lift_label must be nonempty.")
        object.__setattr__(self, "reference_hz", reference)
        object.__setattr__(self, "equilibrium_blend", blend)
        object.__setattr__(self, "ratios", ratios)
        object.__setattr__(self, "frequency_hz", frequencies)
        object.__setattr__(self, "geometry_eigenvalues", eigenvalues)
        object.__setattr__(self, "geometry_ratios", geometry_ratios)
        object.__setattr__(self, "equilibrium_ratios", equilibrium_ratios)
        object.__setattr__(self, "spectrum_lift_label", str(self.spectrum_lift_label))
        object.__setattr__(self, "diagnostics", _diagnostics(self.diagnostics))
        object.__setattr__(self, "provenance", _provenance(self.provenance))


@dataclass(frozen=True)
class ModalResonanceFrame:
    """Derived resonant-body parameters sharing the tuning frame's pitches."""

    revision: int
    time: float
    tuning_revision: int
    mode_ids: tuple[str, ...]
    frequency_hz: Array
    quality_factor: Array
    decay_seconds: Array
    phase_convention: str
    ir_peak_hz: Array
    mode_shape_weights: Array | None = None
    mode_shape_label: str = "unspecified_modal_shape_membership"
    diagnostics: tuple[str, ...] = ()
    provenance: str = "derived_modal_resonance_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "tuning_revision", _revision(self.tuning_revision, name="tuning_revision"))
        object.__setattr__(self, "mode_ids", _mode_ids(self.mode_ids))
        fields = {
            "frequency_hz": _readonly(self.frequency_hz, dtype=float),
            "quality_factor": _readonly(self.quality_factor, dtype=float),
            "decay_seconds": _readonly(self.decay_seconds, dtype=float),
            "ir_peak_hz": _readonly(self.ir_peak_hz, dtype=float),
        }
        default_shape = np.eye(QUBIT_COUNT, dtype=float)[np.arange(MODE_COUNT) // (MODE_COUNT // QUBIT_COUNT)]
        shape_weights = default_shape if self.mode_shape_weights is None else _readonly(self.mode_shape_weights, dtype=float)
        if any(value.shape != (MODE_COUNT,) or not np.all(np.isfinite(value)) for value in fields.values()):
            raise ValueError("modal resonance vectors must be finite 20-vectors.")
        if np.any(fields["frequency_hz"] <= 0.0) or np.any(fields["quality_factor"] <= 0.0) or np.any(fields["decay_seconds"] <= 0.0):
            raise ValueError("frequency, quality factor, and decay must be positive.")
        if not str(self.phase_convention):
            raise ValueError("phase_convention must be nonempty.")
        if shape_weights.shape != (MODE_COUNT, QUBIT_COUNT) or not np.all(np.isfinite(shape_weights)) or np.any(shape_weights < 0.0):
            raise ValueError("mode_shape_weights must be a finite nonnegative 20x4 descriptor matrix.")
        if not np.allclose(np.sum(shape_weights, axis=1), 1.0, atol=1.0e-10, rtol=1.0e-10):
            raise ValueError("every modal shape descriptor row must have unit membership weight.")
        if not str(self.mode_shape_label):
            raise ValueError("mode_shape_label must be nonempty.")
        if not np.allclose(fields["ir_peak_hz"], fields["frequency_hz"], atol=1.0e-9, rtol=1.0e-9):
            raise ValueError("IR peaks must use the exact modal frequencies.")
        for name, value in fields.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "mode_shape_weights", _readonly(shape_weights, dtype=float))
        object.__setattr__(self, "mode_shape_label", str(self.mode_shape_label))
        object.__setattr__(self, "diagnostics", _diagnostics(self.diagnostics))
        object.__setattr__(self, "provenance", _provenance(self.provenance))


@dataclass(frozen=True)
class RelationalSpectralControlFrame:
    """Bounded Laplacian controls for the downstream twenty-mode resonator.

    This is a read-only, perceptual control frame derived from a declared
    four-node relational graph. Its vectors are *not* a new tuning or a claim
    that the graph has twenty independent eigenfunctions: the 4 x 5 modal
    membership is the already-declared lift used by the V3 resonator.
    """

    revision: int
    time: float
    geometry_revision: int
    mode_ids: tuple[str, ...]
    bridge_strength: float
    segmentation: float
    global_connectivity: float
    relational_tension: float
    graph_band_energy: Array
    excitation_gain: Array
    decay_scale: Array
    brightness: Array
    graph_field_label: str
    diagnostics: tuple[str, ...] = ()
    provenance: str = "derived_read_only_relational_laplacian_resonance_control_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "geometry_revision", _revision(self.geometry_revision, name="geometry_revision"))
        object.__setattr__(self, "mode_ids", _mode_ids(self.mode_ids))
        scalars = {
            "bridge_strength": float(self.bridge_strength),
            "segmentation": float(self.segmentation),
            "global_connectivity": float(self.global_connectivity),
            "relational_tension": float(self.relational_tension),
        }
        bands = _readonly(self.graph_band_energy, dtype=float)
        excitation = _readonly(self.excitation_gain, dtype=float)
        decay = _readonly(self.decay_scale, dtype=float)
        brightness = _readonly(self.brightness, dtype=float)
        if not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in scalars.values()):
            raise ValueError("relational spectral scalar descriptors must lie in [0, 1].")
        if bands.shape != (QUBIT_COUNT - 1,) or not np.all(np.isfinite(bands)) or np.any(bands < 0.0):
            raise ValueError("graph_band_energy must be a finite nonnegative three-vector.")
        if float(np.sum(bands)) > 1.0 + 1.0e-10:
            raise ValueError("graph_band_energy must have total energy at most one.")
        if excitation.shape != (MODE_COUNT,) or decay.shape != (MODE_COUNT,) or brightness.shape != (MODE_COUNT,):
            raise ValueError("relational spectral modal controls must be 20-vectors.")
        if not all(np.all(np.isfinite(value)) for value in (excitation, decay, brightness)):
            raise ValueError("relational spectral modal controls must be finite.")
        if np.any(excitation <= 0.0) or np.any(decay <= 0.0) or np.any(brightness < 0.0) or np.any(brightness > 1.0):
            raise ValueError("excitation and decay must be positive; brightness must lie in [0, 1].")
        if not str(self.graph_field_label):
            raise ValueError("graph_field_label must be nonempty.")
        for name, value in scalars.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "graph_band_energy", bands)
        object.__setattr__(self, "excitation_gain", excitation)
        object.__setattr__(self, "decay_scale", decay)
        object.__setattr__(self, "brightness", brightness)
        object.__setattr__(self, "graph_field_label", str(self.graph_field_label))
        object.__setattr__(self, "diagnostics", _diagnostics(self.diagnostics))
        object.__setattr__(self, "provenance", _provenance(self.provenance))


@dataclass(frozen=True)
class AcousticFieldFrame:
    """A 20-mode complex resonant field, independent of speakers or channels.

    ``modal_coefficients`` contains the performer and derived flow contribution
    after their explicit combination.  It is not an array of output channels.
    """

    revision: int
    time: float
    resonance_revision: int
    mode_ids: tuple[str, ...]
    modal_coefficients: Array
    performer_gain: Array
    flow_excitation: Array
    field_basis_label: str
    performer_revision: int = 0
    flow_revision: int = 0
    relational_control_revision: int | None = None
    relational_excitation_gain: Array | None = None
    combination_label: str = "unspecified_performer_plus_flow_complex_field"
    diagnostics: tuple[str, ...] = ()
    provenance: str = "derived_geometry_resonant_field_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "resonance_revision", _revision(self.resonance_revision, name="resonance_revision"))
        object.__setattr__(self, "performer_revision", _revision(self.performer_revision, name="performer_revision"))
        object.__setattr__(self, "flow_revision", _revision(self.flow_revision, name="flow_revision"))
        if self.relational_control_revision is not None:
            object.__setattr__(self, "relational_control_revision", _revision(
                self.relational_control_revision, name="relational_control_revision"
            ))
        object.__setattr__(self, "mode_ids", _mode_ids(self.mode_ids))
        coefficients = _readonly(self.modal_coefficients, dtype=np.complex128)
        performer = _readonly(self.performer_gain, dtype=float)
        flow = _readonly(self.flow_excitation, dtype=np.complex128)
        relational_gain = (
            np.ones(MODE_COUNT, dtype=float)
            if self.relational_excitation_gain is None
            else _readonly(self.relational_excitation_gain, dtype=float)
        )
        if coefficients.shape != (MODE_COUNT,) or performer.shape != (MODE_COUNT,) or flow.shape != (MODE_COUNT,):
            raise ValueError("field vectors must contain exactly 20 modes.")
        if not np.all(np.isfinite(coefficients)) or not np.all(np.isfinite(performer)) or not np.all(np.isfinite(flow)):
            raise ValueError("field values must be finite.")
        if np.any(performer < 0.0):
            raise ValueError("performer_gain must be nonnegative.")
        if relational_gain.shape != (MODE_COUNT,) or not np.all(np.isfinite(relational_gain)) or np.any(relational_gain <= 0.0):
            raise ValueError("relational_excitation_gain must be a positive finite 20-vector.")
        if self.relational_control_revision is None and self.relational_excitation_gain is not None:
            raise ValueError("relational_excitation_gain requires relational_control_revision.")
        if not str(self.field_basis_label):
            raise ValueError("field_basis_label must be nonempty.")
        if not str(self.combination_label):
            raise ValueError("combination_label must be nonempty.")
        object.__setattr__(self, "modal_coefficients", coefficients)
        object.__setattr__(self, "performer_gain", performer)
        object.__setattr__(self, "flow_excitation", flow)
        object.__setattr__(self, "relational_excitation_gain", relational_gain)
        object.__setattr__(self, "combination_label", str(self.combination_label))
        object.__setattr__(self, "diagnostics", _diagnostics(self.diagnostics))
        object.__setattr__(self, "provenance", _provenance(self.provenance))


@dataclass(frozen=True)
class StereoObservationFrame:
    """A virtual even/odd receiver observation of one :class:`AcousticFieldFrame`.

    Complex values retain the control-rate field phase.  A real-time adapter
    decides how to render an evolving sequence of frames to samples; this
    frame never presumes a speaker layout or pans individual modes.
    """

    revision: int
    time: float
    field_revision: int
    receiver_label: str
    mid: complex
    side: complex
    left: complex
    right: complex
    interchannel_correlation: float
    width: float
    provenance: str = "derived_virtual_mid_side_stereo_observer_v3"

    def __post_init__(self) -> None:
        object.__setattr__(self, "revision", _revision(self.revision, name="revision"))
        object.__setattr__(self, "time", _time(self.time))
        object.__setattr__(self, "field_revision", _revision(self.field_revision, name="field_revision"))
        values = tuple(complex(item) for item in (self.mid, self.side, self.left, self.right))
        if not all(math.isfinite(value.real) and math.isfinite(value.imag) for value in values):
            raise ValueError("stereo receiver values must be finite complex values.")
        correlation, width = float(self.interchannel_correlation), float(self.width)
        if not math.isfinite(correlation) or not -1.0 <= correlation <= 1.0:
            raise ValueError("interchannel_correlation must lie in [-1, 1].")
        if not math.isfinite(width) or not 0.0 <= width <= 1.0:
            raise ValueError("width must lie in [0, 1].")
        if not str(self.receiver_label):
            raise ValueError("receiver_label must be nonempty.")
        if abs(values[2] - (values[0] + values[1])) > _EPS or abs(values[3] - (values[0] - values[1])) > _EPS:
            raise ValueError("left/right must be the declared M/S reconstruction.")
        object.__setattr__(self, "mid", values[0])
        object.__setattr__(self, "side", values[1])
        object.__setattr__(self, "left", values[2])
        object.__setattr__(self, "right", values[3])
        object.__setattr__(self, "interchannel_correlation", correlation)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "provenance", _provenance(self.provenance))


__all__ = [
    "AcousticFieldFrame", "Array", "DEFAULT_MODE_IDS", "GeometryBoundaryFrame",
    "MODE_COUNT", "ModalResonanceFrame", "QUBIT_COUNT", "RELATIONAL_EDGE_PAIRS",
    "RelationalSpectralControlFrame",
    "RelationalGeometryFrame", "StereoObservationFrame", "TuningGeometryFrame",
]
