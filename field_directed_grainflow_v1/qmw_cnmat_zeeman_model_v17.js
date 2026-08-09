autowatch = 1;
inlets = 4;
outlets = 3;

var grid = [];
var field = 1.0;
var carrier = 110.0;
var spread = 60.0;
var level = 0.18;
var coherence = 0.5;
var entropy = 0.0;

function clamp(x, lo, hi) { return Math.max(lo, Math.min(hi, Number(x))); }

function list() {
    var a = arrayfromargs(arguments);
    if (inlet === 0) {
        grid = a.map(Number);
    } else if (inlet === 1 && a.length >= 4) {
        field = clamp(a[0], 0, 20);
        carrier = clamp(a[1], 20, 4000);
        spread = clamp(a[2], 0, 1000);
        level = clamp(a[3], 0, 1);
    } else if (inlet === 2 && a.length) {
        coherence = clamp(a[0], 0, 1);
    } else if (inlet === 3 && a.length) {
        entropy = clamp(a[0] / Math.log(16), 0, 1);
    }
    render();
}

function msg_float(v) { list(v); }

function render() {
    if (grid.length < 48) return;
    var resonances = [];
    var sinusoids = [];
    var active = 0;
    for (var cell = 0; cell < 16; cell++) {
        var density = clamp(grid[cell * 3], 0, 1);
        var phase = clamp(grid[cell * 3 + 1], -1, 1);
        var occupancy = clamp(grid[cell * 3 + 2], 0, 1);
        if (density < 0.025 || occupancy <= 0.0) continue;
        var row = Math.floor(cell / 4);
        var column = cell % 4;
        var base = carrier * Math.pow(2, (cell / 15) * 3.0 + phase * 0.25);
        var lande = [1/3, 1, 5/3, 1][column];
        var shift = field * spread * lande;
        var transition = [2/3, 1, 1/3, 2/3][row];
        var gain = level * transition * density * (0.25 + 0.75 * occupancy) * 0.22;
        var decay = 0.12 + 3.8 * coherence * (0.35 + 0.65 * density);
        var lower = clamp(base - shift, 30, 18000);
        var upper = clamp(base + shift, 30, 18000);
        resonances.push(lower, gain, decay, upper, gain, decay);
        var noisiness = clamp(entropy * (1.0 - 0.45 * density), 0, 1);
        sinusoids.push(lower, gain * 0.35, noisiness, upper, gain * 0.35, noisiness);
        active++;
    }
    if (!active) {
        resonances = [carrier, 0.00001, 0.1];
        sinusoids = [carrier, 0.0, 0.0];
    }
    outlet(0, resonances);
    outlet(1, sinusoids);
    outlet(2, "set", "CNMAT model: " + (active * 2) + " Zeeman resonances");
}

function bang() { render(); }
