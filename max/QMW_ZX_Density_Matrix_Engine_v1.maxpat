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
      60,
      35,
      1245,
      1030
    ],
    "gridsize": [
      15,
      15
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            15,
            1040,
            28
          ],
          "text": "QMW ZX Density Matrix Engine \u2014 dynamic atomic complex OSC receiver",
          "fontsize": 17
        }
      },
      {
        "box": {
          "id": "help",
          "maxclass": "comment",
          "patching_rect": [
            25,
            45,
            1160,
            40
          ],
          "text": "Listens on UDP 7498 using CNMAT OSC-route (no oscparse). Complete 2\u00d72 through 256\u00d7256 revisions drive five Jitter matrix buses, metrics, Bloch data, and a folded 16-voice instrument."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            95,
            120,
            22
          ],
          "text": "udpreceive 7498",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "routes",
          "maxclass": "newobj",
          "patching_rect": [
            165,
            95,
            1055,
            22
          ],
          "text": "OSC-route /qmw/zx/density/begin /qmw/zx/density/meta /qmw/zx/density/probabilities /qmw/zx/density/row /qmw/zx/density/bloch /qmw/zx/density/end /qmw/zx/density/error /qmw/zx/density/commit_sent /qmw/zx/pauli/verified /qmw/zx/pauli/score_verified /qmw/zx/pauli/active /qmw/zx/pauli/live /qmw/zx/pauli/error /qmw/zx/euler/result",
          "numinlets": 1,
          "numoutlets": 15,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_begin",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            140,
            160,
            22
          ],
          "text": "prepend begin",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_meta",
          "maxclass": "newobj",
          "patching_rect": [
            311,
            140,
            160,
            22
          ],
          "text": "prepend meta",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_probabilities",
          "maxclass": "newobj",
          "patching_rect": [
            597,
            140,
            160,
            22
          ],
          "text": "prepend probabilities",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_row",
          "maxclass": "newobj",
          "patching_rect": [
            883,
            140,
            160,
            22
          ],
          "text": "prepend row",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_bloch",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            174,
            160,
            22
          ],
          "text": "prepend bloch",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_end",
          "maxclass": "newobj",
          "patching_rect": [
            311,
            174,
            160,
            22
          ],
          "text": "prepend end",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_error",
          "maxclass": "newobj",
          "patching_rect": [
            597,
            174,
            160,
            22
          ],
          "text": "prepend error",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_commit_sent",
          "maxclass": "newobj",
          "patching_rect": [
            883,
            174,
            160,
            22
          ],
          "text": "prepend commit_sent",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_pauli_verified",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            208,
            160,
            22
          ],
          "text": "prepend pauli_verified",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_pauli_score_verified",
          "maxclass": "newobj",
          "patching_rect": [
            311,
            208,
            160,
            22
          ],
          "text": "prepend pauli_score_verified",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_pauli_active",
          "maxclass": "newobj",
          "patching_rect": [
            597,
            208,
            160,
            22
          ],
          "text": "prepend pauli_active",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_pauli_live",
          "maxclass": "newobj",
          "patching_rect": [
            883,
            208,
            160,
            22
          ],
          "text": "prepend pauli_live",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_pauli_error",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            242,
            160,
            22
          ],
          "text": "prepend pauli_error",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "prepend_euler_result",
          "maxclass": "newobj",
          "patching_rect": [
            311,
            242,
            160,
            22
          ],
          "text": "prepend euler_result",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "engine",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            220,
            310,
            22
          ],
          "text": "js qmw_zx_density_matrix_engine_v1.js",
          "numinlets": 1,
          "numoutlets": 12,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "revision_label",
          "maxclass": "comment",
          "patching_rect": [
            355,
            222,
            60,
            20
          ],
          "text": "revision"
        }
      },
      {
        "box": {
          "id": "revision",
          "maxclass": "number",
          "patching_rect": [
            418,
            220,
            78,
            22
          ],
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
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            515,
            220,
            690,
            22
          ],
          "text": "waiting for a complete density revision...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "matrix_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            270,
            375,
            20
          ],
          "text": "Normalized |\u03c1\u1d62\u2c7c| \u2014 updates only after every dynamic row arrives"
        }
      },
      {
        "box": {
          "id": "matrix_view",
          "maxclass": "jit.pwindow",
          "patching_rect": [
            25,
            295,
            390,
            390
          ],
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "jit_matrix",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "complex_send",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            270,
            210,
            22
          ],
          "text": "s qmw.zx.rho.complex.matrix",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "real_send",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            300,
            190,
            22
          ],
          "text": "s qmw.zx.rho.real.matrix",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "imag_send",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            330,
            190,
            22
          ],
          "text": "s qmw.zx.rho.imag.matrix",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "magnitude_send",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            360,
            225,
            22
          ],
          "text": "s qmw.zx.rho.magnitude.matrix",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "phase_send",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            390,
            195,
            22
          ],
          "text": "s qmw.zx.rho.phase.matrix",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "euler_panel",
          "maxclass": "panel",
          "patching_rect": [
            430,
            410,
            245,
            330
          ],
          "bgcolor": [
            0.94,
            0.97,
            0.94,
            1.0
          ],
          "border": 1,
          "rounded": 8,
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "euler_title",
          "maxclass": "comment",
          "patching_rect": [
            440,
            420,
            220,
            22
          ],
          "text": "Euler decomposition \u2014 radians",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "euler_receive",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            446,
            210,
            22
          ],
          "text": "r qmw.euler.result",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "euler_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            472,
            225,
            22
          ],
          "text": "unpack i s i s f f f f f i f",
          "numinlets": 1,
          "numoutlets": 11,
          "outlettype": [
            "int",
            "",
            "int",
            "",
            "float",
            "float",
            "float",
            "float",
            "float",
            "int",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "euler_request_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            499,
            52,
            18
          ],
          "text": "request"
        }
      },
      {
        "box": {
          "id": "euler_request",
          "maxclass": "number",
          "patching_rect": [
            493,
            497,
            52,
            22
          ],
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
          "id": "euler_qubit_label",
          "maxclass": "comment",
          "patching_rect": [
            552,
            499,
            40,
            18
          ],
          "text": "qubit"
        }
      },
      {
        "box": {
          "id": "euler_qubit",
          "maxclass": "number",
          "patching_rect": [
            595,
            497,
            60,
            22
          ],
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
          "id": "euler_source_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            524,
            48,
            18
          ],
          "text": "source"
        }
      },
      {
        "box": {
          "id": "euler_source",
          "maxclass": "message",
          "patching_rect": [
            490,
            522,
            85,
            22
          ],
          "text": "\u2014",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "euler_basis_label",
          "maxclass": "comment",
          "patching_rect": [
            582,
            524,
            35,
            18
          ],
          "text": "basis"
        }
      },
      {
        "box": {
          "id": "euler_basis",
          "maxclass": "message",
          "patching_rect": [
            620,
            522,
            40,
            22
          ],
          "text": "\u2014",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "euler_theta_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            574,
            62,
            18
          ],
          "text": "theta \u03b8"
        }
      },
      {
        "box": {
          "id": "euler_angle_columns",
          "maxclass": "comment",
          "patching_rect": [
            505,
            550,
            150,
            18
          ],
          "text": "radians              \u00d7 \u03c0"
        }
      },
      {
        "box": {
          "id": "euler_theta",
          "maxclass": "flonum",
          "patching_rect": [
            505,
            572,
            70,
            22
          ],
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
          "id": "euler_theta_pi",
          "maxclass": "flonum",
          "patching_rect": [
            585,
            572,
            70,
            22
          ],
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
          "id": "euler_phi_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            598,
            62,
            18
          ],
          "text": "phi \u03c6"
        }
      },
      {
        "box": {
          "id": "euler_phi",
          "maxclass": "flonum",
          "patching_rect": [
            505,
            596,
            70,
            22
          ],
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
          "id": "euler_phi_pi",
          "maxclass": "flonum",
          "patching_rect": [
            585,
            596,
            70,
            22
          ],
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
          "id": "euler_lambda_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            622,
            62,
            18
          ],
          "text": "lambda \u03bb"
        }
      },
      {
        "box": {
          "id": "euler_lambda",
          "maxclass": "flonum",
          "patching_rect": [
            505,
            620,
            70,
            22
          ],
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
          "id": "euler_lambda_pi",
          "maxclass": "flonum",
          "patching_rect": [
            585,
            620,
            70,
            22
          ],
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
          "id": "euler_gamma_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            646,
            62,
            18
          ],
          "text": "gamma \u03b3"
        }
      },
      {
        "box": {
          "id": "euler_gamma",
          "maxclass": "flonum",
          "patching_rect": [
            505,
            644,
            70,
            22
          ],
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
          "id": "euler_gamma_pi",
          "maxclass": "flonum",
          "patching_rect": [
            585,
            644,
            70,
            22
          ],
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
          "id": "euler_scalar_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            670,
            62,
            18
          ],
          "text": "ZX scalar"
        }
      },
      {
        "box": {
          "id": "euler_scalar",
          "maxclass": "flonum",
          "patching_rect": [
            505,
            668,
            70,
            22
          ],
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
          "id": "euler_scalar_pi",
          "maxclass": "flonum",
          "patching_rect": [
            585,
            668,
            70,
            22
          ],
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
          "id": "euler_verified_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            698,
            54,
            18
          ],
          "text": "verified"
        }
      },
      {
        "box": {
          "id": "euler_verified",
          "maxclass": "toggle",
          "patching_rect": [
            495,
            696,
            22,
            22
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "euler_error_label",
          "maxclass": "comment",
          "patching_rect": [
            525,
            698,
            32,
            18
          ],
          "text": "error"
        }
      },
      {
        "box": {
          "id": "euler_error",
          "maxclass": "flonum",
          "patching_rect": [
            558,
            696,
            97,
            22
          ],
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
          "id": "euler_theta_pi_receive",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            718,
            200,
            22
          ],
          "text": "r qmw.euler.theta_pi",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "euler_phi_pi_receive",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            718,
            200,
            22
          ],
          "text": "r qmw.euler.phi_pi",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "euler_lambda_pi_receive",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            718,
            200,
            22
          ],
          "text": "r qmw.euler.lambda_pi",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "euler_gamma_pi_receive",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            718,
            200,
            22
          ],
          "text": "r qmw.euler.gamma_pi",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "euler_scalar_pi_receive",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            718,
            215,
            22
          ],
          "text": "r qmw.euler.zx_scalar_phase_pi",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "population_label",
          "maxclass": "comment",
          "patching_rect": [
            690,
            270,
            275,
            20
          ],
          "text": "basis populations \u03c1\u1d62\u1d62"
        }
      },
      {
        "box": {
          "id": "populations",
          "maxclass": "multislider",
          "patching_rect": [
            690,
            295,
            500,
            105
          ],
          "size": 16,
          "setminmax": [
            0.0,
            1.0
          ],
          "slidercolor": [
            0.37,
            0.72,
            0.48,
            1.0
          ],
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
          "id": "density_dimension_receive",
          "maxclass": "newobj",
          "patching_rect": [
            690,
            402,
            205,
            22
          ],
          "text": "r qmw.zx.density.dimension",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "population_size",
          "maxclass": "newobj",
          "patching_rect": [
            900,
            402,
            95,
            22
          ],
          "text": "prepend size",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "hidden": 1
        }
      },
      {
        "box": {
          "id": "metrics_label",
          "maxclass": "comment",
          "patching_rect": [
            690,
            420,
            500,
            20
          ],
          "text": "revision \u00b7 trace \u00b7 purity \u00b7 coherence \u2113\u2081 \u00b7 entropy \u00b7 min \u03bb \u00b7 weight"
        }
      },
      {
        "box": {
          "id": "metrics_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            690,
            445,
            180,
            22
          ],
          "text": "unpack i f f f f f f",
          "numinlets": 1,
          "numoutlets": 7,
          "outlettype": [
            "int",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float"
          ]
        }
      },
      {
        "box": {
          "id": "bloch_label",
          "maxclass": "comment",
          "patching_rect": [
            690,
            515,
            260,
            20
          ],
          "text": "q \u00b7 Bloch x y z \u00b7 local purity \u00b7 entropy"
        }
      },
      {
        "box": {
          "id": "bloch_display",
          "maxclass": "message",
          "patching_rect": [
            690,
            540,
            500,
            22
          ],
          "text": "waiting for local Bloch vectors...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "voice_label",
          "maxclass": "comment",
          "patching_rect": [
            440,
            750,
            750,
            34
          ],
          "text": "Folded 16-voice instrument: arbitrary-dimensional populations drive amplitude; coherence and phase drive excitation/detuning."
        }
      },
      {
        "box": {
          "id": "freq_apply",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            795,
            118,
            22
          ],
          "text": "prepend applyvalues",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "frequency_signal",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            795,
            132,
            22
          ],
          "text": "mc.sig~ 110 @chans 16",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "frequency_smooth",
          "maxclass": "newobj",
          "patching_rect": [
            725,
            795,
            142,
            22
          ],
          "text": "mc.slide~ 2400 2400",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "oscillators",
          "maxclass": "newobj",
          "patching_rect": [
            885,
            795,
            128,
            22
          ],
          "text": "mc.cycle~ @chans 16",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "amp_apply",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            835,
            118,
            22
          ],
          "text": "prepend applyvalues",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "amplitude_signal",
          "maxclass": "newobj",
          "patching_rect": [
            575,
            835,
            122,
            22
          ],
          "text": "mc.sig~ 0. @chans 16",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "amplitude_smooth",
          "maxclass": "newobj",
          "patching_rect": [
            715,
            835,
            142,
            22
          ],
          "text": "mc.slide~ 4800 4800",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "voice_gain",
          "maxclass": "newobj",
          "patching_rect": [
            885,
            835,
            58,
            22
          ],
          "text": "mc.*~",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "mixdown",
          "maxclass": "newobj",
          "patching_rect": [
            960,
            835,
            185,
            22
          ],
          "text": "mc.mixdown~ 2 @autogain 1",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "multichannelsignal"
          ]
        }
      },
      {
        "box": {
          "id": "unpack_audio",
          "maxclass": "newobj",
          "patching_rect": [
            960,
            875,
            90,
            22
          ],
          "text": "mc.unpack~ 2",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "left_gain",
          "maxclass": "newobj",
          "patching_rect": [
            930,
            915,
            55,
            22
          ],
          "text": "*~ 0.55",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "right_gain",
          "maxclass": "newobj",
          "patching_rect": [
            1015,
            915,
            55,
            22
          ],
          "text": "*~ 0.55",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ]
        }
      },
      {
        "box": {
          "id": "audio_prompt",
          "maxclass": "comment",
          "patching_rect": [
            730,
            973,
            330,
            22
          ],
          "text": "Click speaker after a matrix revision arrives \u2192"
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            1080,
            960,
            68,
            36
          ],
          "text": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "metric_label_0",
          "maxclass": "comment",
          "patching_rect": [
            690,
            474,
            67,
            18
          ],
          "text": "rev"
        }
      },
      {
        "box": {
          "id": "metric_0",
          "maxclass": "number",
          "patching_rect": [
            690,
            492,
            67,
            22
          ],
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
          "id": "metric_label_1",
          "maxclass": "comment",
          "patching_rect": [
            762,
            474,
            67,
            18
          ],
          "text": "trace"
        }
      },
      {
        "box": {
          "id": "metric_1",
          "maxclass": "flonum",
          "patching_rect": [
            762,
            492,
            67,
            22
          ],
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
          "id": "metric_label_2",
          "maxclass": "comment",
          "patching_rect": [
            834,
            474,
            67,
            18
          ],
          "text": "purity"
        }
      },
      {
        "box": {
          "id": "metric_2",
          "maxclass": "flonum",
          "patching_rect": [
            834,
            492,
            67,
            22
          ],
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
          "id": "metric_label_3",
          "maxclass": "comment",
          "patching_rect": [
            906,
            474,
            67,
            18
          ],
          "text": "coherence"
        }
      },
      {
        "box": {
          "id": "metric_3",
          "maxclass": "flonum",
          "patching_rect": [
            906,
            492,
            67,
            22
          ],
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
          "id": "metric_label_4",
          "maxclass": "comment",
          "patching_rect": [
            978,
            474,
            67,
            18
          ],
          "text": "entropy"
        }
      },
      {
        "box": {
          "id": "metric_4",
          "maxclass": "flonum",
          "patching_rect": [
            978,
            492,
            67,
            22
          ],
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
          "id": "metric_label_5",
          "maxclass": "comment",
          "patching_rect": [
            1050,
            474,
            67,
            18
          ],
          "text": "min \u03bb"
        }
      },
      {
        "box": {
          "id": "metric_5",
          "maxclass": "flonum",
          "patching_rect": [
            1050,
            492,
            67,
            22
          ],
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
          "id": "metric_label_6",
          "maxclass": "comment",
          "patching_rect": [
            1122,
            474,
            67,
            18
          ],
          "text": "weight"
        }
      },
      {
        "box": {
          "id": "metric_6",
          "maxclass": "flonum",
          "patching_rect": [
            1122,
            492,
            67,
            22
          ],
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "udp",
            0
          ],
          "destination": [
            "routes",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            0
          ],
          "destination": [
            "prepend_begin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_begin",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            1
          ],
          "destination": [
            "prepend_meta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_meta",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            2
          ],
          "destination": [
            "prepend_probabilities",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_probabilities",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            3
          ],
          "destination": [
            "prepend_row",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_row",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            4
          ],
          "destination": [
            "prepend_bloch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_bloch",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            5
          ],
          "destination": [
            "prepend_end",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_end",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            6
          ],
          "destination": [
            "prepend_error",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_error",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            7
          ],
          "destination": [
            "prepend_commit_sent",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_commit_sent",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            8
          ],
          "destination": [
            "prepend_pauli_verified",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_pauli_verified",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            9
          ],
          "destination": [
            "prepend_pauli_score_verified",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_pauli_score_verified",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            10
          ],
          "destination": [
            "prepend_pauli_active",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_pauli_active",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            11
          ],
          "destination": [
            "prepend_pauli_live",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_pauli_live",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            12
          ],
          "destination": [
            "prepend_pauli_error",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_pauli_error",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "routes",
            13
          ],
          "destination": [
            "prepend_euler_result",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "prepend_euler_result",
            0
          ],
          "destination": [
            "engine",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metrics_unpack",
            0
          ],
          "destination": [
            "metric_0",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metrics_unpack",
            1
          ],
          "destination": [
            "metric_1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metrics_unpack",
            2
          ],
          "destination": [
            "metric_2",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metrics_unpack",
            3
          ],
          "destination": [
            "metric_3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metrics_unpack",
            4
          ],
          "destination": [
            "metric_4",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metrics_unpack",
            5
          ],
          "destination": [
            "metric_5",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "metrics_unpack",
            6
          ],
          "destination": [
            "metric_6",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_receive",
            0
          ],
          "destination": [
            "euler_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            0
          ],
          "destination": [
            "euler_request",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            1
          ],
          "destination": [
            "euler_source",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            2
          ],
          "destination": [
            "euler_qubit",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            3
          ],
          "destination": [
            "euler_basis",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            4
          ],
          "destination": [
            "euler_theta",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            5
          ],
          "destination": [
            "euler_phi",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            6
          ],
          "destination": [
            "euler_lambda",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            7
          ],
          "destination": [
            "euler_gamma",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            8
          ],
          "destination": [
            "euler_scalar",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            9
          ],
          "destination": [
            "euler_verified",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_unpack",
            10
          ],
          "destination": [
            "euler_error",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_theta_pi_receive",
            0
          ],
          "destination": [
            "euler_theta_pi",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_phi_pi_receive",
            0
          ],
          "destination": [
            "euler_phi_pi",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_lambda_pi_receive",
            0
          ],
          "destination": [
            "euler_lambda_pi",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_gamma_pi_receive",
            0
          ],
          "destination": [
            "euler_gamma_pi",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "euler_scalar_pi_receive",
            0
          ],
          "destination": [
            "euler_scalar_pi",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "density_dimension_receive",
            0
          ],
          "destination": [
            "population_size",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "population_size",
            0
          ],
          "destination": [
            "populations",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            0
          ],
          "destination": [
            "complex_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            1
          ],
          "destination": [
            "real_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            2
          ],
          "destination": [
            "imag_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            3
          ],
          "destination": [
            "magnitude_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            3
          ],
          "destination": [
            "matrix_view",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            4
          ],
          "destination": [
            "phase_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            5
          ],
          "destination": [
            "populations",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            6
          ],
          "destination": [
            "metrics_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            7
          ],
          "destination": [
            "bloch_display",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            8
          ],
          "destination": [
            "freq_apply",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_apply",
            0
          ],
          "destination": [
            "frequency_signal",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "frequency_signal",
            0
          ],
          "destination": [
            "frequency_smooth",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "frequency_smooth",
            0
          ],
          "destination": [
            "oscillators",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            9
          ],
          "destination": [
            "amp_apply",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amp_apply",
            0
          ],
          "destination": [
            "amplitude_signal",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amplitude_signal",
            0
          ],
          "destination": [
            "amplitude_smooth",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "oscillators",
            0
          ],
          "destination": [
            "voice_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "amplitude_smooth",
            0
          ],
          "destination": [
            "voice_gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "voice_gain",
            0
          ],
          "destination": [
            "mixdown",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mixdown",
            0
          ],
          "destination": [
            "unpack_audio",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack_audio",
            0
          ],
          "destination": [
            "left_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack_audio",
            1
          ],
          "destination": [
            "right_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "left_gain",
            0
          ],
          "destination": [
            "dac",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "right_gain",
            0
          ],
          "destination": [
            "dac",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            10
          ],
          "destination": [
            "revision",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "engine",
            11
          ],
          "destination": [
            "status",
            1
          ]
        }
      }
    ],
    "dependency_cache": [
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_zx_density_matrix_engine_v1.js",
        "type": "TEXT"
      }
    ],
    "autosave": 0
  }
}
