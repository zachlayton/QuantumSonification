autowatch = 1;
inlets = 1;
outlets = 1;

var modeNames = ["m5", "m4", "m3", "m2", "m1", "m0", "p1", "p2", "p3", "p4", "p5"];

function list() {
    var values = arrayfromargs(arguments);
    if (values.length < 40) {
        post("qmw_bloch_event_to_gen: expected 40 values, received " + values.length + "\n");
        return;
    }
    var eventId = values[0];
    outlet(0, "eventkind", values[1]);
    outlet(0, "eventamp", values[3]);
    outlet(0, "fidelity", values[4]);
    outlet(0, "participation", values[5]);
    outlet(0, "current", values[6]);
    for (var index = 0; index < 11; index++) {
        outlet(0, "pop" + modeNames[index], values[7 + index]);
        outlet(0, "phase" + modeNames[index], values[18 + index]);
        outlet(0, "speed" + modeNames[index], values[29 + index]);
    }
    // Event ID is deliberately last: its change strikes the prepared body.
    outlet(0, "eventid", eventId);
}
