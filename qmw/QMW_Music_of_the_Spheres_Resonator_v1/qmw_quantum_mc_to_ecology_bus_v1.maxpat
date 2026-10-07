{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 0,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [120.0, 120.0, 620.0, 330.0],
    "default_fontsize": 12.0,
    "default_fontname": "Arial",
    "boxes": [
      {
        "box": {
          "id": "obj-1",
          "maxclass": "comment",
          "text": "QMW 16-channel quantum resonator → Operator Ecology stereo bus",
          "patching_rect": [30.0, 20.0, 470.0, 24.0]
        }
      },
      {
        "box": {
          "id": "obj-2",
          "maxclass": "inlet",
          "index": 1,
          "comment": "16-channel MC signal from qmw_density_field_quantum_resonator16_mc_v1",
          "outlettype": ["multichannelsignal"],
          "patching_rect": [80.0, 70.0, 30.0, 30.0]
        }
      },
      {
        "box": {
          "id": "obj-3",
          "maxclass": "newobj",
          "classnamespace": "box",
          "text": "mc.mixdown~ 2 @autogain 1",
          "patching_rect": [80.0, 120.0, 176.0, 23.0]
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "classnamespace": "box",
          "text": "mc.unpack~ 2",
          "patching_rect": [80.0, 165.0, 88.0, 23.0]
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "newobj",
          "classnamespace": "box",
          "text": "send~ qmw_spectral_L",
          "patching_rect": [45.0, 215.0, 142.0, 23.0]
        }
      },
      {
        "box": {
          "id": "obj-6",
          "maxclass": "newobj",
          "classnamespace": "box",
          "text": "send~ qmw_spectral_R",
          "patching_rect": [215.0, 215.0, 142.0, 23.0]
        }
      },
      {
        "box": {
          "id": "obj-7",
          "maxclass": "outlet",
          "index": 1,
          "comment": "stereo monitor left",
          "patching_rect": [100.0, 265.0, 30.0, 30.0]
        }
      },
      {
        "box": {
          "id": "obj-8",
          "maxclass": "outlet",
          "index": 2,
          "comment": "stereo monitor right",
          "patching_rect": [270.0, 265.0, 30.0, 30.0]
        }
      }
    ],
    "lines": [
      {"patchline": {"source": ["obj-2", 0], "destination": ["obj-3", 0]}},
      {"patchline": {"source": ["obj-3", 0], "destination": ["obj-4", 0]}},
      {"patchline": {"source": ["obj-4", 0], "destination": ["obj-5", 0]}},
      {"patchline": {"source": ["obj-4", 1], "destination": ["obj-6", 0]}},
      {"patchline": {"source": ["obj-4", 0], "destination": ["obj-7", 0]}},
      {"patchline": {"source": ["obj-4", 1], "destination": ["obj-8", 0]}}
    ],
    "autosave": 0
  }
}
