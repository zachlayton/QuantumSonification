// qmw_platonic_geometry_controller_dual_spectral_dc_safe_v1.js
// Named-form, interpolation, spectral-noise, and DC-safety controller.
// Connect outlet 0 directly to [gen~].
//
// Messages:
//   shape cube
//   between cube icosahedron
//   morph 0.5
//   transition tetra dodeca 0.35
//   dual
//   next / prev
//   rotate x 90
//   rx 15 / ry -30 / rz 45
//   reset
//
// Parameter forwarding:
//   harmonicity 0.5
//   harmonic_span 0.25
//   topology 0.8
//   geometry_depth 0.6
//   geometry_depth_slew_ms 100
//   pauli_depth 0.2
//   morph_slew_ms 750
//   noise_amount 0.22
//   noise_attack_ms 3
//   noise_decay_ms 22
//   onset_threshold 0.012
//   onset_sensitivity 10
//   noise_color 0.72
//   noise_floor 0
//   noise_spectral_mode 0       (0 quantum, 1 input spectrum)
//   noise_spectral_amount 1
//   noise_spectral_q 7
//   noise_spectral_gain 2.5
//   noise_spectral_base_hz 55
//   noise_spectral_transition_ms 40
//   dc_block_hz 18
//   quantum_magnitudes <8 or more values>
//   quantum_harmonics <8 or more values>
//   rotation_slew_ms 100
//   diffusion_slew_ms 100

autowatch = 1;
inlets = 1;
outlets = 2;

var names = {
    tetra: 0,
    tetrahedron: 0,
    cube: 1,
    hexahedron: 1,
    octa: 2,
    octahedron: 2,
    dodeca: 3,
    dodecahedron: 3,
    icosa: 4,
    icosahedron: 4
};

var displayNames = [
    "tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"
];
var path = [0, 1, 3, 4, 2];
var duals = [0, 2, 1, 4, 3];
var a = 1;
var b = 2;
var amount = 0;
var rotations = [0, 0, 0];

function indexOfName(value) {
    var key = String(value).toLowerCase();
    if (names.hasOwnProperty(key)) return names[key];
    var numeric = Math.round(Number(value));
    if (!isNaN(numeric)) return Math.max(0, Math.min(4, numeric));
    return 1;
}

function emitState() {
    outlet(0, ["solid_a", a]);
    outlet(0, ["solid_b", b]);
    outlet(0, ["geometry_morph", amount]);
    outlet(1, ["geometry", displayNames[a], displayNames[b], amount]);
}

function shape(value) {
    var index = indexOfName(value);
    a = index;
    b = index;
    amount = 0;
    emitState();
}

function between(first, second) {
    a = indexOfName(first);
    b = indexOfName(second);
    amount = 0;
    emitState();
}

function morph(value) {
    amount = Math.max(0, Math.min(1, Number(value)));
    outlet(0, ["geometry_morph", amount]);
    outlet(1, ["geometry", displayNames[a], displayNames[b], amount]);
}

function transition(first, second, value) {
    a = indexOfName(first);
    b = indexOfName(second);
    amount = Math.max(0, Math.min(1, Number(value)));
    emitState();
}

function dual() {
    var current = amount < 0.5 ? a : b;
    a = current;
    b = duals[current];
    amount = 0;
    emitState();
}

function next() {
    var current = amount < 0.5 ? a : b;
    var position = path.indexOf(current);
    if (position < 0) position = 0;
    a = current;
    b = path[(position + 1) % path.length];
    amount = 0;
    emitState();
}

function prev() {
    var current = amount < 0.5 ? a : b;
    var position = path.indexOf(current);
    if (position < 0) position = 0;
    a = current;
    b = path[(position + path.length - 1) % path.length];
    amount = 0;
    emitState();
}

function axisIndex(axis) {
    var key = String(axis).toLowerCase();
    if (key === "x") return 0;
    if (key === "y") return 1;
    return 2;
}

function rotate(axis, degrees) {
    var i = axisIndex(axis);
    rotations[i] = Number(degrees) / 360.0;
    outlet(0, [["rot_x", "rot_y", "rot_z"][i], rotations[i]]);
    outlet(1, ["rotation", rotations[0], rotations[1], rotations[2]]);
}

function incrementRotation(i, degrees) {
    rotations[i] += Number(degrees) / 360.0;
    rotations[i] = rotations[i] - Math.floor(rotations[i]);
    outlet(0, [["rot_x", "rot_y", "rot_z"][i], rotations[i]]);
    outlet(1, ["rotation", rotations[0], rotations[1], rotations[2]]);
}

function rx(degrees) { incrementRotation(0, degrees === undefined ? 90 : degrees); }
function ry(degrees) { incrementRotation(1, degrees === undefined ? 90 : degrees); }
function rz(degrees) { incrementRotation(2, degrees === undefined ? 90 : degrees); }

function forwardParameter(name, value) {
    outlet(0, [name, Number(value)]);
}

function harmonicity(value) { forwardParameter("harmonicity", value); }
function harmonic_span(value) { forwardParameter("harmonic_span", value); }
function topology(value) { forwardParameter("topology", value); }
function geometry_depth(value) { forwardParameter("geometry_depth", value); }
function geometry_depth_slew_ms(value) { forwardParameter("geometry_depth_slew_ms", value); }
function pauli_depth(value) { forwardParameter("pauli_depth", value); }
function morph_slew_ms(value) { forwardParameter("morph_slew_ms", value); }
function rotation_slew_ms(value) { forwardParameter("rotation_slew_ms", value); }
function size(value) { forwardParameter("size", value); }
function decay(value) { forwardParameter("decay", value); }
function absorb(value) { forwardParameter("absorb", value); }
function diffusion(value) { forwardParameter("diffusion", value); }
function diffusion_slew_ms(value) { forwardParameter("diffusion_slew_ms", value); }
function width(value) { forwardParameter("width", value); }
function freeze(value) { forwardParameter("freeze", value); }
function input_gain(value) { forwardParameter("input_gain", value); }
function output_gain(value) { forwardParameter("output_gain", value); }
function noise_amount(value) { forwardParameter("noise_amount", value); }
function noise_attack_ms(value) { forwardParameter("noise_attack_ms", value); }
function noise_decay_ms(value) { forwardParameter("noise_decay_ms", value); }
function onset_threshold(value) { forwardParameter("onset_threshold", value); }
function onset_sensitivity(value) { forwardParameter("onset_sensitivity", value); }
function noise_color(value) { forwardParameter("noise_color", value); }
function noise_floor(value) { forwardParameter("noise_floor", value); }
function noise_spectral_mode(value) { forwardParameter("noise_spectral_mode", value); }
function noise_spectral_amount(value) { forwardParameter("noise_spectral_amount", value); }
function noise_spectral_q(value) { forwardParameter("noise_spectral_q", value); }
function noise_spectral_gain(value) { forwardParameter("noise_spectral_gain", value); }
function noise_spectral_base_hz(value) { forwardParameter("noise_spectral_base_hz", value); }
function noise_spectral_transition_ms(value) { forwardParameter("noise_spectral_transition_ms", value); }
function dc_block_hz(value) { forwardParameter("dc_block_hz", value); }

function forwardQuantumList(prefix, values, fallback) {
    var count = Math.min(8, values.length);
    for (var i = 0; i < count; i++) {
        var value = Number(values[i]);
        if (isNaN(value)) value = fallback(i);
        outlet(0, [prefix + i, value]);
    }
}

function quantum_magnitudes() {
    var values = arrayfromargs(arguments);
    forwardQuantumList("qm", values, function () { return 0; });
}

function quantum_harmonics() {
    var values = arrayfromargs(arguments);
    forwardQuantumList("qh", values, function (index) { return index + 1; });
}

function bang() {
    post("Platonic geometry controller received bang\n");
    outlet(0, ["solid_a", a]);
    outlet(1, ["diagnostic", "bang", a, b, amount]);
}

function msg_int(value) {
    post("Platonic controller received int:", value, "\n");
    outlet(0, ["geometry_morph", value]);
}

function msg_float(value) {
    post("Platonic controller received float:", value, "\n");
    outlet(0, ["geometry_morph", value]);
}

function anything() {
    var args = arrayfromargs(arguments);
    post("Platonic controller received:", messagename);
    for (var i = 0; i < args.length; i++) {
        post(" ", args[i]);
    }
    post("\n");
}

function reset() {
    a = 1;
    b = 2;
    amount = 0;
    rotations = [0, 0, 0];
    emitState();
    outlet(0, ["rot_x", 0]);
    outlet(0, ["rot_y", 0]);
    outlet(0, ["rot_z", 0]);
    post("Platonic geometry controller reset\n");
}

function loadbang() {
    reset();
}
