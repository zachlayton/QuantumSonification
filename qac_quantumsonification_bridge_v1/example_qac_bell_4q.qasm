OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];

// Bell pair on q0/q1; q0 is the least-significant basis bit.
h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
