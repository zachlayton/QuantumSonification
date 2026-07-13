// quantum_spin_polarization_jsui_v1.js
//
// Max jsui visualizer for quantum_spin_polarization_engine_v2.py
//
// Expected messages:
//
//   qubit <index> x <value>
//   qubit <index> y <value>
//   qubit <index> z <value>
//   qubit <index> bloch_r <value>
//   qubit <index> bloch_theta <value>
//   qubit <index> bloch_phi <value>
//   qubit <index> basis_theta <value>
//   qubit <index> basis_phi <value>
//   qubit <index> basis_projection <value>
//   qubit <index> swirl <value>
//   qubit <index> interference <value>
//   qubit <index> brightness <value>
//
//   global spin_x <value>
//   global spin_y <value>
//   global spin_z <value>
//   global basis_projection <value>
//   global audio_phase <value>
//   global audio_swirl <value>
//   global audio_interference <value>
//   global audio_brightness <value>
//
//   pauli ZZZZ <value>
//   pauli XXXX <value>
//   pauli YYYY <value>
//   etc.

//   qubit <index> degree <value>
//   qubit <index> azimuth <value>
//   qubit <index> ellipticity <value>
//   qubit <index> circularity <value>
//   qubit <index> linearity <value>
//


autowatch = 1;
outlets = 1;

mgraphics.init();
mgraphics.relative_coords = 0;
mgraphics.autofill = 0;

// ------------------------------------------------------------
// State
// ------------------------------------------------------------

var NUM_QUBITS = 4;

var qubits = [];
for (var i = 0; i < NUM_QUBITS; i++) {
    qubits.push({
    x: 0.0,
    y: 0.0,
    z: 1.0,

    bloch_r: 1.0,
    bloch_theta: 0.0,
    bloch_phi: 0.0,

    degree: 1.0,
    azimuth: 0.0,
    ellipticity: 0.0,
    circularity: 0.0,
    linearity: 1.0,

    basis_theta: 0.0,
    basis_phi: 0.0,
    basis_projection: 0.0,

    swirl: 0.0,
    interference: 0.0,
    brightness: 1.0
});
}

var globalState = {
    spin_x: 0.0,
    spin_y: 0.0,
    spin_z: 0.0,

    basis_theta: 0.0,
    basis_phi: 0.0,
    basis_projection: 0.0,

    audio_phase: 0.0,
    audio_swirl: 0.0,
    audio_interference: 0.0,
    audio_brightness: 0.0
};

var pauli = {
    ZZII: 0.0,
    XXII: 0.0,
    YYII: 0.0,
    ZIZI: 0.0,
    IZIZ: 0.0,
    ZZZZ: 0.0,
    XXXX: 0.0,
    YYYY: 0.0
};

var title = "PAULI / BLOCH POLARIZATION FIELD";

// ------------------------------------------------------------
// Utility
// ------------------------------------------------------------

function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
}

function norm01(v) {
    return 0.5 * (clamp(v, -1.0, 1.0) + 1.0);
}

function abs01(v) {
    return Math.abs(clamp(v, -1.0, 1.0));
}

function set_source_rgba(r, g, b, a) {
    mgraphics.set_source_rgba(r, g, b, a);
}

function draw_text(txt, x, y, size, r, g, b, a) {
    set_source_rgba(r, g, b, a);
    mgraphics.select_font_face("Menlo");
    mgraphics.set_font_size(size);
    mgraphics.move_to(x, y);
    mgraphics.show_text(txt);
}

function line(x1, y1, x2, y2, width, r, g, b, a) {
    set_source_rgba(r, g, b, a);
    mgraphics.set_line_width(width);
    mgraphics.move_to(x1, y1);
    mgraphics.line_to(x2, y2);
    mgraphics.stroke();
}

function circle(cx, cy, radius, width, r, g, b, a) {
    set_source_rgba(r, g, b, a);
    mgraphics.set_line_width(width);
    mgraphics.ellipse(cx - radius, cy - radius, radius * 2, radius * 2);
    mgraphics.stroke();
}

function fill_circle(cx, cy, radius, r, g, b, a) {
    set_source_rgba(r, g, b, a);
    mgraphics.ellipse(cx - radius, cy - radius, radius * 2, radius * 2);
    mgraphics.fill();
}

function rect(x, y, w, h, r, g, b, a) {
    set_source_rgba(r, g, b, a);
    mgraphics.rectangle(x, y, w, h);
    mgraphics.fill();
}

function stroked_rect(x, y, w, h, width, r, g, b, a) {
    set_source_rgba(r, g, b, a);
    mgraphics.set_line_width(width);
    mgraphics.rectangle(x, y, w, h);
    mgraphics.stroke();
}

function draw_bar(label, x, y, w, h, value, bipolar) {
    var v = bipolar ? norm01(value) : clamp(value, 0.0, 1.0);

    rect(x, y, w, h, 0.08, 0.09, 0.10, 0.85);
    stroked_rect(x, y, w, h, 1.0, 0.25, 0.28, 0.32, 0.75);

    if (bipolar) {
        var mid = x + w * 0.5;
        line(mid, y, mid, y + h, 1.0, 0.45, 0.45, 0.45, 0.6);

        if (value >= 0) {
            rect(mid, y + 2, (w * 0.5 - 2) * clamp(value, 0, 1), h - 4,
                 0.15, 0.75, 0.95, 0.85);
        } else {
            var ww = (w * 0.5 - 2) * Math.abs(clamp(value, -1, 0));
            rect(mid - ww, y + 2, ww, h - 4,
                 0.95, 0.42, 0.35, 0.85);
        }
    } else {
        rect(x + 2, y + 2, (w - 4) * v, h - 4,
             0.75, 0.78, 0.40, 0.85);
    }

    draw_text(label, x, y - 4, 9, 0.72, 0.74, 0.76, 0.9);
}

function fmt(v) {
    var s = v.toFixed(3);
    if (v >= 0) {
        s = "+" + s;
    }
    return s;
}

// ------------------------------------------------------------
// Max message handlers
// ------------------------------------------------------------

function qubit() {
    var args = arrayfromargs(arguments);
    if (args.length < 3) {
        return;
    }

    var q = parseInt(args[0]);
    var key = String(args[1]);
    var value = parseFloat(args[2]);

    if (q < 0 || q >= NUM_QUBITS || isNaN(value)) {
        return;
    }

    if (key === "x") qubits[q].x = value;
    else if (key === "y") qubits[q].y = value;
    else if (key === "z") qubits[q].z = value;

    else if (key === "bloch_r") qubits[q].bloch_r = value;
    else if (key === "bloch_theta") qubits[q].bloch_theta = value;
    else if (key === "bloch_phi") qubits[q].bloch_phi = value;

    else if (key === "degree") qubits[q].degree = value;
    else if (key === "azimuth") qubits[q].azimuth = value;
    else if (key === "ellipticity") qubits[q].ellipticity = value;
    else if (key === "circularity") qubits[q].circularity = value;
    else if (key === "linearity") qubits[q].linearity = value;

    else if (key === "basis_theta") qubits[q].basis_theta = value;
    else if (key === "basis_phi") qubits[q].basis_phi = value;
    else if (key === "basis_projection") qubits[q].basis_projection = value;

    else if (key === "swirl") qubits[q].swirl = value;
    else if (key === "interference") qubits[q].interference = value;
    else if (key === "brightness") qubits[q].brightness = value;

    mgraphics.redraw();
}

function global() {
    var args = arrayfromargs(arguments);
    if (args.length < 2) {
        return;
    }

    var key = String(args[0]);
    var value = parseFloat(args[1]);

    if (isNaN(value)) {
        return;
    }

    if (globalState.hasOwnProperty(key)) {
        globalState[key] = value;
    }

    mgraphics.redraw();
}

function pauli_msg() {
    var args = arrayfromargs(arguments);
    if (args.length < 2) {
        return;
    }

    var key = String(args[0]);
    var value = parseFloat(args[1]);

    if (isNaN(value)) {
        return;
    }

    pauli[key] = value;
    mgraphics.redraw();
}

function reset() {
    for (var i = 0; i < NUM_QUBITS; i++) {
        qubits[i].x = 0.0;
        qubits[i].y = 0.0;
        qubits[i].z = 1.0;
        qubits[i].bloch_r = 1.0;
        qubits[i].bloch_theta = 0.0;
        qubits[i].bloch_phi = 0.0;
        qubits[i].degree = 1.0;
        qubits[i].azimuth = 0.0;
        qubits[i].ellipticity = 0.0;
        qubits[i].circularity = 0.0;
        qubits[i].linearity = 1.0;
        qubits[i].basis_theta = 0.0;
        qubits[i].basis_phi = 0.0;
        qubits[i].basis_projection = 0.0;
        qubits[i].swirl = 0.0;
        qubits[i].interference = 0.0;
        qubits[i].brightness = 1.0;
    }

    for (var k in globalState) {
        globalState[k] = 0.0;
    }

    for (var p in pauli) {
        pauli[p] = 0.0;
    }

    mgraphics.redraw();
}

// ------------------------------------------------------------
// Drawing
// ------------------------------------------------------------

function paint() {
    var w = box.rect[2] - box.rect[0];
    var h = box.rect[3] - box.rect[1];

    // Background
    rect(0, 0, w, h, 0.035, 0.038, 0.045, 1.0);

    draw_text(title, 18, 24, 14, 0.83, 0.86, 0.90, 0.95);
    draw_text("X/Y = Pauli plane  |  Z = polarity  |  gold = moving measurement basis",
              18, 43, 9, 0.50, 0.54, 0.58, 0.9);

    var top = 62;
    var bottomPanelH = 128;
    var gridH = h - top - bottomPanelH - 18;
    var cellW = w * 0.5;
    var cellH = gridH * 0.5;
    var radius = Math.min(cellW, cellH) * 0.30;

    draw_qubit_panel(0, cellW * 0.5, top + cellH * 0.5, radius);
    draw_qubit_panel(1, cellW * 1.5, top + cellH * 0.5, radius);
    draw_qubit_panel(2, cellW * 0.5, top + cellH * 1.5, radius);
    draw_qubit_panel(3, cellW * 1.5, top + cellH * 1.5, radius);

    draw_global_panel(18, h - bottomPanelH + 4, w - 36, bottomPanelH - 16);
}

function draw_qubit_panel(q, cx, cy, radius) {
    var st = qubits[q];

    var panelW = radius * 3.05;
    var panelH = radius * 2.55;
    rect(cx - panelW * 0.5, cy - panelH * 0.5, panelW, panelH,
         0.055, 0.060, 0.070, 0.88);
    stroked_rect(cx - panelW * 0.5, cy - panelH * 0.5, panelW, panelH,
                 1.0, 0.16, 0.18, 0.22, 0.85);

    draw_text("q" + q, cx - panelW * 0.5 + 10, cy - panelH * 0.5 + 18,
              11, 0.80, 0.84, 0.88, 0.95);

    // Bloch/Stokes projection disk.
    circle(cx, cy, radius, 1.0, 0.25, 0.28, 0.33, 0.90);
    circle(cx, cy, radius * 0.5, 0.75, 0.16, 0.18, 0.21, 0.70);

    // Axes.
    line(cx - radius, cy, cx + radius, cy, 1.0, 0.28, 0.30, 0.34, 0.85);
    line(cx, cy - radius, cx, cy + radius, 1.0, 0.28, 0.30, 0.34, 0.85);

    draw_text("X", cx + radius + 5, cy + 3, 8, 0.55, 0.58, 0.62, 0.8);
    draw_text("Y", cx + 4, cy - radius - 5, 8, 0.55, 0.58, 0.62, 0.8);

    // Main Pauli vector in X/Y plane.
    var vx = clamp(st.x, -1.0, 1.0);
    var vy = clamp(st.y, -1.0, 1.0);
    var px = cx + vx * radius;
    var py = cy - vy * radius;

    line(cx, cy, px, py, 2.2, 0.12, 0.78, 0.98, 0.95);
    fill_circle(px, py, 4.5, 0.12, 0.78, 0.98, 0.95);

    // Measurement-basis vector projected into X/Y plane.
    var bx = Math.sin(st.basis_theta) * Math.cos(st.basis_phi);
    var by = Math.sin(st.basis_theta) * Math.sin(st.basis_phi);
    var bpx = cx + bx * radius * 0.92;
    var bpy = cy - by * radius * 0.92;

    line(cx, cy, bpx, bpy, 1.4, 1.0, 0.72, 0.20, 0.90);
    fill_circle(bpx, bpy, 3.5, 1.0, 0.72, 0.20, 0.90);

    // Z gauge to the right.
    var gzX = cx + radius + 24;
    var gzY = cy - radius;
    var gzH = radius * 2;
    var gzW = 10;
    rect(gzX, gzY, gzW, gzH, 0.08, 0.09, 0.10, 0.9);
    stroked_rect(gzX, gzY, gzW, gzH, 1.0, 0.25, 0.28, 0.32, 0.8);

    var zMid = gzY + gzH * 0.5;
    line(gzX - 2, zMid, gzX + gzW + 2, zMid, 1.0, 0.45, 0.45, 0.45, 0.65);

    var zv = clamp(st.z, -1.0, 1.0);
    if (zv >= 0) {
        var zh = gzH * 0.5 * zv;
        rect(gzX + 2, zMid - zh, gzW - 4, zh,
             0.65, 0.85, 0.45, 0.9);
    } else {
        var zh2 = gzH * 0.5 * Math.abs(zv);
        rect(gzX + 2, zMid, gzW - 4, zh2,
             0.95, 0.38, 0.32, 0.9);
    }

    draw_text("Z", gzX - 1, gzY - 7, 8, 0.55, 0.58, 0.62, 0.85);

    // Inner pulse from basis projection.
    var bp = norm01(st.basis_projection);
    circle(cx, cy, radius * (0.15 + 0.25 * bp), 1.0,
           1.0, 0.72, 0.20, 0.35 + 0.35 * bp);

  // Text readout.
    var tx = cx - panelW * 0.5 + 10;
    var ty = cy + panelH * 0.5 - 58;

    draw_text("X " + fmt(st.x) + "   Y " + fmt(st.y) + "   Z " + fmt(st.z),
            tx, ty, 8, 0.72, 0.76, 0.80, 0.92);

    draw_text("theta " + fmt(st.bloch_theta) +
            "   phi " + fmt(st.bloch_phi),
            tx, ty + 12, 8, 0.72, 0.76, 0.80, 0.92);

    draw_text("degree " + fmt(st.degree) +
            "   azim " + fmt(st.azimuth),
            tx, ty + 24, 8, 0.72, 0.76, 0.80, 0.92);

    draw_text("ellip " + fmt(st.ellipticity) +
            "   circ " + fmt(st.circularity) +
            "   lin " + fmt(st.linearity),
            tx, ty + 36, 8, 0.72, 0.76, 0.80, 0.92);

    draw_text("basis " + fmt(st.basis_projection),
            tx, ty + 48, 8, 1.0, 0.72, 0.20, 0.92);

    // Small audio descriptor bars.
    draw_bar("I", tx, ty + 26, panelW * 0.28, 5, st.interference, true);
    draw_bar("S", tx + panelW * 0.33, ty + 26, panelW * 0.28, 5, st.swirl, true);
    draw_bar("B", tx + panelW * 0.66, ty + 26, panelW * 0.25, 5, st.brightness, false);
    draw_bar("degree", tx, ty + 58, panelW * 0.28, 5, st.degree, false);
    draw_bar("circ", tx + panelW * 0.33, ty + 58, panelW * 0.28, 5, st.circularity, false);
    draw_bar("lin", tx + panelW * 0.66, ty + 58, panelW * 0.25, 5, st.linearity, false);

}

function draw_global_panel(x, y, w, h) {
    rect(x, y, w, h, 0.052, 0.057, 0.067, 0.92);
    stroked_rect(x, y, w, h, 1.0, 0.16, 0.18, 0.22, 0.9);

    draw_text("GLOBAL FIELD", x + 10, y + 18, 11, 0.82, 0.85, 0.89, 0.95);

    var barX = x + 12;
    var barY = y + 40;
    var barW = w * 0.34;
    var barH = 8;
    var gap = 18;

    draw_bar("spin X", barX, barY, barW, barH, globalState.spin_x, true);
    draw_bar("spin Y", barX, barY + gap, barW, barH, globalState.spin_y, true);
    draw_bar("spin Z", barX, barY + gap * 2, barW, barH, globalState.spin_z, true);
    draw_bar("basis", barX, barY + gap * 3, barW, barH, globalState.basis_projection, true);

    var ax = x + w * 0.42;
    draw_bar("phase", ax, barY, barW, barH, globalState.audio_phase, true);
    draw_bar("swirl", ax, barY + gap, barW, barH, globalState.audio_swirl, true);
    draw_bar("interference", ax, barY + gap * 2, barW, barH, globalState.audio_interference, true);
    draw_bar("brightness", ax, barY + gap * 3, barW, barH, globalState.audio_brightness, false);

    draw_pauli_field(x + w * 0.80, y + h * 0.54, Math.min(w, h) * 0.32);
}

function draw_pauli_field(cx, cy, radius) {
    draw_text("PAULI STRINGS", cx - radius, cy - radius - 12,
              9, 0.70, 0.74, 0.78, 0.9);

    var keys = ["ZZII", "XXII", "YYII", "ZIZI", "IZIZ", "ZZZZ", "XXXX", "YYYY"];
    var n = keys.length;

    circle(cx, cy, radius, 1.0, 0.25, 0.28, 0.32, 0.75);

    for (var i = 0; i < n; i++) {
        var a = -Math.PI / 2 + (2 * Math.PI * i / n);
        var k = keys[i];
        var v = clamp(pauli[k], -1.0, 1.0);

        var rr = radius * (0.25 + 0.72 * abs01(v));
        var px = cx + Math.cos(a) * rr;
        var py = cy + Math.sin(a) * rr;

        var cr = v >= 0 ? 0.20 : 0.95;
        var cg = v >= 0 ? 0.78 : 0.38;
        var cb = v >= 0 ? 0.95 : 0.32;

        line(cx, cy, px, py, 1.2, cr, cg, cb, 0.80);
        fill_circle(px, py, 3.5 + 3.5 * abs01(v), cr, cg, cb, 0.85);

        var lx = cx + Math.cos(a) * (radius + 22);
        var ly = cy + Math.sin(a) * (radius + 22);
        draw_text(k, lx - 14, ly + 3, 7, 0.60, 0.64, 0.68, 0.85);
    }
}

// ------------------------------------------------------------
// Compatibility aliases
// ------------------------------------------------------------

function pauli() {
    pauli_msg.apply(this, arguments);
}

function bang() {
    mgraphics.redraw();
}