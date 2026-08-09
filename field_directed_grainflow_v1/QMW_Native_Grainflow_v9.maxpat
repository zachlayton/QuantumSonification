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
                    "text": "QMW NATIVE GRAINFLOW v9 — RATE + AM SIGNAL CONTROL"
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
                    "patching_rect": [ 180.0, 247.0, 82.0, 22.0 ],
                    "text": "loadmess 1."
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
                    "destination": [ "unpack", 0 ],
                    "source": [ "pan", 0 ]
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
            }
        ],
        "autosave": 0
    }
}