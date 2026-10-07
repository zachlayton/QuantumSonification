{
  "patcher": {
    "fileversion": 1, "appversion": {"major": 9, "minor": 0, "revision": 0, "architecture": "x64"},
    "rect": [0.0, 0.0, 330.0, 105.0], "openinpresentation": 1,
    "boxes": [
      {"box":{"id":"in","maxclass":"inlet","patching_rect":[18.0,18.0,30.0,30.0]}},
      {"box":{"id":"route","maxclass":"newobj","text":"route #1","patching_rect":[60.0,20.0,80.0,22.0]}},
      {"box":{"id":"matrix","maxclass":"newobj","text":"jit.matrix #1 1 float32 32 32","patching_rect":[150.0,20.0,170.0,22.0]}},
      {"box":{"id":"texture","maxclass":"newobj","text":"jit.gl.texture qmw.metric.ctx @name qmw_metric_#1_tex @type float32","patching_rect":[145.0,52.0,178.0,22.0]}},
      {"box":{"id":"out","maxclass":"outlet","patching_rect":[285.0,78.0,30.0,30.0]}},
      {"box":{"id":"label","maxclass":"comment","text":"#1 overlay · authoritative float texture consumer","patching_rect":[18.0,68.0,255.0,20.0]}}
    ],
    "lines": [
      {"patchline":{"source":["in",0],"destination":["route",0]}},
      {"patchline":{"source":["route",0],"destination":["matrix",0]}},
      {"patchline":{"source":["matrix",0],"destination":["texture",0]}},
      {"patchline":{"source":["texture",0],"destination":["out",0]}}
    ]
  }
}
