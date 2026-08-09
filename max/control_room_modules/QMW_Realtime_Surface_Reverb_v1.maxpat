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
            1720.0,
            650.0
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
                    "text": "QMW REALTIME IMPLICIT SURFACE REVERB v1",
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
                    "text": "20 field probes \u2192 compact 8-line Gen~ FDN \u00b7 no mesh, WAV render, or IR reload",
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
                    "code": "// qmw_compact_realtime_surface_fdn_v1.genexpr\n// Eight-line geometry-modulated FDN; all twenty implicit-surface probes are used.\n\nParam size(0.45);\nParam decay(0.82);\nParam diffusion(0.78);\nParam absorb(0.32);\nParam width(0.90);\nParam freeze(0);\nParam input_gain(0.65);\nParam output_gain(0.72);\nParam surface_depth(0.35);\nParam geometry_morph(0);\nParam geometry_depth(0.55);\nParam harmonicity(0.25);\nParam harmonic_span(0.22);\nParam topology(0.80);\nParam pauli_depth(0.16);\nParam harmonic_resonance(0.5);\nParam spectral_tilt(0);\nParam modal_warp(0);\nParam harmonic_slew_ms(120);\nParam mw1(1); Param mw2(1); Param mw3(1); Param mw4(1);\nParam mw5(1); Param mw6(1); Param mw7(1); Param mw8(1);\nParam rot_x(0);\nParam rot_y(0);\nParam rot_z(0);\nParam rotation_slew_ms(100);\nParam morph_slew_ms(500);\nParam geometry_morph_slew_ms(500);\nParam surface_slew_ms(250);\nParam diffusion_slew_ms(100);\nParam geometry_depth_slew_ms(100);\nParam solid_a(1);\nParam solid_b(2);\n\nParam sf1(0);  Param sf2(0);  Param sf3(0);  Param sf4(0);\nParam sf5(0);  Param sf6(0);  Param sf7(0);  Param sf8(0);\nParam sf9(0);  Param sf10(0); Param sf11(0); Param sf12(0);\nParam sf13(0); Param sf14(0); Param sf15(0); Param sf16(0);\nParam sf17(0); Param sf18(0); Param sf19(0); Param sf20(0);\n\nParam qm0(1); Param qm1(0); Param qm2(0); Param qm3(0);\nParam qm4(0); Param qm5(0); Param qm6(0); Param qm7(0);\nParam qh0(1); Param qh1(2); Param qh2(3); Param qh3(4);\nParam qh4(5); Param qh5(6); Param qh6(7); Param qh7(8);\n\nDelay dl1(192000); Delay dl2(192000); Delay dl3(192000); Delay dl4(192000);\nDelay dl5(192000); Delay dl6(192000); Delay dl7(192000); Delay dl8(192000);\n\nHistory lp1(0); History lp2(0); History lp3(0); History lp4(0);\nHistory lp5(0); History lp6(0); History lp7(0); History lp8(0);\nHistory shape1_z(0); History shape2_z(0); History shape3_z(0); History shape4_z(0);\nHistory shape5_z(0); History shape6_z(0); History shape7_z(0); History shape8_z(0);\nHistory rot_x_z(0); History rot_y_z(0); History rot_z_z(0);\nHistory morph_z(0); History surface_depth_z(0.35); History diffusion_z(0.78);\nHistory resonance_z(0.5); History tilt_z(0); History warp_z(0);\nHistory mw1_z(1); History mw2_z(1); History mw3_z(1); History mw4_z(1);\nHistory mw5_z(1); History mw6_z(1); History mw7_z(1); History mw8_z(1);\nHistory dc_l_x(0); History dc_l_y(0);\nHistory dc_r_x(0); History dc_r_y(0);\n\nsr = samplerate;\npi2 = 6.28318530718;\ns = clamp(size, 0, 1);\nsize_scale = pow(2, (s * 3) - 1.5);\nsurface = clamp(surface_depth, 0, 0.85);\n\n// Fold twenty probes into eight independent geometry lanes.\nshape1_target = (sf1 + sf9 + sf17) * 0.333333333;\nshape2_target = (sf2 + sf10 + sf18) * 0.333333333;\nshape3_target = (sf3 + sf11 + sf19) * 0.333333333;\nshape4_target = (sf4 + sf12 + sf20) * 0.333333333;\nshape5_target = (sf5 + sf13) * 0.5;\nshape6_target = (sf6 + sf14) * 0.5;\nshape7_target = (sf7 + sf15) * 0.5;\nshape8_target = (sf8 + sf16) * 0.5;\n\nsurface_seconds = max(surface_slew_ms, 0.1) * 0.001;\nsurface_coeff = 1 - exp(-1 / max(sr * surface_seconds, 1));\nshape1_z = shape1_z + surface_coeff * (shape1_target - shape1_z);\nshape2_z = shape2_z + surface_coeff * (shape2_target - shape2_z);\nshape3_z = shape3_z + surface_coeff * (shape3_target - shape3_z);\nshape4_z = shape4_z + surface_coeff * (shape4_target - shape4_z);\nshape5_z = shape5_z + surface_coeff * (shape5_target - shape5_z);\nshape6_z = shape6_z + surface_coeff * (shape6_target - shape6_z);\nshape7_z = shape7_z + surface_coeff * (shape7_target - shape7_z);\nshape8_z = shape8_z + surface_coeff * (shape8_target - shape8_z);\n\ndepth_seconds = max(geometry_depth_slew_ms, 0.1) * 0.001;\ndepth_coeff = 1 - exp(-1 / max(sr * depth_seconds, 1));\nsurface_depth_z = surface_depth_z + depth_coeff * (surface - surface_depth_z);\n\nmorph_seconds = max(geometry_morph_slew_ms, 0.1) * 0.001;\nmorph_coeff = 1 - exp(-1 / max(sr * morph_seconds, 1));\nmorph_z = morph_z + morph_coeff * (clamp(geometry_morph, 0, 1) - morph_z);\n\nrotation_seconds = max(rotation_slew_ms, 0.1) * 0.001;\nrotation_coeff = 1 - exp(-1 / max(sr * rotation_seconds, 1));\nrot_x_delta = rot_x - rot_x_z;\nrot_y_delta = rot_y - rot_y_z;\nrot_z_delta = rot_z - rot_z_z;\nrot_x_delta = rot_x_delta - floor(rot_x_delta + 0.5);\nrot_y_delta = rot_y_delta - floor(rot_y_delta + 0.5);\nrot_z_delta = rot_z_delta - floor(rot_z_delta + 0.5);\nrot_x_z = rot_x_z + rotation_coeff * rot_x_delta;\nrot_y_z = rot_y_z + rotation_coeff * rot_y_delta;\nrot_z_z = rot_z_z + rotation_coeff * rot_z_delta;\n\nharmonic_seconds = max(harmonic_slew_ms, 0.1) * 0.001;\nharmonic_coeff = 1 - exp(-1 / max(sr * harmonic_seconds, 1));\nresonance_z = resonance_z + harmonic_coeff * (clamp(harmonic_resonance, 0, 1) - resonance_z);\ntilt_z = tilt_z + harmonic_coeff * (clamp(spectral_tilt, -1, 1) - tilt_z);\nwarp_z = warp_z + harmonic_coeff * (clamp(modal_warp, -1, 1) - warp_z);\nmw1_z = mw1_z + harmonic_coeff * (clamp(mw1, 0.35, 1.65) - mw1_z);\nmw2_z = mw2_z + harmonic_coeff * (clamp(mw2, 0.35, 1.65) - mw2_z);\nmw3_z = mw3_z + harmonic_coeff * (clamp(mw3, 0.35, 1.65) - mw3_z);\nmw4_z = mw4_z + harmonic_coeff * (clamp(mw4, 0.35, 1.65) - mw4_z);\nmw5_z = mw5_z + harmonic_coeff * (clamp(mw5, 0.35, 1.65) - mw5_z);\nmw6_z = mw6_z + harmonic_coeff * (clamp(mw6, 0.35, 1.65) - mw6_z);\nmw7_z = mw7_z + harmonic_coeff * (clamp(mw7, 0.35, 1.65) - mw7_z);\nmw8_z = mw8_z + harmonic_coeff * (clamp(mw8, 0.35, 1.65) - mw8_z);\n\nrx_angle = rot_x_z * pi2;\nry_angle = rot_y_z * pi2;\nrz_angle = rot_z_z * pi2;\nrxs = sin(rx_angle); rxc = cos(rx_angle);\nrys = sin(ry_angle); ryc = cos(ry_angle);\nrzs = sin(rz_angle); rzc = cos(rz_angle);\n\n// Rotation changes the delay geometry itself, not just the final stereo pan.\n// The larger coefficients make XYZ/Bloch motion clearly audible.\nrot1 =  0.62 * rxs + 0.31 * rys + 0.18 * rzs;\nrot2 = -0.48 * rxs + 0.46 * rys - 0.27 * rzs;\nrot3 =  0.35 * rxs - 0.58 * rys + 0.39 * rzs;\nrot4 = -0.57 * rxs - 0.29 * rys - 0.36 * rzs;\nrot5 =  0.44 * rxc + 0.36 * rys - 0.31 * rzs;\nrot6 = -0.38 * rxs + 0.51 * ryc + 0.28 * rzs;\nrot7 =  0.29 * rxs - 0.41 * rys + 0.52 * rzc;\nrot8 = -0.53 * rxc - 0.34 * ryc - 0.26 * rzs;\nshape1 = shape1_z; shape2 = shape2_z; shape3 = shape3_z; shape4 = shape4_z;\nshape5 = shape5_z; shape6 = shape6_z; shape7 = shape7_z; shape8 = shape8_z;\n// Fixed asymmetric terms keep deformation audible even for a perfectly\n// symmetric field such as a sphere sampled on a spherical probe shell.\ndeform_amount = (0.04 + 1.28 * surface_depth_z) * (0.88 + 0.24 * morph_z);\ngeom1 = 0.88 * shape1 + 0.48 * rot1 - 0.42;\ngeom2 = 0.88 * shape2 + 0.48 * rot2 + 0.36;\ngeom3 = 0.88 * shape3 + 0.48 * rot3 - 0.28;\ngeom4 = 0.88 * shape4 + 0.48 * rot4 + 0.46;\ngeom5 = 0.88 * shape5 + 0.48 * rot5 - 0.22;\ngeom6 = 0.88 * shape6 + 0.48 * rot6 + 0.31;\ngeom7 = 0.88 * shape7 + 0.48 * rot7 - 0.49;\ngeom8 = 0.88 * shape8 + 0.48 * rot8 + 0.27;\n\nd1 = clamp(31 * size_scale * exp(deform_amount * geom1 - 0.18 * warp_z) * sr * 0.001, 16, 191999);\nd2 = clamp(37 * size_scale * exp(deform_amount * geom2 + 0.14 * warp_z) * sr * 0.001, 16, 191999);\nd3 = clamp(43 * size_scale * exp(deform_amount * geom3 - 0.10 * warp_z) * sr * 0.001, 16, 191999);\nd4 = clamp(47 * size_scale * exp(deform_amount * geom4 + 0.07 * warp_z) * sr * 0.001, 16, 191999);\nd5 = clamp(53 * size_scale * exp(deform_amount * geom5 - 0.05 * warp_z) * sr * 0.001, 16, 191999);\nd6 = clamp(59 * size_scale * exp(deform_amount * geom6 + 0.09 * warp_z) * sr * 0.001, 16, 191999);\nd7 = clamp(67 * size_scale * exp(deform_amount * geom7 - 0.13 * warp_z) * sr * 0.001, 16, 191999);\nd8 = clamp(73 * size_scale * exp(deform_amount * geom8 + 0.17 * warp_z) * sr * 0.001, 16, 191999);\n\nr1 = dl1.read(d1); r2 = dl2.read(d2); r3 = dl3.read(d3); r4 = dl4.read(d4);\nr5 = dl5.read(d5); r6 = dl6.read(d6); r7 = dl7.read(d7); r8 = dl8.read(d8);\n\nshape_activity = (\n    abs(shape1) + abs(shape2) + abs(shape3) + abs(shape4)\n    + abs(shape5) + abs(shape6) + abs(shape7) + abs(shape8)\n) * 0.125;\neffective_absorb = clamp(\n    absorb + surface_depth_z * (0.14 + 0.18 * shape_activity),\n    0,\n    0.94\n);\nea1 = clamp(effective_absorb - 0.16 * tilt_z, 0, 0.96);\nea2 = clamp(effective_absorb - 0.11 * tilt_z, 0, 0.96);\nea3 = clamp(effective_absorb - 0.06 * tilt_z, 0, 0.96);\nea4 = clamp(effective_absorb - 0.02 * tilt_z, 0, 0.96);\nea5 = clamp(effective_absorb + 0.02 * tilt_z, 0, 0.96);\nea6 = clamp(effective_absorb + 0.06 * tilt_z, 0, 0.96);\nea7 = clamp(effective_absorb + 0.11 * tilt_z, 0, 0.96);\nea8 = clamp(effective_absorb + 0.16 * tilt_z, 0, 0.96);\ncut1 = clamp(0.025 + (1 - ea1) * 0.42, 0.02, 0.46);\ncut2 = clamp(0.025 + (1 - ea2) * 0.42, 0.02, 0.46);\ncut3 = clamp(0.025 + (1 - ea3) * 0.42, 0.02, 0.46);\ncut4 = clamp(0.025 + (1 - ea4) * 0.42, 0.02, 0.46);\ncut5 = clamp(0.025 + (1 - ea5) * 0.42, 0.02, 0.46);\ncut6 = clamp(0.025 + (1 - ea6) * 0.42, 0.02, 0.46);\ncut7 = clamp(0.025 + (1 - ea7) * 0.42, 0.02, 0.46);\ncut8 = clamp(0.025 + (1 - ea8) * 0.42, 0.02, 0.46);\nlp1 = lp1 + cut1 * (r1 - lp1); lp2 = lp2 + cut2 * (r2 - lp2);\nlp3 = lp3 + cut3 * (r3 - lp3); lp4 = lp4 + cut4 * (r4 - lp4);\nlp5 = lp5 + cut5 * (r5 - lp5); lp6 = lp6 + cut6 * (r6 - lp6);\nlp7 = lp7 + cut7 * (r7 - lp7); lp8 = lp8 + cut8 * (r8 - lp8);\n\nf1 = mix(r1, lp1, ea1); f2 = mix(r2, lp2, ea2);\nf3 = mix(r3, lp3, ea3); f4 = mix(r4, lp4, ea4);\nf5 = mix(r5, lp5, ea5); f6 = mix(r6, lp6, ea6);\nf7 = mix(r7, lp7, ea7); f8 = mix(r8, lp8, ea8);\n\n// Normalized eight-point Hadamard diffusion matrix.\nhn = 0.353553391;\nh1 = ( f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8) * hn;\nh2 = ( f1 - f2 + f3 - f4 + f5 - f6 + f7 - f8) * hn;\nh3 = ( f1 + f2 - f3 - f4 + f5 + f6 - f7 - f8) * hn;\nh4 = ( f1 - f2 - f3 + f4 + f5 - f6 - f7 + f8) * hn;\nh5 = ( f1 + f2 + f3 + f4 - f5 - f6 - f7 - f8) * hn;\nh6 = ( f1 - f2 + f3 - f4 - f5 + f6 - f7 + f8) * hn;\nh7 = ( f1 + f2 - f3 - f4 - f5 - f6 + f7 + f8) * hn;\nh8 = ( f1 - f2 - f3 + f4 - f5 + f6 + f7 - f8) * hn;\n\ndiffusion_seconds = max(diffusion_slew_ms, 0.1) * 0.001;\ndiffusion_coeff = 1 - exp(-1 / max(sr * diffusion_seconds, 1));\ndiffusion_z = diffusion_z + diffusion_coeff * (clamp(diffusion, 0, 1) - diffusion_z);\ndiff_amount = diffusion_z;\nn1 = mix(f1, h1, diff_amount); n2 = mix(f2, h2, diff_amount);\nn3 = mix(f3, h3, diff_amount); n4 = mix(f4, h4, diff_amount);\nn5 = mix(f5, h5, diff_amount); n6 = mix(f6, h6, diff_amount);\nn7 = mix(f7, h7, diff_amount); n8 = mix(f8, h8, diff_amount);\n\nfr = clamp(freeze, 0, 1);\neffective_decay = clamp(\n    decay + 0.10 * surface_depth_z - 0.06 * shape_activity,\n    0,\n    1\n);\nfeedback = mix(0.48 + 0.49 * effective_decay, 0.999, fr);\nexcite = in1 * input_gain * (1 - fr) * 0.42;\nrg1 = clamp(feedback + 0.045 * resonance_z * (mw1_z - 1), 0, 0.9985);\nrg2 = clamp(feedback + 0.045 * resonance_z * (mw2_z - 1), 0, 0.9985);\nrg3 = clamp(feedback + 0.045 * resonance_z * (mw3_z - 1), 0, 0.9985);\nrg4 = clamp(feedback + 0.045 * resonance_z * (mw4_z - 1), 0, 0.9985);\nrg5 = clamp(feedback + 0.045 * resonance_z * (mw5_z - 1), 0, 0.9985);\nrg6 = clamp(feedback + 0.045 * resonance_z * (mw6_z - 1), 0, 0.9985);\nrg7 = clamp(feedback + 0.045 * resonance_z * (mw7_z - 1), 0, 0.9985);\nrg8 = clamp(feedback + 0.045 * resonance_z * (mw8_z - 1), 0, 0.9985);\ndl1.write(tanh( excite * mw1_z + rg1 * n1));\ndl2.write(tanh(-excite * mw2_z + rg2 * n2));\ndl3.write(tanh( excite * mw3_z + rg3 * n3));\ndl4.write(tanh(-excite * mw4_z + rg4 * n4));\ndl5.write(tanh(-excite * mw5_z + rg5 * n5));\ndl6.write(tanh( excite * mw6_z + rg6 * n6));\ndl7.write(tanh(-excite * mw7_z + rg7 * n7));\ndl8.write(tanh( excite * mw8_z + rg8 * n8));\n\nspread = clamp(width, 0, 1);\ndecoder_a_l = f1 + f3 + f6 + f8 + spread * (f2 - f5);\ndecoder_a_r = f2 + f4 + f5 + f7 + spread * (f3 - f6);\ndecoder_b_l = f2 + f3 + f5 + f8 + spread * (f1 - f7);\ndecoder_b_r = f1 + f4 + f6 + f7 + spread * (f5 - f2);\ndecoder_c_l = f1 + f2 + f7 + f8 + spread * (f3 - f6);\ndecoder_c_r = f3 + f4 + f5 + f6 + spread * (f8 - f1);\nx_mix = clamp(0.5 + 0.5 * rxs + 0.22 * surface_depth_z * shape1, 0, 1);\ny_mix = clamp(0.5 + 0.5 * rys + 0.22 * surface_depth_z * shape5, 0, 1);\ndecoder_x_l = mix(decoder_a_l, decoder_b_l, x_mix);\ndecoder_x_r = mix(decoder_a_r, decoder_b_r, x_mix);\ndecoder_y_l = mix(decoder_x_l, decoder_c_l, y_mix);\ndecoder_y_r = mix(decoder_x_r, decoder_c_r, y_mix);\nleft_raw = (rzc * decoder_y_l - rzs * decoder_y_r) * output_gain * 0.24;\nright_raw = (rzs * decoder_y_l + rzc * decoder_y_r) * output_gain * 0.24;\n\ndc = exp((-pi2 * 18) / sr);\nleft = left_raw - dc_l_x + dc * dc_l_y;\nright = right_raw - dc_r_x + dc * dc_r_y;\ndc_l_x = left_raw; dc_l_y = left;\ndc_r_x = right_raw; dc_r_y = right;\n\nout1 = left;\nout2 = right;\n",
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
                        1265.0,
                        98.0,
                        22.0
                    ],
                    "text": "OSC-route /qmw"
                }
            },
            {
                "box": {
                    "id": "obj-144",
                    "maxclass": "newobj",
                    "patching_rect": [
                        930.0,
                        1265.0,
                        132.0,
                        22.0
                    ],
                    "text": "OSC-route /acoustics"
                }
            },
            {
                "box": {
                    "id": "obj-145",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1075.0,
                        1265.0,
                        180.0,
                        22.0
                    ],
                    "text": "OSC-route /reverb /modal"
                }
            },
            {
                "box": {
                    "id": "obj-146",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1270.0,
                        1265.0,
                        270.0,
                        22.0
                    ],
                    "text": "OSC-route /resonance /decay /damping"
                }
            },
            {
                "box": {
                    "id": "obj-147",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1270.0,
                        1300.0,
                        230.0,
                        22.0
                    ],
                    "text": "OSC-route /tilt /warp /weights"
                }
            },
            {
                "box": {
                    "id": "obj-148",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1335.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend harmonic_resonance"
                }
            },
            {
                "box": {
                    "id": "obj-149",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1000.0,
                        1335.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend decay"
                }
            },
            {
                "box": {
                    "id": "obj-150",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1180.0,
                        1335.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend absorb"
                }
            },
            {
                "box": {
                    "id": "obj-151",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1370.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend spectral_tilt"
                }
            },
            {
                "box": {
                    "id": "obj-152",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1000.0,
                        1370.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend modal_warp"
                }
            },
            {
                "box": {
                    "id": "obj-153",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1405.0,
                        270.0,
                        22.0
                    ],
                    "text": "unpack 0. 0. 0. 0. 0. 0. 0. 0."
                }
            },
            {
                "box": {
                    "id": "obj-154",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1440.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw1"
                }
            },
            {
                "box": {
                    "id": "obj-155",
                    "maxclass": "newobj",
                    "patching_rect": [
                        955.0,
                        1440.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw2"
                }
            },
            {
                "box": {
                    "id": "obj-156",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1090.0,
                        1440.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw3"
                }
            },
            {
                "box": {
                    "id": "obj-157",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1225.0,
                        1440.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw4"
                }
            },
            {
                "box": {
                    "id": "obj-158",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1475.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw5"
                }
            },
            {
                "box": {
                    "id": "obj-159",
                    "maxclass": "newobj",
                    "patching_rect": [
                        955.0,
                        1475.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw6"
                }
            },
            {
                "box": {
                    "id": "obj-160",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1090.0,
                        1475.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw7"
                }
            },
            {
                "box": {
                    "id": "obj-161",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1225.0,
                        1475.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw8"
                }
            },
            {
                "box": {
                    "id": "obj-162",
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
                    "id": "obj-163",
                    "maxclass": "newobj",
                    "patching_rect": [
                        965.0,
                        980.0,
                        660.0,
                        22.0
                    ],
                    "text": "route rot_x rot_y rot_z source rotation_slew_ms geometry_morph_slew_ms morph_slew_ms surface_slew_ms diffusion_slew_ms geometry_depth_slew_ms size dry_wet reverb_gain morph deform animate mlx_link a b expr resonance decay damping spectral_tilt modal_warp modal_weights harmonic_slew_ms"
                }
            },
            {
                "box": {
                    "id": "obj-164",
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
                    "id": "obj-165",
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
                    "id": "obj-166",
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
                    "id": "obj-167",
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
                    "id": "obj-168",
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
                    "id": "obj-169",
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
                    "id": "obj-170",
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
                    "id": "obj-171",
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
                    "id": "obj-172",
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
                    "id": "obj-173",
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
                    "id": "obj-174",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1160.0,
                        1090.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend harmonic_resonance"
                }
            },
            {
                "box": {
                    "id": "obj-175",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1335.0,
                        1090.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend decay"
                }
            },
            {
                "box": {
                    "id": "obj-176",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1510.0,
                        1090.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend absorb"
                }
            },
            {
                "box": {
                    "id": "obj-177",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1160.0,
                        1125.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend spectral_tilt"
                }
            },
            {
                "box": {
                    "id": "obj-178",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1335.0,
                        1125.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend modal_warp"
                }
            },
            {
                "box": {
                    "id": "obj-179",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1510.0,
                        1125.0,
                        165.0,
                        22.0
                    ],
                    "text": "prepend harmonic_slew_ms"
                }
            },
            {
                "box": {
                    "id": "obj-180",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1160.0,
                        270.0,
                        22.0
                    ],
                    "text": "unpack 0. 0. 0. 0. 0. 0. 0. 0."
                }
            },
            {
                "box": {
                    "id": "obj-181",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1195.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw1"
                }
            },
            {
                "box": {
                    "id": "obj-182",
                    "maxclass": "newobj",
                    "patching_rect": [
                        955.0,
                        1195.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw2"
                }
            },
            {
                "box": {
                    "id": "obj-183",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1090.0,
                        1195.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw3"
                }
            },
            {
                "box": {
                    "id": "obj-184",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1225.0,
                        1195.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw4"
                }
            },
            {
                "box": {
                    "id": "obj-185",
                    "maxclass": "newobj",
                    "patching_rect": [
                        820.0,
                        1230.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw5"
                }
            },
            {
                "box": {
                    "id": "obj-186",
                    "maxclass": "newobj",
                    "patching_rect": [
                        955.0,
                        1230.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw6"
                }
            },
            {
                "box": {
                    "id": "obj-187",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1090.0,
                        1230.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw7"
                }
            },
            {
                "box": {
                    "id": "obj-188",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1225.0,
                        1230.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend mw8"
                }
            },
            {
                "box": {
                    "id": "obj-189",
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
                    "id": "obj-190",
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
                    "id": "obj-191",
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
                    "id": "obj-192",
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
                    "id": "obj-193",
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
                    "id": "obj-194",
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
                    "id": "obj-195",
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
                    "id": "obj-196",
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
                    "id": "obj-197",
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
                    "id": "obj-198",
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
                    "id": "obj-199",
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
                    "id": "obj-200",
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
                    "id": "obj-201",
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
                    "id": "obj-202",
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
                    "id": "obj-203",
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
                    "id": "obj-204",
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
                    "id": "obj-205",
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
                    "id": "obj-206",
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
                    "id": "obj-207",
                    "maxclass": "newobj",
                    "patching_rect": [
                        1390.0,
                        530.0,
                        145.0,
                        22.0
                    ],
                    "text": "prepend emergent_preset"
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
                        "obj-43",
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
                        "obj-52",
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
                        "obj-55",
                        1
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
                        "obj-133",
                        0
                    ],
                    "destination": [
                        "obj-143",
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
                        "obj-145",
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
                        "obj-146",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-145",
                        1
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
                        "obj-146",
                        0
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-146",
                        1
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-146",
                        2
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
                        "obj-5",
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-147",
                        1
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-147",
                        2
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-153",
                        1
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-153",
                        2
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-153",
                        3
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
                        "obj-157",
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
                        "obj-153",
                        4
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-153",
                        5
                    ],
                    "destination": [
                        "obj-159",
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-153",
                        6
                    ],
                    "destination": [
                        "obj-160",
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-153",
                        7
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
                        "obj-5",
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
                        "obj-87",
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
                        "obj-95",
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
                        "obj-103",
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
                        "obj-79",
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
                        "obj-108",
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
                        "obj-112",
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
                        "obj-112",
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
                        "obj-116",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        8
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
                        "obj-163",
                        9
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
                        "obj-164",
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
                        "obj-165",
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
                        "obj-163",
                        10
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
                        "obj-74",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        11
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
                        "obj-58",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        12
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
                        "obj-68",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        13
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
                        "obj-14",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        14
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
                        "obj-18",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
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
                        "obj-163",
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
                        "obj-163",
                        17
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
                        "obj-163",
                        18
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        19
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
                        "obj-163",
                        20
                    ],
                    "destination": [
                        "obj-174",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-174",
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
                        "obj-163",
                        21
                    ],
                    "destination": [
                        "obj-175",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-175",
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
                        "obj-163",
                        22
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
                        "obj-163",
                        23
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        24
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-163",
                        26
                    ],
                    "destination": [
                        "obj-179",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-179",
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
                        "obj-163",
                        25
                    ],
                    "destination": [
                        "obj-180",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        1
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        2
                    ],
                    "destination": [
                        "obj-183",
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        3
                    ],
                    "destination": [
                        "obj-184",
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        4
                    ],
                    "destination": [
                        "obj-185",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-185",
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
                        "obj-180",
                        5
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
                        "obj-186",
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
                        "obj-180",
                        6
                    ],
                    "destination": [
                        "obj-187",
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
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        7
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
                        "obj-5",
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
                        "obj-189",
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
                        "obj-190",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-190",
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
                        2
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
                        "obj-4",
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
                        "obj-193",
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-194",
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
                        "obj-197",
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
                        "obj-198",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-198",
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
                        "obj-197",
                        1
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-197",
                        2
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-197",
                        3
                    ],
                    "destination": [
                        "obj-201",
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-197",
                        4
                    ],
                    "destination": [
                        "obj-202",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-202",
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
                        "obj-197",
                        5
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-197",
                        6
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-197",
                        7
                    ],
                    "destination": [
                        "obj-205",
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-196",
                        1
                    ],
                    "destination": [
                        "obj-206",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-206",
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
                        "obj-4",
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
            }
        ],
        "autosave": 0
    }
}
