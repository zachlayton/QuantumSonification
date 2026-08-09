// Optional local rotation layer for arbitrary QAC designer circuits.
// A selected RX/RY/RZ(pi*theta) is inserted immediately before measurement.
autowatch = 1;
inlets = 1;
outlets = 2; // transformed QASM, status

var enabled = 1;
var axis = "ry";
var normalizedTheta = 0.5;
var targetQubit = 0;

function rx() { axis = "rx"; report(); }
function ry() { axis = "ry"; report(); }
function rz() { axis = "rz"; report(); }

function theta(value) {
    normalizedTheta = Math.max(0.0, Math.min(1.0, Number(value)));
    report();
}

function target(value) {
    targetQubit = Math.max(0, Math.floor(Number(value)));
    report();
}

function enable(value) {
    enabled = Number(value) !== 0;
    report();
}

function report() {
    outlet(1, ["rotation_layer", enabled ? "on" : "off", axis,
        "theta_over_pi", normalizedTheta, "target", targetQubit]);
}

function atomsToText(args, includeName) {
    var items = [];
    if (includeName) items.push(messagename);
    for (var i = 0; i < args.length; i++) items.push(String(args[i]));
    return items.join(" ");
}

function qasm() {
    transform(atomsToText(arrayfromargs(arguments), false));
}

function anything() {
    var text = atomsToText(arrayfromargs(arguments), true);
    if (/^OPENQASM\b/i.test(text)) transform(text);
}

function transform(text) {
    if (!enabled) {
        outlet(0, ["qasm", text]);
        outlet(1, ["rotation_layer", "bypassed"]);
        return;
    }
    var register = /qreg\s+q\s*\[\s*(\d+)\s*\]\s*;/i.exec(text);
    if (!register) {
        outlet(1, ["error", "rotation_layer_qreg_q_not_found"]);
        return;
    }
    var qubits = Number(register[1]);
    if (targetQubit >= qubits) {
        outlet(1, ["error", "rotation_target_out_of_range", targetQubit, qubits]);
        return;
    }
    var angle = normalizedTheta * Math.PI;
    var gate = axis + "(" + angle.toFixed(12) + ") q[" + targetQubit + "]; ";
    var measurement = /\bmeasure\b/i.exec(text);
    var transformed = measurement
        ? text.slice(0, measurement.index) + gate + text.slice(measurement.index)
        : text + " " + gate;
    outlet(0, ["qasm", transformed]);
    outlet(1, ["rotation_applied", axis, "theta_over_pi", normalizedTheta,
        "target", targetQubit]);
}
