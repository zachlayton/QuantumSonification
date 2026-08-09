// Build a parameterized two-qubit entangling circuit for the workshop.
// Inlet: float 0..1 stores theta/pi; bang sends QASM.
// Outlets: complete `qasm <text>` message, status.
autowatch = 1;
inlets = 1;
outlets = 2;

var normalizedTheta = null;
var axis = "ry";

function rx() { axis = "rx"; outlet(1, ["axis", axis]); }
function ry() { axis = "ry"; outlet(1, ["axis", axis]); }
function rz() { axis = "rz"; outlet(1, ["axis", axis, "uses_H_before_RZ"]); }

function msg_float(value) {
    normalizedTheta = Math.max(0.0, Math.min(1.0, Number(value)));
    outlet(1, ["theta", normalizedTheta, "radians", normalizedTheta * Math.PI]);
}

function bang() {
    if (normalizedTheta === null) {
        outlet(1, ["error", "set_theta_before_sending"]);
        return;
    }
    var theta = normalizedTheta * Math.PI;
    var preparation = axis === "rz"
        ? "h q[0]; rz(" + theta.toFixed(12) + ") q[0]; "
        : axis + "(" + theta.toFixed(12) + ") q[0]; ";
    var qasm = "OPENQASM 2.0; include \"qelib1.inc\"; " +
        "qreg q[2]; creg c[2]; " + preparation +
        "cx q[0],q[1]; " +
        "measure q[0] -> c[0]; measure q[1] -> c[1];";
    outlet(0, ["qasm", qasm]);
    outlet(1, ["sent", axis, "theta_over_pi", normalizedTheta]);
}

function set(value) {
    msg_float(value);
}
