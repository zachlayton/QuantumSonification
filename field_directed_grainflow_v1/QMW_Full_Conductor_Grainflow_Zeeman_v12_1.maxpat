{
    "patcher": {
        "fileversion": 1,
        "appversion": {
            "major": 9,
            "minor": 1,
            "revision": 4,
            "architecture": "x64",
            "modernui": 1
        },
        "classnamespace": "box",
        "rect": [ 59.0, 119.0, 1125.0, 796.0 ],
        "boxes": [
            {
                "box": {
                    "attr": "density",
                    "displaymode": 2,
                    "id": "obj-43",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 139.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "space",
                    "displaymode": 2,
                    "id": "obj-40",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 401.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "spaceRandom",
                    "displaymode": 2,
                    "id": "obj-41",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 430.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "transpose",
                    "displaymode": 2,
                    "id": "obj-32",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 284.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "transposeRandom",
                    "displaymode": 2,
                    "id": "obj-33",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 313.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "delay",
                    "displaymode": 2,
                    "id": "obj-30",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 226.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "delayRandom",
                    "displaymode": 2,
                    "id": "obj-31",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 255.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "amp",
                    "displaymode": 2,
                    "id": "obj-24",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 168.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "ampRandom",
                    "displaymode": 2,
                    "id": "obj-29",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 197.0, 151.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "state",
                    "id": "obj-34",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 110.0, 150.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "glissonSt",
                    "displaymode": 2,
                    "id": "obj-46",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 343.0, 150.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "glissonStRandom",
                    "displaymode": 2,
                    "id": "obj-48",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 824.0, 372.0, 150.0, 22.0 ]
                }
            },
            {
                "box": {
                    "fontsize": 18.0,
                    "id": "title",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 20.0, 15.0, 900.0, 27.0 ],
                    "text": "QMW FULL CONDUCTOR GRAINFLOW + ZEEMAN v12"
                }
            },
            {
                "box": {
                    "id": "buf",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "float", "bang" ],
                    "patching_rect": [ 20.0, 60.0, 300.0, 22.0 ],
                    "text": "buffer~ qmw_fdg_source Anton.aif"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "clock",
                    "maxclass": "flonum",
                    "maximum": 100.0,
                    "minimum": 0.1,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 20.0, 110.0, 70.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "clock_p",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 100.0, 110.0, 80.0, 22.0 ],
                    "text": "phasor~ 10."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "scan",
                    "maxclass": "flonum",
                    "maximum": 5.0,
                    "minimum": 0.0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 20.0, 145.0, 70.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "scan_p",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 100.0, 145.0, 80.0, 22.0 ],
                    "text": "phasor~ 0.2"
                }
            },
            {
                "box": {
                    "id": "grain",
                    "maxclass": "newobj",
                    "numinlets": 4,
                    "numoutlets": 9,
                    "outlettype": [ "multichannelsignal", "list", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal", "multichannelsignal" ],
                    "patching_rect": [ 280.0, 125.0, 281.0, 22.0 ],
                    "text": "grainflow~ qmw_fdg_source 8 @delayRandom 500"
                }
            },
            {
                "box": {
                    "id": "rate_label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 20.0, 195.0, 150.0, 20.0 ],
                    "text": "inlet 3: playback rate"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "rate",
                    "maxclass": "flonum",
                    "maximum": 4.0,
                    "minimum": -4.0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 20.0, 218.0, 72.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "rate_sig",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 100.0, 218.0, 62.0, 22.0 ],
                    "text": "sig~ 1."
                }
            },
            {
                "box": {
                    "id": "rate_init",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 20.0, 247.0, 82.0, 22.0 ],
                    "text": "loadmess 1."
                }
            },
            {
                "box": {
                    "id": "amp_label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 180.0, 195.0, 165.0, 20.0 ],
                    "text": "inlet 4: amplitude modulation"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "amp",
                    "maxclass": "flonum",
                    "maximum": 2.0,
                    "minimum": 0.0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 180.0, 218.0, 72.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "amp_sig",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 260.0, 218.0, 62.0, 22.0 ],
                    "text": "sig~ 1."
                }
            },
            {
                "box": {
                    "id": "amp_init",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 180.0, 247.0, 73.0, 22.0 ],
                    "text": "loadmess 0."
                }
            },
            {
                "box": {
                    "id": "enable",
                    "maxclass": "toggle",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "int" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 235.0, 285.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "enable_l",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 155.0, 285.0, 75.0, 22.0 ],
                    "text": "loadmess 1"
                }
            },
            {
                "box": {
                    "id": "pan",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "multichannelsignal", "list" ],
                    "patching_rect": [ 280.0, 330.0, 190.0, 22.0 ],
                    "text": "grainflow.util.stereoPan~"
                }
            },
            {
                "box": {
                    "id": "unpack",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "signal" ],
                    "patching_rect": [ 300.0, 365.0, 90.0, 22.0 ],
                    "text": "mc.unpack~ 2"
                }
            },
            {
                "box": {
                    "id": "gain",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 410.0, 365.0, 65.0, 22.0 ],
                    "text": "*~ 0.25"
                }
            },
            {
                "box": {
                    "id": "gainr",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 485.0, 365.0, 65.0, 22.0 ],
                    "text": "*~ 0.25"
                }
            },
            {
                "box": {
                    "id": "dac",
                    "maxclass": "ezdac~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [ 570.0, 350.0, 55.0, 55.0 ]
                }
            },
            {
                "box": {
                    "id": "clock_i",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 700.0, 280.0, 90.0, 22.0 ],
                    "text": "loadmess 10."
                }
            },
            {
                "box": {
                    "id": "scan_i",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 700.0, 310.0, 90.0, 22.0 ],
                    "text": "loadmess 0.2"
                }
            },
            {
                "box": {
                    "id": "osc_label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 20.0, 410.0, 650.0, 20.0 ],
                    "text": "OSC 7400: conductor frames drive the complete GrainFlow + Zeeman state"
                }
            },
            {
                "box": {
                    "id": "osc",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 20.0, 435.0, 125.0, 22.0 ],
                    "text": "udpreceive 7400"
                }
            },
            {
                "box": {
                    "id": "osc_route",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 6,
                    "outlettype": [ "", "", "", "", "", "FullPacket" ],
                    "patching_rect": [ 155.0, 435.0, 787.0, 22.0 ],
                    "text": "o.route /qmw/density_field/magnitude /qmw/density_field/phase /qmw/density_field/purity /qmw/density_field/entropy /qmw/density_field/coherence"
                }
            },
            {
                "box": {
                    "id": "map_label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 20.0, 470.0, 115.0, 20.0 ],
                    "text": "QUANTUM MAP"
                }
            },
            {
                "box": {
                    "id": "map_enable",
                    "maxclass": "toggle",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "int" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 135.0, 468.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "map_init",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 165.0, 470.0, 78.0, 22.0 ],
                    "text": "loadmess 0"
                }
            },
            {
                "box": {
                    "id": "mag_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 20.0, 505.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "phase_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 180.0, 505.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "purity_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 340.0, 505.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "entropy_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 500.0, 505.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "coherence_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 660.0, 505.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "phase_map",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 180.0, 540.0, 180.0, 22.0 ],
                    "text": "expr pow(2.\\, $f1/3.14159265)"
                }
            },
            {
                "box": {
                    "id": "phase_clip",
                    "maxclass": "newobj",
                    "numinlets": 3,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 180.0, 570.0, 92.0, 22.0 ],
                    "text": "clip 0.25 4."
                }
            },
            {
                "box": {
                    "id": "coh_map",
                    "maxclass": "newobj",
                    "numinlets": 6,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 660.0, 540.0, 150.0, 22.0 ],
                    "text": "scale 0. 1. 0.15 1."
                }
            },
            {
                "box": {
                    "id": "entropy_map",
                    "maxclass": "newobj",
                    "numinlets": 6,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 500.0, 540.0, 145.0, 22.0 ],
                    "text": "scale 0. 1. 0. 500."
                }
            },
            {
                "box": {
                    "id": "zee_label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 20.0, 620.0, 500.0, 20.0 ],
                    "text": "ZEEMAN RESONATORS: field magnitude controls spectral splitting"
                }
            },
            {
                "box": {
                    "id": "zee_field_map",
                    "maxclass": "newobj",
                    "numinlets": 6,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 20.0, 650.0, 145.0, 22.0 ],
                    "text": "scale 0. 1. 0. 8."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "zee_field",
                    "maxclass": "flonum",
                    "maximum": 20.0,
                    "minimum": 0.0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 175.0, 650.0, 72.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "zee_field_pre",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 255.0, 650.0, 88.0, 22.0 ],
                    "text": "prepend field"
                }
            },
            {
                "box": {
                    "id": "zee_controller",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 5,
                    "outlettype": [ "", "", "", "", "" ],
                    "patching_rect": [ 355.0, 650.0, 235.0, 22.0 ],
                    "saved_object_attributes": {
                        "filename": "qmw_fdg_zeeman_controller_v12.js",
                        "parameter_enable": 0
                    },
                    "text": "js qmw_fdg_zeeman_controller_v12.js"
                }
            },
            {
                "box": {
                    "id": "zee_poly",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "signal" ],
                    "patching_rect": [ 600.0, 650.0, 315.0, 22.0 ],
                    "text": "poly~ qmw_fdg_zeeman_ring_voice_v12 8 @parallel 1"
                }
            },
            {
                "box": {
                    "id": "zee_gain_l",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 580.0, 690.0, 62.0, 22.0 ],
                    "text": "*~ 0.18"
                }
            },
            {
                "box": {
                    "id": "zee_gain_r",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "signal" ],
                    "patching_rect": [ 650.0, 690.0, 62.0, 22.0 ],
                    "text": "*~ 0.18"
                }
            },
            {
                "box": {
                    "id": "zee_normal",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 20.0, 690.0, 92.0, 22.0 ],
                    "text": "preset normal"
                }
            },
            {
                "box": {
                    "id": "zee_d1",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 120.0, 690.0, 117.0, 22.0 ],
                    "text": "preset sodium_d1"
                }
            },
            {
                "box": {
                    "id": "zee_d2",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 245.0, 690.0, 117.0, 22.0 ],
                    "text": "preset sodium_d2"
                }
            },
            {
                "box": {
                    "id": "zee_init",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 370.0, 690.0, 105.0, 22.0 ],
                    "text": "loadmess normal"
                }
            },
            {
                "box": {
                    "id": "conductor_route",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 4,
                    "outlettype": [ "", "", "", "FullPacket" ],
                    "patching_rect": [ 20.0, 750.0, 555.0, 22.0 ],
                    "text": "o.route /qmw/conductor/grainflow /qmw/conductor/zeeman /qmw/conductor/zeeman/preset"
                }
            },
            {
                "box": {
                    "id": "grain_frame_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 20.0, 785.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "zee_frame_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 90.0, 785.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "preset_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 160.0, 785.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "grain_unpack",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 14,
                    "outlettype": [ "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float" ],
                    "patching_rect": [ 20.0, 820.0, 430.0, 22.0 ],
                    "text": "unpack f f f f f f f f f f f f f f"
                }
            },
            {
                "box": {
                    "id": "zee_unpack",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 4,
                    "outlettype": [ "float", "float", "float", "float" ],
                    "patching_rect": [ 470.0, 820.0, 125.0, 22.0 ],
                    "text": "unpack f f f f"
                }
            },
            {
                "box": {
                    "id": "zee_carrier_pre",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 600.0, 820.0, 115.0, 22.0 ],
                    "text": "prepend carrierfreq"
                }
            },
            {
                "box": {
                    "id": "zee_spread_pre",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 710.0, 820.0, 95.0, 22.0 ],
                    "text": "prepend spread"
                }
            },
            {
                "box": {
                    "id": "preset_pre",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 815.0, 820.0, 95.0, 22.0 ],
                    "text": "prepend preset"
                }
            },
            {
                "box": {
                    "id": "frame_status",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 235.0, 785.0, 560.0, 22.0 ],
                    "text": "waiting for /qmw/conductor/grainflow"
                }
            },
            {
                "box": {
                    "id": "full_route",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "FullPacket" ],
                    "patching_rect": [ 20.0, 870.0, 285.0, 22.0 ],
                    "text": "o.route /qmw/conductor/grainflow/v2"
                }
            },
            {
                "box": {
                    "id": "full_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 315.0, 870.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "full_unpack",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 28,
                    "outlettype": [ "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float" ],
                    "patching_rect": [ 385.0, 870.0, 610.0, 22.0 ],
                    "text": "unpack f f f f f f f f f f f f f f f f f f f f f f f f f f f f"
                }
            },
            {
                "box": {
                    "id": "full_status",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 20.0, 900.0, 600.0, 22.0 ],
                    "text": "waiting for /qmw/conductor/grainflow/v2"
                }
            },
            {
                "box": {
                    "attr": "ampOffset",
                    "displaymode": 2,
                    "id": "full_attr_ampOffset",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1000.0, 197.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "delayOffset",
                    "displaymode": 2,
                    "id": "full_attr_delayOffset",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1000.0, 284.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "direction",
                    "displaymode": 2,
                    "id": "full_attr_direction",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1000.0, 342.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "glissonStOffset",
                    "displaymode": 2,
                    "id": "full_attr_glissonStOffset",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1000.0, 400.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "rate",
                    "displaymode": 2,
                    "id": "full_attr_rate",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1000.0, 458.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "rateOffset",
                    "displaymode": 2,
                    "id": "full_attr_rateOffset",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 110.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "rateRandom",
                    "displaymode": 2,
                    "id": "full_attr_rateRandom",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 139.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "spaceOffset",
                    "displaymode": 2,
                    "id": "full_attr_spaceOffset",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 197.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "transposeOffset",
                    "displaymode": 2,
                    "id": "full_attr_transposeOffset",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 284.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "window",
                    "displaymode": 2,
                    "id": "full_attr_window",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 342.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "windowOffset",
                    "displaymode": 2,
                    "id": "full_attr_windowOffset",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 371.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "windowRandom",
                    "displaymode": 2,
                    "id": "full_attr_windowRandom",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 400.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "startPoint",
                    "displaymode": 2,
                    "id": "full_attr_startPoint",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 429.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "stopPoint",
                    "displaymode": 2,
                    "id": "full_attr_stopPoint",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 1180.0, 458.0, 165.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "event_route",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "FullPacket" ],
                    "patching_rect": [ 20.0, 940.0, 420.0, 22.0 ],
                    "text": "o.route /qmw/conductor/grainflow/event"
                }
            },
            {
                "box": {
                    "id": "event_gate",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 450.0, 940.0, 58.0, 22.0 ],
                    "text": "gate 1"
                }
            },
            {
                "box": {
                    "id": "event_monitor",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 520.0, 940.0, 420.0, 22.0 ],
                    "text": "stream / spread / deviate / target events"
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "destination": [ "amp_sig", 0 ],
                    "source": [ "amp", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "amp", 0 ],
                    "source": [ "amp_init", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 3 ],
                    "source": [ "amp_sig", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "clock_p", 0 ],
                    "source": [ "clock", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "clock", 0 ],
                    "source": [ "clock_i", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "clock_p", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "amp", 0 ],
                    "source": [ "coh_map", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "coh_map", 0 ],
                    "source": [ "coherence_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "preset_gate", 1 ],
                    "source": [ "conductor_route", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_frame_gate", 1 ],
                    "source": [ "conductor_route", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "enable", 0 ],
                    "source": [ "enable_l", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "entropy_map", 0 ],
                    "source": [ "entropy_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-31", 0 ],
                    "source": [ "entropy_map", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "event_monitor", 0 ],
                    "order": 0,
                    "source": [ "event_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "order": 1,
                    "source": [ "event_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "event_gate", 1 ],
                    "source": [ "event_route", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_ampOffset", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_delayOffset", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_direction", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_glissonStOffset", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_rate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_rateOffset", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_rateRandom", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_spaceOffset", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_startPoint", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_stopPoint", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_transposeOffset", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_window", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_windowOffset", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "full_attr_windowRandom", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_status", 0 ],
                    "order": 1,
                    "source": [ "full_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_unpack", 0 ],
                    "order": 0,
                    "source": [ "full_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_gate", 1 ],
                    "source": [ "full_route", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "amp", 0 ],
                    "source": [ "full_unpack", 27 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_ampOffset", 0 ],
                    "source": [ "full_unpack", 3 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_delayOffset", 0 ],
                    "source": [ "full_unpack", 6 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_direction", 0 ],
                    "source": [ "full_unpack", 8 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_glissonStOffset", 0 ],
                    "source": [ "full_unpack", 10 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_rate", 0 ],
                    "source": [ "full_unpack", 12 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_rateOffset", 0 ],
                    "source": [ "full_unpack", 13 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_rateRandom", 0 ],
                    "source": [ "full_unpack", 14 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_spaceOffset", 0 ],
                    "source": [ "full_unpack", 16 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_startPoint", 0 ],
                    "source": [ "full_unpack", 24 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_stopPoint", 0 ],
                    "source": [ "full_unpack", 25 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_transposeOffset", 0 ],
                    "source": [ "full_unpack", 19 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_window", 0 ],
                    "source": [ "full_unpack", 21 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_windowOffset", 0 ],
                    "source": [ "full_unpack", 22 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_attr_windowRandom", 0 ],
                    "source": [ "full_unpack", 23 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-24", 0 ],
                    "source": [ "full_unpack", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-29", 0 ],
                    "source": [ "full_unpack", 4 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-30", 0 ],
                    "source": [ "full_unpack", 5 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-31", 0 ],
                    "source": [ "full_unpack", 7 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-32", 0 ],
                    "source": [ "full_unpack", 18 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-33", 0 ],
                    "source": [ "full_unpack", 20 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-34", 0 ],
                    "source": [ "full_unpack", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-40", 0 ],
                    "source": [ "full_unpack", 15 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-41", 0 ],
                    "source": [ "full_unpack", 17 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-43", 0 ],
                    "source": [ "full_unpack", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-46", 0 ],
                    "source": [ "full_unpack", 9 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-48", 0 ],
                    "source": [ "full_unpack", 11 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "rate", 0 ],
                    "source": [ "full_unpack", 26 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "dac", 0 ],
                    "source": [ "gain", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "dac", 1 ],
                    "source": [ "gainr", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "pan", 1 ],
                    "source": [ "grain", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "pan", 0 ],
                    "source": [ "grain", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "frame_status", 0 ],
                    "order": 0,
                    "source": [ "grain_frame_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain_unpack", 0 ],
                    "order": 1,
                    "source": [ "grain_frame_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "amp", 0 ],
                    "source": [ "grain_unpack", 13 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-24", 0 ],
                    "source": [ "grain_unpack", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-29", 0 ],
                    "source": [ "grain_unpack", 3 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-30", 0 ],
                    "source": [ "grain_unpack", 4 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-31", 0 ],
                    "source": [ "grain_unpack", 5 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-32", 0 ],
                    "source": [ "grain_unpack", 6 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-33", 0 ],
                    "source": [ "grain_unpack", 7 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-34", 0 ],
                    "source": [ "grain_unpack", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-40", 0 ],
                    "source": [ "grain_unpack", 8 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-41", 0 ],
                    "source": [ "grain_unpack", 9 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-43", 0 ],
                    "source": [ "grain_unpack", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-46", 0 ],
                    "source": [ "grain_unpack", 10 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-48", 0 ],
                    "source": [ "grain_unpack", 11 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "rate", 0 ],
                    "source": [ "grain_unpack", 12 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_field_map", 0 ],
                    "source": [ "mag_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "coherence_gate", 0 ],
                    "order": 0,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "entropy_gate", 0 ],
                    "order": 1,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "event_gate", 0 ],
                    "order": 2,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_gate", 0 ],
                    "order": 4,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain_frame_gate", 0 ],
                    "order": 8,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "mag_gate", 0 ],
                    "order": 9,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "phase_gate", 0 ],
                    "order": 5,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "preset_gate", 0 ],
                    "order": 6,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "purity_gate", 0 ],
                    "order": 3,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_frame_gate", 0 ],
                    "order": 7,
                    "source": [ "map_enable", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "map_enable", 0 ],
                    "source": [ "map_init", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-24", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-29", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-30", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-31", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-32", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-33", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-34", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-40", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-41", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-43", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-46", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 0 ],
                    "source": [ "obj-48", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "conductor_route", 0 ],
                    "order": 3,
                    "source": [ "osc", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "event_route", 0 ],
                    "order": 1,
                    "source": [ "osc", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "full_route", 0 ],
                    "order": 2,
                    "source": [ "osc", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "osc_route", 0 ],
                    "order": 0,
                    "source": [ "osc", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "unpack", 0 ],
                    "source": [ "pan", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "rate", 0 ],
                    "source": [ "phase_clip", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "phase_map", 0 ],
                    "source": [ "phase_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "phase_clip", 0 ],
                    "source": [ "phase_map", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "preset_pre", 0 ],
                    "source": [ "preset_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "preset_pre", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-43", 0 ],
                    "source": [ "purity_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "rate_sig", 0 ],
                    "source": [ "rate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "rate", 0 ],
                    "source": [ "rate_init", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 2 ],
                    "source": [ "rate_sig", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "scan_p", 0 ],
                    "source": [ "scan", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "scan", 0 ],
                    "source": [ "scan_i", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "grain", 1 ],
                    "source": [ "scan_p", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "gain", 0 ],
                    "source": [ "unpack", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "gainr", 0 ],
                    "source": [ "unpack", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "zee_carrier_pre", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_poly", 0 ],
                    "source": [ "zee_controller", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "zee_d1", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "zee_d2", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_field_pre", 0 ],
                    "source": [ "zee_field", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_field", 0 ],
                    "source": [ "zee_field_map", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "zee_field_pre", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_unpack", 0 ],
                    "source": [ "zee_frame_gate", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "dac", 0 ],
                    "source": [ "zee_gain_l", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "dac", 1 ],
                    "source": [ "zee_gain_r", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "zee_init", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "zee_normal", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_gain_l", 0 ],
                    "source": [ "zee_poly", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_gain_r", 0 ],
                    "source": [ "zee_poly", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_controller", 0 ],
                    "source": [ "zee_spread_pre", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_carrier_pre", 0 ],
                    "source": [ "zee_unpack", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_field", 0 ],
                    "source": [ "zee_unpack", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_gain_l", 1 ],
                    "order": 1,
                    "source": [ "zee_unpack", 3 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_gain_r", 1 ],
                    "order": 0,
                    "source": [ "zee_unpack", 3 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "zee_spread_pre", 0 ],
                    "source": [ "zee_unpack", 2 ]
                }
            }
        ],
        "autosave": 0
    }
}