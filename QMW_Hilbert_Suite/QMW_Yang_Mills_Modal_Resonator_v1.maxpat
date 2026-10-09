{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 8,
      "minor": 6,
      "revision": 0,
      "architecture": "x64",
      "modernui": 1
    },
    "rect": [
      80,
      80,
      1100,
      850
    ],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            20,
            15,
            620,
            22
          ],
          "text": "QMW \u2014 Classical SU(2) Yang\u2013Mills / Modal Resonator v1"
        }
      },
      {
        "box": {
          "id": "note",
          "maxclass": "comment",
          "patching_rect": [
            20,
            45,
            780,
            22
          ],
          "text": "Fixed harmonics; energy drives magnitude and motion. No quantum density is fabricated."
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            85,
            220,
            22
          ],
          "text": "udpreceive 7416"
        }
      },
      {
        "box": {
          "id": "root",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            120,
            220,
            22
          ],
          "text": "OSC-route /qmw"
        }
      },
      {
        "box": {
          "id": "ym",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            155,
            220,
            22
          ],
          "text": "OSC-route /yang_mills"
        }
      },
      {
        "box": {
          "id": "version",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            190,
            220,
            22
          ],
          "text": "OSC-route /v1"
        }
      },
      {
        "box": {
          "id": "route",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            225,
            560,
            22
          ],
          "text": "OSC-route /begin /magnitude /speed /diagnostics /end"
        }
      },
      {
        "box": {
          "id": "begin",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            270,
            135,
            22
          ],
          "text": "prepend begin"
        }
      },
      {
        "box": {
          "id": "magnitude",
          "maxclass": "newobj",
          "patching_rect": [
            160,
            270,
            135,
            22
          ],
          "text": "prepend magnitude"
        }
      },
      {
        "box": {
          "id": "speed",
          "maxclass": "newobj",
          "patching_rect": [
            300,
            270,
            135,
            22
          ],
          "text": "prepend speed"
        }
      },
      {
        "box": {
          "id": "diagnostics",
          "maxclass": "newobj",
          "patching_rect": [
            440,
            270,
            135,
            22
          ],
          "text": "prepend diagnostics"
        }
      },
      {
        "box": {
          "id": "end",
          "maxclass": "newobj",
          "patching_rect": [
            580,
            270,
            135,
            22
          ],
          "text": "prepend end"
        }
      },
      {
        "box": {
          "id": "adapter",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            325,
            290,
            22
          ],
          "text": "js qmw_yang_mills_modal_v1.js"
        }
      },
      {
        "box": {
          "id": "receiver_gain",
          "maxclass": "flonum",
          "patching_rect": [
            650,
            325,
            80,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0
        }
      },
      {
        "box": {
          "id": "gainlabel",
          "maxclass": "comment",
          "patching_rect": [
            630,
            300,
            250,
            22
          ],
          "text": "Field coupling 0..1 (receiver)"
        }
      },
      {
        "box": {
          "id": "gainmsg",
          "maxclass": "newobj",
          "patching_rect": [
            650,
            360,
            220,
            22
          ],
          "text": "prepend coupling"
        }
      },
      {
        "box": {
          "id": "reset",
          "maxclass": "message",
          "patching_rect": [
            330,
            325,
            60,
            22
          ],
          "text": "reset"
        }
      },
      {
        "box": {
          "id": "resetnote",
          "maxclass": "comment",
          "patching_rect": [
            320,
            355,
            290,
            22
          ],
          "text": "Reset receiver before restarting sender"
        }
      },
      {
        "box": {
          "id": "load",
          "maxclass": "newobj",
          "patching_rect": [
            870,
            85,
            90,
            22
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "on",
          "maxclass": "message",
          "patching_rect": [
            870,
            120,
            40,
            22
          ],
          "text": "1"
        }
      },
      {
        "box": {
          "id": "watchdog",
          "maxclass": "newobj",
          "patching_rect": [
            870,
            155,
            100,
            22
          ],
          "text": "qmetro 50"
        }
      },
      {
        "box": {
          "id": "init",
          "maxclass": "message",
          "patching_rect": [
            870,
            190,
            150,
            22
          ],
          "text": "reset, coupling 1"
        }
      },
      {
        "box": {
          "id": "gaininit",
          "maxclass": "message",
          "patching_rect": [
            870,
            225,
            50,
            22
          ],
          "text": "1."
        }
      },
      {
        "box": {
          "id": "lanes",
          "maxclass": "multislider",
          "patching_rect": [
            20,
            375,
            300,
            40
          ],
          "size": 16,
          "setminmax": [
            0.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "diagnostic",
          "maxclass": "newobj",
          "patching_rect": [
            340,
            400,
            360,
            22
          ],
          "text": "print YM_energy_drift_Gauss_unitarity_det"
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "newobj",
          "patching_rect": [
            340,
            435,
            220,
            22
          ],
          "text": "print YM_status"
        }
      },
      {
        "box": {
          "id": "base",
          "maxclass": "flonum",
          "patching_rect": [
            20,
            450,
            90,
            22
          ],
          "minimum": 20.0,
          "maximum": 1000.0
        }
      },
      {
        "box": {
          "id": "baselabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            425,
            150,
            22
          ],
          "text": "Fundamental Hz"
        }
      },
      {
        "box": {
          "id": "baseinit",
          "maxclass": "message",
          "patching_rect": [
            870,
            270,
            50,
            22
          ],
          "text": "55."
        }
      },
      {
        "box": {
          "id": "freq",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            485,
            100,
            22
          ],
          "text": "sig~ 55"
        }
      },
      {
        "box": {
          "id": "gen",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            525,
            750,
            22
          ],
          "text": "mc.gen~ @gen qmw_density_field_harmonic_modal_resonator16_mc_v4 @chans 16"
        }
      },
      {
        "box": {
          "id": "dspinit",
          "maxclass": "message",
          "patching_rect": [
            20,
            565,
            750,
            22
          ],
          "text": "reference_tone 0, excitation_floor 0, harmonic_lock 1, quantum_spectrum_morph 0"
        }
      },
      {
        "box": {
          "id": "mix",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            610,
            250,
            22
          ],
          "text": "mc.mixdown~ 2 @autogain 1"
        }
      },
      {
        "box": {
          "id": "unpack",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            645,
            160,
            22
          ],
          "text": "mc.unpack~ 2"
        }
      },
      {
        "box": {
          "id": "master",
          "maxclass": "flonum",
          "patching_rect": [
            480,
            620,
            90,
            22
          ],
          "minimum": 0.0,
          "maximum": 1.0
        }
      },
      {
        "box": {
          "id": "masterlabel",
          "maxclass": "comment",
          "patching_rect": [
            480,
            595,
            230,
            22
          ],
          "text": "Master (starts at 0)"
        }
      },
      {
        "box": {
          "id": "masterinit",
          "maxclass": "message",
          "patching_rect": [
            870,
            305,
            50,
            22
          ],
          "text": "0."
        }
      },
      {
        "box": {
          "id": "ramp",
          "maxclass": "newobj",
          "patching_rect": [
            480,
            655,
            110,
            22
          ],
          "text": "pack 0. 50"
        }
      },
      {
        "box": {
          "id": "line",
          "maxclass": "newobj",
          "patching_rect": [
            480,
            690,
            90,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "level0",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            690,
            90,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "clip0",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            725,
            140,
            22
          ],
          "text": "clip~ -0.95 0.95"
        }
      },
      {
        "box": {
          "id": "level1",
          "maxclass": "newobj",
          "patching_rect": [
            170,
            690,
            90,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "clip1",
          "maxclass": "newobj",
          "patching_rect": [
            170,
            725,
            140,
            22
          ],
          "text": "clip~ -0.95 0.95"
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "ezdac~",
          "patching_rect": [
            20,
            765,
            52,
            52
          ],
          "numinlets": 2,
          "numoutlets": 0
        }
      },
      {
        "box": {
          "id": "mute",
          "maxclass": "message",
          "patching_rect": [
            650,
            620,
            60,
            22
          ],
          "text": "0."
        }
      },
      {
        "box": {
          "id": "mutelabel",
          "maxclass": "comment",
          "patching_rect": [
            650,
            595,
            80,
            22
          ],
          "text": "MUTE"
        }
      },
      {
        "box": {
          "id": "listen",
          "maxclass": "comment",
          "patching_rect": [
            170,
            765,
            650,
            22
          ],
          "text": "Enable DSP, then raise Master slowly. CNMAT OSC-route is required."
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "route",
            0
          ],
          "destination": [
            "begin",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "begin",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            1
          ],
          "destination": [
            "magnitude",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "magnitude",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            2
          ],
          "destination": [
            "speed",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "speed",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            3
          ],
          "destination": [
            "diagnostics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "diagnostics",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "route",
            4
          ],
          "destination": [
            "end",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "end",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "receiver_gain",
            0
          ],
          "destination": [
            "gainmsg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gainmsg",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "reset",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "on",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "on",
            0
          ],
          "destination": [
            "watchdog",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "watchdog",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "init",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "init",
            0
          ],
          "destination": [
            "adapter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "gaininit",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gaininit",
            0
          ],
          "destination": [
            "receiver_gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            1
          ],
          "destination": [
            "lanes",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            2
          ],
          "destination": [
            "diagnostic",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            3
          ],
          "destination": [
            "status",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "baseinit",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "baseinit",
            0
          ],
          "destination": [
            "base",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "base",
            0
          ],
          "destination": [
            "freq",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adapter",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "dspinit",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "dspinit",
            0
          ],
          "destination": [
            "gen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gen",
            0
          ],
          "destination": [
            "mix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "mix",
            0
          ],
          "destination": [
            "unpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "load",
            0
          ],
          "destination": [
            "masterinit",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "masterinit",
            0
          ],
          "destination": [
            "master",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "master",
            0
          ],
          "destination": [
            "ramp",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ramp",
            0
          ],
          "destination": [
            "line",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "unpack",
            0
          ],
          "destination": [
            "level0",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "line",
            0
          ],
          "destination": [
            "level0",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "level0",
            0
          ],
          "destination": [
            "clip0",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clip0",
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
            "unpack",
            1
          ],
          "destination": [
            "level1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "line",
            0
          ],
          "destination": [
            "level1",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "level1",
            0
          ],
          "destination": [
            "clip1",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "clip1",
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
            "mute",
            0
          ],
          "destination": [
            "master",
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
            "ym",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "ym",
            0
          ],
          "destination": [
            "version",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "version",
            0
          ],
          "destination": [
            "route",
            0
          ]
        }
      }
    ]
  }
}
