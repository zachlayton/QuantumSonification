QMW Platonic Geometry Reverb v1
================================

FILES
-----
qmw_platonic_geometry_reverb_v1.genexpr
qmw_platonic_geometry_controller_v1.js
qmw_platonic_geometry_reverb_v1_GEOMETRY.json
build_qmw_platonic_geometry_reverb_v1.py

SOLIDS
------
0  tetrahedron    Schlaefli={3,3} vertices= 4 edges= 6 degree=3
1  cube           Schlaefli={4,3} vertices= 8 edges=12 degree=3
2  octahedron     Schlaefli={3,4} vertices= 6 edges=12 degree=4
3  dodecahedron   Schlaefli={5,3} vertices=20 edges=30 degree=3
4  icosahedron    Schlaefli={3,5} vertices=12 edges=30 degree=5

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

geometry_depth 0..1
    Amount by which rotated vertex projection changes delay ratios.

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

STARTING VALUES
---------------
solid_a 1
solid_b 2
geometry_morph 0
morph_slew_ms 700
size 0.42
decay 0.68
diffusion 0.76
absorb 0.30
topology 0.80
geometry_depth 0.55
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
