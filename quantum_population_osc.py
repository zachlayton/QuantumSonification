# quantum_population_osc.py

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import threading

# Change this import to match your project.
from density_matrix_engine import DensityMatrixEngine


# ------------------------------------------------------------
# POPULATION METRICS
# ------------------------------------------------------------

@dataclass
class PopulationMetrics:
    centroid: np.ndarray
    mean_distance: float
    spread: np.ndarray
    mean_purity: float
    purity_std: float
    mean_entropy: float
    entropy_std: float
    centroid_alignment: float
    coherence: float
    active_fraction: float
    outliers: list[int]


def extract_metrics_from_rho(rho) -> dict:
    """
    Derive sonification metrics directly from a density matrix.

    Works with either:
    - a NumPy array
    - a Qiskit DensityMatrix-like object with a .data attribute
    """

    rho = np.asarray(getattr(rho, "data", rho), dtype=np.complex128)

    # Ensure numerical Hermiticity before eigendecomposition.
    rho = 0.5 * (rho + rho.conj().T)

    # Normalize safely if tiny numerical drift has occurred.
    trace = np.trace(rho)
    if abs(trace) > 1e-12:
        rho = rho / trace

    # Purity: Tr(rho²)
    purity = float(np.real(np.trace(rho @ rho)))
    purity = float(np.clip(purity, 0.0, 1.0))

    # Von Neumann entropy: -Tr(rho log2 rho)
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = np.clip(np.real(eigenvalues), 0.0, 1.0)

    nonzero = eigenvalues[eigenvalues > 1e-12]
    entropy = float(-np.sum(nonzero * np.log2(nonzero)))

    # Bloch coordinates for qubit 0.
    # This traces out all other qubits using a reshape operation.
    dimension = rho.shape[0]
    num_qubits = int(round(np.log2(dimension)))

    if 2 ** num_qubits != dimension:
        raise ValueError(
            f"Density matrix dimension {dimension} is not a power of two."
        )

    if num_qubits == 1:
        reduced = rho
    else:
        tensor = rho.reshape([2] * (2 * num_qubits))

        # Keep qubit 0; trace out qubits 1 ... N-1.
        # Reverse order prevents axis numbering from shifting.
        for qubit in reversed(range(1, num_qubits)):
            tensor = np.trace(
                tensor,
                axis1=qubit,
                axis2=qubit + num_qubits,
            )

        reduced = tensor

    pauli_x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    pauli_y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
    pauli_z = np.array([[1, 0], [0, -1]], dtype=np.complex128)

    bloch_x = float(np.real(np.trace(reduced @ pauli_x)))
    bloch_y = float(np.real(np.trace(reduced @ pauli_y)))
    bloch_z = float(np.real(np.trace(reduced @ pauli_z)))

    return {
        "bloch_x": float(np.clip(bloch_x, -1.0, 1.0)),
        "bloch_y": float(np.clip(bloch_y, -1.0, 1.0)),
        "bloch_z": float(np.clip(bloch_z, -1.0, 1.0)),
        "purity": purity,
        "entropy": entropy,
    }


# ------------------------------------------------------------
# QUANTUM FEATURE LAYER
# ------------------------------------------------------------

PAULI_I = np.array(
    [[1, 0], [0, 1]],
    dtype=np.complex128,
)

PAULI_X = np.array(
    [[0, 1], [1, 0]],
    dtype=np.complex128,
)

PAULI_Y = np.array(
    [[0, -1j], [1j, 0]],
    dtype=np.complex128,
)

PAULI_Z = np.array(
    [[1, 0], [0, -1]],
    dtype=np.complex128,
)


def normalize_density_matrix(rho):
    """
    Clean up numerical drift while preserving Hermiticity and trace.
    """
    rho = np.asarray(getattr(rho, "data", rho), dtype=np.complex128)

    rho = 0.5 * (rho + rho.conj().T)

    trace = np.trace(rho)

    if abs(trace) > 1e-12:
        rho = rho / trace

    return rho


def infer_num_qubits(rho):
    dimension = rho.shape[0]
    num_qubits = int(round(np.log2(dimension)))

    if 2 ** num_qubits != dimension:
        raise ValueError(
            f"Density-matrix dimension {dimension} is not a power of two."
        )

    return num_qubits


def partial_trace_keep(rho, keep_qubits):
    """
    Return the reduced density matrix for the selected qubits.

    Works correctly for tracing out multiple qubits.
    """
    rho = normalize_density_matrix(rho)
    num_qubits = infer_num_qubits(rho)

    keep_qubits = sorted(set(keep_qubits))

    if not keep_qubits:
        raise ValueError("keep_qubits must contain at least one qubit.")

    if any(q < 0 or q >= num_qubits for q in keep_qubits):
        raise ValueError(
            f"Invalid qubit index in {keep_qubits} "
            f"for a {num_qubits}-qubit density matrix."
        )

    tensor = rho.reshape([2] * (2 * num_qubits))

    # Row indices: 0 ... num_qubits - 1
    # Column indices:
    #   same label for traced-out qubits, which contracts them
    #   new label for retained qubits, which preserves them
    input_labels = list(range(num_qubits))
    output_labels = list(keep_qubits)

    for qubit in range(num_qubits):
        if qubit in keep_qubits:
            input_labels.append(num_qubits + qubit)
        else:
            input_labels.append(qubit)

    output_labels.extend(
        [num_qubits + qubit for qubit in keep_qubits]
    )

    reduced_tensor = np.einsum(
        tensor,
        input_labels,
        output_labels,
    )

    reduced_dimension = 2 ** len(keep_qubits)

    return reduced_tensor.reshape(
        reduced_dimension,
        reduced_dimension,
    )


def von_neumann_entropy(rho):
    """
    S(rho) = -Tr(rho log2 rho)
    """
    rho = normalize_density_matrix(rho)

    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = np.clip(np.real(eigenvalues), 0.0, 1.0)

    nonzero = eigenvalues[eigenvalues > 1e-12]

    if len(nonzero) == 0:
        return 0.0

    return float(-np.sum(nonzero * np.log2(nonzero)))


def purity_of(rho):
    """
    Tr(rho^2)
    """
    rho = normalize_density_matrix(rho)

    purity = np.real(np.trace(rho @ rho))

    return float(np.clip(purity, 0.0, 1.0))


def bloch_vector(rho_single_qubit):
    """
    Return [<X>, <Y>, <Z>] for a 2x2 reduced density matrix.
    """
    rho_single_qubit = normalize_density_matrix(rho_single_qubit)

    x = float(np.real(np.trace(rho_single_qubit @ PAULI_X)))
    y = float(np.real(np.trace(rho_single_qubit @ PAULI_Y)))
    z = float(np.real(np.trace(rho_single_qubit @ PAULI_Z)))

    return np.array(
        [
            np.clip(x, -1.0, 1.0),
            np.clip(y, -1.0, 1.0),
            np.clip(z, -1.0, 1.0),
        ],
        dtype=float,
    )


def tensor_product_operators(operators):
    """
    Build a full-register operator from a list such as:
        [Z, I, X, I]
    """
    result = operators[0]

    for operator in operators[1:]:
        result = np.kron(result, operator)

    return result


def pauli_expectation(rho, pauli_map):
    """
    Compute an expectation value such as:

        pauli_expectation(rho, {0: PAULI_Z, 2: PAULI_X})

    All unspecified qubits receive identity operators.
    """
    rho = normalize_density_matrix(rho)
    num_qubits = infer_num_qubits(rho)

    operators = []

    for qubit in range(num_qubits):
        operators.append(
            pauli_map.get(qubit, PAULI_I)
        )

    operator = tensor_product_operators(operators)

    value = np.trace(rho @ operator)

    return float(np.real(value))


def l1_quantum_coherence(rho):
    """
    Basis-dependent superposition/coherence measure:

        sum of absolute off-diagonal density-matrix elements

    This is 0 for a fully diagonal mixture in the computational basis.
    """
    rho = normalize_density_matrix(rho)

    diagonal = np.diag(np.diag(rho))
    off_diagonal = rho - diagonal

    return float(np.sum(np.abs(off_diagonal)))


def participation_ratio(probabilities):
    """
    Effective number of computational-basis states occupied.

        1 / sum(p_i^2)

    1 means one dominant basis state.
    Higher values mean a broader superposition/distribution.
    """
    probabilities = np.asarray(
        probabilities,
        dtype=float,
    )

    denominator = float(np.sum(probabilities ** 2))

    if denominator <= 1e-12:
        return 0.0

    return float(1.0 / denominator)


def extract_quantum_features_from_rho(rho):
    """
    Extract local, relational, and global quantum features
    from a density matrix.

    Designed for the 4-qubit population engine, but works
    for any power-of-two register dimension.
    """
    rho = normalize_density_matrix(rho)
    num_qubits = infer_num_qubits(rho)

    basis_probabilities = np.real(np.diag(rho))
    basis_probabilities = np.clip(
        basis_probabilities,
        0.0,
        1.0,
    )

    probability_sum = float(np.sum(basis_probabilities))

    if probability_sum > 1e-12:
        basis_probabilities = (
            basis_probabilities / probability_sum
        )

    dominant_basis_index = int(
        np.argmax(basis_probabilities)
    )

    dominant_basis_probability = float(
        basis_probabilities[dominant_basis_index]
    )

    local_bloch = []
    local_purities = []
    local_entropies = []
    local_probabilities = []

    for qubit in range(num_qubits):
        reduced = partial_trace_keep(rho, [qubit])

        bloch = bloch_vector(reduced)

        local_bloch.append(bloch.tolist())
        local_purities.append(purity_of(reduced))
        local_entropies.append(von_neumann_entropy(reduced))

        p0 = float(np.real(reduced[0, 0]))
        p1 = float(np.real(reduced[1, 1]))

        local_probabilities.append(
            {
                "p0": float(np.clip(p0, 0.0, 1.0)),
                "p1": float(np.clip(p1, 0.0, 1.0)),
            }
        )

    pair_zz = {}
    pair_xx = {}
    pair_yy = {}

    connected_zz = {}
    pair_mutual_information = {}

    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            key = f"{i}{j}"

            zz = pauli_expectation(
                rho,
                {
                    i: PAULI_Z,
                    j: PAULI_Z,
                },
            )

            xx = pauli_expectation(
                rho,
                {
                    i: PAULI_X,
                    j: PAULI_X,
                },
            )

            yy = pauli_expectation(
                rho,
                {
                    i: PAULI_Y,
                    j: PAULI_Y,
                },
            )

            zi = local_bloch[i][2]
            zj = local_bloch[j][2]

            pair_zz[key] = zz
            pair_xx[key] = xx
            pair_yy[key] = yy

            connected_zz[key] = float(zz - (zi * zj))

            rho_ij = partial_trace_keep(rho, [i, j])

            mutual_information = (
                local_entropies[i]
                + local_entropies[j]
                - von_neumann_entropy(rho_ij)
            )

            pair_mutual_information[key] = float(
                max(0.0, mutual_information)
            )

    global_purity = purity_of(rho)
    global_entropy = von_neumann_entropy(rho)
    coherence_l1 = l1_quantum_coherence(rho)

    return {
        "num_qubits": num_qubits,

        # Register-level observables.
        "global_purity": global_purity,
        "global_entropy": global_entropy,
        "quantum_coherence_l1": coherence_l1,

        # Computational-basis structure.
        "basis_probabilities": basis_probabilities.tolist(),
        "dominant_basis_index": dominant_basis_index,
        "dominant_basis_probability": dominant_basis_probability,
        "participation_ratio": participation_ratio(
            basis_probabilities
        ),

        # Single-qubit layer.
        "local_bloch": local_bloch,
        "local_purities": local_purities,
        "local_entropies": local_entropies,
        "local_probabilities": local_probabilities,

        # Pairwise relation layer.
        "pair_zz": pair_zz,
        "pair_xx": pair_xx,
        "pair_yy": pair_yy,
        "connected_zz": connected_zz,
        "pair_mutual_information": pair_mutual_information,
    }



# ------------------------------------------------------------
# POPULATION ENGINE
# ------------------------------------------------------------



class PopulationEngine:
    """
    Runs many independent density-matrix trajectories.

    Each underlying engine must provide:

        engine.step(dt)
        engine.get_metrics()

    Expected get_metrics() dictionary keys:

        bloch_x
        bloch_y
        bloch_z
        purity
        entropy
    """

    def __init__(
        self,
        engine_factory: Callable[[int], Any],
        population_size: int = 32,
        seed: int = 1234,
    ):
        self.population_size = population_size
        self.rng = np.random.default_rng(seed)

        self.engines = [
            engine_factory(int(self.rng.integers(0, 2**31 - 1)))
            for _ in range(population_size)
        ]

        self.member_metrics: list[dict] = []
        self.last_metrics: PopulationMetrics | None = None
        
        
    def _read_rho(self, engine):
        """
        Try to retrieve the engine's current density matrix.
        Adapt candidate attribute names here if needed.
        """
        for name in ("rho", "density_matrix", "state"):
            if hasattr(engine, name):
                value = getattr(engine, name)
                return np.asarray(getattr(value, "data", value), dtype=np.complex128)

        raise AttributeError(
            "Could not find density matrix on engine. "
            "Check whether your engine stores it as rho, density_matrix, or state."
        )

    def _write_rho(self, engine, rho):
        """
        Write the coupled density matrix back into the engine so that
        its next evolution begins from the newly coupled state.
        """
        for name in ("rho", "density_matrix", "state"):
            if hasattr(engine, name):
                setattr(engine, name, rho)
                return

        raise AttributeError(
            "Could not write density matrix back to engine. "
            "Check the actual state attribute name."
        )

    def apply_mean_field_coupling(self, coupling_strength: float):
        """
        Mix every trajectory slightly toward the population mean state.

        coupling_strength:
            0.0 = independent trajectories
            1.0 = all trajectories become identical immediately
        """
        coupling_strength = float(np.clip(coupling_strength, 0.0, 1.0))

        if coupling_strength <= 0.0:
            return

        rhos = [self._read_rho(engine) for engine in self.engines]
        mean_rho = np.mean(rhos, axis=0)

        # Numerical cleanup: preserve Hermiticity and trace.
        mean_rho = 0.5 * (mean_rho + mean_rho.conj().T)
        mean_trace = np.trace(mean_rho)

        if abs(mean_trace) > 1e-12:
            mean_rho = mean_rho / mean_trace

        for engine, rho in zip(self.engines, rhos):
            coupled_rho = (
                (1.0 - coupling_strength) * rho
                + coupling_strength * mean_rho
            )

            coupled_rho = 0.5 * (
                coupled_rho + coupled_rho.conj().T
            )

            trace = np.trace(coupled_rho)

            if abs(trace) > 1e-12:
                coupled_rho = coupled_rho / trace

            self._write_rho(engine, coupled_rho)        

    def step(
        self,
        dt: float,
        coupling_strength: float = 0.02,
    ) -> PopulationMetrics:
        self.member_metrics = []

        # 1. Advance every member once.
        for engine in self.engines:
            engine.step(dt)

        # 2. Couple the newly evolved states.
        self.apply_mean_field_coupling(coupling_strength)

        # 3. Extract metrics from the coupled states.
        for engine in self.engines:
            rho = self._read_rho(engine)
            
            metrics = extract_metrics_from_rho(rho)
            quantum_features = extract_quantum_features_from_rho(rho)
            
            metrics["quantum_features"] = quantum_features
            
            
            self.member_metrics.append(metrics)

        self.last_metrics = self._analyze_population()
        return self.last_metrics

    def _analyze_population(self) -> PopulationMetrics:
        bloch = np.array(
            [
                [
                    m.get("bloch_x", 0.0),
                    m.get("bloch_y", 0.0),
                    m.get("bloch_z", 0.0),
                ]
                for m in self.member_metrics
            ],
            dtype=float,
        )

        purities = np.array(
            [m.get("purity", 0.0) for m in self.member_metrics],
            dtype=float,
        )

        entropies = np.array(
            [m.get("entropy", 0.0) for m in self.member_metrics],
            dtype=float,
        )

        centroid = np.mean(bloch, axis=0)
        spread = np.std(bloch, axis=0)

        centroid_alignment = float(
            np.clip(np.linalg.norm(centroid), 0.0, 1.0)
        )

        distances = np.linalg.norm(bloch - centroid, axis=1)
        mean_distance = float(np.mean(distances))
        std_distance = float(np.std(distances)) + 1e-9

        synchrony = float(
            1.0 / (1.0 + 20.0 * mean_distance)
        )

        z_scores = (distances - mean_distance) / std_distance
        outliers = np.where(z_scores > 1.5)[0].tolist()

        active_fraction = float(
            np.mean(distances > (mean_distance + std_distance))
        )

        return PopulationMetrics(
            centroid=centroid,
            spread=spread,
            mean_distance=mean_distance,
            mean_purity=float(np.mean(purities)),
            purity_std=float(np.std(purities)),
            mean_entropy=float(np.mean(entropies)),
            entropy_std=float(np.std(entropies)),
            centroid_alignment=centroid_alignment,
            coherence=synchrony,
            active_fraction=active_fraction,
            outliers=outliers,
        )

    def get_member(self, index: int) -> dict:
        return self.member_metrics[index]

    def get_loudest_members(self, count: int = 8) -> list[int]:
        """
        Select trajectories furthest from the centroid.

        These are good candidates for audible individual voices.
        """
        if not self.member_metrics:
            return []

        bloch = np.array(
            [
                [
                    m.get("bloch_x", 0.0),
                    m.get("bloch_y", 0.0),
                    m.get("bloch_z", 0.0),
                ]
                for m in self.member_metrics
            ],
            dtype=float,
        )

        centroid = np.mean(bloch, axis=0)
        distances = np.linalg.norm(bloch - centroid, axis=1)

        return np.argsort(distances)[-count:].tolist()


# ------------------------------------------------------------
# YOUR TRAJECTORY FACTORY
# ------------------------------------------------------------

def make_engine(seed: int) -> DensityMatrixEngine:
    rng = np.random.default_rng(seed)

    # Start with the exact constructor your working engine already uses.
    engine = DensityMatrixEngine()

    # Give each population member an independent RNG, if the engine
    # has a field where random behavior is generated.
    if hasattr(engine, "rng"):
        engine.rng = np.random.default_rng(seed)

    # Small local perturbations only where those attributes exist.
    if hasattr(engine, "noise_strength"):
        engine.noise_strength *= rng.uniform(0.85, 1.15)

    if hasattr(engine, "decoherence_rate"):
        engine.decoherence_rate *= rng.uniform(0.85, 1.15)

    if hasattr(engine, "detuning"):
        engine.detuning += rng.normal(0.0, 0.01)

    if hasattr(engine, "coupling_strength"):
        engine.coupling_strength *= rng.uniform(0.95, 1.05)

    return engine


# ------------------------------------------------------------
# OSC OUTPUT
# ------------------------------------------------------------

def send_population_osc(
    client: SimpleUDPClient,
    population: PopulationEngine,
    metrics: PopulationMetrics,
    coupling_strength: float,
    audible_voice_count: int = 8,
) -> None:


    """
    Sends global field data plus a limited number of individual voices.
    """

    # Global population field.
    client.send_message("/population/centroid/x", float(metrics.centroid[0]))
    client.send_message("/population/centroid/y", float(metrics.centroid[1]))
    client.send_message("/population/centroid/z", float(metrics.centroid[2]))

    client.send_message("/population/spread/x", float(metrics.spread[0]))
    client.send_message("/population/spread/y", float(metrics.spread[1]))
    client.send_message("/population/spread/z", float(metrics.spread[2]))

    client.send_message("/population/purity", float(metrics.mean_purity))
    client.send_message("/population/purity_std", float(metrics.purity_std))

    client.send_message("/population/entropy", float(metrics.mean_entropy))
    client.send_message("/population/entropy_std", float(metrics.entropy_std))

    client.send_message("/population/coherence", float(metrics.coherence))
    client.send_message("/population/activity", float(metrics.active_fraction))
    client.send_message("/population/outlier_count", len(metrics.outliers))
    
    client.send_message("/population/coupling", float(coupling_strength))

    
    
    # Outlier impulses.
    for index in metrics.outliers:
        client.send_message("/population/outlier", int(index))
        
        
    # Individual selected voices.
    audible_members = population.get_loudest_members(audible_voice_count)

    for voice_number, member_index in enumerate(audible_members):
        member = population.get_member(member_index)
        
                # --------------------------------------------------------
        # QUANTUM FEATURE OUTPUT
        # --------------------------------------------------------

            # Outlier impulses.
    for index in metrics.outliers:
        client.send_message("/population/outlier", int(index))

    # Individual selected voices.
    audible_members = population.get_loudest_members(audible_voice_count)

    for voice_number, member_index in enumerate(audible_members):
        member = population.get_member(member_index)

        x = float(member.get("bloch_x", 0.0))
        y = float(member.get("bloch_y", 0.0))
        z = float(member.get("bloch_z", 0.0))
        purity = float(member.get("purity", 0.0))
        entropy = float(member.get("entropy", 0.0))

        base = f"/voice/{voice_number}"

        client.send_message(f"{base}/member_id", int(member_index))
        client.send_message(f"{base}/x", x)
        client.send_message(f"{base}/y", y)
        client.send_message(f"{base}/z", z)
        client.send_message(f"{base}/purity", purity)
        client.send_message(f"{base}/entropy", entropy)

        q = member.get("quantum_features", {})

                

        if q:
            local_bloch = q.get("local_bloch", [])
            local_purities = q.get("local_purities", [])
            local_entropies = q.get("local_entropies", [])

            for qubit_index, bloch in enumerate(local_bloch):
                qubit_base = f"{base}/qubit/{qubit_index}"

                client.send_message(
                    f"{qubit_base}/x",
                    float(bloch[0]),
                )
                client.send_message(
                    f"{qubit_base}/y",
                    float(bloch[1]),
                )
                client.send_message(
                    f"{qubit_base}/z",
                    float(bloch[2]),
                )

                if qubit_index < len(local_purities):
                    client.send_message(
                        f"{qubit_base}/purity",
                        float(local_purities[qubit_index]),
                    )

                if qubit_index < len(local_entropies):
                    client.send_message(
                        f"{qubit_base}/entropy",
                        float(local_entropies[qubit_index]),
                    )

        x = float(member.get("bloch_x", 0.0))
        y = float(member.get("bloch_y", 0.0))
        z = float(member.get("bloch_z", 0.0))
        purity = float(member.get("purity", 0.0))
        entropy = float(member.get("entropy", 0.0))

        base = f"/voice/{voice_number}"

        client.send_message(f"{base}/member_id", int(member_index))
        client.send_message(f"{base}/x", x)
        client.send_message(f"{base}/y", y)
        client.send_message(f"{base}/z", z)
        client.send_message(f"{base}/purity", purity)
        client.send_message(f"{base}/entropy", entropy)



class LiveControls:
    """
    Thread-safe values updated by incoming OSC from Max.
    """

    def __init__(self, coupling: float = 0.02):
        self._lock = threading.Lock()
        self._coupling = float(np.clip(coupling, 0.0, 1.0))

    def set_coupling(self, address: str, value: float):
        value = float(value)
        
        value = float(np.clip(value, 0.0, 0.08))

        with self._lock:
            self._coupling = value

        print(f"Live coupling: {value:.4f}")

    def get_coupling(self) -> float:
        with self._lock:
            return self._coupling

def start_osc_control_server(
    controls: LiveControls,
    host: str = "127.0.0.1",
    port: int = 7401,
):
    dispatcher = Dispatcher()

    def debug_handler(address, *args):
        print(f"OSC received: {address} {args}")

    dispatcher.set_default_handler(debug_handler)
    dispatcher.map("/population/coupling", controls.set_coupling)
    dispatcher.map("/coupling", controls.set_coupling)

    server = ThreadingOSCUDPServer((host, port), dispatcher)

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    print(f"Listening for OSC control on {host}:{port}")
    return server

# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

def main():
    OSC_HOST = "127.0.0.1"
    OSC_PORT = 7400
    CONTROL_PORT = 7401

    POPULATION_SIZE = 32
    AUDIBLE_VOICES = 8

    DT = 0.03
    OSC_INTERVAL = 0.05
    INITIAL_COUPLING = 0.02

    client = SimpleUDPClient(OSC_HOST, OSC_PORT)

    controls = LiveControls(coupling=INITIAL_COUPLING)
    


    control_server = start_osc_control_server(
        controls=controls,
        host=OSC_HOST,
        port=CONTROL_PORT,
    )

    population = PopulationEngine(
        engine_factory=make_engine,
        population_size=POPULATION_SIZE,
    
        seed=1234,
    )

    print("Quantum population engine running.")
    print(f"Population size: {POPULATION_SIZE}")
    print(f"Audible voices: {AUDIBLE_VOICES}")

    last_osc_time = 0.0

    try:
        while True:
            coupling = controls.get_coupling()

            metrics = population.step(
                DT,
                coupling_strength=coupling,
            )

            now = time.time()

            if now - last_osc_time >= OSC_INTERVAL:
                send_population_osc(
                    client=client,
                    population=population,
                    metrics=metrics,
                    coupling_strength=coupling,
                    audible_voice_count=AUDIBLE_VOICES,
                )

                print(
                    f"coherence={metrics.coherence:.3f} "
                    f"distance={metrics.mean_distance:.4f} "
                    f"purity={metrics.mean_purity:.3f} "
                    f"entropy={metrics.mean_entropy:.3f} "
                    f"activity={metrics.active_fraction:.3f} "
                    f"outliers={len(metrics.outliers)} "
                    f"coupling={coupling:.3f}"
                )

                last_osc_time = now

            time.sleep(DT)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        control_server.shutdown()
        control_server.server_close()


if __name__ == "__main__":
    main()