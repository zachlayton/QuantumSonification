from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from sklearn import metrics

from qmw_circuit_bridge import PilotFrame, QMWCircuitBridge


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
        """Replace broad perturbation with directed state-dependent movement.

        Assumes your members have position/velocity numpy vectors. Adapt the
        field names and parameter dimensions to your actual v5 data structure.
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

        controlled_noise = self.rng.normal(0.0, noise_amount * (0.25 + guidance.diffusion), size=dim)
        member.velocity = (
            0.70 * member.velocity
            + 0.24 * guidance.momentum * direction
            + 0.10 * guidance.phase_force * np.roll(direction, 1)
            + controlled_noise
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


def local_operator(qubit, operator):
    return tensor_operator({qubit: operator})


def pair_operator(qubit_a, operator_a, qubit_b, operator_b):
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
    
    def __init__(self):
        self.rng = np.random.default_rng()

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

        self.reset_state()

        # Interactive circuit-builder / pilot-wave bridge
        self.qmw_bridge = QMWCircuitBridge(
            n_qubits=4,
            n_steps=16,
            active_length=16,
            osc_out_port=7400,
            osc_control_port=7403,
            circuit_interval_seconds=1.0,
        )

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

        elif (
            len(name) == 2
            and name[0] in ("x", "y", "z")
            and name[1] in ("0", "1", "2", "3")
        ):
            axis_index = {"x": 0, "y": 1, "z": 2}[name[0]]
            qubit = int(name[1])

            self.base_fields[qubit, axis_index] = value

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

        self.drift_state[:] = 0.0

        for key in self.pair_drift:
            self.pair_drift[key] = 0.0

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

    def local_bloch_vectors(self):
        vectors = []

        for qubit in range(NUM_QUBITS):
            reduced = partial_trace_keep(
                self.rho,
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

        for qubit in range(NUM_QUBITS):
            previous = (qubit - 1) % NUM_QUBITS
            following = (qubit + 1) % NUM_QUBITS

            bx_prev, by_prev, bz_prev = local_bloch[previous]
            bx_next, by_next, bz_next = local_bloch[following]

            x_field = (
                self.base_fields[qubit, 0]
                + self.drift_state[qubit, 0]
                + self.feedback * 0.70 * (by_prev - by_next)
                + self.feedback * 0.25 * global_coherence
            )

            y_field = (
                self.base_fields[qubit, 1]
                + self.drift_state[qubit, 1]
                + self.feedback * 0.60 * (bz_prev + bz_next)
                - self.feedback * 0.25 * global_entropy
            )

            z_field = (
                self.base_fields[qubit, 2]
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
        eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)

        unitary = (
            eigenvectors
            @ np.diag(np.exp(-1j * eigenvalues * dt))
            @ eigenvectors.conj().T
        )

        self.rho = unitary @ self.rho @ unitary.conj().T
        self.rho = normalize_density(self.rho)

    def apply_noise(self):
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

        self.rho = unitary @ self.rho @ unitary.conj().T
     
        self.rho = normalize_density(self.rho)

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
        if self.freeze:
            return self.rho

        self.update_drift()

        # 1. Get the current Hamiltonian
        hamiltonian = self.hamiltonian()

        # 2. Apply one circuit-builder column when its clock/event is due
        rho_before_gate = self.rho.copy()
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

        else:
            self.gate_energy *= 0.95

        # 3. Existing Hamiltonian evolution
        self.unitary_step(
            hamiltonian,
            dt * 3.0,
        )

        # 4. Existing open-system/noise/decoherence layer
        #self.apply_noise()

        # 5. Recompute metrics from the newly evolved state
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

        print("METRIC KEYS:", metrics.keys())
        print(

            "CIRCUIT STATE:",
            "p[:4]=", np.round(populations[:4], 4),
            "q entropy=", {

                q: round(metrics.get("single_qubit_entropy").get(q), 4)
                for q in range(4)
            },
            "coherence=", round(metrics.get("coherence")
                                or metrics.get("coherence_l1")
                                or 0.0,4),

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

        # 6. Bohmian-inspired current graph and OSC stream
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
        }

    
    
        return self.rho
