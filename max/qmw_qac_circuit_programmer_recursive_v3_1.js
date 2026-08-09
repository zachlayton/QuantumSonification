// Recursive Wilson performance extension for the QAC circuit programmer.
// Include v1 directly: nested Max js include chains can stop evaluation before
// the outer file's overrides are installed.
include("qmw_qac_circuit_programmer_v1.js");

outlets = 7; // QAC, status, intervention gate, next, start, stop, reset

var activeCol = 0;
var liveGateRevision = Math.floor(new Date().getTime() / 1000) % 1900000000;

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

function drawActions() {
    actionButton(24, 326, 112, "CLEAR", colors.panel);
    actionButton(146, 326, 112, "BELL", colors.purple);
    actionButton(268, 326, 112, "GHZ", colors.magenta);
    actionButton(390, 326, 112, "WEAVE", colors.cyan);
    actionButton(512, 326, 228, "RESEED RECURSION", colors.orange);

    actionButton(24, 368, 128, "EVOLVE ONCE", colors.yellow);
    actionButton(162, 368, 128, "RECURSE", colors.cyan);
    actionButton(300, 368, 100, "STOP", colors.magenta);
    actionButton(410, 368, 100, "RESET", colors.panel);
    actionButton(520, 368, 220, "INTERVENE STEP " + (activeCol + 1), colors.purple);
}

function onclick(x, y) {
    if (y >= paletteY && y <= paletteY + paletteH) {
        var pi = Math.floor((x - 24) / (paletteW + 7));
        if (pi >= 0 && pi < palette.length) {
            selected = palette[pi];
            mgraphics.redraw();
        }
        return;
    }
    if (x >= left && x < left + COLS * cellW && y >= top && y < top + ROWS * cellH) {
        var c = Math.floor((x - left) / cellW), q = Math.floor((y - top) / cellH);
        activeCol = c;
        setCell(q, c, selected);
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
    if (y >= 368 && y <= 404) {
        if (x < 157) {
            outlet(3, "bang");
            status("evolving one Wilson generation");
        } else if (x < 295) {
            outlet(4, "bang");
            status("recursive evolution running");
        } else if (x < 405) {
            outlet(5, "bang");
            status("recursive evolution stopped");
        } else if (x < 515) {
            outlet(6, "bang");
            status("reset to the Wilson weight-two probe");
        } else {
            performStep();
        }
    }
}
