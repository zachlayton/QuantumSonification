autowatch = 1;
inlets = 1;
outlets = 5;

var probability = 0.0;
var angle = 0.0;
var stateName = "WAITING";
var modeSlewMs = 38.0;

function frame() {
    var a = arrayfromargs(arguments);
    if (a.length < 8) return;
    var iteration = a[0];
    var operatorCode = a[1];
    probability = a[2];
    angle = a[3];
    var phase = a[4];
    var norm = a[5];
    var represented = a[6];
    var residual = a[7];
    var operatorName = operatorCode === 1 ? "ORACLE" : (operatorCode === 2 ? "DIFFUSION" : "PREPARED");
    outlet(1, stateName + " | k=" + iteration + " " + operatorName + " | p=" + probability.toFixed(9) + " | norm=" + norm.toFixed(7));
    outlet(2, probability);

    // These controls are measured from the statevector's Grover-plane angle
    // and complex relative phase, not advanced by an independent LFO.
    outlet(3, "rot_z", angle / (2.0 * Math.PI));
    outlet(3, "rot_x", phase / (2.0 * Math.PI));
    outlet(3, "rot_y", (angle + 0.5 * phase) / (2.0 * Math.PI));
    outlet(3, "rotation_slew_ms", modeSlewMs);
    outlet(3, "modal_warp", Math.min(1.0, Math.sqrt(Math.max(0.0, probability))));
    outlet(3, "spectral_tilt", Math.min(1.0, residual));
    outlet(3, "geometry_depth_slew_ms", 90.0);
    outlet(3, "deform", 0.7);
}

function modes() {
    var a = arrayfromargs(arguments);
    if (a.length < 4) return;
    var count = Math.floor((a.length - 2) / 2);
    var energy = 0.0;
    var i;
    for (i = 0; i < count; i++) {
        var re = a[2 + 2 * i];
        var im = a[3 + 2 * i];
        energy += re * re + im * im;
    }
    var normalization = Math.sqrt(Math.max(energy, 1e-15));
    for (i = 0; i < count; i++) {
        var real = a[2 + 2 * i];
        var imag = a[3 + 2 * i];
        var phase = Math.atan2(imag, real);
        // The Walsh vector is already energy-normalized.  Keep that measured
        // structure audible throughout the search; probability supplies only
        // a gentle ~2.5 dB arrival contour rather than muting early frames.
        var confidenceGain = 0.75 + 0.25 * Math.sqrt(Math.max(0.0, probability));
        var signedGain = 0.14 * confidenceGain * real / normalization;
        var frequency = 42.0 * Math.pow(2.0, i / 12.0);
        var pan = 0.92 * Math.sin(2.0 * Math.PI * i / count + 2.0 * angle + phase);
        outlet(0, "target", i + 1);
        outlet(0, "mode", frequency, signedGain, pan, modeSlewMs);
    }
}

function found() {
    var a = arrayfromargs(arguments);
    outlet(1, "FOUND | exact p=" + Number(a[1]).toFixed(9) + " at iteration " + a[0]);
    outlet(4, 1);
}

function state() {
    var a = arrayfromargs(arguments);
    stateName = a.join(" ");
    outlet(1, stateName);
    if (stateName === "SEARCHING") outlet(4, 0);
}
