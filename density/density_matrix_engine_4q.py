from __future__ import annotations
from dataclasses import dataclass, replace
import queue
import numpy as np
from sklearn import metrics

from excitation.base import QuantumSource
from excitation.born_transition import BornTransitionEngine
from excitation.hydrogen_orbital_v3 import HydrogenOrbitalSource
from excitation.hydrogen_spectrum import HydrogenSpectrumSource
from excitation.schrodinger_packet import SchrodingerPacketSource
from density.grw_event_channel_v1 import (
    GRWConfig,
    GRWEvent,
    GRWEventChannel,
    strength_to_width,
)
from density.measurement_instrument_v1 import (
    MeasurementEvent,
    ProjectiveMeasurementInstrument,
)
from density.durable_state_publication_v1 import (
    DurableStatePublisher,
    StatePublicationConfig,
)
from density.open_system_trajectory_v1 import (
    OpenSystemTrajectoryInstrument,
    amplitude_damping_kraus,
    dephasing_kraus,
    depolarizing_kraus,
)
from guidance.live_bohm_guidance_v1 import (
    BohmEventFamily,
    BohmGuidanceConfig,
    LiveBohmGuidance,
)
from guidance.four_qubit_configuration_guidance_v1 import current_matrix
from hamiltonian.hamiltonian_state import HamiltonianState
from hamiltonian.hamiltonian_translator_v1 import HamiltonianTranslator
from qmw_circuit_bridge import PilotFrame, QMWCircuitBridge
from qmw_temporal_crystal16_v1 import LiveTemporalLayer16


@dataclass
class GuidanceVector:
    node: int
    target_node: int
    momentum: float
    phase_force: float
    diffusion: float

    def pilot_to_population_guidance(pilot: PilotFrame, purity_value: float, coherence_value: float) -> GuidanceVector:
        """Convert state-graph dynamics into musically stable population guidance.

        This is deliberately low-noise. The pilot current supplies direction;
        entropy supplies controlled spread; purity/coherence determine focus.
        """
        focus = float(np.clip(0.55 * purity_value + 0.45 * min(1.0, coherence_value / 4.0), 0.0, 1.0))
        return GuidanceVector(
            node=pilot.node,
            target_node=pilot.next_node,
            momentum=float(np.clip(abs(pilot.current) + pilot.velocity, 0.0, 1.0)),
            phase_force=float(np.clip(pilot.phase_gradient, -1.0, 1.0)),
            diffusion=float(np.clip((pilot.branch_entropy / 4.0) * (1.0 - focus), 0.0, 1.0)),
        )


class CircuitEnabledPopulationMixin:
    """Mixin skeleton: adapt member field names to your Quantum Population v5."""

    def initialise_circuit_layer(self) -> None:
        self.qmw_bridge = QMWCircuitBridge(
            n_qubits=4,
            n_steps=16,
            active_length=16,
            osc_out_port=7400,      # Max receives here
            osc_control_port=7403,  # Circuit GUI sends edits here
            circuit_interval_seconds=0.50,
        )
        self.qmw_bridge.start_control_server()
        self.pilot = {}

    def circuit_step(self, dt: float) -> GuidanceVector:
        # 1. Discrete top-layer intervention.
        self.rho, column, labels = self.qmw_bridge.apply_due_circuit_column(self.rho, dt)

        # 2. Your existing continuous density evolution goes here.
        self.rho = self.apply_lindblad_step(self.rho, dt)

        # 3. Derive guidance and broadcast all quantum / pilot OSC data.
        pilot = self.qmw_bridge.update_and_send(
            self.rho, self.hamiltonian, dt, column, labels
        )
        rho_purity = float(np.trace(self.rho @ self.rho).real)
        rho_coherence = float(np.sum(np.abs(self.rho - np.diag(np.diag(self.rho)))))
        return pilot_to_population_guidance(pilot, rho_purity, rho_coherence)

    def guide_member(self, member, guidance: GuidanceVector, noise_amount: float = 0.03) -> None:
        """Project deterministic configuration guidance into renderer space.

        Assumes your members have position/velocity numpy vectors. Adapt the
        field names and parameter dimensions to your actual v5 data structure.
        ``noise_amount`` remains accepted for API compatibility but noise is a
        renderer concern and no longer changes the guidance path.
        """
        dim = len(member.position)
        node_bits = np.array([(guidance.node >> shift) & 1 for shift in range(3, -1, -1)], dtype=float)
        target_bits = np.array([(guidance.target_node >> shift) & 1 for shift in range(3, -1, -1)], dtype=float)
        # Fold four configuration bits into any parameter-vector dimension.
        desired = np.resize(2.0 * target_bits - 1.0, dim)
        current = np.resize(2.0 * node_bits - 1.0, dim)
        direction = desired - current
        norm = np.linalg.norm(direction)
        if norm > 1e-12:
            direction /= norm

        member.velocity = (
            0.70 * member.velocity
            + 0.24 * guidance.momentum * direction
            + 0.10 * guidance.phase_force * np.roll(direction, 1)
        )
        member.position = member.position + member.velocity





# ------------------------------------------------------------
# SINGLE-QUBIT OPERATORS
# ------------------------------------------------------------

I2 = np.array(
    [[1, 0],
     [0, 1]],
    dtype=np.complex128,
)

X = np.array(
    [[0, 1],
     [1, 0]],
    dtype=np.complex128,
)

Y = np.array(
    [[0, -1j],
     [1j, 0]],
    dtype=np.complex128,
)

Z = np.array(
    [[1, 0],
     [0, -1]],
    dtype=np.complex128,
)


NUM_QUBITS = 4
DIMENSION = 2 ** NUM_QUBITS


# ------------------------------------------------------------
# LINEAR-ALGEBRA HELPERS
# ------------------------------------------------------------

def normalize_density(rho):
    rho = np.asarray(rho, dtype=np.complex128)
    rho = 0.5 * (rho + rho.conj().T)

    trace = np.trace(rho)

    if abs(trace) > 1e-12:
        rho = rho / trace

    return rho


def state_to_density(psi):
    psi = np.asarray(psi, dtype=np.complex128)
    psi = psi / np.linalg.norm(psi)
    return np.outer(psi, psi.conj())


def tensor_operator(operator_map):
    """
    Example:
        tensor_operator({0: X, 2: Z})

    produces:
        X ⊗ I ⊗ Z ⊗ I
    """
    result = np.array([[1]], dtype=np.complex128)

    for qubit in range(NUM_QUBITS):
        result = np.kron(
            result,
            operator_map.get(qubit, I2),
        )

    return result


_LOCAL_PAULI_CACHE = {}
_PAIR_PAULI_CACHE = {}


def _pauli_name(operator):
    """Return a stable cache key only for immutable module Pauli constants."""
    if operator is X:
        return "X"
    if operator is Y:
        return "Y"
    if operator is Z:
        return "Z"
    if operator is I2:
        return "I"
    return None


def local_operator(qubit, operator):
    name = _pauli_name(operator)
    if name is not None:
        key = (int(qubit), name)
        cached = _LOCAL_PAULI_CACHE.get(key)
        if cached is None:
            cached = tensor_operator({qubit: operator})
            _LOCAL_PAULI_CACHE[key] = cached
        return cached
    return tensor_operator({qubit: operator})


def pair_operator(qubit_a, operator_a, qubit_b, operator_b):
    name_a = _pauli_name(operator_a)
    name_b = _pauli_name(operator_b)
    if name_a is not None and name_b is not None:
        key = (int(qubit_a), name_a, int(qubit_b), name_b)
        cached = _PAIR_PAULI_CACHE.get(key)
        if cached is None:
            cached = tensor_operator(
                {
                    qubit_a: operator_a,
                    qubit_b: operator_b,
                }
            )
            _PAIR_PAULI_CACHE[key] = cached
        return cached
    return tensor_operator(
        {
            qubit_a: operator_a,
            qubit_b: operator_b,
        }
    )


def partial_trace_keep(rho, keep_qubits):
    """
    Reduce a 4-qubit density matrix to the requested subsystem.
    """
    rho = normalize_density(rho)

    keep_qubits = sorted(set(keep_qubits))

    if not keep_qubits:
        raise ValueError("keep_qubits cannot be empty.")

    if any(q < 0 or q >= NUM_QUBITS for q in keep_qubits):
        raise ValueError(f"Invalid qubits: {keep_qubits}")

    tensor = rho.reshape([2] * (2 * NUM_QUBITS))

    row_labels = list(range(NUM_QUBITS))
    col_labels = []

    for qubit in range(NUM_QUBITS):
        if qubit in keep_qubits:
            col_labels.append(NUM_QUBITS + qubit)
        else:
            col_labels.append(qubit)

    output_labels = keep_qubits + [
        NUM_QUBITS + qubit
        for qubit in keep_qubits
    ]

    reduced = np.einsum(
        tensor,
        row_labels + col_labels,
        output_labels,
    )

    reduced_dim = 2 ** len(keep_qubits)

    return reduced.reshape(reduced_dim, reduced_dim)


def bloch_vector(rho_single):
    rho_single = normalize_density(rho_single)

    return np.array(
        [
            float(np.real(np.trace(rho_single @ X))),
            float(np.real(np.trace(rho_single @ Y))),
            float(np.real(np.trace(rho_single @ Z))),
        ],
        dtype=float,
    )


def purity(rho):
    rho = normalize_density(rho)
    return float(np.clip(np.real(np.trace(rho @ rho)), 0.0, 1.0))


def von_neumann_entropy(rho):
    rho = normalize_density(rho)

    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = np.clip(np.real(eigenvalues), 0.0, 1.0)

    nonzero = eigenvalues[eigenvalues > 1e-12]

    if len(nonzero) == 0:
        return 0.0

    return float(-np.sum(nonzero * np.log2(nonzero)))


def l1_coherence(rho):
    rho = normalize_density(rho)
    return float(np.sum(np.abs(rho - np.diag(np.diag(rho)))))


# ------------------------------------------------------------
# GENERIC LOCAL NOISE
# ------------------------------------------------------------

def apply_kraus_channel(rho, kraus_ops, qubit):
    result = np.zeros_like(rho, dtype=np.complex128)

    for kraus in kraus_ops:
        full_kraus = local_operator(qubit, kraus)
        result += full_kraus @ rho @ full_kraus.conj().T

    return normalize_density(result)


def dephasing_channel(rho, amount, qubit):
    amount = float(np.clip(amount, 0.0, 1.0))

    k0 = np.sqrt(1.0 - amount) * I2
    k1 = np.sqrt(amount) * Z

    return apply_kraus_channel(rho, [k0, k1], qubit)


def amplitude_damping_channel(rho, gamma, qubit):
    gamma = float(np.clip(gamma, 0.0, 1.0))

    k0 = np.array(
        [[1.0, 0.0],
         [0.0, np.sqrt(1.0 - gamma)]],
        dtype=np.complex128,
    )

    k1 = np.array(
        [[0.0, np.sqrt(gamma)],
         [0.0, 0.0]],
        dtype=np.complex128,
    )

    return apply_kraus_channel(rho, [k0, k1], qubit)


def depolarizing_channel(rho, probability, qubit):
    probability = float(np.clip(probability, 0.0, 1.0))

    k0 = np.sqrt(1.0 - probability) * I2
    scale = np.sqrt(probability / 3.0)

    return apply_kraus_channel(
        rho,
        [
            k0,
            scale * X,
            scale * Y,
            scale * Z,
        ],
        qubit,
    )


# ------------------------------------------------------------
# FOUR-QUBIT RECURSIVE DENSITY-MATRIX ENGINE
# ------------------------------------------------------------

class DensityMatrixEngine:
    
    def __init__(
        self,
        excitation_source: str = "internal",
        osc_telemetry_hz: float | None = None,
        enable_circuit_bridge_control: bool = True,
        verbose: bool = False,
        born_species: str = "H-1",
        born_selection_mode: str = "sequential",
        born_time_scale: float = 100_000_000.0,
        born_duration_min_ms: float = 80.0,
        born_duration_max_ms: float = 2_000.0,
        grw_config: GRWConfig | None = None,
        measurement_seed: int = 29,
        state_publication: StatePublicationConfig | None = None,
        bohm_config: BohmGuidanceConfig | None = None,
        temporal_layer: LiveTemporalLayer16 | None = None,
    ):
        self.rng = np.random.default_rng()
        self.verbose = bool(verbose)

        self.params = {
        # Noise
        "dephase": 0.003,
        "damping": 0.001,
        "depolarize": 0.0005,

        # Base fields
        "x0": 0.35,
        "y0": 0.10,
        "z0": 0.20,

        "x1": 0.20,
        "y1": -0.15,
        "z1": 0.30,

        "x2": -0.18,
        "y2": 0.24,
        "z2": -0.12,

        "x3": 0.12,
        "y3": 0.30,
        "z3": 0.08,

        # Main dynamics
        "coupling": 0.70,
        "drift": 0.05,
        "feedback": 0.35,
        "freeze": 0.0,
        "drive": 1.35,

        # Feedback architecture
        "fb_x_neighbor_diff": 0.70,
        "fb_x_coherence": 0.25,

        "fb_y_neighbor_sum": 0.60,
        "fb_y_entropy": 0.25,

        "fb_z_neighbor_diff": 0.55,
        "fb_z_purity": 0.20,

        # Pair structure
        "pair_coherence_gain": 0.55,
        "pair_entropy_gain": 0.30,
        "pair_xx_ratio": 0.28,
        "pair_yy_ratio": 0.18,
        "diagonal_pair_ratio": 0.45,

        # External quantum-source drive.
        "excitation_drive": 0.35,
    }

        self.base_fields = np.array(
        [
            [
                self.params["x0"],
                self.params["y0"],
                self.params["z0"],
            ],
            [
                self.params["x1"],
                self.params["y1"],
                self.params["z1"],
            ],
            [
                self.params["x2"],
                self.params["y2"],
                self.params["z2"],
            ],
            [
                self.params["x3"],
                self.params["y3"],
                self.params["z3"],
            ],
        ],
        dtype=float,
    )

        self.drift_state = np.zeros(
            (NUM_QUBITS, 3),
            dtype=float,
        )

        self.pair_drift = {
            "01": 0.0,
            "12": 0.0,
            "23": 0.0,
            "30": 0.0,
            "02": 0.0,
            "13": 0.0,
        }

        self.dephase = self.params["dephase"]
        self.damping = self.params["damping"]
        self.depolarize = self.params["depolarize"]

        self.coupling_strength = self.params["coupling"]
        self.drift_amount = self.params["drift"]
        self.feedback = self.params["feedback"]

        self.freeze = bool(self.params["freeze"])
        self.excitation_drive = self.params["excitation_drive"]
        self.translator = HamiltonianTranslator()
        self.hamiltonian_state = HamiltonianState(x=0.0, y=0.0, z=1.0)
        self.excitation_source_kind = "internal"
        self.excitation_source: QuantumSource | None = None
        self.source_descriptor = None
        self.born_config = {
            "species": str(born_species),
            "selection_mode": str(born_selection_mode),
            "time_scale": float(born_time_scale),
            "minimum_duration_seconds": float(born_duration_min_ms) * 0.001,
            "maximum_duration_seconds": float(born_duration_max_ms) * 0.001,
        }
        self.set_excitation_source(excitation_source)

        # One canonical state history. The GRW channel schedules and describes
        # transitions, while this engine remains the sole owner of self.rho.
        self.state_revision = -1
        self.configuration_revision = 0
        self.logical_time = 0.0
        self.last_event_id = 0
        self.last_event_type = "reset"
        self.temporal_layer = temporal_layer
        self.last_temporal_frame = None
        self.bohm = LiveBohmGuidance(bohm_config or BohmGuidanceConfig())
        self.environment_trajectory = OpenSystemTrajectoryInstrument(
            seed=self.bohm.config.environment_seed,
            n_qubits=NUM_QUBITS,
        )
        self.environment_events = []
        self._bohm_event_publish_cursor = 0
        self.grw = GRWEventChannel(grw_config or GRWConfig())
        self.grw_events: list[GRWEvent] = []
        self.last_grw_event: GRWEvent | None = None
        self.measurement = ProjectiveMeasurementInstrument(seed=measurement_seed)
        self.last_measurement_event: MeasurementEvent | None = None
        self.measurement_requests: queue.SimpleQueue[tuple] = queue.SimpleQueue()
        self.state_publisher = (
            DurableStatePublisher(state_publication)
            if state_publication is not None
            else None
        )

        self.reset_state()

        # Interactive circuit-builder / pilot-wave bridge
        self.qmw_bridge = QMWCircuitBridge(
            n_qubits=4,
            n_steps=16,
            active_length=16,
            osc_out_port=7400,
            osc_control_port=7403,
            circuit_interval_seconds=1.0,
            osc_telemetry_hz=osc_telemetry_hz,
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/grw/enabled", self._osc_grw_enabled
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/grw/rate_hz", self._osc_grw_rate_hz
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/grw/strength", self._osc_grw_strength
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/grw/width", self._osc_grw_width
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/grw/basis", self._osc_grw_basis
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/grw/seed", self._osc_grw_seed
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/state/control/measure", self._osc_measure
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/measurement/request", self._osc_measure
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/bohm/enabled", self._osc_bohm_enabled
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/bohm/environment/enabled",
            self._osc_bohm_environment_enabled,
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/bohm/gate_duration", self._osc_bohm_gate_duration
        )
        self.qmw_bridge.add_control_handler(
            "/quantum/bohm/gate_microsteps", self._osc_bohm_gate_microsteps
        )

        if enable_circuit_bridge_control:
            self.qmw_bridge.start_control_server()

        # Latest graph-guidance frame
        self.pilot = None

        # Latched circuit-event state for Max
        self.last_gate_column = -1
        self.last_gate_delta_rho = 0.0
        self.gate_energy = 0.0
        self.gate_event_count = 0
        self.previous_qubit_entropy = np.zeros(NUM_QUBITS, dtype=float)


    def set_param(self, name, value):
        if name not in self.params:
            print(f"Unknown engine parameter: {name}")
            return

        value = float(value)
        self.params[name] = value

        if name == "dephase":
            self.dephase = value

        elif name == "damping":
            self.damping = value

        elif name == "depolarize":
            self.depolarize = value

        elif name == "coupling":
            self.coupling_strength = value

        elif name == "drift":
            self.drift_amount = value

        elif name == "feedback":
            self.feedback = value

        elif name == "freeze":
            self.freeze = bool(value)

        elif name == "excitation_drive":
            self.excitation_drive = value

        elif (
            len(name) == 2
            and name[0] in ("x", "y", "z")
            and name[1] in ("0", "1", "2", "3")
        ):
            axis_index = {"x": 0, "y": 1, "z": 2}[name[0]]
            qubit = int(name[1])

            self.base_fields[qubit, axis_index] = value

    def set_excitation_source(self, source: str) -> None:
        source = str(source).strip().lower()
        if source in ("", "none", "off", "internal"):
            self.excitation_source_kind = "internal"
            self.excitation_source = None
            self.source_descriptor = None
            self._apply_excitation_mode_profile("internal")
            return

        if source in ("hydrogen", "hydrogen_spectrum", "spectrum"):
            self.excitation_source = HydrogenSpectrumSource()
            canonical_source = "hydrogen_spectrum"
        elif source in ("born", "born_transition", "born_transition_engine"):
            self.excitation_source = BornTransitionEngine(
                **getattr(self, "born_config", {})
            )
            canonical_source = "born_transition"
        elif source in ("hydrogen_orbital", "orbital"):
            self.excitation_source = HydrogenOrbitalSource(n=2, l=1, m=0)
            canonical_source = "hydrogen_orbital"
        elif source in ("schrodinger", "schrodinger_packet", "packet", "wavepacket"):
            self.excitation_source = SchrodingerPacketSource()
            canonical_source = "schrodinger_packet"
        elif source in ("schrodinger_interference", "interference"):
            self.excitation_source = SchrodingerPacketSource(
                initial_center=0.0,
                initial_width=0.72,
                initial_momentum=3.4,
                interference=True,
            )
            canonical_source = "schrodinger_interference"
        else:
            raise ValueError(
                "Unknown excitation source. Use internal, born_transition, "
                "hydrogen_spectrum, hydrogen_orbital, schrodinger_packet, or "
                "schrodinger_interference."
            )

        self.excitation_source_kind = canonical_source
        self.source_descriptor = self.excitation_source.descriptor
        self._apply_excitation_mode_profile(canonical_source)

    def _apply_excitation_mode_profile(self, source: str) -> None:
        """Give each excitation family a distinct but bounded dynamic regime.

        The excitation descriptors already differ mathematically, but a single
        conservative drive/coupling profile made those differences converge
        perceptually after the shared four-resonator mapping. These profiles
        preserve the same density engine and OSC protocol while emphasizing
        each source's characteristic temporal behavior.
        """
        profiles = {
            # Neutral reference: the original recursive engine settings.
            "internal": {
                "excitation_drive": 0.0,
                "coupling": 0.70,
                "drift": 0.05,
                "feedback": 0.35,
            },
            # Discrete, event-centred gestures with less recursive smearing.
            "born_transition": {
                "excitation_drive": 1.65,
                "coupling": 0.34,
                "drift": 0.012,
                "feedback": 0.16,
            },
            # Ordered spectral stepping with moderate inter-qubit propagation.
            "hydrogen_spectrum": {
                "excitation_drive": 1.15,
                "coupling": 0.52,
                "drift": 0.025,
                "feedback": 0.24,
            },
            # Stable orbital circulation: coherent, coupled, and low-drift.
            "hydrogen_orbital": {
                "excitation_drive": 0.82,
                "coupling": 0.88,
                "drift": 0.008,
                "feedback": 0.46,
            },
            # Traveling packet: stronger directional motion with moderate drift.
            "schrodinger_packet": {
                "excitation_drive": 1.35,
                "coupling": 0.44,
                "drift": 0.11,
                "feedback": 0.27,
            },
            # Interference: strongest relational drive and animated feedback.
            "schrodinger_interference": {
                "excitation_drive": 1.85,
                "coupling": 0.94,
                "drift": 0.17,
                "feedback": 0.56,
            },
        }
        profile = profiles[source]
        # Some lightweight tests and migration utilities call
        # set_excitation_source() on a partially constructed engine.
        if not hasattr(self, "params"):
            return
        for name, value in profile.items():
            self.params[name] = float(value)
        self.excitation_drive = self.params["excitation_drive"]
        self.coupling_strength = self.params["coupling"]
        self.drift_amount = self.params["drift"]
        self.feedback = self.params["feedback"]

    def set_born_species(self, species: str) -> None:
        """Select an isotope preset and restart the Born transition source."""
        config = dict(getattr(self, "born_config", {}))
        config["species"] = str(species)
        replacement = BornTransitionEngine(**config)
        self.born_config = config
        self.excitation_source = replacement
        self.excitation_source_kind = "born_transition"
        self.source_descriptor = replacement.descriptor

    def update_excitation_source(self, dt: float) -> None:
        if self.excitation_source is None:
            self.source_descriptor = None
            return

        self.excitation_source.step(dt)
        descriptor = self.excitation_source.descriptor
        self.source_descriptor = descriptor
        self.hamiltonian_state = self.translator.translate(
            self.hamiltonian_state,
            descriptor,
        )

    def reset_state(self):
        """
        Four-qubit coherent seed.

        The state occupies multiple computational-basis regions,
        giving all four qubits genuine local and relational dynamics.
        """
        psi = np.zeros(DIMENSION, dtype=np.complex128)

        psi[0] = 0.42
        psi[3] = 0.20j
        psi[5] = 0.31
        psi[6] = -0.18j
        psi[9] = 0.24j
        psi[10] = 0.34
        psi[12] = -0.27
        psi[15] = 0.48j

        self.rho = state_to_density(psi)
        self.state_revision += 1
        self.bohm.reset(self.rho, logical_time=self.logical_time)
        self.configuration_revision = self.bohm.configuration_revision
        self.last_event_type = "reset"
        self._persist_transition(
            event_type="reset",
            rho_after=self.rho,
            event_id=0,
            metadata={"source": "DensityMatrixEngine.reset_state"},
            rho_before=self.rho,
            delta_rho=np.zeros_like(self.rho),
        )

        self.drift_state[:] = 0.0

        for key in self.pair_drift:
            self.pair_drift[key] = 0.0

        if self.verbose:
            print("Four-qubit density matrix reset to active entangled state.")

    def update_drift(self):
        decay = 0.985
        innovation = 0.08 * self.drift_amount

        self.drift_state = (
            decay * self.drift_state
            + self.rng.normal(
                0.0,
                innovation,
                size=(NUM_QUBITS, 3),
            )
        )

        self.drift_state = np.clip(
            self.drift_state,
            -1.0,
            1.0,
        )

        for key in self.pair_drift:
            value = (
                decay * self.pair_drift[key]
                + self.rng.normal(0.0, innovation)
            )

            self.pair_drift[key] = float(
                np.clip(value, -1.0, 1.0)
            )

    def local_bloch_vectors(self, rho=None):
        state = self.rho if rho is None else rho
        vectors = []

        for qubit in range(NUM_QUBITS):
            reduced = partial_trace_keep(
                state,
                [qubit],
            )
            vectors.append(bloch_vector(reduced))

        return np.asarray(vectors, dtype=float)
    
    

    def hamiltonian(self):
        local_bloch = self.local_bloch_vectors()

        global_entropy = von_neumann_entropy(self.rho) / NUM_QUBITS
        global_purity = purity(self.rho)
        global_coherence = l1_coherence(self.rho) / (DIMENSION - 1)

        hamiltonian = np.zeros(
            (DIMENSION, DIMENSION),
            dtype=np.complex128,
        )

        drive = 1.35
        source_x = self.excitation_drive * self.hamiltonian_state.x
        source_y = self.excitation_drive * self.hamiltonian_state.y
        source_z = self.excitation_drive * self.hamiltonian_state.z

        for qubit in range(NUM_QUBITS):
            previous = (qubit - 1) % NUM_QUBITS
            following = (qubit + 1) % NUM_QUBITS

            bx_prev, by_prev, bz_prev = local_bloch[previous]
            bx_next, by_next, bz_next = local_bloch[following]

            x_field = (
                self.base_fields[qubit, 0]
                + source_x
                + self.drift_state[qubit, 0]
                + self.feedback * 0.70 * (by_prev - by_next)
                + self.feedback * 0.25 * global_coherence
            )

            y_field = (
                self.base_fields[qubit, 1]
                + source_y
                + self.drift_state[qubit, 1]
                + self.feedback * 0.60 * (bz_prev + bz_next)
                - self.feedback * 0.25 * global_entropy
            )

            z_field = (
                self.base_fields[qubit, 2]
                + source_z
                + self.drift_state[qubit, 2]
                + self.feedback * 0.55 * (bx_prev - bx_next)
                + self.feedback * 0.20 * global_purity
            )

            hamiltonian += drive * x_field * local_operator(qubit, X)
            hamiltonian += drive * y_field * local_operator(qubit, Y)
            hamiltonian += drive * z_field * local_operator(qubit, Z)

        pair_terms = [
            (0, 1, "01"),
            (1, 2, "12"),
            (2, 3, "23"),
            (3, 0, "30"),
            (0, 2, "02"),
            (1, 3, "13"),
        ]

        for qubit_a, qubit_b, key in pair_terms:
            local_gain = (
                self.coupling_strength
                + 0.35 * self.pair_drift[key]
                + self.feedback * 0.55 * global_coherence
                - self.feedback * 0.30 * global_entropy
            )

            if key in ("02", "13"):
                local_gain *= 0.45

            hamiltonian += (
                local_gain
                * pair_operator(qubit_a, Z, qubit_b, Z)
            )

            hamiltonian += (
                0.28
                * local_gain
                * pair_operator(qubit_a, X, qubit_b, X)
            )

            hamiltonian += (
                0.18
                * local_gain
                * pair_operator(qubit_a, Y, qubit_b, Y)
            )

        return hamiltonian

    def unitary_step(self, hamiltonian, dt):
        self.rho = self.bohm.evolve_density(
            self.rho,
            hamiltonian,
            duration=float(dt),
            microsteps=self.bohm.config.hamiltonian_microsteps,
            family=BohmEventFamily.HAMILTONIAN_CURRENT,
            logical_time_start=self.logical_time,
            timeline_duration=float(dt),
        )
        self.configuration_revision = self.bohm.configuration_revision
        self.state_revision += 1
        self._persist_state(
            event_type="unitary_evolution",
            metadata={"duration": float(dt)},
        )

    @staticmethod
    def evolve_density(rho, hamiltonian, dt):
        """Pure density evolution used to split frames at exact GRW times."""
        eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
        unitary = (
            eigenvectors
            @ np.diag(np.exp(-1j * eigenvalues * dt))
            @ eigenvectors.conj().T
        )
        return normalize_density(unitary @ rho @ unitary.conj().T)

    def apply_noise(self):
        """Apply the legacy unconditioned CPTP channel.

        Kept for callers that explicitly need ensemble evolution.  The live
        Bohm path uses ``apply_noise_trajectory`` when its opt-in control is on.
        """
        rho_before = self.rho.copy()
        dephase_scales = [1.00, 0.78, 0.58, 0.88]
        damping_scales = [0.45, 1.00, 0.65, 0.82]
        depolarize_scales = [1.00, 0.72, 0.55, 0.85]
        

        for qubit in range(NUM_QUBITS):
            self.rho = dephasing_channel(
                self.rho,
                self.dephase * dephase_scales[qubit],
                qubit,
            )

            self.rho = amplitude_damping_channel(
                self.rho,
                self.damping * damping_scales[qubit],
                qubit,
            )

            self.rho = depolarizing_channel(
                self.rho,
                self.depolarize * depolarize_scales[qubit],
                qubit,
            )
        self.state_revision += 1
        self._persist_transition(
            event_type="open_system_channel",
            rho_after=self.rho,
            event_id=self.last_event_id,
            metadata={
                "dephase": self.dephase,
                "damping": self.damping,
                "depolarize": self.depolarize,
            },
            rho_before=rho_before,
            delta_rho=self.rho - rho_before,
        )

    def apply_noise_trajectory(self):
        """Sample local Kraus branches and update rho plus actual configuration."""
        rho_before = self.rho.copy()
        dephase_scales = [1.00, 0.78, 0.58, 0.88]
        damping_scales = [0.45, 1.00, 0.65, 0.82]
        depolarize_scales = [1.00, 0.72, 0.55, 0.85]
        events = []

        channel_specs = (
            (
                "dephasing",
                self.dephase,
                dephase_scales,
                dephasing_kraus,
            ),
            (
                "amplitude_damping",
                self.damping,
                damping_scales,
                amplitude_damping_kraus,
            ),
            (
                "depolarizing",
                self.depolarize,
                depolarize_scales,
                depolarizing_kraus,
            ),
        )
        for channel_name, amount, scales, kraus_factory in channel_specs:
            for qubit in range(NUM_QUBITS):
                event = self.environment_trajectory.apply_local(
                    self.rho,
                    kraus_factory(amount * scales[qubit]),
                    channel=channel_name,
                    qubit=qubit,
                    configuration=self.bohm.configuration,
                    logical_time=self.logical_time,
                )
                self.rho = event.rho_after
                events.append(event)
                if event.jumped:
                    self.bohm.record_discontinuity(
                        BohmEventFamily.ENVIRONMENTAL_JUMP,
                        event.rho_after,
                        logical_time=event.logical_time,
                        configuration_after=event.configuration_after,
                        metadata={
                            "trajectory_event_id": event.event_id,
                            "channel": event.channel,
                            "qubit": event.qubit,
                            "outcome": event.outcome,
                            "outcome_probability": event.outcome_probability,
                        },
                    )

        self.environment_events = events
        self.configuration_revision = self.bohm.configuration_revision
        changed = not np.allclose(self.rho, rho_before, atol=1e-14)
        jumped = [event for event in events if event.jumped]
        if changed:
            self.state_revision += 1
            self._persist_transition(
                event_type="environmental_trajectory",
                rho_after=self.rho,
                event_id=(jumped[-1].event_id if jumped else events[-1].event_id),
                metadata={
                    "unraveling": "local_kraus_trajectory",
                    "environment_seed": self.environment_trajectory.seed,
                    "branches": [event.to_record() for event in events],
                },
                rho_before=rho_before,
                delta_rho=self.rho - rho_before,
            )
        if jumped:
            self.last_event_id = jumped[-1].event_id
            self.last_event_type = BohmEventFamily.ENVIRONMENTAL_JUMP
        return events

    def apply_local_rotation(
        self,
        qubit: int,
        axis: str,
        theta: float,
    ):
        """
        Apply a unitary single-qubit rotation to the current
        four-qubit density matrix.
        """
        rho_before = self.rho.copy()
        axis = axis.lower()

        pauli_map = {
            "x": X,
            "y": Y,
            "z": Z,
        }

        if axis not in pauli_map:
            raise ValueError(f"Unknown rotation axis: {axis}")

        if qubit < 0 or qubit >= NUM_QUBITS:
            raise ValueError(f"Invalid qubit index: {qubit}")

        theta = float(np.clip(theta, -np.pi, np.pi))

        single_qubit_rotation = (
            np.cos(theta / 2.0) * I2
            - 1j * np.sin(theta / 2.0) * pauli_map[axis]
        )

        unitary = local_operator(
            qubit,
            single_qubit_rotation,
        )

        self.rho, generator = self.bohm.unfold_unitary(
            self.rho,
            unitary,
            family=BohmEventFamily.CIRCUIT_CURRENT,
            logical_time=self.logical_time,
        )
        self.configuration_revision = self.bohm.configuration_revision
        self.state_revision += 1
        self._persist_transition(
            event_type="explicit_rotation",
            rho_after=self.rho,
            event_id=self.last_event_id,
            metadata={
                "qubit": qubit,
                "axis": axis.upper(),
                "theta": theta,
                "unfolded": True,
                "internal_duration_seconds": self.bohm.config.gate_duration_seconds,
                "microsteps": self.bohm.config.gate_microsteps,
                "generator_norm": float(np.linalg.norm(generator)),
            },
            rho_before=rho_before,
            delta_rho=self.rho - rho_before,
        )

    def _bohm_metadata(self):
        return {
            "actual_configuration": int(self.bohm.configuration),
            "beable_basis": self.bohm.beable_basis,
            "configuration_revision": int(self.bohm.configuration_revision),
            "last_guidance_frame": (
                self.bohm.last_frame.to_record()
                if self.bohm.last_frame is not None
                else None
            ),
        }

    def _persist_state(self, event_type="state", metadata=None):
        if self.state_publisher is None:
            return None
        packet_metadata = {**(metadata or {}), **self._bohm_metadata()}
        return self.state_publisher.publish_state(
            self.rho,
            revision=self.state_revision,
            logical_time=self.logical_time,
            event_id=self.last_event_id,
            event_type=event_type,
            configuration_revision=self.configuration_revision,
            metadata=packet_metadata,
        )

    def _persist_transition(
        self,
        *,
        event_type,
        rho_after,
        event_id,
        metadata,
        rho_before=None,
        delta_rho=None,
        force_checkpoint=False,
        revision=None,
        logical_time=None,
    ):
        if self.state_publisher is None:
            return None
        packet_metadata = {**(metadata or {}), **self._bohm_metadata()}
        return self.state_publisher.append_transition(
            event_type=event_type,
            rho_after=rho_after,
            revision=self.state_revision if revision is None else revision,
            logical_time=self.logical_time if logical_time is None else logical_time,
            event_id=event_id,
            configuration_revision=self.configuration_revision,
            metadata=packet_metadata,
            rho_before=rho_before,
            delta_rho=delta_rho,
            force_checkpoint=force_checkpoint,
        )

    def _temporal_state_record(self):
        frame = self.last_temporal_frame
        if frame is None:
            return None
        return {
            "revision": int(frame.revision),
            "tick": int(frame.tick),
            "simulation_time": float(frame.simulation_time),
            "protocol": str(frame.protocol),
            "events": [dict(event) for event in frame.events],
            "clock": dict(frame.clock),
            "metadata": dict(frame.metadata),
        }

    def _apply_temporal_layer(self, dt):
        """Apply one optional temporal map while retaining canonical rho ownership."""

        if self.temporal_layer is None:
            self.last_temporal_frame = None
            return None

        updates = self.temporal_layer.advance(
            self.rho,
            dt=float(dt),
            revision=self.state_revision,
        )
        client = getattr(getattr(self, "qmw_bridge", None), "client", None)
        for update in updates:
            rho_before = self.rho.copy()
            frame = update.frame
            self.rho = np.array(frame.rho, dtype=np.complex128, copy=True)
            self.last_temporal_frame = frame

            if update.mutated:
                self.state_revision = int(frame.revision)
                self.last_event_type = "temporal_evolution"
                bohm_event = self.bohm.record_discontinuity(
                    "temporal_evolution",
                    self.rho,
                    logical_time=self.logical_time,
                    ensure_supported=True,
                    metadata={
                        "protocol": frame.protocol,
                        "temporal_tick": frame.tick,
                    },
                )
                self.configuration_revision = self.bohm.configuration_revision
                self._persist_transition(
                    event_type="temporal_evolution",
                    rho_after=self.rho,
                    event_id=self.last_event_id,
                    metadata={
                        "protocol": frame.protocol,
                        "temporal_tick": frame.tick,
                        "temporal_simulation_time": frame.simulation_time,
                        "temporal_events": [
                            dict(event) for event in frame.events
                        ],
                        "temporal_metadata": dict(frame.metadata),
                        "bohm_event": bohm_event.to_record(),
                    },
                    rho_before=rho_before,
                    delta_rho=self.rho - rho_before,
                )

            if client is not None:
                self.temporal_layer.publish_frame(client, frame)
        return updates[-1] if updates else None

    def _publish_bohm_event(self, event):
        client = getattr(getattr(self, "qmw_bridge", None), "client", None)
        if client is None:
            return
        messages = {
            "/quantum/bohm/event/id": event.event_id,
            "/quantum/bohm/event/family": event.family,
            "/quantum/bohm/event/configuration_before": event.configuration_before,
            "/quantum/bohm/event/configuration_after": event.configuration_after,
            "/quantum/bohm/event/jumped": int(event.jumped),
            "/quantum/bohm/configuration": event.configuration_after,
            "/quantum/bohm/beable_basis": event.beable_basis,
            "/quantum/event/type": event.family,
        }
        for address, value in messages.items():
            client.send_message(address, value)

    def _publish_pending_bohm_events(self):
        pending = self.bohm.event_history[self._bohm_event_publish_cursor :]
        for event in pending:
            self._publish_bohm_event(event)
        self._bohm_event_publish_cursor = len(self.bohm.event_history)

    def configure_grw(self, **changes):
        """Update immutable GRW controls and reschedule from logical now."""
        self.grw.reconfigure(**changes)
        self._publish_grw_status()

    def configure_bohm(self, **changes):
        self.bohm.config = replace(self.bohm.config, **changes)
        self._publish_bohm_status()

    def _osc_bohm_enabled(self, _address, enabled):
        self.configure_bohm(enabled=bool(int(enabled)))

    def _osc_bohm_environment_enabled(self, _address, enabled):
        self.configure_bohm(
            environment_trajectory_enabled=bool(int(enabled))
        )

    def _osc_bohm_gate_duration(self, _address, seconds):
        self.configure_bohm(gate_duration_seconds=max(1e-6, float(seconds)))

    def _osc_bohm_gate_microsteps(self, _address, count):
        self.configure_bohm(gate_microsteps=max(1, int(count)))

    def _publish_bohm_status(self):
        client = getattr(getattr(self, "qmw_bridge", None), "client", None)
        if client is None:
            return
        messages = {
            "/quantum/bohm/enabled": int(self.bohm.config.enabled),
            "/quantum/bohm/environment/enabled": int(
                self.bohm.config.environment_trajectory_enabled
            ),
            "/quantum/bohm/gate_duration": self.bohm.config.gate_duration_seconds,
            "/quantum/bohm/gate_microsteps": self.bohm.config.gate_microsteps,
            "/quantum/bohm/configuration": int(self.bohm.configuration),
            "/quantum/bohm/beable_basis": self.bohm.beable_basis,
        }
        for address, value in messages.items():
            client.send_message(address, value)

    def _osc_grw_enabled(self, _address, enabled):
        self.configure_grw(enabled=bool(int(enabled)))

    def _osc_grw_rate_hz(self, _address, rate_hz):
        self.configure_grw(rate_hz=max(0.0, float(rate_hz)))

    def _osc_grw_strength(self, _address, strength):
        self.configure_grw(
            width=strength_to_width(float(np.clip(strength, 0.0, 1.0)))
        )

    def _osc_grw_width(self, _address, width):
        self.configure_grw(width=max(1e-6, float(width)))

    def _osc_grw_basis(self, _address, basis):
        value = str(basis).upper()
        if value not in ("X", "Y", "Z", "CIRCUIT"):
            raise ValueError("GRW basis must be X, Y, Z, or circuit")
        self.configure_grw(basis_source=value.lower() if value == "CIRCUIT" else value)

    def _osc_grw_seed(self, _address, seed):
        self.configure_grw(seed=int(seed))

    def _publish_grw_status(self):
        client = getattr(getattr(self, "qmw_bridge", None), "client", None)
        if client is None:
            return
        status = {
            "/quantum/grw/enabled": int(self.grw.config.enabled),
            "/quantum/grw/rate_hz": self.grw.config.rate_hz,
            "/quantum/grw/strength": self.grw.config.strength,
            "/quantum/grw/width": self.grw.config.width,
            "/quantum/grw/basis": self._grw_basis(),
            "/quantum/grw/seed": self.grw.config.seed,
            "/quantum/grw/next_event_ms": self.grw.next_event_ms,
        }
        for address, value in status.items():
            client.send_message(address, value)

    def _grw_basis(self):
        source = str(self.grw.config.basis_source).upper()
        if source in ("X", "Y", "Z"):
            return source
        if source != "CIRCUIT":
            return "Z"

        try:
            active = self.qmw_bridge.registry_circuit.active_measurement_bases()
            if active:
                axis = str(active[-1][1].pauli_axis or "").upper()
                if axis in ("X", "Y", "Z"):
                    return axis
        except (AttributeError, IndexError, TypeError):
            pass
        return "Z"

    def _publish_grw_event(self, event):
        """Publish descriptors only; the bridge's later state packet uses rho+."""
        client = getattr(self.qmw_bridge, "client", None)
        if client is None:
            return
        messages = {
            "/quantum/grw/event/flash": int(event.audible),
            "/quantum/grw/event/id": event.event_id,
            "/quantum/grw/event/qubit": event.qubit,
            "/quantum/grw/event/outcome": event.outcome,
            "/quantum/grw/event/probability": event.probability,
            "/quantum/grw/event/salience": event.trace_distance,
            "/quantum/grw/event/coherence_delta": event.coherence_delta,
            "/quantum/grw/event/purity_delta": event.purity_delta,
            "/quantum/grw/event/dominant_pauli": event.dominant_pauli,
            "/quantum/grw/event/dominant_pauli_delta": event.dominant_pauli_delta_value,
            "/quantum/grw/next_event_ms": self.grw.next_event_ms,
            "/quantum/event/type": "spontaneous_localization",
        }
        for address, value in messages.items():
            client.send_message(address, value)

    def perform_measurement(
        self,
        basis="Z",
        mode="collapse",
        request_id=0,
    ):
        """Sample an explicit measurement and mutate only canonical self.rho."""
        event = self.measurement.measure(
            self.rho,
            basis=basis,
            mode=mode,
            logical_time=self.logical_time,
            revision_before=self.state_revision,
            request_id=request_id,
        )
        if event.changed_state:
            self.rho = event.rho_after
            self.state_revision = event.revision_after
            self.last_event_type = "explicit_measurement"
        else:
            self.last_event_type = "measurement_probe"
        bohm_event = self.bohm.record_discontinuity(
            BohmEventFamily.EXPLICIT_MEASUREMENT,
            event.rho_after,
            logical_time=event.logical_time,
            ensure_supported=event.changed_state,
            metadata={
                "measurement_event_id": event.event_id,
                "request_id": event.request_id,
                "basis": event.basis,
                "mode": event.mode,
                "outcome": event.outcome,
            },
        )
        self.configuration_revision = self.bohm.configuration_revision
        self.last_event_id = event.event_id
        self.last_measurement_event = event
        self._persist_transition(
            event_type=(
                "explicit_measurement" if event.changed_state else "measurement_probe"
            ),
            rho_after=event.rho_after,
            event_id=event.event_id,
            metadata={
                "request_id": event.request_id,
                "basis": event.basis,
                "mode": event.mode,
                "outcome": event.outcome,
                "bitstring": event.bitstring,
                "probability": event.probability,
                "trace_distance": event.trace_distance,
                "measurement_seed": self.measurement.seed,
                "bohm_event": bohm_event.to_record(),
            },
            rho_before=event.rho_before,
            delta_rho=event.delta_rho,
        )
        self._publish_measurement_event(event)
        self._publish_pending_bohm_events()
        return event

    def _osc_measure(self, _address, *args):
        basis = str(args[0]).upper() if args else "Z"
        mode = str(args[1]).lower() if len(args) > 1 else "collapse"
        request_id = int(args[2]) if len(args) > 2 else 0
        reply_port = int(args[3]) if len(args) > 3 else 0
        reply_host = str(args[4]) if len(args) > 4 else "127.0.0.1"
        self.measurement_requests.put(
            (basis, mode, request_id, reply_host, reply_port)
        )

    def _drain_measurement_requests(self):
        """Apply threaded OSC requests on the engine's state-owning thread."""
        events = []
        while True:
            try:
                basis, mode, request_id, reply_host, reply_port = (
                    self.measurement_requests.get_nowait()
                )
            except queue.Empty:
                break
            try:
                event = self.perform_measurement(
                    basis=basis,
                    mode=mode,
                    request_id=request_id,
                )
            except Exception as exc:
                self._send_measurement_error(
                    request_id,
                    str(exc),
                    reply_host,
                    reply_port,
                )
                continue
            events.append(event)
            self._send_measurement_reply(event, reply_host, reply_port)
        return events

    def _send_measurement_error(self, request_id, message, reply_host, reply_port):
        client = getattr(self.qmw_bridge, "client", None)
        payload = [int(request_id), str(message)]
        if client is not None:
            client.send_message("/quantum/measurement/error", payload)
        if reply_port > 0:
            from pythonosc.udp_client import SimpleUDPClient

            reply = SimpleUDPClient(reply_host, reply_port)
            reply.send_message("/quantum/state/error/measurement", payload)
            sock = getattr(reply, "_sock", None)
            if sock is not None:
                sock.close()

    @staticmethod
    def _send_measurement_reply(event, reply_host, reply_port):
        if reply_port > 0:
            from pythonosc.udp_client import SimpleUDPClient

            reply = SimpleUDPClient(reply_host, reply_port)
            reply.send_message(
                "/quantum/state/event/measurement",
                event.osc_payload(),
            )
            reply.send_message(
                "/quantum/state/event/rho",
                [
                    event.revision_after,
                    event.rho_after.shape[0],
                    *event.rho_after.real.reshape(-1).tolist(),
                    *event.rho_after.imag.reshape(-1).tolist(),
                ],
            )
            sock = getattr(reply, "_sock", None)
            if sock is not None:
                sock.close()

    def _publish_measurement_event(self, event):
        client = getattr(self.qmw_bridge, "client", None)
        if client is None:
            return
        messages = {
            "/quantum/measurement/request_id": event.request_id,
            "/quantum/measurement/event_id": event.event_id,
            "/quantum/measurement/basis": event.basis,
            "/quantum/measurement/mode": event.mode,
            "/quantum/measurement/outcome": event.outcome,
            "/quantum/measurement/bitstring": event.bitstring,
            "/quantum/measurement/probability": event.probability,
            "/quantum/measurement/trace_distance": event.trace_distance,
            "/quantum/measurement/revision": event.revision_after,
            "/quantum/measurement/flash": 1,
            "/quantum/event/type": (
                "explicit_measurement" if event.changed_state else "measurement_probe"
            ),
        }
        for address, value in messages.items():
            client.send_message(address, value)
        client.send_message(
            "/quantum/state/event/measurement",
            event.osc_payload(),
        )

    def partial_trace(self, rho, keep, n_qubits=4):
        """
        Trace out all qubits except those listed in `keep`.

        rho: full 2^n x 2^n density matrix
        keep: list of qubit indices to retain, e.g. [0] or [0, 1]
        """
        keep = list(keep)
        trace_out = [q for q in range(n_qubits) if q not in keep]

        # Reshape rho into 2n tensor indices:
        # row qubit indices followed by column qubit indices.
        tensor = rho.reshape([2] * (2 * n_qubits))

        current_n = n_qubits

        # Trace from highest index downward so axis indexing stays valid.
        for q in sorted(trace_out, reverse=True):
            tensor = np.trace(
                tensor,
                axis1=q,
                axis2=q + current_n,
            )
            current_n -= 1

        dim_keep = 2 ** len(keep)
        return tensor.reshape(dim_keep, dim_keep)

    def von_neumann_entropy(self, rho_reduced, base=2):
        """
        Von Neumann entropy of a reduced density matrix.

        base=2 -> ebits
        base=np.e -> natural-log units, where a Bell pair = log(2)
        """
        rho_hermitian = 0.5 * (rho_reduced + rho_reduced.conj().T)

        eigvals = np.linalg.eigvalsh(rho_hermitian).real
        eigvals = np.clip(eigvals, 0.0, 1.0)

        # Remove numerical zeros before log.
        eigvals = eigvals[eigvals > 1e-12]

        if len(eigvals) == 0:
            return 0.0

        entropy = -np.sum(eigvals * np.log(eigvals))

        if base == 2:
            entropy /= np.log(2)
        elif base != np.e:
            entropy /= np.log(base)

        return float(entropy)

    def entanglement_metrics(self, rho):
        """
        Return one-qubit entropies and useful 2-vs-2 bipartition entropies.
        """
        single_qubit_entropy = {}

        for q in range(4):
            rho_q = self.partial_trace(rho, keep=[q], n_qubits=4)
            single_qubit_entropy[q] = self.von_neumann_entropy(rho_q, base=2)

        bipartition_entropy = {
            "01_vs_23": self.von_neumann_entropy(
                self.partial_trace(rho, keep=[0, 1], n_qubits=4),
                base=2,
            ),
            "02_vs_13": self.von_neumann_entropy(
                self.partial_trace(rho, keep=[0, 2], n_qubits=4),
                base=2,
            ),
            "03_vs_12": self.von_neumann_entropy(
                self.partial_trace(rho, keep=[0, 3], n_qubits=4),
                base=2,
            ),
        }

        mean_single_entropy = float(
            np.mean(list(single_qubit_entropy.values()))
        )

        return {
            "single_qubit_entropy": single_qubit_entropy,
            "mean_single_entropy": mean_single_entropy,
            "bipartition_entropy": bipartition_entropy,
        }


    def step(self, dt):
        # OSC callbacks enqueue only. Explicit measurement is applied here so
        # circuit, GRW, and performer-requested transitions have one owner.
        self.bohm.begin_frame()
        self._drain_measurement_requests()
        if self.freeze:
            return self.rho

        self.update_drift()
        self.update_excitation_source(dt)

        # 1. Get the current Hamiltonian
        hamiltonian = self.hamiltonian()

        # 2. Take one due circuit column. The native bridge returns its unitary
        # for generator unfolding; older third-party bridges retain their
        # instantaneous apply_due_circuit_column compatibility path.
        rho_before_gate = self.rho.copy()
        gate_generator = None
        gate_unfolded = False
        take_due = getattr(self.qmw_bridge, "take_due_circuit_column", None)
        if callable(take_due):
            gate_unitary, circuit_column, gate_labels = take_due(dt)
            if gate_unitary is not None:
                self.rho, gate_generator = self.bohm.unfold_unitary(
                    self.rho,
                    gate_unitary,
                    family=BohmEventFamily.CIRCUIT_CURRENT,
                    logical_time=self.logical_time,
                )
                gate_unfolded = True
        else:
            self.rho, circuit_column, gate_labels = (
                self.qmw_bridge.apply_due_circuit_column(self.rho, dt)
            )
        gate_delta_rho = float(
            np.linalg.norm(self.rho - rho_before_gate)
        )
        gate_applied = 1 if circuit_column is not None else 0

        if gate_applied:

            self.last_gate_column = int(circuit_column)
            self.last_gate_delta_rho = gate_delta_rho
            self.gate_energy = gate_delta_rho
            self.gate_event_count += 1
            self.state_revision += 1
            self.configuration_revision = self.bohm.configuration_revision
            self.last_event_type = "circuit_gate"
            self._persist_transition(
                event_type="circuit_gate",
                rho_after=self.rho,
                event_id=self.gate_event_count,
                metadata={
                    "column": self.last_gate_column,
                    "gate_labels": gate_labels or [],
                    "gate_delta_rho": gate_delta_rho,
                    "unfolded": gate_unfolded,
                    "internal_duration_seconds": (
                        self.bohm.config.gate_duration_seconds
                        if gate_unfolded
                        else 0.0
                    ),
                    "microsteps": (
                        self.bohm.config.gate_microsteps if gate_unfolded else 0
                    ),
                    "generator_norm": (
                        float(np.linalg.norm(gate_generator))
                        if gate_generator is not None
                        else None
                    ),
                    "qasm_lines": self.qmw_bridge.circuit.to_openqasm2_lines(),
                },
                rho_before=rho_before_gate,
                delta_rho=self.rho - rho_before_gate,
            )

        else:
            self.gate_energy *= 0.95

        # 3. Optional open-system trajectories. The legacy unconditioned
        # apply_noise() method remains available, while this branch samples
        # explicit environmental Kraus outcomes and updates the beable.
        if self.bohm.config.environment_trajectory_enabled:
            self.apply_noise_trajectory()
        else:
            self.environment_events = []

        # 4. Evolve to each exact GRW time, apply the hit to canonical rho,
        # then evolve through the remainder of this frame.
        guidance_clock = [self.logical_time]

        def guided_hamiltonian_evolution(state, segment):
            effective_duration = segment * 3.0
            evolved = self.bohm.evolve_density(
                state,
                hamiltonian,
                duration=effective_duration,
                microsteps=self.bohm.config.hamiltonian_microsteps,
                family=BohmEventFamily.HAMILTONIAN_CURRENT,
                logical_time_start=guidance_clock[0],
                timeline_duration=segment,
            )
            guidance_clock[0] += segment
            return evolved

        grw_bohm_events = {}

        def record_grw_configuration(event):
            grw_bohm_events[event.event_id] = self.bohm.record_discontinuity(
                BohmEventFamily.SPONTANEOUS_LOCALIZATION,
                event.rho_after,
                logical_time=event.logical_time,
                metadata={
                    "grw_event_id": event.event_id,
                    "qubit": event.qubit,
                    "outcome": event.outcome,
                    "basis": event.basis,
                    "trace_distance": event.trace_distance,
                },
            )

        grw_result = self.grw.advance(
            self.rho,
            dt,
            revision=self.state_revision,
            basis=self._grw_basis(),
            evolve=guided_hamiltonian_evolution,
            on_event=record_grw_configuration,
        )
        self.rho = grw_result.rho
        self.state_revision = grw_result.revision
        self.logical_time = grw_result.logical_time
        self.grw_events = list(grw_result.events)
        for event in self.grw_events:
            self.last_grw_event = event
            self.last_event_id = event.event_id
            self.last_event_type = "spontaneous_localization"
            self.configuration_revision = self.bohm.configuration_revision
            self._persist_transition(
                event_type="spontaneous_localization",
                rho_after=event.rho_after,
                event_id=event.event_id,
                metadata={
                    **event.to_record(include_matrices=False),
                    "grw_seed": self.grw.config.seed,
                    "constituent_scale": self.grw.config.constituent_scale,
                    "bohm_event": grw_bohm_events[event.event_id].to_record(),
                },
                rho_before=event.rho_before,
                delta_rho=event.delta_rho,
                revision=event.revision_after,
                logical_time=event.logical_time,
            )
            self._publish_grw_event(event)

        self.configuration_revision = self.bohm.configuration_revision

        # 5. Apply the selected temporal protocol. Observer mode advances only
        # clocks and descriptors; explicit evolvers return a new canonical rho.
        self._apply_temporal_layer(dt)

        # Publish the exact post-frame canonical state even when the frame had
        # no discrete event. Event history remains limited to actual changes.
        self._persist_state(
            event_type="frame_state",
            metadata={
                "dt": float(dt),
                "grw_events": len(self.grw_events),
                "temporal": self._temporal_state_record(),
            },
        )

        self._publish_pending_bohm_events()

        # 6. Recompute metrics from the newly evolved state
        metrics = self.entanglement_metrics(self.rho)
        self.entanglement = metrics

        self.entropy_q0 = metrics["single_qubit_entropy"][0]
        self.entropy_q1 = metrics["single_qubit_entropy"][1]
        self.entropy_q2 = metrics["single_qubit_entropy"][2]
        self.entropy_q3 = metrics["single_qubit_entropy"][3]

        self.entropy_mean = metrics["mean_single_entropy"]

        qubit_entropy = np.array(
            [
                self.entropy_q0,
                self.entropy_q1,
                self.entropy_q2,
                self.entropy_q3,
            ],
            dtype=float,
        )
        entropy_total = float(np.sum(qubit_entropy))
        entropy_spread = float(np.max(qubit_entropy) - np.min(qubit_entropy))

        if entropy_total > 1e-12:
            entropy_centroid = float(
                np.dot(np.arange(NUM_QUBITS, dtype=float), qubit_entropy)
                / entropy_total
            )
        else:
            entropy_centroid = 0.0

        entropy_motion_vector = qubit_entropy - self.previous_qubit_entropy
        entropy_motion = float(np.linalg.norm(entropy_motion_vector))
        entropy_motion_mean = float(np.mean(np.abs(entropy_motion_vector)))
        entropy_dominant_qubit = int(np.argmax(qubit_entropy))
        self.previous_qubit_entropy = qubit_entropy.copy()

        self.entropy_01_23 = metrics["bipartition_entropy"]["01_vs_23"]
        self.entropy_02_13 = metrics["bipartition_entropy"]["02_vs_13"]
        self.entropy_03_12 = metrics["bipartition_entropy"]["03_vs_12"]

        populations = np.real(np.diag(self.rho))

        local_bloch = self.local_bloch_vectors()

        if self.verbose:
            print("METRIC KEYS:", metrics.keys())
            print(
                "CIRCUIT STATE:",
                "p[:4]=", np.round(populations[:4], 4),
                "q entropy=", {
                    q: round(metrics.get("single_qubit_entropy").get(q), 4)
                    for q in range(4)
                },
                "coherence=", round(
                    metrics.get("coherence")
                    or metrics.get("coherence_l1")
                    or 0.0,
                    4,
                ),
                "purity=", round(metrics.get("purity") or 0.0, 4),
                "S=", round(metrics.get("entropy") or 0.0, 4),
            )

                # Direct global density metrics for OSC.
        rho_hermitian = 0.5 * (
            self.rho + self.rho.conj().T
        )

        purity_direct = float(
            np.real(np.trace(rho_hermitian @ rho_hermitian))
        )

        diagonal = np.diag(np.diag(rho_hermitian))
        coherence_direct = float(
            np.sum(np.abs(rho_hermitian - diagonal))
        )

        eigenvalues = np.linalg.eigvalsh(rho_hermitian)
        eigenvalues = np.clip(
            np.real(eigenvalues),
            1e-12,
            None,
        )
        eigenvalues = eigenvalues / np.sum(eigenvalues)

        entropy_direct = float(
            -np.sum(eigenvalues * np.log2(eigenvalues))
        )

        phase_populations = np.clip(
            np.real(np.diag(rho_hermitian)),
            0.0,
            None,
        )
        phase_reference = int(np.argmax(phase_populations))
        reference_population = float(phase_populations[phase_reference])
        reference_coherence = rho_hermitian[:, phase_reference]
        basis_phases = np.angle(reference_coherence)
        basis_phases[phase_reference] = 0.0

        phase_quality = np.zeros(DIMENSION, dtype=float)
        if reference_population > 1e-12:
            quality_denominator = np.sqrt(
                np.maximum(
                    phase_populations * reference_population,
                    1e-24,
                )
            )
            phase_quality = np.clip(
                np.abs(reference_coherence) / quality_denominator,
                0.0,
                1.0,
            )
        phase_quality[phase_reference] = 1.0 if reference_population > 1e-12 else 0.0
        basis_labels = [
            format(index, f"0{NUM_QUBITS}b")
            for index in range(DIMENSION)
        ]

        # 6. Publish the authoritative configuration through the legacy pilot
        # telemetry shape. The bridge no longer advances an independent node.
        guidance_frame = self.bohm.last_frame
        if guidance_frame is not None:
            authoritative_pilot = PilotFrame(
                node=guidance_frame.source,
                next_node=guidance_frame.destination,
                velocity=float(
                    min(1.0, guidance_frame.total_rate * max(float(dt), 0.0))
                ),
                current=guidance_frame.current,
                phase_gradient=guidance_frame.phase_gradient,
                branch_entropy=guidance_frame.branch_entropy,
                current_matrix=current_matrix(hamiltonian, self.rho),
            )
            install_frame = getattr(
                self.qmw_bridge, "set_authoritative_pilot_frame", None
            )
            if callable(install_frame):
                install_frame(authoritative_pilot)

        self.pilot = self.qmw_bridge.update_and_send(
            self.rho,
            hamiltonian,
            dt,
            circuit_column,
            gate_labels,
        )
        qasm_lines = self.qmw_bridge.circuit.to_openqasm2_lines()

        self.circuit_state = {
            "populations": populations.tolist(),
            "single_qubit_entropy": metrics.get(
                "single_qubit_entropy",
                {},
            ),
            "entropy_spread": entropy_spread,
            "entropy_centroid": entropy_centroid,
            "entropy_centroid_norm": entropy_centroid / max(1, NUM_QUBITS - 1),
            "entropy_motion": entropy_motion,
            "entropy_motion_mean": entropy_motion_mean,
            "entropy_motion_vector": entropy_motion_vector.tolist(),
            "entropy_dominant_qubit": entropy_dominant_qubit,
            "local_bloch": local_bloch.tolist(),
            "coherence": coherence_direct,
            "purity": purity_direct,
            "entropy": entropy_direct,
            "basis_labels": basis_labels,
            "phase_reference": phase_reference,
            "basis_phases": basis_phases.tolist(),
            "phase_quality": phase_quality.tolist(),
            "qasm": "\n".join(qasm_lines),
            "qasm_lines": qasm_lines,
            "column": int(circuit_column) if circuit_column is not None else -1,
            "gate_labels": gate_labels or [],
            "pilot": self.pilot or {},
            "gate_applied": gate_applied,
            "gate_delta_rho": gate_delta_rho,
            "last_gate_column": self.last_gate_column,
            "last_gate_delta_rho": self.last_gate_delta_rho,
            "gate_energy": self.gate_energy,
            "gate_event_count": self.gate_event_count,
            "excitation_source": self.excitation_source_kind,
            "hamiltonian_state": self.hamiltonian_state.as_pauli_terms(),
            "source_descriptor": (
                self.source_descriptor.__dict__
                if self.source_descriptor is not None
                else None
            ),
            "revision": self.state_revision,
            "logical_time": self.logical_time,
            "last_event_id": self.last_event_id,
            "last_event_type": self.last_event_type,
            "configuration_revision": self.configuration_revision,
            "temporal": self._temporal_state_record(),
            "bohm": {
                "enabled": self.bohm.config.enabled,
                "actual_configuration": int(self.bohm.configuration),
                "bitstring": format(self.bohm.configuration, "04b"),
                "beable_basis": self.bohm.beable_basis,
                "configuration_revision": self.bohm.configuration_revision,
                "gate_duration_seconds": self.bohm.config.gate_duration_seconds,
                "gate_microsteps": self.bohm.config.gate_microsteps,
                "hamiltonian_microsteps": self.bohm.config.hamiltonian_microsteps,
                "environment_trajectory_enabled": (
                    self.bohm.config.environment_trajectory_enabled
                ),
                "last_frame": (
                    self.bohm.last_frame.to_record()
                    if self.bohm.last_frame is not None
                    else None
                ),
                "events_this_frame": [
                    event.to_record() for event in self.bohm.events_this_frame
                ],
            },
            "environment_events_this_frame": [
                event.to_record() for event in self.environment_events
            ],
            "grw": {
                "enabled": self.grw.config.enabled,
                "rate_hz": self.grw.config.rate_hz,
                "width": self.grw.config.width,
                "strength": self.grw.config.strength,
                "basis": self._grw_basis(),
                "next_event_ms": self.grw.next_event_ms,
                "events_this_frame": [
                    event.to_record(include_matrices=False)
                    for event in self.grw_events
                ],
            },
        }

    
    
        return self.rho
