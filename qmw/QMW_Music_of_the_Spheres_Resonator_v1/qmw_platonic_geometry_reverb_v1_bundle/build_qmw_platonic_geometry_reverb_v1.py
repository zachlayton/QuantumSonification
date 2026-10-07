from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

OUT = Path('/tmp/platonic_out')
OUT.mkdir(parents=True, exist_ok=True)

PHI = (1.0 + math.sqrt(5.0)) / 2.0


def normalize_rows(values):
    arr = np.asarray(values, dtype=float)
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)


def regular_solids():
    tetra = normalize_rows([
        (1, 1, 1),
        (1, -1, -1),
        (-1, 1, -1),
        (-1, -1, 1),
    ])

    cube = normalize_rows(list(itertools.product([-1, 1], repeat=3)))

    octa = normalize_rows([
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    ])

    dodeca_values = list(itertools.product([-1, 1], repeat=3))
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            dodeca_values.extend([
                (0, s1 / PHI, s2 * PHI),
                (s1 / PHI, s2 * PHI, 0),
                (s2 * PHI, 0, s1 / PHI),
            ])
    dodeca = normalize_rows(dodeca_values)

    icosa_values = []
    for s1 in (-1, 1):
        for s2 in (-1, 1):
            icosa_values.extend([
                (0, s1, s2 * PHI),
                (s1, s2 * PHI, 0),
                (s2 * PHI, 0, s1),
            ])
    icosa = normalize_rows(icosa_values)

    return [
        {'id': 0, 'name': 'tetrahedron', 'short': 'tetra', 'p': 3, 'q': 3, 'coords': tetra},
        {'id': 1, 'name': 'cube', 'short': 'cube', 'p': 4, 'q': 3, 'coords': cube},
        {'id': 2, 'name': 'octahedron', 'short': 'octa', 'p': 3, 'q': 4, 'coords': octa},
        {'id': 3, 'name': 'dodecahedron', 'short': 'dodeca', 'p': 5, 'q': 3, 'coords': dodeca},
        {'id': 4, 'name': 'icosahedron', 'short': 'icosa', 'p': 3, 'q': 5, 'coords': icosa},
    ]


def find_edges(coords):
    distances = []
    n = len(coords)
    for i in range(n):
        for j in range(i + 1, n):
            distance = float(np.linalg.norm(coords[i] - coords[j]))
            distances.append((distance, i, j))
    edge_length = min(distance for distance, _, _ in distances if distance > 1e-10)
    edges = [
        (i, j)
        for distance, i, j in distances
        if abs(distance - edge_length) < 1e-6
    ]
    return edge_length, edges


def fmt(value):
    if abs(value) < 5e-10:
        value = 0.0
    text = f'{value:.9f}'
    text = text.rstrip('0').rstrip('.')
    if text in {'-0', ''}:
        text = '0'
    return text


def build_tables():
    solids = regular_solids()
    canonical = solids[3]['coords']  # dodecahedron: twenty canonical DSP sites
    reference_axis = normalize_rows([(1.0, math.sqrt(2.0), PHI)])[0]

    for solid in solids:
        coords = solid['coords']
        edge_length, edges = find_edges(coords)
        n = len(coords)
        degree = np.zeros(n, dtype=int)
        for i, j in edges:
            degree[i] += 1
            degree[j] += 1
        if not np.all(degree == solid['q']):
            raise RuntimeError(f"Unexpected degree for {solid['name']}: {degree}")

        # Embed each solid in a common set of twenty directional sites.
        cost = 1.0 - coords @ canonical.T
        row_ind, col_ind = linear_sum_assignment(cost)
        slot_to_vertex = {int(slot): int(vertex) for vertex, slot in zip(row_ind, col_ind)}
        vertex_to_slot = {vertex: slot for slot, vertex in slot_to_vertex.items()}

        active = np.zeros(20, dtype=float)
        slot_coords = canonical.copy()
        for slot, vertex in slot_to_vertex.items():
            active[slot] = 1.0
            slot_coords[slot] = coords[vertex]

        # Spatially ordered overtone indices: vertex ranking along an irrational axis.
        projections = coords @ reference_axis
        ordered_vertices = list(np.argsort(projections))
        harmonic_number_by_vertex = {
            int(vertex): rank + 1 for rank, vertex in enumerate(ordered_vertices)
        }
        active_harmonics = np.array([
            harmonic_number_by_vertex[v] for v in range(n)
        ], dtype=float)
        harmonic_log_center = float(np.mean(np.log(active_harmonics)))
        harmonic_log_ratio = np.zeros(20, dtype=float)
        pauli_index = np.zeros(20, dtype=int)
        for slot, vertex in slot_to_vertex.items():
            harmonic_number = harmonic_number_by_vertex[vertex]
            harmonic_log_ratio[slot] = harmonic_log_center - math.log(harmonic_number)
            pauli_index[slot] = (harmonic_number - 1) % 8

        # Embed normalized adjacency A/q into twenty sites.
        adjacency = np.zeros((20, 20), dtype=float)
        embedded_edges = []
        for i, j in edges:
            si, sj = vertex_to_slot[i], vertex_to_slot[j]
            adjacency[si, sj] = 1.0 / solid['q']
            adjacency[sj, si] = 1.0 / solid['q']
            embedded_edges.append((si, sj))

        eigvals = np.linalg.eigvalsh(adjacency)
        if np.max(np.abs(eigvals)) > 1.0000001:
            raise RuntimeError(f"Adjacency is not contractive for {solid['name']}")

        solid.update({
            'vertex_count': n,
            'edge_count': len(edges),
            'edge_length': edge_length,
            'degree': int(solid['q']),
            'slot_to_vertex': slot_to_vertex,
            'active': active,
            'slot_coords': slot_coords,
            'harmonic_log_ratio': harmonic_log_ratio,
            'pauli_index': pauli_index,
            'adjacency': adjacency,
            'embedded_edges': embedded_edges,
            'spectral_radius': float(np.max(np.abs(eigvals))),
        })
    return solids, canonical


def selection_block(prefix, index_name, solids):
    # Variables for 20 nodes: active, xyz, overtone log ratio, and Pauli source.
    lines = []
    default = solids[0]
    for i in range(20):
        lines.extend([
            f'a{prefix}{i+1} = {fmt(default["active"][i])};',
            f'x{prefix}{i+1} = {fmt(default["slot_coords"][i,0])};',
            f'y{prefix}{i+1} = {fmt(default["slot_coords"][i,1])};',
            f'z{prefix}{i+1} = {fmt(default["slot_coords"][i,2])};',
            f'h{prefix}{i+1} = {fmt(default["harmonic_log_ratio"][i])};',
            f'p{prefix}{i+1} = raw{int(default["pauli_index"][i])+1};',
        ])

    for s, solid in enumerate(solids):
        keyword = 'if' if s == 0 else 'else if'
        lines.append(f'{keyword} ({index_name} == {s}) {{')
        for i in range(20):
            lines.extend([
                f'    a{prefix}{i+1} = {fmt(solid["active"][i])};',
                f'    x{prefix}{i+1} = {fmt(solid["slot_coords"][i,0])};',
                f'    y{prefix}{i+1} = {fmt(solid["slot_coords"][i,1])};',
                f'    z{prefix}{i+1} = {fmt(solid["slot_coords"][i,2])};',
                f'    h{prefix}{i+1} = {fmt(solid["harmonic_log_ratio"][i])};',
                f'    p{prefix}{i+1} = raw{int(solid["pauli_index"][i])+1};',
            ])
        lines.append('}')
    return '\n'.join(lines)


def adjacency_formulas(solids):
    lines = []
    for s, solid in enumerate(solids):
        adjacency = solid['adjacency']
        lines.append(f'// {solid["name"]}: {solid["vertex_count"]} vertices, degree {solid["degree"]}')
        for i in range(20):
            terms = []
            for j in range(20):
                weight = adjacency[i, j]
                if abs(weight) > 1e-12:
                    terms.append(f'({fmt(weight)} * f{j+1})')
            expression = ' + '.join(terms) if terms else '0'
            lines.append(f'adj{s}_{i+1} = {expression};')
    return '\n'.join(lines)


def adjacency_selection(prefix, index_name, solids):
    lines = []
    for i in range(20):
        lines.append(f'adj{prefix}{i+1} = adj0_{i+1};')
    for s in range(len(solids)):
        keyword = 'if' if s == 0 else 'else if'
        lines.append(f'{keyword} ({index_name} == {s}) {{')
        for i in range(20):
            lines.append(f'    adj{prefix}{i+1} = adj{s}_{i+1};')
        lines.append('}')
    return '\n'.join(lines)


def make_genexpr(solids):
    params = '''Param solid_a(1);
Param solid_b(2);
Param geometry_morph(0);
Param morph_slew_ms(500);
Param rotation_slew_ms(100);
Param size(0.45);
Param decay(0.72);
Param diffusion(0.72);
Param diffusion_slew_ms(100);
Param absorb(0.35);
Param tilt(0);
Param topology(0.80);
Param geometry_depth(0.55);
Param geometry_depth_slew_ms(100);
Param harmonicity(0.25);
Param harmonic_span(0.22);
Param pauli_depth(0.16);
Param rot_x(0);
Param rot_y(0);
Param rot_z(0);
Param width(0.90);
Param freeze(0);
Param input_gain(0.25);
Param output_gain(0.40);'''

    delays = '\n'.join(f'Delay dl{i}(384000);' for i in range(1, 21))
    lowpasses = '\n'.join(f'History lp{i}(0);' for i in range(1, 21))
    histories = lowpasses + '\n\n' + '\n'.join([
        'History apz1(0);', 'History apz2(0);', 'History apz3(0);', 'History apz4(0);',
        'History diffusion_z(0.72);',
        'History morph_z(0);', 'History morph_z2(0);',
        'History geometry_depth_z(0.55);',
        'History rot_x_z(0);', 'History rot_y_z(0);', 'History rot_z_z(0);',
    ])

    raw = '\n'.join(f'raw{i} = clamp(in{i+1}, -1, 1);' for i in range(1, 9))
    select_a = selection_block('A', 'sa', solids)
    select_b = selection_block('B', 'sb', solids)

    node_geometry = []
    for i in range(1, 21):
        node_geometry.extend([
            f'act{i} = mix(aA{i}, aB{i}, morph);',
            f'amp{i} = sqrt(max(act{i}, 0));',
            f'xg{i} = mix(xA{i}, xB{i}, morph);',
            f'yg{i} = mix(yA{i}, yB{i}, morph);',
            f'zg{i} = mix(zA{i}, zB{i}, morph);',
            f'hl{i} = mix(hA{i}, hB{i}, morph);',
            f'pv{i} = mix(pA{i}, pB{i}, morph);',
            '',
            f'xr1_{i} = xg{i};',
            f'yr1_{i} = yg{i} * cx - zg{i} * sx;',
            f'zr1_{i} = yg{i} * sx + zg{i} * cx;',
            f'xr2_{i} = xr1_{i} * cy + zr1_{i} * sy;',
            f'yr2_{i} = yr1_{i};',
            f'zr2_{i} = -xr1_{i} * sy + zr1_{i} * cy;',
            f'xr{i} = xr2_{i} * cz - yr2_{i} * sz;',
            f'yr{i} = xr2_{i} * sz + yr2_{i} * cz;',
            f'zr{i} = zr2_{i};',
            f'proj{i} = xr{i} * 0.425325404 + yr{i} * 0.601501006 + zr{i} * 0.688190961;',
            f'logratio{i} = (1 - harm) * (gdepth * proj{i}) + harm * (hspan * hl{i}) + pdepth * pv{i};',
            f'dms{i} = base_ms * size_scale * exp(logratio{i});',
            f'd{i} = clamp(dms{i} * sr * 0.001, 16, 383999);',
        ])
    node_geometry_text = '\n'.join(node_geometry)

    reads = '\n'.join(f'r{i} = dl{i}.read(d{i});' for i in range(1, 21))

    damping = []
    for i in range(1, 21):
        damping.extend([
            f'lp{i} = lp{i} + cut_norm * (r{i} - lp{i});',
            f'f{i} = mix(r{i}, lp{i}, ab) * amp{i};',
        ])
    damping_text = '\n'.join(damping)

    adj_formula_text = adjacency_formulas(solids)
    adj_select_a = adjacency_selection('A', 'sa', solids)
    adj_select_b = adjacency_selection('B', 'sb', solids)

    adj_morph = '\n'.join(
        f'adj{i} = mix(adjA{i}, adjB{i}, morph);' for i in range(1, 21)
    )

    sum_f = ' + '.join(f'(amp{i} * f{i})' for i in range(1, 21))
    sum_act = ' + '.join(f'act{i}' for i in range(1, 21))
    hh = '\n'.join(
        f'hh{i} = f{i} - 2 * amp{i} * hh_dot / hh_den;' for i in range(1, 21)
    )
    net = '\n'.join(
        f'net{i} = mix(hh{i}, adj{i}, topo);' for i in range(1, 21)
    )

    gains = '\n'.join(
        f'g{i} = pow(10, (-3 * d{i}) / (sr * t60));' for i in range(1, 21)
    )

    # Alternating injection signs reduce common-mode buildup.
    signs = [1 if bin(i).count('1') % 2 == 0 else -1 for i in range(20)]
    writes = []
    for i, sign in enumerate(signs, 1):
        writes.extend([
            f'inj{i} = diffused * {sign} * amp{i} * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr{i}));',
            f'fb{i} = net{i} * mix(g{i}, 0.9995, fr);',
            f'w{i} = (inj{i} * (1 - fr) + fb{i}) * amp{i};',
            f'dl{i}.write(tanh(w{i}));',
        ])
    writes_text = '\n'.join(writes)

    output_terms_l = []
    output_terms_r = []
    for i in range(1, 21):
        output_terms_l.append(
            f'(r{i} * amp{i} * sqrt(0.5 * (1 - clamp(xr{i} * wd, -1, 1))))'
        )
        output_terms_r.append(
            f'(r{i} * amp{i} * sqrt(0.5 * (1 + clamp(xr{i} * wd, -1, 1))))'
        )
    left_sum = ' +\n    '.join(output_terms_l)
    right_sum = ' +\n    '.join(output_terms_r)

    code = f'''// qmw_platonic_geometry_reverb_v1.genexpr
// Twenty-node morphing Platonic feedback-delay network for Max Gen~.
//
// in1      mono audio input
// in2..in9 eight Pauli-correlation signals in the range -1..1
// out1     left reverberant output
// out2     right reverberant output
//
// solid IDs:
// 0 tetrahedron  {{3,3}}
// 1 cube         {{4,3}}
// 2 octahedron   {{3,4}}
// 3 dodecahedron {{5,3}}
// 4 icosahedron  {{3,5}}
//
// The engine keeps twenty DSP nodes and morphs four linked fields:
// activation, spherical coordinates, overtone-derived delay ratios,
// and normalized graph adjacency. This allows continuous topology changes.

{params}

{delays}

{histories}

sr = samplerate;
pi2 = 6.28318530718;

// Input diffusion.
diffusion_target = clamp(diffusion, 0, 1);
diffusion_seconds = max(diffusion_slew_ms, 0) * 0.001;
diffusion_coeff = (diffusion_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * diffusion_seconds)));
diffusion_z = diffusion_z + diffusion_coeff * (diffusion_target - diffusion_z);
diff_g = 0.15 + 0.70 * diffusion_z;
x = in1 * input_gain;
a1d = x - diff_g * apz1;
y1d = apz1 + diff_g * a1d;
apz1 = a1d;
a2d = y1d - diff_g * apz2;
y2d = apz2 + diff_g * a2d;
apz2 = a2d;
a3d = y2d - diff_g * apz3;
y3d = apz3 + diff_g * a3d;
apz3 = a3d;
a4d = y3d - diff_g * apz4;
diffused = apz4 + diff_g * a4d;
apz4 = a4d;

// Smooth the global geometry morph internally.
target_morph = clamp(geometry_morph, 0, 1);
morph_seconds = max(morph_slew_ms, 0) * 0.001;
morph_coeff = (morph_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * morph_seconds)));
morph_z = morph_z + morph_coeff * (target_morph - morph_z);
morph_z2 = morph_z2 + morph_coeff * (morph_z - morph_z2);
morph_phase = clamp(morph_z2, 0, 1);
morph = morph_phase * morph_phase * (3 - 2 * morph_phase);

sa = clamp(floor(solid_a + 0.5), 0, 4);
sb = clamp(floor(solid_b + 0.5), 0, 4);

{raw}

// Source-solid field.
{select_a}

// Destination-solid field.
{select_b}

// Global geometric and harmonic controls.
s = clamp(size, 0, 1);
size_scale = pow(2, (s * 4) - 2);
base_ms = 47;
geometry_depth_target = clamp(geometry_depth, 0, 1);
geometry_depth_seconds = max(geometry_depth_slew_ms, 0) * 0.001;
geometry_depth_coeff = (geometry_depth_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * geometry_depth_seconds)));
geometry_depth_z = geometry_depth_z + geometry_depth_coeff * (geometry_depth_target - geometry_depth_z);
gdepth = geometry_depth_z * 0.90;
harm = clamp(harmonicity, 0, 1);
hspan = clamp(harmonic_span, 0, 1);
pdepth = clamp(pauli_depth, 0, 1) * 0.38;

// Smooth rotations along the shortest circular path to avoid discontinuous
// delay-time and spatial changes. Rotation values are measured in turns.
rotation_seconds = max(rotation_slew_ms, 0) * 0.001;
rotation_coeff = (rotation_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * rotation_seconds)));
rot_x_delta = rot_x - rot_x_z;
rot_y_delta = rot_y - rot_y_z;
rot_z_delta = rot_z - rot_z_z;
rot_x_delta = rot_x_delta - floor(rot_x_delta + 0.5);
rot_y_delta = rot_y_delta - floor(rot_y_delta + 0.5);
rot_z_delta = rot_z_delta - floor(rot_z_delta + 0.5);
rot_x_z = rot_x_z + rotation_coeff * rot_x_delta;
rot_y_z = rot_y_z + rotation_coeff * rot_y_delta;
rot_z_z = rot_z_z + rotation_coeff * rot_z_delta;

rxang = rot_x_z * pi2;
ryang = rot_y_z * pi2;
rzang = rot_z_z * pi2;
cx = cos(rxang); sx = sin(rxang);
cy = cos(ryang); sy = sin(ryang);
cz = cos(rzang); sz = sin(rzang);

{node_geometry_text}

active_sum = max({sum_act}, 0.000001);
input_norm = 1 / sqrt(active_sum);

{reads}

// Frequency-dependent absorption in every feedback branch.
ab = clamp(absorb, 0, 1);
tl = clamp(tilt, -1, 1);
cut_norm = clamp(0.015 + (1 - ab) * 0.45 + tl * 0.12, 0.005, 0.48);

{damping_text}

// Five normalized Platonic adjacency operators.
{adj_formula_text}

// Select and interpolate the two graph topologies.
{adj_select_a}

{adj_select_b}

{adj_morph}

// Active-node Householder diffusion remains energy preserving.
hh_dot = {sum_f};
hh_den = active_sum;
{hh}

topo = clamp(topology, 0, 1);
{net}

// Delay-compensated T60 feedback.
dec = clamp(decay, 0, 1);
t60 = 0.18 * pow(194.444444, dec);
{gains}

fr = clamp(freeze, 0, 1);
{writes_text}

// Spatial decoder follows the continuously rotated/morphed coordinates.
wd = clamp(width, 0, 1);
out_norm = output_gain / sqrt(active_sum);
left =
    {left_sum};
right =
    {right_sum};
out1 = left * out_norm;
out2 = right * out_norm;
'''
    return code


def make_controller():
    return r'''// qmw_platonic_geometry_controller_v1.js
// Named-form and interpolation controller for qmw_platonic_geometry_reverb_v1.
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
'''


def make_readme(solids):
    rows = []
    for s in solids:
        rows.append(
            f"{s['id']}  {s['name']:<14} Schlaefli={{{s['p']},{s['q']}}} "
            f"vertices={s['vertex_count']:>2} edges={s['edge_count']:>2} degree={s['degree']}"
        )
    solid_table = '\n'.join(rows)
    return f'''QMW Platonic Geometry Reverb v1
================================

FILES
-----
qmw_platonic_geometry_reverb_v1.genexpr
qmw_platonic_geometry_controller_v1.js
qmw_platonic_geometry_reverb_v1_GEOMETRY.json
build_qmw_platonic_geometry_reverb_v1.py

SOLIDS
------
{solid_table}

DSP MODEL
---------
The engine uses twenty fixed delay nodes, enough for the dodecahedron. Every
solid is embedded into the same twenty directional sites. A geometry morph
interpolates four coordinated fields:

1. node activation
2. vertex coordinates
3. normalized adjacency / feedback topology
4. overtone-derived delay ratios

The fixed node count makes continuous transformation possible even when the
source and destination solids have different numbers of vertices.

GEN~ INPUTS
-----------
in1      mono audio
in2      XXII
in3      YYII
in4      ZZII
in5      IXXI
in6      IYYI
in7      IZZI
in8      IIXX
in9      IIYY

The eight Pauli correlations repeat across larger solids according to each
solid's spatially ordered overtone indices.

CORE PARAMETERS
---------------
solid_a 0..4
solid_b 0..4
geometry_morph 0..1
morph_slew_ms 0..5000
    Cascaded two-stage smoothing before cubic morph easing.
rotation_slew_ms 0..5000
diffusion_slew_ms 0..5000
    Smoothing time for the four-stage input allpass coefficient.

geometry_depth 0..1
    Amount by which rotated vertex projection changes delay ratios.
geometry_depth_slew_ms 0..5000
    Smoothing time for geometry-depth changes.

harmonicity 0..1
    0 = delay ratios arise from geometric projection.
    1 = delay ratios move toward the overtone ordering assigned to vertices.

harmonic_span 0..1
    Compression/expansion of the overtone-derived delay family. Start low.

pauli_depth 0..1
    Pauli deformation of each node's delay ratio.

topology 0..1
    0 = active-node Householder diffusion.
    1 = strict interpolated Platonic adjacency.

rot_x / rot_y / rot_z
    Continuous rotations in turns: 0.25 = 90 degrees.
    Rotation follows the shortest circular path using rotation_slew_ms.

STARTING VALUES
---------------
solid_a 1
solid_b 2
geometry_morph 0
morph_slew_ms 700
rotation_slew_ms 100
size 0.42
decay 0.68
diffusion 0.76
diffusion_slew_ms 100
absorb 0.30
topology 0.80
geometry_depth 0.55
geometry_depth_slew_ms 100
harmonicity 0.20
harmonic_span 0.18
pauli_depth 0.12
width 0.90
input_gain 0.20
output_gain 0.35

MAX CONTROLLER
--------------
Place beside the patch or in Max's search path:

    [js qmw_platonic_geometry_controller_v1.js]

Connect outlet 0 directly to [gen~]. Try:

    shape tetrahedron
    between cube octahedron
    morph 0.5
    transition dodecahedron icosahedron 0.25
    dual
    next
    rx 15
    rotate z 90
    harmonicity 0.45
    topology 1.

FIRST LISTENING TESTS
---------------------
A. Geometry only
   harmonicity 0; pauli_depth 0; topology 1

B. Harmonic room
   harmonicity 0.5; harmonic_span 0.2; pauli_depth 0

C. Quantum deformation
   harmonicity 0.25; pauli_depth 0.15; topology 0.8

D. Duality
   between cube octahedron, then move morph slowly from 0 to 1.
   Repeat with dodecahedron and icosahedron.

SAFETY AND PERFORMANCE
----------------------
This is a twenty-delay network with a maximum allocation of 384000 samples
per line. Begin at low monitor level. High decay, freeze, abrupt morphs, and
large harmonic_span values can generate strong resonant energy.

The generated code and geometry tables are structurally verified, but this
environment cannot compile GenExpr. Max may reveal a small version-specific
syntax adjustment on first compile.
'''


def make_design_note():
    return '''# Platonic Geometry Reverb: design proposition

This instrument treats architectural form, harmonic proportion, and quantum
relation as three distinct but interoperable organizations of resonance.

- **Architectural form** determines which delay nodes exist, how they connect,
  and where they are oriented in a virtual spherical field.
- **Harmonic proportion** moves delay times toward overtone-derived ratios, so
  the room and the resonator can partially share a numerical order.
- **Pauli correlation** deforms the delays from within, making the quantum
  relational field act upon a geometrically invariant substrate.

A morph between solids therefore transforms several linked invariants at once:
vertex count, valence, cycle structure, symmetry, graph spectrum, and spatial
projection. The transformation is audible as a change in diffusion speed,
recurrence, modal emphasis, directional spread, and decay circulation.

The dual pairs provide especially clear experiments:

- cube ↔ octahedron: vertices and faces exchange roles;
- dodecahedron ↔ icosahedron: sparse pentagonal circulation becomes dense
  triangular circulation;
- tetrahedron: self-duality, a compact topology in which every vertex is
  adjacent to every other vertex.

This is a practical realization of transformation through invariance. The
signal, decay law, and broad energy constraint may remain stable while the
relational form through which energy circulates changes continuously.
'''


def main():
    solids, canonical = build_tables()
    genexpr = make_genexpr(solids)
    controller = make_controller()
    readme = make_readme(solids)
    design = make_design_note()

    geometry_json = {
        'canonical_site': 'normalized dodecahedron vertices',
        'canonical_coordinates': canonical.tolist(),
        'solids': [],
    }
    for s in solids:
        geometry_json['solids'].append({
            'id': s['id'],
            'name': s['name'],
            'schlaefli': [s['p'], s['q']],
            'vertex_count': s['vertex_count'],
            'edge_count': s['edge_count'],
            'vertex_degree': s['degree'],
            'edge_length_on_unit_sphere': s['edge_length'],
            'spectral_radius_normalized_adjacency': s['spectral_radius'],
            'slot_to_vertex': {str(k): v for k, v in sorted(s['slot_to_vertex'].items())},
            'active_slots': [int(i) for i in np.where(s['active'] > 0.5)[0]],
            'embedded_edges': [list(edge) for edge in s['embedded_edges']],
            'harmonic_log_ratio': s['harmonic_log_ratio'].tolist(),
            'pauli_source_indices_zero_based': s['pauli_index'].tolist(),
        })

    files = {
        'qmw_platonic_geometry_reverb_v1.genexpr': genexpr,
        'qmw_platonic_geometry_controller_v1.js': controller,
        'qmw_platonic_geometry_reverb_v1_README.txt': readme,
        'qmw_platonic_geometry_reverb_v1_DESIGN.md': design,
        'qmw_platonic_geometry_reverb_v1_GEOMETRY.json': json.dumps(geometry_json, indent=2),
    }

    for name, content in files.items():
        (OUT / name).write_text(content)

    # Structural checks.
    if genexpr.count('{') != genexpr.count('}'):
        raise RuntimeError('Unbalanced braces in GenExpr')
    if controller.count('{') != controller.count('}'):
        raise RuntimeError('Unbalanced braces in JS controller')
    if genexpr.count('Delay dl') != 20:
        raise RuntimeError('Expected 20 delay lines')
    if genexpr.count('.write(') != 20:
        raise RuntimeError('Expected 20 delay writes')

    print(f'Generated {len(files)} files in {OUT}')
    print(f'GenExpr lines: {len(genexpr.splitlines())}')
    for s in solids:
        print(s['name'], s['vertex_count'], s['edge_count'], s['degree'], s['spectral_radius'])


if __name__ == '__main__':
    main()
