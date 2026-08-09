// Incremental live-gate extension for the v1 QAC circuit programmer.
include("qmw_qac_circuit_programmer_v1.js");

outlets = 3; // QAC commands, status, revisioned live-gate OSC arguments

var activeCol = 0;
var liveGateRevision = Math.floor(new Date().getTime() / 1000) % 1900000000;

function drawActions() {
    actionButton(24, 326, 112, "CLEAR", colors.panel);
    actionButton(146, 326, 112, "BELL", colors.purple);
    actionButton(268, 326, 112, "GHZ", colors.magenta);
    actionButton(390, 326, 112, "WEAVE", colors.cyan);
    actionButton(512, 326, 228, "RESEED CIRCUIT", colors.orange);
    actionButton(512, 368, 228, "PERFORM STEP " + (activeCol + 1), colors.yellow);
}

function onclick(x,y) {
    if (y >= paletteY && y <= paletteY + paletteH) {
        var pi = Math.floor((x - 24) / (paletteW + 7));
        if (pi >= 0 && pi < palette.length) {
            selected = palette[pi];
            mgraphics.redraw();
        }
        return;
    }
    if (x >= left && x < left + COLS*cellW && y >= top && y < top + ROWS*cellH) {
        var c = Math.floor((x-left)/cellW), q = Math.floor((y-top)/cellH);
        activeCol = c;
        setCell(q,c,selected);
        status("step " + (c + 1) + " selected · " + selected + " on q" + q);
        mgraphics.redraw();
        return;
    }
    if (y >= 326 && y <= 362) {
        if (x < 136) clear();
        else if (x < 258) preset("bell");
        else if (x < 380) preset("ghz");
        else if (x < 502) preset("weave");
        else compile();
        return;
    }
    if (y >= 368 && y <= 404 && x >= 512 && x <= 740) performStep();
}

function nextGateRevision() {
    liveGateRevision += 1;
    if (liveGateRevision >= 2000000000) liveGateRevision = 1;
    return liveGateRevision;
}

function performStep() {
    var control = -1, target = -1, count = 0;
    for (var q = 0; q < ROWS; q++) {
        var gate = grid[q][activeCol];
        if (gate === "CTRL") control = q;
        else if (gate === "TARG") target = q;
        else if (gate !== "I") {
            outlet(2, nextGateRevision(), gate.toLowerCase(), q);
            count++;
        }
    }
    if (control >= 0 && target >= 0 && control !== target) {
        outlet(2, nextGateRevision(), "cx", control, target);
        count++;
    } else if (control >= 0 || target >= 0) {
        status("step " + (activeCol + 1) + " has an incomplete CNOT");
        return;
    }
    if (count === 0) status("step " + (activeCol + 1) + " is empty");
    else status("performed " + count + " live gate" + (count === 1 ? "" : "s") + " from step " + (activeCol + 1));
}

