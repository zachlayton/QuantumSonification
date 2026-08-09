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
      70,
      35,
      1280,
      1330
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            25,
            15,
            900,
            25
          ],
          "text": "QMW Native Quantum Instruments v1 \u2014 spinor, EPR, exchange",
          "fontsize": 16
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25,
            44,
            950,
            32
          ],
          "text": "State input 7482; source control output 7483. Python remains the physics engine while Max selects and resets its source."
        }
      },
      {
        "box": {
          "id": "source_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            68,
            95,
            20
          ],
          "text": "excitation source"
        }
      },
      {
        "box": {
          "id": "source_menu",
          "maxclass": "umenu",
          "patching_rect": [
            125,
            66,
            260,
            22
          ],
          "items": [
            "all_native",
            ",",
            "spin_1_2_precession",
            ",",
            "quantum_entanglement_epr",
            ",",
            "identical_particles_boson",
            ",",
            "identical_particles_fermion",
            ",",
            "morse_potential",
            ",",
            "aharonov_bohm_effect",
            ",",
            "landau_levels",
            ",",
            "hydrogen_zeeman",
            ",",
            "hydrogen_stark",
            ",",
            "helium_variational_two_electron",
            ",",
            "delta_function_shell",
            ",",
            "dirac_hydrogen_fine_structure",
            ",",
            "dirac_step_klein"
          ],
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
          "id": "control_format",
          "maxclass": "newobj",
          "patching_rect": [
            395,
            66,
            275,
            22
          ],
          "text": "o.pack /qmw/instrument/control/select",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "FullPacket"
          ]
        }
      },
      {
        "box": {
          "id": "control_send",
          "maxclass": "newobj",
          "patching_rect": [
            680,
            66,
            175,
            22
          ],
          "text": "udpsend 127.0.0.1 7483",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "selected_label",
          "maxclass": "comment",
          "patching_rect": [
            865,
            68,
            65,
            20
          ],
          "text": "selected:"
        }
      },
      {
        "box": {
          "id": "selected",
          "maxclass": "message",
          "patching_rect": [
            925,
            66,
            190,
            22
          ],
          "text": "waiting",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            90,
            115,
            22
          ],
          "text": "udpreceive 7482",
          "numinlets": 0,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "activity",
          "maxclass": "button",
          "patching_rect": [
            155,
            89,
            24,
            24
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "activity_label",
          "maxclass": "comment",
          "patching_rect": [
            185,
            91,
            130,
            20
          ],
          "text": "OSC packet activity"
        }
      },
      {
        "box": {
          "id": "root",
          "maxclass": "newobj",
          "patching_rect": [
            325,
            90,
            190,
            22
          ],
          "text": "OSC-route /qmw/instrument",
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
          "id": "families",
          "maxclass": "newobj",
          "patching_rect": [
            530,
            90,
            485,
            22
          ],
          "text": "OSC-route /spin /epr /exchange /field /relativistic /dirac /control",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
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
          "id": "control_route",
          "maxclass": "newobj",
          "patching_rect": [
            825,
            90,
            135,
            22
          ],
          "text": "OSC-route /selected",
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
          "id": "selected_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            970,
            90,
            90,
            22
          ],
          "text": "prepend set",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "unmatched",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            90,
            190,
            22
          ],
          "text": "print qmw_native_unmatched",
          "numinlets": 1,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "spin_header",
          "maxclass": "comment",
          "patching_rect": [
            25,
            145,
            300,
            22
          ],
          "text": "SPIN-1/2 PRECESSION",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "spin_route",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            175,
            240,
            22
          ],
          "text": "OSC-route /frame /state_real /state_imag",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spin_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            210,
            45,
            22
          ],
          "text": "t l b",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "list",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "spin_flash",
          "maxclass": "button",
          "patching_rect": [
            78,
            209,
            24,
            24
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "spin_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            248,
            420,
            22
          ],
          "text": "unpack i f f f f f f f f f f f f f f f f",
          "numinlets": 1,
          "numoutlets": 17,
          "outlettype": [
            "int",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
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
          "id": "spin_omega_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            282,
            160,
            20
          ],
          "text": "Larmor angular frequency"
        }
      },
      {
        "box": {
          "id": "spin_omega",
          "maxclass": "flonum",
          "patching_rect": [
            190,
            280,
            85,
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
          "id": "spin_bloch_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            318,
            110,
            20
          ],
          "text": "Bloch vector"
        }
      },
      {
        "box": {
          "id": "spin_bloch_pack",
          "maxclass": "newobj",
          "patching_rect": [
            140,
            316,
            82,
            22
          ],
          "text": "pak f f f",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spin_bloch",
          "maxclass": "multislider",
          "patching_rect": [
            235,
            306,
            260,
            48
          ],
          "size": 3,
          "setminmax": [
            -1.0,
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
          "id": "spin_prob_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            370,
            110,
            20
          ],
          "text": "Z probabilities"
        }
      },
      {
        "box": {
          "id": "spin_prob_pack",
          "maxclass": "newobj",
          "patching_rect": [
            140,
            368,
            60,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "spin_prob",
          "maxclass": "multislider",
          "patching_rect": [
            215,
            360,
            280,
            48
          ],
          "size": 2,
          "setminmax": [
            0.0,
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
          "id": "spin_energy_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            418,
            65,
            20
          ],
          "text": "energy"
        }
      },
      {
        "box": {
          "id": "spin_energy",
          "maxclass": "flonum",
          "patching_rect": [
            92,
            416,
            75,
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
          "id": "spin_phase_label",
          "maxclass": "comment",
          "patching_rect": [
            178,
            418,
            92,
            20
          ],
          "text": "relative phase"
        }
      },
      {
        "box": {
          "id": "spin_phase",
          "maxclass": "flonum",
          "patching_rect": [
            275,
            416,
            85,
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
          "id": "spin_real_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            447,
            78,
            20
          ],
          "text": "spinor Re"
        }
      },
      {
        "box": {
          "id": "spin_real",
          "maxclass": "multislider",
          "patching_rect": [
            105,
            442,
            170,
            34
          ],
          "size": 2,
          "setminmax": [
            -1.0,
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
          "id": "spin_imag_label",
          "maxclass": "comment",
          "patching_rect": [
            285,
            447,
            78,
            20
          ],
          "text": "spinor Im"
        }
      },
      {
        "box": {
          "id": "spin_imag",
          "maxclass": "multislider",
          "patching_rect": [
            365,
            442,
            130,
            34
          ],
          "size": 2,
          "setminmax": [
            -1.0,
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
          "id": "epr_header",
          "maxclass": "comment",
          "patching_rect": [
            540,
            145,
            300,
            22
          ],
          "text": "EPR / BELL PAIR",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "epr_route",
          "maxclass": "newobj",
          "patching_rect": [
            540,
            175,
            300,
            22
          ],
          "text": "OSC-route /frame /correlation_tensor /state_real /state_imag",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
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
          "id": "epr_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            540,
            210,
            45,
            22
          ],
          "text": "t l b",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "list",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "epr_flash",
          "maxclass": "button",
          "patching_rect": [
            593,
            209,
            24,
            24
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "epr_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            540,
            248,
            420,
            22
          ],
          "text": "unpack i f f f f f f f f f f f f f f f f",
          "numinlets": 1,
          "numoutlets": 17,
          "outlettype": [
            "int",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
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
          "id": "conc_label",
          "maxclass": "comment",
          "patching_rect": [
            540,
            282,
            85,
            20
          ],
          "text": "concurrence"
        }
      },
      {
        "box": {
          "id": "concurrence",
          "maxclass": "flonum",
          "patching_rect": [
            630,
            280,
            75,
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
          "id": "chsh_label",
          "maxclass": "comment",
          "patching_rect": [
            720,
            282,
            75,
            20
          ],
          "text": "CHSH max"
        }
      },
      {
        "box": {
          "id": "chsh",
          "maxclass": "flonum",
          "patching_rect": [
            800,
            280,
            75,
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
          "id": "epr_a_label",
          "maxclass": "comment",
          "patching_rect": [
            540,
            318,
            170,
            20
          ],
          "text": "A | B measured +X"
        }
      },
      {
        "box": {
          "id": "epr_a_pack",
          "maxclass": "newobj",
          "patching_rect": [
            640,
            316,
            82,
            22
          ],
          "text": "pak f f f",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "epr_a",
          "maxclass": "multislider",
          "patching_rect": [
            730,
            307,
            230,
            42
          ],
          "size": 3,
          "setminmax": [
            -1.0,
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
          "id": "epr_b_label",
          "maxclass": "comment",
          "patching_rect": [
            540,
            365,
            170,
            20
          ],
          "text": "B | A measured +X"
        }
      },
      {
        "box": {
          "id": "epr_b_pack",
          "maxclass": "newobj",
          "patching_rect": [
            640,
            363,
            82,
            22
          ],
          "text": "pak f f f",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "epr_b",
          "maxclass": "multislider",
          "patching_rect": [
            730,
            354,
            230,
            42
          ],
          "size": 3,
          "setminmax": [
            -1.0,
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
          "id": "epr_corr_label",
          "maxclass": "comment",
          "patching_rect": [
            540,
            402,
            125,
            20
          ],
          "text": "correlation tensor"
        }
      },
      {
        "box": {
          "id": "epr_corr",
          "maxclass": "multislider",
          "patching_rect": [
            670,
            398,
            290,
            42
          ],
          "size": 9,
          "setminmax": [
            -1.0,
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
          "id": "epr_real_label",
          "maxclass": "comment",
          "patching_rect": [
            540,
            452,
            68,
            20
          ],
          "text": "state Re"
        }
      },
      {
        "box": {
          "id": "epr_real",
          "maxclass": "multislider",
          "patching_rect": [
            610,
            446,
            155,
            36
          ],
          "size": 4,
          "setminmax": [
            -1.0,
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
          "id": "epr_imag_label",
          "maxclass": "comment",
          "patching_rect": [
            775,
            452,
            68,
            20
          ],
          "text": "state Im"
        }
      },
      {
        "box": {
          "id": "epr_imag",
          "maxclass": "multislider",
          "patching_rect": [
            845,
            446,
            115,
            36
          ],
          "size": 4,
          "setminmax": [
            -1.0,
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
          "id": "exchange_header",
          "maxclass": "comment",
          "patching_rect": [
            25,
            505,
            390,
            22
          ],
          "text": "IDENTICAL PARTICLES \u2014 BOSON / FERMION",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "exchange_route",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            535,
            355,
            22
          ],
          "text": "OSC-route /frame /marginal_a /marginal_b /pair /end",
          "numinlets": 1,
          "numoutlets": 6,
          "outlettype": [
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
          "id": "exchange_trigger",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            570,
            45,
            22
          ],
          "text": "t l b",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "list",
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "exchange_flash",
          "maxclass": "button",
          "patching_rect": [
            78,
            569,
            24,
            24
          ],
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ]
        }
      },
      {
        "box": {
          "id": "exchange_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            608,
            250,
            22
          ],
          "text": "unpack i f f i f f f i",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
            "int",
            "float",
            "float",
            "int",
            "float",
            "float",
            "float",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "symmetry_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            642,
            100,
            20
          ],
          "text": "symmetry \u00b11"
        }
      },
      {
        "box": {
          "id": "symmetry",
          "maxclass": "number",
          "patching_rect": [
            130,
            640,
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
          "id": "swap_label",
          "maxclass": "comment",
          "patching_rect": [
            205,
            642,
            90,
            20
          ],
          "text": "swap <P12>"
        }
      },
      {
        "box": {
          "id": "swap",
          "maxclass": "flonum",
          "patching_rect": [
            300,
            640,
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
          "id": "coinc_label",
          "maxclass": "comment",
          "patching_rect": [
            385,
            642,
            92,
            20
          ],
          "text": "coincidence"
        }
      },
      {
        "box": {
          "id": "coincidence",
          "maxclass": "flonum",
          "patching_rect": [
            480,
            640,
            85,
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
          "id": "purity_label",
          "maxclass": "comment",
          "patching_rect": [
            580,
            642,
            105,
            20
          ],
          "text": "one-body purity"
        }
      },
      {
        "box": {
          "id": "purity",
          "maxclass": "flonum",
          "patching_rect": [
            690,
            640,
            85,
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
          "id": "pair_status",
          "maxclass": "message",
          "patching_rect": [
            25,
            680,
            620,
            22
          ],
          "text": "waiting for joint-coordinate pair samples...",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pair_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            395,
            535,
            105,
            22
          ],
          "text": "prepend set",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "note",
          "maxclass": "comment",
          "patching_rect": [
            25,
            730,
            930,
            44
          ],
          "text": "Default +X spin in a Z field: Bloch X/Y and relative phase move; Z probabilities remain exactly 0.5. Use --magnetic-field 0 1 0 to rotate population through Z."
        }
      },
      {
        "box": {
          "id": "field_header",
          "maxclass": "comment",
          "patching_rect": [
            25,
            785,
            500,
            22
          ],
          "text": "CONTINUOUS EXTERNAL-FIELD WAVEFUNCTION",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "field_route",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            815,
            190,
            22
          ],
          "text": "OSC-route /name /frame",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_name_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            225,
            815,
            90,
            22
          ],
          "text": "prepend set",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_name",
          "maxclass": "message",
          "patching_rect": [
            325,
            815,
            300,
            22
          ],
          "text": "inactive \u2014 select a spatial field source",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            850,
            535,
            22
          ],
          "text": "unpack i f f i f f f f f f f f f f f f f f f",
          "numinlets": 1,
          "numoutlets": 19,
          "outlettype": [
            "int",
            "float",
            "float",
            "int",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
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
          "id": "field_desc_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            883,
            160,
            20
          ],
          "text": "E phase P structure C J"
        }
      },
      {
        "box": {
          "id": "field_desc_pack",
          "maxclass": "newobj",
          "patching_rect": [
            190,
            881,
            145,
            22
          ],
          "text": "pak f f f f f f",
          "numinlets": 6,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_desc",
          "maxclass": "multislider",
          "patching_rect": [
            345,
            875,
            285,
            42
          ],
          "size": 6,
          "setminmax": [
            0.0,
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
          "id": "field_pos_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            930,
            75,
            20
          ],
          "text": "position"
        }
      },
      {
        "box": {
          "id": "field_pos_pack",
          "maxclass": "newobj",
          "patching_rect": [
            105,
            928,
            82,
            22
          ],
          "text": "pak f f f",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_pos",
          "maxclass": "multislider",
          "patching_rect": [
            195,
            921,
            190,
            42
          ],
          "size": 3,
          "setminmax": [
            -10.0,
            10.0
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
          "id": "field_spread_label",
          "maxclass": "comment",
          "patching_rect": [
            405,
            930,
            65,
            20
          ],
          "text": "spread"
        }
      },
      {
        "box": {
          "id": "field_spread_pack",
          "maxclass": "newobj",
          "patching_rect": [
            475,
            928,
            82,
            22
          ],
          "text": "pak f f f",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_spread",
          "maxclass": "multislider",
          "patching_rect": [
            565,
            921,
            190,
            42
          ],
          "size": 3,
          "setminmax": [
            0.0,
            10.0
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
          "id": "field_obs_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            977,
            340,
            20
          ],
          "text": "field/Zeff/radius, frequency/repulsion/g, scale/E/bound count"
        }
      },
      {
        "box": {
          "id": "field_obs_pack",
          "maxclass": "newobj",
          "patching_rect": [
            290,
            975,
            82,
            22
          ],
          "text": "pak f f f",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "field_obs",
          "maxclass": "multislider",
          "patching_rect": [
            380,
            968,
            375,
            42
          ],
          "size": 3,
          "setminmax": [
            -2.0,
            2.0
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
          "id": "field_note",
          "maxclass": "comment",
          "patching_rect": [
            775,
            880,
            430,
            70
          ],
          "text": "Spatial cloud/grains are also sent to the established cloud patch on UDP 7480. These grains sample continuous unitary evolution; they are renderer events, not physical collapses."
        }
      },
      {
        "box": {
          "id": "rel_header",
          "maxclass": "comment",
          "patching_rect": [
            25,
            1025,
            500,
            22
          ],
          "text": "DIRAC HYDROGEN FINE STRUCTURE \u2014 LEVEL AMPLITUDES",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "rel_route",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            1055,
            325,
            22
          ],
          "text": "OSC-route /frame /level /state_real /state_imag",
          "numinlets": 1,
          "numoutlets": 5,
          "outlettype": [
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
          "id": "rel_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            1088,
            245,
            22
          ],
          "text": "unpack i f f f f f f i",
          "numinlets": 1,
          "numoutlets": 8,
          "outlettype": [
            "int",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "rel_energy_label",
          "maxclass": "comment",
          "patching_rect": [
            285,
            1090,
            85,
            20
          ],
          "text": "binding <E>"
        }
      },
      {
        "box": {
          "id": "rel_energy",
          "maxclass": "flonum",
          "patching_rect": [
            375,
            1088,
            95,
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
          "id": "rel_split_label",
          "maxclass": "comment",
          "patching_rect": [
            485,
            1090,
            105,
            20
          ],
          "text": "fine splitting"
        }
      },
      {
        "box": {
          "id": "rel_split",
          "maxclass": "flonum",
          "patching_rect": [
            595,
            1088,
            110,
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
          "id": "rel_scale_label",
          "maxclass": "comment",
          "patching_rect": [
            720,
            1090,
            80,
            20
          ],
          "text": "time scale"
        }
      },
      {
        "box": {
          "id": "rel_scale",
          "maxclass": "flonum",
          "patching_rect": [
            805,
            1088,
            100,
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
          "id": "rel_level_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            365,
            1055,
            90,
            22
          ],
          "text": "prepend set",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rel_level",
          "maxclass": "message",
          "patching_rect": [
            465,
            1055,
            580,
            22
          ],
          "text": "inactive \u2014 select dirac_hydrogen_fine_structure",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "rel_real_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            1124,
            60,
            20
          ],
          "text": "state Re"
        }
      },
      {
        "box": {
          "id": "rel_real",
          "maxclass": "multislider",
          "patching_rect": [
            90,
            1118,
            210,
            38
          ],
          "size": 2,
          "setminmax": [
            -1.0,
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
          "id": "rel_imag_label",
          "maxclass": "comment",
          "patching_rect": [
            315,
            1124,
            60,
            20
          ],
          "text": "state Im"
        }
      },
      {
        "box": {
          "id": "rel_imag",
          "maxclass": "multislider",
          "patching_rect": [
            380,
            1118,
            210,
            38
          ],
          "size": 2,
          "setminmax": [
            -1.0,
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
          "id": "dirac_header",
          "maxclass": "comment",
          "patching_rect": [
            25,
            1175,
            500,
            22
          ],
          "text": "DIRAC STEP / KLEIN SCATTERING \u2014 TWO-COMPONENT FIELD",
          "fontsize": 14
        }
      },
      {
        "box": {
          "id": "dirac_route",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            1205,
            205,
            22
          ],
          "text": "OSC-route /frame /sample /end",
          "numinlets": 1,
          "numoutlets": 4,
          "outlettype": [
            "",
            "",
            "",
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dirac_unpack",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            1238,
            285,
            22
          ],
          "text": "unpack i f f f f f f f i",
          "numinlets": 1,
          "numoutlets": 9,
          "outlettype": [
            "int",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "int"
          ]
        }
      },
      {
        "box": {
          "id": "dirac_lr_label",
          "maxclass": "comment",
          "patching_rect": [
            325,
            1240,
            115,
            20
          ],
          "text": "left / right mass"
        }
      },
      {
        "box": {
          "id": "dirac_lr_pack",
          "maxclass": "newobj",
          "patching_rect": [
            445,
            1238,
            60,
            22
          ],
          "text": "pak f f",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dirac_lr",
          "maxclass": "multislider",
          "patching_rect": [
            515,
            1232,
            220,
            38
          ],
          "size": 2,
          "setminmax": [
            0.0,
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
          "id": "dirac_param_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            1278,
            190,
            20
          ],
          "text": "energy, step, incoming E, zone"
        }
      },
      {
        "box": {
          "id": "dirac_param_pack",
          "maxclass": "newobj",
          "patching_rect": [
            220,
            1276,
            105,
            22
          ],
          "text": "pak f f f i",
          "numinlets": 4,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dirac_param",
          "maxclass": "message",
          "patching_rect": [
            335,
            1276,
            400,
            22
          ],
          "text": "inactive \u2014 select dirac_step_klein",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dirac_sample_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            245,
            1205,
            90,
            22
          ],
          "text": "prepend set",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "dirac_sample",
          "maxclass": "message",
          "patching_rect": [
            345,
            1205,
            690,
            22
          ],
          "text": "inactive \u2014 select dirac_step_klein",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "source_menu",
            1
          ],
          "destination": [
            "control_format",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_format",
            0
          ],
          "destination": [
            "control_send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "udp",
            0
          ],
          "destination": [
            "activity",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "udp",
            0
          ],
          "destination": [
            "root",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "root",
            0
          ],
          "destination": [
            "families",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "root",
            1
          ],
          "destination": [
            "unmatched",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            0
          ],
          "destination": [
            "spin_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            1
          ],
          "destination": [
            "epr_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            2
          ],
          "destination": [
            "exchange_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            3
          ],
          "destination": [
            "field_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            4
          ],
          "destination": [
            "rel_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            5
          ],
          "destination": [
            "dirac_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            6
          ],
          "destination": [
            "control_route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "families",
            7
          ],
          "destination": [
            "unmatched",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_route",
            0
          ],
          "destination": [
            "selected_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "selected_prepend",
            0
          ],
          "destination": [
            "selected",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "control_route",
            1
          ],
          "destination": [
            "unmatched",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_route",
            0
          ],
          "destination": [
            "spin_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_trigger",
            0
          ],
          "destination": [
            "spin_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_trigger",
            1
          ],
          "destination": [
            "spin_flash",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            3
          ],
          "destination": [
            "spin_omega",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            12
          ],
          "destination": [
            "spin_bloch_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            13
          ],
          "destination": [
            "spin_bloch_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            14
          ],
          "destination": [
            "spin_bloch_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_bloch_pack",
            0
          ],
          "destination": [
            "spin_bloch",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            15
          ],
          "destination": [
            "spin_prob_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            16
          ],
          "destination": [
            "spin_prob_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_prob_pack",
            0
          ],
          "destination": [
            "spin_prob",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            4
          ],
          "destination": [
            "spin_energy",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_unpack",
            5
          ],
          "destination": [
            "spin_phase",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_route",
            1
          ],
          "destination": [
            "spin_real",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spin_route",
            2
          ],
          "destination": [
            "spin_imag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_route",
            0
          ],
          "destination": [
            "epr_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_trigger",
            0
          ],
          "destination": [
            "epr_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_trigger",
            1
          ],
          "destination": [
            "epr_flash",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            3
          ],
          "destination": [
            "concurrence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            4
          ],
          "destination": [
            "chsh",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            11
          ],
          "destination": [
            "epr_a_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            12
          ],
          "destination": [
            "epr_a_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            13
          ],
          "destination": [
            "epr_a_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_a_pack",
            0
          ],
          "destination": [
            "epr_a",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            14
          ],
          "destination": [
            "epr_b_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            15
          ],
          "destination": [
            "epr_b_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_unpack",
            16
          ],
          "destination": [
            "epr_b_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_b_pack",
            0
          ],
          "destination": [
            "epr_b",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_route",
            1
          ],
          "destination": [
            "epr_corr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_route",
            2
          ],
          "destination": [
            "epr_real",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "epr_route",
            3
          ],
          "destination": [
            "epr_imag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_route",
            0
          ],
          "destination": [
            "exchange_trigger",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_trigger",
            0
          ],
          "destination": [
            "exchange_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_trigger",
            1
          ],
          "destination": [
            "exchange_flash",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_unpack",
            3
          ],
          "destination": [
            "symmetry",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_unpack",
            4
          ],
          "destination": [
            "swap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_unpack",
            5
          ],
          "destination": [
            "coincidence",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_unpack",
            6
          ],
          "destination": [
            "purity",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "exchange_route",
            3
          ],
          "destination": [
            "pair_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pair_prepend",
            0
          ],
          "destination": [
            "pair_status",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_route",
            0
          ],
          "destination": [
            "field_name_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_name_prepend",
            0
          ],
          "destination": [
            "field_name",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_route",
            1
          ],
          "destination": [
            "field_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_route",
            2
          ],
          "destination": [
            "unmatched",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            4
          ],
          "destination": [
            "field_desc_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            5
          ],
          "destination": [
            "field_desc_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            6
          ],
          "destination": [
            "field_desc_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            7
          ],
          "destination": [
            "field_desc_pack",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            8
          ],
          "destination": [
            "field_desc_pack",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            9
          ],
          "destination": [
            "field_desc_pack",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_desc_pack",
            0
          ],
          "destination": [
            "field_desc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            10
          ],
          "destination": [
            "field_pos_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            11
          ],
          "destination": [
            "field_pos_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            12
          ],
          "destination": [
            "field_pos_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_pos_pack",
            0
          ],
          "destination": [
            "field_pos",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            13
          ],
          "destination": [
            "field_spread_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            14
          ],
          "destination": [
            "field_spread_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            15
          ],
          "destination": [
            "field_spread_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_spread_pack",
            0
          ],
          "destination": [
            "field_spread",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            16
          ],
          "destination": [
            "field_obs_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            17
          ],
          "destination": [
            "field_obs_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_unpack",
            18
          ],
          "destination": [
            "field_obs_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "field_obs_pack",
            0
          ],
          "destination": [
            "field_obs",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_route",
            0
          ],
          "destination": [
            "rel_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_route",
            1
          ],
          "destination": [
            "rel_level_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_level_prepend",
            0
          ],
          "destination": [
            "rel_level",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_route",
            2
          ],
          "destination": [
            "rel_real",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_route",
            3
          ],
          "destination": [
            "rel_imag",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_route",
            4
          ],
          "destination": [
            "unmatched",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_unpack",
            3
          ],
          "destination": [
            "rel_energy",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_unpack",
            4
          ],
          "destination": [
            "rel_split",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rel_unpack",
            6
          ],
          "destination": [
            "rel_scale",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_route",
            0
          ],
          "destination": [
            "dirac_unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_route",
            1
          ],
          "destination": [
            "dirac_sample_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_sample_prepend",
            0
          ],
          "destination": [
            "dirac_sample",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_route",
            3
          ],
          "destination": [
            "unmatched",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_unpack",
            4
          ],
          "destination": [
            "dirac_lr_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_unpack",
            5
          ],
          "destination": [
            "dirac_lr_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_lr_pack",
            0
          ],
          "destination": [
            "dirac_lr",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_unpack",
            3
          ],
          "destination": [
            "dirac_param_pack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_unpack",
            6
          ],
          "destination": [
            "dirac_param_pack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_unpack",
            7
          ],
          "destination": [
            "dirac_param_pack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_unpack",
            8
          ],
          "destination": [
            "dirac_param_pack",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dirac_param_pack",
            0
          ],
          "destination": [
            "dirac_param",
            0
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
        "name": "o.pack.mxo",
        "type": "iLaX"
      }
    ],
    "autosave": 0
  }
}
