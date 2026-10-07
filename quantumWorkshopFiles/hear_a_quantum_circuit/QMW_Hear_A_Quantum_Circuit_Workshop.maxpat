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
    "rect": [70.0, 70.0, 1260.0, 790.0],
    "openinpresentation": 1,
    "gridsize": [15.0, 15.0],
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "fontsize": 24.0,
          "text": "HEAR A QUANTUM CIRCUIT · WORKSHOP CONSOLE",
          "patching_rect": [24.0, 18.0, 860.0, 34.0],
          "presentation": 1,
          "presentation_rect": [24.0, 18.0, 860.0, 34.0],
          "textcolor": [0.90, 0.93, 0.97, 1.0]
        }
      },
      {
        "box": {
          "id": "startup",
          "maxclass": "comment",
          "fontsize": 13.0,
          "text": "LIVE: start workshop_max_launcher.py · FALLBACK: run the command shown below",
          "patching_rect": [24.0, 55.0, 850.0, 23.0],
          "presentation": 1,
          "presentation_rect": [24.0, 55.0, 850.0, 23.0],
          "textcolor": [0.51, 0.81, 1.0, 1.0]
        }
      },
      {
        "box": {
          "id": "ui",
          "filename": "qmw_qac_circuit_programmer_workshop_v1.js",
          "jsarguments": ["qmw_qac_circuit_programmer_workshop_v1.js"],
          "maxclass": "jsui",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": ["", "", ""],
          "parameter_enable": 0,
          "patching_rect": [24.0, 88.0, 890.0, 420.0],
          "presentation": 1,
          "presentation_rect": [24.0, 88.0, 890.0, 420.0]
        }
      },
      {
        "box": {
          "id": "module_heading",
          "maxclass": "comment",
          "fontsize": 18.0,
          "text": "FIVE SMALL MODULES",
          "patching_rect": [940.0, 92.0, 280.0, 25.0],
          "presentation": 1,
          "presentation_rect": [940.0, 92.0, 280.0, 25.0],
          "textcolor": [0.95, 0.76, 0.11, 1.0]
        }
      },
      {
        "box": {
          "id": "module_hint",
          "maxclass": "comment",
          "fontsize": 12.0,
          "linecount": 2,
          "text": "Predict first. Click a number to hear it live.\nThe same click also shows a dependable command.",
          "patching_rect": [940.0, 122.0, 290.0, 38.0],
          "presentation": 1,
          "presentation_rect": [940.0, 122.0, 290.0, 38.0],
          "textcolor": [0.70, 0.74, 0.80, 1.0]
        }
      },
      {
        "box": {
          "id": "m1",
          "maxclass": "message",
          "text": "1",
          "patching_rect": [940.0, 177.0, 38.0, 24.0],
          "presentation": 1,
          "presentation_rect": [940.0, 177.0, 38.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m1_label",
          "maxclass": "comment",
          "fontsize": 14.0,
          "text": "1  SUPERPOSITION · hear H",
          "patching_rect": [988.0, 177.0, 240.0, 24.0],
          "presentation": 1,
          "presentation_rect": [988.0, 177.0, 240.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m2",
          "maxclass": "message",
          "text": "2",
          "patching_rect": [940.0, 221.0, 38.0, 24.0],
          "presentation": 1,
          "presentation_rect": [940.0, 221.0, 38.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m2_label",
          "maxclass": "comment",
          "fontsize": 14.0,
          "linecount": 2,
          "text": "2  BLOCH SPHERE · move + hear\nProcessing can follow through optional OSC",
          "patching_rect": [988.0, 217.0, 250.0, 42.0],
          "presentation": 1,
          "presentation_rect": [988.0, 217.0, 250.0, 42.0]
        }
      },
      {
        "box": {
          "id": "m3",
          "maxclass": "message",
          "text": "3",
          "patching_rect": [940.0, 275.0, 38.0, 24.0],
          "presentation": 1,
          "presentation_rect": [940.0, 275.0, 38.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m3_label",
          "maxclass": "comment",
          "fontsize": 14.0,
          "text": "3  CIRCUIT DESIGN · use the JSUI",
          "patching_rect": [988.0, 275.0, 250.0, 24.0],
          "presentation": 1,
          "presentation_rect": [988.0, 275.0, 250.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m4",
          "maxclass": "message",
          "text": "4",
          "patching_rect": [940.0, 319.0, 38.0, 24.0],
          "presentation": 1,
          "presentation_rect": [940.0, 319.0, 38.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m4_label",
          "maxclass": "comment",
          "fontsize": 14.0,
          "text": "4  ENTANGLEMENT · compare CNOT",
          "patching_rect": [988.0, 319.0, 250.0, 24.0],
          "presentation": 1,
          "presentation_rect": [988.0, 319.0, 250.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m5",
          "maxclass": "message",
          "text": "5",
          "patching_rect": [940.0, 363.0, 38.0, 24.0],
          "presentation": 1,
          "presentation_rect": [940.0, 363.0, 38.0, 24.0]
        }
      },
      {
        "box": {
          "id": "m5_label",
          "maxclass": "comment",
          "fontsize": 14.0,
          "text": "5  ENTROPY · sample before hardware",
          "patching_rect": [988.0, 363.0, 250.0, 24.0],
          "presentation": 1,
          "presentation_rect": [988.0, 363.0, 250.0, 24.0]
        }
      },
      {
        "box": {
          "id": "fallback",
          "maxclass": "comment",
          "fontsize": 12.0,
          "linecount": 5,
          "text": "DEPENDABLE PATH\n1. Start the launcher for one-click sound.\n2. Or run the command shown below.\n3. Open outputs/*.wav if playback is blocked.\nThe JSUI state bars work without Python.",
          "patching_rect": [940.0, 418.0, 288.0, 92.0],
          "presentation": 1,
          "presentation_rect": [940.0, 418.0, 288.0, 92.0],
          "textcolor": [0.70, 0.74, 0.80, 1.0]
        }
      },
      {
        "box": {
          "id": "status_label",
          "maxclass": "comment",
          "fontsize": 13.0,
          "text": "FACILITATOR COMMAND",
          "patching_rect": [24.0, 530.0, 170.0, 22.0],
          "presentation": 1,
          "presentation_rect": [24.0, 530.0, 170.0, 22.0],
          "textcolor": [0.51, 0.81, 1.0, 1.0]
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "text": "Click module 1–5 to show its terminal command.",
          "patching_rect": [194.0, 526.0, 720.0, 24.0],
          "presentation": 1,
          "presentation_rect": [194.0, 526.0, 720.0, 24.0]
        }
      },
      {
        "box": {
          "id": "live_status_label",
          "maxclass": "comment",
          "fontsize": 13.0,
          "text": "LIVE STATUS",
          "patching_rect": [24.0, 566.0, 170.0, 22.0],
          "presentation": 1,
          "presentation_rect": [24.0, 566.0, 170.0, 22.0],
          "textcolor": [0.95, 0.76, 0.11, 1.0]
        }
      },
      {
        "box": {
          "id": "live_status",
          "maxclass": "message",
          "text": "Start: python workshop_max_launcher.py",
          "patching_rect": [194.0, 562.0, 720.0, 24.0],
          "presentation": 1,
          "presentation_rect": [194.0, 562.0, 720.0, 24.0]
        }
      },
      {
        "box": {
          "id": "select_module",
          "maxclass": "newobj",
          "text": "sel 1 2 3 4 5",
          "patching_rect": [55.0, 610.0, 112.0, 22.0]
        }
      },
      {
        "box": {
          "id": "cmd1",
          "maxclass": "message",
          "text": "python 01_superposition.py --h",
          "patching_rect": [185.0, 575.0, 210.0, 22.0]
        }
      },
      {
        "box": {
          "id": "cmd2",
          "maxclass": "message",
          "text": "python 02_bloch_sphere.py --axis ry --theta pi/2",
          "patching_rect": [185.0, 610.0, 315.0, 22.0]
        }
      },
      {
        "box": {
          "id": "cmd3",
          "maxclass": "message",
          "text": "python 03_circuit_design.py --gates h z h",
          "patching_rect": [185.0, 645.0, 285.0, 22.0]
        }
      },
      {
        "box": {
          "id": "cmd4",
          "maxclass": "message",
          "text": "python 04_entanglement.py --cnot",
          "patching_rect": [515.0, 575.0, 230.0, 22.0]
        }
      },
      {
        "box": {
          "id": "cmd5",
          "maxclass": "message",
          "text": "python 05_entropy_and_measurement.py --shots 32",
          "patching_rect": [515.0, 610.0, 320.0, 22.0]
        }
      },
      {
        "box": {
          "id": "set_status",
          "maxclass": "newobj",
          "text": "prepend set",
          "patching_rect": [515.0, 655.0, 82.0, 22.0]
        }
      },
      {
        "box": {
          "id": "qac_print",
          "maxclass": "newobj",
          "text": "print QAC_WORKSHOP_COMMANDS",
          "patching_rect": [24.0, 575.0, 200.0, 22.0]
        }
      },
      {
        "box": {
          "id": "circuit_route",
          "maxclass": "newobj",
          "text": "route circuit",
          "patching_rect": [850.0, 610.0, 86.0, 22.0]
        }
      },
      {
        "box": {
          "id": "sequence_print",
          "maxclass": "newobj",
          "text": "print WORKSHOP_SEQUENCE",
          "patching_rect": [850.0, 645.0, 180.0, 22.0]
        }
      },
      {
        "box": {
          "id": "pack_run",
          "maxclass": "newobj",
          "text": "o.pack /workshop/run",
          "patching_rect": [1050.0, 575.0, 145.0, 22.0]
        }
      },
      {
        "box": {
          "id": "pack_circuit",
          "maxclass": "newobj",
          "text": "o.pack /workshop/circuit",
          "patching_rect": [1050.0, 610.0, 165.0, 22.0]
        }
      },
      {
        "box": {
          "id": "udp_send",
          "maxclass": "newobj",
          "text": "udpsend 127.0.0.1 7498",
          "patching_rect": [1050.0, 645.0, 160.0, 22.0]
        }
      },
      {
        "box": {
          "id": "udp_receive",
          "maxclass": "newobj",
          "text": "udpreceive 7499",
          "patching_rect": [24.0, 700.0, 105.0, 22.0]
        }
      },
      {
        "box": {
          "id": "osc_route",
          "maxclass": "newobj",
          "text": "OSC-route /workshop/status /workshop/feedback",
          "patching_rect": [145.0, 700.0, 292.0, 22.0]
        }
      },
      {
        "box": {
          "id": "prepend_live_status",
          "maxclass": "newobj",
          "text": "prepend set",
          "patching_rect": [455.0, 685.0, 82.0, 22.0]
        }
      },
      {
        "box": {
          "id": "prepend_launcher_status",
          "maxclass": "newobj",
          "text": "prepend launcherstatus",
          "patching_rect": [455.0, 720.0, 145.0, 22.0]
        }
      },
      {
        "box": {
          "id": "prepend_feedback",
          "maxclass": "newobj",
          "text": "prepend feedback",
          "patching_rect": [620.0, 720.0, 120.0, 22.0]
        }
      }
    ],
    "lines": [
      {"patchline": {"source": ["m1", 0], "destination": ["select_module", 0]}},
      {"patchline": {"source": ["m2", 0], "destination": ["select_module", 0]}},
      {"patchline": {"source": ["m3", 0], "destination": ["select_module", 0]}},
      {"patchline": {"source": ["m4", 0], "destination": ["select_module", 0]}},
      {"patchline": {"source": ["m5", 0], "destination": ["select_module", 0]}},
      {"patchline": {"source": ["m1", 0], "destination": ["pack_run", 0]}},
      {"patchline": {"source": ["m2", 0], "destination": ["pack_run", 0]}},
      {"patchline": {"source": ["m3", 0], "destination": ["pack_run", 0]}},
      {"patchline": {"source": ["m4", 0], "destination": ["pack_run", 0]}},
      {"patchline": {"source": ["m5", 0], "destination": ["pack_run", 0]}},
      {"patchline": {"source": ["select_module", 0], "destination": ["cmd1", 0]}},
      {"patchline": {"source": ["select_module", 1], "destination": ["cmd2", 0]}},
      {"patchline": {"source": ["select_module", 2], "destination": ["cmd3", 0]}},
      {"patchline": {"source": ["select_module", 3], "destination": ["cmd4", 0]}},
      {"patchline": {"source": ["select_module", 4], "destination": ["cmd5", 0]}},
      {"patchline": {"source": ["cmd1", 0], "destination": ["set_status", 0]}},
      {"patchline": {"source": ["cmd2", 0], "destination": ["set_status", 0]}},
      {"patchline": {"source": ["cmd3", 0], "destination": ["set_status", 0]}},
      {"patchline": {"source": ["cmd4", 0], "destination": ["set_status", 0]}},
      {"patchline": {"source": ["cmd5", 0], "destination": ["set_status", 0]}},
      {"patchline": {"source": ["set_status", 0], "destination": ["status", 0]}},
      {"patchline": {"source": ["ui", 0], "destination": ["qac_print", 0]}},
      {"patchline": {"source": ["ui", 1], "destination": ["live_status", 0]}},
      {"patchline": {"source": ["ui", 2], "destination": ["circuit_route", 0]}},
      {"patchline": {"source": ["circuit_route", 0], "destination": ["sequence_print", 0]}},
      {"patchline": {"source": ["circuit_route", 0], "destination": ["pack_circuit", 0]}},
      {"patchline": {"source": ["pack_run", 0], "destination": ["udp_send", 0]}},
      {"patchline": {"source": ["pack_circuit", 0], "destination": ["udp_send", 0]}},
      {"patchline": {"source": ["udp_receive", 0], "destination": ["osc_route", 0]}},
      {"patchline": {"source": ["osc_route", 0], "destination": ["prepend_live_status", 0]}},
      {"patchline": {"source": ["prepend_live_status", 0], "destination": ["live_status", 0]}},
      {"patchline": {"source": ["osc_route", 0], "destination": ["prepend_launcher_status", 0]}},
      {"patchline": {"source": ["prepend_launcher_status", 0], "destination": ["ui", 0]}},
      {"patchline": {"source": ["osc_route", 1], "destination": ["prepend_feedback", 0]}},
      {"patchline": {"source": ["prepend_feedback", 0], "destination": ["ui", 0]}}
    ],
    "dependency_cache": [
      {
        "name": "qmw_qac_circuit_programmer_workshop_v1.js",
        "patcherrelativepath": ".",
        "type": "TEXT",
        "implicit": 1
      },
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
