// Beginner workshop specialization of max/qmw_qac_circuit_programmer_v1.js.
//
// Reused conventions and contract:
//   outlet 0 — QAC-style QuantumCircuit / gate / Simulator commands
//   outlet 1 — status text
//   outlet 2 — compact H/X/Y/Z sequence for Max printing or optional helpers
//
// The research programmer has four rows, sixteen columns, and a broad palette.
// This teaching surface intentionally exposes one row, six slots, H/X/Y/Z,
// clear, and test/hear. The deeper QAC machinery stays backstage.
autowatch = 1;
inlets = 1;
outlets = 3;

mgraphics.init();
mgraphics.relative_coords = 0;
mgraphics.autofill = 0;

var ROWS = 1, COLS = 6;
var palette = ["I", "H", "X", "Y", "Z"];
var selected = "H";
var grid = [];
var hoverRow = -1, hoverCol = -1;
var left = 74, top = 188, cellW = 82, cellH = 70;
var paletteY = 104, paletteW = 72, paletteH = 34;
var targetStage = 0;
var p0 = 1.0, p1 = 0.0, bx = 0.0, by = 0.0, bz = 1.0;
var lastStatus = "Place gates, then choose TEST + HEAR.";

var colors = {
    bg: [0.055, 0.075, 0.105, 1], panel: [0.09, 0.12, 0.16, 1],
    line: [0.34, 0.39, 0.46, 1], text: [0.9, 0.93, 0.97, 1],
    blue: [0.27, 0.54, 1, 1], orange: [1, 0.51, 0.17, 1],
    cyan: [0.51, 0.81, 1, 1], yellow: [0.95, 0.76, 0.11, 1],
    green: [0.30, 0.86, 0.56, 1], muted: [0.57, 0.62, 0.69, 1]
};

function initGrid() {
    grid = [[]];
    for (var c = 0; c < COLS; c++) grid[0].push("I");
}
initGrid();

function paint() {
    var w = box.rect[2] - box.rect[0], h = box.rect[3] - box.rect[1];
    mgraphics.set_source_rgba(colors.bg);
    mgraphics.rectangle(0, 0, w, h);
    mgraphics.fill();
    drawTitle();
    drawPalette();
    drawGrid();
    drawStatePanel();
    drawActions();
    drawFooter(w, h);
}

function drawTitle() {
    mgraphics.select_font_face("Arial");
    mgraphics.set_source_rgba(colors.text);
    mgraphics.set_font_size(22);
    mgraphics.move_to(24, 30);
    mgraphics.show_text("QAC CIRCUIT CHALLENGE");
    mgraphics.set_font_size(15);
    mgraphics.set_source_rgba(colors.cyan);
    mgraphics.move_to(24, 58);
    mgraphics.show_text(
        targetStage === 0
            ? "Start at |0>: reach |1>. Can H-Z-H match X?"
            : "Nice. Keep building: return from |1> to |0>."
    );
    mgraphics.set_source_rgba(colors.muted);
    mgraphics.set_font_size(12);
    mgraphics.move_to(24, 80);
    mgraphics.show_text("Gate order reads left → right. Click a gate, then a numbered slot.");
}

function drawPalette() {
    mgraphics.set_source_rgba(colors.muted);
    mgraphics.set_font_size(11);
    mgraphics.move_to(24, 98);
    mgraphics.show_text("GATE");
    for (var i = 0; i < palette.length; i++) {
        var x = 74 + i * (paletteW + 9), active = palette[i] === selected;
        mgraphics.set_source_rgba(active ? colors.yellow : colors.panel);
        rounded(x, paletteY, paletteW, paletteH, 6);
        mgraphics.fill();
        mgraphics.set_source_rgba(active ? colors.bg : gateColor(palette[i]));
        centerText(palette[i], x, paletteY + 22, paletteW, 14);
    }
}

function drawGrid() {
    var y = top;
    mgraphics.set_source_rgba(colors.text);
    mgraphics.set_font_size(15);
    mgraphics.move_to(24, y + 41);
    mgraphics.show_text("q0");
    mgraphics.set_source_rgba(colors.line);
    mgraphics.set_line_width(3);
    mgraphics.move_to(left, y + cellH * 0.5);
    mgraphics.line_to(left + COLS * cellW, y + cellH * 0.5);
    mgraphics.stroke();
    for (var c = 0; c < COLS; c++) {
        var x = left + c * cellW, gate = grid[0][c];
        if (hoverRow === 0 && hoverCol === c) {
            mgraphics.set_source_rgba(0.25, 0.32, 0.42, 0.60);
            mgraphics.rectangle(x + 3, y + 5, cellW - 6, cellH - 10);
            mgraphics.fill();
        }
        if (gate !== "I") drawGate(gate, x, y, cellW, cellH);
        mgraphics.set_source_rgba(colors.muted);
        centerText(String(c + 1), x, top - 12, cellW, 10);
    }
}

function drawGate(gate, x, y, w, h) {
    mgraphics.set_source_rgba(gateColor(gate));
    rounded(x + 13, y + 12, w - 26, h - 24, 7);
    mgraphics.fill();
    mgraphics.set_source_rgba(colors.bg);
    centerText(gate, x, y + h / 2 + 6, w, 17);
}

function drawStatePanel() {
    var x = 600, y = 96, w = 260, h = 196;
    mgraphics.set_source_rgba(colors.panel);
    rounded(x, y, w, h, 10);
    mgraphics.fill();
    mgraphics.set_source_rgba(colors.text);
    mgraphics.set_font_size(14);
    mgraphics.move_to(x + 18, y + 27);
    mgraphics.show_text("IMMEDIATE STATE FEEDBACK");

    drawProbabilityBar(x + 18, y + 50, 142, "|0>", p0, colors.blue);
    drawProbabilityBar(x + 18, y + 88, 142, "|1>", p1, colors.orange);

    var cx = x + 210, cy = y + 106, radius = 50;
    mgraphics.set_source_rgba(colors.line);
    mgraphics.set_line_width(1.5);
    mgraphics.arc(cx, cy, radius, 0, 6.283);
    mgraphics.stroke();
    mgraphics.move_to(cx, cy - radius);
    mgraphics.line_to(cx, cy + radius);
    mgraphics.stroke();
    mgraphics.set_source_rgba(colors.muted);
    centerText("|0>", cx - 22, cy - radius - 7, 44, 10);
    centerText("|1>", cx - 22, cy + radius + 15, 44, 10);
    var px = cx + bx * radius;
    var py = cy - bz * radius;
    mgraphics.set_source_rgba(colors.yellow);
    mgraphics.set_line_width(3);
    mgraphics.move_to(cx, cy);
    mgraphics.line_to(px, py);
    mgraphics.stroke();
    mgraphics.arc(px, py, 6, 0, 6.283);
    mgraphics.fill();

    mgraphics.set_source_rgba(colors.muted);
    mgraphics.set_font_size(11);
    mgraphics.move_to(x + 18, y + 164);
    mgraphics.show_text(
        "Bloch (x, y, z) = (" +
        fixed(bx) + ", " + fixed(by) + ", " + fixed(bz) + ")"
    );
    mgraphics.set_source_rgba(challengeColor());
    mgraphics.set_font_size(12);
    mgraphics.move_to(x + 18, y + 186);
    mgraphics.show_text(challengeText());
}

function drawProbabilityBar(x, y, w, label, value, color) {
    mgraphics.set_source_rgba(colors.muted);
    mgraphics.set_font_size(12);
    mgraphics.move_to(x, y + 14);
    mgraphics.show_text(label);
    mgraphics.set_source_rgba(colors.bg);
    rounded(x + 34, y, w, 18, 4);
    mgraphics.fill();
    mgraphics.set_source_rgba(color);
    rounded(x + 34, y, Math.max(1, w * value), 18, 4);
    mgraphics.fill();
    mgraphics.set_source_rgba(colors.text);
    mgraphics.set_font_size(10);
    mgraphics.move_to(x + 182, y + 13);
    mgraphics.show_text(Math.round(value * 100) + "%");
}

function drawActions() {
    actionButton(24, 302, 150, "CLEAR", colors.panel);
    actionButton(188, 302, 190, "TEST + HEAR", colors.orange);
    actionButton(392, 302, 142, "LOAD H-Z-H", colors.cyan);
    actionButton(544, 302, 142, "LOAD H-X-H", colors.green);
    actionButton(696, 302, 142, "LOAD H-Y-H", colors.yellow);
}

function drawFooter(w, h) {
    mgraphics.set_source_rgba(colors.muted);
    mgraphics.set_font_size(12);
    mgraphics.move_to(24, 370);
    mgraphics.show_text("Status: " + lastStatus);
    mgraphics.move_to(24, 394);
    mgraphics.show_text(
        "If sound is unavailable, the state bars and printed Python circuit remain the fallback."
    );
}

function actionButton(x, y, w, label, color) {
    mgraphics.set_source_rgba(color);
    rounded(x, y, w, 40, 7);
    mgraphics.fill();
    var darkText = label === "TEST + HEAR" || label.indexOf("LOAD ") === 0;
    mgraphics.set_source_rgba(darkText ? colors.bg : colors.text);
    centerText(label, x, y + 25, w, 13);
}

function onclick(x, y) {
    if (y >= paletteY && y <= paletteY + paletteH) {
        var pi = Math.floor((x - 74) / (paletteW + 9));
        if (pi >= 0 && pi < palette.length) {
            selected = palette[pi];
            mgraphics.redraw();
        }
        return;
    }
    if (
        x >= left && x < left + COLS * cellW &&
        y >= top && y < top + cellH
    ) {
        var c = Math.floor((x - left) / cellW);
        setCell(0, c, selected);
        evaluate(false);
        mgraphics.redraw();
        return;
    }
    if (y >= 302 && y <= 342) {
        if (x >= 24 && x <= 174) clear();
        else if (x >= 188 && x <= 378) compile();
        else if (x >= 392 && x <= 534) preset("hzh");
        else if (x >= 544 && x <= 686) preset("hxh");
        else if (x >= 696 && x <= 838) preset("hyh");
    }
}

function onmousemove(x, y) {
    hoverCol = (x >= left && x < left + COLS * cellW)
        ? Math.floor((x - left) / cellW) : -1;
    hoverRow = (y >= top && y < top + cellH) ? 0 : -1;
    mgraphics.redraw();
}

function setCell(q, c, gate) {
    grid[0][c] = gate;
}

function clear() {
    initGrid();
    targetStage = 0;
    evaluate(false);
    status("Cleared. Target is |1>.");
    mgraphics.redraw();
}

function preset(name) {
    initGrid();
    var middle = name === "hxh" ? "X" : name === "hyh" ? "Y" : "Z";
    grid[0][0] = "H";
    grid[0][1] = middle;
    grid[0][2] = "H";
    evaluate(false);
    status("Loaded H → " + middle + " → H. Predict before testing.");
    mgraphics.redraw();
}

function gateSequence() {
    var gates = [];
    for (var c = 0; c < COLS; c++) {
        if (grid[0][c] !== "I") gates.push(grid[0][c].toLowerCase());
    }
    return gates;
}

function evaluate(advanceChallenge) {
    var gates = gateSequence();
    var ar = 1.0, ai = 0.0, br = 0.0, bi = 0.0;
    var invsqrt2 = 0.7071067811865476;
    for (var i = 0; i < gates.length; i++) {
        if (gates[i] === "h") {
            var nextAr = (ar + br) * invsqrt2;
            var nextAi = (ai + bi) * invsqrt2;
            var nextBr = (ar - br) * invsqrt2;
            var nextBi = (ai - bi) * invsqrt2;
            ar = nextAr; ai = nextAi; br = nextBr; bi = nextBi;
        } else if (gates[i] === "x") {
            var swapAr = ar, swapAi = ai;
            ar = br; ai = bi; br = swapAr; bi = swapAi;
        } else if (gates[i] === "y") {
            // Y[a,b] = [-i b, i a].
            var yAr = bi, yAi = -br;
            var yBr = -ai, yBi = ar;
            ar = yAr; ai = yAi; br = yBr; bi = yBi;
        } else if (gates[i] === "z") {
            br = -br;
            bi = -bi;
        }
    }
    p0 = ar * ar + ai * ai;
    p1 = br * br + bi * bi;
    bx = 2.0 * (ar * br + ai * bi);
    by = 2.0 * (ar * bi - ai * br);
    bz = p0 - p1;
    if (advanceChallenge && targetStage === 0 && p1 > 0.999) {
        targetStage = 1;
        status("Target |1> reached. Now extend the circuit to return to |0>.");
    } else if (advanceChallenge && targetStage === 1 && p0 > 0.999) {
        status("Challenge complete: the state returned to |0>.");
    }
}

function compile() {
    var gates = gateSequence();
    if (gates.length === 0) {
        status("Place at least one H, X, Y, or Z gate before testing.");
        return;
    }
    evaluate(true);

    // Preserve the original QAC JSUI command contract on outlet 0.
    outlet(0, "QuantumCircuit", "qc", 1, 1);
    for (var i = 0; i < gates.length; i++) {
        outlet(0, "qc", gates[i], 0);
    }
    outlet(0, "Simulator", "sim", "qc", 1024);
    outlet(0, "sim", "get_qasm");

    // The workshop bridge uses only this compact, beginner-safe outlet.
    outlet(2, "circuit", gates.join(","));
    if (!(targetStage === 1 && p1 > 0.999) && !(targetStage === 1 && p0 > 0.999)) {
        status(
            "Sent " + gates.join(" → ").toUpperCase() +
            " to Python audio. If the launcher is off, run Module 3 below."
        );
    }
    mgraphics.redraw();
}

function feedback(nextP0, nextP1, nextX, nextY, nextZ) {
    p0 = Number(nextP0);
    p1 = Number(nextP1);
    bx = Number(nextX);
    by = Number(nextY);
    bz = Number(nextZ);
    mgraphics.redraw();
}

function launcherstatus() {
    var words = arrayfromargs(arguments);
    lastStatus = words.join(" ");
    mgraphics.redraw();
}

function status(text) {
    lastStatus = text;
    outlet(1, "set", text);
}

function challengeText() {
    if (targetStage === 0 && p1 > 0.999) return "Target |1> is ready to test.";
    if (targetStage === 1 && p0 > 0.999) return "Return target |0> is ready to test.";
    return targetStage === 0 ? "Current target: |1>" : "Current target: |0>";
}

function challengeColor() {
    if ((targetStage === 0 && p1 > 0.999) || (targetStage === 1 && p0 > 0.999)) {
        return colors.green;
    }
    return colors.yellow;
}

function fixed(value) {
    if (Math.abs(value) < 0.005) value = 0;
    return value.toFixed(2);
}

function gateColor(gate) {
    if (gate === "H") return colors.orange;
    if (gate === "X") return colors.green;
    if (gate === "Y") return colors.yellow;
    if (gate === "Z") return colors.cyan;
    return colors.text;
}

function rounded(x, y, w, h, r) {
    mgraphics.rectangle_rounded(x, y, w, h, r, r);
}

function centerText(text, x, y, w, size) {
    mgraphics.set_font_size(size);
    var measurement = mgraphics.text_measure(text);
    mgraphics.move_to(x + (w - measurement[0]) / 2, y);
    mgraphics.show_text(text);
}

function bang() {
    compile();
}
