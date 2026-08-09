autowatch = 1;
inlets = 2;
outlets = 2;

var grid = [];
var field = 1.0;
var carrier = 110.0;
var spread = 60.0;

function clamp(x, lo, hi) { return Math.max(lo, Math.min(hi, Number(x))); }
function list() {
    var a = arrayfromargs(arguments);
    if (inlet === 0) grid = a.map(Number);
    else if (a.length >= 3) {
        field = clamp(a[0], 0, 20);
        carrier = clamp(a[1], 20, 4000);
        spread = clamp(a[2], 0, 1000);
    }
    render();
}
function render() {
    if (grid.length < 48) return;
    var model = [];
    var active = 0;
    for (var cell = 0; cell < 16; cell++) {
        var density = clamp(grid[cell*3], 0, 1);
        var phase = clamp(grid[cell*3+1], -1, 1);
        var occupancy = clamp(grid[cell*3+2], 0, 1);
        if (density < 0.04 || occupancy <= 0) continue;
        var base = carrier * Math.pow(2, (cell/15)*2.5 + phase*0.2);
        var factor = [1/3, 1, 5/3, 1][cell%4];
        var shift = field * spread * factor;
        var gain = 0.055 * density * (0.25 + 0.75*occupancy);
        var decay = 0.3 + 4.2*density;
        model.push(clamp(base-shift,30,18000),gain,decay);
        model.push(clamp(base+shift,30,18000),gain,decay);
        active += 2;
    }
    if (!active) model = [carrier,0.00001,0.2];
    outlet(0,model);
    outlet(1,"set","model loaded: "+active+" decaying Zeeman sinusoids — press RING");
}
function bang() { render(); }
