{
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 0,
            "revision": 5,
            "architecture": "x64",
            "modernui": 1
        },
        "classnamespace": "box",
        "rect": [
            30.0,
            80.0,
            1780.0,
            850.0
        ],
        "openinpresentation": 1,
        "default_fontsize": 12.0,
        "default_fontface": 0,
        "default_fontname": "Arial",
        "gridonopen": 1,
        "gridsize": [
            10.0,
            10.0
        ],
        "boxes": [
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "panel",
                    "patching_rect": [
                        10.0,
                        10.0,
                        760.0,
                        490.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        10.0,
                        760.0,
                        490.0
                    ],
                    "background": 1,
                    "bgcolor": [
                        0.055,
                        0.095,
                        0.095,
                        1.0
                    ],
                    "border": 1,
                    "rounded": 12
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "comment",
                    "patching_rect": [
                        28.0,
                        22.0,
                        620.0,
                        28.0
                    ],
                    "text": "QMW REALTIME IMPLICIT SURFACE REVERB v3",
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        22.0,
                        620.0,
                        28.0
                    ],
                    "fontsize": 18.0,
                    "fontface": 1,
                    "textcolor": [
                        0.72,
                        0.95,
                        0.9,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "comment",
                    "patching_rect": [
                        28.0,
                        52.0,
                        700.0,
                        20.0
                    ],
                    "text": "20 field probes \u2192 compact FDN \u00b7 four independently timed qbit grains",
                    "presentation": 1,
                    "presentation_rect": [
                        28.0,
                        52.0,
                        700.0,
                        20.0
                    ],
                    "fontsize": 11.0,
                    "textcolor": [
                        0.55,
                        0.76,
                        0.72,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        210.0,
                        222.0,
                        22.0
                    ],
                    "text": "js qmw_implicit_surface_controller_v1.js",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "gen.codebox~",
                    "patching_rect": [
                        1090.0,
                        330.0,
                        310.0,
                        48.0
                    ],
                    "code": "// qmw_compact_realtime_surface_fdn_v2_noise.genexpr\n// Eight-line geometry-modulated FDN; all twenty implicit-surface probes are used.\n\nParam size(0.45);\nParam decay(0.82);\nParam diffusion(0.78);\nParam absorb(0.32);\nParam width(0.90);\nParam freeze(0);\nParam input_gain(0.65);\nParam output_gain(0.72);\n\n// Internal geometry excitation: onset burst + continuously adjustable floor.\nParam noise_amount(0.28);\nParam noise_decay_ms(45);\nParam onset_threshold(0.012);\nParam onset_sensitivity(10);\nParam noise_color(0.72);\nParam noise_floor(0.008);\nParam noise_spectral_mode(0);\nParam noise_spectral_amount(0.75);\nParam noise_spectral_q(7);\nParam noise_spectral_gain(2.5);\nParam noise_spectral_base_hz(55);\nParam noise_spectral_smooth_ms(80);\nParam surface_depth(0.35);\nParam geometry_morph(0);\nParam geometry_depth(0.55);\nParam harmonicity(0.25);\nParam harmonic_span(0.22);\nParam topology(0.80);\nParam pauli_depth(0.16);\nParam rot_x(0);\nParam rot_y(0);\nParam rot_z(0);\nParam rotation_slew_ms(100);\nParam morph_slew_ms(500);\nParam geometry_morph_slew_ms(500);\nParam surface_slew_ms(250);\nParam diffusion_slew_ms(100);\nParam geometry_depth_slew_ms(100);\nParam solid_a(1);\nParam solid_b(2);\n\nParam sf1(0);  Param sf2(0);  Param sf3(0);  Param sf4(0);\nParam sf5(0);  Param sf6(0);  Param sf7(0);  Param sf8(0);\nParam sf9(0);  Param sf10(0); Param sf11(0); Param sf12(0);\nParam sf13(0); Param sf14(0); Param sf15(0); Param sf16(0);\nParam sf17(0); Param sf18(0); Param sf19(0); Param sf20(0);\n\nParam qm0(1); Param qm1(0); Param qm2(0); Param qm3(0);\nParam qm4(0); Param qm5(0); Param qm6(0); Param qm7(0);\nParam qh0(1); Param qh1(2); Param qh2(3); Param qh3(4);\nParam qh4(5); Param qh5(6); Param qh6(7); Param qh7(8);\n\nDelay dl1(192000); Delay dl2(192000); Delay dl3(192000); Delay dl4(192000);\nDelay dl5(192000); Delay dl6(192000); Delay dl7(192000); Delay dl8(192000);\n\nHistory lp1(0); History lp2(0); History lp3(0); History lp4(0);\nHistory lp5(0); History lp6(0); History lp7(0); History lp8(0);\nHistory shape1_z(0); History shape2_z(0); History shape3_z(0); History shape4_z(0);\nHistory shape5_z(0); History shape6_z(0); History shape7_z(0); History shape8_z(0);\nHistory rot_x_z(0); History rot_y_z(0); History rot_z_z(0);\nHistory morph_z(0); History surface_depth_z(0.35); History diffusion_z(0.78);\nHistory dc_l_x(0); History dc_l_y(0);\nHistory dc_r_x(0); History dc_r_y(0);\nHistory noise_onset_fast(0); History noise_onset_slow(0);\nHistory noise_env(0); History noise_lp(0);\nHistory noise_w0(1); History noise_w1(0); History noise_w2(0); History noise_w3(0);\nHistory noise_h0(1); History noise_h1(3); History noise_h2(5); History noise_h3(7);\nHistory noise_ic1_0(0); History noise_ic2_0(0);\nHistory noise_ic1_1(0); History noise_ic2_1(0);\nHistory noise_ic1_2(0); History noise_ic2_2(0);\nHistory noise_ic1_3(0); History noise_ic2_3(0);\n\nsr = samplerate;\npi2 = 6.28318530718;\ns = clamp(size, 0, 1);\nsize_scale = pow(2, (s * 3) - 1.5);\nsurface = clamp(surface_depth, 0, 0.85);\n\n// Fold twenty probes into eight independent geometry lanes.\nshape1_target = (sf1 + sf9 + sf17) * 0.333333333;\nshape2_target = (sf2 + sf10 + sf18) * 0.333333333;\nshape3_target = (sf3 + sf11 + sf19) * 0.333333333;\nshape4_target = (sf4 + sf12 + sf20) * 0.333333333;\nshape5_target = (sf5 + sf13) * 0.5;\nshape6_target = (sf6 + sf14) * 0.5;\nshape7_target = (sf7 + sf15) * 0.5;\nshape8_target = (sf8 + sf16) * 0.5;\n\nsurface_seconds = max(surface_slew_ms, 0.1) * 0.001;\nsurface_coeff = 1 - exp(-1 / max(sr * surface_seconds, 1));\nshape1_z = shape1_z + surface_coeff * (shape1_target - shape1_z);\nshape2_z = shape2_z + surface_coeff * (shape2_target - shape2_z);\nshape3_z = shape3_z + surface_coeff * (shape3_target - shape3_z);\nshape4_z = shape4_z + surface_coeff * (shape4_target - shape4_z);\nshape5_z = shape5_z + surface_coeff * (shape5_target - shape5_z);\nshape6_z = shape6_z + surface_coeff * (shape6_target - shape6_z);\nshape7_z = shape7_z + surface_coeff * (shape7_target - shape7_z);\nshape8_z = shape8_z + surface_coeff * (shape8_target - shape8_z);\n\ndepth_seconds = max(geometry_depth_slew_ms, 0.1) * 0.001;\ndepth_coeff = 1 - exp(-1 / max(sr * depth_seconds, 1));\nsurface_depth_z = surface_depth_z + depth_coeff * (surface - surface_depth_z);\n\nmorph_seconds = max(geometry_morph_slew_ms, 0.1) * 0.001;\nmorph_coeff = 1 - exp(-1 / max(sr * morph_seconds, 1));\nmorph_z = morph_z + morph_coeff * (clamp(geometry_morph, 0, 1) - morph_z);\n\nrotation_seconds = max(rotation_slew_ms, 0.1) * 0.001;\nrotation_coeff = 1 - exp(-1 / max(sr * rotation_seconds, 1));\nrot_x_delta = rot_x - rot_x_z;\nrot_y_delta = rot_y - rot_y_z;\nrot_z_delta = rot_z - rot_z_z;\nrot_x_delta = rot_x_delta - floor(rot_x_delta + 0.5);\nrot_y_delta = rot_y_delta - floor(rot_y_delta + 0.5);\nrot_z_delta = rot_z_delta - floor(rot_z_delta + 0.5);\nrot_x_z = rot_x_z + rotation_coeff * rot_x_delta;\nrot_y_z = rot_y_z + rotation_coeff * rot_y_delta;\nrot_z_z = rot_z_z + rotation_coeff * rot_z_delta;\n\nrx_angle = rot_x_z * pi2;\nry_angle = rot_y_z * pi2;\nrz_angle = rot_z_z * pi2;\nrxs = sin(rx_angle); rxc = cos(rx_angle);\nrys = sin(ry_angle); ryc = cos(ry_angle);\nrzs = sin(rz_angle); rzc = cos(rz_angle);\n\n// Rotation changes the delay geometry itself, not just the final stereo pan.\n// The larger coefficients make XYZ/Bloch motion clearly audible.\nrot1 =  0.62 * rxs + 0.31 * rys + 0.18 * rzs;\nrot2 = -0.48 * rxs + 0.46 * rys - 0.27 * rzs;\nrot3 =  0.35 * rxs - 0.58 * rys + 0.39 * rzs;\nrot4 = -0.57 * rxs - 0.29 * rys - 0.36 * rzs;\nrot5 =  0.44 * rxc + 0.36 * rys - 0.31 * rzs;\nrot6 = -0.38 * rxs + 0.51 * ryc + 0.28 * rzs;\nrot7 =  0.29 * rxs - 0.41 * rys + 0.52 * rzc;\nrot8 = -0.53 * rxc - 0.34 * ryc - 0.26 * rzs;\nshape1 = shape1_z; shape2 = shape2_z; shape3 = shape3_z; shape4 = shape4_z;\nshape5 = shape5_z; shape6 = shape6_z; shape7 = shape7_z; shape8 = shape8_z;\n// Fixed asymmetric terms keep deformation audible even for a perfectly\n// symmetric field such as a sphere sampled on a spherical probe shell.\ndeform_amount = (0.04 + 1.28 * surface_depth_z) * (0.88 + 0.24 * morph_z);\ngeom1 = 0.88 * shape1 + 0.48 * rot1 - 0.42;\ngeom2 = 0.88 * shape2 + 0.48 * rot2 + 0.36;\ngeom3 = 0.88 * shape3 + 0.48 * rot3 - 0.28;\ngeom4 = 0.88 * shape4 + 0.48 * rot4 + 0.46;\ngeom5 = 0.88 * shape5 + 0.48 * rot5 - 0.22;\ngeom6 = 0.88 * shape6 + 0.48 * rot6 + 0.31;\ngeom7 = 0.88 * shape7 + 0.48 * rot7 - 0.49;\ngeom8 = 0.88 * shape8 + 0.48 * rot8 + 0.27;\n\nd1 = clamp(31 * size_scale * exp(deform_amount * geom1) * sr * 0.001, 16, 191999);\nd2 = clamp(37 * size_scale * exp(deform_amount * geom2) * sr * 0.001, 16, 191999);\nd3 = clamp(43 * size_scale * exp(deform_amount * geom3) * sr * 0.001, 16, 191999);\nd4 = clamp(47 * size_scale * exp(deform_amount * geom4) * sr * 0.001, 16, 191999);\nd5 = clamp(53 * size_scale * exp(deform_amount * geom5) * sr * 0.001, 16, 191999);\nd6 = clamp(59 * size_scale * exp(deform_amount * geom6) * sr * 0.001, 16, 191999);\nd7 = clamp(67 * size_scale * exp(deform_amount * geom7) * sr * 0.001, 16, 191999);\nd8 = clamp(73 * size_scale * exp(deform_amount * geom8) * sr * 0.001, 16, 191999);\n\nr1 = dl1.read(d1); r2 = dl2.read(d2); r3 = dl3.read(d3); r4 = dl4.read(d4);\nr5 = dl5.read(d5); r6 = dl6.read(d6); r7 = dl7.read(d7); r8 = dl8.read(d8);\n\nshape_activity = (\n    abs(shape1) + abs(shape2) + abs(shape3) + abs(shape4)\n    + abs(shape5) + abs(shape6) + abs(shape7) + abs(shape8)\n) * 0.125;\neffective_absorb = clamp(\n    absorb + surface_depth_z * (0.14 + 0.18 * shape_activity),\n    0,\n    0.94\n);\ncut = clamp(0.025 + (1 - effective_absorb) * 0.42, 0.02, 0.46);\nlp1 = lp1 + cut * (r1 - lp1); lp2 = lp2 + cut * (r2 - lp2);\nlp3 = lp3 + cut * (r3 - lp3); lp4 = lp4 + cut * (r4 - lp4);\nlp5 = lp5 + cut * (r5 - lp5); lp6 = lp6 + cut * (r6 - lp6);\nlp7 = lp7 + cut * (r7 - lp7); lp8 = lp8 + cut * (r8 - lp8);\n\nf1 = mix(r1, lp1, effective_absorb); f2 = mix(r2, lp2, effective_absorb);\nf3 = mix(r3, lp3, effective_absorb); f4 = mix(r4, lp4, effective_absorb);\nf5 = mix(r5, lp5, effective_absorb); f6 = mix(r6, lp6, effective_absorb);\nf7 = mix(r7, lp7, effective_absorb); f8 = mix(r8, lp8, effective_absorb);\n\n// Normalized eight-point Hadamard diffusion matrix.\nhn = 0.353553391;\nh1 = ( f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8) * hn;\nh2 = ( f1 - f2 + f3 - f4 + f5 - f6 + f7 - f8) * hn;\nh3 = ( f1 + f2 - f3 - f4 + f5 + f6 - f7 - f8) * hn;\nh4 = ( f1 - f2 - f3 + f4 + f5 - f6 - f7 + f8) * hn;\nh5 = ( f1 + f2 + f3 + f4 - f5 - f6 - f7 - f8) * hn;\nh6 = ( f1 - f2 + f3 - f4 - f5 + f6 - f7 + f8) * hn;\nh7 = ( f1 + f2 - f3 - f4 - f5 - f6 + f7 + f8) * hn;\nh8 = ( f1 - f2 - f3 + f4 - f5 + f6 + f7 - f8) * hn;\n\ndiffusion_seconds = max(diffusion_slew_ms, 0.1) * 0.001;\ndiffusion_coeff = 1 - exp(-1 / max(sr * diffusion_seconds, 1));\ndiffusion_z = diffusion_z + diffusion_coeff * (clamp(diffusion, 0, 1) - diffusion_z);\ndiff_amount = diffusion_z;\nn1 = mix(f1, h1, diff_amount); n2 = mix(f2, h2, diff_amount);\nn3 = mix(f3, h3, diff_amount); n4 = mix(f4, h4, diff_amount);\nn5 = mix(f5, h5, diff_amount); n6 = mix(f6, h6, diff_amount);\nn7 = mix(f7, h7, diff_amount); n8 = mix(f8, h8, diff_amount);\n\nfr = clamp(freeze, 0, 1);\neffective_decay = clamp(\n    decay + 0.10 * surface_depth_z - 0.06 * shape_activity,\n    0,\n    1\n);\nfeedback = mix(0.48 + 0.49 * effective_decay, 0.999, fr);\n// Input and noise are combined *inside* the geometry excitation path.\ninput_signal = in1 * input_gain;\ninput_abs = abs(input_signal);\nnoise_fast_coeff = exp(-1 / max(0.0015 * sr, 1));\nnoise_slow_coeff = exp(-1 / max(0.035 * sr, 1));\nnoise_onset_fast = input_abs + noise_fast_coeff * (noise_onset_fast - input_abs);\nnoise_onset_slow = input_abs + noise_slow_coeff * (noise_onset_slow - input_abs);\nnoise_onset = clamp(\n    (noise_onset_fast - noise_onset_slow - max(onset_threshold, 0))\n    * max(onset_sensitivity, 0),\n    0,\n    1\n);\nnoise_decay_samples = max(noise_decay_ms, 0.1) * 0.001 * sr;\nnoise_decay_coeff = exp(-1 / max(noise_decay_samples, 1));\nnoise_env = max(noise_env * noise_decay_coeff, noise_onset);\n\nraw_internal_noise = noise();\nnoise_color_norm = clamp(noise_color, 0, 1);\nnoise_cut_hz = min(350 + 15000 * noise_color_norm, 0.45 * sr);\nnoise_cut_coeff = 1 - exp((-pi2 * noise_cut_hz) / sr);\nnoise_lp = noise_lp + noise_cut_coeff * (raw_internal_noise - noise_lp);\ncolored_internal_noise = mix(noise_lp, raw_internal_noise, noise_color_norm);\n\n// Four inexpensive state-variable bands follow paired qm magnitudes and qh\n// Hamiltonian ratios. This retains the earlier quantum spectral character\n// without importing the twenty-delay research core.\nnoise_smooth_seconds = max(noise_spectral_smooth_ms, 0.1) * 0.001;\nnoise_smooth_coeff = 1 - exp(-1 / max(sr * noise_smooth_seconds, 1));\nnoise_w0_target = sqrt(max(0, qm0 + qm1));\nnoise_w1_target = sqrt(max(0, qm2 + qm3));\nnoise_w2_target = sqrt(max(0, qm4 + qm5));\nnoise_w3_target = sqrt(max(0, qm6 + qm7));\nnoise_w0 = noise_w0 + noise_smooth_coeff * (noise_w0_target - noise_w0);\nnoise_w1 = noise_w1 + noise_smooth_coeff * (noise_w1_target - noise_w1);\nnoise_w2 = noise_w2 + noise_smooth_coeff * (noise_w2_target - noise_w2);\nnoise_w3 = noise_w3 + noise_smooth_coeff * (noise_w3_target - noise_w3);\nnoise_h0 = noise_h0 + noise_smooth_coeff * (max(qh0, 0.01) - noise_h0);\nnoise_h1 = noise_h1 + noise_smooth_coeff * (max(qh2, 0.01) - noise_h1);\nnoise_h2 = noise_h2 + noise_smooth_coeff * (max(qh4, 0.01) - noise_h2);\nnoise_h3 = noise_h3 + noise_smooth_coeff * (max(qh6, 0.01) - noise_h3);\nnoise_base = clamp(noise_spectral_base_hz, 20, 2000);\nnoise_k = 1 / max(noise_spectral_q, 0.5);\n\nnoise_f0 = clamp(noise_base * noise_h0, 20, 0.45 * sr);\nnoise_g0 = tan(0.5 * pi2 * noise_f0 / sr);\nnoise_a1_0 = 1 / (1 + noise_g0 * (noise_g0 + noise_k));\nnoise_a2_0 = noise_g0 * noise_a1_0; noise_a3_0 = noise_g0 * noise_a2_0;\nnoise_v3_0 = colored_internal_noise - noise_ic2_0;\nnoise_v1_0 = noise_a1_0 * noise_ic1_0 + noise_a2_0 * noise_v3_0;\nnoise_v2_0 = noise_ic2_0 + noise_a2_0 * noise_ic1_0 + noise_a3_0 * noise_v3_0;\nnoise_ic1_0 = 2 * noise_v1_0 - noise_ic1_0; noise_ic2_0 = 2 * noise_v2_0 - noise_ic2_0;\n\nnoise_f1 = clamp(noise_base * noise_h1, 20, 0.45 * sr);\nnoise_g1 = tan(0.5 * pi2 * noise_f1 / sr);\nnoise_a1_1 = 1 / (1 + noise_g1 * (noise_g1 + noise_k));\nnoise_a2_1 = noise_g1 * noise_a1_1; noise_a3_1 = noise_g1 * noise_a2_1;\nnoise_v3_1 = colored_internal_noise - noise_ic2_1;\nnoise_v1_1 = noise_a1_1 * noise_ic1_1 + noise_a2_1 * noise_v3_1;\nnoise_v2_1 = noise_ic2_1 + noise_a2_1 * noise_ic1_1 + noise_a3_1 * noise_v3_1;\nnoise_ic1_1 = 2 * noise_v1_1 - noise_ic1_1; noise_ic2_1 = 2 * noise_v2_1 - noise_ic2_1;\n\nnoise_f2 = clamp(noise_base * noise_h2, 20, 0.45 * sr);\nnoise_g2 = tan(0.5 * pi2 * noise_f2 / sr);\nnoise_a1_2 = 1 / (1 + noise_g2 * (noise_g2 + noise_k));\nnoise_a2_2 = noise_g2 * noise_a1_2; noise_a3_2 = noise_g2 * noise_a2_2;\nnoise_v3_2 = colored_internal_noise - noise_ic2_2;\nnoise_v1_2 = noise_a1_2 * noise_ic1_2 + noise_a2_2 * noise_v3_2;\nnoise_v2_2 = noise_ic2_2 + noise_a2_2 * noise_ic1_2 + noise_a3_2 * noise_v3_2;\nnoise_ic1_2 = 2 * noise_v1_2 - noise_ic1_2; noise_ic2_2 = 2 * noise_v2_2 - noise_ic2_2;\n\nnoise_f3 = clamp(noise_base * noise_h3, 20, 0.45 * sr);\nnoise_g3 = tan(0.5 * pi2 * noise_f3 / sr);\nnoise_a1_3 = 1 / (1 + noise_g3 * (noise_g3 + noise_k));\nnoise_a2_3 = noise_g3 * noise_a1_3; noise_a3_3 = noise_g3 * noise_a2_3;\nnoise_v3_3 = colored_internal_noise - noise_ic2_3;\nnoise_v1_3 = noise_a1_3 * noise_ic1_3 + noise_a2_3 * noise_v3_3;\nnoise_v2_3 = noise_ic2_3 + noise_a2_3 * noise_ic1_3 + noise_a3_3 * noise_v3_3;\nnoise_ic1_3 = 2 * noise_v1_3 - noise_ic1_3; noise_ic2_3 = 2 * noise_v2_3 - noise_ic2_3;\n\nnoise_weight_energy = noise_w0 * noise_w0 + noise_w1 * noise_w1\n    + noise_w2 * noise_w2 + noise_w3 * noise_w3;\nquantum_internal_noise = (\n    noise_v1_0 * noise_w0 + noise_v1_1 * noise_w1\n    + noise_v1_2 * noise_w2 + noise_v1_3 * noise_w3\n) / sqrt(max(noise_weight_energy, 0.000001));\nspectral_internal_noise = tanh(quantum_internal_noise * clamp(noise_spectral_gain, 0, 8));\nshaped_internal_noise = mix(\n    colored_internal_noise,\n    spectral_internal_noise,\n    clamp(noise_spectral_amount, 0, 1)\n);\ninternal_noise = shaped_internal_noise * (\n    clamp(noise_floor, 0, 0.25)\n    + noise_env * clamp(noise_amount, 0, 1)\n);\nexcite = (input_signal + internal_noise) * (1 - fr) * 0.42;\ndl1.write(tanh( excite + feedback * n1));\ndl2.write(tanh(-excite + feedback * n2));\ndl3.write(tanh( excite + feedback * n3));\ndl4.write(tanh(-excite + feedback * n4));\ndl5.write(tanh(-excite + feedback * n5));\ndl6.write(tanh( excite + feedback * n6));\ndl7.write(tanh(-excite + feedback * n7));\ndl8.write(tanh( excite + feedback * n8));\n\nspread = clamp(width, 0, 1);\ndecoder_a_l = f1 + f3 + f6 + f8 + spread * (f2 - f5);\ndecoder_a_r = f2 + f4 + f5 + f7 + spread * (f3 - f6);\ndecoder_b_l = f2 + f3 + f5 + f8 + spread * (f1 - f7);\ndecoder_b_r = f1 + f4 + f6 + f7 + spread * (f5 - f2);\ndecoder_c_l = f1 + f2 + f7 + f8 + spread * (f3 - f6);\ndecoder_c_r = f3 + f4 + f5 + f6 + spread * (f8 - f1);\nx_mix = clamp(0.5 + 0.5 * rxs + 0.22 * surface_depth_z * shape1, 0, 1);\ny_mix = clamp(0.5 + 0.5 * rys + 0.22 * surface_depth_z * shape5, 0, 1);\ndecoder_x_l = mix(decoder_a_l, decoder_b_l, x_mix);\ndecoder_x_r = mix(decoder_a_r, decoder_b_r, x_mix);\ndecoder_y_l = mix(decoder_x_l, decoder_c_l, y_mix);\ndecoder_y_r = mix(decoder_x_r, decoder_c_r, y_mix);\nleft_raw = (rzc * decoder_y_l - rzs * decoder_y_r) * output_gain * 0.24;\nright_raw = (rzs * decoder_y_l + rzc * decoder_y_r) * output_gain * 0.24;\n\ndc = exp((-pi2 * 18) / sr);\nleft = left_raw - dc_l_x + dc * dc_l_y;\nright = right_raw - dc_r_x + dc * dc_r_y;\ndc_l_x = left_raw; dc_l_y = left;\ndc_r_x = right_raw; dc_r_y = right;\n\nout1 = left;\nout2 = right;\n",
                    "fontname": "<Monospaced>",
                    "fontsize": 10.0,
                    "numinlets": 9,
                    "numoutlets": 2,
                    "outlettype": [
                        "signal",
                        "signal"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "umenu",
                    "patching_rect": [
                        38.0,
                        105.0,
                        150.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        105.0,
                        150.0,
                        22.0
                    ],
                    "items": [
                        "tetrahedron",
                        ",",
                        "cube",
                        ",",
                        "octahedron",
                        ",",
                        "dodecahedron",
                        ",",
                        "icosahedron",
                        ",",
                        "sphere",
                        ",",
                        "ellipsoid",
                        ",",
                        "torus",
                        ",",
                        "superellipsoid",
                        ",",
                        "tanglecube",
                        ",",
                        "heart",
                        ",",
                        "roman_surface",
                        ",",
                        "cayley",
                        ",",
                        "gyroid",
                        ",",
                        "schwarz_p",
                        ",",
                        "schwarz_d",
                        ",",
                        "neovius",
                        ",",
                        "lidinoid",
                        ",",
                        "iwp",
                        ",",
                        "fischer_koch_s",
                        ",",
                        "catenoid",
                        ",",
                        "helicoid",
                        ",",
                        "custom"
                    ],
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "int",
                        "",
                        ""
                    ],
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "umenu",
                    "patching_rect": [
                        218.0,
                        105.0,
                        150.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        218.0,
                        105.0,
                        150.0,
                        22.0
                    ],
                    "items": [
                        "tetrahedron",
                        ",",
                        "cube",
                        ",",
                        "octahedron",
                        ",",
                        "dodecahedron",
                        ",",
                        "icosahedron",
                        ",",
                        "sphere",
                        ",",
                        "ellipsoid",
                        ",",
                        "torus",
                        ",",
                        "superellipsoid",
                        ",",
                        "tanglecube",
                        ",",
                        "heart",
                        ",",
                        "roman_surface",
                        ",",
                        "cayley",
                        ",",
                        "gyroid",
                        ",",
                        "schwarz_p",
                        ",",
                        "schwarz_d",
                        ",",
                        "neovius",
                        ",",
                        "lidinoid",
                        ",",
                        "iwp",
                        ",",
                        "fischer_koch_s",
                        ",",
                        "catenoid",
                        ",",
                        "helicoid",
                        ",",
                        "custom"
                    ],
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "int",
                        "",
                        ""
                    ],
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "comment",
                    "patching_rect": [
                        38.0,
                        82.0,
                        150.0,
                        18.0
                    ],
                    "text": "SURFACE A",
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        82.0,
                        150.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "maxclass": "comment",
                    "patching_rect": [
                        218.0,
                        82.0,
                        150.0,
                        18.0
                    ],
                    "text": "SURFACE B",
                    "presentation": 1,
                    "presentation_rect": [
                        218.0,
                        82.0,
                        150.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        88.0,
                        68.0,
                        22.0
                    ],
                    "text": "prepend a"
                }
            },
            {
                "box": {
                    "id": "obj-11",
                    "maxclass": "newobj",
                    "patching_rect": [
                        900.0,
                        88.0,
                        68.0,
                        22.0
                    ],
                    "text": "prepend b"
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        50.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 5"
                }
            },
            {
                "box": {
                    "id": "obj-13",
                    "maxclass": "newobj",
                    "patching_rect": [
                        900.0,
                        50.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 13"
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "slider",
                    "patching_rect": [
                        38.0,
                        166.0,
                        330.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        166.0,
                        330.0,
                        24.0
                    ],
                    "size": 1001,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-15",
                    "maxclass": "comment",
                    "patching_rect": [
                        38.0,
                        142.0,
                        150.0,
                        18.0
                    ],
                    "text": "EQUATION MORPH",
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        142.0,
                        150.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-16",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        126.0,
                        58.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-17",
                    "maxclass": "newobj",
                    "patching_rect": [
                        890.0,
                        126.0,
                        92.0,
                        22.0
                    ],
                    "text": "prepend morph"
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "slider",
                    "patching_rect": [
                        398.0,
                        166.0,
                        210.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        398.0,
                        166.0,
                        210.0,
                        24.0
                    ],
                    "size": 851,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "maxclass": "comment",
                    "patching_rect": [
                        398.0,
                        142.0,
                        150.0,
                        18.0
                    ],
                    "text": "FIELD DEFORMATION",
                    "presentation": 1,
                    "presentation_rect": [
                        398.0,
                        142.0,
                        150.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        164.0,
                        58.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "newobj",
                    "patching_rect": [
                        890.0,
                        164.0,
                        96.0,
                        22.0
                    ],
                    "text": "prepend deform"
                }
            },
            {
                "box": {
                    "id": "obj-22",
                    "maxclass": "newobj",
                    "patching_rect": [
                        990.0,
                        50.0,
                        86.0,
                        22.0
                    ],
                    "text": "loadmess 350"
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "toggle",
                    "patching_rect": [
                        638.0,
                        165.0,
                        25.0,
                        25.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        638.0,
                        165.0,
                        25.0,
                        25.0
                    ],
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "comment",
                    "patching_rect": [
                        670.0,
                        168.0,
                        70.0,
                        18.0
                    ],
                    "text": "ANIMATE",
                    "presentation": 1,
                    "presentation_rect": [
                        670.0,
                        168.0,
                        70.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-25",
                    "maxclass": "toggle",
                    "patching_rect": [
                        638.0,
                        104.0,
                        25.0,
                        25.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        638.0,
                        104.0,
                        25.0,
                        25.0
                    ],
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "comment",
                    "patching_rect": [
                        670.0,
                        107.0,
                        76.0,
                        18.0
                    ],
                    "text": "MLX LINK",
                    "presentation": 1,
                    "presentation_rect": [
                        670.0,
                        107.0,
                        76.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1095.0,
                        88.0,
                        145.0,
                        22.0
                    ],
                    "text": "prepend emergent_enable"
                }
            },
            {
                "box": {
                    "id": "obj-28",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        250.0,
                        62.0,
                        22.0
                    ],
                    "text": "metro 50"
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "newobj",
                    "patching_rect": [
                        895.0,
                        250.0,
                        94.0,
                        22.0
                    ],
                    "text": "counter 0 999"
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1000.0,
                        250.0,
                        82.0,
                        22.0
                    ],
                    "text": "* 0.006283185"
                }
            },
            {
                "box": {
                    "id": "obj-31",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1095.0,
                        250.0,
                        92.0,
                        22.0
                    ],
                    "text": "prepend phase"
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "message",
                    "patching_rect": [
                        38.0,
                        215.0,
                        702.0,
                        44.0
                    ],
                    "text": "surface sphere gyroid 0. deform 0.35",
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        215.0,
                        702.0,
                        44.0
                    ],
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "comment",
                    "patching_rect": [
                        38.0,
                        446.0,
                        112.0,
                        18.0
                    ],
                    "text": "CUSTOM f(x,y,z)",
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        446.0,
                        112.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "maxclass": "textedit",
                    "patching_rect": [
                        150.0,
                        442.0,
                        405.0,
                        24.0
                    ],
                    "text": "(1+0.5*deform)*x*x + (1-0.3*deform)*y*y + z*z - 0.72",
                    "presentation": 1,
                    "presentation_rect": [
                        150.0,
                        442.0,
                        405.0,
                        24.0
                    ],
                    "keymode": 1,
                    "lines": 1,
                    "wordwrap": 0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 4,
                    "outlettype": [
                        "",
                        "int",
                        "",
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-35",
                    "maxclass": "button",
                    "patching_rect": [
                        565.0,
                        442.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        565.0,
                        442.0,
                        24.0,
                        24.0
                    ],
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "maxclass": "comment",
                    "patching_rect": [
                        594.0,
                        446.0,
                        42.0,
                        18.0
                    ],
                    "text": "APPLY",
                    "presentation": 1,
                    "presentation_rect": [
                        594.0,
                        446.0,
                        42.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-37",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1185.0,
                        210.0,
                        65.0,
                        22.0
                    ],
                    "text": "route text"
                }
            },
            {
                "box": {
                    "id": "obj-38",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1265.0,
                        210.0,
                        82.0,
                        22.0
                    ],
                    "text": "prepend expr"
                }
            },
            {
                "box": {
                    "id": "obj-39",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        330.0,
                        152.0,
                        22.0
                    ],
                    "text": "receive~ qmw_spectral_L"
                }
            },
            {
                "box": {
                    "id": "obj-40",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        366.0,
                        152.0,
                        22.0
                    ],
                    "text": "receive~ qmw_spectral_R"
                }
            },
            {
                "box": {
                    "id": "obj-41",
                    "maxclass": "newobj",
                    "patching_rect": [
                        990.0,
                        330.0,
                        58.0,
                        22.0
                    ],
                    "text": "*~ 0.625"
                }
            },
            {
                "box": {
                    "id": "obj-42",
                    "maxclass": "newobj",
                    "patching_rect": [
                        990.0,
                        366.0,
                        58.0,
                        22.0
                    ],
                    "text": "*~ 0.375"
                }
            },
            {
                "box": {
                    "id": "obj-43",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1060.0,
                        346.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-44",
                    "maxclass": "meter~",
                    "patching_rect": [
                        40.0,
                        302.0,
                        280.0,
                        16.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        40.0,
                        302.0,
                        280.0,
                        16.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-45",
                    "maxclass": "meter~",
                    "patching_rect": [
                        40.0,
                        326.0,
                        280.0,
                        16.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        40.0,
                        326.0,
                        280.0,
                        16.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-46",
                    "maxclass": "comment",
                    "patching_rect": [
                        330.0,
                        302.0,
                        90.0,
                        18.0
                    ],
                    "text": "INPUT L",
                    "presentation": 1,
                    "presentation_rect": [
                        330.0,
                        302.0,
                        90.0,
                        18.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-47",
                    "maxclass": "comment",
                    "patching_rect": [
                        330.0,
                        326.0,
                        90.0,
                        18.0
                    ],
                    "text": "INPUT R",
                    "presentation": 1,
                    "presentation_rect": [
                        330.0,
                        326.0,
                        90.0,
                        18.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-48",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1370.0,
                        310.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-49",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1370.0,
                        346.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-50",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1420.0,
                        310.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-51",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1420.0,
                        346.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-52",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1310.0,
                        390.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-53",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1310.0,
                        426.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-54",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1490.0,
                        330.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-55",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1490.0,
                        366.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-56",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        330.0,
                        88.0,
                        22.0
                    ],
                    "text": "clip~ -0.98 0.98"
                }
            },
            {
                "box": {
                    "id": "obj-57",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        366.0,
                        88.0,
                        22.0
                    ],
                    "text": "clip~ -0.98 0.98"
                }
            },
            {
                "box": {
                    "id": "obj-58",
                    "maxclass": "slider",
                    "patching_rect": [
                        38.0,
                        270.0,
                        210.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        270.0,
                        210.0,
                        20.0
                    ],
                    "size": 1001,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-59",
                    "maxclass": "comment",
                    "patching_rect": [
                        38.0,
                        247.0,
                        210.0,
                        18.0
                    ],
                    "text": "MASTER DRY / WET",
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        247.0,
                        210.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-60",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1310.0,
                        470.0,
                        58.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-61",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1380.0,
                        470.0,
                        42.0,
                        22.0
                    ],
                    "text": "t f f"
                }
            },
            {
                "box": {
                    "id": "obj-62",
                    "maxclass": "message",
                    "patching_rect": [
                        1435.0,
                        455.0,
                        55.0,
                        22.0
                    ],
                    "text": "$1 30"
                }
            },
            {
                "box": {
                    "id": "obj-63",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1500.0,
                        455.0,
                        42.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-64",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1435.0,
                        490.0,
                        42.0,
                        22.0
                    ],
                    "text": "!- 1."
                }
            },
            {
                "box": {
                    "id": "obj-65",
                    "maxclass": "message",
                    "patching_rect": [
                        1490.0,
                        490.0,
                        55.0,
                        22.0
                    ],
                    "text": "$1 30"
                }
            },
            {
                "box": {
                    "id": "obj-66",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1555.0,
                        490.0,
                        42.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-67",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1240.0,
                        470.0,
                        66.0,
                        22.0
                    ],
                    "text": "loadmess 650"
                }
            },
            {
                "box": {
                    "id": "obj-68",
                    "maxclass": "slider",
                    "patching_rect": [
                        268.0,
                        270.0,
                        100.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        268.0,
                        270.0,
                        100.0,
                        20.0
                    ],
                    "size": 1001,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-69",
                    "maxclass": "comment",
                    "patching_rect": [
                        268.0,
                        247.0,
                        125.0,
                        18.0
                    ],
                    "text": "REVERB GAIN 0\u20134x",
                    "presentation": 1,
                    "presentation_rect": [
                        268.0,
                        247.0,
                        125.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-70",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1240.0,
                        520.0,
                        50.0,
                        22.0
                    ],
                    "text": "/ 250."
                }
            },
            {
                "box": {
                    "id": "obj-71",
                    "maxclass": "message",
                    "patching_rect": [
                        1300.0,
                        520.0,
                        55.0,
                        22.0
                    ],
                    "text": "$1 30"
                }
            },
            {
                "box": {
                    "id": "obj-72",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1365.0,
                        520.0,
                        42.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-73",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1160.0,
                        520.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 375"
                }
            },
            {
                "box": {
                    "id": "obj-74",
                    "maxclass": "slider",
                    "patching_rect": [
                        398.0,
                        270.0,
                        210.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        398.0,
                        270.0,
                        210.0,
                        20.0
                    ],
                    "size": 1001,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-75",
                    "maxclass": "comment",
                    "patching_rect": [
                        398.0,
                        247.0,
                        150.0,
                        18.0
                    ],
                    "text": "SIZE",
                    "presentation": 1,
                    "presentation_rect": [
                        398.0,
                        247.0,
                        150.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-76",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1095.0,
                        290.0,
                        58.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-77",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1165.0,
                        290.0,
                        80.0,
                        22.0
                    ],
                    "text": "prepend size"
                }
            },
            {
                "box": {
                    "id": "obj-78",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1015.0,
                        290.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 450"
                }
            },
            {
                "box": {
                    "id": "obj-79",
                    "maxclass": "toggle",
                    "patching_rect": [
                        638.0,
                        265.0,
                        25.0,
                        25.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        638.0,
                        265.0,
                        25.0,
                        25.0
                    ],
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-80",
                    "maxclass": "comment",
                    "patching_rect": [
                        670.0,
                        268.0,
                        80.0,
                        18.0
                    ],
                    "text": "BLOCH XYZ",
                    "presentation": 1,
                    "presentation_rect": [
                        670.0,
                        268.0,
                        80.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-81",
                    "maxclass": "newobj",
                    "patching_rect": [
                        930.0,
                        650.0,
                        68.0,
                        22.0
                    ],
                    "text": "loadmess 0"
                }
            },
            {
                "box": {
                    "id": "obj-82",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1010.0,
                        650.0,
                        42.0,
                        22.0
                    ],
                    "text": "t b i"
                }
            },
            {
                "box": {
                    "id": "obj-83",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1065.0,
                        650.0,
                        32.0,
                        22.0
                    ],
                    "text": "+ 1"
                }
            },
            {
                "box": {
                    "id": "obj-84",
                    "maxclass": "slider",
                    "patching_rect": [
                        38.0,
                        418.0,
                        170.0,
                        18.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        418.0,
                        170.0,
                        18.0
                    ],
                    "size": 1001,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-85",
                    "maxclass": "comment",
                    "patching_rect": [
                        38.0,
                        395.0,
                        105.0,
                        18.0
                    ],
                    "text": "ROTATE X",
                    "presentation": 1,
                    "presentation_rect": [
                        38.0,
                        395.0,
                        105.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-86",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        690.0,
                        58.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-87",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        725.0,
                        42.0,
                        22.0
                    ],
                    "text": "f 0."
                }
            },
            {
                "box": {
                    "id": "obj-88",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1120.0,
                        725.0,
                        50.0,
                        22.0
                    ],
                    "text": "f 0."
                }
            },
            {
                "box": {
                    "id": "obj-89",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1120.0,
                        770.0,
                        62.0,
                        22.0
                    ],
                    "text": "switch 2"
                }
            },
            {
                "box": {
                    "id": "obj-90",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1120.0,
                        805.0,
                        88.0,
                        22.0
                    ],
                    "text": "prepend rot_x"
                }
            },
            {
                "box": {
                    "id": "obj-91",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        650.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 0"
                }
            },
            {
                "box": {
                    "id": "obj-92",
                    "maxclass": "slider",
                    "patching_rect": [
                        238.0,
                        418.0,
                        170.0,
                        18.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        238.0,
                        418.0,
                        170.0,
                        18.0
                    ],
                    "size": 1001,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-93",
                    "maxclass": "comment",
                    "patching_rect": [
                        238.0,
                        395.0,
                        105.0,
                        18.0
                    ],
                    "text": "ROTATE Y",
                    "presentation": 1,
                    "presentation_rect": [
                        238.0,
                        395.0,
                        105.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-94",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        690.0,
                        58.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-95",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        725.0,
                        42.0,
                        22.0
                    ],
                    "text": "f 0."
                }
            },
            {
                "box": {
                    "id": "obj-96",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1210.0,
                        725.0,
                        50.0,
                        22.0
                    ],
                    "text": "f 0."
                }
            },
            {
                "box": {
                    "id": "obj-97",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1220.0,
                        770.0,
                        62.0,
                        22.0
                    ],
                    "text": "switch 2"
                }
            },
            {
                "box": {
                    "id": "obj-98",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1220.0,
                        805.0,
                        88.0,
                        22.0
                    ],
                    "text": "prepend rot_y"
                }
            },
            {
                "box": {
                    "id": "obj-99",
                    "maxclass": "newobj",
                    "patching_rect": [
                        910.0,
                        650.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 0"
                }
            },
            {
                "box": {
                    "id": "obj-100",
                    "maxclass": "slider",
                    "patching_rect": [
                        438.0,
                        418.0,
                        170.0,
                        18.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        438.0,
                        418.0,
                        170.0,
                        18.0
                    ],
                    "size": 1001,
                    "floatoutput": 0,
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-101",
                    "maxclass": "comment",
                    "patching_rect": [
                        438.0,
                        395.0,
                        105.0,
                        18.0
                    ],
                    "text": "ROTATE Z",
                    "presentation": 1,
                    "presentation_rect": [
                        438.0,
                        395.0,
                        105.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-102",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1000.0,
                        690.0,
                        58.0,
                        22.0
                    ],
                    "text": "/ 1000."
                }
            },
            {
                "box": {
                    "id": "obj-103",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1000.0,
                        725.0,
                        42.0,
                        22.0
                    ],
                    "text": "f 0."
                }
            },
            {
                "box": {
                    "id": "obj-104",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1300.0,
                        725.0,
                        50.0,
                        22.0
                    ],
                    "text": "f 0."
                }
            },
            {
                "box": {
                    "id": "obj-105",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1320.0,
                        770.0,
                        62.0,
                        22.0
                    ],
                    "text": "switch 2"
                }
            },
            {
                "box": {
                    "id": "obj-106",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1320.0,
                        805.0,
                        88.0,
                        22.0
                    ],
                    "text": "prepend rot_z"
                }
            },
            {
                "box": {
                    "id": "obj-107",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1000.0,
                        650.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 0"
                }
            },
            {
                "box": {
                    "id": "obj-108",
                    "maxclass": "flonum",
                    "patching_rect": [
                        398.0,
                        105.0,
                        70.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        398.0,
                        105.0,
                        70.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 5000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-109",
                    "maxclass": "comment",
                    "patching_rect": [
                        398.0,
                        82.0,
                        76.0,
                        18.0
                    ],
                    "text": "ROT SLEW",
                    "presentation": 1,
                    "presentation_rect": [
                        398.0,
                        82.0,
                        76.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-110",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1420.0,
                        650.0,
                        160.0,
                        22.0
                    ],
                    "text": "prepend rotation_slew_ms"
                }
            },
            {
                "box": {
                    "id": "obj-111",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1335.0,
                        650.0,
                        78.0,
                        22.0
                    ],
                    "text": "loadmess 100"
                }
            },
            {
                "box": {
                    "id": "obj-112",
                    "maxclass": "flonum",
                    "patching_rect": [
                        478.0,
                        105.0,
                        70.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        478.0,
                        105.0,
                        70.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 5000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-113",
                    "maxclass": "comment",
                    "patching_rect": [
                        478.0,
                        82.0,
                        76.0,
                        18.0
                    ],
                    "text": "MORPH SLEW",
                    "presentation": 1,
                    "presentation_rect": [
                        478.0,
                        82.0,
                        76.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-114",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1420.0,
                        685.0,
                        160.0,
                        22.0
                    ],
                    "text": "prepend geometry_morph_slew_ms"
                }
            },
            {
                "box": {
                    "id": "obj-115",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1335.0,
                        685.0,
                        78.0,
                        22.0
                    ],
                    "text": "loadmess 500"
                }
            },
            {
                "box": {
                    "id": "obj-116",
                    "maxclass": "flonum",
                    "patching_rect": [
                        558.0,
                        105.0,
                        70.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        558.0,
                        105.0,
                        70.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 5000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-117",
                    "maxclass": "comment",
                    "patching_rect": [
                        558.0,
                        82.0,
                        76.0,
                        18.0
                    ],
                    "text": "SURF SLEW",
                    "presentation": 1,
                    "presentation_rect": [
                        558.0,
                        82.0,
                        76.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-118",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1420.0,
                        720.0,
                        160.0,
                        22.0
                    ],
                    "text": "prepend surface_slew_ms"
                }
            },
            {
                "box": {
                    "id": "obj-119",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1335.0,
                        720.0,
                        78.0,
                        22.0
                    ],
                    "text": "loadmess 250"
                }
            },
            {
                "box": {
                    "id": "obj-120",
                    "maxclass": "meter~",
                    "patching_rect": [
                        440.0,
                        354.0,
                        190.0,
                        12.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        440.0,
                        354.0,
                        190.0,
                        12.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-121",
                    "maxclass": "meter~",
                    "patching_rect": [
                        440.0,
                        374.0,
                        190.0,
                        12.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        440.0,
                        374.0,
                        190.0,
                        12.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-122",
                    "maxclass": "comment",
                    "patching_rect": [
                        640.0,
                        350.0,
                        90.0,
                        18.0
                    ],
                    "text": "GEN WET L",
                    "presentation": 1,
                    "presentation_rect": [
                        640.0,
                        350.0,
                        90.0,
                        18.0
                    ],
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-123",
                    "maxclass": "comment",
                    "patching_rect": [
                        640.0,
                        370.0,
                        90.0,
                        18.0
                    ],
                    "text": "GEN WET R",
                    "presentation": 1,
                    "presentation_rect": [
                        640.0,
                        370.0,
                        90.0,
                        18.0
                    ],
                    "fontsize": 9.0
                }
            },
            {
                "box": {
                    "id": "obj-124",
                    "maxclass": "meter~",
                    "patching_rect": [
                        440.0,
                        302.0,
                        280.0,
                        16.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        440.0,
                        302.0,
                        280.0,
                        16.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-125",
                    "maxclass": "meter~",
                    "patching_rect": [
                        440.0,
                        326.0,
                        280.0,
                        16.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        440.0,
                        326.0,
                        280.0,
                        16.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-126",
                    "maxclass": "comment",
                    "patching_rect": [
                        650.0,
                        302.0,
                        70.0,
                        18.0
                    ],
                    "text": "OUT L",
                    "presentation": 1,
                    "presentation_rect": [
                        650.0,
                        302.0,
                        70.0,
                        18.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-127",
                    "maxclass": "comment",
                    "patching_rect": [
                        650.0,
                        326.0,
                        70.0,
                        18.0
                    ],
                    "text": "OUT R",
                    "presentation": 1,
                    "presentation_rect": [
                        650.0,
                        326.0,
                        70.0,
                        18.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-128",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1525.0,
                        330.0,
                        145.0,
                        22.0
                    ],
                    "text": "send~ qmw_surface_L"
                }
            },
            {
                "box": {
                    "id": "obj-129",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1525.0,
                        366.0,
                        145.0,
                        22.0
                    ],
                    "text": "send~ qmw_surface_R"
                }
            },
            {
                "box": {
                    "id": "obj-130",
                    "maxclass": "ezdac~",
                    "patching_rect": [
                        650.0,
                        414.0,
                        52.0,
                        52.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        650.0,
                        414.0,
                        52.0,
                        52.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "obj-131",
                    "maxclass": "comment",
                    "patching_rect": [
                        622.0,
                        470.0,
                        105.0,
                        18.0
                    ],
                    "text": "AUDIO DSP",
                    "presentation": 1,
                    "presentation_rect": [
                        622.0,
                        470.0,
                        105.0,
                        18.0
                    ],
                    "fontface": 1
                }
            },
            {
                "box": {
                    "id": "obj-132",
                    "maxclass": "comment",
                    "patching_rect": [
                        820.0,
                        850.0,
                        390.0,
                        72.0
                    ],
                    "text": "PLATONIC: tetra \u00b7 cube \u00b7 octa \u00b7 dodeca \u00b7 icosa\nALGEBRAIC: sphere \u00b7 ellipsoid \u00b7 torus \u00b7 superellipsoid \u00b7 tanglecube \u00b7 heart \u00b7 Roman \u00b7 Cayley\nMINIMAL: gyroid \u00b7 Schwarz P/D \u00b7 Neovius \u00b7 Lidinoid \u00b7 I-WP \u00b7 Fischer-Koch S \u00b7 catenoid \u00b7 helicoid \u00b7 CUSTOM expr",
                    "linecount": 3,
                    "textcolor": [
                        0.66,
                        0.82,
                        0.78,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-133",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        430.0,
                        95.0,
                        22.0
                    ],
                    "text": "r qmw.osc.raw"
                }
            },
            {
                "box": {
                    "id": "obj-134",
                    "maxclass": "newobj",
                    "patching_rect": [
                        930.0,
                        430.0,
                        98.0,
                        22.0
                    ],
                    "text": "OSC-route /qmw"
                }
            },
            {
                "box": {
                    "id": "obj-135",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1045.0,
                        430.0,
                        145.0,
                        22.0
                    ],
                    "text": "OSC-route /density_field"
                }
            },
            {
                "box": {
                    "id": "obj-136",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1210.0,
                        430.0,
                        390.0,
                        22.0
                    ],
                    "text": "OSC-route /magnitude /harmonics /entropy /purity /coherence"
                }
            },
            {
                "box": {
                    "id": "obj-137",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        900.0,
                        98.0,
                        22.0
                    ],
                    "text": "OSC-route /qmw"
                }
            },
            {
                "box": {
                    "id": "obj-138",
                    "maxclass": "newobj",
                    "patching_rect": [
                        930.0,
                        900.0,
                        105.0,
                        22.0
                    ],
                    "text": "OSC-route /bloch"
                }
            },
            {
                "box": {
                    "id": "obj-139",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1045.0,
                        900.0,
                        250.0,
                        22.0
                    ],
                    "text": "OSC-route /vector_x /vector_y /vector_z"
                }
            },
            {
                "box": {
                    "id": "obj-140",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1045.0,
                        935.0,
                        120.0,
                        22.0
                    ],
                    "text": "scale -1. 1. -0.25 0.25"
                }
            },
            {
                "box": {
                    "id": "obj-141",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1175.0,
                        935.0,
                        120.0,
                        22.0
                    ],
                    "text": "scale -1. 1. -0.25 0.25"
                }
            },
            {
                "box": {
                    "id": "obj-142",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1305.0,
                        935.0,
                        120.0,
                        22.0
                    ],
                    "text": "scale -1. 1. -0.25 0.25"
                }
            },
            {
                "box": {
                    "id": "obj-143",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        980.0,
                        132.0,
                        22.0
                    ],
                    "text": "r qmw.surface.control"
                }
            },
            {
                "box": {
                    "id": "obj-144",
                    "maxclass": "newobj",
                    "patching_rect": [
                        965.0,
                        980.0,
                        660.0,
                        22.0
                    ],
                    "text": "route rot_x rot_y rot_z source rotation_slew_ms geometry_morph_slew_ms morph_slew_ms surface_slew_ms diffusion_slew_ms geometry_depth_slew_ms size dry_wet reverb_gain morph deform animate mlx_link a b expr"
                }
            },
            {
                "box": {
                    "id": "obj-145",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1015.0,
                        175.0,
                        22.0
                    ],
                    "text": "prepend diffusion_slew_ms"
                }
            },
            {
                "box": {
                    "id": "obj-146",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1010.0,
                        1015.0,
                        205.0,
                        22.0
                    ],
                    "text": "prepend geometry_depth_slew_ms"
                }
            },
            {
                "box": {
                    "id": "obj-147",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1230.0,
                        1015.0,
                        67.0,
                        22.0
                    ],
                    "text": "* 1000"
                }
            },
            {
                "box": {
                    "id": "obj-148",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1305.0,
                        1015.0,
                        67.0,
                        22.0
                    ],
                    "text": "* 1000"
                }
            },
            {
                "box": {
                    "id": "obj-149",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1380.0,
                        1015.0,
                        67.0,
                        22.0
                    ],
                    "text": "* 250"
                }
            },
            {
                "box": {
                    "id": "obj-150",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1455.0,
                        1015.0,
                        67.0,
                        22.0
                    ],
                    "text": "* 1000"
                }
            },
            {
                "box": {
                    "id": "obj-151",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1530.0,
                        1015.0,
                        67.0,
                        22.0
                    ],
                    "text": "* 1000"
                }
            },
            {
                "box": {
                    "id": "obj-152",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1050.0,
                        92.0,
                        22.0
                    ],
                    "text": "prepend a"
                }
            },
            {
                "box": {
                    "id": "obj-153",
                    "maxclass": "newobj",
                    "patching_rect": [
                        925.0,
                        1050.0,
                        92.0,
                        22.0
                    ],
                    "text": "prepend b"
                }
            },
            {
                "box": {
                    "id": "obj-154",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1030.0,
                        1050.0,
                        92.0,
                        22.0
                    ],
                    "text": "prepend expr"
                }
            },
            {
                "box": {
                    "id": "obj-155",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1210.0,
                        470.0,
                        90.0,
                        22.0
                    ],
                    "text": "prepend magnitude"
                }
            },
            {
                "box": {
                    "id": "obj-156",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1305.0,
                        470.0,
                        90.0,
                        22.0
                    ],
                    "text": "prepend harmonics"
                }
            },
            {
                "box": {
                    "id": "obj-157",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1400.0,
                        470.0,
                        90.0,
                        22.0
                    ],
                    "text": "prepend entropy"
                }
            },
            {
                "box": {
                    "id": "obj-158",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1495.0,
                        470.0,
                        90.0,
                        22.0
                    ],
                    "text": "prepend purity"
                }
            },
            {
                "box": {
                    "id": "obj-159",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1590.0,
                        470.0,
                        90.0,
                        22.0
                    ],
                    "text": "prepend coherence"
                }
            },
            {
                "box": {
                    "id": "obj-160",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        530.0,
                        112.0,
                        22.0
                    ],
                    "text": "udpreceive 7431"
                }
            },
            {
                "box": {
                    "id": "obj-161",
                    "maxclass": "newobj",
                    "patching_rect": [
                        945.0,
                        530.0,
                        125.0,
                        22.0
                    ],
                    "text": "OSC-route /emergent"
                }
            },
            {
                "box": {
                    "id": "obj-162",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1085.0,
                        530.0,
                        165.0,
                        22.0
                    ],
                    "text": "OSC-route /geometry /state"
                }
            },
            {
                "box": {
                    "id": "obj-163",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        570.0,
                        770.0,
                        22.0
                    ],
                    "text": "OSC-route /surface_area /mean_height /height_variance /mean_curvature /curvature_variance /pattern_entropy /anisotropy /growth_velocity"
                }
            },
            {
                "box": {
                    "id": "obj-164",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent surface_area"
                }
            },
            {
                "box": {
                    "id": "obj-165",
                    "maxclass": "newobj",
                    "patching_rect": [
                        932.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent mean_height"
                }
            },
            {
                "box": {
                    "id": "obj-166",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1044.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent height_variance"
                }
            },
            {
                "box": {
                    "id": "obj-167",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1156.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent mean_curvature"
                }
            },
            {
                "box": {
                    "id": "obj-168",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1268.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent curvature_variance"
                }
            },
            {
                "box": {
                    "id": "obj-169",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1380.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent pattern_entropy"
                }
            },
            {
                "box": {
                    "id": "obj-170",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1492.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent anisotropy"
                }
            },
            {
                "box": {
                    "id": "obj-171",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1604.0,
                        608.0,
                        108.0,
                        22.0
                    ],
                    "text": "prepend emergent growth_velocity"
                }
            },
            {
                "box": {
                    "id": "obj-172",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1270.0,
                        530.0,
                        102.0,
                        22.0
                    ],
                    "text": "OSC-route /preset"
                }
            },
            {
                "box": {
                    "id": "obj-173",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1390.0,
                        530.0,
                        145.0,
                        22.0
                    ],
                    "text": "prepend emergent_preset"
                }
            },
            {
                "box": {
                    "id": "obj-174",
                    "maxclass": "panel",
                    "patching_rect": [
                        10.0,
                        505.0,
                        760.0,
                        215.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        10.0,
                        505.0,
                        760.0,
                        215.0
                    ],
                    "background": 1,
                    "bgcolor": [
                        0.075,
                        0.065,
                        0.12,
                        1.0
                    ],
                    "border": 1,
                    "rounded": 12
                }
            },
            {
                "box": {
                    "id": "obj-175",
                    "maxclass": "comment",
                    "patching_rect": [
                        25.0,
                        510.0,
                        360.0,
                        22.0
                    ],
                    "text": "RESONANCE GRAINS + QUANTUM RHYTHM MATRIX",
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        510.0,
                        360.0,
                        22.0
                    ],
                    "fontsize": 13.0,
                    "fontface": 1,
                    "textcolor": [
                        0.86,
                        0.78,
                        1.0,
                        1.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-176",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        340.0,
                        245.0,
                        22.0
                    ],
                    "text": "js qmw_resonance_grain_scheduler_v3.js",
                    "numinlets": 1,
                    "numoutlets": 7,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "float",
                        "float",
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-177",
                    "maxclass": "umenu",
                    "patching_rect": [
                        25.0,
                        556.0,
                        100.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        556.0,
                        100.0,
                        22.0
                    ],
                    "items": [
                        "DRONE",
                        ",",
                        "GRAINS",
                        ",",
                        "HYBRID"
                    ],
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "int",
                        "",
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-178",
                    "maxclass": "umenu",
                    "patching_rect": [
                        135.0,
                        556.0,
                        105.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        135.0,
                        556.0,
                        105.0,
                        22.0
                    ],
                    "items": [
                        "LOCAL",
                        ",",
                        "QUANTUM",
                        ",",
                        "OSC"
                    ],
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "int",
                        "",
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-179",
                    "maxclass": "comment",
                    "patching_rect": [
                        25.0,
                        536.0,
                        80.0,
                        18.0
                    ],
                    "text": "MODE",
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        536.0,
                        80.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-180",
                    "maxclass": "comment",
                    "patching_rect": [
                        135.0,
                        536.0,
                        80.0,
                        18.0
                    ],
                    "text": "TRIGGER SOURCE",
                    "presentation": 1,
                    "presentation_rect": [
                        135.0,
                        536.0,
                        80.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-181",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        380.0,
                        88.0,
                        22.0
                    ],
                    "text": "prepend mode"
                }
            },
            {
                "box": {
                    "id": "obj-182",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1880.0,
                        380.0,
                        138.0,
                        22.0
                    ],
                    "text": "prepend trigger_source"
                }
            },
            {
                "box": {
                    "id": "obj-183",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        410.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 2"
                }
            },
            {
                "box": {
                    "id": "obj-184",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1880.0,
                        410.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 0"
                }
            },
            {
                "box": {
                    "id": "obj-185",
                    "maxclass": "comment",
                    "patching_rect": [
                        250.0,
                        536.0,
                        52.0,
                        18.0
                    ],
                    "text": "EVENTS",
                    "presentation": 1,
                    "presentation_rect": [
                        250.0,
                        536.0,
                        52.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-186",
                    "maxclass": "toggle",
                    "patching_rect": [
                        262.0,
                        556.0,
                        22.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        262.0,
                        556.0,
                        22.0,
                        22.0
                    ],
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "int"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-187",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1980.0,
                        410.0,
                        72.0,
                        22.0
                    ],
                    "text": "loadmess 1"
                }
            },
            {
                "box": {
                    "id": "obj-188",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1980.0,
                        380.0,
                        98.0,
                        22.0
                    ],
                    "text": "prepend enable"
                }
            },
            {
                "box": {
                    "id": "obj-189",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        450.0,
                        72.0,
                        22.0
                    ],
                    "text": "metro 50"
                }
            },
            {
                "box": {
                    "id": "obj-190",
                    "maxclass": "comment",
                    "patching_rect": [
                        302.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "text": "Q0 Hz",
                    "presentation": 1,
                    "presentation_rect": [
                        302.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-191",
                    "maxclass": "flonum",
                    "patching_rect": [
                        302.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        302.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 20.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-192",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        528.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend local_rate0"
                }
            },
            {
                "box": {
                    "id": "obj-193",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        556.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 0.85"
                }
            },
            {
                "box": {
                    "id": "obj-194",
                    "maxclass": "comment",
                    "patching_rect": [
                        352.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "text": "Q1 Hz",
                    "presentation": 1,
                    "presentation_rect": [
                        352.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-195",
                    "maxclass": "flonum",
                    "patching_rect": [
                        352.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        352.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 20.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-196",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        640.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend local_rate1"
                }
            },
            {
                "box": {
                    "id": "obj-197",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        668.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 1.1"
                }
            },
            {
                "box": {
                    "id": "obj-198",
                    "maxclass": "comment",
                    "patching_rect": [
                        402.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "text": "Q2 Hz",
                    "presentation": 1,
                    "presentation_rect": [
                        402.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-199",
                    "maxclass": "flonum",
                    "patching_rect": [
                        402.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        402.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 20.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-200",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        752.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend local_rate2"
                }
            },
            {
                "box": {
                    "id": "obj-201",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        500.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 1.45"
                }
            },
            {
                "box": {
                    "id": "obj-202",
                    "maxclass": "comment",
                    "patching_rect": [
                        452.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "text": "Q3 Hz",
                    "presentation": 1,
                    "presentation_rect": [
                        452.0,
                        516.0,
                        52.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-203",
                    "maxclass": "flonum",
                    "patching_rect": [
                        452.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        452.0,
                        537.0,
                        44.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 20.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-204",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        584.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend local_rate3"
                }
            },
            {
                "box": {
                    "id": "obj-205",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        612.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 1.9"
                }
            },
            {
                "box": {
                    "id": "obj-206",
                    "maxclass": "comment",
                    "patching_rect": [
                        502.0,
                        516.0,
                        60.0,
                        18.0
                    ],
                    "text": "PROB",
                    "presentation": 1,
                    "presentation_rect": [
                        502.0,
                        516.0,
                        60.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-207",
                    "maxclass": "flonum",
                    "patching_rect": [
                        502.0,
                        537.0,
                        52.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        502.0,
                        537.0,
                        52.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-208",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        696.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend probability"
                }
            },
            {
                "box": {
                    "id": "obj-209",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        724.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 0.8"
                }
            },
            {
                "box": {
                    "id": "obj-210",
                    "maxclass": "comment",
                    "patching_rect": [
                        560.0,
                        516.0,
                        73.0,
                        18.0
                    ],
                    "text": "DUR ms",
                    "presentation": 1,
                    "presentation_rect": [
                        560.0,
                        516.0,
                        73.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-211",
                    "maxclass": "flonum",
                    "patching_rect": [
                        560.0,
                        537.0,
                        65.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        560.0,
                        537.0,
                        65.0,
                        22.0
                    ],
                    "minimum": 12.0,
                    "maximum": 4000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-212",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        528.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend duration"
                }
            },
            {
                "box": {
                    "id": "obj-213",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        556.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 180"
                }
            },
            {
                "box": {
                    "id": "obj-214",
                    "maxclass": "comment",
                    "patching_rect": [
                        632.0,
                        516.0,
                        66.0,
                        18.0
                    ],
                    "text": "ATK ms",
                    "presentation": 1,
                    "presentation_rect": [
                        632.0,
                        516.0,
                        66.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-215",
                    "maxclass": "flonum",
                    "patching_rect": [
                        632.0,
                        537.0,
                        58.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        632.0,
                        537.0,
                        58.0,
                        22.0
                    ],
                    "minimum": 0.5,
                    "maximum": 1000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-216",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        640.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend attack"
                }
            },
            {
                "box": {
                    "id": "obj-217",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        668.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 12"
                }
            },
            {
                "box": {
                    "id": "obj-218",
                    "maxclass": "comment",
                    "patching_rect": [
                        698.0,
                        516.0,
                        63.0,
                        18.0
                    ],
                    "text": "COH\u2192DUR",
                    "presentation": 1,
                    "presentation_rect": [
                        698.0,
                        516.0,
                        63.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-219",
                    "maxclass": "flonum",
                    "patching_rect": [
                        698.0,
                        537.0,
                        55.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        698.0,
                        537.0,
                        55.0,
                        22.0
                    ],
                    "minimum": -1.0,
                    "maximum": 1.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-220",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        752.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend coherence_duration"
                }
            },
            {
                "box": {
                    "id": "obj-221",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        500.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 0.65"
                }
            },
            {
                "box": {
                    "id": "obj-222",
                    "maxclass": "comment",
                    "patching_rect": [
                        235.0,
                        587.0,
                        66.0,
                        18.0
                    ],
                    "text": "CELL",
                    "presentation": 1,
                    "presentation_rect": [
                        235.0,
                        587.0,
                        66.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-223",
                    "maxclass": "flonum",
                    "patching_rect": [
                        235.0,
                        608.0,
                        58.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        235.0,
                        608.0,
                        58.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 0.99,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-224",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        584.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend cell_threshold"
                }
            },
            {
                "box": {
                    "id": "obj-225",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        612.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 0.2"
                }
            },
            {
                "box": {
                    "id": "obj-226",
                    "maxclass": "comment",
                    "patching_rect": [
                        302.0,
                        587.0,
                        66.0,
                        18.0
                    ],
                    "text": "Q GATE",
                    "presentation": 1,
                    "presentation_rect": [
                        302.0,
                        587.0,
                        66.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-227",
                    "maxclass": "flonum",
                    "patching_rect": [
                        302.0,
                        608.0,
                        58.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        302.0,
                        608.0,
                        58.0,
                        22.0
                    ],
                    "minimum": 0.001,
                    "maximum": 0.25,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-228",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        696.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend quantum_threshold"
                }
            },
            {
                "box": {
                    "id": "obj-229",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        724.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 0.012"
                }
            },
            {
                "box": {
                    "id": "obj-230",
                    "maxclass": "comment",
                    "patching_rect": [
                        368.0,
                        587.0,
                        68.0,
                        18.0
                    ],
                    "text": "STEP ms",
                    "presentation": 1,
                    "presentation_rect": [
                        368.0,
                        587.0,
                        68.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-231",
                    "maxclass": "flonum",
                    "patching_rect": [
                        368.0,
                        608.0,
                        60.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        368.0,
                        608.0,
                        60.0,
                        22.0
                    ],
                    "minimum": 5.0,
                    "maximum": 2000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-232",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        528.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend quantum_step"
                }
            },
            {
                "box": {
                    "id": "obj-233",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        556.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 90"
                }
            },
            {
                "box": {
                    "id": "obj-234",
                    "maxclass": "comment",
                    "patching_rect": [
                        435.0,
                        587.0,
                        76.0,
                        18.0
                    ],
                    "text": "REFRACT ms",
                    "presentation": 1,
                    "presentation_rect": [
                        435.0,
                        587.0,
                        76.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-235",
                    "maxclass": "flonum",
                    "patching_rect": [
                        435.0,
                        608.0,
                        68.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        435.0,
                        608.0,
                        68.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 4000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-236",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        640.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend refractory"
                }
            },
            {
                "box": {
                    "id": "obj-237",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        668.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 400"
                }
            },
            {
                "box": {
                    "id": "obj-238",
                    "maxclass": "comment",
                    "patching_rect": [
                        510.0,
                        587.0,
                        63.0,
                        18.0
                    ],
                    "text": "GROOVE",
                    "presentation": 1,
                    "presentation_rect": [
                        510.0,
                        587.0,
                        63.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-239",
                    "maxclass": "flonum",
                    "patching_rect": [
                        510.0,
                        608.0,
                        55.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        510.0,
                        608.0,
                        55.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-240",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1660.0,
                        752.0,
                        110.0,
                        22.0
                    ],
                    "text": "prepend groove"
                }
            },
            {
                "box": {
                    "id": "obj-241",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1540.0,
                        500.0,
                        105.0,
                        22.0
                    ],
                    "text": "loadmess 0.35"
                }
            },
            {
                "box": {
                    "id": "obj-242",
                    "maxclass": "comment",
                    "patching_rect": [
                        25.0,
                        588.0,
                        70.0,
                        18.0
                    ],
                    "text": "GRAIN LEVEL",
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        588.0,
                        70.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-243",
                    "maxclass": "flonum",
                    "patching_rect": [
                        25.0,
                        608.0,
                        65.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        608.0,
                        65.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 3.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-244",
                    "maxclass": "comment",
                    "patching_rect": [
                        102.0,
                        588.0,
                        70.0,
                        18.0
                    ],
                    "text": "DRONE MIX",
                    "presentation": 1,
                    "presentation_rect": [
                        102.0,
                        588.0,
                        70.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-245",
                    "maxclass": "flonum",
                    "patching_rect": [
                        102.0,
                        608.0,
                        65.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        102.0,
                        608.0,
                        65.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-246",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        735.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend level"
                }
            },
            {
                "box": {
                    "id": "obj-247",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        765.0,
                        90.0,
                        22.0
                    ],
                    "text": "loadmess 1.35"
                }
            },
            {
                "box": {
                    "id": "obj-248",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1900.0,
                        735.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend drone_mix"
                }
            },
            {
                "box": {
                    "id": "obj-249",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1900.0,
                        765.0,
                        90.0,
                        22.0
                    ],
                    "text": "loadmess 0.65"
                }
            },
            {
                "box": {
                    "id": "obj-250",
                    "maxclass": "button",
                    "patching_rect": [
                        182.0,
                        608.0,
                        23.0,
                        23.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        182.0,
                        608.0,
                        23.0,
                        23.0
                    ],
                    "parameter_enable": 0
                }
            },
            {
                "box": {
                    "id": "obj-251",
                    "maxclass": "comment",
                    "patching_rect": [
                        176.0,
                        588.0,
                        52.0,
                        18.0
                    ],
                    "text": "FIRE",
                    "presentation": 1,
                    "presentation_rect": [
                        176.0,
                        588.0,
                        52.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-252",
                    "maxclass": "message",
                    "patching_rect": [
                        2040.0,
                        450.0,
                        52.0,
                        22.0
                    ],
                    "text": "trigger"
                }
            },
            {
                "box": {
                    "id": "obj-253",
                    "maxclass": "message",
                    "patching_rect": [
                        573.0,
                        600.0,
                        169.0,
                        34.0
                    ],
                    "text": "grain hybrid local matrix 0000/0000/0000/0000 ready",
                    "presentation": 1,
                    "presentation_rect": [
                        573.0,
                        600.0,
                        169.0,
                        34.0
                    ],
                    "linecount": 2
                }
            },
            {
                "box": {
                    "id": "obj-254",
                    "maxclass": "comment",
                    "patching_rect": [
                        25.0,
                        647.0,
                        64.0,
                        18.0
                    ],
                    "text": "NOISE",
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        647.0,
                        64.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-255",
                    "maxclass": "flonum",
                    "patching_rect": [
                        25.0,
                        668.0,
                        60.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        25.0,
                        668.0,
                        60.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-256",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1230.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_amount"
                }
            },
            {
                "box": {
                    "id": "obj-257",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1300.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 0.28"
                }
            },
            {
                "box": {
                    "id": "obj-258",
                    "maxclass": "comment",
                    "patching_rect": [
                        95.0,
                        647.0,
                        64.0,
                        18.0
                    ],
                    "text": "FLOOR",
                    "presentation": 1,
                    "presentation_rect": [
                        95.0,
                        647.0,
                        64.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-259",
                    "maxclass": "flonum",
                    "patching_rect": [
                        95.0,
                        668.0,
                        60.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        95.0,
                        668.0,
                        60.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 0.25,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-260",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1935.0,
                        1230.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_floor"
                }
            },
            {
                "box": {
                    "id": "obj-261",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1935.0,
                        1300.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 0.008"
                }
            },
            {
                "box": {
                    "id": "obj-262",
                    "maxclass": "comment",
                    "patching_rect": [
                        165.0,
                        647.0,
                        64.0,
                        18.0
                    ],
                    "text": "COLOR",
                    "presentation": 1,
                    "presentation_rect": [
                        165.0,
                        647.0,
                        64.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-263",
                    "maxclass": "flonum",
                    "patching_rect": [
                        165.0,
                        668.0,
                        60.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        165.0,
                        668.0,
                        60.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-264",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2090.0,
                        1230.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_color"
                }
            },
            {
                "box": {
                    "id": "obj-265",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2090.0,
                        1300.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 0.72"
                }
            },
            {
                "box": {
                    "id": "obj-266",
                    "maxclass": "comment",
                    "patching_rect": [
                        235.0,
                        647.0,
                        72.0,
                        18.0
                    ],
                    "text": "DECAY",
                    "presentation": 1,
                    "presentation_rect": [
                        235.0,
                        647.0,
                        72.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-267",
                    "maxclass": "flonum",
                    "patching_rect": [
                        235.0,
                        668.0,
                        68.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        235.0,
                        668.0,
                        68.0,
                        22.0
                    ],
                    "minimum": 0.1,
                    "maximum": 500.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-268",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2245.0,
                        1230.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_decay_ms"
                }
            },
            {
                "box": {
                    "id": "obj-269",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2245.0,
                        1300.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 45"
                }
            },
            {
                "box": {
                    "id": "obj-270",
                    "maxclass": "comment",
                    "patching_rect": [
                        313.0,
                        647.0,
                        72.0,
                        18.0
                    ],
                    "text": "Q SHAPE",
                    "presentation": 1,
                    "presentation_rect": [
                        313.0,
                        647.0,
                        72.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-271",
                    "maxclass": "flonum",
                    "patching_rect": [
                        313.0,
                        668.0,
                        68.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        313.0,
                        668.0,
                        68.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-272",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1265.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_spectral_amount"
                }
            },
            {
                "box": {
                    "id": "obj-273",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1335.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 0.75"
                }
            },
            {
                "box": {
                    "id": "obj-274",
                    "maxclass": "comment",
                    "patching_rect": [
                        391.0,
                        647.0,
                        68.0,
                        18.0
                    ],
                    "text": "Q GAIN",
                    "presentation": 1,
                    "presentation_rect": [
                        391.0,
                        647.0,
                        68.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-275",
                    "maxclass": "flonum",
                    "patching_rect": [
                        391.0,
                        668.0,
                        64.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        391.0,
                        668.0,
                        64.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 8.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-276",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1935.0,
                        1265.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_spectral_gain"
                }
            },
            {
                "box": {
                    "id": "obj-277",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1935.0,
                        1335.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 2.5"
                }
            },
            {
                "box": {
                    "id": "obj-278",
                    "maxclass": "comment",
                    "patching_rect": [
                        465.0,
                        647.0,
                        76.0,
                        18.0
                    ],
                    "text": "BASE Hz",
                    "presentation": 1,
                    "presentation_rect": [
                        465.0,
                        647.0,
                        76.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-279",
                    "maxclass": "flonum",
                    "patching_rect": [
                        465.0,
                        668.0,
                        72.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        465.0,
                        668.0,
                        72.0,
                        22.0
                    ],
                    "minimum": 20.0,
                    "maximum": 2000.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-280",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2090.0,
                        1265.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_spectral_base_hz"
                }
            },
            {
                "box": {
                    "id": "obj-281",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2090.0,
                        1335.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 55"
                }
            },
            {
                "box": {
                    "id": "obj-282",
                    "maxclass": "comment",
                    "patching_rect": [
                        547.0,
                        647.0,
                        62.0,
                        18.0
                    ],
                    "text": "Q",
                    "presentation": 1,
                    "presentation_rect": [
                        547.0,
                        647.0,
                        62.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-283",
                    "maxclass": "flonum",
                    "patching_rect": [
                        547.0,
                        668.0,
                        58.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        547.0,
                        668.0,
                        58.0,
                        22.0
                    ],
                    "minimum": 0.5,
                    "maximum": 30.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-284",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2245.0,
                        1265.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend noise_spectral_q"
                }
            },
            {
                "box": {
                    "id": "obj-285",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2245.0,
                        1335.0,
                        112.0,
                        22.0
                    ],
                    "text": "loadmess 7"
                }
            },
            {
                "box": {
                    "id": "obj-286",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1375.0,
                        128.0,
                        22.0
                    ],
                    "text": "r qmw.noise.control"
                }
            },
            {
                "box": {
                    "id": "obj-287",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1920.0,
                        1375.0,
                        720.0,
                        22.0
                    ],
                    "text": "route amount floor color decay_ms spectral_amount spectral_gain base_hz q"
                }
            },
            {
                "box": {
                    "id": "obj-288",
                    "maxclass": "comment",
                    "patching_rect": [
                        615.0,
                        647.0,
                        78.0,
                        18.0
                    ],
                    "text": "GRAIN DRY",
                    "presentation": 1,
                    "presentation_rect": [
                        615.0,
                        647.0,
                        78.0,
                        18.0
                    ],
                    "fontface": 1,
                    "fontsize": 8.0
                }
            },
            {
                "box": {
                    "id": "obj-289",
                    "maxclass": "flonum",
                    "patching_rect": [
                        615.0,
                        668.0,
                        72.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        615.0,
                        668.0,
                        72.0,
                        22.0
                    ],
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "parameter_enable": 0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-290",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2410.0,
                        900.0,
                        92.0,
                        22.0
                    ],
                    "text": "loadmess 0.5"
                }
            },
            {
                "box": {
                    "id": "obj-291",
                    "maxclass": "message",
                    "patching_rect": [
                        2410.0,
                        935.0,
                        55.0,
                        22.0
                    ],
                    "text": "$1 30"
                }
            },
            {
                "box": {
                    "id": "obj-292",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2410.0,
                        970.0,
                        45.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-293",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        855.0,
                        45.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-294",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        895.0,
                        142.0,
                        22.0
                    ],
                    "text": "receive~ qmw_qubit_0"
                }
            },
            {
                "box": {
                    "id": "obj-295",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        930.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-296",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1885.0,
                        855.0,
                        45.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-297",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1935.0,
                        895.0,
                        142.0,
                        22.0
                    ],
                    "text": "receive~ qmw_qubit_1"
                }
            },
            {
                "box": {
                    "id": "obj-298",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1935.0,
                        930.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-299",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1990.0,
                        855.0,
                        45.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-300",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2090.0,
                        895.0,
                        142.0,
                        22.0
                    ],
                    "text": "receive~ qmw_qubit_2"
                }
            },
            {
                "box": {
                    "id": "obj-301",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2090.0,
                        930.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-302",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2095.0,
                        855.0,
                        45.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-303",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2245.0,
                        895.0,
                        142.0,
                        22.0
                    ],
                    "text": "receive~ qmw_qubit_3"
                }
            },
            {
                "box": {
                    "id": "obj-304",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2245.0,
                        930.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-305",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        970.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-306",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1870.0,
                        970.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-307",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1825.0,
                        1005.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-308",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1870.0,
                        1005.0,
                        48.0,
                        22.0
                    ],
                    "text": "*~ 0.5"
                }
            },
            {
                "box": {
                    "id": "obj-309",
                    "maxclass": "message",
                    "patching_rect": [
                        2070.0,
                        900.0,
                        55.0,
                        22.0
                    ],
                    "text": "$1 30"
                }
            },
            {
                "box": {
                    "id": "obj-310",
                    "maxclass": "message",
                    "patching_rect": [
                        2140.0,
                        900.0,
                        55.0,
                        22.0
                    ],
                    "text": "$1 30"
                }
            },
            {
                "box": {
                    "id": "obj-311",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2070.0,
                        935.0,
                        45.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-312",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2140.0,
                        935.0,
                        45.0,
                        22.0
                    ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "id": "obj-313",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1975.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-314",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2025.0,
                        1005.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-315",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2000.0,
                        1010.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-316",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2210.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-317",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2250.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-318",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2290.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-319",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2330.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-320",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2370.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-321",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2395.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-322",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2435.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-323",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2475.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-324",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2515.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "*~"
                }
            },
            {
                "box": {
                    "id": "obj-325",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2555.0,
                        975.0,
                        32.0,
                        22.0
                    ],
                    "text": "+~"
                }
            },
            {
                "box": {
                    "id": "obj-326",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1080.0,
                        95.0,
                        22.0
                    ],
                    "text": "r qmw.osc.raw"
                }
            },
            {
                "box": {
                    "id": "obj-327",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1890.0,
                        1080.0,
                        98.0,
                        22.0
                    ],
                    "text": "OSC-route /qmw"
                }
            },
            {
                "box": {
                    "id": "obj-328",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2005.0,
                        1060.0,
                        145.0,
                        22.0
                    ],
                    "text": "OSC-route /density_field"
                }
            },
            {
                "box": {
                    "id": "obj-329",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2165.0,
                        1030.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-330",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2165.0,
                        1060.0,
                        168.0,
                        22.0
                    ],
                    "text": "OSC-route /entropy /magnitude"
                }
            },
            {
                "box": {
                    "id": "obj-331",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2290.0,
                        1060.0,
                        105.0,
                        22.0
                    ],
                    "text": "prepend entropy"
                }
            },
            {
                "box": {
                    "id": "obj-332",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2410.0,
                        1060.0,
                        125.0,
                        22.0
                    ],
                    "text": "prepend magnitudes"
                }
            },
            {
                "box": {
                    "id": "obj-333",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2005.0,
                        1100.0,
                        112.0,
                        22.0
                    ],
                    "text": "OSC-route /event"
                }
            },
            {
                "box": {
                    "id": "obj-334",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2130.0,
                        1130.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-335",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2130.0,
                        1100.0,
                        140.0,
                        22.0
                    ],
                    "text": "OSC-route /resonance"
                }
            },
            {
                "box": {
                    "id": "obj-336",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2285.0,
                        1100.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend external"
                }
            },
            {
                "box": {
                    "id": "obj-337",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2005.0,
                        1165.0,
                        112.0,
                        22.0
                    ],
                    "text": "OSC-route /grain"
                }
            },
            {
                "box": {
                    "id": "obj-338",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2130.0,
                        1165.0,
                        205.0,
                        22.0
                    ],
                    "text": "OSC-route /rates /quantum_state"
                }
            },
            {
                "box": {
                    "id": "obj-339",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2255.0,
                        1165.0,
                        118.0,
                        22.0
                    ],
                    "text": "prepend osc_rates"
                }
            },
            {
                "box": {
                    "id": "obj-340",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2385.0,
                        1165.0,
                        148.0,
                        22.0
                    ],
                    "text": "prepend quantum_state"
                }
            },
            {
                "box": {
                    "id": "obj-341",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1140.0,
                        128.0,
                        22.0
                    ],
                    "text": "r qmw.grain.control"
                }
            },
            {
                "box": {
                    "id": "obj-342",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1920.0,
                        1140.0,
                        710.0,
                        22.0
                    ],
                    "text": "route enable mode source rates probability duration attack randomness level drone_mix trigger seed grain_dry quantum_threshold refractory quantum_step groove cell_threshold coherence_duration"
                }
            },
            {
                "box": {
                    "id": "obj-343",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1180.0,
                        128.0,
                        22.0
                    ],
                    "text": "prepend local_rates"
                }
            },
            {
                "box": {
                    "id": "obj-344",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1780.0,
                        1180.0,
                        104.0,
                        22.0
                    ],
                    "text": "prepend duration"
                }
            },
            {
                "box": {
                    "id": "obj-345",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1892.0,
                        1180.0,
                        104.0,
                        22.0
                    ],
                    "text": "prepend attack"
                }
            },
            {
                "box": {
                    "id": "obj-346",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2004.0,
                        1180.0,
                        104.0,
                        22.0
                    ],
                    "text": "prepend randomness"
                }
            },
            {
                "box": {
                    "id": "obj-347",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2116.0,
                        1180.0,
                        104.0,
                        22.0
                    ],
                    "text": "prepend level"
                }
            },
            {
                "box": {
                    "id": "obj-348",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2228.0,
                        1180.0,
                        104.0,
                        22.0
                    ],
                    "text": "prepend drone_mix"
                }
            },
            {
                "box": {
                    "id": "obj-349",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2340.0,
                        1180.0,
                        104.0,
                        22.0
                    ],
                    "text": "prepend trigger"
                }
            },
            {
                "box": {
                    "id": "obj-350",
                    "maxclass": "newobj",
                    "patching_rect": [
                        2452.0,
                        1180.0,
                        104.0,
                        22.0
                    ],
                    "text": "prepend seed"
                }
            },
            {
                "box": {
                    "id": "obj-351",
                    "maxclass": "newobj",
                    "text": "expr min(1., max(0., $f1 / 4.))",
                    "patching_rect": [
                        1400.0,
                        440.0,
                        190.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-352",
                    "maxclass": "newobj",
                    "text": "expr min(1., max(0., $f1 / 15.))",
                    "patching_rect": [
                        1595.0,
                        440.0,
                        195.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "source": [
                        "obj-4",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-6",
                        1
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-7",
                        1
                    ],
                    "destination": [
                        "obj-11",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-10",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-11",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-12",
                        0
                    ],
                    "destination": [
                        "obj-6",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-13",
                        0
                    ],
                    "destination": [
                        "obj-7",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-14",
                        0
                    ],
                    "destination": [
                        "obj-16",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-16",
                        0
                    ],
                    "destination": [
                        "obj-17",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-17",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-12",
                        0
                    ],
                    "destination": [
                        "obj-14",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-22",
                        0
                    ],
                    "destination": [
                        "obj-18",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-18",
                        0
                    ],
                    "destination": [
                        "obj-20",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-20",
                        0
                    ],
                    "destination": [
                        "obj-21",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-21",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-25",
                        0
                    ],
                    "destination": [
                        "obj-27",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-27",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-23",
                        0
                    ],
                    "destination": [
                        "obj-28",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-28",
                        0
                    ],
                    "destination": [
                        "obj-29",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-29",
                        0
                    ],
                    "destination": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-30",
                        0
                    ],
                    "destination": [
                        "obj-31",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-31",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-4",
                        1
                    ],
                    "destination": [
                        "obj-32",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-35",
                        0
                    ],
                    "destination": [
                        "obj-34",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-34",
                        0
                    ],
                    "destination": [
                        "obj-37",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-37",
                        0
                    ],
                    "destination": [
                        "obj-38",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-38",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-39",
                        0
                    ],
                    "destination": [
                        "obj-41",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-40",
                        0
                    ],
                    "destination": [
                        "obj-42",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-41",
                        0
                    ],
                    "destination": [
                        "obj-43",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-42",
                        0
                    ],
                    "destination": [
                        "obj-43",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-39",
                        0
                    ],
                    "destination": [
                        "obj-44",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-40",
                        0
                    ],
                    "destination": [
                        "obj-45",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-5",
                        0
                    ],
                    "destination": [
                        "obj-48",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-5",
                        1
                    ],
                    "destination": [
                        "obj-49",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-48",
                        0
                    ],
                    "destination": [
                        "obj-50",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-49",
                        0
                    ],
                    "destination": [
                        "obj-51",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-39",
                        0
                    ],
                    "destination": [
                        "obj-52",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-40",
                        0
                    ],
                    "destination": [
                        "obj-53",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-50",
                        0
                    ],
                    "destination": [
                        "obj-54",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-51",
                        0
                    ],
                    "destination": [
                        "obj-55",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-54",
                        0
                    ],
                    "destination": [
                        "obj-56",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-55",
                        0
                    ],
                    "destination": [
                        "obj-57",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-67",
                        0
                    ],
                    "destination": [
                        "obj-58",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-58",
                        0
                    ],
                    "destination": [
                        "obj-60",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-60",
                        0
                    ],
                    "destination": [
                        "obj-61",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-61",
                        0
                    ],
                    "destination": [
                        "obj-62",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-61",
                        1
                    ],
                    "destination": [
                        "obj-64",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-62",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-64",
                        0
                    ],
                    "destination": [
                        "obj-65",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-65",
                        0
                    ],
                    "destination": [
                        "obj-66",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-63",
                        0
                    ],
                    "destination": [
                        "obj-50",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-63",
                        0
                    ],
                    "destination": [
                        "obj-51",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-66",
                        0
                    ],
                    "destination": [
                        "obj-52",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-66",
                        0
                    ],
                    "destination": [
                        "obj-53",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-73",
                        0
                    ],
                    "destination": [
                        "obj-68",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-68",
                        0
                    ],
                    "destination": [
                        "obj-70",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-70",
                        0
                    ],
                    "destination": [
                        "obj-71",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-71",
                        0
                    ],
                    "destination": [
                        "obj-72",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-72",
                        0
                    ],
                    "destination": [
                        "obj-48",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-72",
                        0
                    ],
                    "destination": [
                        "obj-49",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-78",
                        0
                    ],
                    "destination": [
                        "obj-74",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-74",
                        0
                    ],
                    "destination": [
                        "obj-76",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-76",
                        0
                    ],
                    "destination": [
                        "obj-77",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-77",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-81",
                        0
                    ],
                    "destination": [
                        "obj-79",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-79",
                        0
                    ],
                    "destination": [
                        "obj-82",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-82",
                        1
                    ],
                    "destination": [
                        "obj-83",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-91",
                        0
                    ],
                    "destination": [
                        "obj-84",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-84",
                        0
                    ],
                    "destination": [
                        "obj-86",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-86",
                        0
                    ],
                    "destination": [
                        "obj-87",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-87",
                        0
                    ],
                    "destination": [
                        "obj-89",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-88",
                        0
                    ],
                    "destination": [
                        "obj-89",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-83",
                        0
                    ],
                    "destination": [
                        "obj-89",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-82",
                        0
                    ],
                    "destination": [
                        "obj-87",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-82",
                        0
                    ],
                    "destination": [
                        "obj-88",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-89",
                        0
                    ],
                    "destination": [
                        "obj-90",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-90",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-99",
                        0
                    ],
                    "destination": [
                        "obj-92",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-92",
                        0
                    ],
                    "destination": [
                        "obj-94",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-94",
                        0
                    ],
                    "destination": [
                        "obj-95",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-95",
                        0
                    ],
                    "destination": [
                        "obj-97",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-96",
                        0
                    ],
                    "destination": [
                        "obj-97",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-83",
                        0
                    ],
                    "destination": [
                        "obj-97",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-82",
                        0
                    ],
                    "destination": [
                        "obj-95",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-82",
                        0
                    ],
                    "destination": [
                        "obj-96",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-97",
                        0
                    ],
                    "destination": [
                        "obj-98",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-98",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-107",
                        0
                    ],
                    "destination": [
                        "obj-100",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-100",
                        0
                    ],
                    "destination": [
                        "obj-102",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-102",
                        0
                    ],
                    "destination": [
                        "obj-103",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-103",
                        0
                    ],
                    "destination": [
                        "obj-105",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-104",
                        0
                    ],
                    "destination": [
                        "obj-105",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-83",
                        0
                    ],
                    "destination": [
                        "obj-105",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-82",
                        0
                    ],
                    "destination": [
                        "obj-103",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-82",
                        0
                    ],
                    "destination": [
                        "obj-104",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-105",
                        0
                    ],
                    "destination": [
                        "obj-106",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-106",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-111",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-108",
                        0
                    ],
                    "destination": [
                        "obj-110",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-110",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-115",
                        0
                    ],
                    "destination": [
                        "obj-112",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-112",
                        0
                    ],
                    "destination": [
                        "obj-114",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-114",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-119",
                        0
                    ],
                    "destination": [
                        "obj-116",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-116",
                        0
                    ],
                    "destination": [
                        "obj-118",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-118",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-48",
                        0
                    ],
                    "destination": [
                        "obj-120",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-49",
                        0
                    ],
                    "destination": [
                        "obj-121",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-56",
                        0
                    ],
                    "destination": [
                        "obj-124",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-57",
                        0
                    ],
                    "destination": [
                        "obj-125",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-56",
                        0
                    ],
                    "destination": [
                        "obj-128",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-57",
                        0
                    ],
                    "destination": [
                        "obj-129",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-56",
                        0
                    ],
                    "destination": [
                        "obj-130",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-57",
                        0
                    ],
                    "destination": [
                        "obj-130",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-133",
                        0
                    ],
                    "destination": [
                        "obj-134",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-134",
                        0
                    ],
                    "destination": [
                        "obj-135",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-135",
                        0
                    ],
                    "destination": [
                        "obj-136",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-133",
                        0
                    ],
                    "destination": [
                        "obj-137",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-137",
                        0
                    ],
                    "destination": [
                        "obj-138",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-138",
                        0
                    ],
                    "destination": [
                        "obj-139",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-139",
                        0
                    ],
                    "destination": [
                        "obj-140",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-140",
                        0
                    ],
                    "destination": [
                        "obj-88",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-139",
                        1
                    ],
                    "destination": [
                        "obj-141",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-141",
                        0
                    ],
                    "destination": [
                        "obj-96",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-139",
                        2
                    ],
                    "destination": [
                        "obj-142",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-142",
                        0
                    ],
                    "destination": [
                        "obj-104",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-143",
                        0
                    ],
                    "destination": [
                        "obj-144",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        0
                    ],
                    "destination": [
                        "obj-87",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        1
                    ],
                    "destination": [
                        "obj-95",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        2
                    ],
                    "destination": [
                        "obj-103",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        3
                    ],
                    "destination": [
                        "obj-79",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        4
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        5
                    ],
                    "destination": [
                        "obj-112",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        6
                    ],
                    "destination": [
                        "obj-112",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        7
                    ],
                    "destination": [
                        "obj-116",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        8
                    ],
                    "destination": [
                        "obj-145",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        9
                    ],
                    "destination": [
                        "obj-146",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-145",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-146",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        10
                    ],
                    "destination": [
                        "obj-147",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-147",
                        0
                    ],
                    "destination": [
                        "obj-74",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        11
                    ],
                    "destination": [
                        "obj-148",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-148",
                        0
                    ],
                    "destination": [
                        "obj-58",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        12
                    ],
                    "destination": [
                        "obj-149",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-149",
                        0
                    ],
                    "destination": [
                        "obj-68",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        13
                    ],
                    "destination": [
                        "obj-150",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-150",
                        0
                    ],
                    "destination": [
                        "obj-14",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        14
                    ],
                    "destination": [
                        "obj-151",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-151",
                        0
                    ],
                    "destination": [
                        "obj-18",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        15
                    ],
                    "destination": [
                        "obj-23",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        16
                    ],
                    "destination": [
                        "obj-25",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        17
                    ],
                    "destination": [
                        "obj-152",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-152",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        18
                    ],
                    "destination": [
                        "obj-153",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-153",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-144",
                        19
                    ],
                    "destination": [
                        "obj-154",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-154",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-136",
                        0
                    ],
                    "destination": [
                        "obj-155",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-155",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-136",
                        1
                    ],
                    "destination": [
                        "obj-156",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-156",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-157",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-136",
                        3
                    ],
                    "destination": [
                        "obj-158",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-158",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-159",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-160",
                        0
                    ],
                    "destination": [
                        "obj-161",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-161",
                        0
                    ],
                    "destination": [
                        "obj-162",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-162",
                        0
                    ],
                    "destination": [
                        "obj-163",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        0
                    ],
                    "destination": [
                        "obj-164",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-164",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        1
                    ],
                    "destination": [
                        "obj-165",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-165",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        2
                    ],
                    "destination": [
                        "obj-166",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-166",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        3
                    ],
                    "destination": [
                        "obj-167",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-167",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        4
                    ],
                    "destination": [
                        "obj-168",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-168",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        5
                    ],
                    "destination": [
                        "obj-169",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-169",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        6
                    ],
                    "destination": [
                        "obj-170",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-170",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        7
                    ],
                    "destination": [
                        "obj-171",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-171",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-162",
                        1
                    ],
                    "destination": [
                        "obj-172",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-172",
                        0
                    ],
                    "destination": [
                        "obj-173",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-173",
                        0
                    ],
                    "destination": [
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-183",
                        0
                    ],
                    "destination": [
                        "obj-177",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-177",
                        0
                    ],
                    "destination": [
                        "obj-181",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-181",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-184",
                        0
                    ],
                    "destination": [
                        "obj-178",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-178",
                        0
                    ],
                    "destination": [
                        "obj-182",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-182",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-187",
                        0
                    ],
                    "destination": [
                        "obj-186",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-187",
                        0
                    ],
                    "destination": [
                        "obj-189",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-187",
                        0
                    ],
                    "destination": [
                        "obj-188",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-186",
                        0
                    ],
                    "destination": [
                        "obj-189",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-186",
                        0
                    ],
                    "destination": [
                        "obj-188",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-188",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-193",
                        0
                    ],
                    "destination": [
                        "obj-191",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-191",
                        0
                    ],
                    "destination": [
                        "obj-192",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-192",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-197",
                        0
                    ],
                    "destination": [
                        "obj-195",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-195",
                        0
                    ],
                    "destination": [
                        "obj-196",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-196",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-201",
                        0
                    ],
                    "destination": [
                        "obj-199",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-199",
                        0
                    ],
                    "destination": [
                        "obj-200",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-200",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-205",
                        0
                    ],
                    "destination": [
                        "obj-203",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-203",
                        0
                    ],
                    "destination": [
                        "obj-204",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-204",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-209",
                        0
                    ],
                    "destination": [
                        "obj-207",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-207",
                        0
                    ],
                    "destination": [
                        "obj-208",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-208",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-213",
                        0
                    ],
                    "destination": [
                        "obj-211",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-211",
                        0
                    ],
                    "destination": [
                        "obj-212",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-212",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-217",
                        0
                    ],
                    "destination": [
                        "obj-215",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-215",
                        0
                    ],
                    "destination": [
                        "obj-216",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-216",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-221",
                        0
                    ],
                    "destination": [
                        "obj-219",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-219",
                        0
                    ],
                    "destination": [
                        "obj-220",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-220",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-225",
                        0
                    ],
                    "destination": [
                        "obj-223",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-223",
                        0
                    ],
                    "destination": [
                        "obj-224",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-224",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-229",
                        0
                    ],
                    "destination": [
                        "obj-227",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-227",
                        0
                    ],
                    "destination": [
                        "obj-228",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-228",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-233",
                        0
                    ],
                    "destination": [
                        "obj-231",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-231",
                        0
                    ],
                    "destination": [
                        "obj-232",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-232",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-237",
                        0
                    ],
                    "destination": [
                        "obj-235",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-235",
                        0
                    ],
                    "destination": [
                        "obj-236",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-236",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-241",
                        0
                    ],
                    "destination": [
                        "obj-239",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-239",
                        0
                    ],
                    "destination": [
                        "obj-240",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-240",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-247",
                        0
                    ],
                    "destination": [
                        "obj-243",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-247",
                        0
                    ],
                    "destination": [
                        "obj-246",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-243",
                        0
                    ],
                    "destination": [
                        "obj-246",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-246",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-249",
                        0
                    ],
                    "destination": [
                        "obj-245",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-249",
                        0
                    ],
                    "destination": [
                        "obj-248",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-245",
                        0
                    ],
                    "destination": [
                        "obj-248",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-248",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-250",
                        0
                    ],
                    "destination": [
                        "obj-252",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-252",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-176",
                        6
                    ],
                    "destination": [
                        "obj-253",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-257",
                        0
                    ],
                    "destination": [
                        "obj-255",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-257",
                        0
                    ],
                    "destination": [
                        "obj-256",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-255",
                        0
                    ],
                    "destination": [
                        "obj-256",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-256",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-261",
                        0
                    ],
                    "destination": [
                        "obj-259",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-261",
                        0
                    ],
                    "destination": [
                        "obj-260",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-259",
                        0
                    ],
                    "destination": [
                        "obj-260",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-260",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-265",
                        0
                    ],
                    "destination": [
                        "obj-263",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-265",
                        0
                    ],
                    "destination": [
                        "obj-264",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-263",
                        0
                    ],
                    "destination": [
                        "obj-264",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-264",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-269",
                        0
                    ],
                    "destination": [
                        "obj-267",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-269",
                        0
                    ],
                    "destination": [
                        "obj-268",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-267",
                        0
                    ],
                    "destination": [
                        "obj-268",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-268",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-273",
                        0
                    ],
                    "destination": [
                        "obj-271",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-273",
                        0
                    ],
                    "destination": [
                        "obj-272",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-271",
                        0
                    ],
                    "destination": [
                        "obj-272",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-272",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-277",
                        0
                    ],
                    "destination": [
                        "obj-275",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-277",
                        0
                    ],
                    "destination": [
                        "obj-276",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-275",
                        0
                    ],
                    "destination": [
                        "obj-276",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-276",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-281",
                        0
                    ],
                    "destination": [
                        "obj-279",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-281",
                        0
                    ],
                    "destination": [
                        "obj-280",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-279",
                        0
                    ],
                    "destination": [
                        "obj-280",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-280",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-285",
                        0
                    ],
                    "destination": [
                        "obj-283",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-285",
                        0
                    ],
                    "destination": [
                        "obj-284",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-283",
                        0
                    ],
                    "destination": [
                        "obj-284",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-284",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-286",
                        0
                    ],
                    "destination": [
                        "obj-287",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        0
                    ],
                    "destination": [
                        "obj-255",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        1
                    ],
                    "destination": [
                        "obj-259",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        2
                    ],
                    "destination": [
                        "obj-263",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        3
                    ],
                    "destination": [
                        "obj-267",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        4
                    ],
                    "destination": [
                        "obj-271",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        5
                    ],
                    "destination": [
                        "obj-275",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        6
                    ],
                    "destination": [
                        "obj-279",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-287",
                        7
                    ],
                    "destination": [
                        "obj-283",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-290",
                        0
                    ],
                    "destination": [
                        "obj-289",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-290",
                        0
                    ],
                    "destination": [
                        "obj-291",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-289",
                        0
                    ],
                    "destination": [
                        "obj-291",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-291",
                        0
                    ],
                    "destination": [
                        "obj-292",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-176",
                        0
                    ],
                    "destination": [
                        "obj-293",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-294",
                        0
                    ],
                    "destination": [
                        "obj-295",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-293",
                        0
                    ],
                    "destination": [
                        "obj-295",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-176",
                        1
                    ],
                    "destination": [
                        "obj-296",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-297",
                        0
                    ],
                    "destination": [
                        "obj-298",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-296",
                        0
                    ],
                    "destination": [
                        "obj-298",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-176",
                        2
                    ],
                    "destination": [
                        "obj-299",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-300",
                        0
                    ],
                    "destination": [
                        "obj-301",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-299",
                        0
                    ],
                    "destination": [
                        "obj-301",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-176",
                        3
                    ],
                    "destination": [
                        "obj-302",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-303",
                        0
                    ],
                    "destination": [
                        "obj-304",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-302",
                        0
                    ],
                    "destination": [
                        "obj-304",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-295",
                        0
                    ],
                    "destination": [
                        "obj-305",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-301",
                        0
                    ],
                    "destination": [
                        "obj-305",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-298",
                        0
                    ],
                    "destination": [
                        "obj-306",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-304",
                        0
                    ],
                    "destination": [
                        "obj-306",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-305",
                        0
                    ],
                    "destination": [
                        "obj-307",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-306",
                        0
                    ],
                    "destination": [
                        "obj-307",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-307",
                        0
                    ],
                    "destination": [
                        "obj-308",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-176",
                        4
                    ],
                    "destination": [
                        "obj-309",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-176",
                        5
                    ],
                    "destination": [
                        "obj-310",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-309",
                        0
                    ],
                    "destination": [
                        "obj-311",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-310",
                        0
                    ],
                    "destination": [
                        "obj-312",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-43",
                        0
                    ],
                    "destination": [
                        "obj-313",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-311",
                        0
                    ],
                    "destination": [
                        "obj-313",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-308",
                        0
                    ],
                    "destination": [
                        "obj-314",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-312",
                        0
                    ],
                    "destination": [
                        "obj-314",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-313",
                        0
                    ],
                    "destination": [
                        "obj-315",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-314",
                        0
                    ],
                    "destination": [
                        "obj-315",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-315",
                        0
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-52",
                        0
                    ],
                    "destination": [
                        "obj-316",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-311",
                        0
                    ],
                    "destination": [
                        "obj-316",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-305",
                        0
                    ],
                    "destination": [
                        "obj-317",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-312",
                        0
                    ],
                    "destination": [
                        "obj-317",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-317",
                        0
                    ],
                    "destination": [
                        "obj-318",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-292",
                        0
                    ],
                    "destination": [
                        "obj-318",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-318",
                        0
                    ],
                    "destination": [
                        "obj-319",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-66",
                        0
                    ],
                    "destination": [
                        "obj-319",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-316",
                        0
                    ],
                    "destination": [
                        "obj-320",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-319",
                        0
                    ],
                    "destination": [
                        "obj-320",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-320",
                        0
                    ],
                    "destination": [
                        "obj-54",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-53",
                        0
                    ],
                    "destination": [
                        "obj-321",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-311",
                        0
                    ],
                    "destination": [
                        "obj-321",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-306",
                        0
                    ],
                    "destination": [
                        "obj-322",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-312",
                        0
                    ],
                    "destination": [
                        "obj-322",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-322",
                        0
                    ],
                    "destination": [
                        "obj-323",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-292",
                        0
                    ],
                    "destination": [
                        "obj-323",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-323",
                        0
                    ],
                    "destination": [
                        "obj-324",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-66",
                        0
                    ],
                    "destination": [
                        "obj-324",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-321",
                        0
                    ],
                    "destination": [
                        "obj-325",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-324",
                        0
                    ],
                    "destination": [
                        "obj-325",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-325",
                        0
                    ],
                    "destination": [
                        "obj-55",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-326",
                        0
                    ],
                    "destination": [
                        "obj-327",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-327",
                        0
                    ],
                    "destination": [
                        "obj-328",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-328",
                        0
                    ],
                    "destination": [
                        "obj-329",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-329",
                        4
                    ],
                    "destination": [
                        "obj-330",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-330",
                        0
                    ],
                    "destination": [
                        "obj-331",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-331",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-330",
                        1
                    ],
                    "destination": [
                        "obj-332",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-332",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-327",
                        0
                    ],
                    "destination": [
                        "obj-333",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-333",
                        0
                    ],
                    "destination": [
                        "obj-334",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-334",
                        4
                    ],
                    "destination": [
                        "obj-335",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-335",
                        0
                    ],
                    "destination": [
                        "obj-336",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-336",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-327",
                        0
                    ],
                    "destination": [
                        "obj-337",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-337",
                        0
                    ],
                    "destination": [
                        "obj-338",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-338",
                        0
                    ],
                    "destination": [
                        "obj-339",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-339",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-338",
                        1
                    ],
                    "destination": [
                        "obj-340",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-340",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-341",
                        0
                    ],
                    "destination": [
                        "obj-342",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        0
                    ],
                    "destination": [
                        "obj-186",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        1
                    ],
                    "destination": [
                        "obj-177",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        2
                    ],
                    "destination": [
                        "obj-178",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        3
                    ],
                    "destination": [
                        "obj-343",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-343",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        4
                    ],
                    "destination": [
                        "obj-207",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        5
                    ],
                    "destination": [
                        "obj-344",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-344",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        6
                    ],
                    "destination": [
                        "obj-345",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-345",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        7
                    ],
                    "destination": [
                        "obj-346",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-346",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        8
                    ],
                    "destination": [
                        "obj-347",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-347",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        9
                    ],
                    "destination": [
                        "obj-348",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-348",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        10
                    ],
                    "destination": [
                        "obj-349",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-349",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        11
                    ],
                    "destination": [
                        "obj-350",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-350",
                        0
                    ],
                    "destination": [
                        "obj-176",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        12
                    ],
                    "destination": [
                        "obj-289",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        13
                    ],
                    "destination": [
                        "obj-227",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        14
                    ],
                    "destination": [
                        "obj-235",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        15
                    ],
                    "destination": [
                        "obj-231",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        16
                    ],
                    "destination": [
                        "obj-239",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        17
                    ],
                    "destination": [
                        "obj-223",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-342",
                        18
                    ],
                    "destination": [
                        "obj-219",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-136",
                        2
                    ],
                    "destination": [
                        "obj-351",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-351",
                        0
                    ],
                    "destination": [
                        "obj-157",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-136",
                        4
                    ],
                    "destination": [
                        "obj-352",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-352",
                        0
                    ],
                    "destination": [
                        "obj-159",
                        0
                    ]
                }
            }
        ],
        "dependency_cache": [
            {
                "name": "OSC-route.mxo",
                "type": "iLaX",
                "implicit": 1
            },
            {
                "name": "qmw_implicit_surface_controller_v1.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": "..",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qmw_resonance_grain_scheduler_v3.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": "..",
                "type": "TEXT",
                "implicit": 1
            }
        ],
        "autosave": 0
    }
}
