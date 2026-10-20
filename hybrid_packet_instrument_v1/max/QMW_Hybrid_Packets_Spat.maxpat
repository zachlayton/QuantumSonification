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
    "classnamespace": "box",
    "rect": [
      40,
      40,
      1320,
      1240
    ],
    "bglocked": 0,
    "openinpresentation": 0,
    "default_fontsize": 12,
    "default_fontface": 0,
    "default_fontname": "Arial",
    "boxes": [
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            20,
            15,
            1100,
            24
          ],
          "text": "QMW HYBRID PACKETS v1 \u2014 SuperCollider excitation / existing v4.2b FX / Max + Spat"
        }
      },
      {
        "box": {
          "id": "setup",
          "maxclass": "comment",
          "patching_rect": [
            20,
            45,
            1180,
            24
          ],
          "text": "Start SC wrapper and Python backend first. Select the audio loopback driver: SC outputs must arrive at the same Max input numbers."
        }
      },
      {
        "box": {
          "id": "sc",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            110,
            250,
            24
          ],
          "text": "udpsend 127.0.0.1 17920"
        }
      },
      {
        "box": {
          "id": "physics",
          "maxclass": "newobj",
          "patching_rect": [
            660,
            110,
            250,
            24
          ],
          "text": "udpsend 127.0.0.1 17921"
        }
      },
      {
        "box": {
          "id": "start",
          "maxclass": "message",
          "patching_rect": [
            20,
            80,
            170,
            24
          ],
          "text": "/qmw/hybrid/start"
        }
      },
      {
        "box": {
          "id": "stop",
          "maxclass": "message",
          "patching_rect": [
            205,
            80,
            170,
            24
          ],
          "text": "/qmw/hybrid/stop"
        }
      },
      {
        "box": {
          "id": "burst",
          "maxclass": "message",
          "patching_rect": [
            390,
            80,
            170,
            24
          ],
          "text": "/qmw/hybrid/burst"
        }
      },
      {
        "box": {
          "id": "reset",
          "maxclass": "message",
          "patching_rect": [
            660,
            80,
            240,
            24
          ],
          "text": "/qmw/hybrid/physics/reset"
        }
      },
      {
        "box": {
          "id": "synthtitle",
          "maxclass": "comment",
          "patching_rect": [
            20,
            150,
            620,
            24
          ],
          "text": "SYNTHESIS / SHARED BODY (right-hand value boxes apply defaults when clicked)"
        }
      },
      {
        "box": {
          "id": "physicstitle",
          "maxclass": "comment",
          "patching_rect": [
            660,
            150,
            650,
            24
          ],
          "text": "HAMILTONIAN \u2014 parameter changes prepare a new state; rate only changes time scale"
        }
      },
      {
        "box": {
          "id": "blendlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            185,
            125,
            24
          ],
          "text": "blend"
        }
      },
      {
        "box": {
          "id": "blendnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            185,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "blendpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            185,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/blend"
        }
      },
      {
        "box": {
          "id": "blenddefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            185,
            70,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "densitylabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            215,
            125,
            24
          ],
          "text": "density"
        }
      },
      {
        "box": {
          "id": "densitynum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            215,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 4000
        }
      },
      {
        "box": {
          "id": "densitypre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            215,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/density"
        }
      },
      {
        "box": {
          "id": "densitydefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            215,
            70,
            24
          ],
          "text": "8"
        }
      },
      {
        "box": {
          "id": "durationlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            245,
            125,
            24
          ],
          "text": "duration"
        }
      },
      {
        "box": {
          "id": "durationnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            245,
            90,
            24
          ],
          "format": 6,
          "minimum": 0.002,
          "maximum": 2
        }
      },
      {
        "box": {
          "id": "durationpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            245,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/duration"
        }
      },
      {
        "box": {
          "id": "durationdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            245,
            70,
            24
          ],
          "text": "0.08"
        }
      },
      {
        "box": {
          "id": "carrierlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            275,
            125,
            24
          ],
          "text": "carrier"
        }
      },
      {
        "box": {
          "id": "carriernum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            275,
            90,
            24
          ],
          "format": 6,
          "minimum": 1,
          "maximum": 12000
        }
      },
      {
        "box": {
          "id": "carrierpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            275,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/carrier"
        }
      },
      {
        "box": {
          "id": "carrierdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            275,
            70,
            24
          ],
          "text": "165"
        }
      },
      {
        "box": {
          "id": "centerlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            305,
            125,
            24
          ],
          "text": "center"
        }
      },
      {
        "box": {
          "id": "centernum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            305,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "centerpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            305,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/center"
        }
      },
      {
        "box": {
          "id": "centerdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            305,
            70,
            24
          ],
          "text": "0.5"
        }
      },
      {
        "box": {
          "id": "widthlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            335,
            125,
            24
          ],
          "text": "width"
        }
      },
      {
        "box": {
          "id": "widthnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            335,
            90,
            24
          ],
          "format": 6,
          "minimum": 0.01,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "widthpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            335,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/width"
        }
      },
      {
        "box": {
          "id": "widthdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            335,
            70,
            24
          ],
          "text": "0.15"
        }
      },
      {
        "box": {
          "id": "f0label",
          "maxclass": "comment",
          "patching_rect": [
            20,
            365,
            125,
            24
          ],
          "text": "f0"
        }
      },
      {
        "box": {
          "id": "f0num",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            365,
            90,
            24
          ],
          "format": 6,
          "minimum": 15,
          "maximum": 1000
        }
      },
      {
        "box": {
          "id": "f0pre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            365,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/f0"
        }
      },
      {
        "box": {
          "id": "f0default",
          "maxclass": "message",
          "patching_rect": [
            565,
            365,
            70,
            24
          ],
          "text": "55"
        }
      },
      {
        "box": {
          "id": "decaylabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            395,
            125,
            24
          ],
          "text": "decay"
        }
      },
      {
        "box": {
          "id": "decaynum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            395,
            90,
            24
          ],
          "format": 6,
          "minimum": 0.02,
          "maximum": 20
        }
      },
      {
        "box": {
          "id": "decaypre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            395,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/decay"
        }
      },
      {
        "box": {
          "id": "decaydefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            395,
            70,
            24
          ],
          "text": "2"
        }
      },
      {
        "box": {
          "id": "gainlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            425,
            125,
            24
          ],
          "text": "gain"
        }
      },
      {
        "box": {
          "id": "gainnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            425,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 0.2
        }
      },
      {
        "box": {
          "id": "gainpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            425,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/gain"
        }
      },
      {
        "box": {
          "id": "gaindefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            425,
            70,
            24
          ],
          "text": "0.03"
        }
      },
      {
        "box": {
          "id": "attacklabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            455,
            125,
            24
          ],
          "text": "attack"
        }
      },
      {
        "box": {
          "id": "attacknum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            455,
            90,
            24
          ],
          "format": 6,
          "minimum": 0.001,
          "maximum": 10
        }
      },
      {
        "box": {
          "id": "attackpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            455,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/attack"
        }
      },
      {
        "box": {
          "id": "attackdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            455,
            70,
            24
          ],
          "text": "0.1"
        }
      },
      {
        "box": {
          "id": "releaselabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            485,
            125,
            24
          ],
          "text": "release"
        }
      },
      {
        "box": {
          "id": "releasenum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            485,
            90,
            24
          ],
          "format": 6,
          "minimum": 0.005,
          "maximum": 20
        }
      },
      {
        "box": {
          "id": "releasepre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            485,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/release"
        }
      },
      {
        "box": {
          "id": "releasedefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            485,
            70,
            24
          ],
          "text": "1"
        }
      },
      {
        "box": {
          "id": "densityDepthlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            515,
            125,
            24
          ],
          "text": "densityDepth"
        }
      },
      {
        "box": {
          "id": "densityDepthnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            515,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "densityDepthpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            515,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/densityDepth"
        }
      },
      {
        "box": {
          "id": "densityDepthdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            515,
            70,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "envelopeDepthlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            545,
            125,
            24
          ],
          "text": "envelopeDepth"
        }
      },
      {
        "box": {
          "id": "envelopeDepthnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            545,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "envelopeDepthpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            545,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/envelopeDepth"
        }
      },
      {
        "box": {
          "id": "envelopeDepthdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            545,
            70,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "normalizelabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            575,
            125,
            24
          ],
          "text": "normalize"
        }
      },
      {
        "box": {
          "id": "normalizenum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            575,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "normalizepre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            575,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/normalize"
        }
      },
      {
        "box": {
          "id": "normalizedefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            575,
            70,
            24
          ],
          "text": "1"
        }
      },
      {
        "box": {
          "id": "fxSendlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            605,
            125,
            24
          ],
          "text": "fxSend"
        }
      },
      {
        "box": {
          "id": "fxSendnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            605,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "fxSendpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            605,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/fxSend"
        }
      },
      {
        "box": {
          "id": "fxSenddefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            605,
            70,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "spatiallabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            635,
            125,
            24
          ],
          "text": "spatial"
        }
      },
      {
        "box": {
          "id": "spatialnum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            635,
            90,
            24
          ],
          "format": 6,
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "spatialpre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            635,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/spatial"
        }
      },
      {
        "box": {
          "id": "spatialdefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            635,
            70,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "phaselabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            665,
            125,
            24
          ],
          "text": "phase"
        }
      },
      {
        "box": {
          "id": "phasenum",
          "maxclass": "flonum",
          "patching_rect": [
            150,
            665,
            90,
            24
          ],
          "format": 6,
          "minimum": -3.14159,
          "maximum": 3.14159
        }
      },
      {
        "box": {
          "id": "phasepre",
          "maxclass": "newobj",
          "patching_rect": [
            250,
            665,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/control/phase"
        }
      },
      {
        "box": {
          "id": "phasedefault",
          "maxclass": "message",
          "patching_rect": [
            565,
            665,
            70,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "h_potentiallabel",
          "maxclass": "comment",
          "patching_rect": [
            660,
            185,
            125,
            24
          ],
          "text": "potential"
        }
      },
      {
        "box": {
          "id": "h_potentialnum",
          "maxclass": "flonum",
          "patching_rect": [
            790,
            185,
            90,
            24
          ],
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "h_potentialpre",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            185,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/physics/potential"
        }
      },
      {
        "box": {
          "id": "h_potentialdefault",
          "maxclass": "message",
          "patching_rect": [
            1205,
            185,
            70,
            24
          ],
          "text": "1"
        }
      },
      {
        "box": {
          "id": "h_centerlabel",
          "maxclass": "comment",
          "patching_rect": [
            660,
            215,
            125,
            24
          ],
          "text": "center"
        }
      },
      {
        "box": {
          "id": "h_centernum",
          "maxclass": "flonum",
          "patching_rect": [
            790,
            215,
            90,
            24
          ],
          "minimum": -0.8,
          "maximum": 0.8
        }
      },
      {
        "box": {
          "id": "h_centerpre",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            215,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/physics/center"
        }
      },
      {
        "box": {
          "id": "h_centerdefault",
          "maxclass": "message",
          "patching_rect": [
            1205,
            215,
            70,
            24
          ],
          "text": "-0.35"
        }
      },
      {
        "box": {
          "id": "h_widthlabel",
          "maxclass": "comment",
          "patching_rect": [
            660,
            245,
            125,
            24
          ],
          "text": "width"
        }
      },
      {
        "box": {
          "id": "h_widthnum",
          "maxclass": "flonum",
          "patching_rect": [
            790,
            245,
            90,
            24
          ],
          "minimum": 0.02,
          "maximum": 0.8
        }
      },
      {
        "box": {
          "id": "h_widthpre",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            245,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/physics/width"
        }
      },
      {
        "box": {
          "id": "h_widthdefault",
          "maxclass": "message",
          "patching_rect": [
            1205,
            245,
            70,
            24
          ],
          "text": "0.12"
        }
      },
      {
        "box": {
          "id": "h_momentumlabel",
          "maxclass": "comment",
          "patching_rect": [
            660,
            275,
            125,
            24
          ],
          "text": "momentum"
        }
      },
      {
        "box": {
          "id": "h_momentumnum",
          "maxclass": "flonum",
          "patching_rect": [
            790,
            275,
            90,
            24
          ],
          "minimum": -80,
          "maximum": 80
        }
      },
      {
        "box": {
          "id": "h_momentumpre",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            275,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/physics/momentum"
        }
      },
      {
        "box": {
          "id": "h_momentumdefault",
          "maxclass": "message",
          "patching_rect": [
            1205,
            275,
            70,
            24
          ],
          "text": "2"
        }
      },
      {
        "box": {
          "id": "h_phaselabel",
          "maxclass": "comment",
          "patching_rect": [
            660,
            305,
            125,
            24
          ],
          "text": "phase"
        }
      },
      {
        "box": {
          "id": "h_phasenum",
          "maxclass": "flonum",
          "patching_rect": [
            790,
            305,
            90,
            24
          ],
          "minimum": -3.14159,
          "maximum": 3.14159
        }
      },
      {
        "box": {
          "id": "h_phasepre",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            305,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/physics/phase"
        }
      },
      {
        "box": {
          "id": "h_phasedefault",
          "maxclass": "message",
          "patching_rect": [
            1205,
            305,
            70,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "h_omegalabel",
          "maxclass": "comment",
          "patching_rect": [
            660,
            335,
            125,
            24
          ],
          "text": "omega"
        }
      },
      {
        "box": {
          "id": "h_omeganum",
          "maxclass": "flonum",
          "patching_rect": [
            790,
            335,
            90,
            24
          ],
          "minimum": 0,
          "maximum": 30
        }
      },
      {
        "box": {
          "id": "h_omegapre",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            335,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/physics/omega"
        }
      },
      {
        "box": {
          "id": "h_omegadefault",
          "maxclass": "message",
          "patching_rect": [
            1205,
            335,
            70,
            24
          ],
          "text": "8"
        }
      },
      {
        "box": {
          "id": "h_ratelabel",
          "maxclass": "comment",
          "patching_rect": [
            660,
            365,
            125,
            24
          ],
          "text": "rate"
        }
      },
      {
        "box": {
          "id": "h_ratenum",
          "maxclass": "flonum",
          "patching_rect": [
            790,
            365,
            90,
            24
          ],
          "minimum": 0,
          "maximum": 10
        }
      },
      {
        "box": {
          "id": "h_ratepre",
          "maxclass": "newobj",
          "patching_rect": [
            890,
            365,
            300,
            24
          ],
          "text": "prepend /qmw/hybrid/physics/rate"
        }
      },
      {
        "box": {
          "id": "h_ratedefault",
          "maxclass": "message",
          "patching_rect": [
            1205,
            365,
            70,
            24
          ],
          "text": "0.1"
        }
      },
      {
        "box": {
          "id": "help",
          "maxclass": "comment",
          "patching_rect": [
            660,
            420,
            630,
            24
          ],
          "text": "blend: 0=synthesis, 1=Hamiltonian projection. Burst shapes cloud density and/or force. Modal decay continues after excitation."
        }
      },
      {
        "box": {
          "id": "help2",
          "maxclass": "comment",
          "patching_rect": [
            660,
            455,
            630,
            24
          ],
          "text": "Physics: potential 0=box, 1=harmonic inside hard walls. Dimensionless hbar=m=1. This is pure-state projection sonification."
        }
      },
      {
        "box": {
          "id": "help3",
          "maxclass": "comment",
          "patching_rect": [
            660,
            490,
            630,
            24
          ],
          "text": "Existing QMW window retains ring, wavefold, fuzz and Clouds/VST controls. Hybrid fxSend feeds the existing shared effects return."
        }
      },
      {
        "box": {
          "id": "help4",
          "maxclass": "comment",
          "patching_rect": [
            660,
            525,
            630,
            24
          ],
          "text": "The 16 pickup channels are dry. Processed stereo includes the existing instrument master and effects. Select one route below."
        }
      },
      {
        "box": {
          "id": "help5",
          "maxclass": "comment",
          "patching_rect": [
            660,
            560,
            630,
            24
          ],
          "text": "High packet rates are limited by grain capacity. This version has no physical temperature bath or anharmonic material simulation."
        }
      },
      {
        "box": {
          "id": "audiotitle",
          "maxclass": "comment",
          "patching_rect": [
            20,
            720,
            1180,
            24
          ],
          "text": "AUDIO ROUTING \u2014 configure loopback/aggregate device; this patch never turns DSP on automatically"
        }
      },
      {
        "box": {
          "id": "adc",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            760,
            650,
            24
          ],
          "text": "adc~ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"
        }
      },
      {
        "box": {
          "id": "fieldpack",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            810,
            140,
            24
          ],
          "text": "mc.pack~ 16"
        }
      },
      {
        "box": {
          "id": "masterpack",
          "maxclass": "newobj",
          "patching_rect": [
            240,
            810,
            140,
            24
          ],
          "text": "mc.pack~ 16"
        }
      },
      {
        "box": {
          "id": "select",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            870,
            160,
            24
          ],
          "text": "mc.selector~ 2"
        }
      },
      {
        "box": {
          "id": "fieldselect",
          "maxclass": "message",
          "patching_rect": [
            440,
            800,
            40,
            24
          ],
          "text": "1"
        }
      },
      {
        "box": {
          "id": "fieldlabel",
          "maxclass": "comment",
          "patching_rect": [
            490,
            800,
            370,
            24
          ],
          "text": "16 dry field pickups (SC5\u201320)"
        }
      },
      {
        "box": {
          "id": "masterselect",
          "maxclass": "message",
          "patching_rect": [
            440,
            835,
            40,
            24
          ],
          "text": "2"
        }
      },
      {
        "box": {
          "id": "masterlabel",
          "maxclass": "comment",
          "patching_rect": [
            490,
            835,
            480,
            24
          ],
          "text": "Processed stereo master (SC1\u20132 \u2192 source1/2)"
        }
      },
      {
        "box": {
          "id": "muteselect",
          "maxclass": "message",
          "patching_rect": [
            440,
            870,
            40,
            24
          ],
          "text": "0"
        }
      },
      {
        "box": {
          "id": "mutelabel",
          "maxclass": "comment",
          "patching_rect": [
            490,
            870,
            200,
            24
          ],
          "text": "Mute input"
        }
      },
      {
        "box": {
          "id": "renderer",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            930,
            350,
            24
          ],
          "text": "qmw_craive_spat128_renderer16_v9"
        }
      },
      {
        "box": {
          "id": "fieldpositions",
          "maxclass": "message",
          "patching_rect": [
            20,
            1120,
            1280,
            24
          ],
          "text": "/source/1/xyz -2.000000 2. 0., /source/2/xyz -1.733333 2. 0., /source/3/xyz -1.466667 2. 0., /source/4/xyz -1.200000 2. 0., /source/5/xyz -0.933333 2. 0., /source/6/xyz -0.666667 2. 0., /source/7/xyz -0.400000 2. 0., /source/8/xyz -0.133333 2. 0., /source/9/xyz 0.133333 2. 0., /source/10/xyz 0.400000 2. 0., /source/11/xyz 0.666667 2. 0., /source/12/xyz 0.933333 2. 0., /source/13/xyz 1.200000 2. 0., /source/14/xyz 1.466667 2. 0., /source/15/xyz 1.733333 2. 0., /source/16/xyz 2.000000 2. 0."
        }
      },
      {
        "box": {
          "id": "fieldposlabel",
          "maxclass": "comment",
          "patching_rect": [
            20,
            1080,
            1180,
            24
          ],
          "text": "CLICK BELOW to place the 16 pickups on a 4 m line. Geometry is playback scale, independent of model box size."
        }
      },
      {
        "box": {
          "id": "stereopositions",
          "maxclass": "message",
          "patching_rect": [
            660,
            930,
            570,
            24
          ],
          "text": "/source/1/xyz -1. 2. 0., /source/2/xyz 1. 2. 0."
        }
      },
      {
        "box": {
          "id": "gain",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            980,
            130,
            24
          ],
          "text": "mc.*~ 0."
        }
      },
      {
        "box": {
          "id": "level",
          "maxclass": "flonum",
          "patching_rect": [
            190,
            980,
            85,
            24
          ],
          "minimum": 0,
          "maximum": 1
        }
      },
      {
        "box": {
          "id": "levellabel",
          "maxclass": "comment",
          "patching_rect": [
            300,
            980,
            800,
            24
          ],
          "text": "Array gain starts at 0. Configure CRAIVE output map before raising."
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            1020,
            1200,
            24
          ],
          "text": "mc.dac~ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127 128"
        }
      },
      {
        "box": {
          "id": "status",
          "maxclass": "newobj",
          "patching_rect": [
            660,
            1020,
            250,
            24
          ],
          "text": "print QMW_Hybrid_Spat"
        }
      },
      {
        "box": {
          "id": "final",
          "maxclass": "comment",
          "patching_rect": [
            20,
            1170,
            1260,
            24
          ],
          "text": "FX fidelity path = processed stereo master; spatial-field path = 16 dry pickups. Never sum either input to stereo before WFS."
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "start",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "stop",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "burst",
            0
          ],
          "destination": [
            "sc",
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
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "blendnum",
            0
          ],
          "destination": [
            "blendpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "blendpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "blenddefault",
            0
          ],
          "destination": [
            "blendnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "densitynum",
            0
          ],
          "destination": [
            "densitypre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "densitypre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "densitydefault",
            0
          ],
          "destination": [
            "densitynum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "durationnum",
            0
          ],
          "destination": [
            "durationpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "durationpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "durationdefault",
            0
          ],
          "destination": [
            "durationnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carriernum",
            0
          ],
          "destination": [
            "carrierpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrierpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "carrierdefault",
            0
          ],
          "destination": [
            "carriernum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "centernum",
            0
          ],
          "destination": [
            "centerpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "centerpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "centerdefault",
            0
          ],
          "destination": [
            "centernum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "widthnum",
            0
          ],
          "destination": [
            "widthpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "widthpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "widthdefault",
            0
          ],
          "destination": [
            "widthnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "f0num",
            0
          ],
          "destination": [
            "f0pre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "f0pre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "f0default",
            0
          ],
          "destination": [
            "f0num",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "decaynum",
            0
          ],
          "destination": [
            "decaypre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "decaypre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "decaydefault",
            0
          ],
          "destination": [
            "decaynum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gainnum",
            0
          ],
          "destination": [
            "gainpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gainpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gaindefault",
            0
          ],
          "destination": [
            "gainnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "attacknum",
            0
          ],
          "destination": [
            "attackpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "attackpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "attackdefault",
            0
          ],
          "destination": [
            "attacknum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "releasenum",
            0
          ],
          "destination": [
            "releasepre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "releasepre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "releasedefault",
            0
          ],
          "destination": [
            "releasenum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "densityDepthnum",
            0
          ],
          "destination": [
            "densityDepthpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "densityDepthpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "densityDepthdefault",
            0
          ],
          "destination": [
            "densityDepthnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "envelopeDepthnum",
            0
          ],
          "destination": [
            "envelopeDepthpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "envelopeDepthpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "envelopeDepthdefault",
            0
          ],
          "destination": [
            "envelopeDepthnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "normalizenum",
            0
          ],
          "destination": [
            "normalizepre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "normalizepre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "normalizedefault",
            0
          ],
          "destination": [
            "normalizenum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fxSendnum",
            0
          ],
          "destination": [
            "fxSendpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fxSendpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fxSenddefault",
            0
          ],
          "destination": [
            "fxSendnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatialnum",
            0
          ],
          "destination": [
            "spatialpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatialpre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "spatialdefault",
            0
          ],
          "destination": [
            "spatialnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phasenum",
            0
          ],
          "destination": [
            "phasepre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phasepre",
            0
          ],
          "destination": [
            "sc",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "phasedefault",
            0
          ],
          "destination": [
            "phasenum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_potentialnum",
            0
          ],
          "destination": [
            "h_potentialpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_potentialpre",
            0
          ],
          "destination": [
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_potentialdefault",
            0
          ],
          "destination": [
            "h_potentialnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_centernum",
            0
          ],
          "destination": [
            "h_centerpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_centerpre",
            0
          ],
          "destination": [
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_centerdefault",
            0
          ],
          "destination": [
            "h_centernum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_widthnum",
            0
          ],
          "destination": [
            "h_widthpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_widthpre",
            0
          ],
          "destination": [
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_widthdefault",
            0
          ],
          "destination": [
            "h_widthnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_momentumnum",
            0
          ],
          "destination": [
            "h_momentumpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_momentumpre",
            0
          ],
          "destination": [
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_momentumdefault",
            0
          ],
          "destination": [
            "h_momentumnum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_phasenum",
            0
          ],
          "destination": [
            "h_phasepre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_phasepre",
            0
          ],
          "destination": [
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_phasedefault",
            0
          ],
          "destination": [
            "h_phasenum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_omeganum",
            0
          ],
          "destination": [
            "h_omegapre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_omegapre",
            0
          ],
          "destination": [
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_omegadefault",
            0
          ],
          "destination": [
            "h_omeganum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_ratenum",
            0
          ],
          "destination": [
            "h_ratepre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_ratepre",
            0
          ],
          "destination": [
            "physics",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "h_ratedefault",
            0
          ],
          "destination": [
            "h_ratenum",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            4
          ],
          "destination": [
            "fieldpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            5
          ],
          "destination": [
            "fieldpack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            6
          ],
          "destination": [
            "fieldpack",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            7
          ],
          "destination": [
            "fieldpack",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            8
          ],
          "destination": [
            "fieldpack",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            9
          ],
          "destination": [
            "fieldpack",
            5
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            10
          ],
          "destination": [
            "fieldpack",
            6
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            11
          ],
          "destination": [
            "fieldpack",
            7
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            12
          ],
          "destination": [
            "fieldpack",
            8
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            13
          ],
          "destination": [
            "fieldpack",
            9
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            14
          ],
          "destination": [
            "fieldpack",
            10
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            15
          ],
          "destination": [
            "fieldpack",
            11
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            16
          ],
          "destination": [
            "fieldpack",
            12
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            17
          ],
          "destination": [
            "fieldpack",
            13
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            18
          ],
          "destination": [
            "fieldpack",
            14
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            19
          ],
          "destination": [
            "fieldpack",
            15
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            0
          ],
          "destination": [
            "masterpack",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "adc",
            1
          ],
          "destination": [
            "masterpack",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fieldpack",
            0
          ],
          "destination": [
            "select",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "masterpack",
            0
          ],
          "destination": [
            "select",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fieldselect",
            0
          ],
          "destination": [
            "select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "masterselect",
            0
          ],
          "destination": [
            "select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "muteselect",
            0
          ],
          "destination": [
            "select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "select",
            0
          ],
          "destination": [
            "renderer",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "fieldpositions",
            0
          ],
          "destination": [
            "renderer",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "stereopositions",
            0
          ],
          "destination": [
            "renderer",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "renderer",
            0
          ],
          "destination": [
            "gain",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "level",
            0
          ],
          "destination": [
            "gain",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "gain",
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
            "renderer",
            2
          ],
          "destination": [
            "status",
            0
          ]
        }
      }
    ]
  }
}
