#!/usr/bin/env python3
"""Build the real-time implicit/algebraic/minimal surface Gen~ reverb rack."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_ROOT = PROJECT_ROOT / "max"
MODULE_ROOT = MAX_ROOT / "control_room_modules"
SOURCE_GENEXPR = (
    PROJECT_ROOT
    / "qmw_platonic_geometry_reverb_noise_excitation_v1"
    / "qmw_platonic_geometry_reverb_dual_spectral_dc_safe_v1.genexpr"
)
CONTROLLER = MAX_ROOT / "qmw_implicit_surface_controller_v1.js"
OUTPUT = MODULE_ROOT / "QMW_Realtime_Surface_Reverb_v1.maxpat"
CONTROL_ROOM = MAX_ROOT / "QMW_Control_Room_v1.maxpat"


SURFACES = (
    # Platonic solids (convex implicit half-space fields).
    "tetrahedron",
    "cube",
    "octahedron",
    "dodecahedron",
    "icosahedron",
    # Algebraic surfaces.
    "sphere",
    "ellipsoid",
    "torus",
    "superellipsoid",
    "tanglecube",
    "heart",
    "roman_surface",
    "cayley",
    # Triply-periodic and classical minimal surfaces.
    "gyroid",
    "schwarz_p",
    "schwarz_d",
    "neovius",
    "lidinoid",
    "iwp",
    "fischer_koch_s",
    "catenoid",
    "helicoid",
    # User formula compiled by the Max JS controller.
    "custom",
)


def compact_surface_genexpr() -> str:
    """Return the low-memory real-time surface FDN used by the control room.

    The original twenty-delay research core is retained in SOURCE_GENEXPR, but
    proved too large to be a dependable embedded Gen~ target.  This production
    core folds all twenty field probes into eight modulated delay lines.
    """
    return r"""// qmw_compact_realtime_surface_fdn_v1.genexpr
// Eight-line geometry-modulated FDN; all twenty implicit-surface probes are used.

Param size(0.45);
Param decay(0.82);
Param diffusion(0.78);
Param absorb(0.32);
Param width(0.90);
Param freeze(0);
Param input_gain(0.65);
Param output_gain(0.72);
Param surface_depth(0.35);
Param geometry_morph(0);
Param geometry_depth(0.55);
Param harmonicity(0.25);
Param harmonic_span(0.22);
Param topology(0.80);
Param pauli_depth(0.16);
Param harmonic_resonance(0.5);
Param spectral_tilt(0);
Param modal_warp(0);
Param harmonic_slew_ms(120);
Param mw1(1); Param mw2(1); Param mw3(1); Param mw4(1);
Param mw5(1); Param mw6(1); Param mw7(1); Param mw8(1);
Param rot_x(0);
Param rot_y(0);
Param rot_z(0);
Param rotation_slew_ms(100);
Param morph_slew_ms(500);
Param geometry_morph_slew_ms(500);
Param surface_slew_ms(250);
Param diffusion_slew_ms(100);
Param geometry_depth_slew_ms(100);
Param solid_a(1);
Param solid_b(2);

Param sf1(0);  Param sf2(0);  Param sf3(0);  Param sf4(0);
Param sf5(0);  Param sf6(0);  Param sf7(0);  Param sf8(0);
Param sf9(0);  Param sf10(0); Param sf11(0); Param sf12(0);
Param sf13(0); Param sf14(0); Param sf15(0); Param sf16(0);
Param sf17(0); Param sf18(0); Param sf19(0); Param sf20(0);

Param qm0(1); Param qm1(0); Param qm2(0); Param qm3(0);
Param qm4(0); Param qm5(0); Param qm6(0); Param qm7(0);
Param qh0(1); Param qh1(2); Param qh2(3); Param qh3(4);
Param qh4(5); Param qh5(6); Param qh6(7); Param qh7(8);

Delay dl1(192000); Delay dl2(192000); Delay dl3(192000); Delay dl4(192000);
Delay dl5(192000); Delay dl6(192000); Delay dl7(192000); Delay dl8(192000);

History lp1(0); History lp2(0); History lp3(0); History lp4(0);
History lp5(0); History lp6(0); History lp7(0); History lp8(0);
History shape1_z(0); History shape2_z(0); History shape3_z(0); History shape4_z(0);
History shape5_z(0); History shape6_z(0); History shape7_z(0); History shape8_z(0);
History rot_x_z(0); History rot_y_z(0); History rot_z_z(0);
History morph_z(0); History surface_depth_z(0.35); History diffusion_z(0.78);
History resonance_z(0.5); History tilt_z(0); History warp_z(0);
History mw1_z(1); History mw2_z(1); History mw3_z(1); History mw4_z(1);
History mw5_z(1); History mw6_z(1); History mw7_z(1); History mw8_z(1);
History dc_l_x(0); History dc_l_y(0);
History dc_r_x(0); History dc_r_y(0);

sr = samplerate;
pi2 = 6.28318530718;
s = clamp(size, 0, 1);
size_scale = pow(2, (s * 3) - 1.5);
surface = clamp(surface_depth, 0, 0.85);

// Fold twenty probes into eight independent geometry lanes.
shape1_target = (sf1 + sf9 + sf17) * 0.333333333;
shape2_target = (sf2 + sf10 + sf18) * 0.333333333;
shape3_target = (sf3 + sf11 + sf19) * 0.333333333;
shape4_target = (sf4 + sf12 + sf20) * 0.333333333;
shape5_target = (sf5 + sf13) * 0.5;
shape6_target = (sf6 + sf14) * 0.5;
shape7_target = (sf7 + sf15) * 0.5;
shape8_target = (sf8 + sf16) * 0.5;

surface_seconds = max(surface_slew_ms, 0.1) * 0.001;
surface_coeff = 1 - exp(-1 / max(sr * surface_seconds, 1));
shape1_z = shape1_z + surface_coeff * (shape1_target - shape1_z);
shape2_z = shape2_z + surface_coeff * (shape2_target - shape2_z);
shape3_z = shape3_z + surface_coeff * (shape3_target - shape3_z);
shape4_z = shape4_z + surface_coeff * (shape4_target - shape4_z);
shape5_z = shape5_z + surface_coeff * (shape5_target - shape5_z);
shape6_z = shape6_z + surface_coeff * (shape6_target - shape6_z);
shape7_z = shape7_z + surface_coeff * (shape7_target - shape7_z);
shape8_z = shape8_z + surface_coeff * (shape8_target - shape8_z);

depth_seconds = max(geometry_depth_slew_ms, 0.1) * 0.001;
depth_coeff = 1 - exp(-1 / max(sr * depth_seconds, 1));
surface_depth_z = surface_depth_z + depth_coeff * (surface - surface_depth_z);

morph_seconds = max(geometry_morph_slew_ms, 0.1) * 0.001;
morph_coeff = 1 - exp(-1 / max(sr * morph_seconds, 1));
morph_z = morph_z + morph_coeff * (clamp(geometry_morph, 0, 1) - morph_z);

rotation_seconds = max(rotation_slew_ms, 0.1) * 0.001;
rotation_coeff = 1 - exp(-1 / max(sr * rotation_seconds, 1));
rot_x_delta = rot_x - rot_x_z;
rot_y_delta = rot_y - rot_y_z;
rot_z_delta = rot_z - rot_z_z;
rot_x_delta = rot_x_delta - floor(rot_x_delta + 0.5);
rot_y_delta = rot_y_delta - floor(rot_y_delta + 0.5);
rot_z_delta = rot_z_delta - floor(rot_z_delta + 0.5);
rot_x_z = rot_x_z + rotation_coeff * rot_x_delta;
rot_y_z = rot_y_z + rotation_coeff * rot_y_delta;
rot_z_z = rot_z_z + rotation_coeff * rot_z_delta;

harmonic_seconds = max(harmonic_slew_ms, 0.1) * 0.001;
harmonic_coeff = 1 - exp(-1 / max(sr * harmonic_seconds, 1));
resonance_z = resonance_z + harmonic_coeff * (clamp(harmonic_resonance, 0, 1) - resonance_z);
tilt_z = tilt_z + harmonic_coeff * (clamp(spectral_tilt, -1, 1) - tilt_z);
warp_z = warp_z + harmonic_coeff * (clamp(modal_warp, -1, 1) - warp_z);
mw1_z = mw1_z + harmonic_coeff * (clamp(mw1, 0.35, 1.65) - mw1_z);
mw2_z = mw2_z + harmonic_coeff * (clamp(mw2, 0.35, 1.65) - mw2_z);
mw3_z = mw3_z + harmonic_coeff * (clamp(mw3, 0.35, 1.65) - mw3_z);
mw4_z = mw4_z + harmonic_coeff * (clamp(mw4, 0.35, 1.65) - mw4_z);
mw5_z = mw5_z + harmonic_coeff * (clamp(mw5, 0.35, 1.65) - mw5_z);
mw6_z = mw6_z + harmonic_coeff * (clamp(mw6, 0.35, 1.65) - mw6_z);
mw7_z = mw7_z + harmonic_coeff * (clamp(mw7, 0.35, 1.65) - mw7_z);
mw8_z = mw8_z + harmonic_coeff * (clamp(mw8, 0.35, 1.65) - mw8_z);

rx_angle = rot_x_z * pi2;
ry_angle = rot_y_z * pi2;
rz_angle = rot_z_z * pi2;
rxs = sin(rx_angle); rxc = cos(rx_angle);
rys = sin(ry_angle); ryc = cos(ry_angle);
rzs = sin(rz_angle); rzc = cos(rz_angle);

// Rotation changes the delay geometry itself, not just the final stereo pan.
// The larger coefficients make XYZ/Bloch motion clearly audible.
rot1 =  0.62 * rxs + 0.31 * rys + 0.18 * rzs;
rot2 = -0.48 * rxs + 0.46 * rys - 0.27 * rzs;
rot3 =  0.35 * rxs - 0.58 * rys + 0.39 * rzs;
rot4 = -0.57 * rxs - 0.29 * rys - 0.36 * rzs;
rot5 =  0.44 * rxc + 0.36 * rys - 0.31 * rzs;
rot6 = -0.38 * rxs + 0.51 * ryc + 0.28 * rzs;
rot7 =  0.29 * rxs - 0.41 * rys + 0.52 * rzc;
rot8 = -0.53 * rxc - 0.34 * ryc - 0.26 * rzs;
shape1 = shape1_z; shape2 = shape2_z; shape3 = shape3_z; shape4 = shape4_z;
shape5 = shape5_z; shape6 = shape6_z; shape7 = shape7_z; shape8 = shape8_z;
// Fixed asymmetric terms keep deformation audible even for a perfectly
// symmetric field such as a sphere sampled on a spherical probe shell.
deform_amount = (0.04 + 1.28 * surface_depth_z) * (0.88 + 0.24 * morph_z);
geom1 = 0.88 * shape1 + 0.48 * rot1 - 0.42;
geom2 = 0.88 * shape2 + 0.48 * rot2 + 0.36;
geom3 = 0.88 * shape3 + 0.48 * rot3 - 0.28;
geom4 = 0.88 * shape4 + 0.48 * rot4 + 0.46;
geom5 = 0.88 * shape5 + 0.48 * rot5 - 0.22;
geom6 = 0.88 * shape6 + 0.48 * rot6 + 0.31;
geom7 = 0.88 * shape7 + 0.48 * rot7 - 0.49;
geom8 = 0.88 * shape8 + 0.48 * rot8 + 0.27;

d1 = clamp(31 * size_scale * exp(deform_amount * geom1 - 0.18 * warp_z) * sr * 0.001, 16, 191999);
d2 = clamp(37 * size_scale * exp(deform_amount * geom2 + 0.14 * warp_z) * sr * 0.001, 16, 191999);
d3 = clamp(43 * size_scale * exp(deform_amount * geom3 - 0.10 * warp_z) * sr * 0.001, 16, 191999);
d4 = clamp(47 * size_scale * exp(deform_amount * geom4 + 0.07 * warp_z) * sr * 0.001, 16, 191999);
d5 = clamp(53 * size_scale * exp(deform_amount * geom5 - 0.05 * warp_z) * sr * 0.001, 16, 191999);
d6 = clamp(59 * size_scale * exp(deform_amount * geom6 + 0.09 * warp_z) * sr * 0.001, 16, 191999);
d7 = clamp(67 * size_scale * exp(deform_amount * geom7 - 0.13 * warp_z) * sr * 0.001, 16, 191999);
d8 = clamp(73 * size_scale * exp(deform_amount * geom8 + 0.17 * warp_z) * sr * 0.001, 16, 191999);

r1 = dl1.read(d1); r2 = dl2.read(d2); r3 = dl3.read(d3); r4 = dl4.read(d4);
r5 = dl5.read(d5); r6 = dl6.read(d6); r7 = dl7.read(d7); r8 = dl8.read(d8);

shape_activity = (
    abs(shape1) + abs(shape2) + abs(shape3) + abs(shape4)
    + abs(shape5) + abs(shape6) + abs(shape7) + abs(shape8)
) * 0.125;
effective_absorb = clamp(
    absorb + surface_depth_z * (0.14 + 0.18 * shape_activity),
    0,
    0.94
);
ea1 = clamp(effective_absorb - 0.16 * tilt_z, 0, 0.96);
ea2 = clamp(effective_absorb - 0.11 * tilt_z, 0, 0.96);
ea3 = clamp(effective_absorb - 0.06 * tilt_z, 0, 0.96);
ea4 = clamp(effective_absorb - 0.02 * tilt_z, 0, 0.96);
ea5 = clamp(effective_absorb + 0.02 * tilt_z, 0, 0.96);
ea6 = clamp(effective_absorb + 0.06 * tilt_z, 0, 0.96);
ea7 = clamp(effective_absorb + 0.11 * tilt_z, 0, 0.96);
ea8 = clamp(effective_absorb + 0.16 * tilt_z, 0, 0.96);
cut1 = clamp(0.025 + (1 - ea1) * 0.42, 0.02, 0.46);
cut2 = clamp(0.025 + (1 - ea2) * 0.42, 0.02, 0.46);
cut3 = clamp(0.025 + (1 - ea3) * 0.42, 0.02, 0.46);
cut4 = clamp(0.025 + (1 - ea4) * 0.42, 0.02, 0.46);
cut5 = clamp(0.025 + (1 - ea5) * 0.42, 0.02, 0.46);
cut6 = clamp(0.025 + (1 - ea6) * 0.42, 0.02, 0.46);
cut7 = clamp(0.025 + (1 - ea7) * 0.42, 0.02, 0.46);
cut8 = clamp(0.025 + (1 - ea8) * 0.42, 0.02, 0.46);
lp1 = lp1 + cut1 * (r1 - lp1); lp2 = lp2 + cut2 * (r2 - lp2);
lp3 = lp3 + cut3 * (r3 - lp3); lp4 = lp4 + cut4 * (r4 - lp4);
lp5 = lp5 + cut5 * (r5 - lp5); lp6 = lp6 + cut6 * (r6 - lp6);
lp7 = lp7 + cut7 * (r7 - lp7); lp8 = lp8 + cut8 * (r8 - lp8);

f1 = mix(r1, lp1, ea1); f2 = mix(r2, lp2, ea2);
f3 = mix(r3, lp3, ea3); f4 = mix(r4, lp4, ea4);
f5 = mix(r5, lp5, ea5); f6 = mix(r6, lp6, ea6);
f7 = mix(r7, lp7, ea7); f8 = mix(r8, lp8, ea8);

// Normalized eight-point Hadamard diffusion matrix.
hn = 0.353553391;
h1 = ( f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8) * hn;
h2 = ( f1 - f2 + f3 - f4 + f5 - f6 + f7 - f8) * hn;
h3 = ( f1 + f2 - f3 - f4 + f5 + f6 - f7 - f8) * hn;
h4 = ( f1 - f2 - f3 + f4 + f5 - f6 - f7 + f8) * hn;
h5 = ( f1 + f2 + f3 + f4 - f5 - f6 - f7 - f8) * hn;
h6 = ( f1 - f2 + f3 - f4 - f5 + f6 - f7 + f8) * hn;
h7 = ( f1 + f2 - f3 - f4 - f5 - f6 + f7 + f8) * hn;
h8 = ( f1 - f2 - f3 + f4 - f5 + f6 + f7 - f8) * hn;

diffusion_seconds = max(diffusion_slew_ms, 0.1) * 0.001;
diffusion_coeff = 1 - exp(-1 / max(sr * diffusion_seconds, 1));
diffusion_z = diffusion_z + diffusion_coeff * (clamp(diffusion, 0, 1) - diffusion_z);
diff_amount = diffusion_z;
n1 = mix(f1, h1, diff_amount); n2 = mix(f2, h2, diff_amount);
n3 = mix(f3, h3, diff_amount); n4 = mix(f4, h4, diff_amount);
n5 = mix(f5, h5, diff_amount); n6 = mix(f6, h6, diff_amount);
n7 = mix(f7, h7, diff_amount); n8 = mix(f8, h8, diff_amount);

fr = clamp(freeze, 0, 1);
effective_decay = clamp(
    decay + 0.10 * surface_depth_z - 0.06 * shape_activity,
    0,
    1
);
feedback = mix(0.48 + 0.49 * effective_decay, 0.999, fr);
excite = in1 * input_gain * (1 - fr) * 0.42;
rg1 = clamp(feedback + 0.045 * resonance_z * (mw1_z - 1), 0, 0.9985);
rg2 = clamp(feedback + 0.045 * resonance_z * (mw2_z - 1), 0, 0.9985);
rg3 = clamp(feedback + 0.045 * resonance_z * (mw3_z - 1), 0, 0.9985);
rg4 = clamp(feedback + 0.045 * resonance_z * (mw4_z - 1), 0, 0.9985);
rg5 = clamp(feedback + 0.045 * resonance_z * (mw5_z - 1), 0, 0.9985);
rg6 = clamp(feedback + 0.045 * resonance_z * (mw6_z - 1), 0, 0.9985);
rg7 = clamp(feedback + 0.045 * resonance_z * (mw7_z - 1), 0, 0.9985);
rg8 = clamp(feedback + 0.045 * resonance_z * (mw8_z - 1), 0, 0.9985);
dl1.write(tanh( excite * mw1_z + rg1 * n1));
dl2.write(tanh(-excite * mw2_z + rg2 * n2));
dl3.write(tanh( excite * mw3_z + rg3 * n3));
dl4.write(tanh(-excite * mw4_z + rg4 * n4));
dl5.write(tanh(-excite * mw5_z + rg5 * n5));
dl6.write(tanh( excite * mw6_z + rg6 * n6));
dl7.write(tanh(-excite * mw7_z + rg7 * n7));
dl8.write(tanh( excite * mw8_z + rg8 * n8));

spread = clamp(width, 0, 1);
decoder_a_l = f1 + f3 + f6 + f8 + spread * (f2 - f5);
decoder_a_r = f2 + f4 + f5 + f7 + spread * (f3 - f6);
decoder_b_l = f2 + f3 + f5 + f8 + spread * (f1 - f7);
decoder_b_r = f1 + f4 + f6 + f7 + spread * (f5 - f2);
decoder_c_l = f1 + f2 + f7 + f8 + spread * (f3 - f6);
decoder_c_r = f3 + f4 + f5 + f6 + spread * (f8 - f1);
x_mix = clamp(0.5 + 0.5 * rxs + 0.22 * surface_depth_z * shape1, 0, 1);
y_mix = clamp(0.5 + 0.5 * rys + 0.22 * surface_depth_z * shape5, 0, 1);
decoder_x_l = mix(decoder_a_l, decoder_b_l, x_mix);
decoder_x_r = mix(decoder_a_r, decoder_b_r, x_mix);
decoder_y_l = mix(decoder_x_l, decoder_c_l, y_mix);
decoder_y_r = mix(decoder_x_r, decoder_c_r, y_mix);
left_raw = (rzc * decoder_y_l - rzs * decoder_y_r) * output_gain * 0.24;
right_raw = (rzs * decoder_y_l + rzc * decoder_y_r) * output_gain * 0.24;

dc = exp((-pi2 * 18) / sr);
left = left_raw - dc_l_x + dc * dc_l_y;
right = right_raw - dc_r_x + dc * dc_r_y;
dc_l_x = left_raw; dc_l_y = left;
dc_r_x = right_raw; dc_r_y = right;

out1 = left;
out2 = right;
"""


def extend_genexpr(source: str) -> str:
    """Add twenty smoothed implicit-field probes to the Platonic FDN."""
    parameter_anchor = "Param output_gain(0.40);"
    input_gain_anchor = "Param input_gain(0.25);"
    history_anchor = "History diffusion_z(0.72);"
    runtime_anchor = "sr = samplerate;\npi2 = 6.28318530718;"
    if source.count(parameter_anchor) != 1:
        raise RuntimeError("Platonic GenExpr output-gain anchor changed")
    if source.count(input_gain_anchor) != 1:
        raise RuntimeError("Platonic GenExpr input-gain anchor changed")
    if source.count(history_anchor) != 1:
        raise RuntimeError("Platonic GenExpr history anchor changed")
    if source.count(runtime_anchor) != 1:
        raise RuntimeError("Platonic GenExpr runtime anchor changed")

    probe_params = "\n".join(f"Param sf{index}(0);" for index in range(1, 21))
    probe_histories = "\n".join(
        f"History surface_z{index}(0);" for index in range(1, 21)
    )
    probe_smoothing = "\n".join(
        f"surface_z{index} = surface_z{index} + surface_coeff * "
        f"(clamp(sf{index}, -1, 1) - surface_z{index});"
        for index in range(1, 21)
    )

    source = source.replace(
        parameter_anchor,
        "Param output_gain(0.65);"
        + "\n\n// Live algebraic/minimal-surface probe field."
        + "\nParam surface_depth(0.35);"
        + "\nParam surface_slew_ms(250);\n"
        + probe_params,
    )
    source = source.replace(input_gain_anchor, "Param input_gain(0.55);")
    source = source.replace(
        history_anchor,
        history_anchor + "\n" + probe_histories,
    )
    source = source.replace(
        runtime_anchor,
        runtime_anchor
        + "\n\n// Smooth control-rate implicit-field probes before delay modulation."
        + "\nsurface_seconds = max(surface_slew_ms, 0.1) * 0.001;"
        + "\nsurface_coeff = 1 - exp(-1 / max(sr * surface_seconds, 1));\n"
        + probe_smoothing,
    )

    for index in range(1, 21):
        anchor = f"pdepth * pv{index};"
        replacement = (
            f"pdepth * pv{index} + clamp(surface_depth, 0, 0.85) "
            f"* surface_z{index};"
        )
        if source.count(anchor) != 1:
            raise RuntimeError(f"Platonic GenExpr node {index} anchor changed")
        source = source.replace(anchor, replacement)

    required = (
        "Param sf1(0);",
        "Param sf20(0);",
        "History surface_z20(0);",
        "surface_depth",
        "surface_slew_ms",
        "out1 = output_left_dc;",
        "out2 = output_right_dc;",
    )
    if not all(token in source for token in required):
        raise RuntimeError("Extended implicit-surface GenExpr is incomplete")
    return source


class PatchBuilder:
    def __init__(self) -> None:
        self.boxes: list[dict[str, Any]] = []
        self.lines: list[dict[str, Any]] = []
        self.counter = 0

    def add(
        self,
        maxclass: str,
        rect: list[float],
        *,
        text: str | None = None,
        presentation: bool = False,
        presentation_rect: list[float] | None = None,
        **properties: Any,
    ) -> str:
        self.counter += 1
        identifier = f"obj-{self.counter}"
        box: dict[str, Any] = {
            "id": identifier,
            "maxclass": maxclass,
            "patching_rect": rect,
        }
        if text is not None:
            box["text"] = text
        if presentation:
            box["presentation"] = 1
            box["presentation_rect"] = presentation_rect or list(rect)
        box.update(properties)
        self.boxes.append({"box": box})
        return identifier

    def connect(
        self,
        source: str,
        outlet: int,
        destination: str,
        inlet: int = 0,
        *,
        order: int | None = None,
    ) -> None:
        line: dict[str, Any] = {
            "source": [source, outlet],
            "destination": [destination, inlet],
        }
        if order is not None:
            line["order"] = order
        self.lines.append({"patchline": line})


def menu_items() -> list[str]:
    values: list[str] = []
    for index, name in enumerate(SURFACES):
        if index:
            values.append(",")
        values.append(name)
    return values


def build_patch() -> dict[str, Any]:
    code = compact_surface_genexpr()
    builder = PatchBuilder()

    builder.add(
        "panel",
        [10.0, 10.0, 760.0, 490.0],
        presentation=True,
        background=1,
        bgcolor=[0.055, 0.095, 0.095, 1.0],
        border=1,
        rounded=12,
    )
    builder.add(
        "comment",
        [28.0, 22.0, 620.0, 28.0],
        text="QMW REALTIME IMPLICIT SURFACE REVERB v1",
        presentation=True,
        fontsize=18.0,
        fontface=1,
        textcolor=[0.72, 0.95, 0.90, 1.0],
    )
    builder.add(
        "comment",
        [28.0, 52.0, 700.0, 20.0],
        text="20 field probes → compact 8-line Gen~ FDN · no mesh, WAV render, or IR reload",
        presentation=True,
        fontsize=11.0,
        textcolor=[0.55, 0.76, 0.72, 1.0],
    )

    controller = builder.add(
        "newobj",
        [820.0, 210.0, 222.0, 22.0],
        text="js qmw_implicit_surface_controller_v1.js",
        numinlets=1,
        numoutlets=2,
        outlettype=["", ""],
    )
    codebox = builder.add(
        "gen.codebox~",
        [1090.0, 330.0, 310.0, 48.0],
        code=code,
        fontname="<Monospaced>",
        fontsize=10.0,
        numinlets=9,
        numoutlets=2,
        outlettype=["signal", "signal"],
    )
    builder.connect(controller, 0, codebox)

    menu_a = builder.add(
        "umenu",
        [38.0, 105.0, 150.0, 22.0],
        presentation=True,
        items=menu_items(),
        numinlets=1,
        numoutlets=3,
        outlettype=["int", "", ""],
        parameter_enable=0,
    )
    menu_b = builder.add(
        "umenu",
        [218.0, 105.0, 150.0, 22.0],
        presentation=True,
        items=menu_items(),
        numinlets=1,
        numoutlets=3,
        outlettype=["int", "", ""],
        parameter_enable=0,
    )
    builder.add("comment", [38.0, 82.0, 150.0, 18.0], text="SURFACE A", presentation=True, fontface=1)
    builder.add("comment", [218.0, 82.0, 150.0, 18.0], text="SURFACE B", presentation=True, fontface=1)
    prepend_a = builder.add("newobj", [820.0, 88.0, 68.0, 22.0], text="prepend a")
    prepend_b = builder.add("newobj", [900.0, 88.0, 68.0, 22.0], text="prepend b")
    builder.connect(menu_a, 1, prepend_a)
    builder.connect(menu_b, 1, prepend_b)
    builder.connect(prepend_a, 0, controller)
    builder.connect(prepend_b, 0, controller)
    load_a = builder.add(
        "newobj", [820.0, 50.0, 72.0, 22.0],
        text=f"loadmess {SURFACES.index('sphere')}",
    )
    load_b = builder.add(
        "newobj", [900.0, 50.0, 72.0, 22.0],
        text=f"loadmess {SURFACES.index('gyroid')}",
    )
    builder.connect(load_a, 0, menu_a)
    builder.connect(load_b, 0, menu_b)

    morph_slider = builder.add(
        "slider",
        [38.0, 166.0, 330.0, 24.0],
        presentation=True,
        size=1001,
        floatoutput=0,
        parameter_enable=0,
    )
    builder.add("comment", [38.0, 142.0, 150.0, 18.0], text="EQUATION MORPH", presentation=True, fontface=1)
    morph_scale = builder.add("newobj", [820.0, 126.0, 58.0, 22.0], text="/ 1000.")
    morph_prepend = builder.add("newobj", [890.0, 126.0, 92.0, 22.0], text="prepend morph")
    builder.connect(morph_slider, 0, morph_scale)
    builder.connect(morph_scale, 0, morph_prepend)
    builder.connect(morph_prepend, 0, controller)
    builder.connect(load_a, 0, morph_slider)

    deform_slider = builder.add(
        "slider",
        [398.0, 166.0, 210.0, 24.0],
        presentation=True,
        size=851,
        floatoutput=0,
        parameter_enable=0,
    )
    builder.add("comment", [398.0, 142.0, 150.0, 18.0], text="FIELD DEFORMATION", presentation=True, fontface=1)
    deform_scale = builder.add("newobj", [820.0, 164.0, 58.0, 22.0], text="/ 1000.")
    deform_prepend = builder.add("newobj", [890.0, 164.0, 96.0, 22.0], text="prepend deform")
    deform_load = builder.add("newobj", [990.0, 50.0, 86.0, 22.0], text="loadmess 350")
    builder.connect(deform_load, 0, deform_slider)
    builder.connect(deform_slider, 0, deform_scale)
    builder.connect(deform_scale, 0, deform_prepend)
    builder.connect(deform_prepend, 0, controller)

    animate = builder.add(
        "toggle",
        [638.0, 165.0, 25.0, 25.0],
        presentation=True,
        parameter_enable=0,
    )
    builder.add("comment", [670.0, 168.0, 70.0, 18.0], text="ANIMATE", presentation=True, fontface=1)
    emergent_toggle = builder.add(
        "toggle",
        [638.0, 104.0, 25.0, 25.0],
        presentation=True,
        parameter_enable=0,
    )
    builder.add("comment", [670.0, 107.0, 76.0, 18.0], text="MLX LINK", presentation=True, fontface=1)
    emergent_enable = builder.add(
        "newobj",
        [1095.0, 88.0, 145.0, 22.0],
        text="prepend emergent_enable",
    )
    builder.connect(emergent_toggle, 0, emergent_enable)
    builder.connect(emergent_enable, 0, controller)
    metro = builder.add("newobj", [820.0, 250.0, 62.0, 22.0], text="metro 50")
    counter = builder.add("newobj", [895.0, 250.0, 94.0, 22.0], text="counter 0 999")
    phase_scale = builder.add("newobj", [1000.0, 250.0, 82.0, 22.0], text="* 0.006283185")
    phase_prepend = builder.add("newobj", [1095.0, 250.0, 92.0, 22.0], text="prepend phase")
    builder.connect(animate, 0, metro)
    builder.connect(metro, 0, counter)
    builder.connect(counter, 0, phase_scale)
    builder.connect(phase_scale, 0, phase_prepend)
    builder.connect(phase_prepend, 0, controller)

    status = builder.add(
        "message",
        [38.0, 215.0, 702.0, 44.0],
        text="surface sphere gyroid 0. deform 0.35",
        presentation=True,
        linecount=2,
    )
    # The controller emits a complete `set ...` list from outlet 1.  Connecting
    # it directly avoids status text getting stranded behind an extra prepend.
    builder.connect(controller, 1, status)

    # A small, presentation-mode formula editor.  The JS controller compiles
    # this into a restricted expression tree (never eval), then the CUSTOM menu
    # entry can be used on either side of the equation morph.
    builder.add(
        "comment",
        [38.0, 446.0, 112.0, 18.0],
        text="CUSTOM f(x,y,z)",
        presentation=True,
        fontface=1,
        fontsize=9.0,
    )
    expression_editor = builder.add(
        "textedit",
        [150.0, 442.0, 405.0, 24.0],
        presentation=True,
        text="(1+0.5*deform)*x*x + (1-0.3*deform)*y*y + z*z - 0.72",
        keymode=1,
        lines=1,
        wordwrap=0,
        parameter_enable=0,
        numinlets=1,
        numoutlets=4,
        outlettype=["", "int", "", ""],
    )
    expression_apply = builder.add(
        "button",
        [565.0, 442.0, 24.0, 24.0],
        presentation=True,
        parameter_enable=0,
    )
    builder.add(
        "comment",
        [594.0, 446.0, 42.0, 18.0],
        text="APPLY",
        presentation=True,
        fontface=1,
        fontsize=8.0,
    )
    expression_route = builder.add(
        "newobj", [1185.0, 210.0, 65.0, 22.0], text="route text"
    )
    expression_prepend = builder.add(
        "newobj", [1265.0, 210.0, 82.0, 22.0], text="prepend expr"
    )
    builder.connect(expression_apply, 0, expression_editor)
    builder.connect(expression_editor, 0, expression_route)
    builder.connect(expression_route, 0, expression_prepend)
    builder.connect(expression_prepend, 0, controller)

    receive_l = builder.add("newobj", [820.0, 330.0, 152.0, 22.0], text="receive~ qmw_spectral_L")
    receive_r = builder.add("newobj", [820.0, 366.0, 152.0, 22.0], text="receive~ qmw_spectral_R")
    excite_l = builder.add("newobj", [990.0, 330.0, 58.0, 22.0], text="*~ 0.625")
    excite_r = builder.add("newobj", [990.0, 366.0, 58.0, 22.0], text="*~ 0.375")
    sum_input = builder.add("newobj", [1060.0, 346.0, 32.0, 22.0], text="+~")
    # The unequal stereo fold-down prevents anti-phase L/R material from
    # cancelling completely before it reaches the mono Gen~ excitation inlet.
    builder.connect(receive_l, 0, excite_l)
    builder.connect(receive_r, 0, excite_r)
    builder.connect(excite_l, 0, sum_input, 0)
    builder.connect(excite_r, 0, sum_input, 1)
    builder.connect(sum_input, 0, codebox, 0)

    input_meter_l = builder.add("meter~", [40.0, 302.0, 280.0, 16.0], presentation=True, numinlets=1, numoutlets=1, outlettype=["float"])
    input_meter_r = builder.add("meter~", [40.0, 326.0, 280.0, 16.0], presentation=True, numinlets=1, numoutlets=1, outlettype=["float"])
    builder.add("comment", [330.0, 302.0, 90.0, 18.0], text="INPUT L", presentation=True)
    builder.add("comment", [330.0, 326.0, 90.0, 18.0], text="INPUT R", presentation=True)
    builder.connect(receive_l, 0, input_meter_l)
    builder.connect(receive_r, 0, input_meter_r)

    # Reverb gain precedes the master dry/wet crossfade, so the user can set
    # effect return level independently from the dry/wet balance.
    reverb_level_l = builder.add("newobj", [1370.0, 310.0, 32.0, 22.0], text="*~")
    reverb_level_r = builder.add("newobj", [1370.0, 346.0, 32.0, 22.0], text="*~")
    wet_l = builder.add("newobj", [1420.0, 310.0, 32.0, 22.0], text="*~")
    wet_r = builder.add("newobj", [1420.0, 346.0, 32.0, 22.0], text="*~")
    dry_l = builder.add("newobj", [1310.0, 390.0, 32.0, 22.0], text="*~")
    dry_r = builder.add("newobj", [1310.0, 426.0, 32.0, 22.0], text="*~")
    mix_l = builder.add("newobj", [1490.0, 330.0, 32.0, 22.0], text="+~")
    mix_r = builder.add("newobj", [1490.0, 366.0, 32.0, 22.0], text="+~")
    clip_l = builder.add("newobj", [1540.0, 330.0, 88.0, 22.0], text="clip~ -0.98 0.98")
    clip_r = builder.add("newobj", [1540.0, 366.0, 88.0, 22.0], text="clip~ -0.98 0.98")
    builder.connect(codebox, 0, reverb_level_l)
    builder.connect(codebox, 1, reverb_level_r)
    builder.connect(reverb_level_l, 0, wet_l)
    builder.connect(reverb_level_r, 0, wet_r)
    builder.connect(receive_l, 0, dry_l)
    builder.connect(receive_r, 0, dry_r)
    builder.connect(wet_l, 0, mix_l, 0)
    builder.connect(wet_r, 0, mix_r, 0)
    builder.connect(dry_l, 0, mix_l, 1)
    builder.connect(dry_r, 0, mix_r, 1)
    builder.connect(mix_l, 0, clip_l)
    builder.connect(mix_r, 0, clip_r)

    dry_wet_slider = builder.add(
        "slider",
        [38.0, 270.0, 210.0, 20.0],
        presentation=True,
        size=1001,
        floatoutput=0,
        parameter_enable=0,
    )
    builder.add(
        "comment",
        [38.0, 247.0, 210.0, 18.0],
        text="MASTER DRY / WET",
        presentation=True,
        fontface=1,
    )
    dry_wet_scale = builder.add("newobj", [1310.0, 470.0, 58.0, 22.0], text="/ 1000.")
    dry_wet_trigger = builder.add("newobj", [1380.0, 470.0, 42.0, 22.0], text="t f f")
    wet_ramp_message = builder.add("message", [1435.0, 455.0, 55.0, 22.0], text="$1 30")
    wet_ramp = builder.add("newobj", [1500.0, 455.0, 42.0, 22.0], text="line~")
    dry_complement = builder.add("newobj", [1435.0, 490.0, 42.0, 22.0], text="!- 1.")
    dry_ramp_message = builder.add("message", [1490.0, 490.0, 55.0, 22.0], text="$1 30")
    dry_ramp = builder.add("newobj", [1555.0, 490.0, 42.0, 22.0], text="line~")
    dry_wet_load = builder.add("newobj", [1240.0, 470.0, 66.0, 22.0], text="loadmess 650")
    builder.connect(dry_wet_load, 0, dry_wet_slider)
    builder.connect(dry_wet_slider, 0, dry_wet_scale)
    builder.connect(dry_wet_scale, 0, dry_wet_trigger)
    builder.connect(dry_wet_trigger, 0, wet_ramp_message)
    builder.connect(dry_wet_trigger, 1, dry_complement)
    builder.connect(wet_ramp_message, 0, wet_ramp)
    builder.connect(dry_complement, 0, dry_ramp_message)
    builder.connect(dry_ramp_message, 0, dry_ramp)
    builder.connect(wet_ramp, 0, wet_l, 1)
    builder.connect(wet_ramp, 0, wet_r, 1)
    builder.connect(dry_ramp, 0, dry_l, 1)
    builder.connect(dry_ramp, 0, dry_r, 1)

    reverb_gain_slider = builder.add(
        "slider",
        [268.0, 270.0, 100.0, 20.0],
        presentation=True,
        size=1001,
        floatoutput=0,
        parameter_enable=0,
    )
    builder.add(
        "comment",
        [268.0, 247.0, 125.0, 18.0],
        text="REVERB GAIN 0–4x",
        presentation=True,
        fontface=1,
        fontsize=9.0,
    )
    reverb_gain_scale = builder.add("newobj", [1240.0, 520.0, 50.0, 22.0], text="/ 250.")
    reverb_gain_message = builder.add("message", [1300.0, 520.0, 55.0, 22.0], text="$1 30")
    reverb_gain_ramp = builder.add("newobj", [1365.0, 520.0, 42.0, 22.0], text="line~")
    reverb_gain_load = builder.add("newobj", [1160.0, 520.0, 72.0, 22.0], text="loadmess 375")
    builder.connect(reverb_gain_load, 0, reverb_gain_slider)
    builder.connect(reverb_gain_slider, 0, reverb_gain_scale)
    builder.connect(reverb_gain_scale, 0, reverb_gain_message)
    builder.connect(reverb_gain_message, 0, reverb_gain_ramp)
    builder.connect(reverb_gain_ramp, 0, reverb_level_l, 1)
    builder.connect(reverb_gain_ramp, 0, reverb_level_r, 1)

    size_slider = builder.add(
        "slider",
        [398.0, 270.0, 210.0, 20.0],
        presentation=True,
        size=1001,
        floatoutput=0,
        parameter_enable=0,
    )
    builder.add(
        "comment",
        [398.0, 247.0, 150.0, 18.0],
        text="SIZE",
        presentation=True,
        fontface=1,
    )
    size_scale = builder.add("newobj", [1095.0, 290.0, 58.0, 22.0], text="/ 1000.")
    size_prepend = builder.add("newobj", [1165.0, 290.0, 80.0, 22.0], text="prepend size")
    size_load = builder.add("newobj", [1015.0, 290.0, 72.0, 22.0], text="loadmess 450")
    builder.connect(size_load, 0, size_slider)
    builder.connect(size_slider, 0, size_scale)
    builder.connect(size_scale, 0, size_prepend)
    builder.connect(size_prepend, 0, codebox)

    # Manual XYZ rotation controls.  Values are cycles (0..1), matching the
    # original Platonic patch while remaining easy to map from normalized OSC.
    rotation_source = builder.add(
        "toggle",
        [638.0, 265.0, 25.0, 25.0],
        presentation=True,
        parameter_enable=0,
    )
    builder.add(
        "comment",
        [670.0, 268.0, 80.0, 18.0],
        text="BLOCH XYZ",
        presentation=True,
        fontface=1,
        fontsize=9.0,
    )
    source_load = builder.add("newobj", [930.0, 650.0, 68.0, 22.0], text="loadmess 0")
    source_trigger = builder.add("newobj", [1010.0, 650.0, 42.0, 22.0], text="t b i")
    source_index = builder.add("newobj", [1065.0, 650.0, 32.0, 22.0], text="+ 1")
    builder.connect(source_load, 0, rotation_source)
    builder.connect(rotation_source, 0, source_trigger)
    builder.connect(source_trigger, 1, source_index)

    manual_rotation_values: list[str] = []
    bloch_rotation_values: list[str] = []
    rotation_selectors: list[str] = []
    for index, axis in enumerate(("x", "y", "z")):
        x_position = 38.0 + index * 200.0
        rotation_slider = builder.add(
            "slider",
            [x_position, 418.0, 170.0, 18.0],
            presentation=True,
            size=1001,
            floatoutput=0,
            parameter_enable=0,
        )
        builder.add(
            "comment",
            [x_position, 395.0, 105.0, 18.0],
            text=f"ROTATE {axis.upper()}",
            presentation=True,
            fontface=1,
            fontsize=9.0,
        )
        manual_scale = builder.add(
            "newobj", [820.0 + index * 90.0, 690.0, 58.0, 22.0], text="/ 1000."
        )
        manual_value = builder.add(
            "newobj", [820.0 + index * 90.0, 725.0, 42.0, 22.0], text="f 0."
        )
        bloch_value = builder.add(
            "newobj", [1120.0 + index * 90.0, 725.0, 50.0, 22.0], text="f 0."
        )
        selector = builder.add(
            "newobj", [1120.0 + index * 100.0, 770.0, 62.0, 22.0], text="switch 2"
        )
        rotation_prepend = builder.add(
            "newobj",
            [1120.0 + index * 100.0, 805.0, 88.0, 22.0],
            text=f"prepend rot_{axis}",
        )
        manual_load = builder.add(
            "newobj", [820.0 + index * 90.0, 650.0, 72.0, 22.0], text="loadmess 0"
        )
        builder.connect(manual_load, 0, rotation_slider)
        builder.connect(rotation_slider, 0, manual_scale)
        builder.connect(manual_scale, 0, manual_value)
        builder.connect(manual_value, 0, selector, 1)
        builder.connect(bloch_value, 0, selector, 2)
        builder.connect(source_index, 0, selector, 0)
        builder.connect(source_trigger, 0, manual_value, 0)
        builder.connect(source_trigger, 0, bloch_value, 0)
        builder.connect(selector, 0, rotation_prepend)
        builder.connect(rotation_prepend, 0, codebox)
        manual_rotation_values.append(manual_value)
        bloch_rotation_values.append(bloch_value)
        rotation_selectors.append(selector)

    # Slew times remain explicit messages to Gen~, so manual, Bloch, and future
    # sources share exactly the same smoothing behavior.
    slew_specs = (
        ("ROT SLEW", "rotation_slew_ms", 100, 398.0),
        ("MORPH SLEW", "geometry_morph_slew_ms", 500, 478.0),
        ("SURF SLEW", "surface_slew_ms", 250, 558.0),
    )
    slew_controls: dict[str, str] = {}
    for label, parameter, default, x_position in slew_specs:
        number = builder.add(
            "flonum",
            [x_position, 105.0, 70.0, 22.0],
            presentation=True,
            minimum=0.0,
            maximum=5000.0,
            parameter_enable=0,
            numinlets=1,
            numoutlets=2,
            outlettype=["", "bang"],
        )
        builder.add(
            "comment",
            [x_position, 82.0, 76.0, 18.0],
            text=label,
            presentation=True,
            fontface=1,
            fontsize=8.0,
        )
        prepend = builder.add(
            "newobj", [1420.0, 650.0 + len(slew_controls) * 35.0, 160.0, 22.0],
            text=f"prepend {parameter}",
        )
        load = builder.add(
            "newobj", [1335.0, 650.0 + len(slew_controls) * 35.0, 78.0, 22.0],
            text=f"loadmess {default}",
        )
        builder.connect(load, 0, number)
        builder.connect(number, 0, prepend)
        builder.connect(prepend, 0, codebox)
        slew_controls[parameter] = number

    wet_meter_l = builder.add("meter~", [440.0, 354.0, 190.0, 12.0], presentation=True, numinlets=1, numoutlets=1, outlettype=["float"])
    wet_meter_r = builder.add("meter~", [440.0, 374.0, 190.0, 12.0], presentation=True, numinlets=1, numoutlets=1, outlettype=["float"])
    builder.add("comment", [640.0, 350.0, 90.0, 18.0], text="GEN WET L", presentation=True, fontsize=9.0)
    builder.add("comment", [640.0, 370.0, 90.0, 18.0], text="GEN WET R", presentation=True, fontsize=9.0)
    builder.connect(reverb_level_l, 0, wet_meter_l)
    builder.connect(reverb_level_r, 0, wet_meter_r)
    output_meter_l = builder.add("meter~", [440.0, 302.0, 280.0, 16.0], presentation=True, numinlets=1, numoutlets=1, outlettype=["float"])
    output_meter_r = builder.add("meter~", [440.0, 326.0, 280.0, 16.0], presentation=True, numinlets=1, numoutlets=1, outlettype=["float"])
    builder.add("comment", [650.0, 302.0, 70.0, 18.0], text="OUT L", presentation=True)
    builder.add("comment", [650.0, 326.0, 70.0, 18.0], text="OUT R", presentation=True)
    builder.connect(clip_l, 0, output_meter_l)
    builder.connect(clip_r, 0, output_meter_r)
    send_l = builder.add("newobj", [1525.0, 330.0, 145.0, 22.0], text="send~ qmw_surface_L")
    send_r = builder.add("newobj", [1525.0, 366.0, 145.0, 22.0], text="send~ qmw_surface_R")
    dac = builder.add("ezdac~", [650.0, 414.0, 52.0, 52.0], presentation=True, numinlets=2, numoutlets=0)
    builder.add("comment", [622.0, 470.0, 105.0, 18.0], text="AUDIO DSP", presentation=True, fontface=1)
    for source, destination, inlet in ((clip_l, send_l, 0), (clip_r, send_r, 0), (clip_l, dac, 0), (clip_r, dac, 1)):
        builder.connect(source, 0, destination, inlet)

    builder.add(
        "comment",
        [820.0, 850.0, 390.0, 72.0],
        text=(
            "PLATONIC: tetra · cube · octa · dodeca · icosa\n"
            "ALGEBRAIC: sphere · ellipsoid · torus · superellipsoid · tanglecube · heart · Roman · Cayley\n"
            "MINIMAL: gyroid · Schwarz P/D · Neovius · Lidinoid · I-WP · Fischer-Koch S · catenoid · helicoid · CUSTOM expr"
        ),
        linecount=3,
        textcolor=[0.66, 0.82, 0.78, 1.0],
    )

    raw = builder.add("newobj", [820.0, 430.0, 95.0, 22.0], text="r qmw.osc.raw")
    route_qmw = builder.add("newobj", [930.0, 430.0, 98.0, 22.0], text="OSC-route /qmw")
    route_density = builder.add("newobj", [1045.0, 430.0, 145.0, 22.0], text="OSC-route /density_field")
    route_values = builder.add(
        "newobj",
        [1210.0, 430.0, 390.0, 22.0],
        text="OSC-route /magnitude /harmonics /entropy /purity /coherence",
    )
    builder.connect(raw, 0, route_qmw)
    builder.connect(route_qmw, 0, route_density)
    builder.connect(route_density, 0, route_values)

    bloch_qmw = builder.add("newobj", [820.0, 900.0, 98.0, 22.0], text="OSC-route /qmw")
    bloch_root = builder.add("newobj", [930.0, 900.0, 105.0, 22.0], text="OSC-route /bloch")
    bloch_axes = builder.add(
        "newobj",
        [1045.0, 900.0, 250.0, 22.0],
        text="OSC-route /vector_x /vector_y /vector_z",
    )
    builder.connect(raw, 0, bloch_qmw)
    builder.connect(bloch_qmw, 0, bloch_root)
    builder.connect(bloch_root, 0, bloch_axes)
    for index, destination in enumerate(bloch_rotation_values):
        normalize = builder.add(
            "newobj",
            [1045.0 + index * 130.0, 935.0, 120.0, 22.0],
            text="scale -1. 1. -0.25 0.25",
        )
        builder.connect(bloch_axes, index, normalize)
        builder.connect(normalize, 0, destination)

    # Bloch spherical-harmonic controls arrive as one coherent QMW acoustic
    # family. Route them directly so the reverb responds whenever this module
    # is embedded in a control room; the standalone adapter mirrors the same
    # values onto qmw.surface.control for other renderers.
    acoustic_qmw = builder.add(
        "newobj", [820.0, 1265.0, 98.0, 22.0], text="OSC-route /qmw"
    )
    acoustic_root = builder.add(
        "newobj", [930.0, 1265.0, 132.0, 22.0], text="OSC-route /acoustics"
    )
    acoustic_domains = builder.add(
        "newobj",
        [1075.0, 1265.0, 180.0, 22.0],
        text="OSC-route /reverb /modal",
    )
    acoustic_reverb = builder.add(
        "newobj",
        [1270.0, 1265.0, 270.0, 22.0],
        text="OSC-route /resonance /decay /damping",
    )
    acoustic_modal = builder.add(
        "newobj",
        [1270.0, 1300.0, 230.0, 22.0],
        text="OSC-route /tilt /warp /weights",
    )
    builder.connect(raw, 0, acoustic_qmw)
    builder.connect(acoustic_qmw, 0, acoustic_root)
    builder.connect(acoustic_root, 0, acoustic_domains)
    builder.connect(acoustic_domains, 0, acoustic_reverb)
    builder.connect(acoustic_domains, 1, acoustic_modal)
    direct_scalars = (
        (acoustic_reverb, 0, "harmonic_resonance"),
        (acoustic_reverb, 1, "decay"),
        (acoustic_reverb, 2, "absorb"),
        (acoustic_modal, 0, "spectral_tilt"),
        (acoustic_modal, 1, "modal_warp"),
    )
    for index, (source, outlet, parameter) in enumerate(direct_scalars):
        prepend = builder.add(
            "newobj",
            [820.0 + (index % 3) * 180.0, 1335.0 + (index // 3) * 35.0, 165.0, 22.0],
            text=f"prepend {parameter}",
        )
        builder.connect(source, outlet, prepend)
        builder.connect(prepend, 0, codebox)
    direct_weights = builder.add(
        "newobj",
        [820.0, 1405.0, 270.0, 22.0],
        text="unpack 0. 0. 0. 0. 0. 0. 0. 0.",
    )
    builder.connect(acoustic_modal, 2, direct_weights)
    for index in range(8):
        prepend = builder.add(
            "newobj",
            [820.0 + (index % 4) * 135.0, 1440.0 + (index // 4) * 35.0, 112.0, 22.0],
            text=f"prepend mw{index + 1}",
        )
        builder.connect(direct_weights, index, prepend)
        builder.connect(prepend, 0, codebox)

    # Local message inlet for future sequencers or alternate XYZ sources.
    # Examples: rot_x 0.25, source 1, rotation_slew_ms 300.
    surface_control = builder.add(
        "newobj", [820.0, 980.0, 132.0, 22.0], text="r qmw.surface.control"
    )
    surface_control_route = builder.add(
        "newobj",
        [965.0, 980.0, 660.0, 22.0],
        text=(
            "route rot_x rot_y rot_z source rotation_slew_ms "
            "geometry_morph_slew_ms morph_slew_ms surface_slew_ms "
            "diffusion_slew_ms geometry_depth_slew_ms size dry_wet "
            "reverb_gain morph deform animate mlx_link a b expr "
            "resonance decay damping spectral_tilt modal_warp modal_weights "
            "harmonic_slew_ms"
        ),
    )
    builder.connect(surface_control, 0, surface_control_route)
    for index, destination in enumerate(manual_rotation_values):
        builder.connect(surface_control_route, index, destination)
    builder.connect(surface_control_route, 3, rotation_source)
    builder.connect(surface_control_route, 4, slew_controls["rotation_slew_ms"])
    builder.connect(surface_control_route, 5, slew_controls["geometry_morph_slew_ms"])
    builder.connect(surface_control_route, 6, slew_controls["geometry_morph_slew_ms"])
    builder.connect(surface_control_route, 7, slew_controls["surface_slew_ms"])
    diffusion_slew_prepend = builder.add(
        "newobj", [820.0, 1015.0, 175.0, 22.0], text="prepend diffusion_slew_ms"
    )
    depth_slew_prepend = builder.add(
        "newobj", [1010.0, 1015.0, 205.0, 22.0], text="prepend geometry_depth_slew_ms"
    )
    builder.connect(surface_control_route, 8, diffusion_slew_prepend)
    builder.connect(surface_control_route, 9, depth_slew_prepend)
    builder.connect(diffusion_slew_prepend, 0, codebox)
    builder.connect(depth_slew_prepend, 0, codebox)

    normalized_targets = (
        (10, size_slider, 1000.0),
        (11, dry_wet_slider, 1000.0),
        (12, reverb_gain_slider, 250.0),
        (13, morph_slider, 1000.0),
        (14, deform_slider, 1000.0),
    )
    for index, destination, multiplier in normalized_targets:
        scale_control = builder.add(
            "newobj", [1230.0 + (index - 10) * 75.0, 1015.0, 67.0, 22.0],
            text=f"* {multiplier:g}",
        )
        builder.connect(surface_control_route, index, scale_control)
        builder.connect(scale_control, 0, destination)
    builder.connect(surface_control_route, 15, animate)
    builder.connect(surface_control_route, 16, emergent_toggle)
    for route_index, selector in ((17, "a"), (18, "b"), (19, "expr")):
        prepend = builder.add(
            "newobj",
            [820.0 + (route_index - 17) * 105.0, 1050.0, 92.0, 22.0],
            text=f"prepend {selector}",
        )
        builder.connect(surface_control_route, route_index, prepend)
        builder.connect(prepend, 0, controller)

    harmonic_scalar_controls = (
        (20, "harmonic_resonance"),
        (21, "decay"),
        (22, "absorb"),
        (23, "spectral_tilt"),
        (24, "modal_warp"),
        (26, "harmonic_slew_ms"),
    )
    for offset, (route_index, parameter) in enumerate(harmonic_scalar_controls):
        prepend = builder.add(
            "newobj",
            [1160.0 + (offset % 3) * 175.0, 1090.0 + (offset // 3) * 35.0, 165.0, 22.0],
            text=f"prepend {parameter}",
        )
        builder.connect(surface_control_route, route_index, prepend)
        builder.connect(prepend, 0, codebox)

    modal_unpack = builder.add(
        "newobj",
        [820.0, 1160.0, 270.0, 22.0],
        text="unpack 0. 0. 0. 0. 0. 0. 0. 0.",
    )
    builder.connect(surface_control_route, 25, modal_unpack)
    for index in range(8):
        prepend = builder.add(
            "newobj",
            [820.0 + (index % 4) * 135.0, 1195.0 + (index // 4) * 35.0, 112.0, 22.0],
            text=f"prepend mw{index + 1}",
        )
        builder.connect(modal_unpack, index, prepend)
        builder.connect(prepend, 0, codebox)

    value_names = ("magnitude", "harmonics", "entropy", "purity", "coherence")
    for index, name in enumerate(value_names):
        prepend = builder.add(
            "newobj",
            [1210.0 + index * 95.0, 470.0, 90.0, 22.0],
            text=f"prepend {name}",
        )
        builder.connect(route_values, index, prepend)
        builder.connect(prepend, 0, controller)

    emergent_udp = builder.add(
        "newobj",
        [820.0, 530.0, 112.0, 22.0],
        text="udpreceive 7431",
    )
    emergent_root = builder.add(
        "newobj",
        [945.0, 530.0, 125.0, 22.0],
        text="OSC-route /emergent",
    )
    emergent_family = builder.add(
        "newobj",
        [1085.0, 530.0, 165.0, 22.0],
        text="OSC-route /geometry /state",
    )
    emergent_geometry = builder.add(
        "newobj",
        [820.0, 570.0, 770.0, 22.0],
        text=(
            "OSC-route /surface_area /mean_height /height_variance "
            "/mean_curvature /curvature_variance /pattern_entropy "
            "/anisotropy /growth_velocity"
        ),
    )
    emergent_names = (
        "surface_area",
        "mean_height",
        "height_variance",
        "mean_curvature",
        "curvature_variance",
        "pattern_entropy",
        "anisotropy",
        "growth_velocity",
    )
    builder.connect(emergent_udp, 0, emergent_root)
    builder.connect(emergent_root, 0, emergent_family)
    builder.connect(emergent_family, 0, emergent_geometry)
    for index, name in enumerate(emergent_names):
        prepend = builder.add(
            "newobj",
            [820.0 + index * 112.0, 608.0, 108.0, 22.0],
            text=f"prepend emergent {name}",
        )
        builder.connect(emergent_geometry, index, prepend)
        builder.connect(prepend, 0, controller)
    emergent_state = builder.add(
        "newobj",
        [1270.0, 530.0, 102.0, 22.0],
        text="OSC-route /preset",
    )
    emergent_preset = builder.add(
        "newobj",
        [1390.0, 530.0, 145.0, 22.0],
        text="prepend emergent_preset",
    )
    builder.connect(emergent_family, 1, emergent_state)
    builder.connect(emergent_state, 0, emergent_preset)
    builder.connect(emergent_preset, 0, controller)

    dependency_cache = [
        {"name": "OSC-route.mxo", "type": "iLaX", "implicit": 1},
        {
            "name": CONTROLLER.name,
            "bootpath": str(MAX_ROOT),
            "patcherrelativepath": "..",
            "type": "TEXT",
            "implicit": 1,
        },
    ]
    return {
        "patcher": {
            "fileversion": 1,
            "appversion": {
                "major": 9,
                "minor": 0,
                "revision": 5,
                "architecture": "x64",
                "modernui": 1,
            },
            "classnamespace": "box",
            "rect": [30.0, 80.0, 1720.0, 650.0],
            "openinpresentation": 1,
            "default_fontsize": 12.0,
            "default_fontface": 0,
            "default_fontname": "Arial",
            "gridonopen": 1,
            "gridsize": [10.0, 10.0],
            "boxes": builder.boxes,
            "lines": builder.lines,
            "dependency_cache": dependency_cache,
            "autosave": 0,
        }
    }


def validate_patch(payload: dict[str, Any]) -> None:
    patcher = payload["patcher"]
    boxes = {entry["box"]["id"]: entry["box"] for entry in patcher["boxes"]}
    texts = [box.get("text", "") for box in boxes.values()]
    codeboxes = [box for box in boxes.values() if box.get("maxclass") == "gen.codebox~"]
    if len(codeboxes) != 1:
        raise RuntimeError("Surface module must contain exactly one Gen~ codebox")
    code = codeboxes[0].get("code", "")
    for token in (
        "qmw_compact_realtime_surface_fdn_v1",
        "Param sf1(0);",
        "Param sf20(0);",
        "Param rot_x(0);",
        "Param rot_y(0);",
        "Param rotation_slew_ms(100);",
        "Param morph_slew_ms(500);",
        "Param geometry_morph_slew_ms(500);",
        "Param surface_slew_ms(250);",
        "Delay dl8(192000);",
        "out2 = right;",
    ):
        if token not in code:
            raise RuntimeError(f"Generated Gen~ code is missing {token!r}")
    for text in (
        "receive~ qmw_spectral_L",
        "receive~ qmw_spectral_R",
        "send~ qmw_surface_L",
        "send~ qmw_surface_R",
        "js qmw_implicit_surface_controller_v1.js",
        "loadmess 650",
        "loadmess 375",
        "/ 250.",
        "prepend size",
        "OSC-route /vector_x /vector_y /vector_z",
        "r qmw.surface.control",
        "prepend rot_x",
        "prepend rot_y",
        "prepend rot_z",
        "switch 2",
        "prepend rotation_slew_ms",
        "prepend geometry_morph_slew_ms",
        "prepend surface_slew_ms",
        "prepend diffusion_slew_ms",
        "prepend geometry_depth_slew_ms",
        "route text",
        "prepend expr",
        "*~ 0.625",
        "*~ 0.375",
    ):
        if text not in texts:
            raise RuntimeError(f"Generated patch is missing {text!r}")
    if not CONTROLLER.is_file():
        raise RuntimeError(f"Missing Max JS controller: {CONTROLLER}")


def sync_embedded_control_room(payload: dict[str, Any]) -> bool:
    """Refresh only the embedded surface module, preserving the parent layout."""
    if not CONTROL_ROOM.is_file():
        return False

    control_room = json.loads(CONTROL_ROOM.read_text(encoding="utf-8"))
    replacements = 0

    def visit(value: Any) -> None:
        nonlocal replacements
        if isinstance(value, dict):
            if (
                value.get("maxclass") == "bpatcher"
                and value.get("name") == OUTPUT.name
                and "patcher" in value
            ):
                value["patcher"] = payload["patcher"]
                replacements += 1
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(control_room)
    if replacements > 1:
        raise RuntimeError(
            f"Expected at most one embedded surface module, found {replacements}"
        )
    if replacements == 1:
        CONTROL_ROOM.write_text(
            json.dumps(control_room, indent=4) + "\n",
            encoding="utf-8",
        )
        return True
    return False


def main() -> int:
    payload = build_patch()
    validate_patch(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT}")
    if sync_embedded_control_room(payload):
        print(f"Updated embedded surface module in {CONTROL_ROOM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
