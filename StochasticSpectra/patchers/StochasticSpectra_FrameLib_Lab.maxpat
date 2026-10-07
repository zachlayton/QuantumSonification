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
      60.0,
      40.0,
      1005.0,
      865.0
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
    "description": "Simple direct/FrameLib stochastic voice with a separate packet envelope.",
    "digest": "Four visible controls: audio, morph rate, voice selection, and envelope mode.",
    "tags": "FrameLib stochastic wavetable envelope spectrogram",
    "boxes": [
      {
        "box": {
          "id": "source_panel",
          "maxclass": "panel",
          "patching_rect": [
            20.0,
            92.0,
            960.0,
            175.0
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
            282.0,
            960.0,
            175.0
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
            472.0,
            960.0,
            125.0
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
            612.0,
            960.0,
            225.0
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
            28.0,
            17.0,
            720.0,
            32.0
          ],
          "text": "Stochastic Spectra + FrameLib \u2014 Simple Instrument",
          "fontsize": 22.0
        }
      },
      {
        "box": {
          "id": "subtitle",
          "maxclass": "comment",
          "patching_rect": [
            30.0,
            53.0,
            690.0,
            24.0
          ],
          "text": "Four controls only: AUDIO, RATE, VOICE, and ENVELOPE",
          "fontsize": 13.0
        }
      },
      {
        "box": {
          "id": "audio_instruction",
          "maxclass": "comment",
          "patching_rect": [
            785.0,
            22.0,
            145.0,
            24.0
          ],
          "text": "1  CLICK AUDIO",
          "fontsize": 15.0
        }
      },
      {
        "box": {
          "id": "dac",
          "maxclass": "ezdac~",
          "patching_rect": [
            925.0,
            18.0,
            45.0,
            45.0
          ]
        }
      },
      {
        "box": {
          "id": "source_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            103.0,
            720.0,
            24.0
          ],
          "text": "2  SOURCE \u2014 fundamental pitch and stochastic morph rate",
          "fontsize": 15.0
        }
      },
      {
        "box": {
          "id": "source_note",
          "maxclass": "comment",
          "patching_rect": [
            38.0,
            135.0,
            730.0,
            22.0
          ],
          "text": "FUNDAMENTAL changes pitch. RATE changes how often a new spectrum is chosen; evolution is already ON.",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "rate_value",
          "maxclass": "flonum",
          "patching_rect": [
            45.0,
            180.0,
            75.0,
            24.0
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
            132.0,
            181.0,
            100.0,
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
            250.0,
            181.0,
            48.0,
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
            308.0,
            181.0,
            42.0,
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
            360.0,
            181.0,
            42.0,
            22.0
          ],
          "text": "8."
        }
      },
      {
        "box": {
          "id": "next",
          "maxclass": "message",
          "patching_rect": [
            425.0,
            181.0,
            55.0,
            22.0
          ],
          "text": "next"
        }
      },
      {
        "box": {
          "id": "freq_label",
          "maxclass": "comment",
          "patching_rect": [
            45.0,
            225.0,
            125.0,
            20.0
          ],
          "text": "FUNDAMENTAL Hz",
          "fontsize": 11.0
        }
      },
      {
        "box": {
          "id": "freq_value",
          "maxclass": "flonum",
          "patching_rect": [
            170.0,
            222.0,
            75.0,
            24.0
          ],
          "minimum": 1.0,
          "maximum": 20000.0
        }
      },
      {
        "box": {
          "id": "freq_prepend",
          "maxclass": "newobj",
          "patching_rect": [
            257.0,
            223.0,
            100.0,
            22.0
          ],
          "text": "prepend freq"
        }
      },
      {
        "box": {
          "id": "freq_55",
          "maxclass": "message",
          "patching_rect": [
            375.0,
            223.0,
            45.0,
            22.0
          ],
          "text": "55."
        }
      },
      {
        "box": {
          "id": "freq_110",
          "maxclass": "message",
          "patching_rect": [
            430.0,
            223.0,
            50.0,
            22.0
          ],
          "text": "110."
        }
      },
      {
        "box": {
          "id": "freq_220",
          "maxclass": "message",
          "patching_rect": [
            490.0,
            223.0,
            50.0,
            22.0
          ],
          "text": "220."
        }
      },
      {
        "box": {
          "id": "freq_load",
          "maxclass": "newobj",
          "patching_rect": [
            555.0,
            223.0,
            100.0,
            22.0
          ],
          "text": "loadmess 55."
        }
      },
      {
        "box": {
          "id": "morph_preset",
          "maxclass": "message",
          "patching_rect": [
            675.0,
            223.0,
            130.0,
            22.0
          ],
          "text": "gain 0.2, modes 24, slope 0., interp 400., slew 20., ampdepth 1., phasedepth 1., evolve 1, next"
        }
      },
      {
        "box": {
          "id": "preset_label",
          "maxclass": "comment",
          "patching_rect": [
            815.0,
            225.0,
            135.0,
            20.0
          ],
          "text": "RESET EVOLUTION",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "stoch",
          "maxclass": "newobj",
          "patching_rect": [
            820.0,
            181.0,
            135.0,
            22.0
          ],
          "text": "stochspectra~"
        }
      },
      {
        "box": {
          "id": "preset_load",
          "maxclass": "newobj",
          "patching_rect": [
            700.0,
            181.0,
            72.0,
            22.0
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "rate_load",
          "maxclass": "newobj",
          "patching_rect": [
            510.0,
            181.0,
            90.0,
            22.0
          ],
          "text": "loadmess 2."
        }
      },
      {
        "box": {
          "id": "frame_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            293.0,
            680.0,
            24.0
          ],
          "text": "3  VOICE \u2014 direct stochastic source or FrameLib spectral memory",
          "fontsize": 15.0
        }
      },
      {
        "box": {
          "id": "frame_note",
          "maxclass": "comment",
          "patching_rect": [
            38.0,
            325.0,
            745.0,
            22.0
          ],
          "text": "With AUDIO on, click CAPTURE once; then set VOICE to 1. Set it back to 0 for the direct source.",
          "fontsize": 12.0
        }
      },
      {
        "box": {
          "id": "capture_now",
          "maxclass": "button",
          "patching_rect": [
            48.0,
            369.0,
            28.0,
            28.0
          ]
        }
      },
      {
        "box": {
          "id": "capture_label",
          "maxclass": "comment",
          "patching_rect": [
            84.0,
            373.0,
            78.0,
            20.0
          ],
          "text": "CAPTURE",
          "fontsize": 11.0
        }
      },
      {
        "box": {
          "id": "voice_toggle",
          "maxclass": "toggle",
          "patching_rect": [
            205.0,
            369.0,
            28.0,
            28.0
          ]
        }
      },
      {
        "box": {
          "id": "voice_label",
          "maxclass": "comment",
          "patching_rect": [
            242.0,
            373.0,
            240.0,
            20.0
          ],
          "text": "VOICE: 0 DIRECT / 1 FRAMELIB",
          "fontsize": 11.0
        }
      },
      {
        "box": {
          "id": "voice_select",
          "maxclass": "newobj",
          "patching_rect": [
            205.0,
            412.0,
            70.0,
            22.0
          ],
          "text": "sel 0 1"
        }
      },
      {
        "box": {
          "id": "choose_direct",
          "maxclass": "message",
          "patching_rect": [
            300.0,
            412.0,
            145.0,
            22.0
          ],
          "text": "0 0 1., 1 0 0."
        }
      },
      {
        "box": {
          "id": "choose_frame",
          "maxclass": "message",
          "patching_rect": [
            460.0,
            412.0,
            145.0,
            22.0
          ],
          "text": "0 0 0., 1 0 1."
        }
      },
      {
        "box": {
          "id": "voice_load",
          "maxclass": "newobj",
          "patching_rect": [
            625.0,
            412.0,
            85.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "direct_delay",
          "maxclass": "newobj",
          "patching_rect": [
            510.0,
            369.0,
            125.0,
            22.0
          ],
          "text": "delay~ 4096 4096"
        }
      },
      {
        "box": {
          "id": "freeze",
          "maxclass": "newobj",
          "patching_rect": [
            660.0,
            369.0,
            125.0,
            22.0
          ],
          "text": "fl-freeze-stoch"
        }
      },
      {
        "box": {
          "id": "matrix",
          "maxclass": "newobj",
          "patching_rect": [
            800.0,
            369.0,
            165.0,
            22.0
          ],
          "text": "matrix~ 2 1 0. @ramp 50"
        }
      },
      {
        "box": {
          "id": "env_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            483.0,
            620.0,
            24.0
          ],
          "text": "4  ENVELOPE \u2014 continuous sound or gamma-renewal packets",
          "fontsize": 15.0
        }
      },
      {
        "box": {
          "id": "env_toggle",
          "maxclass": "toggle",
          "patching_rect": [
            48.0,
            533.0,
            28.0,
            28.0
          ]
        }
      },
      {
        "box": {
          "id": "env_label",
          "maxclass": "comment",
          "patching_rect": [
            86.0,
            537.0,
            270.0,
            20.0
          ],
          "text": "ENVELOPE: 0 CONTINUOUS / 1 GAMMA",
          "fontsize": 11.0
        }
      },
      {
        "box": {
          "id": "env_select",
          "maxclass": "newobj",
          "patching_rect": [
            375.0,
            534.0,
            70.0,
            22.0
          ],
          "text": "sel 0 1"
        }
      },
      {
        "box": {
          "id": "env_off",
          "maxclass": "message",
          "patching_rect": [
            465.0,
            534.0,
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
            560.0,
            534.0,
            365.0,
            22.0
          ],
          "text": "mode gamma, density 3., shape 2., duration 150., reset"
        }
      },
      {
        "box": {
          "id": "env_load",
          "maxclass": "newobj",
          "patching_rect": [
            375.0,
            567.0,
            85.0,
            22.0
          ],
          "text": "loadmess 0"
        }
      },
      {
        "box": {
          "id": "env",
          "maxclass": "newobj",
          "patching_rect": [
            790.0,
            567.0,
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
            935.0,
            534.0,
            38.0,
            22.0
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "monitor_title",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            623.0,
            480.0,
            24.0
          ],
          "text": "OUTPUT \u2014 selected voice \u00d7 separate envelope",
          "fontsize": 15.0
        }
      },
      {
        "box": {
          "id": "atten",
          "maxclass": "newobj",
          "patching_rect": [
            430.0,
            658.0,
            70.0,
            22.0
          ],
          "text": "*~ 0.5"
        }
      },
      {
        "box": {
          "id": "meter",
          "maxclass": "meter~",
          "patching_rect": [
            525.0,
            650.0,
            18.0,
            92.0
          ]
        }
      },
      {
        "box": {
          "id": "scope",
          "maxclass": "scope~",
          "patching_rect": [
            570.0,
            650.0,
            380.0,
            90.0
          ],
          "range": [
            -1.0,
            1.0
          ]
        }
      },
      {
        "box": {
          "id": "spectrogram_label",
          "maxclass": "comment",
          "patching_rect": [
            38.0,
            665.0,
            220.0,
            20.0
          ],
          "text": "SCROLLING SPECTROGRAM",
          "fontsize": 10.0
        }
      },
      {
        "box": {
          "id": "spectrogram",
          "maxclass": "spectroscope~",
          "patching_rect": [
            38.0,
            690.0,
            365.0,
            110.0
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
          "id": "footer",
          "maxclass": "comment",
          "patching_rect": [
            35.0,
            805.0,
            770.0,
            22.0
          ],
          "text": "If either custom object is orange, Max has not loaded the external and controls cannot work.",
          "fontsize": 12.0
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "preset_load",
            0
          ],
          "destination": [
            "morph_preset",
            0
          ],
          "hidden": 1
        }
      },
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
            "freq_value",
            0
          ],
          "destination": [
            "freq_prepend",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_prepend",
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
            "freq_55",
            0
          ],
          "destination": [
            "freq_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_110",
            0
          ],
          "destination": [
            "freq_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_220",
            0
          ],
          "destination": [
            "freq_value",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "freq_load",
            0
          ],
          "destination": [
            "freq_value",
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
            "direct_delay",
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
            "freeze",
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
            "voice_toggle",
            0
          ],
          "destination": [
            "voice_select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "voice_select",
            0
          ],
          "destination": [
            "choose_direct",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "voice_select",
            1
          ],
          "destination": [
            "choose_frame",
            0
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
            "voice_load",
            0
          ],
          "destination": [
            "voice_toggle",
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
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_toggle",
            0
          ],
          "destination": [
            "env_select",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_select",
            0
          ],
          "destination": [
            "env_off",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "env_select",
            1
          ],
          "destination": [
            "env_gamma",
            0
          ]
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
            "env_load",
            0
          ],
          "destination": [
            "env_toggle",
            0
          ],
          "hidden": 1
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
