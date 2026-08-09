autowatch = 1;
inlets = 1;
outlets = 5;

var addresses = [
    {ml: -1, spin: -1, label: "(2,1,-1,down)"},
    {ml: -1, spin:  1, label: "(2,1,-1,up)"},
    {ml:  0, spin: -1, label: "(2,1,0,down)"},
    {ml:  0, spin:  1, label: "(2,1,0,up)"},
    {ml:  1, spin: -1, label: "(2,1,1,down)"},
    {ml:  1, spin:  1, label: "(2,1,1,up)"}
];
var occupied = [0, 0, 0, 0, 0, 0];
var fieldT = 1.0;
var baseHz = 220.0;
var orbitalSpacingHz = 24.0;
var zeemanHzPerT = 30.0;
var rawRingMix = 1.0;
var fmIndex = 0.0;
var rotationDegrees = 0.0;
var stateOverlap = 0.0;
var rejected = 0;

function clamp(value, low, high) {
    return Math.max(low, Math.min(high, Number(value)));
}

function validIndex(value) {
    var index = Math.floor(Number(value));
    return index >= 0 && index < addresses.length ? index : -1;
}

function fill() {
    for (var i = 0; i < occupied.length; i++) {
        occupied[i] = 1;
    }
    update("CLOSED 2p SUBSHELL: six distinct addresses, net magnetic factor = 0");
}

function clear() {
    for (var i = 0; i < occupied.length; i++) {
        occupied[i] = 0;
    }
    update("LEDGER CLEARED");
}

function toggle(value) {
    var index = validIndex(value);
    if (index < 0) return;
    occupied[index] = occupied[index] ? 0 : 1;
    update(occupied[index] ? "OCCUPIED " + addresses[index].label : "RELEASED " + addresses[index].label);
}

function occupy(value) {
    var index = validIndex(value);
    if (index < 0) return;
    if (occupied[index]) {
        rejected += 1;
        update("EXCLUDED: " + addresses[index].label + " is already occupied; rejected attempts=" + rejected);
        return;
    }
    occupied[index] = 1;
    update("OCCUPIED " + addresses[index].label);
}

function field(value) {
    fieldT = clamp(value, 0.0, 20.0);
    update();
}

function base(value) {
    baseHz = clamp(value, 30.0, 8000.0);
    update();
}

function orbital(value) {
    orbitalSpacingHz = clamp(value, 0.0, 1000.0);
    update();
}

function zeeman(value) {
    zeemanHzPerT = clamp(value, 0.0, 1000.0);
    update();
}

function raw(value) {
    rawRingMix = clamp(value, 0.0, 1.0);
    update();
}

function index(value) {
    fmIndex = clamp(value, 0.0, 12.0);
    update();
}

function rotate(value) {
    rotationDegrees = clamp(value, 0.0, 720.0);
    update();
}

function overlap(value) {
    stateOverlap = clamp(value, 0.0, 1.0);
    update();
}

function bang() {
    update();
}

function update(message) {
    var count = 0;
    var magneticSum = 0.0;
    var i;
    for (i = 0; i < occupied.length; i++) {
        count += occupied[i];
        if (occupied[i]) magneticSum += addresses[i].ml + addresses[i].spin;
    }
    var voiceGain = count > 0 ? 0.46 / Math.sqrt(count) : 0.0;

    for (i = 0; i < addresses.length; i++) {
        var state = addresses[i];
        var displacement = orbitalSpacingHz * state.ml +
            fieldT * zeemanHzPerT * (state.ml + state.spin);
        var pan = clamp(0.62 * state.ml + 0.16 * state.spin, -0.95, 0.95);
        outlet(0, "target", i + 1);
        outlet(0, "carrier", baseHz);
        outlet(0, "shift", Math.abs(displacement));
        outlet(0, "side", displacement < 0.0 ? -1.0 : 1.0);
        outlet(0, "raw", rawRingMix);
        outlet(0, "index", fmIndex);
        outlet(0, "pan", pan);
        outlet(0, "gain", occupied[i] ? voiceGain : 0.0);
    }

    outlet(1, occupied);

    // Equal-path interference against the unrotated reference spinor.
    // I = [1 + cos(theta/2)] / 2: zero at 2pi, return at 4pi.
    var angleRadians = rotationDegrees * Math.PI / 180.0;
    var spinIntensity = 0.5 * (1.0 + Math.cos(angleRadians / 2.0));
    outlet(2, 0.24 * Math.sqrt(Math.max(0.0, spinIntensity)));

    // Norm of the normalized Slater wedge for total one-state overlap s.
    var wedgeNorm = Math.sqrt(Math.max(0.0, 1.0 - stateOverlap * stateOverlap));
    outlet(3, 0.24 * wedgeNorm);

    var status = message || (
        "RING BANK raw=" + rawRingMix.toFixed(2) + " FM index=" + fmIndex.toFixed(2) +
        " | occupied=" + count + "/6 | sum(m_l+2m_s)=" + magneticSum.toFixed(1) +
        " | spin rotation=" + rotationDegrees.toFixed(1) + " deg | Slater norm=" + wedgeNorm.toFixed(3)
    );
    outlet(4, "set", status);
}
