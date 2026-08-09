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
      45,
      1370,
      1020
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
            1050,
            28
          ],
          "text": "QMW QUANTUMSONIFICATION FOUNDATIONS EVALUATOR v1",
          "fontsize": 18.0
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            25,
            45,
            1120,
            38
          ],
          "text": "OSC 7474 \u00b7 graph-density representability \u00b7 tensor-relative negativity \u00b7 invariant-subspace continuity",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "udp",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            92,
            165,
            22
          ],
          "text": "udpreceive 7474 cnmat",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "osc",
          "maxclass": "newobj",
          "patching_rect": [
            215,
            92,
            130,
            22
          ],
          "text": "OpenSoundControl",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            "OSCTimeTag"
          ]
        }
      },
      {
        "box": {
          "id": "root",
          "maxclass": "newobj",
          "patching_rect": [
            370,
            92,
            105,
            22
          ],
          "text": "OSC-route /qsf",
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
          "id": "domain",
          "maxclass": "newobj",
          "patching_rect": [
            500,
            92,
            230,
            22
          ],
          "text": "OSC-route /graph /modal /status",
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
          "id": "graphroute",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            138,
            585,
            22
          ],
          "text": "OSC-route /dimension /rho_real /rho_abs /metrics /projection /negativity",
          "numinlets": 1,
          "numoutlets": 7,
          "outlettype": [
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
          "id": "modalroute",
          "maxclass": "newobj",
          "patching_rect": [
            630,
            138,
            720,
            22
          ],
          "text": "OSC-route /count /eigenvalues /stable_ids /cluster_ids /overlap /angles /residuals /revision",
          "numinlets": 1,
          "numoutlets": 9,
          "outlettype": [
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
          "id": "pdim",
          "maxclass": "newobj",
          "patching_rect": [
            25,
            175,
            120,
            22
          ],
          "text": "prepend graph_dimension",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "preal",
          "maxclass": "newobj",
          "patching_rect": [
            155,
            175,
            120,
            22
          ],
          "text": "prepend graph_rho_real",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pabs",
          "maxclass": "newobj",
          "patching_rect": [
            285,
            175,
            115,
            22
          ],
          "text": "prepend graph_rho_abs",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pcount",
          "maxclass": "newobj",
          "patching_rect": [
            630,
            175,
            120,
            22
          ],
          "text": "prepend modal_count",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "peigen",
          "maxclass": "newobj",
          "patching_rect": [
            760,
            175,
            145,
            22
          ],
          "text": "prepend modal_eigenvalues",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pstable",
          "maxclass": "newobj",
          "patching_rect": [
            915,
            175,
            135,
            22
          ],
          "text": "prepend modal_stable_ids",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pcluster",
          "maxclass": "newobj",
          "patching_rect": [
            1060,
            175,
            145,
            22
          ],
          "text": "prepend modal_cluster_ids",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "poverlap",
          "maxclass": "newobj",
          "patching_rect": [
            630,
            207,
            135,
            22
          ],
          "text": "prepend modal_overlap",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pangles",
          "maxclass": "newobj",
          "patching_rect": [
            775,
            207,
            125,
            22
          ],
          "text": "prepend modal_angles",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "presiduals",
          "maxclass": "newobj",
          "patching_rect": [
            910,
            207,
            140,
            22
          ],
          "text": "prepend modal_residuals",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "pstatus",
          "maxclass": "newobj",
          "patching_rect": [
            1060,
            207,
            95,
            22
          ],
          "text": "prepend status",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "js",
          "maxclass": "newobj",
          "patching_rect": [
            500,
            245,
            250,
            22
          ],
          "text": "js qmw_foundations_evaluator_v1.js",
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
          "id": "real_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            282,
            350,
            22
          ],
          "text": "rho_G signed real part \u00b7 blue negative / red positive",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "abs_label",
          "maxclass": "comment",
          "patching_rect": [
            390,
            282,
            320,
            22
          ],
          "text": "|rho_G| magnitude",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "modal_label",
          "maxclass": "comment",
          "patching_rect": [
            755,
            282,
            550,
            22
          ],
          "text": "modal rows: eigenvalue \u00b7 stable ID \u00b7 cluster ID \u00b7 overlap \u00b7 angle confidence \u00b7 residual quality",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "realview",
          "maxclass": "jit.pwindow",
          "patching_rect": [
            25,
            308,
            335,
            335
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
          "id": "absview",
          "maxclass": "jit.pwindow",
          "patching_rect": [
            390,
            308,
            335,
            335
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
          "id": "modalview",
          "maxclass": "jit.pwindow",
          "patching_rect": [
            755,
            308,
            570,
            230
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
          "id": "graph_metrics_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            665,
            700,
            22
          ],
          "text": "GRAPH METRICS: entropy \u00b7 purity \u00b7 rank \u00b7 nullity \u00b7 components",
          "fontsize": 13.0
        }
      },
      {
        "box": {
          "id": "graph_metrics",
          "maxclass": "multislider",
          "patching_rect": [
            25,
            690,
            700,
            70
          ],
          "size": 5,
          "setminmax": [
            0.0,
            16.0
          ],
          "slidercolor": [
            0.15,
            0.72,
            0.92,
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
          "id": "projection_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            772,
            700,
            22
          ],
          "text": "PROJECTION: Frobenius error \u00b7 trace distance \u00b7 imaginary residual \u00b7 rank deficit",
          "fontsize": 13.0
        }
      },
      {
        "box": {
          "id": "projection",
          "maxclass": "multislider",
          "patching_rect": [
            25,
            797,
            700,
            70
          ],
          "size": 4,
          "setminmax": [
            0.0,
            1.0
          ],
          "slidercolor": [
            0.95,
            0.44,
            0.24,
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
          "id": "negative_label",
          "maxclass": "comment",
          "patching_rect": [
            25,
            882,
            155,
            22
          ],
          "text": "negativity"
        }
      },
      {
        "box": {
          "id": "negative",
          "maxclass": "flonum",
          "patching_rect": [
            180,
            882,
            90,
            22
          ],
          "minimum": 0.0,
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
          "id": "revision_label",
          "maxclass": "comment",
          "patching_rect": [
            755,
            565,
            95,
            22
          ],
          "text": "revision"
        }
      },
      {
        "box": {
          "id": "revision",
          "maxclass": "number",
          "patching_rect": [
            850,
            565,
            80,
            22
          ],
          "minimum": 0,
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
          "id": "eigen_label",
          "maxclass": "comment",
          "patching_rect": [
            755,
            610,
            570,
            22
          ],
          "text": "eigenvalues"
        }
      },
      {
        "box": {
          "id": "eigen",
          "maxclass": "multislider",
          "patching_rect": [
            755,
            635,
            570,
            55
          ],
          "size": 16,
          "setminmax": [
            0.0,
            16.0
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
          "id": "overlap_label",
          "maxclass": "comment",
          "patching_rect": [
            755,
            705,
            570,
            22
          ],
          "text": "per-mode cluster overlap confidence"
        }
      },
      {
        "box": {
          "id": "overlap",
          "maxclass": "multislider",
          "patching_rect": [
            755,
            730,
            570,
            55
          ],
          "size": 16,
          "setminmax": [
            0.0,
            1.0
          ],
          "slidercolor": [
            0.3,
            0.88,
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
          "id": "residual_label",
          "maxclass": "comment",
          "patching_rect": [
            755,
            800,
            570,
            22
          ],
          "text": "generalized eigenpair residuals (display range 0\u20131e-4)"
        }
      },
      {
        "box": {
          "id": "residual",
          "maxclass": "multislider",
          "patching_rect": [
            755,
            825,
            570,
            55
          ],
          "size": 16,
          "setminmax": [
            0.0,
            0.0001
          ],
          "slidercolor": [
            0.92,
            0.25,
            0.3,
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
          "id": "status_label",
          "maxclass": "comment",
          "patching_rect": [
            755,
            895,
            65,
            22
          ],
          "text": "status"
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "message",
          "patching_rect": [
            825,
            895,
            500,
            22
          ],
          "text": "waiting for /qsf OSC on UDP 7474",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ]
        }
      },
      {
        "box": {
          "id": "contract",
          "maxclass": "comment",
          "patching_rect": [
            25,
            930,
            1300,
            55
          ],
          "text": "OSC contract: /qsf/graph/{dimension,rho_real,rho_abs,metrics,projection,negativity} \u00b7 /qsf/modal/{count,eigenvalues,stable_ids,cluster_ids,overlap,angles,residuals,revision} \u00b7 /qsf/status",
          "fontsize": 11.0
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
            "osc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "osc",
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
            "domain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "domain",
            0
          ],
          "destination": [
            "graphroute",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "domain",
            1
          ],
          "destination": [
            "modalroute",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "domain",
            2
          ],
          "destination": [
            "pstatus",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "graphroute",
            0
          ],
          "destination": [
            "pdim",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "graphroute",
            1
          ],
          "destination": [
            "preal",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "graphroute",
            2
          ],
          "destination": [
            "pabs",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "graphroute",
            3
          ],
          "destination": [
            "graph_metrics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "graphroute",
            4
          ],
          "destination": [
            "projection",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "graphroute",
            5
          ],
          "destination": [
            "negative",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            0
          ],
          "destination": [
            "pcount",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            1
          ],
          "destination": [
            "peigen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            1
          ],
          "destination": [
            "eigen",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            2
          ],
          "destination": [
            "pstable",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            3
          ],
          "destination": [
            "pcluster",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            4
          ],
          "destination": [
            "poverlap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            4
          ],
          "destination": [
            "overlap",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            5
          ],
          "destination": [
            "pangles",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            6
          ],
          "destination": [
            "presiduals",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            6
          ],
          "destination": [
            "residual",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "modalroute",
            7
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
            "pdim",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "preal",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pabs",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pcount",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "peigen",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pstable",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pcluster",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "poverlap",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pangles",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "presiduals",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "pstatus",
            0
          ],
          "destination": [
            "js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            0
          ],
          "destination": [
            "realview",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            1
          ],
          "destination": [
            "absview",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            2
          ],
          "destination": [
            "modalview",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "js",
            3
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
        "name": "OpenSoundControl.mxo",
        "type": "iLaX"
      },
      {
        "name": "OSC-route.mxo",
        "type": "iLaX"
      },
      {
        "name": "qmw_foundations_evaluator_v1.js",
        "type": "TEXT"
      }
    ],
    "autosave": 0
  }
}
