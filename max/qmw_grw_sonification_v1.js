autowatch = 1;
inlets = 1;
outlets = 8;

// Outlets 0..3: one event-control list per affected-qubit branch.
// Outlet 4: persistent rho+ branch levels.
// Outlet 5: post-event populations.
// Outlet 6: normalized |rho+| matrix.
// Outlet 7: status text.

function event() {
    var values = arrayfromargs(arguments);
    if (values.length < 10) return;

    var eventId = values[0];
    var branch = Math.max(0, Math.min(3, values[1] | 0));
    var amplitude = values[2];
    var coherenceLoss = values[3];
    var bandwidth = values[4];
    var grain = values[5];
    var axis = values[6];
    var sign = values[7];
    var pauliDelta = values[8];
    var audible = values[9] | 0;

    if (audible) {
        outlet(branch, [
            amplitude,
            bandwidth,
            grain,
            axis,
            sign,
            pauliDelta
        ]);
    }
    outlet(7, "set", "GRW event " + eventId +
        " | q" + branch +
        " | amp " + Number(amplitude).toFixed(3) +
        " | coherence loss " + Number(coherenceLoss).toFixed(3));
}

function branch_levels() {
    outlet(4, arrayfromargs(arguments).slice(0, 4));
}

function population() {
    outlet(5, arrayfromargs(arguments).slice(0, 16));
}

function rho_magnitude() {
    outlet(6, arrayfromargs(arguments).slice(0, 256));
}

function pauli() {
    var values = arrayfromargs(arguments);
    if (values.length >= 3) {
        outlet(7, "set", "Pauli " + values[0] +
            " | axis " + values[1] +
            " | delta " + Number(values[2]).toFixed(4));
    }
}
