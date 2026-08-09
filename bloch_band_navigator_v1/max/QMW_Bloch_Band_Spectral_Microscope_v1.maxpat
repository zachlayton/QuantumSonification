{
  "patcher": {
    "fileversion": 1,
    "appversion": {"major": 9, "minor": 0, "revision": 0, "architecture": "x64", "modernui": 1},
    "classnamespace": "box",
    "rect": [120.0, 90.0, 1040.0, 650.0],
    "gridsize": [15.0, 15.0],
    "boxes": [
      {"box":{"id":"title","maxclass":"comment","text":"BLOCH BAND SPECTRAL MICROSCOPE v1","fontsize":18.0,"fontface":1,"patching_rect":[40.0,25.0,520.0,28.0]}},
      {"box":{"id":"subtitle","maxclass":"comment","text":"LEFT: cell-periodic Re(u_nk)     RIGHT: complete Re[exp(ikx)u_nk]","fontsize":13.0,"patching_rect":[40.0,58.0,590.0,22.0]}},
      {"box":{"id":"instructions","maxclass":"comment","text":"Receives fixed reciprocal-spectrum specimens on UDP 7490. Start DSP, then run StartBlochSpectralMicroscope.command from the package folder.","linecount":2,"patching_rect":[40.0,92.0,650.0,42.0]}},
      {"box":{"id":"udp","maxclass":"newobj","text":"udpreceive 7490","numinlets":0,"numoutlets":1,"outlettype":["anything"],"patching_rect":[40.0,155.0,105.0,22.0]}},
      {"box":{"id":"route","maxclass":"newobj","text":"route /qmw/blochband/state","numinlets":2,"numoutlets":2,"patching_rect":[40.0,275.0,190.0,22.0]}},
      {"box":{"id":"converter","maxclass":"newobj","text":"js qmw_bloch_band_state_to_gen.js","numinlets":1,"numoutlets":1,"patching_rect":[40.0,315.0,220.0,22.0]}},
      {"box":{"id":"loadbang","maxclass":"newobj","text":"loadbang","numinlets":1,"numoutlets":1,"patching_rect":[340.0,155.0,60.0,22.0]}},
      {"box":{"id":"defaults","maxclass":"message","text":"amp 0.18, smoothms 80, cellfreq 92, carrier 720, energyscale 34, energyzero 1.5448614","numinlets":2,"numoutlets":1,"patching_rect":[340.0,195.0,465.0,22.0]}},
      {"box":{"id":"gen","maxclass":"newobj","text":"gen~ qmw_bloch_band_resonator","numinlets":1,"numoutlets":4,"outlettype":["signal","signal","signal","signal"],"patching_rect":[340.0,285.0,205.0,22.0]}},
      {"box":{"id":"outlabels","maxclass":"comment","text":"Gen outlets: Re(u), Im(u), Re(psi), Im(psi)","patching_rect":[340.0,315.0,300.0,22.0]}},
      {"box":{"id":"leftgain","maxclass":"newobj","text":"*~ 0.8","numinlets":2,"numoutlets":1,"outlettype":["signal"],"patching_rect":[340.0,355.0,48.0,22.0]}},
      {"box":{"id":"rightgain","maxclass":"newobj","text":"*~ 0.8","numinlets":2,"numoutlets":1,"outlettype":["signal"],"patching_rect":[495.0,355.0,48.0,22.0]}},
      {"box":{"id":"leftmeter","maxclass":"meter~","numinlets":1,"numoutlets":1,"patching_rect":[340.0,400.0,18.0,120.0]}},
      {"box":{"id":"rightmeter","maxclass":"meter~","numinlets":1,"numoutlets":1,"patching_rect":[525.0,400.0,18.0,120.0]}},
      {"box":{"id":"leftlabel","maxclass":"comment","text":"Re(u_nk)","patching_rect":[300.0,530.0,75.0,22.0]}},
      {"box":{"id":"rightlabel","maxclass":"comment","text":"Re(psi_nk)","patching_rect":[500.0,530.0,85.0,22.0]}},
      {"box":{"id":"dac","maxclass":"ezdac~","numinlets":2,"numoutlets":0,"patching_rect":[415.0,550.0,45.0,45.0]}},
      {"box":{"id":"note","maxclass":"comment","text":"Click the speaker to enable stereo monitoring. The World Clock/Spat patch provides the four-quadrature spatial version.","linecount":2,"patching_rect":[640.0,285.0,335.0,44.0]}}
    ],
    "lines": [
      {"patchline":{"source":["udp",0],"destination":["route",0]}},
      {"patchline":{"source":["route",0],"destination":["converter",0]}},
      {"patchline":{"source":["converter",0],"destination":["gen",0]}},
      {"patchline":{"source":["loadbang",0],"destination":["defaults",0]}},
      {"patchline":{"source":["defaults",0],"destination":["gen",0]}},
      {"patchline":{"source":["gen",0],"destination":["leftgain",0]}},
      {"patchline":{"source":["gen",2],"destination":["rightgain",0]}},
      {"patchline":{"source":["leftgain",0],"destination":["leftmeter",0]}},
      {"patchline":{"source":["rightgain",0],"destination":["rightmeter",0]}},
      {"patchline":{"source":["leftgain",0],"destination":["dac",0]}},
      {"patchline":{"source":["rightgain",0],"destination":["dac",1]}}
    ],
    "dependency_cache": [
      {"name":"qmw_bloch_band_resonator.gendsp","type":"gDSP"},
      {"name":"qmw_bloch_band_state_to_gen.js","type":"TEXT"}
    ],
    "autosave": 0
  }
}
