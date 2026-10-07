{
  "patcher": {
    "fileversion": 1, "appversion": {"major": 9,"minor": 0,"revision": 0,"architecture": "x64"},
    "rect": [80.0,80.0,1280.0,800.0], "openinpresentation": 1,
    "boxes": [
      {"box":{"id":"title","maxclass":"comment","text":"QMW Quantum Metric Field · Jitter contract consumer v1","fontsize":20.0,"patching_rect":[24.0,18.0,570.0,30.0]}},
      {"box":{"id":"boundary","maxclass":"comment","text":"Consumes revision-locked fields only. No potential, metric, curvature, mode, or trajectory mathematics is performed in Max.","patching_rect":[24.0,50.0,800.0,20.0]}},
      {"box":{"id":"toggle","maxclass":"toggle","patching_rect":[24.0,87.0,24.0,24.0]}},
      {"box":{"id":"connect","maxclass":"message","text":"connect $1","patching_rect":[58.0,88.0,75.0,22.0]}},
      {"box":{"id":"node","maxclass":"newobj","text":"node.script live_client.js @autostart 1","patching_rect":[148.0,88.0,220.0,22.0]}},
      {"box":{"id":"fixture","maxclass":"message","text":"fixture /private/tmp/qmw_metric_threejs_final/qmw_metric_fixture_frames.json 900","patching_rect":[24.0,126.0,340.0,22.0]}},
      {"box":{"id":"route","maxclass":"newobj","text":"route frame status","patching_rect":[385.0,88.0,115.0,22.0]}},
      {"box":{"id":"prepend","maxclass":"newobj","text":"prepend frame","patching_rect":[385.0,126.0,95.0,22.0]}},
      {"box":{"id":"adapter","maxclass":"newobj","text":"js frame_to_jitter.js","patching_rect":[385.0,162.0,135.0,22.0]}},
      {"box":{"id":"status","maxclass":"message","text":"offline","patching_rect":[520.0,88.0,150.0,22.0]}},
      {"box":{"id":"presets","maxclass":"umenu","items":["analysis",",","performance"],"patching_rect":[700.0,88.0,120.0,22.0]}},
      {"box":{"id":"presetRoute","maxclass":"newobj","text":"prepend preset","patching_rect":[835.0,88.0,100.0,22.0]}},
      {"box":{"id":"visualControls","maxclass":"newobj","text":"js qmw_metric_visual_controls.js","patching_rect":[950.0,88.0,190.0,22.0]}},
      {"box":{"id":"commandReceive","maxclass":"newobj","text":"r qmw.metric.visual.command","patching_rect":[950.0,54.0,180.0,22.0]}},
      {"box":{"id":"presetSend","maxclass":"newobj","text":"s qmw.metric.visual.control","patching_rect":[950.0,126.0,170.0,22.0]}},
      {"box":{"id":"world","maxclass":"newobj","text":"jit.world qmw.metric.ctx @floating 1 @fsaa 1 @erase_color 0.02 0.025 0.05 1","patching_rect":[700.0,126.0,420.0,22.0]}},
      {"box":{"id":"density","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["density"],"patching_rect":[24.0,220.0,180.0,80.0]}},
      {"box":{"id":"potential","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["potential"],"patching_rect":[216.0,220.0,180.0,80.0]}},
      {"box":{"id":"contours","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["potential"],"patching_rect":[408.0,220.0,180.0,80.0]}},
      {"box":{"id":"metric","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["metric_00"],"patching_rect":[600.0,220.0,180.0,80.0]}},
      {"box":{"id":"lapse","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["lapse"],"patching_rect":[792.0,220.0,180.0,80.0]}},
      {"box":{"id":"curvature","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["curvature"],"patching_rect":[984.0,220.0,180.0,80.0]}},
      {"box":{"id":"hessian","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["hessian_00"],"patching_rect":[24.0,322.0,180.0,80.0]}},
      {"box":{"id":"current","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["probability_current_x"],"patching_rect":[216.0,322.0,180.0,80.0]}},
      {"box":{"id":"connection","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["phase_connection_x"],"patching_rect":[408.0,322.0,180.0,80.0]}},
      {"box":{"id":"vorticity","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["vorticity"],"patching_rect":[600.0,322.0,180.0,80.0]}},
      {"box":{"id":"eigenmode","maxclass":"bpatcher","name":"qmw_metric_overlay.maxpat","args":["eigenmode_0"],"patching_rect":[792.0,322.0,180.0,80.0]}},
      {"box":{"id":"trajectory","maxclass":"bpatcher","name":"qmw_metric_trajectory.maxpat","patching_rect":[984.0,322.0,240.0,80.0]}},
      {"box":{"id":"display","maxclass":"bpatcher","name":"qmw_metric_display.maxpat","patching_rect":[24.0,430.0,1080.0,280.0]}},
      {"box":{"id":"note","maxclass":"comment","text":"Each named bpatcher owns one float32 matrix/texture edge. Display geometry rebuilds only after an authoritative frame commit.","patching_rect":[24.0,720.0,900.0,40.0]}}
    ],
    "lines": [
      {"patchline":{"source":["toggle",0],"destination":["connect",0]}},{"patchline":{"source":["connect",0],"destination":["node",0]}},{"patchline":{"source":["fixture",0],"destination":["node",0]}},
      {"patchline":{"source":["node",0],"destination":["route",0]}},{"patchline":{"source":["route",0],"destination":["prepend",0]}},{"patchline":{"source":["route",1],"destination":["status",1]}},{"patchline":{"source":["prepend",0],"destination":["adapter",0]}},
      {"patchline":{"source":["presets",1],"destination":["presetRoute",0]}},{"patchline":{"source":["presetRoute",0],"destination":["visualControls",0]}},{"patchline":{"source":["commandReceive",0],"destination":["visualControls",0]}},{"patchline":{"source":["visualControls",0],"destination":["presetSend",0]}},{"patchline":{"source":["visualControls",0],"destination":["display",0]}},
      {"patchline":{"source":["adapter",0],"destination":["density",0]}},{"patchline":{"source":["adapter",0],"destination":["potential",0]}},{"patchline":{"source":["adapter",0],"destination":["contours",0]}},{"patchline":{"source":["adapter",0],"destination":["metric",0]}},{"patchline":{"source":["adapter",0],"destination":["lapse",0]}},{"patchline":{"source":["adapter",0],"destination":["curvature",0]}},{"patchline":{"source":["adapter",0],"destination":["hessian",0]}},{"patchline":{"source":["adapter",0],"destination":["current",0]}},{"patchline":{"source":["adapter",0],"destination":["connection",0]}},{"patchline":{"source":["adapter",0],"destination":["vorticity",0]}},{"patchline":{"source":["adapter",0],"destination":["eigenmode",0]}},{"patchline":{"source":["adapter",0],"destination":["trajectory",0]}},{"patchline":{"source":["adapter",0],"destination":["display",0]}}
    ]
  }
}
