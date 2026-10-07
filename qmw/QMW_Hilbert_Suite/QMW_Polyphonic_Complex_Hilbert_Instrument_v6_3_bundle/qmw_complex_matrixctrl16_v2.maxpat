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
      34.0,
      100.0,
      1220.0,
      790.0
    ],
    "gridsize": [
      15.0,
      15.0
    ],
    "boxes": [
      {
        "box": {
          "fontface": 1,
          "fontsize": 18.0,
          "id": "title",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            15.0,
            565.0,
            27.0
          ],
          "text": "QMW COMPLEX MATRIX PERFORMANCE EDITOR v2 \u2014 16 \u00d7 16"
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            30.0,
            43.0,
            650.0,
            20.0
          ],
          "text": "column = source/input harmonic j     row = destination/output harmonic i     cell = |rho[i,j]|"
        }
      },
      {
        "box": {
          "comment": "",
          "id": "in-control",
          "index": 1,
          "maxclass": "inlet",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            735.0,
            20.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "comment": "",
          "id": "in-re",
          "index": 2,
          "maxclass": "inlet",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            795.0,
            20.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "comment": "",
          "id": "in-im",
          "index": 3,
          "maxclass": "inlet",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            855.0,
            20.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "id": "in-labels",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            705.0,
            52.0,
            260.0,
            20.0
          ],
          "text": "control       upstream Re       upstream Im"
        }
      },
      {
        "box": {
          "columns": 16,
          "dialmode": 2,
          "id": "grid",
          "maxclass": "matrixctrl",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "list",
            "list"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            45.0,
            95.0,
            544.0,
            544.0
          ],
          "rows": 16
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "grid-top",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            180.0,
            70.0,
            250.0,
            20.0
          ],
          "text": "SOURCE / INPUT HARMONIC  0 \u2026 15"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "grid-side",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            45.0,
            646.0,
            200.0,
            20.0
          ],
          "text": "DESTINATION / OUTPUT"
        }
      },
      {
        "box": {
          "id": "js",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 7,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ],
          "patching_rect": [
            665.0,
            95.0,
            245.0,
            22.0
          ],
          "saved_object_attributes": {
            "filename": "qmw_complex_matrixctrl16_v1.js",
            "parameter_enable": 0
          },
          "text": "js qmw_complex_matrixctrl16_v1.js"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "source-title",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            135.0,
            130.0,
            20.0
          ],
          "text": "MATRIX SOURCE"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "follow",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            160.0,
            48.0,
            22.0
          ],
          "text": "follow"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "freeze",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            720.0,
            160.0,
            48.0,
            22.0
          ],
          "text": "freeze"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "manual",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            775.0,
            160.0,
            52.0,
            22.0
          ],
          "text": "manual"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "morph",
          "maxclass": "flonum",
          "maximum": 1.0,
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            840.0,
            160.0,
            60.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "prepend-morph",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            840.0,
            190.0,
            95.0,
            22.0
          ],
          "text": "prepend morph"
        }
      },
      {
        "box": {
          "id": "morph-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            910.0,
            162.0,
            160.0,
            20.0
          ],
          "text": "0 upstream  /  1 manual"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "selected-title",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            230.0,
            190.0,
            20.0
          ],
          "text": "SELECTED COMPLEX CELL"
        }
      },
      {
        "box": {
          "id": "column",
          "maxclass": "number",
          "maximum": 15,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            665.0,
            260.0,
            50.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "row",
          "maxclass": "number",
          "maximum": 15,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            730.0,
            260.0,
            50.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "cell-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            285.0,
            145.0,
            20.0
          ],
          "text": "column j       row i"
        }
      },
      {
        "box": {
          "id": "pak-select",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            310.0,
            100.0,
            22.0
          ],
          "text": "pak select 0 0"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "magnitude",
          "maxclass": "flonum",
          "maximum": 1.0,
          "minimum": 0.0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            665.0,
            355.0,
            75.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "phase",
          "maxclass": "flonum",
          "maximum": 3.141593,
          "minimum": -3.141593,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            755.0,
            355.0,
            75.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "selected-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            380.0,
            250.0,
            20.0
          ],
          "text": "magnitude                    phase radians"
        }
      },
      {
        "box": {
          "id": "prepend-mag",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            405.0,
            125.0,
            22.0
          ],
          "text": "prepend magnitude"
        }
      },
      {
        "box": {
          "id": "prepend-phase",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800.0,
            405.0,
            105.0,
            22.0
          ],
          "text": "prepend phase"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "real-display",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            930.0,
            355.0,
            75.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "imag-display",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1020.0,
            355.0,
            75.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "ri-label",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            930.0,
            380.0,
            222.0,
            20.0
          ],
          "text": "Re (computed)                 Im (computed)"
        }
      },
      {
        "box": {
          "id": "unpack-selected",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
            "int",
            "int",
            "float",
            "float",
            "float",
            "float"
          ],
          "patching_rect": [
            930.0,
            310.0,
            145.0,
            22.0
          ],
          "text": "unpack i i f f f f"
        }
      },
      {
        "box": {
          "id": "identity",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            465.0,
            53.0,
            22.0
          ],
          "text": "identity"
        }
      },
      {
        "box": {
          "id": "clear-offdiag",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            730.0,
            465.0,
            82.0,
            22.0
          ],
          "text": "clearoffdiag"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "hermitian-on",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            510.0,
            76.0,
            22.0
          ],
          "text": "hermitian 1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "hermitian-off",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            750.0,
            510.0,
            76.0,
            22.0
          ],
          "text": "hermitian 0"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "safety-on",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            545.0,
            57.0,
            22.0
          ],
          "text": "safety 1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "safety-off",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            730.0,
            545.0,
            57.0,
            22.0
          ],
          "text": "safety 0"
        }
      },
      {
        "box": {
          "id": "safety-note",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            555.0,
            530.0,
            20.0
          ],
          "text": "Hermitian lock mirrors conjugate cells. Safety constrains maximum complex row/column sum to 1."
        }
      },
      {
        "box": {
          "id": "physical-note",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            595.0,
            598.0,
            20.0
          ],
          "text": "Manual/free edits are an audio routing operator; they are not guaranteed positive-semidefinite density matrices."
        }
      },
      {
        "box": {
          "id": "print",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            930.0,
            95.0,
            155.0,
            22.0
          ],
          "text": "print qmw.matrixctrl16"
        }
      },
      {
        "box": {
          "id": "loadbang",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "patching_rect": [
            1100.0,
            20.0,
            60.0,
            22.0
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "trigger-load",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "bang",
            "bang",
            "bang"
          ],
          "patching_rect": [
            1100.0,
            50.0,
            60.0,
            22.0
          ],
          "text": "t b b b"
        }
      },
      {
        "box": {
          "comment": "",
          "id": "out-re",
          "index": 1,
          "maxclass": "outlet",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            700.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "comment": "",
          "id": "out-im",
          "index": 2,
          "maxclass": "outlet",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            735.0,
            700.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "comment": "",
          "id": "out-commit",
          "index": 3,
          "maxclass": "outlet",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            805.0,
            700.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "comment": "",
          "id": "out-status",
          "index": 4,
          "maxclass": "outlet",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            875.0,
            700.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "id": "out-labels",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            645.0,
            735.0,
            330.0,
            20.0
          ],
          "text": "Re matrix       Im matrix       commit          status"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-column",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            235.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-row",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            730.0,
            235.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-magnitude",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            665.0,
            330.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-phase",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            755.0,
            330.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-real",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            949.0,
            335.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-imag",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1020.0,
            335.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "id": "source-menu",
          "items": [
            "follow",
            ",",
            "freeze",
            ",",
            "manual",
            ",",
            "morph"
          ],
          "maxclass": "umenu",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "int",
            "",
            ""
          ],
          "parameter_enable": 0,
          "patching_rect": [
            665.0,
            160.0,
            160.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-source-menu",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            650.0,
            130.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "id": "hermitian-toggle",
          "maxclass": "toggle",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            665.0,
            520.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend-hermitian",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            695.0,
            510.0,
            115.0,
            22.0
          ],
          "text": "prepend hermitian"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-hermitian-toggle",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            820.0,
            510.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "id": "safety-toggle",
          "maxclass": "toggle",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            730.0,
            520.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "prepend-safety",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            695.0,
            545.0,
            100.0,
            22.0
          ],
          "text": "prepend safety"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-safety-toggle",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            805.0,
            545.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "ui-unpack",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
            "int",
            "int",
            "int",
            "float",
            "int"
          ],
          "patching_rect": [
            930.0,
            465.0,
            125.0,
            22.0
          ],
          "text": "unpack i i i f i"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "safety-scale-display",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            795.0,
            520.0,
            75.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-safety-scale",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            875.0,
            510.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "id": "commit-count-display",
          "ignoreclick": 1,
          "maxclass": "number",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            885.0,
            520.0,
            65.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "hidden": 1,
          "id": "set-commit-count",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1070.0,
            510.0,
            48.0,
            22.0
          ],
          "text": "set $1"
        }
      },
      {
        "box": {
          "id": "applied-led",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            975.0,
            517.0,
            30.0,
            30.0
          ]
        }
      },
      {
        "box": {
          "fontface": 1,
          "hidden": 1,
          "id": "persistent-labels",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            580.0,
            522.0,
            20.0
          ],
          "text": "HERMITIAN LOCK                         SAFETY                     SCALE           COMMITS       APPLIED"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "label-hermitian",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            665.0,
            495.0,
            110.0,
            20.0
          ],
          "text": "Hermitian Lock"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "label-safety",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            730.0,
            495.0,
            60.0,
            20.0
          ],
          "text": "Safety"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "label-scale",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            795.0,
            495.0,
            60.0,
            20.0
          ],
          "text": "Scale"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "label-commits",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            885.0,
            495.0,
            70.0,
            20.0
          ],
          "text": "Commits"
        }
      },
      {
        "box": {
          "fontface": 1,
          "id": "label-applied",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            965.0,
            495.0,
            70.0,
            20.0
          ],
          "text": "Applied"
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "clear-offdiag",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "pak-select",
            1
          ],
          "source": [
            "column",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "follow",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "freeze",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "grid",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "hermitian-off",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "hermitian-on",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend-hermitian",
            0
          ],
          "source": [
            "hermitian-toggle",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "identity",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "in-control",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            2
          ],
          "source": [
            "in-im",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            1
          ],
          "source": [
            "in-re",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "applied-led",
            0
          ],
          "order": 0,
          "source": [
            "js",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "grid",
            0
          ],
          "source": [
            "js",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "out-commit",
            0
          ],
          "order": 1,
          "source": [
            "js",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "out-im",
            0
          ],
          "source": [
            "js",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "out-re",
            0
          ],
          "source": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "out-status",
            0
          ],
          "order": 1,
          "source": [
            "js",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "print",
            0
          ],
          "order": 0,
          "source": [
            "js",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "ui-unpack",
            0
          ],
          "source": [
            "js",
            6
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "unpack-selected",
            0
          ],
          "source": [
            "js",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "trigger-load",
            0
          ],
          "source": [
            "loadbang",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend-mag",
            0
          ],
          "source": [
            "magnitude",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "manual",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend-morph",
            0
          ],
          "source": [
            "morph",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "pak-select",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend-phase",
            0
          ],
          "source": [
            "phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "prepend-hermitian",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "prepend-mag",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "prepend-morph",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "prepend-phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "prepend-safety",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "pak-select",
            2
          ],
          "source": [
            "row",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "safety-off",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "safety-on",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "prepend-safety",
            0
          ],
          "source": [
            "safety-toggle",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "column",
            0
          ],
          "source": [
            "set-column",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "commit-count-display",
            0
          ],
          "source": [
            "set-commit-count",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "hermitian-toggle",
            0
          ],
          "source": [
            "set-hermitian-toggle",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "imag-display",
            0
          ],
          "source": [
            "set-imag",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "magnitude",
            0
          ],
          "source": [
            "set-magnitude",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "phase",
            0
          ],
          "source": [
            "set-phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "real-display",
            0
          ],
          "source": [
            "set-real",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "row",
            0
          ],
          "source": [
            "set-row",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "safety-scale-display",
            0
          ],
          "source": [
            "set-safety-scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "safety-toggle",
            0
          ],
          "source": [
            "set-safety-toggle",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "source-menu",
            0
          ],
          "source": [
            "set-source-menu",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "js",
            0
          ],
          "source": [
            "source-menu",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "follow",
            0
          ],
          "source": [
            "trigger-load",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "hermitian-on",
            0
          ],
          "source": [
            "trigger-load",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "safety-on",
            0
          ],
          "source": [
            "trigger-load",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-commit-count",
            0
          ],
          "source": [
            "ui-unpack",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-hermitian-toggle",
            0
          ],
          "source": [
            "ui-unpack",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-safety-scale",
            0
          ],
          "source": [
            "ui-unpack",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-safety-toggle",
            0
          ],
          "source": [
            "ui-unpack",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-source-menu",
            0
          ],
          "source": [
            "ui-unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-column",
            0
          ],
          "source": [
            "unpack-selected",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-imag",
            0
          ],
          "source": [
            "unpack-selected",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-magnitude",
            0
          ],
          "source": [
            "unpack-selected",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-phase",
            0
          ],
          "source": [
            "unpack-selected",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-real",
            0
          ],
          "source": [
            "unpack-selected",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "set-row",
            0
          ],
          "source": [
            "unpack-selected",
            1
          ]
        }
      }
    ],
    "originid": "pat-45",
    "dependency_cache": [
      {
        "name": "qmw_complex_matrixctrl16_v1.js",
        "bootpath": "~/QuantumSonification/QMW_Hilbert_Suite",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
