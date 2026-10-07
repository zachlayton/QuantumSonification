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
        "rect": [ 251.0, 100.0, 1227.0, 816.0 ],
        "boxes": [
            {
                "box": {
                    "format": 6,
                    "id": "obj-110",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 863.0, 351.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-109",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 924.0, 351.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-105",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 893.0, 439.0, 29.5, 22.0 ],
                    "text": "* 5."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-106",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 888.0, 473.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-107",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 893.0, 411.0, 41.0, 22.0 ],
                    "text": "abs 0."
                }
            },
            {
                "box": {
                    "id": "obj-102",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 821.0, 439.0, 29.5, 22.0 ],
                    "text": "* 5."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-103",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 816.0, 473.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-104",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 821.0, 411.0, 41.0, 22.0 ],
                    "text": "abs 0."
                }
            },
            {
                "box": {
                    "attr": "mode",
                    "fontface": 0,
                    "fontname": "Arial",
                    "fontsize": 12.0,
                    "id": "obj-98",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 724.0, 131.0, 167.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "timestretch",
                    "fontface": 0,
                    "fontname": "Arial",
                    "fontsize": 12.0,
                    "id": "obj-4",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 543.0, 21.0, 150.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "speed",
                    "fontface": 0,
                    "fontname": "Arial",
                    "fontsize": 12.0,
                    "id": "obj-99",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 695.0, 21.0, 150.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "pitchshift",
                    "fontface": 0,
                    "fontname": "Arial",
                    "fontsize": 12.0,
                    "id": "obj-100",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 724.0, 55.0, 150.0, 22.0 ]
                }
            },
            {
                "box": {
                    "attr": "pitchshiftcent",
                    "fontface": 0,
                    "fontname": "Arial",
                    "fontsize": 12.0,
                    "id": "obj-101",
                    "maxclass": "attrui",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 724.0, 93.0, 150.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-95",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 271.0, 856.0, 113.0, 22.0 ],
                    "text": "morph_slew_ms $1"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-94",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 302.5, 799.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-92",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 271.0, 828.0, 113.0, 22.0 ],
                    "presentation_linecount": 2,
                    "text": "morph_slew_ms $1"
                }
            },
            {
                "box": {
                    "id": "obj-88",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 188.0, 730.0, 29.5, 22.0 ],
                    "text": "* 5."
                }
            },
            {
                "box": {
                    "id": "obj-89",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 183.0, 793.0, 87.0, 22.0 ],
                    "text": "harmonicity $1"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-90",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 183.0, 764.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-91",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 188.0, 702.0, 41.0, 22.0 ],
                    "text": "abs 0."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-87",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 382.0, 60.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-85",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 338.0, 60.0, 29.5, 22.0 ],
                    "text": "* 1."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-72",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 338.0, 90.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-75",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 338.0, 21.0, 41.0, 22.0 ],
                    "text": "abs 0."
                }
            },
            {
                "box": {
                    "id": "obj-70",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 294.0, 130.0, 47.0, 22.0 ],
                    "text": "size $1"
                }
            },
            {
                "box": {
                    "id": "obj-63",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 38.0, 66.0, 110.0, 22.0 ],
                    "presentation_linecount": 2,
                    "text": "shape icosahedron"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-46",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 16.0, 8.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-44",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 38.0, 38.0, 131.0, 22.0 ],
                    "text": "transition tetra cube $1"
                }
            },
            {
                "box": {
                    "id": "obj-34",
                    "lastchannelcount": 0,
                    "maxclass": "live.gain~",
                    "numinlets": 2,
                    "numoutlets": 5,
                    "outlettype": [ "signal", "signal", "", "float", "list" ],
                    "parameter_enable": 1,
                    "patching_rect": [ 324.0, 394.0, 69.0, 91.0 ],
                    "saved_attribute_attributes": {
                        "valueof": {
                            "parameter_longname": "live.gain~",
                            "parameter_mmax": 6.0,
                            "parameter_mmin": -70.0,
                            "parameter_modmode": 3,
                            "parameter_shortname": "live.gain~",
                            "parameter_type": 0,
                            "parameter_unitstyle": 4
                        }
                    },
                    "varname": "live.gain~"
                }
            },
            {
                "box": {
                    "id": "obj-33",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 38.0, 90.0, 84.0, 22.0 ],
                    "presentation_linecount": 2,
                    "text": "shape dodeca"
                }
            },
            {
                "box": {
                    "id": "obj-31",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 38.0, 118.0, 69.0, 22.0 ],
                    "text": "shape tetra"
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 37.0, 145.0, 71.0, 22.0 ],
                    "text": "shape cube"
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 358.0, 741.0, 35.0, 22.0 ],
                    "text": "rz $1"
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 321.0, 741.0, 35.0, 22.0 ],
                    "text": "ry $1"
                }
            },
            {
                "box": {
                    "id": "obj-22",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 284.0, 741.0, 35.0, 22.0 ],
                    "text": "rx $1"
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 376.0, 799.0, 71.0, 22.0 ],
                    "text": "topology $1"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-17",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 411.0, 748.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 411.0, 710.0, 41.0, 22.0 ],
                    "text": "abs 0."
                }
            },
            {
                "box": {
                    "id": "obj-13",
                    "linecount": 31,
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 16.0, 474.0, 150.0, 422.0 ],
                    "text": "Messages:\n//   shape cube\n//   between cube icosahedron\n//   morph 0.5\n//   transition tetra dodeca 0.35\n//   dual\n//   next / prev\n//   rotate x 90\n//   rx 15 / ry -30 / rz 45\n//   reset\n//\n// Parameter forwarding:\n//   harmonicity 0.5\n//   harmonic_span 0.25\n//   topology 0.8\n//   geometry_depth 0.6\n//   geometry_depth_slew_ms 100\n//   pauli_depth 0.2\n//   morph_slew_ms 750\n//   noise_amount 0.22\n//   noise_decay_ms 22\n//   onset_threshold 0.012\n//   onset_sensitivity 10\n//   noise_color 0.72\n//   noise_floor 0\n//   rotation_slew_ms 100\n//   diffusion_slew_ms 100"
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 606.0, 94.0, 35.0, 22.0 ],
                    "text": "open"
                }
            },
            {
                "box": {
                    "id": "obj-84",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 193.75, 445.0, 29.5, 22.0 ],
                    "text": "* 2."
                }
            },
            {
                "box": {
                    "id": "obj-83",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 216.0, 144.0, 47.0, 22.0 ],
                    "text": "* 0.125"
                }
            },
            {
                "box": {
                    "id": "obj-82",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 216.0, 110.0, 47.0, 22.0 ],
                    "text": "* 0.125"
                }
            },
            {
                "box": {
                    "id": "obj-81",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 166.0, 77.0, 47.0, 22.0 ],
                    "text": "* 0.125"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-79",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 318.0, 597.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-80",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 318.0, 559.0, 41.0, 22.0 ],
                    "text": "abs 0."
                }
            },
            {
                "box": {
                    "id": "obj-78",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 318.0, 631.0, 87.0, 22.0 ],
                    "text": "pauli_depth $1"
                }
            },
            {
                "box": {
                    "id": "obj-77",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 183.5, 508.0, 112.0, 22.0 ],
                    "text": "geometry_depth $1"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-76",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 183.5, 479.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-74",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 188.0, 417.0, 41.0, 22.0 ],
                    "text": "abs 0."
                }
            },
            {
                "box": {
                    "id": "obj-73",
                    "linecount": 2,
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 183.5, 354.0, 65.0, 35.0 ],
                    "text": "geometry_morph $1"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-71",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 184.0, 324.0, 64.5, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-69",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 183.5, 294.0, 33.0, 22.0 ],
                    "text": "* 0.5"
                }
            },
            {
                "box": {
                    "id": "obj-68",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "float" ],
                    "patching_rect": [ 183.5, 263.0, 29.5, 22.0 ],
                    "text": "+ 1."
                }
            },
            {
                "box": {
                    "id": "obj-66",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 148.0, 172.0, 65.0, 22.0 ],
                    "text": "rotate z $1"
                }
            },
            {
                "box": {
                    "id": "obj-65",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 148.0, 144.0, 65.0, 22.0 ],
                    "text": "rotate y $1"
                }
            },
            {
                "box": {
                    "id": "obj-64",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 148.0, 110.0, 65.0, 22.0 ],
                    "text": "rotate x $1"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-55",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 738.0, 787.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-56",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 730.0, 749.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-57",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 667.0, 787.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-58",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 659.0, 749.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-59",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 601.0, 787.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-60",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 593.0, 749.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-61",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 528.0, 787.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-62",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 520.0, 749.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-53",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 738.0, 702.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-54",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 730.0, 664.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-51",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 667.0, 702.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-52",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 659.0, 664.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-49",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 601.0, 702.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-50",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 593.0, 664.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-48",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 528.0, 702.0, 34.0, 22.0 ],
                    "text": "line~"
                }
            },
            {
                "box": {
                    "hidden": 1,
                    "id": "obj-47",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 520.0, 664.0, 64.0, 22.0 ],
                    "text": "pack 0. 30"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-39",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 782.0, 315.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-40",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 730.0, 315.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-41",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 678.0, 315.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-42",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 618.0, 315.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-38",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 782.0, 281.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-37",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 730.0, 281.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-36",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 678.0, 281.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-32",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 619.0, 275.0, 50.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-30",
                    "linecount": 2,
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 9,
                    "outlettype": [ "", "", "", "", "", "", "", "", "" ],
                    "patching_rect": [ 657.0, 234.0, 243.0, 35.0 ],
                    "text": "OSC-route /XXII /YYII /ZZII /IXXI /IYYI /IZZI /IIXX /IIYY"
                }
            },
            {
                "box": {
                    "id": "obj-29",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "" ],
                    "patching_rect": [ 657.0, 204.0, 98.0, 22.0 ],
                    "text": "OSC-route /pauli"
                }
            },
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 657.0, 174.0, 97.0, 22.0 ],
                    "text": "udpreceive 7400"
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "linecount": 3,
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "" ],
                    "patching_rect": [ 21.0, 218.0, 149.0, 49.0 ],
                    "saved_object_attributes": {
                        "filename": "qmw_platonic_geometry_controller_v1.js",
                        "parameter_enable": 0
                    },
                    "text": "js qmw_platonic_geometry_controller_v1.js"
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 582.0, 55.0, 41.0, 22.0 ],
                    "text": "loop 1"
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "ezdac~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [ 324.0, 508.0, 45.0, 45.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "toggle",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "int" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 474.0, 50.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "bang" ],
                    "patching_rect": [ 467.0, 94.0, 95.0, 22.0 ],
                    "text": "sfplay~ @loop 1"
                }
            },
            {
                "box": {
                    "code": "// qmw_platonic_geometry_reverb_v1.genexpr\n// Twenty-node morphing Platonic feedback-delay network for Max Gen~.\n//\n// in1      mono audio input\n// in2..in9 eight Pauli-correlation signals in the range -1..1\n// out1     left reverberant output\n// out2     right reverberant output\n//\n// solid IDs:\n// 0 tetrahedron  {3,3}\n// 1 cube         {4,3}\n// 2 octahedron   {3,4}\n// 3 dodecahedron {5,3}\n// 4 icosahedron  {3,5}\n//\n// The engine keeps twenty DSP nodes and morphs four linked fields:\n// activation, spherical coordinates, overtone-derived delay ratios,\n// and normalized graph adjacency. This allows continuous topology changes.\n\nParam solid_a(1);\nParam solid_b(2);\nParam geometry_morph(0);\nParam morph_slew_ms(500);\nParam rotation_slew_ms(100);\nParam size(0.45);\nParam decay(0.72);\nParam diffusion(0.72);\nParam diffusion_slew_ms(100);\nParam absorb(0.35);\nParam tilt(0);\nParam topology(0.80);\nParam geometry_depth(0.55);\nParam geometry_depth_slew_ms(100);\nParam harmonicity(0.25);\nParam harmonic_span(0.22);\nParam pauli_depth(0.16);\nParam rot_x(0);\nParam rot_y(0);\nParam rot_z(0);\nParam width(0.90);\nParam freeze(0);\nParam input_gain(0.25);\n\n// Onset-sensitive broadband excitation.\nParam noise_amount(0.22);\nParam noise_decay_ms(22);\nParam onset_threshold(0.012);\nParam onset_sensitivity(10);\nParam noise_color(0.72);\nParam noise_floor(0);\n\nParam output_gain(0.40);\n\nDelay dl1(384000);\nDelay dl2(384000);\nDelay dl3(384000);\nDelay dl4(384000);\nDelay dl5(384000);\nDelay dl6(384000);\nDelay dl7(384000);\nDelay dl8(384000);\nDelay dl9(384000);\nDelay dl10(384000);\nDelay dl11(384000);\nDelay dl12(384000);\nDelay dl13(384000);\nDelay dl14(384000);\nDelay dl15(384000);\nDelay dl16(384000);\nDelay dl17(384000);\nDelay dl18(384000);\nDelay dl19(384000);\nDelay dl20(384000);\n\nHistory lp1(0);\nHistory lp2(0);\nHistory lp3(0);\nHistory lp4(0);\nHistory lp5(0);\nHistory lp6(0);\nHistory lp7(0);\nHistory lp8(0);\nHistory lp9(0);\nHistory lp10(0);\nHistory lp11(0);\nHistory lp12(0);\nHistory lp13(0);\nHistory lp14(0);\nHistory lp15(0);\nHistory lp16(0);\nHistory lp17(0);\nHistory lp18(0);\nHistory lp19(0);\nHistory lp20(0);\n\nHistory apz1(0);\nHistory apz2(0);\nHistory apz3(0);\nHistory apz4(0);\nHistory onset_fast(0);\nHistory onset_slow(0);\nHistory noise_env(0);\nHistory noise_lp(0);\nHistory diffusion_z(0.72);\nHistory morph_z(0);\nHistory morph_z2(0);\nHistory geometry_depth_z(0.55);\nHistory rot_x_z(0);\nHistory rot_y_z(0);\nHistory rot_z_z(0);\n\nsr = samplerate;\npi2 = 6.28318530718;\n\n// Input diffusion.\ndiffusion_target = clamp(diffusion, 0, 1);\ndiffusion_seconds = max(diffusion_slew_ms, 0) * 0.001;\ndiffusion_coeff = (diffusion_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * diffusion_seconds)));\ndiffusion_z = diffusion_z + diffusion_coeff * (diffusion_target - diffusion_z);\ndiff_g = 0.15 + 0.70 * diffusion_z;\ninput_signal = in1 * input_gain;\ninput_abs = abs(input_signal);\n\n// A fast-minus-slow envelope detector avoids per-sample derivative scaling,\n// so the onset threshold remains comparable across sample rates.\nonset_fast_samples = max(0.0015 * sr, 1);\nonset_slow_samples = max(0.035 * sr, 1);\nonset_fast_coeff = exp(-1 / onset_fast_samples);\nonset_slow_coeff = exp(-1 / onset_slow_samples);\nonset_fast = input_abs + onset_fast_coeff * (onset_fast - input_abs);\nonset_slow = input_abs + onset_slow_coeff * (onset_slow - input_abs);\nonset_strength = clamp(\n    (onset_fast - onset_slow - max(onset_threshold, 0))\n    * max(onset_sensitivity, 0),\n    0,\n    1\n);\n\nnoise_decay_samples = max(noise_decay_ms, 0.1) * 0.001 * sr;\nnoise_decay_coeff = exp(-1 / max(noise_decay_samples, 1));\nnoise_env = max(noise_env * noise_decay_coeff, onset_strength);\n\nraw_noise = noise();\nnoise_color_norm = clamp(noise_color, 0, 1);\nnoise_cut_hz = min(500 + 11500 * noise_color_norm, 0.45 * sr);\nnoise_cut_coeff = 1 - exp((-pi2 * noise_cut_hz) / sr);\nnoise_lp = noise_lp + noise_cut_coeff * (raw_noise - noise_lp);\ncolored_noise = mix(noise_lp, raw_noise, noise_color_norm);\n\nburst_excitation =\n    colored_noise\n    * noise_env\n    * clamp(noise_amount, 0, 1);\ncontinuous_excitation =\n    colored_noise\n    * clamp(noise_floor, 0, 0.25);\nexcitation = input_signal + burst_excitation + continuous_excitation;\n\nx = excitation;\na1d = x - diff_g * apz1;\ny1d = apz1 + diff_g * a1d;\napz1 = a1d;\na2d = y1d - diff_g * apz2;\ny2d = apz2 + diff_g * a2d;\napz2 = a2d;\na3d = y2d - diff_g * apz3;\ny3d = apz3 + diff_g * a3d;\napz3 = a3d;\na4d = y3d - diff_g * apz4;\ndiffused = apz4 + diff_g * a4d;\napz4 = a4d;\n\n// Smooth the global geometry morph internally.\ntarget_morph = clamp(geometry_morph, 0, 1);\nmorph_seconds = max(morph_slew_ms, 0) * 0.001;\nmorph_coeff = (morph_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * morph_seconds)));\nmorph_z = morph_z + morph_coeff * (target_morph - morph_z);\nmorph_z2 = morph_z2 + morph_coeff * (morph_z - morph_z2);\nmorph_phase = clamp(morph_z2, 0, 1);\nmorph = morph_phase * morph_phase * (3 - 2 * morph_phase);\n\nsa = clamp(floor(solid_a + 0.5), 0, 4);\nsb = clamp(floor(solid_b + 0.5), 0, 4);\n\nraw1 = clamp(in2, -1, 1);\nraw2 = clamp(in3, -1, 1);\nraw3 = clamp(in4, -1, 1);\nraw4 = clamp(in5, -1, 1);\nraw5 = clamp(in6, -1, 1);\nraw6 = clamp(in7, -1, 1);\nraw7 = clamp(in8, -1, 1);\nraw8 = clamp(in9, -1, 1);\n\n// Source-solid field.\naA1 = 0;\nxA1 = -0.577350269;\nyA1 = -0.577350269;\nzA1 = -0.577350269;\nhA1 = 0;\npA1 = raw1;\naA2 = 1;\nxA2 = -0.577350269;\nyA2 = -0.577350269;\nzA2 = 0.577350269;\nhA2 = -0.304098831;\npA2 = raw3;\naA3 = 1;\nxA3 = -0.577350269;\nyA3 = 0.577350269;\nzA3 = -0.577350269;\nhA3 = 0.101366277;\npA3 = raw2;\naA4 = 0;\nxA4 = -0.577350269;\nyA4 = 0.577350269;\nzA4 = 0.577350269;\nhA4 = 0;\npA4 = raw1;\naA5 = 1;\nxA5 = 0.577350269;\nyA5 = -0.577350269;\nzA5 = -0.577350269;\nhA5 = 0.794513458;\npA5 = raw1;\naA6 = 0;\nxA6 = 0.577350269;\nyA6 = -0.577350269;\nzA6 = 0.577350269;\nhA6 = 0;\npA6 = raw1;\naA7 = 0;\nxA7 = 0.577350269;\nyA7 = 0.577350269;\nzA7 = -0.577350269;\nhA7 = 0;\npA7 = raw1;\naA8 = 1;\nxA8 = 0.577350269;\nyA8 = 0.577350269;\nzA8 = 0.577350269;\nhA8 = -0.591780904;\npA8 = raw4;\naA9 = 0;\nxA9 = 0;\nyA9 = -0.35682209;\nzA9 = -0.934172359;\nhA9 = 0;\npA9 = raw1;\naA10 = 0;\nxA10 = -0.35682209;\nyA10 = -0.934172359;\nzA10 = 0;\nhA10 = 0;\npA10 = raw1;\naA11 = 0;\nxA11 = -0.934172359;\nyA11 = 0;\nzA11 = -0.35682209;\nhA11 = 0;\npA11 = raw1;\naA12 = 0;\nxA12 = 0;\nyA12 = -0.35682209;\nzA12 = 0.934172359;\nhA12 = 0;\npA12 = raw1;\naA13 = 0;\nxA13 = -0.35682209;\nyA13 = 0.934172359;\nzA13 = 0;\nhA13 = 0;\npA13 = raw1;\naA14 = 0;\nxA14 = 0.934172359;\nyA14 = 0;\nzA14 = -0.35682209;\nhA14 = 0;\npA14 = raw1;\naA15 = 0;\nxA15 = 0;\nyA15 = 0.35682209;\nzA15 = -0.934172359;\nhA15 = 0;\npA15 = raw1;\naA16 = 0;\nxA16 = 0.35682209;\nyA16 = -0.934172359;\nzA16 = 0;\nhA16 = 0;\npA16 = raw1;\naA17 = 0;\nxA17 = -0.934172359;\nyA17 = 0;\nzA17 = 0.35682209;\nhA17 = 0;\npA17 = raw1;\naA18 = 0;\nxA18 = 0;\nyA18 = 0.35682209;\nzA18 = 0.934172359;\nhA18 = 0;\npA18 = raw1;\naA19 = 0;\nxA19 = 0.35682209;\nyA19 = 0.934172359;\nzA19 = 0;\nhA19 = 0;\npA19 = raw1;\naA20 = 0;\nxA20 = 0.934172359;\nyA20 = 0;\nzA20 = 0.35682209;\nhA20 = 0;\npA20 = raw1;\nif (sa == 0) {\n    aA1 = 0;\n    xA1 = -0.577350269;\n    yA1 = -0.577350269;\n    zA1 = -0.577350269;\n    hA1 = 0;\n    pA1 = raw1;\n    aA2 = 1;\n    xA2 = -0.577350269;\n    yA2 = -0.577350269;\n    zA2 = 0.577350269;\n    hA2 = -0.304098831;\n    pA2 = raw3;\n    aA3 = 1;\n    xA3 = -0.577350269;\n    yA3 = 0.577350269;\n    zA3 = -0.577350269;\n    hA3 = 0.101366277;\n    pA3 = raw2;\n    aA4 = 0;\n    xA4 = -0.577350269;\n    yA4 = 0.577350269;\n    zA4 = 0.577350269;\n    hA4 = 0;\n    pA4 = raw1;\n    aA5 = 1;\n    xA5 = 0.577350269;\n    yA5 = -0.577350269;\n    zA5 = -0.577350269;\n    hA5 = 0.794513458;\n    pA5 = raw1;\n    aA6 = 0;\n    xA6 = 0.577350269;\n    yA6 = -0.577350269;\n    zA6 = 0.577350269;\n    hA6 = 0;\n    pA6 = raw1;\n    aA7 = 0;\n    xA7 = 0.577350269;\n    yA7 = 0.577350269;\n    zA7 = -0.577350269;\n    hA7 = 0;\n    pA7 = raw1;\n    aA8 = 1;\n    xA8 = 0.577350269;\n    yA8 = 0.577350269;\n    zA8 = 0.577350269;\n    hA8 = -0.591780904;\n    pA8 = raw4;\n    aA9 = 0;\n    xA9 = 0;\n    yA9 = -0.35682209;\n    zA9 = -0.934172359;\n    hA9 = 0;\n    pA9 = raw1;\n    aA10 = 0;\n    xA10 = -0.35682209;\n    yA10 = -0.934172359;\n    zA10 = 0;\n    hA10 = 0;\n    pA10 = raw1;\n    aA11 = 0;\n    xA11 = -0.934172359;\n    yA11 = 0;\n    zA11 = -0.35682209;\n    hA11 = 0;\n    pA11 = raw1;\n    aA12 = 0;\n    xA12 = 0;\n    yA12 = -0.35682209;\n    zA12 = 0.934172359;\n    hA12 = 0;\n    pA12 = raw1;\n    aA13 = 0;\n    xA13 = -0.35682209;\n    yA13 = 0.934172359;\n    zA13 = 0;\n    hA13 = 0;\n    pA13 = raw1;\n    aA14 = 0;\n    xA14 = 0.934172359;\n    yA14 = 0;\n    zA14 = -0.35682209;\n    hA14 = 0;\n    pA14 = raw1;\n    aA15 = 0;\n    xA15 = 0;\n    yA15 = 0.35682209;\n    zA15 = -0.934172359;\n    hA15 = 0;\n    pA15 = raw1;\n    aA16 = 0;\n    xA16 = 0.35682209;\n    yA16 = -0.934172359;\n    zA16 = 0;\n    hA16 = 0;\n    pA16 = raw1;\n    aA17 = 0;\n    xA17 = -0.934172359;\n    yA17 = 0;\n    zA17 = 0.35682209;\n    hA17 = 0;\n    pA17 = raw1;\n    aA18 = 0;\n    xA18 = 0;\n    yA18 = 0.35682209;\n    zA18 = 0.934172359;\n    hA18 = 0;\n    pA18 = raw1;\n    aA19 = 0;\n    xA19 = 0.35682209;\n    yA19 = 0.934172359;\n    zA19 = 0;\n    hA19 = 0;\n    pA19 = raw1;\n    aA20 = 0;\n    xA20 = 0.934172359;\n    yA20 = 0;\n    zA20 = 0.35682209;\n    hA20 = 0;\n    pA20 = raw1;\n}\nelse if (sa == 1) {\n    aA1 = 1;\n    xA1 = -0.577350269;\n    yA1 = -0.577350269;\n    zA1 = -0.577350269;\n    hA1 = 1.325575363;\n    pA1 = raw1;\n    aA2 = 1;\n    xA2 = -0.577350269;\n    yA2 = -0.577350269;\n    zA2 = 0.577350269;\n    hA2 = -0.060718998;\n    pA2 = raw4;\n    aA3 = 1;\n    xA3 = -0.577350269;\n    yA3 = 0.577350269;\n    zA3 = -0.577350269;\n    hA3 = 0.226963074;\n    pA3 = raw3;\n    aA4 = 1;\n    xA4 = -0.577350269;\n    yA4 = 0.577350269;\n    zA4 = 0.577350269;\n    hA4 = -0.620334786;\n    pA4 = raw7;\n    aA5 = 1;\n    xA5 = 0.577350269;\n    yA5 = -0.577350269;\n    zA5 = -0.577350269;\n    hA5 = 0.632428182;\n    pA5 = raw2;\n    aA6 = 1;\n    xA6 = 0.577350269;\n    yA6 = -0.577350269;\n    zA6 = 0.577350269;\n    hA6 = -0.466184106;\n    pA6 = raw6;\n    aA7 = 1;\n    xA7 = 0.577350269;\n    yA7 = 0.577350269;\n    zA7 = -0.577350269;\n    hA7 = -0.28386255;\n    pA7 = raw5;\n    aA8 = 1;\n    xA8 = 0.577350269;\n    yA8 = 0.577350269;\n    zA8 = 0.577350269;\n    hA8 = -0.753866179;\n    pA8 = raw8;\n    aA9 = 0;\n    xA9 = 0;\n    yA9 = -0.35682209;\n    zA9 = -0.934172359;\n    hA9 = 0;\n    pA9 = raw1;\n    aA10 = 0;\n    xA10 = -0.35682209;\n    yA10 = -0.934172359;\n    zA10 = 0;\n    hA10 = 0;\n    pA10 = raw1;\n    aA11 = 0;\n    xA11 = -0.934172359;\n    yA11 = 0;\n    zA11 = -0.35682209;\n    hA11 = 0;\n    pA11 = raw1;\n    aA12 = 0;\n    xA12 = 0;\n    yA12 = -0.35682209;\n    zA12 = 0.934172359;\n    hA12 = 0;\n    pA12 = raw1;\n    aA13 = 0;\n    xA13 = -0.35682209;\n    yA13 = 0.934172359;\n    zA13 = 0;\n    hA13 = 0;\n    pA13 = raw1;\n    aA14 = 0;\n    xA14 = 0.934172359;\n    yA14 = 0;\n    zA14 = -0.35682209;\n    hA14 = 0;\n    pA14 = raw1;\n    aA15 = 0;\n    xA15 = 0;\n    yA15 = 0.35682209;\n    zA15 = -0.934172359;\n    hA15 = 0;\n    pA15 = raw1;\n    aA16 = 0;\n    xA16 = 0.35682209;\n    yA16 = -0.934172359;\n    zA16 = 0;\n    hA16 = 0;\n    pA16 = raw1;\n    aA17 = 0;\n    xA17 = -0.934172359;\n    yA17 = 0;\n    zA17 = 0.35682209;\n    hA17 = 0;\n    pA17 = raw1;\n    aA18 = 0;\n    xA18 = 0;\n    yA18 = 0.35682209;\n    zA18 = 0.934172359;\n    hA18 = 0;\n    pA18 = raw1;\n    aA19 = 0;\n    xA19 = 0.35682209;\n    yA19 = 0.934172359;\n    zA19 = 0;\n    hA19 = 0;\n    pA19 = raw1;\n    aA20 = 0;\n    xA20 = 0.934172359;\n    yA20 = 0;\n    zA20 = 0.35682209;\n    hA20 = 0;\n    pA20 = raw1;\n}\nelse if (sa == 2) {\n    aA1 = 0;\n    xA1 = -0.577350269;\n    yA1 = -0.577350269;\n    zA1 = -0.577350269;\n    hA1 = 0;\n    pA1 = raw1;\n    aA2 = 0;\n    xA2 = -0.577350269;\n    yA2 = -0.577350269;\n    zA2 = 0.577350269;\n    hA2 = 0;\n    pA2 = raw1;\n    aA3 = 0;\n    xA3 = -0.577350269;\n    yA3 = 0.577350269;\n    zA3 = -0.577350269;\n    hA3 = 0;\n    pA3 = raw1;\n    aA4 = 0;\n    xA4 = -0.577350269;\n    yA4 = 0.577350269;\n    zA4 = 0.577350269;\n    hA4 = 0;\n    pA4 = raw1;\n    aA5 = 0;\n    xA5 = 0.577350269;\n    yA5 = -0.577350269;\n    zA5 = -0.577350269;\n    hA5 = 0;\n    pA5 = raw1;\n    aA6 = 0;\n    xA6 = 0.577350269;\n    yA6 = -0.577350269;\n    zA6 = 0.577350269;\n    hA6 = 0;\n    pA6 = raw1;\n    aA7 = 0;\n    xA7 = 0.577350269;\n    yA7 = 0.577350269;\n    zA7 = -0.577350269;\n    hA7 = 0;\n    pA7 = raw1;\n    aA8 = 0;\n    xA8 = 0.577350269;\n    yA8 = 0.577350269;\n    zA8 = 0.577350269;\n    hA8 = 0;\n    pA8 = raw1;\n    aA9 = 1;\n    xA9 = 0;\n    yA9 = 0;\n    zA9 = -1;\n    hA9 = 1.096541869;\n    pA9 = raw1;\n    aA10 = 1;\n    xA10 = 0;\n    yA10 = -1;\n    zA10 = 0;\n    hA10 = 0.403394688;\n    pA10 = raw2;\n    aA11 = 1;\n    xA11 = -1;\n    yA11 = 0;\n    zA11 = 0;\n    hA11 = -0.00207042;\n    pA11 = raw3;\n    aA12 = 1;\n    xA12 = 0;\n    yA12 = 0;\n    zA12 = 1;\n    hA12 = -0.695217601;\n    pA12 = raw6;\n    aA13 = 1;\n    xA13 = 0;\n    yA13 = 1;\n    zA13 = 0;\n    hA13 = -0.512896044;\n    pA13 = raw5;\n    aA14 = 1;\n    xA14 = 1;\n    yA14 = 0;\n    zA14 = 0;\n    hA14 = -0.289752492;\n    pA14 = raw4;\n    aA15 = 0;\n    xA15 = 0;\n    yA15 = 0.35682209;\n    zA15 = -0.934172359;\n    hA15 = 0;\n    pA15 = raw1;\n    aA16 = 0;\n    xA16 = 0.35682209;\n    yA16 = -0.934172359;\n    zA16 = 0;\n    hA16 = 0;\n    pA16 = raw1;\n    aA17 = 0;\n    xA17 = -0.934172359;\n    yA17 = 0;\n    zA17 = 0.35682209;\n    hA17 = 0;\n    pA17 = raw1;\n    aA18 = 0;\n    xA18 = 0;\n    yA18 = 0.35682209;\n    zA18 = 0.934172359;\n    hA18 = 0;\n    pA18 = raw1;\n    aA19 = 0;\n    xA19 = 0.35682209;\n    yA19 = 0.934172359;\n    zA19 = 0;\n    hA19 = 0;\n    pA19 = raw1;\n    aA20 = 0;\n    xA20 = 0.934172359;\n    yA20 = 0;\n    zA20 = 0.35682209;\n    hA20 = 0;\n    pA20 = raw1;\n}\nelse if (sa == 3) {\n    aA1 = 1;\n    xA1 = -0.577350269;\n    yA1 = -0.577350269;\n    zA1 = -0.577350269;\n    hA1 = 2.116780823;\n    pA1 = raw1;\n    aA2 = 1;\n    xA2 = -0.577350269;\n    yA2 = -0.577350269;\n    zA2 = 0.577350269;\n    hA2 = -0.080443754;\n    pA2 = raw1;\n    aA3 = 1;\n    xA3 = -0.577350269;\n    yA3 = 0.577350269;\n    zA3 = -0.577350269;\n    hA3 = 0.037339281;\n    pA3 = raw8;\n    aA4 = 1;\n    xA4 = -0.577350269;\n    yA4 = 0.577350269;\n    zA4 = 0.577350269;\n    hA4 = -0.655807899;\n    pA4 = raw8;\n    aA5 = 1;\n    xA5 = 0.577350269;\n    yA5 = -0.577350269;\n    zA5 = -0.577350269;\n    hA5 = 0.507342911;\n    pA5 = raw5;\n    aA6 = 1;\n    xA6 = 0.577350269;\n    yA6 = -0.577350269;\n    zA6 = 0.577350269;\n    hA6 = -0.448168534;\n    pA6 = raw5;\n    aA7 = 1;\n    xA7 = 0.577350269;\n    yA7 = 0.577350269;\n    zA7 = -0.577350269;\n    hA7 = -0.368125827;\n    pA7 = raw4;\n    aA8 = 1;\n    xA8 = 0.577350269;\n    yA8 = 0.577350269;\n    zA8 = 0.577350269;\n    hA8 = -0.878951451;\n    pA8 = raw4;\n    aA9 = 1;\n    xA9 = 0;\n    yA9 = -0.35682209;\n    zA9 = -0.934172359;\n    hA9 = 1.423633642;\n    pA9 = raw2;\n    aA10 = 1;\n    xA10 = -0.35682209;\n    yA10 = -0.934172359;\n    zA10 = 0;\n    hA10 = 1.018168534;\n    pA10 = raw3;\n    aA11 = 1;\n    xA11 = -0.934172359;\n    yA11 = 0;\n    zA11 = -0.35682209;\n    hA11 = 0.730486462;\n    pA11 = raw4;\n    aA12 = 1;\n    xA12 = 0;\n    yA12 = -0.35682209;\n    zA12 = 0.934172359;\n    hA12 = -0.591269378;\n    pA12 = raw7;\n    aA13 = 1;\n    xA13 = -0.35682209;\n    yA13 = 0.934172359;\n    zA13 = 0;\n    hA13 = -0.522276507;\n    pA13 = raw6;\n    aA14 = 1;\n    xA14 = 0.934172359;\n    yA14 = 0;\n    zA14 = -0.35682209;\n    hA14 = -0.28111445;\n    pA14 = raw3;\n    aA15 = 1;\n    xA15 = 0;\n    yA15 = 0.35682209;\n    zA15 = -0.934172359;\n    hA15 = 0.325021354;\n    pA15 = raw6;\n    aA16 = 1;\n    xA16 = 0.35682209;\n    yA16 = -0.934172359;\n    zA16 = 0;\n    hA16 = 0.170870674;\n    pA16 = raw7;\n    aA17 = 1;\n    xA17 = -0.934172359;\n    yA17 = 0;\n    zA17 = 0.35682209;\n    hA17 = -0.18580427;\n    pA17 = raw2;\n    aA18 = 1;\n    xA18 = 0;\n    yA18 = 0.35682209;\n    zA18 = 0.934172359;\n    hA18 = -0.827658156;\n    pA18 = raw3;\n    aA19 = 1;\n    xA19 = 0.35682209;\n    yA19 = 0.934172359;\n    zA19 = 0;\n    hA19 = -0.773590935;\n    pA19 = raw2;\n    aA20 = 1;\n    xA20 = 0.934172359;\n    yA20 = 0;\n    zA20 = 0.35682209;\n    hA20 = -0.716432521;\n    pA20 = raw1;\n}\nelse if (sa == 4) {\n    aA1 = 0;\n    xA1 = -0.577350269;\n    yA1 = -0.577350269;\n    zA1 = -0.577350269;\n    hA1 = 0;\n    pA1 = raw1;\n    aA2 = 0;\n    xA2 = -0.577350269;\n    yA2 = -0.577350269;\n    zA2 = 0.577350269;\n    hA2 = 0;\n    pA2 = raw1;\n    aA3 = 0;\n    xA3 = -0.577350269;\n    yA3 = 0.577350269;\n    zA3 = -0.577350269;\n    hA3 = 0;\n    pA3 = raw1;\n    aA4 = 0;\n    xA4 = -0.577350269;\n    yA4 = 0.577350269;\n    zA4 = 0.577350269;\n    hA4 = 0;\n    pA4 = raw1;\n    aA5 = 0;\n    xA5 = 0.577350269;\n    yA5 = -0.577350269;\n    zA5 = -0.577350269;\n    hA5 = 0;\n    pA5 = raw1;\n    aA6 = 0;\n    xA6 = 0.577350269;\n    yA6 = -0.577350269;\n    zA6 = 0.577350269;\n    hA6 = 0;\n    pA6 = raw1;\n    aA7 = 0;\n    xA7 = 0.577350269;\n    yA7 = 0.577350269;\n    zA7 = -0.577350269;\n    hA7 = 0;\n    pA7 = raw1;\n    aA8 = 0;\n    xA8 = 0.577350269;\n    yA8 = 0.577350269;\n    zA8 = 0.577350269;\n    hA8 = 0;\n    pA8 = raw1;\n    aA9 = 1;\n    xA9 = 0;\n    yA9 = -0.525731112;\n    zA9 = -0.850650808;\n    hA9 = 1.665601208;\n    pA9 = raw1;\n    aA10 = 1;\n    xA10 = -0.525731112;\n    yA10 = -0.850650808;\n    zA10 = 0;\n    hA10 = 0.972454027;\n    pA10 = raw2;\n    aA11 = 1;\n    xA11 = -0.850650808;\n    yA11 = 0;\n    zA11 = -0.525731112;\n    hA11 = 0.566988919;\n    pA11 = raw3;\n    aA12 = 1;\n    xA12 = 0;\n    yA12 = -0.525731112;\n    zA12 = 0.850650808;\n    hA12 = -0.413840334;\n    pA12 = raw8;\n    aA13 = 1;\n    xA13 = -0.525731112;\n    yA13 = 0.850650808;\n    zA13 = 0;\n    hA13 = -0.531623369;\n    pA13 = raw1;\n    aA14 = 1;\n    xA14 = 0.850650808;\n    yA14 = 0;\n    zA14 = -0.525731112;\n    hA14 = -0.280308941;\n    pA14 = raw7;\n    aA15 = 1;\n    xA15 = 0;\n    yA15 = 0.525731112;\n    zA15 = -0.850650808;\n    hA15 = 0.056163296;\n    pA15 = raw5;\n    aA16 = 1;\n    xA16 = 0.525731112;\n    yA16 = -0.850650808;\n    zA16 = 0;\n    hA16 = 0.279306847;\n    pA16 = raw4;\n    aA17 = 1;\n    xA17 = -0.850650808;\n    yA17 = 0;\n    zA17 = 0.525731112;\n    hA17 = -0.126158261;\n    pA17 = raw6;\n    aA18 = 1;\n    xA18 = 0;\n    yA18 = 0.525731112;\n    zA18 = 0.850650808;\n    hA18 = -0.819305442;\n    pA18 = raw4;\n    aA19 = 1;\n    xA19 = 0.525731112;\n    yA19 = 0.850650808;\n    zA19 = 0;\n    hA19 = -0.732294065;\n    pA19 = raw3;\n    aA20 = 1;\n    xA20 = 0.850650808;\n    yA20 = 0;\n    zA20 = 0.525731112;\n    hA20 = -0.636983885;\n    pA20 = raw2;\n}\n\n// Destination-solid field.\naB1 = 0;\nxB1 = -0.577350269;\nyB1 = -0.577350269;\nzB1 = -0.577350269;\nhB1 = 0;\npB1 = raw1;\naB2 = 1;\nxB2 = -0.577350269;\nyB2 = -0.577350269;\nzB2 = 0.577350269;\nhB2 = -0.304098831;\npB2 = raw3;\naB3 = 1;\nxB3 = -0.577350269;\nyB3 = 0.577350269;\nzB3 = -0.577350269;\nhB3 = 0.101366277;\npB3 = raw2;\naB4 = 0;\nxB4 = -0.577350269;\nyB4 = 0.577350269;\nzB4 = 0.577350269;\nhB4 = 0;\npB4 = raw1;\naB5 = 1;\nxB5 = 0.577350269;\nyB5 = -0.577350269;\nzB5 = -0.577350269;\nhB5 = 0.794513458;\npB5 = raw1;\naB6 = 0;\nxB6 = 0.577350269;\nyB6 = -0.577350269;\nzB6 = 0.577350269;\nhB6 = 0;\npB6 = raw1;\naB7 = 0;\nxB7 = 0.577350269;\nyB7 = 0.577350269;\nzB7 = -0.577350269;\nhB7 = 0;\npB7 = raw1;\naB8 = 1;\nxB8 = 0.577350269;\nyB8 = 0.577350269;\nzB8 = 0.577350269;\nhB8 = -0.591780904;\npB8 = raw4;\naB9 = 0;\nxB9 = 0;\nyB9 = -0.35682209;\nzB9 = -0.934172359;\nhB9 = 0;\npB9 = raw1;\naB10 = 0;\nxB10 = -0.35682209;\nyB10 = -0.934172359;\nzB10 = 0;\nhB10 = 0;\npB10 = raw1;\naB11 = 0;\nxB11 = -0.934172359;\nyB11 = 0;\nzB11 = -0.35682209;\nhB11 = 0;\npB11 = raw1;\naB12 = 0;\nxB12 = 0;\nyB12 = -0.35682209;\nzB12 = 0.934172359;\nhB12 = 0;\npB12 = raw1;\naB13 = 0;\nxB13 = -0.35682209;\nyB13 = 0.934172359;\nzB13 = 0;\nhB13 = 0;\npB13 = raw1;\naB14 = 0;\nxB14 = 0.934172359;\nyB14 = 0;\nzB14 = -0.35682209;\nhB14 = 0;\npB14 = raw1;\naB15 = 0;\nxB15 = 0;\nyB15 = 0.35682209;\nzB15 = -0.934172359;\nhB15 = 0;\npB15 = raw1;\naB16 = 0;\nxB16 = 0.35682209;\nyB16 = -0.934172359;\nzB16 = 0;\nhB16 = 0;\npB16 = raw1;\naB17 = 0;\nxB17 = -0.934172359;\nyB17 = 0;\nzB17 = 0.35682209;\nhB17 = 0;\npB17 = raw1;\naB18 = 0;\nxB18 = 0;\nyB18 = 0.35682209;\nzB18 = 0.934172359;\nhB18 = 0;\npB18 = raw1;\naB19 = 0;\nxB19 = 0.35682209;\nyB19 = 0.934172359;\nzB19 = 0;\nhB19 = 0;\npB19 = raw1;\naB20 = 0;\nxB20 = 0.934172359;\nyB20 = 0;\nzB20 = 0.35682209;\nhB20 = 0;\npB20 = raw1;\nif (sb == 0) {\n    aB1 = 0;\n    xB1 = -0.577350269;\n    yB1 = -0.577350269;\n    zB1 = -0.577350269;\n    hB1 = 0;\n    pB1 = raw1;\n    aB2 = 1;\n    xB2 = -0.577350269;\n    yB2 = -0.577350269;\n    zB2 = 0.577350269;\n    hB2 = -0.304098831;\n    pB2 = raw3;\n    aB3 = 1;\n    xB3 = -0.577350269;\n    yB3 = 0.577350269;\n    zB3 = -0.577350269;\n    hB3 = 0.101366277;\n    pB3 = raw2;\n    aB4 = 0;\n    xB4 = -0.577350269;\n    yB4 = 0.577350269;\n    zB4 = 0.577350269;\n    hB4 = 0;\n    pB4 = raw1;\n    aB5 = 1;\n    xB5 = 0.577350269;\n    yB5 = -0.577350269;\n    zB5 = -0.577350269;\n    hB5 = 0.794513458;\n    pB5 = raw1;\n    aB6 = 0;\n    xB6 = 0.577350269;\n    yB6 = -0.577350269;\n    zB6 = 0.577350269;\n    hB6 = 0;\n    pB6 = raw1;\n    aB7 = 0;\n    xB7 = 0.577350269;\n    yB7 = 0.577350269;\n    zB7 = -0.577350269;\n    hB7 = 0;\n    pB7 = raw1;\n    aB8 = 1;\n    xB8 = 0.577350269;\n    yB8 = 0.577350269;\n    zB8 = 0.577350269;\n    hB8 = -0.591780904;\n    pB8 = raw4;\n    aB9 = 0;\n    xB9 = 0;\n    yB9 = -0.35682209;\n    zB9 = -0.934172359;\n    hB9 = 0;\n    pB9 = raw1;\n    aB10 = 0;\n    xB10 = -0.35682209;\n    yB10 = -0.934172359;\n    zB10 = 0;\n    hB10 = 0;\n    pB10 = raw1;\n    aB11 = 0;\n    xB11 = -0.934172359;\n    yB11 = 0;\n    zB11 = -0.35682209;\n    hB11 = 0;\n    pB11 = raw1;\n    aB12 = 0;\n    xB12 = 0;\n    yB12 = -0.35682209;\n    zB12 = 0.934172359;\n    hB12 = 0;\n    pB12 = raw1;\n    aB13 = 0;\n    xB13 = -0.35682209;\n    yB13 = 0.934172359;\n    zB13 = 0;\n    hB13 = 0;\n    pB13 = raw1;\n    aB14 = 0;\n    xB14 = 0.934172359;\n    yB14 = 0;\n    zB14 = -0.35682209;\n    hB14 = 0;\n    pB14 = raw1;\n    aB15 = 0;\n    xB15 = 0;\n    yB15 = 0.35682209;\n    zB15 = -0.934172359;\n    hB15 = 0;\n    pB15 = raw1;\n    aB16 = 0;\n    xB16 = 0.35682209;\n    yB16 = -0.934172359;\n    zB16 = 0;\n    hB16 = 0;\n    pB16 = raw1;\n    aB17 = 0;\n    xB17 = -0.934172359;\n    yB17 = 0;\n    zB17 = 0.35682209;\n    hB17 = 0;\n    pB17 = raw1;\n    aB18 = 0;\n    xB18 = 0;\n    yB18 = 0.35682209;\n    zB18 = 0.934172359;\n    hB18 = 0;\n    pB18 = raw1;\n    aB19 = 0;\n    xB19 = 0.35682209;\n    yB19 = 0.934172359;\n    zB19 = 0;\n    hB19 = 0;\n    pB19 = raw1;\n    aB20 = 0;\n    xB20 = 0.934172359;\n    yB20 = 0;\n    zB20 = 0.35682209;\n    hB20 = 0;\n    pB20 = raw1;\n}\nelse if (sb == 1) {\n    aB1 = 1;\n    xB1 = -0.577350269;\n    yB1 = -0.577350269;\n    zB1 = -0.577350269;\n    hB1 = 1.325575363;\n    pB1 = raw1;\n    aB2 = 1;\n    xB2 = -0.577350269;\n    yB2 = -0.577350269;\n    zB2 = 0.577350269;\n    hB2 = -0.060718998;\n    pB2 = raw4;\n    aB3 = 1;\n    xB3 = -0.577350269;\n    yB3 = 0.577350269;\n    zB3 = -0.577350269;\n    hB3 = 0.226963074;\n    pB3 = raw3;\n    aB4 = 1;\n    xB4 = -0.577350269;\n    yB4 = 0.577350269;\n    zB4 = 0.577350269;\n    hB4 = -0.620334786;\n    pB4 = raw7;\n    aB5 = 1;\n    xB5 = 0.577350269;\n    yB5 = -0.577350269;\n    zB5 = -0.577350269;\n    hB5 = 0.632428182;\n    pB5 = raw2;\n    aB6 = 1;\n    xB6 = 0.577350269;\n    yB6 = -0.577350269;\n    zB6 = 0.577350269;\n    hB6 = -0.466184106;\n    pB6 = raw6;\n    aB7 = 1;\n    xB7 = 0.577350269;\n    yB7 = 0.577350269;\n    zB7 = -0.577350269;\n    hB7 = -0.28386255;\n    pB7 = raw5;\n    aB8 = 1;\n    xB8 = 0.577350269;\n    yB8 = 0.577350269;\n    zB8 = 0.577350269;\n    hB8 = -0.753866179;\n    pB8 = raw8;\n    aB9 = 0;\n    xB9 = 0;\n    yB9 = -0.35682209;\n    zB9 = -0.934172359;\n    hB9 = 0;\n    pB9 = raw1;\n    aB10 = 0;\n    xB10 = -0.35682209;\n    yB10 = -0.934172359;\n    zB10 = 0;\n    hB10 = 0;\n    pB10 = raw1;\n    aB11 = 0;\n    xB11 = -0.934172359;\n    yB11 = 0;\n    zB11 = -0.35682209;\n    hB11 = 0;\n    pB11 = raw1;\n    aB12 = 0;\n    xB12 = 0;\n    yB12 = -0.35682209;\n    zB12 = 0.934172359;\n    hB12 = 0;\n    pB12 = raw1;\n    aB13 = 0;\n    xB13 = -0.35682209;\n    yB13 = 0.934172359;\n    zB13 = 0;\n    hB13 = 0;\n    pB13 = raw1;\n    aB14 = 0;\n    xB14 = 0.934172359;\n    yB14 = 0;\n    zB14 = -0.35682209;\n    hB14 = 0;\n    pB14 = raw1;\n    aB15 = 0;\n    xB15 = 0;\n    yB15 = 0.35682209;\n    zB15 = -0.934172359;\n    hB15 = 0;\n    pB15 = raw1;\n    aB16 = 0;\n    xB16 = 0.35682209;\n    yB16 = -0.934172359;\n    zB16 = 0;\n    hB16 = 0;\n    pB16 = raw1;\n    aB17 = 0;\n    xB17 = -0.934172359;\n    yB17 = 0;\n    zB17 = 0.35682209;\n    hB17 = 0;\n    pB17 = raw1;\n    aB18 = 0;\n    xB18 = 0;\n    yB18 = 0.35682209;\n    zB18 = 0.934172359;\n    hB18 = 0;\n    pB18 = raw1;\n    aB19 = 0;\n    xB19 = 0.35682209;\n    yB19 = 0.934172359;\n    zB19 = 0;\n    hB19 = 0;\n    pB19 = raw1;\n    aB20 = 0;\n    xB20 = 0.934172359;\n    yB20 = 0;\n    zB20 = 0.35682209;\n    hB20 = 0;\n    pB20 = raw1;\n}\nelse if (sb == 2) {\n    aB1 = 0;\n    xB1 = -0.577350269;\n    yB1 = -0.577350269;\n    zB1 = -0.577350269;\n    hB1 = 0;\n    pB1 = raw1;\n    aB2 = 0;\n    xB2 = -0.577350269;\n    yB2 = -0.577350269;\n    zB2 = 0.577350269;\n    hB2 = 0;\n    pB2 = raw1;\n    aB3 = 0;\n    xB3 = -0.577350269;\n    yB3 = 0.577350269;\n    zB3 = -0.577350269;\n    hB3 = 0;\n    pB3 = raw1;\n    aB4 = 0;\n    xB4 = -0.577350269;\n    yB4 = 0.577350269;\n    zB4 = 0.577350269;\n    hB4 = 0;\n    pB4 = raw1;\n    aB5 = 0;\n    xB5 = 0.577350269;\n    yB5 = -0.577350269;\n    zB5 = -0.577350269;\n    hB5 = 0;\n    pB5 = raw1;\n    aB6 = 0;\n    xB6 = 0.577350269;\n    yB6 = -0.577350269;\n    zB6 = 0.577350269;\n    hB6 = 0;\n    pB6 = raw1;\n    aB7 = 0;\n    xB7 = 0.577350269;\n    yB7 = 0.577350269;\n    zB7 = -0.577350269;\n    hB7 = 0;\n    pB7 = raw1;\n    aB8 = 0;\n    xB8 = 0.577350269;\n    yB8 = 0.577350269;\n    zB8 = 0.577350269;\n    hB8 = 0;\n    pB8 = raw1;\n    aB9 = 1;\n    xB9 = 0;\n    yB9 = 0;\n    zB9 = -1;\n    hB9 = 1.096541869;\n    pB9 = raw1;\n    aB10 = 1;\n    xB10 = 0;\n    yB10 = -1;\n    zB10 = 0;\n    hB10 = 0.403394688;\n    pB10 = raw2;\n    aB11 = 1;\n    xB11 = -1;\n    yB11 = 0;\n    zB11 = 0;\n    hB11 = -0.00207042;\n    pB11 = raw3;\n    aB12 = 1;\n    xB12 = 0;\n    yB12 = 0;\n    zB12 = 1;\n    hB12 = -0.695217601;\n    pB12 = raw6;\n    aB13 = 1;\n    xB13 = 0;\n    yB13 = 1;\n    zB13 = 0;\n    hB13 = -0.512896044;\n    pB13 = raw5;\n    aB14 = 1;\n    xB14 = 1;\n    yB14 = 0;\n    zB14 = 0;\n    hB14 = -0.289752492;\n    pB14 = raw4;\n    aB15 = 0;\n    xB15 = 0;\n    yB15 = 0.35682209;\n    zB15 = -0.934172359;\n    hB15 = 0;\n    pB15 = raw1;\n    aB16 = 0;\n    xB16 = 0.35682209;\n    yB16 = -0.934172359;\n    zB16 = 0;\n    hB16 = 0;\n    pB16 = raw1;\n    aB17 = 0;\n    xB17 = -0.934172359;\n    yB17 = 0;\n    zB17 = 0.35682209;\n    hB17 = 0;\n    pB17 = raw1;\n    aB18 = 0;\n    xB18 = 0;\n    yB18 = 0.35682209;\n    zB18 = 0.934172359;\n    hB18 = 0;\n    pB18 = raw1;\n    aB19 = 0;\n    xB19 = 0.35682209;\n    yB19 = 0.934172359;\n    zB19 = 0;\n    hB19 = 0;\n    pB19 = raw1;\n    aB20 = 0;\n    xB20 = 0.934172359;\n    yB20 = 0;\n    zB20 = 0.35682209;\n    hB20 = 0;\n    pB20 = raw1;\n}\nelse if (sb == 3) {\n    aB1 = 1;\n    xB1 = -0.577350269;\n    yB1 = -0.577350269;\n    zB1 = -0.577350269;\n    hB1 = 2.116780823;\n    pB1 = raw1;\n    aB2 = 1;\n    xB2 = -0.577350269;\n    yB2 = -0.577350269;\n    zB2 = 0.577350269;\n    hB2 = -0.080443754;\n    pB2 = raw1;\n    aB3 = 1;\n    xB3 = -0.577350269;\n    yB3 = 0.577350269;\n    zB3 = -0.577350269;\n    hB3 = 0.037339281;\n    pB3 = raw8;\n    aB4 = 1;\n    xB4 = -0.577350269;\n    yB4 = 0.577350269;\n    zB4 = 0.577350269;\n    hB4 = -0.655807899;\n    pB4 = raw8;\n    aB5 = 1;\n    xB5 = 0.577350269;\n    yB5 = -0.577350269;\n    zB5 = -0.577350269;\n    hB5 = 0.507342911;\n    pB5 = raw5;\n    aB6 = 1;\n    xB6 = 0.577350269;\n    yB6 = -0.577350269;\n    zB6 = 0.577350269;\n    hB6 = -0.448168534;\n    pB6 = raw5;\n    aB7 = 1;\n    xB7 = 0.577350269;\n    yB7 = 0.577350269;\n    zB7 = -0.577350269;\n    hB7 = -0.368125827;\n    pB7 = raw4;\n    aB8 = 1;\n    xB8 = 0.577350269;\n    yB8 = 0.577350269;\n    zB8 = 0.577350269;\n    hB8 = -0.878951451;\n    pB8 = raw4;\n    aB9 = 1;\n    xB9 = 0;\n    yB9 = -0.35682209;\n    zB9 = -0.934172359;\n    hB9 = 1.423633642;\n    pB9 = raw2;\n    aB10 = 1;\n    xB10 = -0.35682209;\n    yB10 = -0.934172359;\n    zB10 = 0;\n    hB10 = 1.018168534;\n    pB10 = raw3;\n    aB11 = 1;\n    xB11 = -0.934172359;\n    yB11 = 0;\n    zB11 = -0.35682209;\n    hB11 = 0.730486462;\n    pB11 = raw4;\n    aB12 = 1;\n    xB12 = 0;\n    yB12 = -0.35682209;\n    zB12 = 0.934172359;\n    hB12 = -0.591269378;\n    pB12 = raw7;\n    aB13 = 1;\n    xB13 = -0.35682209;\n    yB13 = 0.934172359;\n    zB13 = 0;\n    hB13 = -0.522276507;\n    pB13 = raw6;\n    aB14 = 1;\n    xB14 = 0.934172359;\n    yB14 = 0;\n    zB14 = -0.35682209;\n    hB14 = -0.28111445;\n    pB14 = raw3;\n    aB15 = 1;\n    xB15 = 0;\n    yB15 = 0.35682209;\n    zB15 = -0.934172359;\n    hB15 = 0.325021354;\n    pB15 = raw6;\n    aB16 = 1;\n    xB16 = 0.35682209;\n    yB16 = -0.934172359;\n    zB16 = 0;\n    hB16 = 0.170870674;\n    pB16 = raw7;\n    aB17 = 1;\n    xB17 = -0.934172359;\n    yB17 = 0;\n    zB17 = 0.35682209;\n    hB17 = -0.18580427;\n    pB17 = raw2;\n    aB18 = 1;\n    xB18 = 0;\n    yB18 = 0.35682209;\n    zB18 = 0.934172359;\n    hB18 = -0.827658156;\n    pB18 = raw3;\n    aB19 = 1;\n    xB19 = 0.35682209;\n    yB19 = 0.934172359;\n    zB19 = 0;\n    hB19 = -0.773590935;\n    pB19 = raw2;\n    aB20 = 1;\n    xB20 = 0.934172359;\n    yB20 = 0;\n    zB20 = 0.35682209;\n    hB20 = -0.716432521;\n    pB20 = raw1;\n}\nelse if (sb == 4) {\n    aB1 = 0;\n    xB1 = -0.577350269;\n    yB1 = -0.577350269;\n    zB1 = -0.577350269;\n    hB1 = 0;\n    pB1 = raw1;\n    aB2 = 0;\n    xB2 = -0.577350269;\n    yB2 = -0.577350269;\n    zB2 = 0.577350269;\n    hB2 = 0;\n    pB2 = raw1;\n    aB3 = 0;\n    xB3 = -0.577350269;\n    yB3 = 0.577350269;\n    zB3 = -0.577350269;\n    hB3 = 0;\n    pB3 = raw1;\n    aB4 = 0;\n    xB4 = -0.577350269;\n    yB4 = 0.577350269;\n    zB4 = 0.577350269;\n    hB4 = 0;\n    pB4 = raw1;\n    aB5 = 0;\n    xB5 = 0.577350269;\n    yB5 = -0.577350269;\n    zB5 = -0.577350269;\n    hB5 = 0;\n    pB5 = raw1;\n    aB6 = 0;\n    xB6 = 0.577350269;\n    yB6 = -0.577350269;\n    zB6 = 0.577350269;\n    hB6 = 0;\n    pB6 = raw1;\n    aB7 = 0;\n    xB7 = 0.577350269;\n    yB7 = 0.577350269;\n    zB7 = -0.577350269;\n    hB7 = 0;\n    pB7 = raw1;\n    aB8 = 0;\n    xB8 = 0.577350269;\n    yB8 = 0.577350269;\n    zB8 = 0.577350269;\n    hB8 = 0;\n    pB8 = raw1;\n    aB9 = 1;\n    xB9 = 0;\n    yB9 = -0.525731112;\n    zB9 = -0.850650808;\n    hB9 = 1.665601208;\n    pB9 = raw1;\n    aB10 = 1;\n    xB10 = -0.525731112;\n    yB10 = -0.850650808;\n    zB10 = 0;\n    hB10 = 0.972454027;\n    pB10 = raw2;\n    aB11 = 1;\n    xB11 = -0.850650808;\n    yB11 = 0;\n    zB11 = -0.525731112;\n    hB11 = 0.566988919;\n    pB11 = raw3;\n    aB12 = 1;\n    xB12 = 0;\n    yB12 = -0.525731112;\n    zB12 = 0.850650808;\n    hB12 = -0.413840334;\n    pB12 = raw8;\n    aB13 = 1;\n    xB13 = -0.525731112;\n    yB13 = 0.850650808;\n    zB13 = 0;\n    hB13 = -0.531623369;\n    pB13 = raw1;\n    aB14 = 1;\n    xB14 = 0.850650808;\n    yB14 = 0;\n    zB14 = -0.525731112;\n    hB14 = -0.280308941;\n    pB14 = raw7;\n    aB15 = 1;\n    xB15 = 0;\n    yB15 = 0.525731112;\n    zB15 = -0.850650808;\n    hB15 = 0.056163296;\n    pB15 = raw5;\n    aB16 = 1;\n    xB16 = 0.525731112;\n    yB16 = -0.850650808;\n    zB16 = 0;\n    hB16 = 0.279306847;\n    pB16 = raw4;\n    aB17 = 1;\n    xB17 = -0.850650808;\n    yB17 = 0;\n    zB17 = 0.525731112;\n    hB17 = -0.126158261;\n    pB17 = raw6;\n    aB18 = 1;\n    xB18 = 0;\n    yB18 = 0.525731112;\n    zB18 = 0.850650808;\n    hB18 = -0.819305442;\n    pB18 = raw4;\n    aB19 = 1;\n    xB19 = 0.525731112;\n    yB19 = 0.850650808;\n    zB19 = 0;\n    hB19 = -0.732294065;\n    pB19 = raw3;\n    aB20 = 1;\n    xB20 = 0.850650808;\n    yB20 = 0;\n    zB20 = 0.525731112;\n    hB20 = -0.636983885;\n    pB20 = raw2;\n}\n\n// Global geometric and harmonic controls.\ns = clamp(size, 0, 1);\nsize_scale = pow(2, (s * 4) - 2);\nbase_ms = 47;\ngeometry_depth_target = clamp(geometry_depth, 0, 1);\ngeometry_depth_seconds = max(geometry_depth_slew_ms, 0) * 0.001;\ngeometry_depth_coeff = (geometry_depth_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * geometry_depth_seconds)));\ngeometry_depth_z = geometry_depth_z + geometry_depth_coeff * (geometry_depth_target - geometry_depth_z);\ngdepth = geometry_depth_z * 0.90;\nharm = clamp(harmonicity, 0, 1);\nhspan = clamp(harmonic_span, 0, 1);\npdepth = clamp(pauli_depth, 0, 1) * 0.38;\n\n// Smooth rotations along the shortest circular path to avoid discontinuous\n// delay-time and spatial changes. Rotation values are measured in turns.\nrotation_seconds = max(rotation_slew_ms, 0) * 0.001;\nrotation_coeff = (rotation_seconds <= 0.000001) ? 1 : (1 - exp(-1 / (sr * rotation_seconds)));\nrot_x_delta = rot_x - rot_x_z;\nrot_y_delta = rot_y - rot_y_z;\nrot_z_delta = rot_z - rot_z_z;\nrot_x_delta = rot_x_delta - floor(rot_x_delta + 0.5);\nrot_y_delta = rot_y_delta - floor(rot_y_delta + 0.5);\nrot_z_delta = rot_z_delta - floor(rot_z_delta + 0.5);\nrot_x_z = rot_x_z + rotation_coeff * rot_x_delta;\nrot_y_z = rot_y_z + rotation_coeff * rot_y_delta;\nrot_z_z = rot_z_z + rotation_coeff * rot_z_delta;\n\nrxang = rot_x_z * pi2;\nryang = rot_y_z * pi2;\nrzang = rot_z_z * pi2;\ncx = cos(rxang); sx = sin(rxang);\ncy = cos(ryang); sy = sin(ryang);\ncz = cos(rzang); sz = sin(rzang);\n\nact1 = mix(aA1, aB1, morph);\namp1 = sqrt(max(act1, 0));\nxg1 = mix(xA1, xB1, morph);\nyg1 = mix(yA1, yB1, morph);\nzg1 = mix(zA1, zB1, morph);\nhl1 = mix(hA1, hB1, morph);\npv1 = mix(pA1, pB1, morph);\n\nxr1_1 = xg1;\nyr1_1 = yg1 * cx - zg1 * sx;\nzr1_1 = yg1 * sx + zg1 * cx;\nxr2_1 = xr1_1 * cy + zr1_1 * sy;\nyr2_1 = yr1_1;\nzr2_1 = -xr1_1 * sy + zr1_1 * cy;\nxr1 = xr2_1 * cz - yr2_1 * sz;\nyr1 = xr2_1 * sz + yr2_1 * cz;\nzr1 = zr2_1;\nproj1 = xr1 * 0.425325404 + yr1 * 0.601501006 + zr1 * 0.688190961;\nlogratio1 = (1 - harm) * (gdepth * proj1) + harm * (hspan * hl1) + pdepth * pv1;\ndms1 = base_ms * size_scale * exp(logratio1);\nd1 = clamp(dms1 * sr * 0.001, 16, 383999);\nact2 = mix(aA2, aB2, morph);\namp2 = sqrt(max(act2, 0));\nxg2 = mix(xA2, xB2, morph);\nyg2 = mix(yA2, yB2, morph);\nzg2 = mix(zA2, zB2, morph);\nhl2 = mix(hA2, hB2, morph);\npv2 = mix(pA2, pB2, morph);\n\nxr1_2 = xg2;\nyr1_2 = yg2 * cx - zg2 * sx;\nzr1_2 = yg2 * sx + zg2 * cx;\nxr2_2 = xr1_2 * cy + zr1_2 * sy;\nyr2_2 = yr1_2;\nzr2_2 = -xr1_2 * sy + zr1_2 * cy;\nxr2 = xr2_2 * cz - yr2_2 * sz;\nyr2 = xr2_2 * sz + yr2_2 * cz;\nzr2 = zr2_2;\nproj2 = xr2 * 0.425325404 + yr2 * 0.601501006 + zr2 * 0.688190961;\nlogratio2 = (1 - harm) * (gdepth * proj2) + harm * (hspan * hl2) + pdepth * pv2;\ndms2 = base_ms * size_scale * exp(logratio2);\nd2 = clamp(dms2 * sr * 0.001, 16, 383999);\nact3 = mix(aA3, aB3, morph);\namp3 = sqrt(max(act3, 0));\nxg3 = mix(xA3, xB3, morph);\nyg3 = mix(yA3, yB3, morph);\nzg3 = mix(zA3, zB3, morph);\nhl3 = mix(hA3, hB3, morph);\npv3 = mix(pA3, pB3, morph);\n\nxr1_3 = xg3;\nyr1_3 = yg3 * cx - zg3 * sx;\nzr1_3 = yg3 * sx + zg3 * cx;\nxr2_3 = xr1_3 * cy + zr1_3 * sy;\nyr2_3 = yr1_3;\nzr2_3 = -xr1_3 * sy + zr1_3 * cy;\nxr3 = xr2_3 * cz - yr2_3 * sz;\nyr3 = xr2_3 * sz + yr2_3 * cz;\nzr3 = zr2_3;\nproj3 = xr3 * 0.425325404 + yr3 * 0.601501006 + zr3 * 0.688190961;\nlogratio3 = (1 - harm) * (gdepth * proj3) + harm * (hspan * hl3) + pdepth * pv3;\ndms3 = base_ms * size_scale * exp(logratio3);\nd3 = clamp(dms3 * sr * 0.001, 16, 383999);\nact4 = mix(aA4, aB4, morph);\namp4 = sqrt(max(act4, 0));\nxg4 = mix(xA4, xB4, morph);\nyg4 = mix(yA4, yB4, morph);\nzg4 = mix(zA4, zB4, morph);\nhl4 = mix(hA4, hB4, morph);\npv4 = mix(pA4, pB4, morph);\n\nxr1_4 = xg4;\nyr1_4 = yg4 * cx - zg4 * sx;\nzr1_4 = yg4 * sx + zg4 * cx;\nxr2_4 = xr1_4 * cy + zr1_4 * sy;\nyr2_4 = yr1_4;\nzr2_4 = -xr1_4 * sy + zr1_4 * cy;\nxr4 = xr2_4 * cz - yr2_4 * sz;\nyr4 = xr2_4 * sz + yr2_4 * cz;\nzr4 = zr2_4;\nproj4 = xr4 * 0.425325404 + yr4 * 0.601501006 + zr4 * 0.688190961;\nlogratio4 = (1 - harm) * (gdepth * proj4) + harm * (hspan * hl4) + pdepth * pv4;\ndms4 = base_ms * size_scale * exp(logratio4);\nd4 = clamp(dms4 * sr * 0.001, 16, 383999);\nact5 = mix(aA5, aB5, morph);\namp5 = sqrt(max(act5, 0));\nxg5 = mix(xA5, xB5, morph);\nyg5 = mix(yA5, yB5, morph);\nzg5 = mix(zA5, zB5, morph);\nhl5 = mix(hA5, hB5, morph);\npv5 = mix(pA5, pB5, morph);\n\nxr1_5 = xg5;\nyr1_5 = yg5 * cx - zg5 * sx;\nzr1_5 = yg5 * sx + zg5 * cx;\nxr2_5 = xr1_5 * cy + zr1_5 * sy;\nyr2_5 = yr1_5;\nzr2_5 = -xr1_5 * sy + zr1_5 * cy;\nxr5 = xr2_5 * cz - yr2_5 * sz;\nyr5 = xr2_5 * sz + yr2_5 * cz;\nzr5 = zr2_5;\nproj5 = xr5 * 0.425325404 + yr5 * 0.601501006 + zr5 * 0.688190961;\nlogratio5 = (1 - harm) * (gdepth * proj5) + harm * (hspan * hl5) + pdepth * pv5;\ndms5 = base_ms * size_scale * exp(logratio5);\nd5 = clamp(dms5 * sr * 0.001, 16, 383999);\nact6 = mix(aA6, aB6, morph);\namp6 = sqrt(max(act6, 0));\nxg6 = mix(xA6, xB6, morph);\nyg6 = mix(yA6, yB6, morph);\nzg6 = mix(zA6, zB6, morph);\nhl6 = mix(hA6, hB6, morph);\npv6 = mix(pA6, pB6, morph);\n\nxr1_6 = xg6;\nyr1_6 = yg6 * cx - zg6 * sx;\nzr1_6 = yg6 * sx + zg6 * cx;\nxr2_6 = xr1_6 * cy + zr1_6 * sy;\nyr2_6 = yr1_6;\nzr2_6 = -xr1_6 * sy + zr1_6 * cy;\nxr6 = xr2_6 * cz - yr2_6 * sz;\nyr6 = xr2_6 * sz + yr2_6 * cz;\nzr6 = zr2_6;\nproj6 = xr6 * 0.425325404 + yr6 * 0.601501006 + zr6 * 0.688190961;\nlogratio6 = (1 - harm) * (gdepth * proj6) + harm * (hspan * hl6) + pdepth * pv6;\ndms6 = base_ms * size_scale * exp(logratio6);\nd6 = clamp(dms6 * sr * 0.001, 16, 383999);\nact7 = mix(aA7, aB7, morph);\namp7 = sqrt(max(act7, 0));\nxg7 = mix(xA7, xB7, morph);\nyg7 = mix(yA7, yB7, morph);\nzg7 = mix(zA7, zB7, morph);\nhl7 = mix(hA7, hB7, morph);\npv7 = mix(pA7, pB7, morph);\n\nxr1_7 = xg7;\nyr1_7 = yg7 * cx - zg7 * sx;\nzr1_7 = yg7 * sx + zg7 * cx;\nxr2_7 = xr1_7 * cy + zr1_7 * sy;\nyr2_7 = yr1_7;\nzr2_7 = -xr1_7 * sy + zr1_7 * cy;\nxr7 = xr2_7 * cz - yr2_7 * sz;\nyr7 = xr2_7 * sz + yr2_7 * cz;\nzr7 = zr2_7;\nproj7 = xr7 * 0.425325404 + yr7 * 0.601501006 + zr7 * 0.688190961;\nlogratio7 = (1 - harm) * (gdepth * proj7) + harm * (hspan * hl7) + pdepth * pv7;\ndms7 = base_ms * size_scale * exp(logratio7);\nd7 = clamp(dms7 * sr * 0.001, 16, 383999);\nact8 = mix(aA8, aB8, morph);\namp8 = sqrt(max(act8, 0));\nxg8 = mix(xA8, xB8, morph);\nyg8 = mix(yA8, yB8, morph);\nzg8 = mix(zA8, zB8, morph);\nhl8 = mix(hA8, hB8, morph);\npv8 = mix(pA8, pB8, morph);\n\nxr1_8 = xg8;\nyr1_8 = yg8 * cx - zg8 * sx;\nzr1_8 = yg8 * sx + zg8 * cx;\nxr2_8 = xr1_8 * cy + zr1_8 * sy;\nyr2_8 = yr1_8;\nzr2_8 = -xr1_8 * sy + zr1_8 * cy;\nxr8 = xr2_8 * cz - yr2_8 * sz;\nyr8 = xr2_8 * sz + yr2_8 * cz;\nzr8 = zr2_8;\nproj8 = xr8 * 0.425325404 + yr8 * 0.601501006 + zr8 * 0.688190961;\nlogratio8 = (1 - harm) * (gdepth * proj8) + harm * (hspan * hl8) + pdepth * pv8;\ndms8 = base_ms * size_scale * exp(logratio8);\nd8 = clamp(dms8 * sr * 0.001, 16, 383999);\nact9 = mix(aA9, aB9, morph);\namp9 = sqrt(max(act9, 0));\nxg9 = mix(xA9, xB9, morph);\nyg9 = mix(yA9, yB9, morph);\nzg9 = mix(zA9, zB9, morph);\nhl9 = mix(hA9, hB9, morph);\npv9 = mix(pA9, pB9, morph);\n\nxr1_9 = xg9;\nyr1_9 = yg9 * cx - zg9 * sx;\nzr1_9 = yg9 * sx + zg9 * cx;\nxr2_9 = xr1_9 * cy + zr1_9 * sy;\nyr2_9 = yr1_9;\nzr2_9 = -xr1_9 * sy + zr1_9 * cy;\nxr9 = xr2_9 * cz - yr2_9 * sz;\nyr9 = xr2_9 * sz + yr2_9 * cz;\nzr9 = zr2_9;\nproj9 = xr9 * 0.425325404 + yr9 * 0.601501006 + zr9 * 0.688190961;\nlogratio9 = (1 - harm) * (gdepth * proj9) + harm * (hspan * hl9) + pdepth * pv9;\ndms9 = base_ms * size_scale * exp(logratio9);\nd9 = clamp(dms9 * sr * 0.001, 16, 383999);\nact10 = mix(aA10, aB10, morph);\namp10 = sqrt(max(act10, 0));\nxg10 = mix(xA10, xB10, morph);\nyg10 = mix(yA10, yB10, morph);\nzg10 = mix(zA10, zB10, morph);\nhl10 = mix(hA10, hB10, morph);\npv10 = mix(pA10, pB10, morph);\n\nxr1_10 = xg10;\nyr1_10 = yg10 * cx - zg10 * sx;\nzr1_10 = yg10 * sx + zg10 * cx;\nxr2_10 = xr1_10 * cy + zr1_10 * sy;\nyr2_10 = yr1_10;\nzr2_10 = -xr1_10 * sy + zr1_10 * cy;\nxr10 = xr2_10 * cz - yr2_10 * sz;\nyr10 = xr2_10 * sz + yr2_10 * cz;\nzr10 = zr2_10;\nproj10 = xr10 * 0.425325404 + yr10 * 0.601501006 + zr10 * 0.688190961;\nlogratio10 = (1 - harm) * (gdepth * proj10) + harm * (hspan * hl10) + pdepth * pv10;\ndms10 = base_ms * size_scale * exp(logratio10);\nd10 = clamp(dms10 * sr * 0.001, 16, 383999);\nact11 = mix(aA11, aB11, morph);\namp11 = sqrt(max(act11, 0));\nxg11 = mix(xA11, xB11, morph);\nyg11 = mix(yA11, yB11, morph);\nzg11 = mix(zA11, zB11, morph);\nhl11 = mix(hA11, hB11, morph);\npv11 = mix(pA11, pB11, morph);\n\nxr1_11 = xg11;\nyr1_11 = yg11 * cx - zg11 * sx;\nzr1_11 = yg11 * sx + zg11 * cx;\nxr2_11 = xr1_11 * cy + zr1_11 * sy;\nyr2_11 = yr1_11;\nzr2_11 = -xr1_11 * sy + zr1_11 * cy;\nxr11 = xr2_11 * cz - yr2_11 * sz;\nyr11 = xr2_11 * sz + yr2_11 * cz;\nzr11 = zr2_11;\nproj11 = xr11 * 0.425325404 + yr11 * 0.601501006 + zr11 * 0.688190961;\nlogratio11 = (1 - harm) * (gdepth * proj11) + harm * (hspan * hl11) + pdepth * pv11;\ndms11 = base_ms * size_scale * exp(logratio11);\nd11 = clamp(dms11 * sr * 0.001, 16, 383999);\nact12 = mix(aA12, aB12, morph);\namp12 = sqrt(max(act12, 0));\nxg12 = mix(xA12, xB12, morph);\nyg12 = mix(yA12, yB12, morph);\nzg12 = mix(zA12, zB12, morph);\nhl12 = mix(hA12, hB12, morph);\npv12 = mix(pA12, pB12, morph);\n\nxr1_12 = xg12;\nyr1_12 = yg12 * cx - zg12 * sx;\nzr1_12 = yg12 * sx + zg12 * cx;\nxr2_12 = xr1_12 * cy + zr1_12 * sy;\nyr2_12 = yr1_12;\nzr2_12 = -xr1_12 * sy + zr1_12 * cy;\nxr12 = xr2_12 * cz - yr2_12 * sz;\nyr12 = xr2_12 * sz + yr2_12 * cz;\nzr12 = zr2_12;\nproj12 = xr12 * 0.425325404 + yr12 * 0.601501006 + zr12 * 0.688190961;\nlogratio12 = (1 - harm) * (gdepth * proj12) + harm * (hspan * hl12) + pdepth * pv12;\ndms12 = base_ms * size_scale * exp(logratio12);\nd12 = clamp(dms12 * sr * 0.001, 16, 383999);\nact13 = mix(aA13, aB13, morph);\namp13 = sqrt(max(act13, 0));\nxg13 = mix(xA13, xB13, morph);\nyg13 = mix(yA13, yB13, morph);\nzg13 = mix(zA13, zB13, morph);\nhl13 = mix(hA13, hB13, morph);\npv13 = mix(pA13, pB13, morph);\n\nxr1_13 = xg13;\nyr1_13 = yg13 * cx - zg13 * sx;\nzr1_13 = yg13 * sx + zg13 * cx;\nxr2_13 = xr1_13 * cy + zr1_13 * sy;\nyr2_13 = yr1_13;\nzr2_13 = -xr1_13 * sy + zr1_13 * cy;\nxr13 = xr2_13 * cz - yr2_13 * sz;\nyr13 = xr2_13 * sz + yr2_13 * cz;\nzr13 = zr2_13;\nproj13 = xr13 * 0.425325404 + yr13 * 0.601501006 + zr13 * 0.688190961;\nlogratio13 = (1 - harm) * (gdepth * proj13) + harm * (hspan * hl13) + pdepth * pv13;\ndms13 = base_ms * size_scale * exp(logratio13);\nd13 = clamp(dms13 * sr * 0.001, 16, 383999);\nact14 = mix(aA14, aB14, morph);\namp14 = sqrt(max(act14, 0));\nxg14 = mix(xA14, xB14, morph);\nyg14 = mix(yA14, yB14, morph);\nzg14 = mix(zA14, zB14, morph);\nhl14 = mix(hA14, hB14, morph);\npv14 = mix(pA14, pB14, morph);\n\nxr1_14 = xg14;\nyr1_14 = yg14 * cx - zg14 * sx;\nzr1_14 = yg14 * sx + zg14 * cx;\nxr2_14 = xr1_14 * cy + zr1_14 * sy;\nyr2_14 = yr1_14;\nzr2_14 = -xr1_14 * sy + zr1_14 * cy;\nxr14 = xr2_14 * cz - yr2_14 * sz;\nyr14 = xr2_14 * sz + yr2_14 * cz;\nzr14 = zr2_14;\nproj14 = xr14 * 0.425325404 + yr14 * 0.601501006 + zr14 * 0.688190961;\nlogratio14 = (1 - harm) * (gdepth * proj14) + harm * (hspan * hl14) + pdepth * pv14;\ndms14 = base_ms * size_scale * exp(logratio14);\nd14 = clamp(dms14 * sr * 0.001, 16, 383999);\nact15 = mix(aA15, aB15, morph);\namp15 = sqrt(max(act15, 0));\nxg15 = mix(xA15, xB15, morph);\nyg15 = mix(yA15, yB15, morph);\nzg15 = mix(zA15, zB15, morph);\nhl15 = mix(hA15, hB15, morph);\npv15 = mix(pA15, pB15, morph);\n\nxr1_15 = xg15;\nyr1_15 = yg15 * cx - zg15 * sx;\nzr1_15 = yg15 * sx + zg15 * cx;\nxr2_15 = xr1_15 * cy + zr1_15 * sy;\nyr2_15 = yr1_15;\nzr2_15 = -xr1_15 * sy + zr1_15 * cy;\nxr15 = xr2_15 * cz - yr2_15 * sz;\nyr15 = xr2_15 * sz + yr2_15 * cz;\nzr15 = zr2_15;\nproj15 = xr15 * 0.425325404 + yr15 * 0.601501006 + zr15 * 0.688190961;\nlogratio15 = (1 - harm) * (gdepth * proj15) + harm * (hspan * hl15) + pdepth * pv15;\ndms15 = base_ms * size_scale * exp(logratio15);\nd15 = clamp(dms15 * sr * 0.001, 16, 383999);\nact16 = mix(aA16, aB16, morph);\namp16 = sqrt(max(act16, 0));\nxg16 = mix(xA16, xB16, morph);\nyg16 = mix(yA16, yB16, morph);\nzg16 = mix(zA16, zB16, morph);\nhl16 = mix(hA16, hB16, morph);\npv16 = mix(pA16, pB16, morph);\n\nxr1_16 = xg16;\nyr1_16 = yg16 * cx - zg16 * sx;\nzr1_16 = yg16 * sx + zg16 * cx;\nxr2_16 = xr1_16 * cy + zr1_16 * sy;\nyr2_16 = yr1_16;\nzr2_16 = -xr1_16 * sy + zr1_16 * cy;\nxr16 = xr2_16 * cz - yr2_16 * sz;\nyr16 = xr2_16 * sz + yr2_16 * cz;\nzr16 = zr2_16;\nproj16 = xr16 * 0.425325404 + yr16 * 0.601501006 + zr16 * 0.688190961;\nlogratio16 = (1 - harm) * (gdepth * proj16) + harm * (hspan * hl16) + pdepth * pv16;\ndms16 = base_ms * size_scale * exp(logratio16);\nd16 = clamp(dms16 * sr * 0.001, 16, 383999);\nact17 = mix(aA17, aB17, morph);\namp17 = sqrt(max(act17, 0));\nxg17 = mix(xA17, xB17, morph);\nyg17 = mix(yA17, yB17, morph);\nzg17 = mix(zA17, zB17, morph);\nhl17 = mix(hA17, hB17, morph);\npv17 = mix(pA17, pB17, morph);\n\nxr1_17 = xg17;\nyr1_17 = yg17 * cx - zg17 * sx;\nzr1_17 = yg17 * sx + zg17 * cx;\nxr2_17 = xr1_17 * cy + zr1_17 * sy;\nyr2_17 = yr1_17;\nzr2_17 = -xr1_17 * sy + zr1_17 * cy;\nxr17 = xr2_17 * cz - yr2_17 * sz;\nyr17 = xr2_17 * sz + yr2_17 * cz;\nzr17 = zr2_17;\nproj17 = xr17 * 0.425325404 + yr17 * 0.601501006 + zr17 * 0.688190961;\nlogratio17 = (1 - harm) * (gdepth * proj17) + harm * (hspan * hl17) + pdepth * pv17;\ndms17 = base_ms * size_scale * exp(logratio17);\nd17 = clamp(dms17 * sr * 0.001, 16, 383999);\nact18 = mix(aA18, aB18, morph);\namp18 = sqrt(max(act18, 0));\nxg18 = mix(xA18, xB18, morph);\nyg18 = mix(yA18, yB18, morph);\nzg18 = mix(zA18, zB18, morph);\nhl18 = mix(hA18, hB18, morph);\npv18 = mix(pA18, pB18, morph);\n\nxr1_18 = xg18;\nyr1_18 = yg18 * cx - zg18 * sx;\nzr1_18 = yg18 * sx + zg18 * cx;\nxr2_18 = xr1_18 * cy + zr1_18 * sy;\nyr2_18 = yr1_18;\nzr2_18 = -xr1_18 * sy + zr1_18 * cy;\nxr18 = xr2_18 * cz - yr2_18 * sz;\nyr18 = xr2_18 * sz + yr2_18 * cz;\nzr18 = zr2_18;\nproj18 = xr18 * 0.425325404 + yr18 * 0.601501006 + zr18 * 0.688190961;\nlogratio18 = (1 - harm) * (gdepth * proj18) + harm * (hspan * hl18) + pdepth * pv18;\ndms18 = base_ms * size_scale * exp(logratio18);\nd18 = clamp(dms18 * sr * 0.001, 16, 383999);\nact19 = mix(aA19, aB19, morph);\namp19 = sqrt(max(act19, 0));\nxg19 = mix(xA19, xB19, morph);\nyg19 = mix(yA19, yB19, morph);\nzg19 = mix(zA19, zB19, morph);\nhl19 = mix(hA19, hB19, morph);\npv19 = mix(pA19, pB19, morph);\n\nxr1_19 = xg19;\nyr1_19 = yg19 * cx - zg19 * sx;\nzr1_19 = yg19 * sx + zg19 * cx;\nxr2_19 = xr1_19 * cy + zr1_19 * sy;\nyr2_19 = yr1_19;\nzr2_19 = -xr1_19 * sy + zr1_19 * cy;\nxr19 = xr2_19 * cz - yr2_19 * sz;\nyr19 = xr2_19 * sz + yr2_19 * cz;\nzr19 = zr2_19;\nproj19 = xr19 * 0.425325404 + yr19 * 0.601501006 + zr19 * 0.688190961;\nlogratio19 = (1 - harm) * (gdepth * proj19) + harm * (hspan * hl19) + pdepth * pv19;\ndms19 = base_ms * size_scale * exp(logratio19);\nd19 = clamp(dms19 * sr * 0.001, 16, 383999);\nact20 = mix(aA20, aB20, morph);\namp20 = sqrt(max(act20, 0));\nxg20 = mix(xA20, xB20, morph);\nyg20 = mix(yA20, yB20, morph);\nzg20 = mix(zA20, zB20, morph);\nhl20 = mix(hA20, hB20, morph);\npv20 = mix(pA20, pB20, morph);\n\nxr1_20 = xg20;\nyr1_20 = yg20 * cx - zg20 * sx;\nzr1_20 = yg20 * sx + zg20 * cx;\nxr2_20 = xr1_20 * cy + zr1_20 * sy;\nyr2_20 = yr1_20;\nzr2_20 = -xr1_20 * sy + zr1_20 * cy;\nxr20 = xr2_20 * cz - yr2_20 * sz;\nyr20 = xr2_20 * sz + yr2_20 * cz;\nzr20 = zr2_20;\nproj20 = xr20 * 0.425325404 + yr20 * 0.601501006 + zr20 * 0.688190961;\nlogratio20 = (1 - harm) * (gdepth * proj20) + harm * (hspan * hl20) + pdepth * pv20;\ndms20 = base_ms * size_scale * exp(logratio20);\nd20 = clamp(dms20 * sr * 0.001, 16, 383999);\n\nactive_sum = max(act1 + act2 + act3 + act4 + act5 + act6 + act7 + act8 + act9 + act10 + act11 + act12 + act13 + act14 + act15 + act16 + act17 + act18 + act19 + act20, 0.000001);\ninput_norm = 1 / sqrt(active_sum);\n\nr1 = dl1.read(d1);\nr2 = dl2.read(d2);\nr3 = dl3.read(d3);\nr4 = dl4.read(d4);\nr5 = dl5.read(d5);\nr6 = dl6.read(d6);\nr7 = dl7.read(d7);\nr8 = dl8.read(d8);\nr9 = dl9.read(d9);\nr10 = dl10.read(d10);\nr11 = dl11.read(d11);\nr12 = dl12.read(d12);\nr13 = dl13.read(d13);\nr14 = dl14.read(d14);\nr15 = dl15.read(d15);\nr16 = dl16.read(d16);\nr17 = dl17.read(d17);\nr18 = dl18.read(d18);\nr19 = dl19.read(d19);\nr20 = dl20.read(d20);\n\n// Frequency-dependent absorption in every feedback branch.\nab = clamp(absorb, 0, 1);\ntl = clamp(tilt, -1, 1);\ncut_norm = clamp(0.015 + (1 - ab) * 0.45 + tl * 0.12, 0.005, 0.48);\n\nlp1 = lp1 + cut_norm * (r1 - lp1);\nf1 = mix(r1, lp1, ab) * amp1;\nlp2 = lp2 + cut_norm * (r2 - lp2);\nf2 = mix(r2, lp2, ab) * amp2;\nlp3 = lp3 + cut_norm * (r3 - lp3);\nf3 = mix(r3, lp3, ab) * amp3;\nlp4 = lp4 + cut_norm * (r4 - lp4);\nf4 = mix(r4, lp4, ab) * amp4;\nlp5 = lp5 + cut_norm * (r5 - lp5);\nf5 = mix(r5, lp5, ab) * amp5;\nlp6 = lp6 + cut_norm * (r6 - lp6);\nf6 = mix(r6, lp6, ab) * amp6;\nlp7 = lp7 + cut_norm * (r7 - lp7);\nf7 = mix(r7, lp7, ab) * amp7;\nlp8 = lp8 + cut_norm * (r8 - lp8);\nf8 = mix(r8, lp8, ab) * amp8;\nlp9 = lp9 + cut_norm * (r9 - lp9);\nf9 = mix(r9, lp9, ab) * amp9;\nlp10 = lp10 + cut_norm * (r10 - lp10);\nf10 = mix(r10, lp10, ab) * amp10;\nlp11 = lp11 + cut_norm * (r11 - lp11);\nf11 = mix(r11, lp11, ab) * amp11;\nlp12 = lp12 + cut_norm * (r12 - lp12);\nf12 = mix(r12, lp12, ab) * amp12;\nlp13 = lp13 + cut_norm * (r13 - lp13);\nf13 = mix(r13, lp13, ab) * amp13;\nlp14 = lp14 + cut_norm * (r14 - lp14);\nf14 = mix(r14, lp14, ab) * amp14;\nlp15 = lp15 + cut_norm * (r15 - lp15);\nf15 = mix(r15, lp15, ab) * amp15;\nlp16 = lp16 + cut_norm * (r16 - lp16);\nf16 = mix(r16, lp16, ab) * amp16;\nlp17 = lp17 + cut_norm * (r17 - lp17);\nf17 = mix(r17, lp17, ab) * amp17;\nlp18 = lp18 + cut_norm * (r18 - lp18);\nf18 = mix(r18, lp18, ab) * amp18;\nlp19 = lp19 + cut_norm * (r19 - lp19);\nf19 = mix(r19, lp19, ab) * amp19;\nlp20 = lp20 + cut_norm * (r20 - lp20);\nf20 = mix(r20, lp20, ab) * amp20;\n\n// Five normalized Platonic adjacency operators.\n// tetrahedron: 4 vertices, degree 3\nadj0_1 = 0;\nadj0_2 = (0.333333333 * f3) + (0.333333333 * f5) + (0.333333333 * f8);\nadj0_3 = (0.333333333 * f2) + (0.333333333 * f5) + (0.333333333 * f8);\nadj0_4 = 0;\nadj0_5 = (0.333333333 * f2) + (0.333333333 * f3) + (0.333333333 * f8);\nadj0_6 = 0;\nadj0_7 = 0;\nadj0_8 = (0.333333333 * f2) + (0.333333333 * f3) + (0.333333333 * f5);\nadj0_9 = 0;\nadj0_10 = 0;\nadj0_11 = 0;\nadj0_12 = 0;\nadj0_13 = 0;\nadj0_14 = 0;\nadj0_15 = 0;\nadj0_16 = 0;\nadj0_17 = 0;\nadj0_18 = 0;\nadj0_19 = 0;\nadj0_20 = 0;\n// cube: 8 vertices, degree 3\nadj1_1 = (0.333333333 * f2) + (0.333333333 * f3) + (0.333333333 * f5);\nadj1_2 = (0.333333333 * f1) + (0.333333333 * f4) + (0.333333333 * f6);\nadj1_3 = (0.333333333 * f1) + (0.333333333 * f4) + (0.333333333 * f7);\nadj1_4 = (0.333333333 * f2) + (0.333333333 * f3) + (0.333333333 * f8);\nadj1_5 = (0.333333333 * f1) + (0.333333333 * f6) + (0.333333333 * f7);\nadj1_6 = (0.333333333 * f2) + (0.333333333 * f5) + (0.333333333 * f8);\nadj1_7 = (0.333333333 * f3) + (0.333333333 * f5) + (0.333333333 * f8);\nadj1_8 = (0.333333333 * f4) + (0.333333333 * f6) + (0.333333333 * f7);\nadj1_9 = 0;\nadj1_10 = 0;\nadj1_11 = 0;\nadj1_12 = 0;\nadj1_13 = 0;\nadj1_14 = 0;\nadj1_15 = 0;\nadj1_16 = 0;\nadj1_17 = 0;\nadj1_18 = 0;\nadj1_19 = 0;\nadj1_20 = 0;\n// octahedron: 6 vertices, degree 4\nadj2_1 = 0;\nadj2_2 = 0;\nadj2_3 = 0;\nadj2_4 = 0;\nadj2_5 = 0;\nadj2_6 = 0;\nadj2_7 = 0;\nadj2_8 = 0;\nadj2_9 = (0.25 * f10) + (0.25 * f11) + (0.25 * f13) + (0.25 * f14);\nadj2_10 = (0.25 * f9) + (0.25 * f11) + (0.25 * f12) + (0.25 * f14);\nadj2_11 = (0.25 * f9) + (0.25 * f10) + (0.25 * f12) + (0.25 * f13);\nadj2_12 = (0.25 * f10) + (0.25 * f11) + (0.25 * f13) + (0.25 * f14);\nadj2_13 = (0.25 * f9) + (0.25 * f11) + (0.25 * f12) + (0.25 * f14);\nadj2_14 = (0.25 * f9) + (0.25 * f10) + (0.25 * f12) + (0.25 * f13);\nadj2_15 = 0;\nadj2_16 = 0;\nadj2_17 = 0;\nadj2_18 = 0;\nadj2_19 = 0;\nadj2_20 = 0;\n// dodecahedron: 20 vertices, degree 3\nadj3_1 = (0.333333333 * f9) + (0.333333333 * f10) + (0.333333333 * f11);\nadj3_2 = (0.333333333 * f10) + (0.333333333 * f12) + (0.333333333 * f17);\nadj3_3 = (0.333333333 * f11) + (0.333333333 * f13) + (0.333333333 * f15);\nadj3_4 = (0.333333333 * f13) + (0.333333333 * f17) + (0.333333333 * f18);\nadj3_5 = (0.333333333 * f9) + (0.333333333 * f14) + (0.333333333 * f16);\nadj3_6 = (0.333333333 * f12) + (0.333333333 * f16) + (0.333333333 * f20);\nadj3_7 = (0.333333333 * f14) + (0.333333333 * f15) + (0.333333333 * f19);\nadj3_8 = (0.333333333 * f18) + (0.333333333 * f19) + (0.333333333 * f20);\nadj3_9 = (0.333333333 * f1) + (0.333333333 * f5) + (0.333333333 * f15);\nadj3_10 = (0.333333333 * f1) + (0.333333333 * f2) + (0.333333333 * f16);\nadj3_11 = (0.333333333 * f1) + (0.333333333 * f3) + (0.333333333 * f17);\nadj3_12 = (0.333333333 * f2) + (0.333333333 * f6) + (0.333333333 * f18);\nadj3_13 = (0.333333333 * f3) + (0.333333333 * f4) + (0.333333333 * f19);\nadj3_14 = (0.333333333 * f5) + (0.333333333 * f7) + (0.333333333 * f20);\nadj3_15 = (0.333333333 * f3) + (0.333333333 * f7) + (0.333333333 * f9);\nadj3_16 = (0.333333333 * f5) + (0.333333333 * f6) + (0.333333333 * f10);\nadj3_17 = (0.333333333 * f2) + (0.333333333 * f4) + (0.333333333 * f11);\nadj3_18 = (0.333333333 * f4) + (0.333333333 * f8) + (0.333333333 * f12);\nadj3_19 = (0.333333333 * f7) + (0.333333333 * f8) + (0.333333333 * f13);\nadj3_20 = (0.333333333 * f6) + (0.333333333 * f8) + (0.333333333 * f14);\n// icosahedron: 12 vertices, degree 5\nadj4_1 = 0;\nadj4_2 = 0;\nadj4_3 = 0;\nadj4_4 = 0;\nadj4_5 = 0;\nadj4_6 = 0;\nadj4_7 = 0;\nadj4_8 = 0;\nadj4_9 = (0.2 * f10) + (0.2 * f11) + (0.2 * f14) + (0.2 * f15) + (0.2 * f16);\nadj4_10 = (0.2 * f9) + (0.2 * f11) + (0.2 * f12) + (0.2 * f16) + (0.2 * f17);\nadj4_11 = (0.2 * f9) + (0.2 * f10) + (0.2 * f13) + (0.2 * f15) + (0.2 * f17);\nadj4_12 = (0.2 * f10) + (0.2 * f16) + (0.2 * f17) + (0.2 * f18) + (0.2 * f20);\nadj4_13 = (0.2 * f11) + (0.2 * f15) + (0.2 * f17) + (0.2 * f18) + (0.2 * f19);\nadj4_14 = (0.2 * f9) + (0.2 * f15) + (0.2 * f16) + (0.2 * f19) + (0.2 * f20);\nadj4_15 = (0.2 * f9) + (0.2 * f11) + (0.2 * f13) + (0.2 * f14) + (0.2 * f19);\nadj4_16 = (0.2 * f9) + (0.2 * f10) + (0.2 * f12) + (0.2 * f14) + (0.2 * f20);\nadj4_17 = (0.2 * f10) + (0.2 * f11) + (0.2 * f12) + (0.2 * f13) + (0.2 * f18);\nadj4_18 = (0.2 * f12) + (0.2 * f13) + (0.2 * f17) + (0.2 * f19) + (0.2 * f20);\nadj4_19 = (0.2 * f13) + (0.2 * f14) + (0.2 * f15) + (0.2 * f18) + (0.2 * f20);\nadj4_20 = (0.2 * f12) + (0.2 * f14) + (0.2 * f16) + (0.2 * f18) + (0.2 * f19);\n\n// Select and interpolate the two graph topologies.\nadjA1 = adj0_1;\nadjA2 = adj0_2;\nadjA3 = adj0_3;\nadjA4 = adj0_4;\nadjA5 = adj0_5;\nadjA6 = adj0_6;\nadjA7 = adj0_7;\nadjA8 = adj0_8;\nadjA9 = adj0_9;\nadjA10 = adj0_10;\nadjA11 = adj0_11;\nadjA12 = adj0_12;\nadjA13 = adj0_13;\nadjA14 = adj0_14;\nadjA15 = adj0_15;\nadjA16 = adj0_16;\nadjA17 = adj0_17;\nadjA18 = adj0_18;\nadjA19 = adj0_19;\nadjA20 = adj0_20;\nif (sa == 0) {\n    adjA1 = adj0_1;\n    adjA2 = adj0_2;\n    adjA3 = adj0_3;\n    adjA4 = adj0_4;\n    adjA5 = adj0_5;\n    adjA6 = adj0_6;\n    adjA7 = adj0_7;\n    adjA8 = adj0_8;\n    adjA9 = adj0_9;\n    adjA10 = adj0_10;\n    adjA11 = adj0_11;\n    adjA12 = adj0_12;\n    adjA13 = adj0_13;\n    adjA14 = adj0_14;\n    adjA15 = adj0_15;\n    adjA16 = adj0_16;\n    adjA17 = adj0_17;\n    adjA18 = adj0_18;\n    adjA19 = adj0_19;\n    adjA20 = adj0_20;\n}\nelse if (sa == 1) {\n    adjA1 = adj1_1;\n    adjA2 = adj1_2;\n    adjA3 = adj1_3;\n    adjA4 = adj1_4;\n    adjA5 = adj1_5;\n    adjA6 = adj1_6;\n    adjA7 = adj1_7;\n    adjA8 = adj1_8;\n    adjA9 = adj1_9;\n    adjA10 = adj1_10;\n    adjA11 = adj1_11;\n    adjA12 = adj1_12;\n    adjA13 = adj1_13;\n    adjA14 = adj1_14;\n    adjA15 = adj1_15;\n    adjA16 = adj1_16;\n    adjA17 = adj1_17;\n    adjA18 = adj1_18;\n    adjA19 = adj1_19;\n    adjA20 = adj1_20;\n}\nelse if (sa == 2) {\n    adjA1 = adj2_1;\n    adjA2 = adj2_2;\n    adjA3 = adj2_3;\n    adjA4 = adj2_4;\n    adjA5 = adj2_5;\n    adjA6 = adj2_6;\n    adjA7 = adj2_7;\n    adjA8 = adj2_8;\n    adjA9 = adj2_9;\n    adjA10 = adj2_10;\n    adjA11 = adj2_11;\n    adjA12 = adj2_12;\n    adjA13 = adj2_13;\n    adjA14 = adj2_14;\n    adjA15 = adj2_15;\n    adjA16 = adj2_16;\n    adjA17 = adj2_17;\n    adjA18 = adj2_18;\n    adjA19 = adj2_19;\n    adjA20 = adj2_20;\n}\nelse if (sa == 3) {\n    adjA1 = adj3_1;\n    adjA2 = adj3_2;\n    adjA3 = adj3_3;\n    adjA4 = adj3_4;\n    adjA5 = adj3_5;\n    adjA6 = adj3_6;\n    adjA7 = adj3_7;\n    adjA8 = adj3_8;\n    adjA9 = adj3_9;\n    adjA10 = adj3_10;\n    adjA11 = adj3_11;\n    adjA12 = adj3_12;\n    adjA13 = adj3_13;\n    adjA14 = adj3_14;\n    adjA15 = adj3_15;\n    adjA16 = adj3_16;\n    adjA17 = adj3_17;\n    adjA18 = adj3_18;\n    adjA19 = adj3_19;\n    adjA20 = adj3_20;\n}\nelse if (sa == 4) {\n    adjA1 = adj4_1;\n    adjA2 = adj4_2;\n    adjA3 = adj4_3;\n    adjA4 = adj4_4;\n    adjA5 = adj4_5;\n    adjA6 = adj4_6;\n    adjA7 = adj4_7;\n    adjA8 = adj4_8;\n    adjA9 = adj4_9;\n    adjA10 = adj4_10;\n    adjA11 = adj4_11;\n    adjA12 = adj4_12;\n    adjA13 = adj4_13;\n    adjA14 = adj4_14;\n    adjA15 = adj4_15;\n    adjA16 = adj4_16;\n    adjA17 = adj4_17;\n    adjA18 = adj4_18;\n    adjA19 = adj4_19;\n    adjA20 = adj4_20;\n}\n\nadjB1 = adj0_1;\nadjB2 = adj0_2;\nadjB3 = adj0_3;\nadjB4 = adj0_4;\nadjB5 = adj0_5;\nadjB6 = adj0_6;\nadjB7 = adj0_7;\nadjB8 = adj0_8;\nadjB9 = adj0_9;\nadjB10 = adj0_10;\nadjB11 = adj0_11;\nadjB12 = adj0_12;\nadjB13 = adj0_13;\nadjB14 = adj0_14;\nadjB15 = adj0_15;\nadjB16 = adj0_16;\nadjB17 = adj0_17;\nadjB18 = adj0_18;\nadjB19 = adj0_19;\nadjB20 = adj0_20;\nif (sb == 0) {\n    adjB1 = adj0_1;\n    adjB2 = adj0_2;\n    adjB3 = adj0_3;\n    adjB4 = adj0_4;\n    adjB5 = adj0_5;\n    adjB6 = adj0_6;\n    adjB7 = adj0_7;\n    adjB8 = adj0_8;\n    adjB9 = adj0_9;\n    adjB10 = adj0_10;\n    adjB11 = adj0_11;\n    adjB12 = adj0_12;\n    adjB13 = adj0_13;\n    adjB14 = adj0_14;\n    adjB15 = adj0_15;\n    adjB16 = adj0_16;\n    adjB17 = adj0_17;\n    adjB18 = adj0_18;\n    adjB19 = adj0_19;\n    adjB20 = adj0_20;\n}\nelse if (sb == 1) {\n    adjB1 = adj1_1;\n    adjB2 = adj1_2;\n    adjB3 = adj1_3;\n    adjB4 = adj1_4;\n    adjB5 = adj1_5;\n    adjB6 = adj1_6;\n    adjB7 = adj1_7;\n    adjB8 = adj1_8;\n    adjB9 = adj1_9;\n    adjB10 = adj1_10;\n    adjB11 = adj1_11;\n    adjB12 = adj1_12;\n    adjB13 = adj1_13;\n    adjB14 = adj1_14;\n    adjB15 = adj1_15;\n    adjB16 = adj1_16;\n    adjB17 = adj1_17;\n    adjB18 = adj1_18;\n    adjB19 = adj1_19;\n    adjB20 = adj1_20;\n}\nelse if (sb == 2) {\n    adjB1 = adj2_1;\n    adjB2 = adj2_2;\n    adjB3 = adj2_3;\n    adjB4 = adj2_4;\n    adjB5 = adj2_5;\n    adjB6 = adj2_6;\n    adjB7 = adj2_7;\n    adjB8 = adj2_8;\n    adjB9 = adj2_9;\n    adjB10 = adj2_10;\n    adjB11 = adj2_11;\n    adjB12 = adj2_12;\n    adjB13 = adj2_13;\n    adjB14 = adj2_14;\n    adjB15 = adj2_15;\n    adjB16 = adj2_16;\n    adjB17 = adj2_17;\n    adjB18 = adj2_18;\n    adjB19 = adj2_19;\n    adjB20 = adj2_20;\n}\nelse if (sb == 3) {\n    adjB1 = adj3_1;\n    adjB2 = adj3_2;\n    adjB3 = adj3_3;\n    adjB4 = adj3_4;\n    adjB5 = adj3_5;\n    adjB6 = adj3_6;\n    adjB7 = adj3_7;\n    adjB8 = adj3_8;\n    adjB9 = adj3_9;\n    adjB10 = adj3_10;\n    adjB11 = adj3_11;\n    adjB12 = adj3_12;\n    adjB13 = adj3_13;\n    adjB14 = adj3_14;\n    adjB15 = adj3_15;\n    adjB16 = adj3_16;\n    adjB17 = adj3_17;\n    adjB18 = adj3_18;\n    adjB19 = adj3_19;\n    adjB20 = adj3_20;\n}\nelse if (sb == 4) {\n    adjB1 = adj4_1;\n    adjB2 = adj4_2;\n    adjB3 = adj4_3;\n    adjB4 = adj4_4;\n    adjB5 = adj4_5;\n    adjB6 = adj4_6;\n    adjB7 = adj4_7;\n    adjB8 = adj4_8;\n    adjB9 = adj4_9;\n    adjB10 = adj4_10;\n    adjB11 = adj4_11;\n    adjB12 = adj4_12;\n    adjB13 = adj4_13;\n    adjB14 = adj4_14;\n    adjB15 = adj4_15;\n    adjB16 = adj4_16;\n    adjB17 = adj4_17;\n    adjB18 = adj4_18;\n    adjB19 = adj4_19;\n    adjB20 = adj4_20;\n}\n\nadj1 = mix(adjA1, adjB1, morph);\nadj2 = mix(adjA2, adjB2, morph);\nadj3 = mix(adjA3, adjB3, morph);\nadj4 = mix(adjA4, adjB4, morph);\nadj5 = mix(adjA5, adjB5, morph);\nadj6 = mix(adjA6, adjB6, morph);\nadj7 = mix(adjA7, adjB7, morph);\nadj8 = mix(adjA8, adjB8, morph);\nadj9 = mix(adjA9, adjB9, morph);\nadj10 = mix(adjA10, adjB10, morph);\nadj11 = mix(adjA11, adjB11, morph);\nadj12 = mix(adjA12, adjB12, morph);\nadj13 = mix(adjA13, adjB13, morph);\nadj14 = mix(adjA14, adjB14, morph);\nadj15 = mix(adjA15, adjB15, morph);\nadj16 = mix(adjA16, adjB16, morph);\nadj17 = mix(adjA17, adjB17, morph);\nadj18 = mix(adjA18, adjB18, morph);\nadj19 = mix(adjA19, adjB19, morph);\nadj20 = mix(adjA20, adjB20, morph);\n\n// Active-node Householder diffusion remains energy preserving.\nhh_dot = (amp1 * f1) + (amp2 * f2) + (amp3 * f3) + (amp4 * f4) + (amp5 * f5) + (amp6 * f6) + (amp7 * f7) + (amp8 * f8) + (amp9 * f9) + (amp10 * f10) + (amp11 * f11) + (amp12 * f12) + (amp13 * f13) + (amp14 * f14) + (amp15 * f15) + (amp16 * f16) + (amp17 * f17) + (amp18 * f18) + (amp19 * f19) + (amp20 * f20);\nhh_den = active_sum;\nhh1 = f1 - 2 * amp1 * hh_dot / hh_den;\nhh2 = f2 - 2 * amp2 * hh_dot / hh_den;\nhh3 = f3 - 2 * amp3 * hh_dot / hh_den;\nhh4 = f4 - 2 * amp4 * hh_dot / hh_den;\nhh5 = f5 - 2 * amp5 * hh_dot / hh_den;\nhh6 = f6 - 2 * amp6 * hh_dot / hh_den;\nhh7 = f7 - 2 * amp7 * hh_dot / hh_den;\nhh8 = f8 - 2 * amp8 * hh_dot / hh_den;\nhh9 = f9 - 2 * amp9 * hh_dot / hh_den;\nhh10 = f10 - 2 * amp10 * hh_dot / hh_den;\nhh11 = f11 - 2 * amp11 * hh_dot / hh_den;\nhh12 = f12 - 2 * amp12 * hh_dot / hh_den;\nhh13 = f13 - 2 * amp13 * hh_dot / hh_den;\nhh14 = f14 - 2 * amp14 * hh_dot / hh_den;\nhh15 = f15 - 2 * amp15 * hh_dot / hh_den;\nhh16 = f16 - 2 * amp16 * hh_dot / hh_den;\nhh17 = f17 - 2 * amp17 * hh_dot / hh_den;\nhh18 = f18 - 2 * amp18 * hh_dot / hh_den;\nhh19 = f19 - 2 * amp19 * hh_dot / hh_den;\nhh20 = f20 - 2 * amp20 * hh_dot / hh_den;\n\ntopo = clamp(topology, 0, 1);\nnet1 = mix(hh1, adj1, topo);\nnet2 = mix(hh2, adj2, topo);\nnet3 = mix(hh3, adj3, topo);\nnet4 = mix(hh4, adj4, topo);\nnet5 = mix(hh5, adj5, topo);\nnet6 = mix(hh6, adj6, topo);\nnet7 = mix(hh7, adj7, topo);\nnet8 = mix(hh8, adj8, topo);\nnet9 = mix(hh9, adj9, topo);\nnet10 = mix(hh10, adj10, topo);\nnet11 = mix(hh11, adj11, topo);\nnet12 = mix(hh12, adj12, topo);\nnet13 = mix(hh13, adj13, topo);\nnet14 = mix(hh14, adj14, topo);\nnet15 = mix(hh15, adj15, topo);\nnet16 = mix(hh16, adj16, topo);\nnet17 = mix(hh17, adj17, topo);\nnet18 = mix(hh18, adj18, topo);\nnet19 = mix(hh19, adj19, topo);\nnet20 = mix(hh20, adj20, topo);\n\n// Delay-compensated T60 feedback.\ndec = clamp(decay, 0, 1);\nt60 = 0.18 * pow(194.444444, dec);\ng1 = pow(10, (-3 * d1) / (sr * t60));\ng2 = pow(10, (-3 * d2) / (sr * t60));\ng3 = pow(10, (-3 * d3) / (sr * t60));\ng4 = pow(10, (-3 * d4) / (sr * t60));\ng5 = pow(10, (-3 * d5) / (sr * t60));\ng6 = pow(10, (-3 * d6) / (sr * t60));\ng7 = pow(10, (-3 * d7) / (sr * t60));\ng8 = pow(10, (-3 * d8) / (sr * t60));\ng9 = pow(10, (-3 * d9) / (sr * t60));\ng10 = pow(10, (-3 * d10) / (sr * t60));\ng11 = pow(10, (-3 * d11) / (sr * t60));\ng12 = pow(10, (-3 * d12) / (sr * t60));\ng13 = pow(10, (-3 * d13) / (sr * t60));\ng14 = pow(10, (-3 * d14) / (sr * t60));\ng15 = pow(10, (-3 * d15) / (sr * t60));\ng16 = pow(10, (-3 * d16) / (sr * t60));\ng17 = pow(10, (-3 * d17) / (sr * t60));\ng18 = pow(10, (-3 * d18) / (sr * t60));\ng19 = pow(10, (-3 * d19) / (sr * t60));\ng20 = pow(10, (-3 * d20) / (sr * t60));\n\nfr = clamp(freeze, 0, 1);\ninj1 = diffused * 1 * amp1 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr1));\nfb1 = net1 * mix(g1, 0.9995, fr);\nw1 = (inj1 * (1 - fr) + fb1) * amp1;\ndl1.write(tanh(w1));\ninj2 = diffused * -1 * amp2 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr2));\nfb2 = net2 * mix(g2, 0.9995, fr);\nw2 = (inj2 * (1 - fr) + fb2) * amp2;\ndl2.write(tanh(w2));\ninj3 = diffused * -1 * amp3 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr3));\nfb3 = net3 * mix(g3, 0.9995, fr);\nw3 = (inj3 * (1 - fr) + fb3) * amp3;\ndl3.write(tanh(w3));\ninj4 = diffused * 1 * amp4 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr4));\nfb4 = net4 * mix(g4, 0.9995, fr);\nw4 = (inj4 * (1 - fr) + fb4) * amp4;\ndl4.write(tanh(w4));\ninj5 = diffused * -1 * amp5 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr5));\nfb5 = net5 * mix(g5, 0.9995, fr);\nw5 = (inj5 * (1 - fr) + fb5) * amp5;\ndl5.write(tanh(w5));\ninj6 = diffused * 1 * amp6 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr6));\nfb6 = net6 * mix(g6, 0.9995, fr);\nw6 = (inj6 * (1 - fr) + fb6) * amp6;\ndl6.write(tanh(w6));\ninj7 = diffused * 1 * amp7 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr7));\nfb7 = net7 * mix(g7, 0.9995, fr);\nw7 = (inj7 * (1 - fr) + fb7) * amp7;\ndl7.write(tanh(w7));\ninj8 = diffused * -1 * amp8 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr8));\nfb8 = net8 * mix(g8, 0.9995, fr);\nw8 = (inj8 * (1 - fr) + fb8) * amp8;\ndl8.write(tanh(w8));\ninj9 = diffused * -1 * amp9 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr9));\nfb9 = net9 * mix(g9, 0.9995, fr);\nw9 = (inj9 * (1 - fr) + fb9) * amp9;\ndl9.write(tanh(w9));\ninj10 = diffused * 1 * amp10 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr10));\nfb10 = net10 * mix(g10, 0.9995, fr);\nw10 = (inj10 * (1 - fr) + fb10) * amp10;\ndl10.write(tanh(w10));\ninj11 = diffused * 1 * amp11 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr11));\nfb11 = net11 * mix(g11, 0.9995, fr);\nw11 = (inj11 * (1 - fr) + fb11) * amp11;\ndl11.write(tanh(w11));\ninj12 = diffused * -1 * amp12 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr12));\nfb12 = net12 * mix(g12, 0.9995, fr);\nw12 = (inj12 * (1 - fr) + fb12) * amp12;\ndl12.write(tanh(w12));\ninj13 = diffused * 1 * amp13 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr13));\nfb13 = net13 * mix(g13, 0.9995, fr);\nw13 = (inj13 * (1 - fr) + fb13) * amp13;\ndl13.write(tanh(w13));\ninj14 = diffused * -1 * amp14 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr14));\nfb14 = net14 * mix(g14, 0.9995, fr);\nw14 = (inj14 * (1 - fr) + fb14) * amp14;\ndl14.write(tanh(w14));\ninj15 = diffused * -1 * amp15 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr15));\nfb15 = net15 * mix(g15, 0.9995, fr);\nw15 = (inj15 * (1 - fr) + fb15) * amp15;\ndl15.write(tanh(w15));\ninj16 = diffused * 1 * amp16 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr16));\nfb16 = net16 * mix(g16, 0.9995, fr);\nw16 = (inj16 * (1 - fr) + fb16) * amp16;\ndl16.write(tanh(w16));\ninj17 = diffused * -1 * amp17 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr17));\nfb17 = net17 * mix(g17, 0.9995, fr);\nw17 = (inj17 * (1 - fr) + fb17) * amp17;\ndl17.write(tanh(w17));\ninj18 = diffused * 1 * amp18 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr18));\nfb18 = net18 * mix(g18, 0.9995, fr);\nw18 = (inj18 * (1 - fr) + fb18) * amp18;\ndl18.write(tanh(w18));\ninj19 = diffused * 1 * amp19 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr19));\nfb19 = net19 * mix(g19, 0.9995, fr);\nw19 = (inj19 * (1 - fr) + fb19) * amp19;\ndl19.write(tanh(w19));\ninj20 = diffused * -1 * amp20 * input_norm * (0.65 + 0.35 * (0.5 + 0.5 * zr20));\nfb20 = net20 * mix(g20, 0.9995, fr);\nw20 = (inj20 * (1 - fr) + fb20) * amp20;\ndl20.write(tanh(w20));\n\n// Spatial decoder follows the continuously rotated/morphed coordinates.\nwd = clamp(width, 0, 1);\nout_norm = output_gain / sqrt(active_sum);\nleft =\n    (r1 * amp1 * sqrt(0.5 * (1 - clamp(xr1 * wd, -1, 1)))) +\n    (r2 * amp2 * sqrt(0.5 * (1 - clamp(xr2 * wd, -1, 1)))) +\n    (r3 * amp3 * sqrt(0.5 * (1 - clamp(xr3 * wd, -1, 1)))) +\n    (r4 * amp4 * sqrt(0.5 * (1 - clamp(xr4 * wd, -1, 1)))) +\n    (r5 * amp5 * sqrt(0.5 * (1 - clamp(xr5 * wd, -1, 1)))) +\n    (r6 * amp6 * sqrt(0.5 * (1 - clamp(xr6 * wd, -1, 1)))) +\n    (r7 * amp7 * sqrt(0.5 * (1 - clamp(xr7 * wd, -1, 1)))) +\n    (r8 * amp8 * sqrt(0.5 * (1 - clamp(xr8 * wd, -1, 1)))) +\n    (r9 * amp9 * sqrt(0.5 * (1 - clamp(xr9 * wd, -1, 1)))) +\n    (r10 * amp10 * sqrt(0.5 * (1 - clamp(xr10 * wd, -1, 1)))) +\n    (r11 * amp11 * sqrt(0.5 * (1 - clamp(xr11 * wd, -1, 1)))) +\n    (r12 * amp12 * sqrt(0.5 * (1 - clamp(xr12 * wd, -1, 1)))) +\n    (r13 * amp13 * sqrt(0.5 * (1 - clamp(xr13 * wd, -1, 1)))) +\n    (r14 * amp14 * sqrt(0.5 * (1 - clamp(xr14 * wd, -1, 1)))) +\n    (r15 * amp15 * sqrt(0.5 * (1 - clamp(xr15 * wd, -1, 1)))) +\n    (r16 * amp16 * sqrt(0.5 * (1 - clamp(xr16 * wd, -1, 1)))) +\n    (r17 * amp17 * sqrt(0.5 * (1 - clamp(xr17 * wd, -1, 1)))) +\n    (r18 * amp18 * sqrt(0.5 * (1 - clamp(xr18 * wd, -1, 1)))) +\n    (r19 * amp19 * sqrt(0.5 * (1 - clamp(xr19 * wd, -1, 1)))) +\n    (r20 * amp20 * sqrt(0.5 * (1 - clamp(xr20 * wd, -1, 1))));\nright =\n    (r1 * amp1 * sqrt(0.5 * (1 + clamp(xr1 * wd, -1, 1)))) +\n    (r2 * amp2 * sqrt(0.5 * (1 + clamp(xr2 * wd, -1, 1)))) +\n    (r3 * amp3 * sqrt(0.5 * (1 + clamp(xr3 * wd, -1, 1)))) +\n    (r4 * amp4 * sqrt(0.5 * (1 + clamp(xr4 * wd, -1, 1)))) +\n    (r5 * amp5 * sqrt(0.5 * (1 + clamp(xr5 * wd, -1, 1)))) +\n    (r6 * amp6 * sqrt(0.5 * (1 + clamp(xr6 * wd, -1, 1)))) +\n    (r7 * amp7 * sqrt(0.5 * (1 + clamp(xr7 * wd, -1, 1)))) +\n    (r8 * amp8 * sqrt(0.5 * (1 + clamp(xr8 * wd, -1, 1)))) +\n    (r9 * amp9 * sqrt(0.5 * (1 + clamp(xr9 * wd, -1, 1)))) +\n    (r10 * amp10 * sqrt(0.5 * (1 + clamp(xr10 * wd, -1, 1)))) +\n    (r11 * amp11 * sqrt(0.5 * (1 + clamp(xr11 * wd, -1, 1)))) +\n    (r12 * amp12 * sqrt(0.5 * (1 + clamp(xr12 * wd, -1, 1)))) +\n    (r13 * amp13 * sqrt(0.5 * (1 + clamp(xr13 * wd, -1, 1)))) +\n    (r14 * amp14 * sqrt(0.5 * (1 + clamp(xr14 * wd, -1, 1)))) +\n    (r15 * amp15 * sqrt(0.5 * (1 + clamp(xr15 * wd, -1, 1)))) +\n    (r16 * amp16 * sqrt(0.5 * (1 + clamp(xr16 * wd, -1, 1)))) +\n    (r17 * amp17 * sqrt(0.5 * (1 + clamp(xr17 * wd, -1, 1)))) +\n    (r18 * amp18 * sqrt(0.5 * (1 + clamp(xr18 * wd, -1, 1)))) +\n    (r19 * amp19 * sqrt(0.5 * (1 + clamp(xr19 * wd, -1, 1)))) +\n    (r20 * amp20 * sqrt(0.5 * (1 + clamp(xr20 * wd, -1, 1))));\nout1 = left * out_norm;\nout2 = right * out_norm;\n",
                    "fontface": 0,
                    "fontname": "<Monospaced>",
                    "fontsize": 12.0,
                    "id": "obj-1",
                    "maxclass": "gen.codebox~",
                    "numinlets": 9,
                    "numoutlets": 2,
                    "outlettype": [ "signal", "signal" ],
                    "patching_rect": [ 271.0, 174.0, 340.0, 200.0 ],
                    "varname": "gen~_AA"
                }
            },
            {
                "box": {
                    "id": "obj-noise-title",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 21.0, 282.0, 145.0, 20.0 ],
                    "text": "NOISE EXCITATION"
                }
            },
            {
                "box": {
                    "id": "obj-noise-1",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 21.0, 310.0, 122.0, 22.0 ],
                    "text": "noise_amount 0.22"
                }
            },
            {
                "box": {
                    "id": "obj-noise-2",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 21.0, 338.0, 122.0, 22.0 ],
                    "text": "noise_decay_ms 22"
                }
            },
            {
                "box": {
                    "id": "obj-noise-3",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 21.0, 366.0, 127.0, 22.0 ],
                    "text": "onset_threshold 0.012"
                }
            },
            {
                "box": {
                    "id": "obj-noise-4",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 21.0, 394.0, 122.0, 22.0 ],
                    "text": "onset_sensitivity 10"
                }
            },
            {
                "box": {
                    "id": "obj-noise-5",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 21.0, 422.0, 122.0, 22.0 ],
                    "text": "noise_color 0.72"
                }
            },
            {
                "box": {
                    "id": "obj-noise-6",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 21.0, 450.0, 122.0, 22.0 ],
                    "text": "noise_floor 0"
                }
            },
            {
                "box": {
                    "id": "obj-clock-title",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 990.0, 20.0, 196.0, 20.0 ],
                    "text": "MAX → PYTHON QUANTUM CLOCK"
                }
            },
            {
                "box": {
                    "id": "obj-clock-toggle",
                    "maxclass": "toggle",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "int" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 990.0, 49.0, 24.0, 24.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-clock-run-label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1022.0, 51.0, 135.0, 20.0 ],
                    "text": "RUN EXTERNAL CLOCK"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-clock-interval",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "", "bang" ],
                    "parameter_enable": 0,
                    "patching_rect": [ 990.0, 82.0, 62.0, 22.0 ]
                }
            },
            {
                "box": {
                    "id": "obj-clock-ms-label",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 1058.0, 83.0, 76.0, 20.0 ],
                    "text": "interval ms"
                }
            },
            {
                "box": {
                    "id": "obj-clock-load",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 990.0, 112.0, 99.0, 22.0 ],
                    "text": "loadmess 33.333"
                }
            },
            {
                "box": {
                    "id": "obj-clock-trigger",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "float", "float" ],
                    "patching_rect": [ 1100.0, 112.0, 39.0, 22.0 ],
                    "text": "t f f"
                }
            },
            {
                "box": {
                    "id": "obj-clock-qmetro",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "bang" ],
                    "patching_rect": [ 990.0, 145.0, 89.0, 22.0 ],
                    "text": "qmetro 33.333"
                }
            },
            {
                "box": {
                    "id": "obj-clock-prepend-set",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 1088.0, 145.0, 171.0, 22.0 ],
                    "text": "prepend set /qmw/engine/tick"
                }
            },
            {
                "box": {
                    "id": "obj-clock-message",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [ "" ],
                    "patching_rect": [ 990.0, 178.0, 169.0, 22.0 ],
                    "text": "/qmw/engine/tick 33.333"
                }
            },
            {
                "box": {
                    "id": "obj-clock-build-packet",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [ "bang", "" ],
                    "patching_rect": [ 1168.0, 178.0, 38.0, 22.0 ],
                    "text": "t b l"
                }
            },
            {
                "box": {
                    "id": "obj-clock-osc",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [ "", "", "OSCTimeTag" ],
                    "patching_rect": [ 990.0, 211.0, 116.0, 22.0 ],
                    "text": "OpenSoundControl"
                }
            },
            {
                "box": {
                    "id": "obj-clock-udp",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 990.0, 244.0, 152.0, 22.0 ],
                    "text": "udpsend 127.0.0.1 7402"
                }
            },
            {
                "box": {
                    "id": "obj-clock-help",
                    "linecount": 3,
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [ 990.0, 275.0, 218.0, 47.0 ],
                    "text": "Python: --clock-source external\nTicks coalesce while Python is busy.\nMax audio never waits for Python."
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "destination": [ "obj-34", 1 ],
                    "source": [ "obj-1", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-34", 0 ],
                    "source": [ "obj-1", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-10", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-100", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-101", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-103", 0 ],
                    "source": [ "obj-102", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-100", 0 ],
                    "source": [ "obj-103", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-102", 0 ],
                    "source": [ "obj-104", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-106", 0 ],
                    "source": [ "obj-105", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-101", 0 ],
                    "source": [ "obj-106", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-105", 0 ],
                    "source": [ "obj-107", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-105", 1 ],
                    "source": [ "obj-109", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-102", 1 ],
                    "source": [ "obj-110", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-20", 0 ],
                    "order": 1,
                    "source": [ "obj-17", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-99", 0 ],
                    "order": 0,
                    "source": [ "obj-17", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-17", 0 ],
                    "source": [ "obj-18", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-20", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-22", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-23", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-24", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-26", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-29", 0 ],
                    "source": [ "obj-27", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-30", 0 ],
                    "source": [ "obj-29", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 0 ],
                    "source": [ "obj-3", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-32", 0 ],
                    "order": 0,
                    "source": [ "obj-30", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-36", 0 ],
                    "order": 0,
                    "source": [ "obj-30", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-37", 0 ],
                    "source": [ "obj-30", 2 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-38", 0 ],
                    "order": 0,
                    "source": [ "obj-30", 3 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-39", 0 ],
                    "source": [ "obj-30", 7 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-40", 0 ],
                    "source": [ "obj-30", 6 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-41", 0 ],
                    "source": [ "obj-30", 5 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-42", 0 ],
                    "source": [ "obj-30", 4 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-46", 0 ],
                    "order": 1,
                    "source": [ "obj-30", 3 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-81", 0 ],
                    "order": 1,
                    "source": [ "obj-30", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-82", 0 ],
                    "order": 1,
                    "source": [ "obj-30", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-31", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-22", 0 ],
                    "order": 1,
                    "source": [ "obj-32", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-47", 0 ],
                    "hidden": 1,
                    "order": 0,
                    "source": [ "obj-32", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-33", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-6", 1 ],
                    "order": 0,
                    "source": [ "obj-34", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-6", 0 ],
                    "order": 1,
                    "source": [ "obj-34", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-50", 0 ],
                    "hidden": 1,
                    "source": [ "obj-36", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-24", 0 ],
                    "order": 0,
                    "source": [ "obj-37", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-83", 0 ],
                    "order": 1,
                    "source": [ "obj-37", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-68", 0 ],
                    "source": [ "obj-38", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-104", 0 ],
                    "order": 0,
                    "source": [ "obj-39", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-23", 0 ],
                    "order": 4,
                    "source": [ "obj-39", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-54", 0 ],
                    "hidden": 1,
                    "order": 2,
                    "source": [ "obj-39", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-56", 0 ],
                    "hidden": 1,
                    "order": 1,
                    "source": [ "obj-39", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-75", 0 ],
                    "order": 3,
                    "source": [ "obj-39", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-80", 0 ],
                    "order": 5,
                    "source": [ "obj-39", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-4", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-52", 0 ],
                    "hidden": 1,
                    "order": 1,
                    "source": [ "obj-40", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-58", 0 ],
                    "hidden": 1,
                    "order": 0,
                    "source": [ "obj-40", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-107", 0 ],
                    "order": 0,
                    "source": [ "obj-41", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-18", 0 ],
                    "order": 2,
                    "source": [ "obj-41", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-60", 0 ],
                    "hidden": 1,
                    "order": 1,
                    "source": [ "obj-41", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-91", 0 ],
                    "order": 3,
                    "source": [ "obj-41", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-62", 0 ],
                    "hidden": 1,
                    "order": 0,
                    "source": [ "obj-42", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-74", 0 ],
                    "order": 1,
                    "source": [ "obj-42", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-44", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-44", 0 ],
                    "source": [ "obj-46", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-48", 0 ],
                    "hidden": 1,
                    "source": [ "obj-47", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 1 ],
                    "hidden": 1,
                    "source": [ "obj-48", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 2 ],
                    "hidden": 1,
                    "source": [ "obj-49", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-5", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-49", 0 ],
                    "hidden": 1,
                    "source": [ "obj-50", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 3 ],
                    "hidden": 1,
                    "source": [ "obj-51", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-51", 0 ],
                    "hidden": 1,
                    "source": [ "obj-52", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 4 ],
                    "hidden": 1,
                    "source": [ "obj-53", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-53", 0 ],
                    "hidden": 1,
                    "source": [ "obj-54", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 8 ],
                    "hidden": 1,
                    "source": [ "obj-55", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-55", 0 ],
                    "hidden": 1,
                    "source": [ "obj-56", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 7 ],
                    "hidden": 1,
                    "source": [ "obj-57", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-57", 0 ],
                    "hidden": 1,
                    "source": [ "obj-58", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 6 ],
                    "hidden": 1,
                    "source": [ "obj-59", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-59", 0 ],
                    "hidden": 1,
                    "source": [ "obj-60", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 5 ],
                    "hidden": 1,
                    "source": [ "obj-61", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-61", 0 ],
                    "hidden": 1,
                    "source": [ "obj-62", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-64", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-65", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-66", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-69", 0 ],
                    "source": [ "obj-68", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-71", 0 ],
                    "source": [ "obj-69", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 0 ],
                    "source": [ "obj-70", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-73", 0 ],
                    "source": [ "obj-71", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-70", 0 ],
                    "source": [ "obj-72", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-73", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-84", 0 ],
                    "source": [ "obj-74", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-85", 0 ],
                    "source": [ "obj-75", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-77", 0 ],
                    "source": [ "obj-76", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-77", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-78", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-78", 0 ],
                    "source": [ "obj-79", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-8", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-79", 0 ],
                    "source": [ "obj-80", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-64", 0 ],
                    "source": [ "obj-81", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-65", 0 ],
                    "source": [ "obj-82", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-66", 0 ],
                    "source": [ "obj-83", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-76", 0 ],
                    "source": [ "obj-84", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-72", 0 ],
                    "source": [ "obj-85", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-85", 1 ],
                    "source": [ "obj-87", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-90", 0 ],
                    "source": [ "obj-88", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 0 ],
                    "source": [ "obj-89", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 0 ],
                    "source": [ "obj-9", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-89", 0 ],
                    "source": [ "obj-90", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-88", 0 ],
                    "source": [ "obj-91", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-1", 0 ],
                    "source": [ "obj-92", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-92", 0 ],
                    "source": [ "obj-94", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-98", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-3", 0 ],
                    "source": [ "obj-99", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-noise-1", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-noise-2", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-noise-3", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-noise-4", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-noise-5", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-9", 0 ],
                    "source": [ "obj-noise-6", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-qmetro", 0 ],
                    "source": [ "obj-clock-toggle", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-interval", 0 ],
                    "source": [ "obj-clock-load", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-trigger", 0 ],
                    "source": [ "obj-clock-interval", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-qmetro", 1 ],
                    "source": [ "obj-clock-trigger", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-prepend-set", 0 ],
                    "source": [ "obj-clock-trigger", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-message", 0 ],
                    "source": [ "obj-clock-prepend-set", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-message", 0 ],
                    "source": [ "obj-clock-qmetro", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-build-packet", 0 ],
                    "source": [ "obj-clock-message", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-osc", 0 ],
                    "source": [ "obj-clock-build-packet", 1 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-osc", 0 ],
                    "source": [ "obj-clock-build-packet", 0 ]
                }
            },
            {
                "patchline": {
                    "destination": [ "obj-clock-udp", 0 ],
                    "source": [ "obj-clock-osc", 0 ]
                }
            }
        ],
        "parameters": {
            "obj-34": [ "live.gain~", "live.gain~", 0 ],
            "parameterbanks": {
                "0": {
                    "index": 0,
                    "name": "",
                    "parameters": [ "-", "-", "-", "-", "-", "-", "-", "-" ],
                    "buttons": [ "-", "-", "-", "-", "-", "-", "-", "-" ]
                }
            },
            "inherited_shortname": 1
        },
        "autosave": 0
    }
}
