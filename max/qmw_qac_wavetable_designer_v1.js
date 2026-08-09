// Four-qubit / sixteen-step QAC circuit programmer for Max jsui.
autowatch = 1;
inlets = 1;
outlets = 2; // QAC commands, status

mgraphics.init();
mgraphics.relative_coords = 0;
mgraphics.autofill = 0;

var ROWS = 4, COLS = 16;
var palette = ["I", "H", "X", "Y", "Z", "S", "T", "CTRL", "TARG"];
var selected = "H";
var grid = [];
var hoverRow = -1, hoverCol = -1;
var left = 58, top = 112, cellW = 43, cellH = 52;
var paletteY = 42, paletteW = 62, paletteH = 30;

var colors = {
    bg: [0.055, 0.075, 0.105, 1], panel: [0.09, 0.12, 0.16, 1],
    line: [0.34, 0.39, 0.46, 1], text: [0.9, 0.93, 0.97, 1],
    blue: [0.27, 0.54, 1, 1], orange: [1, 0.51, 0.17, 1],
    magenta: [0.93, 0.33, 0.60, 1], cyan: [0.51, 0.81, 1, 1],
    yellow: [0.95, 0.76, 0.11, 1], purple: [0.75, 0.58, 1, 1]
};

function initGrid() {
    grid = [];
    for (var q = 0; q < ROWS; q++) {
        var row = [];
        for (var c = 0; c < COLS; c++) row.push("I");
        grid.push(row);
    }
}
initGrid();

function paint() {
    var w = box.rect[2] - box.rect[0], h = box.rect[3] - box.rect[1];
    mgraphics.set_source_rgba(colors.bg); mgraphics.rectangle(0, 0, w, h); mgraphics.fill();
    drawTitle(); drawPalette(); drawGrid(); drawActions();
}

function drawTitle() {
    mgraphics.set_source_rgba(colors.text); mgraphics.select_font_face("Arial");
    mgraphics.set_font_size(20); mgraphics.move_to(24, 27);
    mgraphics.show_text("QMW · QAC FOUR-QUBIT CIRCUIT PROGRAMMER");
}

function drawPalette() {
    for (var i = 0; i < palette.length; i++) {
        var x = 24 + i * (paletteW + 7), active = palette[i] === selected;
        mgraphics.set_source_rgba(active ? colors.yellow : colors.panel);
        rounded(x, paletteY, paletteW, paletteH, 5); mgraphics.fill();
        mgraphics.set_source_rgba(active ? colors.bg : gateColor(palette[i]));
        centerText(palette[i], x, paletteY + 20, paletteW, 12);
    }
}

function drawGrid() {
    for (var q = 0; q < ROWS; q++) {
        var y = top + q * cellH;
        mgraphics.set_source_rgba(colors.text); mgraphics.set_font_size(14);
        mgraphics.move_to(22, y + 31); mgraphics.show_text("q" + q);
        mgraphics.set_source_rgba(colors.line); mgraphics.set_line_width(2);
        mgraphics.move_to(left, y + cellH * 0.5); mgraphics.line_to(left + COLS * cellW, y + cellH * 0.5); mgraphics.stroke();
        for (var c = 0; c < COLS; c++) {
            var x = left + c * cellW, gate = grid[q][c];
            if (q === hoverRow && c === hoverCol) {
                mgraphics.set_source_rgba(0.25, 0.32, 0.42, 0.55);
                mgraphics.rectangle(x + 2, y + 4, cellW - 4, cellH - 8); mgraphics.fill();
            }
            if (gate !== "I") drawGate(gate, x, y, cellW, cellH);
            if (q === 0) {
                mgraphics.set_source_rgba(0.58, 0.63, 0.7, 1); mgraphics.set_font_size(9);
                centerText(String(c + 1), x, top - 9, cellW, 9);
            }
        }
    }
}

function drawGate(gate, x, y, w, h) {
    var color = gateColor(gate);
    if (gate === "CTRL") {
        mgraphics.set_source_rgba(color); mgraphics.arc(x + w/2, y + h/2, 6, 0, 6.283); mgraphics.fill(); return;
    }
    if (gate === "TARG") {
        mgraphics.set_source_rgba(color); mgraphics.set_line_width(2.5);
        mgraphics.arc(x + w/2, y + h/2, 11, 0, 6.283); mgraphics.stroke();
        mgraphics.move_to(x+w/2-8,y+h/2);mgraphics.line_to(x+w/2+8,y+h/2);
        mgraphics.move_to(x+w/2,y+h/2-8);mgraphics.line_to(x+w/2,y+h/2+8);mgraphics.stroke(); return;
    }
    mgraphics.set_source_rgba(color); rounded(x+5,y+9,w-10,h-18,5); mgraphics.fill();
    mgraphics.set_source_rgba(colors.bg); centerText(gate,x,y+h/2+5,w,12);
}

function drawActions() {
    actionButton(24, 338, 130, "CLEAR", colors.panel);
    actionButton(164, 338, 130, "BELL", colors.purple);
    actionButton(304, 338, 130, "GHZ", colors.magenta);
    actionButton(444, 338, 130, "WEAVE", colors.cyan);
    actionButton(590, 338, 150, "SEND QASM", colors.orange);
}

function actionButton(x,y,w,label,color) {
    mgraphics.set_source_rgba(color); rounded(x,y,w,36,6); mgraphics.fill();
    mgraphics.set_source_rgba(label === "SEND QASM" ? colors.bg : colors.text);
    centerText(label,x,y+23,w,13);
}

function onclick(x,y) {
    if (y >= paletteY && y <= paletteY + paletteH) {
        var pi = Math.floor((x - 24) / (paletteW + 7));
        if (pi >= 0 && pi < palette.length) { selected = palette[pi]; mgraphics.redraw(); }
        return;
    }
    if (x >= left && x < left + COLS*cellW && y >= top && y < top + ROWS*cellH) {
        var c = Math.floor((x-left)/cellW), q = Math.floor((y-top)/cellH);
        setCell(q,c,selected); mgraphics.redraw(); return;
    }
    if (y >= 338 && y <= 374) {
        if (x < 154) clear(); else if (x < 294) preset("bell");
        else if (x < 434) preset("ghz"); else if (x < 574) preset("weave");
        else compile();
    }
}

function onmousemove(x,y) {
    hoverCol = (x>=left && x<left+COLS*cellW) ? Math.floor((x-left)/cellW) : -1;
    hoverRow = (y>=top && y<top+ROWS*cellH) ? Math.floor((y-top)/cellH) : -1;
    mgraphics.redraw();
}

function setCell(q,c,gate) {
    if (gate === "I") { grid[q][c] = "I"; return; }
    if (gate === "CTRL" || gate === "TARG") {
        for (var r=0;r<ROWS;r++) if (grid[r][c] === gate) grid[r][c] = "I";
    }
    grid[q][c] = gate;
}

function clear() { initGrid(); status("cleared"); mgraphics.redraw(); }
function preset(name) {
    initGrid();
    if (name === "bell") { grid[0][0]="H";grid[0][1]="CTRL";grid[1][1]="TARG"; }
    else if (name === "ghz") { grid[0][0]="H";grid[0][1]="CTRL";grid[1][1]="TARG";grid[1][2]="CTRL";grid[2][2]="TARG";grid[2][3]="CTRL";grid[3][3]="TARG"; }
    else if (name === "weave") { for(var q=0;q<4;q++)grid[q][q]="H";grid[0][5]="CTRL";grid[1][5]="TARG";grid[2][7]="CTRL";grid[3][7]="TARG";grid[1][10]="CTRL";grid[2][10]="TARG";grid[0][13]="T";grid[3][14]="S"; }
    status("preset " + name); mgraphics.redraw();
}

function compile() {
    outlet(0, "QuantumCircuit", "qc", 4, 4);
    var count = 0;
    for (var c=0;c<COLS;c++) {
        var control=-1,target=-1;
        for (var q=0;q<ROWS;q++) {
            var gate=grid[q][c];
            if (gate === "CTRL") control=q;
            else if (gate === "TARG") target=q;
            else if (gate !== "I") { outlet(0,"qc",gate.toLowerCase(),q); count++; }
        }
        if (control>=0 && target>=0 && control!==target) { outlet(0,"qc","cx",control,target);count++; }
    }
    outlet(0, "Simulator", "sim", "qc", 256);
    outlet(0, "sim", "get_qasm");
    status("sent " + count + " gates → QASM bridge");
}

function status(text) { outlet(1, "set", text); }
function gateColor(g) { if(g==="H")return colors.orange;if(g==="X"||g==="CTRL"||g==="TARG")return colors.blue;if(g==="Y")return colors.magenta;if(g==="Z"||g==="S"||g==="T")return colors.cyan;return colors.text; }
function rounded(x,y,w,h,r) { mgraphics.rectangle_rounded(x,y,w,h,r,r); }
function centerText(text,x,y,w,size) { mgraphics.set_font_size(size);var m=mgraphics.text_measure(text);mgraphics.move_to(x+(w-m[0])/2,y);mgraphics.show_text(text); }
function bang() { compile(); }
