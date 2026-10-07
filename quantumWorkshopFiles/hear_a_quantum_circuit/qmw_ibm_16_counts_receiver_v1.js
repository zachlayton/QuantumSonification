// Format the compact four-qubit IBM OSC replies for the workshop patch.
autowatch = 1;
inlets = 1;
outlets = 2; // 16 probabilities, participant-facing status

var NUM_OUTCOMES = 16;

function probabilities() {
    var args = arrayfromargs(arguments);
    if (args.length !== NUM_OUTCOMES + 2) {
        outlet(1, "set", "IBM reply rejected: expected 16 probabilities");
        return;
    }
    var revision = Number(args[0]);
    var source = String(args[1]);
    var values = [];
    var total = 0;
    for (var i = 0; i < NUM_OUTCOMES; i++) {
        var value = Math.max(0, Number(args[i + 2]) || 0);
        values.push(value);
        total += value;
    }
    if (total <= 0) {
        outlet(1, "set", "IBM reply rejected: probability total is zero");
        return;
    }
    for (i = 0; i < NUM_OUTCOMES; i++) values[i] /= total;
    outlet(0, values);
    outlet(1, "set", source.toUpperCase() + " 16 outcomes received · revision " + revision);
}

function status() {
    var args = arrayfromargs(arguments);
    if (!args.length) return;
    var stage = String(args[0]);
    if (stage === "ready") {
        outlet(1, "set", "Bridge ready · " + String(args[1]).toUpperCase() + " mode");
    } else if (stage === "receiving_qasm") {
        outlet(1, "set", "Receiving QAC/QASM · revision " + args[1]);
    } else if (stage === "qasm_validated") {
        outlet(1, "set", "Four-qubit QASM validated · revision " + args[1]);
    } else if (stage === "selecting_backend") {
        outlet(1, "set", "Selecting IBM backend…");
    } else if (stage === "submitted") {
        outlet(
            1,
            "set",
            "IBM submitted · " + args[2] + " · job " + args[3]
                + " · " + args[4] + " shots"
        );
    } else if (stage === "complete") {
        outlet(1, "set", String(args[2]).toUpperCase() + " measurement complete");
    } else {
        outlet(1, "set", args.join(" "));
    }
}

function result() {
    var args = arrayfromargs(arguments);
    if (args.length < 5) return;
    var source = String(args[1]).toUpperCase();
    var backend = String(args[2]);
    var job = String(args[3]);
    var shots = Number(args[4]);
    outlet(
        1,
        "set",
        source + " result · " + backend
            + (job !== "none" ? " · job " + job : "")
            + (shots > 0 ? " · " + shots + " shots" : "")
    );
}

function error() {
    var args = arrayfromargs(arguments);
    outlet(1, "set", "ERROR · " + args.join(" "));
}
