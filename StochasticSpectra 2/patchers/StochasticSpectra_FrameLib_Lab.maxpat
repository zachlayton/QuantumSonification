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
      45.0,
      30.0,
      1210.0,
      1050.0
    ],
    "bglocked": 0,
    "openinpresentation": 0,
    "default_fontname": "Arial",
    "default_fontsize": 12.0,
    "gridonopen": 1,
    "gridsize": [
      15.0,
      15.0
    ],
    "gridsnaponopen": 1,
    "objectsnaponopen": 1,
    "statusbarvisible": 2,
    "toolbarvisible": 1,
    "description": "FrameLib statistical spectral-memory companion for Stochastic Spectra.",
    "digest": "Direct and FrameLib-resynthesized stochastic voices through a separate packet envelope.",
    "tags": "FrameLib stochastic spectral freeze wavetable envelope analysis",
    "boxes": [
      {
        "box": {
          "id": "source_panel",
          "maxclass": "panel",
          "patching_rect": [
            20.0,
            85.0,
            1160.0,
            215.0
          ],
          "background": 1,
          "bgcolor": [
            0.91,
            0.95,
            0.99,
            1.0
          ],
          "border": 1,
          "bordercolor": [
            0.7,
            0.72,
            0.76,
            1.0
          ],
          "rounded": 10
        }
      },
      {
        "box": {
          "id": "frame_panel",
          "maxclass": "panel",
          "patching_rect": [
            20.0,
            315.0,
            1160.0,
            230.0
          ],
          "background": 1,
          "bgcolor": [
            0.96,
            0.93,
            0.99,
            1.0
          ],
          "border": 1,
          "bordercolor": [
            0.7,
            0.72,
            0.76,
            1.0
          ],
          "rounded": 10
        }
      },
      {
        "box": {
          "id": "env_panel",
          "maxclass": "panel",
          "patching_rect": [
            20.0,
            560.0,
            1160.0,
            135.0
          ],
          "background": 1,
          "bgcolor": [
            0.99,
            0.93,
            0.93,
            1.0
          ],
          "border": 1,
          "bordercolor": [
            0.7,
            0.72,
            0.76,
            1.0
          ],
          "rounded": 10
        }
      },
      {
        "box": {
          "id": "monitor_panel",
          "maxclass": "panel",
          "patching_rect": [
            20.0,
            710.0,
            1160.0,
            280.0
          ],
          "background": 1,
          "bgcolor": [
            0.91,
            0.97,
            0.94,
            1.0
          ],
          "border": 1,
          "bordercolor": [
            0.7,
            0.72,
            0.76,
            1.0
          ],
          "rounded": 10
        }
      },
      {
        "box": {
          "id": "title",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            17.0,
            720.0,
            32.0
          ],
          "text": "Stochastic Spectra \u00d7 FrameLib Lab",
          "fontsize": 22.0
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            32.0,
            53.0,
            1100.0,
            22.0
          ],
          "text": "v0.5.0 companion patch \u2022 direct stochastic voice + FrameLib statistical spectral memory \u2022 separate packet envelope and explicit *~",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "source_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            96.0,
            390.0,
            24.0
          ],
          "text": "1  CONTINUOUS STOCHASTIC SOURCE",
          "fontsize": 16.0
        }
      },
      {
        "box": {
          "id": "morph_preset",
          "maxclass": "message",
          "patching_rect": [
            38.0,
            132.0,
            760.0,
            22.0
          ],
          "text": "modes 24, slope 0., interp 400., slew 20., ampdepth 1., phasedepth 1., evolve 1, next"
        }
      },
      {
        "box": {
          "id": "morph_label",
          "maxclass": "comment",
          "patching_rect": [
            815.0,
            134.0,
            190.0,
            20.0
          ],
          "text": "AUDIBLE MORPH PRESET",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "evolve_on",
          "maxclass": "message",
          "patching_rect": [
            38.0,
            172.0,
            88.0,
            22.0
          ],
          "text": "evolve 1"
        }
      },
      {
        "box": {
          "id": "evolve_off",
          "maxclass": "message",
          "patching_rect": [
            136.0,
            172.0,
            88.0,
            22.0
          ],
          "text": "evolve 0"
        }
      },
      {
        "box": {
          "id": "next",
          "maxclass": "message",
          "patching_rect": [
            234.0,
            172.0,
            60.0,
            22.0
          ],
          "text": "next"
        }
      },
      {
        "box": {
          "id": "rate_label",
          "maxclass": "comment",
          "patching_rect": [
            314.0,
            174.0,
            115.0,
            20.0
          ],
          "text": "RATE targets/sec",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "rate_value",
          "maxclass": "flonum",
          "patching_rect": [
            426.0,
            172.0,
            70.0,
            22.0
          ],
          "minimum": 0.01,
          "maximum": 100.0
        }
      },
      {
        "box": {
          "id": "rate_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            508.0,
            172.0,
            98.0,
            22.0
          ],
          "text": "prepend rate"
        }
      },
      {
        "box": {
          "id": "rate_slow",
          "maxclass": "message",
          "patching_rect": [
            622.0,
            172.0,
            45.0,
            22.0
          ],
          "text": "0.5"
        }
      },
      {
        "box": {
          "id": "rate_mid",
          "maxclass": "message",
          "patching_rect": [
            677.0,
            172.0,
            40.0,
            22.0
          ],
          "text": "2."
        }
      },
      {
        "box": {
          "id": "rate_fast",
          "maxclass": "message",
          "patching_rect": [
            727.0,
            172.0,
            40.0,
            22.0
          ],
          "text": "8."
        }
      },
      {
        "box": {
          "id": "rate_load",
          "maxclass": "newobj",
          "patching_rect": [
            782.0,
            172.0,
            90.0,
            22.0
          ],
          "text": "loadmess 2."
        }
      },
      {
        "box": {
          "id": "spectral_status",
          "maxclass": "message",
          "patching_rect": [
            890.0,
            172.0,
            66.0,
            22.0
          ],
          "text": "status"
        }
      },
      {
        "box": {
          "id": "stoch",
          "maxclass": "newobj",
          "patching_rect": [
            965.0,
            210.0,
            135.0,
            22.0
          ],
          "text": "stochspectra~"
        }
      },
      {
        "box": {
          "id": "source_note",
          "maxclass": "comment",
          "patching_rect": [
            38.0,
            246.0,
            900.0,
            22.0
          ],
          "text": "This remains the authoritative continuous voice. FrameLib is an additive analysis/resynthesis branch, not part of the external.",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "frame_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            326.0,
            520.0,
            24.0
          ],
          "text": "2  FRAMELIB STATISTICAL SPECTRAL MEMORY",
          "fontsize": 16.0
        }
      },
      {
        "box": {
          "id": "frame_dependency",
          "maxclass": "comment",
          "patching_rect": [
            485.0,
            328.0,
            675.0,
            22.0
          ],
          "text": "Requires installed FrameLib 1.0.1. fl-freeze-stoch analyses overlapping FFT frames and regenerates magnitudes/phase deltas statistically.",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "capture_now",
          "maxclass": "button",
          "patching_rect": [
            42.0,
            374.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "capture_now_label",
          "maxclass": "comment",
          "patching_rect": [
            76.0,
            376.0,
            190.0,
            20.0
          ],
          "text": "CAPTURE / UPDATE MODEL",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "capture_auto",
          "maxclass": "toggle",
          "patching_rect": [
            42.0,
            414.0,
            24.0,
            24.0
          ]
        }
      },
      {
        "box": {
          "id": "capture_auto_label",
          "maxclass": "comment",
          "patching_rect": [
            76.0,
            416.0,
            100.0,
            20.0
          ],
          "text": "AUTO UPDATE",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "capture_metro",
          "maxclass": "newobj",
          "patching_rect": [
            190.0,
            414.0,
            90.0,
            22.0
          ],
          "text": "qmetro 1000"
        }
      },
      {
        "box": {
          "id": "capture_ms",
          "maxclass": "number",
          "patching_rect": [
            293.0,
            414.0,
            70.0,
            22.0
          ],
          "minimum": 100,
          "maximum": 10000
        }
      },
      {
        "box": {
          "id": "capture_ms_label",
          "maxclass": "comment",
          "patching_rect": [
            369.0,
            416.0,
            28.0,
            20.0
          ],
          "text": "ms",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "capture_toggle_load",
          "maxclass": "newobj",
          "patching_rect": [
            42.0,
            450.0,
            82.0,
            22.0
          ],
          "text": "loadmess 1"
        }
      },
      {
        "box": {
          "id": "capture_ms_load",
          "maxclass": "newobj",
          "patching_rect": [
            135.0,
            450.0,
            105.0,
            22.0
          ],
          "text": "loadmess 1000"
        }
      },
      {
        "box": {
          "id": "freeze",
          "maxclass": "newobj",
          "patching_rect": [
            420.0,
            405.0,
            125.0,
            22.0
          ],
          "text": "fl-freeze-stoch"
        }
      },
      {
        "box": {
          "id": "freeze_note",
          "maxclass": "comment",
          "patching_rect": [
            409.0,
            437.0,
            190.0,
            18.0
          ],
          "text": "FrameLib tutorial abstraction",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "choose_direct",
          "maxclass": "message",
          "patching_rect": [
            630.0,
            374.0,
            145.0,
            22.0
          ],
          "text": "0 0 1., 1 0 0."
        }
      },
      {
        "box": {
          "id": "choose_direct_label",
          "maxclass": "comment",
          "patching_rect": [
            780.0,
            376.0,
            65.0,
            20.0
          ],
          "text": "DIRECT",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "choose_frame",
          "maxclass": "message",
          "patching_rect": [
            630.0,
            410.0,
            145.0,
            22.0
          ],
          "text": "0 0 0., 1 0 1."
        }
      },
      {
        "box": {
          "id": "choose_frame_label",
          "maxclass": "comment",
          "patching_rect": [
            780.0,
            412.0,
            75.0,
            20.0
          ],
          "text": "FRAMELIB",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "direct_delay",
          "maxclass": "newobj",
          "patching_rect": [
            630.0,
            452.0,
            125.0,
            22.0
          ],
          "text": "delay~ 4096 4096"
        }
      },
      {
        "box": {
          "id": "matrix",
          "maxclass": "newobj",
          "patching_rect": [
            870.0,
            395.0,
            175.0,
            22.0
          ],
          "text": "matrix~ 2 1 0. @ramp 50"
        }
      },
      {
        "box": {
          "id": "direct_load",
          "maxclass": "newobj",
          "patching_rect": [
            870.0,
            435.0,
            130.0,
            22.0
          ],
          "text": "loadmess 0 0 1."
        }
      },
      {
        "box": {
          "id": "frame_note",
          "maxclass": "comment",
          "patching_rect": [
            38.0,
            500.0,
            1060.0,
            22.0
          ],
          "text": "The direct path is delayed 4096 samples to match FrameLib source latency. The 50 ms matrix ramp avoids hard switching; resynthesis is intentionally not phase-identical.",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "env_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            571.0,
            360.0,
            24.0
          ],
          "text": "3  SEPARATE EVENT ENVELOPE",
          "fontsize": 16.0
        }
      },
      {
        "box": {
          "id": "env_off",
          "maxclass": "message",
          "patching_rect": [
            38.0,
            612.0,
            82.0,
            22.0
          ],
          "text": "mode off"
        }
      },
      {
        "box": {
          "id": "env_gamma",
          "maxclass": "message",
          "patching_rect": [
            135.0,
            612.0,
            690.0,
            22.0
          ],
          "text": "mode gamma, density 3., shape 2., duration 150., window gaussian, polyphony 16, reset"
        }
      },
      {
        "box": {
          "id": "env_status",
          "maxclass": "message",
          "patching_rect": [
            840.0,
            612.0,
            66.0,
            22.0
          ],
          "text": "status"
        }
      },
      {
        "box": {
          "id": "env",
          "maxclass": "newobj",
          "patching_rect": [
            925.0,
            612.0,
            145.0,
            22.0
          ],
          "text": "stochpacketenv~"
        }
      },
      {
        "box": {
          "id": "multiply",
          "maxclass": "newobj",
          "patching_rect": [
            1090.0,
            612.0,
            45.0,
            22.0
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "env_note",
          "maxclass": "comment",
          "patching_rect": [
            38.0,
            656.0,
            930.0,
            22.0
          ],
          "text": "FrameLib/direct voice enters the left inlet; stochpacketenv~ amplitude enters the right inlet. Multiplication remains explicit.",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "monitor_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            721.0,
            470.0,
            24.0
          ],
          "text": "4  FRAMELIB OBSERVER + AUDIO MONITOR",
          "fontsize": 16.0
        }
      },
      {
        "box": {
          "id": "analysis_interval",
          "maxclass": "newobj",
          "patching_rect": [
            40.0,
            765.0,
            110.0,
            22.0
          ],
          "text": "fl.interval~ 1024"
        }
      },
      {
        "box": {
          "id": "analysis_source",
          "maxclass": "newobj",
          "patching_rect": [
            165.0,
            765.0,
            160.0,
            22.0
          ],
          "text": "fl.source~ /length 4096"
        }
      },
      {
        "box": {
          "id": "analysis_window",
          "maxclass": "newobj",
          "patching_rect": [
            340.0,
            765.0,
            220.0,
            22.0
          ],
          "text": "fl.window~ hann /compensate linear"
        }
      },
      {
        "box": {
          "id": "analysis_fft",
          "maxclass": "newobj",
          "patching_rect": [
            575.0,
            765.0,
            62.0,
            22.0
          ],
          "text": "fl.fft~"
        }
      },
      {
        "box": {
          "id": "analysis_magnitude",
          "maxclass": "newobj",
          "patching_rect": [
            652.0,
            765.0,
            72.0,
            22.0
          ],
          "text": "fl.hypot~"
        }
      },
      {
        "box": {
          "id": "centroid",
          "maxclass": "newobj",
          "patching_rect": [
            740.0,
            750.0,
            88.0,
            22.0
          ],
          "text": "fl.centroid~"
        }
      },
      {
        "box": {
          "id": "flatness",
          "maxclass": "newobj",
          "patching_rect": [
            740.0,
            785.0,
            88.0,
            22.0
          ],
          "text": "fl.flatness~"
        }
      },
      {
        "box": {
          "id": "delta",
          "maxclass": "newobj",
          "patching_rect": [
            740.0,
            820.0,
            100.0,
            22.0
          ],
          "text": "fl.framedelta~"
        }
      },
      {
        "box": {
          "id": "delta_rms",
          "maxclass": "newobj",
          "patching_rect": [
            855.0,
            820.0,
            60.0,
            22.0
          ],
          "text": "fl.rms~"
        }
      },
      {
        "box": {
          "id": "centroid_to_max",
          "maxclass": "newobj",
          "patching_rect": [
            845.0,
            750.0,
            70.0,
            22.0
          ],
          "text": "fl.tomax~"
        }
      },
      {
        "box": {
          "id": "flatness_to_max",
          "maxclass": "newobj",
          "patching_rect": [
            845.0,
            785.0,
            70.0,
            22.0
          ],
          "text": "fl.tomax~"
        }
      },
      {
        "box": {
          "id": "delta_to_max",
          "maxclass": "newobj",
          "patching_rect": [
            930.0,
            820.0,
            70.0,
            22.0
          ],
          "text": "fl.tomax~"
        }
      },
      {
        "box": {
          "id": "centroid_value",
          "maxclass": "flonum",
          "patching_rect": [
            930.0,
            750.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "flatness_value",
          "maxclass": "flonum",
          "patching_rect": [
            930.0,
            785.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "delta_value",
          "maxclass": "flonum",
          "patching_rect": [
            1015.0,
            820.0,
            72.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "centroid_label",
          "maxclass": "comment",
          "patching_rect": [
            1010.0,
            752.0,
            95.0,
            20.0
          ],
          "text": "centroid bin",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "flatness_label",
          "maxclass": "comment",
          "patching_rect": [
            1010.0,
            787.0,
            75.0,
            20.0
          ],
          "text": "flatness",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "delta_label",
          "maxclass": "comment",
          "patching_rect": [
            1090.0,
            822.0,
            82.0,
            20.0
          ],
          "text": "frame \u0394 RMS",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "atten",
          "maxclass": "newobj",
          "patching_rect": [
            420.0,
            860.0,
            75.0,
            22.0
          ],
          "text": "*~ 0.35"
        }
      },
      {
        "box": {
          "id": "meter",
          "maxclass": "meter~",
          "patching_rect": [
            520.0,
            846.0,
            18.0,
            80.0
          ]
        }
      },
      {
        "box": {
          "id": "scope",
          "maxclass": "scope~",
          "patching_rect": [
            565.0,
            850.0,
            235.0,
            85.0
          ],
          "range": [
            -1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "spectrogram",
          "maxclass": "spectroscope~",
          "patching_rect": [
            40.0,
            895.0,
            350.0,
            70.0
          ],
          "logfreq": 1,
          "monochrome": 0,
          "range": [
            0.0,
            1.0
          ],
          "scroll": 2,
          "sono": 1
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "ezdac~",
          "patching_rect": [
            840.0,
            880.0,
            45.0,
            45.0
          ]
        }
      },
      {
        "box": {
          "id": "dac_note",
          "maxclass": "comment",
          "patching_rect": [
            900.0,
            894.0,
            120.0,
            20.0
          ],
          "text": "Audio starts OFF",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "footer",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            1002.0,
            1000.0,
            22.0
          ],
          "text": "Observer metrics are read-only and measured before the packet envelope. They do not drive the voice in this first integration slice.",
          "fontsize": 12.0
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "morph_preset",
            0
          ],
          "destination": [
            "stoch",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "evolve_on",
            0
          ],
          "destination": [
            "stoch",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "evolve_off",
            0
          ],
          "destination": [
            "stoch",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "next",
            0
          ],
          "destination": [
            "stoch",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "rate_prepend",
            0
          ],
          "destination": [
            "stoch",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "spectral_status",
            0
          ],
          "destination": [
            "stoch",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "env_off",
            0
          ],
          "destination": [
            "env",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "env_gamma",
            0
          ],
          "destination": [
            "env",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "env_status",
            0
          ],
          "destination": [
            "env",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "rate_value",
            0
          ],
          "destination": [
            "rate_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rate_slow",
            0
          ],
          "destination": [
            "rate_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rate_mid",
            0
          ],
          "destination": [
            "rate_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rate_fast",
            0
          ],
          "destination": [
            "rate_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "rate_load",
            0
          ],
          "destination": [
            "rate_value",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "stoch",
            0
          ],
          "destination": [
            "freeze",
            0
          ],
          "order": 0
        }
      },
      {
        "patchline": {
          "source": [
            "stoch",
            0
          ],
          "destination": [
            "direct_delay",
            0
          ],
          "order": 1
        }
      },
      {
        "patchline": {
          "source": [
            "direct_delay",
            0
          ],
          "destination": [
            "matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "capture_now",
            0
          ],
          "destination": [
            "freeze",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "capture_auto",
            0
          ],
          "destination": [
            "capture_metro",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "capture_metro",
            0
          ],
          "destination": [
            "freeze",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "capture_ms",
            0
          ],
          "destination": [
            "capture_metro",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "capture_toggle_load",
            0
          ],
          "destination": [
            "capture_auto",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "capture_ms_load",
            0
          ],
          "destination": [
            "capture_ms",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "freeze",
            0
          ],
          "destination": [
            "matrix",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "choose_direct",
            0
          ],
          "destination": [
            "matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "choose_frame",
            0
          ],
          "destination": [
            "matrix",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "direct_load",
            0
          ],
          "destination": [
            "matrix",
            0
          ],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": [
            "matrix",
            0
          ],
          "destination": [
            "multiply",
            0
          ],
          "order": 0
        }
      },
      {
        "patchline": {
          "source": [
            "matrix",
            0
          ],
          "destination": [
            "analysis_source",
            0
          ],
          "order": 1
        }
      },
      {
        "patchline": {
          "source": [
            "env",
            0
          ],
          "destination": [
            "multiply",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_interval",
            0
          ],
          "destination": [
            "analysis_source",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_source",
            0
          ],
          "destination": [
            "analysis_window",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_window",
            0
          ],
          "destination": [
            "analysis_fft",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_fft",
            0
          ],
          "destination": [
            "analysis_magnitude",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_fft",
            1
          ],
          "destination": [
            "analysis_magnitude",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_magnitude",
            0
          ],
          "destination": [
            "centroid",
            0
          ],
          "order": 0
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_magnitude",
            0
          ],
          "destination": [
            "flatness",
            0
          ],
          "order": 1
        }
      },
      {
        "patchline": {
          "source": [
            "analysis_magnitude",
            0
          ],
          "destination": [
            "delta",
            0
          ],
          "order": 2
        }
      },
      {
        "patchline": {
          "source": [
            "delta",
            0
          ],
          "destination": [
            "delta_rms",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "centroid",
            0
          ],
          "destination": [
            "centroid_to_max",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "flatness",
            0
          ],
          "destination": [
            "flatness_to_max",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "delta_rms",
            0
          ],
          "destination": [
            "delta_to_max",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "centroid_to_max",
            0
          ],
          "destination": [
            "centroid_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "flatness_to_max",
            0
          ],
          "destination": [
            "flatness_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "delta_to_max",
            0
          ],
          "destination": [
            "delta_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "multiply",
            0
          ],
          "destination": [
            "atten",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "atten",
            0
          ],
          "destination": [
            "meter",
            0
          ],
          "order": 0
        }
      },
      {
        "patchline": {
          "source": [
            "atten",
            0
          ],
          "destination": [
            "scope",
            0
          ],
          "order": 1
        }
      },
      {
        "patchline": {
          "source": [
            "atten",
            0
          ],
          "destination": [
            "spectrogram",
            0
          ],
          "order": 2
        }
      },
      {
        "patchline": {
          "source": [
            "atten",
            0
          ],
          "destination": [
            "dac",
            0
          ],
          "order": 3
        }
      },
      {
        "patchline": {
          "source": [
            "atten",
            0
          ],
          "destination": [
            "dac",
            1
          ],
          "order": 4
        }
      }
    ]
  }
}
