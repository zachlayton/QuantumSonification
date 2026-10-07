"""Bounded, read-only resource diagnostics with explicit adequacy boundaries.

See docs/qmw_architecture/RESOURCE_DEFINITIONS.md for primary definitions and
limits. A basis coherence measure, a bipartite entanglement measure, a Pauli
nonstabilizerness measure, and a contextuality scenario are distinct objects.
This observer never creates a state from a correlation matrix or counts.
"""
from __future__ import annotations

import hashlib
from itertools import product
import json
import math
from types import MappingProxyType

import numpy as np

from qmw.core.quantum_spectrum import analyze_quantum_spectrum
from qmw.qmw_representation_laboratory_v4.observables import pauli_expectation

from .contracts import BasisMetadata, FeatureFrame, FeatureId, FeatureValue, finite, nonempty, plain


VERSION = "1"
DEFAULT_METRICS = ("purity", "entropy_nats", "coherence_l1", "coherence_relative_entropy_nats")
_BIPARTITE = frozenset({"negativity", "log_negativity", "reduced_entropy_nats", "entanglement_entropy_nats"})
_PAULI = frozenset({"stabilizer_renyi2_bits", "stabilizer_diagnostics"})
SUPPORTED_METRICS = frozenset(DEFAULT_METRICS) | _BIPARTITE | _PAULI | {"contextuality"}
_ORTHONORMAL = frozenset({"computational", "hamiltonian", "qho", "qft", "geometry", "orthonormal", "custom_unitary"})
COHERENCE_SOURCE = "https://arxiv.org/html/1311.0275v3"
ENTANGLEMENT_SOURCE = "https://arxiv.org/html/quant-ph/0102117v1"
MAGIC_SOURCE = "https://arxiv.org/html/2106.12587v5"
MAGIC_LIMITS_SOURCE = "https://arxiv.org/html/2404.11652v3"
CONTEXTUALITY_SOURCE = "https://arxiv.org/html/1401.4174v2"


def _entropy(values, tolerance):
    # Same explicitly thresholded policy as the canonical spectral observer.
    positive = np.asarray(values, float)
    positive = positive[positive > tolerance]
    return float(-np.sum(positive*np.log(positive)))


def _factorization(dimensions, partition, dimension):
    if dimensions is None:
        if partition is not None:
            raise ValueError("partition requires explicit subsystem dimensions")
        return None, None
    dimensions = tuple(dimensions)
    if (not dimensions or any(isinstance(d, (bool, np.bool_)) or not isinstance(d, (int, np.integer))
                              or d < 2 for d in dimensions) or math.prod(dimensions) != dimension):
        raise ValueError("subsystem dimensions must be integers >= 2 with product equal to rho dimension")
    dimensions = tuple(int(d) for d in dimensions)
    if partition is None:
        return dimensions, None
    partition = tuple(partition)
    if (not partition or any(isinstance(q, (bool, np.bool_)) or not isinstance(q, (int, np.integer))
                             or q < 0 or q >= len(dimensions) for q in partition)
            or len(set(partition)) != len(partition) or len(partition) == len(dimensions)):
        raise ValueError("partition must be a nonempty proper subset of distinct subsystem indices")
    return dimensions, tuple(sorted(int(q) for q in partition))


def _bipartite_tensor(density, dimensions, partition):
    """Group A,B row/column axes; subsystem zero is least significant."""
    n = len(dimensions)
    a_qubits = tuple(sorted(partition, reverse=True))
    b_qubits = tuple(q for q in reversed(range(n)) if q not in partition)
    a_axes = tuple(n-1-q for q in a_qubits)
    b_axes = tuple(n-1-q for q in b_qubits)
    axes = a_axes + b_axes + tuple(n+q for q in a_axes) + tuple(n+q for q in b_axes)
    d_a = math.prod(dimensions[q] for q in partition)
    d_b = density.shape[0]//d_a
    tensor = density.reshape(tuple(reversed(dimensions))*2).transpose(axes)
    return tensor.reshape(d_a, d_b, d_a, d_b), axes


class ResourceAnalyzer:
    """Observe a density feature without evolution or hidden representation changes.

    Tensor structure is caller-declared, never inferred from a 16x16 shape.
    Dimensions list subsystem 0 first, with that subsystem least significant
    in the coordinate index. ``partition`` identifies party A; its complement
    is B. Tensor/Pauli measures require computational q0_lsb coordinates.

    Enumeration of all Pauli strings is optional and defaults to four qubits.
    Unsupported measures remain typed missing outputs with explanatory reasons.
    Invalid data and contradictory declarations instead raise ValueError.
    """

    def __init__(self, *, max_dimension=64, max_magic_qubits=4, tolerance=1e-10):
        if (isinstance(max_dimension, (bool, np.bool_)) or not isinstance(max_dimension, int)
                or not 2 <= max_dimension <= 256):
            raise ValueError("max_dimension must be an integer in [2,256]")
        if (isinstance(max_magic_qubits, (bool, np.bool_)) or not isinstance(max_magic_qubits, int)
                or not 1 <= max_magic_qubits <= 6):
            raise ValueError("max_magic_qubits must be an integer in [1,6]")
        tolerance = finite(tolerance, "tolerance")
        if not 0 < tolerance <= 1e-6:
            raise ValueError("tolerance must be positive and <= 1e-6")
        self.configuration = MappingProxyType(dict(max_dimension=max_dimension,
            max_magic_qubits=max_magic_qubits, tolerance=tolerance))

    def analyze(self, rho: FeatureValue, *, metrics=None, subsystem_dimensions=None,
                partition=None, frame_id=None) -> FeatureFrame:
        if not isinstance(rho, FeatureValue) or rho.id.quantity != "density_matrix" or rho.id.kind != "matrix":
            raise ValueError("ResourceAnalyzer requires a typed density_matrix matrix feature")
        raw = rho.require_available()
        if rho.units not in ("1", "dimensionless"):
            raise ValueError("rho requires dimensionless units")
        density = np.asarray(raw, complex)
        if density.ndim != 2 or density.shape[0] != density.shape[1] or density.shape[0] < 1:
            raise ValueError("rho must be a nonempty square matrix")
        d = density.shape[0]
        if d > self.configuration["max_dimension"]:
            raise ValueError("rho exceeds the configured resource dimension cap")
        if rho.provenance.basis.dimension != d:
            raise ValueError("rho and declared basis dimension differ")
        if rho.provenance.basis.kind not in _ORTHONORMAL:
            raise ValueError("resource measures require declared orthonormal density coordinates")
        if isinstance(metrics, str):
            raise ValueError("metrics must be a sequence of distinct metric names")
        requested = DEFAULT_METRICS if metrics is None else tuple(metrics)
        if len(set(requested)) != len(requested) or any(m not in SUPPORTED_METRICS for m in requested):
            raise ValueError("unknown or duplicate resource metric")
        dims, part = _factorization(subsystem_dimensions, partition, d)
        tolerance = self.configuration["tolerance"]
        # Canonical validation is reused without inventing a Hamiltonian source:
        # the all-zero matrix is solely this API's required auxiliary argument.
        spectrum = analyze_quantum_spectrum(density, np.zeros_like(density), tolerance=tolerance,
                                            degeneracy_tolerance=tolerance)
        pure_state = (abs(spectrum.purity-1) <= 2*tolerance
                      and np.sum(np.maximum(spectrum.density_eigenvalues[:-1], 0)) <= tolerance)
        context = {"source_feature": rho.id.to_dict(), "configuration": self.configuration,
            "subsystem_dimensions": dims, "partition_A": part,
            "index_convention": "subsystem0_least_significant_mixed_radix",
            "input_uncertainty": rho.uncertainty,
            "pure_within_tolerance": bool(pure_state),
            "numerical_policy": "canonical rho validation; entropy includes eigenvalues > tolerance; no state repair or renormalization"}
        if frame_id is None:
            digest = hashlib.sha256(json.dumps(plain({"source": rho.provenance.digest,
                "context": context, "metrics": requested}), sort_keys=True,
                separators=(",", ":")).encode()).hexdigest()
            frame_id = f"{rho.provenance.record_id}:resources:{digest}"
        else:
            nonempty(frame_id, "frame_id")
        spectral_p = rho.provenance.derive(frame_id+":spectrum", "qmw.core.quantum_spectrum", VERSION,
            context | {"eigenvalues": spectrum.density_eigenvalues,
                "auxiliary_hamiltonian": "zero API placeholder for density-only validation; no dynamics"},
            units="1", normalization="none")
        diagonal = np.real(np.diag(density))
        diagonal_p = rho.provenance.derive(frame_id+":diagonal", "diagonal_in_declared_basis", VERSION,
            context | {"diagonal": diagonal}, units="1", normalization="none")
        uncertainty = None if rho.uncertainty is None else {
            "kind": "nonlinear_input_uncertainty", "status": "not_propagated",
            "input": rho.uncertainty, "input_units": rho.units,
            "reason": "no estimator/covariance propagation model declared"}
        outputs = []

        def emit(name, value, formula, *, units="1", parents=None, source="canonical spectral definition",
                 limits="", extra=None, reason=None, kind="scalar"):
            parent_nodes = (rho.provenance,) if parents is None else tuple(parents)
            p = parent_nodes[0].derive(frame_id+":"+name, "resource_analysis."+name, VERSION,
                context | {"formula": formula, "definition_source": source, "limits": limits, **(extra or {})},
                units=units, normalization="none", parents=parent_nodes, source_path="resources."+name,
                evidence="derived" if reason is None else "capability_report")
            outputs.append(FeatureValue(FeatureId("resources."+name, name, kind), value, p,
                availability="available" if reason is None else "unsupported", reason=reason,
                uncertainty=uncertainty if reason is None else None))

        tensor_reason = None
        if dims is None:
            tensor_reason = "explicit subsystem dimensions required; tensor structure is not inferred from matrix size"
        elif rho.provenance.basis.kind != "computational" or rho.provenance.basis.subsystem_order != "q0_lsb":
            tensor_reason = "tensor/Pauli diagnostics require computational q0_lsb coordinates; undo a global basis transform first"
        grouped = grouped_p = pt_p = reduced_p = pt_values = reduced_values = None
        if set(requested) & _BIPARTITE and tensor_reason is None and part is not None:
            grouped, axes = _bipartite_tensor(density, dims, part)
            grouped_p = rho.provenance.derive(frame_id+":bipartition", "declared_tensor_regrouping", VERSION,
                context | {"tensor_axis_permutation": axes, "grouped_shape": grouped.shape}, units="1")
            pt = grouped.transpose(2, 1, 0, 3).reshape(d, d)
            pt_values = np.linalg.eigvalsh(pt)
            pt_p = grouped_p.derive(frame_id+":partial_transpose", "partial_transpose_A", VERSION,
                {"eigenvalues": pt_values, "partition_A": part}, units="1")
            reduced = np.trace(grouped, axis1=1, axis2=3)
            reduced_values = np.linalg.eigvalsh(reduced)
            reduced_basis = BasisMetadata(rho.provenance.basis.basis_id+":reduced:"+",".join(map(str, part)),
                reduced.shape[0], "computational", "q0_lsb", details={
                    "original_subsystem_indices": part, "dimensions": tuple(dims[q] for q in part),
                    "source_basis": rho.provenance.basis.to_dict()})
            reduced_p = grouped_p.derive(frame_id+":reduced_density", "partial_trace_B", VERSION,
                {"eigenvalues": reduced_values, "partition_A": part}, units="1", basis=reduced_basis)

        pauli_reason = tensor_reason
        if pauli_reason is None and any(size != 2 for size in dims):
            pauli_reason = "this stabilizer diagnostic supports qubit tensor factors only"
        if pauli_reason is None and not pure_state:
            pauli_reason = "mixed-state magic/stabilizer classification is unsupported; no convex-roof extension implemented"
        if pauli_reason is None and len(dims) > self.configuration["max_magic_qubits"]:
            pauli_reason = "Pauli enumeration exceeds configured magic qubit cap"
        pauli_p = expectations = moment = None
        if set(requested) & _PAULI and pauli_reason is None:
            labels = tuple("".join(chars) for chars in product("IXYZ", repeat=len(dims)))
            expectations = np.array([pauli_expectation(density, label) for label in labels])
            moment = float(np.sum(expectations**4)/d)
            if not 0 < moment <= 1+8*tolerance:
                raise ValueError("pure-state Pauli fourth moment inconsistent with admitted rho")
            pauli_p = rho.provenance.derive(frame_id+":pauli_expectations", "qmw.pauli_expectations", VERSION,
                context | {"labels_q0_first": labels, "expectations": expectations,
                    "reuse": "qmw.qmw_representation_laboratory_v4.observables.pauli_expectation",
                    "identity_included": True, "phase_representatives": "+1 Hermitian IXYZ strings"}, units="1")

        for name in requested:
            if name == "purity":
                emit(name, spectrum.purity, "Re Tr(rho @ rho)", parents=(spectral_p,))
            elif name == "entropy_nats":
                emit(name, spectrum.entropy, "-sum(lambda*ln(lambda), lambda>tolerance)",
                     units="nat", parents=(spectral_p,))
            elif name == "coherence_l1":
                offdiag = density-np.diag(np.diag(density))
                emit(name, float(np.sum(np.abs(offdiag))), "sum_{i!=j} abs(rho_ij)",
                     source=COHERENCE_SOURCE, limits="basis dependent; unnormalized maximum d-1")
            elif name == "coherence_relative_entropy_nats":
                amount = _entropy(diagonal, tolerance)-spectrum.entropy
                if amount < -8*tolerance*d:
                    raise ValueError("relative entropy coherence inconsistent with admitted density")
                emit(name, max(0., amount), "S(diagonal(rho))-S(rho)", units="nat",
                     parents=(diagonal_p, spectral_p), source=COHERENCE_SOURCE,
                     limits="basis dependent; natural logarithm; numerical negative roundoff floored at zero")
            elif name in _BIPARTITE:
                reason = tensor_reason or ("explicit nonempty proper partition required" if part is None else None)
                if name == "entanglement_entropy_nats" and reason is None and not pure_state:
                    reason = "entanglement entropy requires a globally pure state; reduced mixed-state entropy is not entanglement"
                units = "nat" if "entropy_nats" in name else "bit" if name == "log_negativity" else "1"
                formulas = {"negativity": "sum(max(-eig(rho^T_A),0))",
                    "log_negativity": "log2(norm1(rho^T_A))",
                    "reduced_entropy_nats": "S(Tr_B(rho))",
                    "entanglement_entropy_nats": "S(Tr_B(rho)) for globally pure rho"}
                if reason is not None:
                    emit(name, None, formulas[name], units=units, source=ENTANGLEMENT_SOURCE, reason=reason)
                elif name in ("negativity", "log_negativity"):
                    amount = float(np.sum(np.maximum(-pt_values, 0))) if name == "negativity" else max(0., float(np.log2(np.sum(np.abs(pt_values)))))
                    emit(name, amount, formulas[name], units=units, parents=(pt_p,), source=ENTANGLEMENT_SOURCE,
                        limits="bipartite only; zero negativity does not certify separability in arbitrary dimensions",
                        extra={"partial_transpose_minimum_eigenvalue": float(pt_values.min()),
                               "trace_norm": float(np.sum(np.abs(pt_values)))})
                else:
                    emit(name, _entropy(reduced_values, tolerance), formulas[name], units=units,
                        parents=(reduced_p,), source=ENTANGLEMENT_SOURCE,
                        limits="entanglement meaning only when global rho is pure; reduced entropy otherwise")
            elif name in _PAULI:
                formula = "-log2(sum_P(Tr(rho P)^4)/d)" if name == "stabilizer_renyi2_bits" else "count_P(abs(abs(Tr(rho P))-1)<=tolerance)"
                if pauli_reason is not None:
                    emit(name, None, formula, units="bit" if name == "stabilizer_renyi2_bits" else "1",
                         source=MAGIC_SOURCE, reason=pauli_reason,
                         kind="scalar" if name == "stabilizer_renyi2_bits" else "record")
                elif name == "stabilizer_renyi2_bits":
                    emit(name, max(0., -float(np.log2(moment))), formula, units="bit", parents=(pauli_p,),
                         source=MAGIC_SOURCE, limits="pure-qubit deterministic stabilizer monotone; not strong on-average monotonicity or mixed-state magic",
                         extra={"limits_source": MAGIC_LIMITS_SOURCE, "normalized_pauli_fourth_moment": moment})
                else:
                    count = int(np.count_nonzero(np.abs(np.abs(expectations)-1) <= tolerance))
                    emit(name, {"qubits": len(dims), "pauli_terms": d*d,
                        "signed_stabilizer_count": count,
                        "is_stabilizer_within_tolerance": count == d and abs(moment-1) <= 8*tolerance,
                        "normalized_pauli_fourth_moment": moment,
                        "pauli_purity_residual": abs(float(np.sum(expectations**2)/d)-spectrum.purity),
                        "classification": "pure_state_pauli_diagnostic", "tolerance": tolerance},
                        formula, kind="record", parents=(pauli_p,), source=MAGIC_SOURCE,
                        limits="finite-tolerance diagnostic; no mixed-state stabilizer decomposition or magic cost")
            else:
                emit(name, None, "requires a declared compatibility/exclusivity scenario and inequality",
                    source=CONTEXTUALITY_SOURCE,
                    reason="contextuality requires a measurement scenario, compatibility assumptions, and an inequality; rho or magic alone is insufficient")
        return FeatureFrame(frame_id, tuple(outputs), {
            "analyzer": "ResourceAnalyzer", "version": VERSION, "configuration": self.configuration,
            "requested_metrics": requested, "pure_within_tolerance": bool(pure_state),
            "capabilities": {f.id.quantity: {"availability": f.availability, "reason": f.reason} for f in outputs},
            "state_evolution": False, "rho_reconstruction": False})


__all__ = ["ResourceAnalyzer", "DEFAULT_METRICS", "SUPPORTED_METRICS"]
