autowatch = 1;
inlets = 1;
outlets = 2;

var voice = 1;
var voiceCount = 64;

function list() {
    var values = arrayfromargs(arguments);
    if (values.length < 12) return;
    // Input: frame, grain, x, y, z, amp, phase, jx, jy, jz, energy, decayMs.
    outlet(0, "target", voice);
    outlet(0, ["grain"].concat(values.slice(2, 12)));
    outlet(1, "set", "frame " + values[0] + " grain " + values[1] +
        " decay " + Number(values[11]).toFixed(2) + " ms");
    voice = (voice % voiceCount) + 1;
}

function voices(count) {
    voiceCount = Math.max(1, count | 0);
    voice = 1;
}
