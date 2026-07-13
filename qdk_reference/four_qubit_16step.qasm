// Canonical 4-qubit / 16-step circuit score for QuantumSonification.
//
// This file is intentionally readable in the QDK VS Code circuit viewer.
// It is a reference circuit: the MLX engine remains the real-time engine.
// Keep gate order and parameter values synchronized with
// qdk_reference_simulator.py and, later, QMWCircuitBridge.

OPENQASM 3.0;
include "stdgates.inc";

qubit[4] q;
bit[4] c;

// Step 00–03: local preparation
h  q[0];
ry(0.370000) q[1];
rx(-0.510000) q[2];
rz(0.290000) q[3];

// Step 04–07: first entangling weave
cx q[0], q[1];
rz(0.730000) q[1];
cx q[1], q[2];
ry(-0.440000) q[2];

// Step 08–11: phase circulation
cx q[2], q[3];
rx(0.610000) q[3];
cz q[3], q[0];
ry(0.220000) q[0];

// Step 12–15: closure and interference
cx q[0], q[2];
rz(-0.680000) q[2];
cx q[1], q[3];
h  q[3];

// Measurement is deliberately separated from the unitary score.
// Uncomment only when you want sampled bitstrings rather than rho:
// c = measure q;
