// Recursive Wilson performance extension for the QAC circuit programmer.
// Include v1 directly: nested Max js include chains can stop evaluation before
// the outer file's overrides are installed.
include("qmw_qac_circuit_programmer_v1.js");

outlets = 7; // QAC, status, intervention gate, next, start, stop, reset

var activeCol = 0;
var liveGateRevision = Math.floor(new Date().getTime() / 1000) % 1900000000;
var loopRunning = false;
var loopIntervalMs = 240;
var loopTask = null;

function paint() {
    var w = box.rect[2] - box.rect[0], h = box.rect[3] - box.rect[1];
    mgraphics.set_source_rgba(colors.bg); mgraphics.rectangle(0, 0, w, h); mgraphics.fill();
    drawTitle(); drawPalette(); drawGrid(); drawLoopCursor(); drawActions();
}

function drawLoopCursor() {
    var x = left + activeCol * cellW;
    mgraphics.set_source_rgba(loopRunning ? colors.yellow : colors.line);
    mgraphics.set_line_width(loopRunning ? 3.5 : 1.5);
    mgraphics.rectangle(x + 1.5, top + 1.5, cellW - 3, ROWS * cellH - 3);
    mgraphics.stroke();
}

function clear() {
    stopLoop(false);
    initGrid();
    activeCol = 0;
    outlet(6, "bang");
    status("cleared circuit and reset engine");
    mgraphics.redraw();
}

function preset(name) {
    stopLoop(false);
    initGrid();
    if (name === "bell") {
        grid[0][0] = "H";
        grid[0][1] = "CTRL";
        grid[1][1] = "TARG";
    } else if (name === "ghz") {
        grid[0][0] = "H";
        grid[0][1] = "CTRL";
        grid[1][1] = "TARG";
        grid[1][2] = "CTRL";
        grid[2][2] = "TARG";
        grid[2][3] = "CTRL";
        grid[3][3] = "TARG";
    } else if (name === "weave") {
        for (var q = 0; q < 4; q++) grid[q][q] = "H";
        grid[0][5] = "CTRL";
        grid[1][5] = "TARG";
        grid[2][7] = "CTRL";
        grid[3][7] = "TARG";
        grid[1][10] = "CTRL";
        grid[2][10] = "TARG";
        grid[0][13] = "T";
        grid[3][14] = "S";
    }
    activeCol = 0;
    mgraphics.redraw();
    compile();
    status("preset " + name + " committed to engine");
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
        return false;
    }
    if (count === 0) status("step " + (activeCol + 1) + " is empty");
    else status("performed " + count + " live gate" + (count === 1 ? "" : "s") + " from step " + (activeCol + 1));
    return true;
}

function ensureLoopTask() {
    if (loopTask === null) loopTask = new Task(loopTick, this);
    loopTask.interval = loopIntervalMs;
}

function loopTick() {
    if (!loopRunning) return;
    performStep();
    activeCol = (activeCol + 1) % COLS;
    mgraphics.redraw();
}

function startLoop() {
    if (loopRunning) return;
    loopRunning = true;
    ensureLoopTask();
    loopTask.repeat();
    status("circuit loop running from step " + (activeCol + 1) + " · " + loopIntervalMs + " ms");
    mgraphics.redraw();
}

function stopLoop(report) {
    loopRunning = false;
    if (loopTask !== null) loopTask.cancel();
    if (report !== false) status("circuit loop stopped at step " + (activeCol + 1));
    mgraphics.redraw();
}

function toggleLoop() {
    if (loopRunning) stopLoop(true);
    else startLoop();
}

function setLoopInterval(value) {
    loopIntervalMs = Math.max(30, Math.min(4000, Math.round(Number(value))));
    if (loopTask !== null) loopTask.interval = loopIntervalMs;
    status("circuit loop interval " + loopIntervalMs + " ms");
    mgraphics.redraw();
}

function loopms(value) {
    setLoopInterval(value);
}

function startloop() {
    startLoop();
}

function stoploop() {
    stopLoop(true);
}

function notifydeleted() {
    loopRunning = false;
    if (loopTask !== null) loopTask.cancel();
}

function drawActions() {
    actionButton(24, 326, 112, "CLEAR", colors.panel);
    actionButton(146, 326, 112, "BELL", colors.purple);
    actionButton(268, 326, 112, "GHZ", colors.magenta);
    actionButton(390, 326, 112, "WEAVE", colors.cyan);
    actionButton(512, 326, 228, "RESEED RECURSION", colors.orange);

    actionButton(24, 368, 92, "EVOLVE", colors.yellow);
    actionButton(122, 368, 92, "RECURSE", colors.cyan);
    actionButton(220, 368, 72, "STOP", colors.magenta);
    actionButton(298, 368, 72, "RESET", colors.panel);
    actionButton(376, 368, 132, "STEP " + (activeCol + 1), colors.purple);
    actionButton(514, 368, 110, loopRunning ? "STOP LOOP" : "LOOP " + loopIntervalMs, loopRunning ? colors.magenta : colors.cyan);
    actionButton(630, 368, 50, "−", colors.panel);
    actionButton(686, 368, 50, "+", colors.panel);
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
        if (x < 119) {
            outlet(3, "bang");
            status("evolving one Wilson generation");
        } else if (x < 217) {
            outlet(4, "bang");
            status("recursive evolution running");
        } else if (x < 295) {
            outlet(5, "bang");
            status("recursive evolution stopped");
        } else if (x < 373) {
            outlet(6, "bang");
            status("reset to the Wilson weight-two probe");
        } else if (x < 511) {
            performStep();
        } else if (x < 627) {
            toggleLoop();
        } else if (x < 683) {
            setLoopInterval(loopIntervalMs - 30);
        } else {
            setLoopInterval(loopIntervalMs + 30);
        }
    }
}
