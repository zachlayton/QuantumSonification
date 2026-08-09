{
  "patcher": {
    "fileversion":1,
    "appversion":{"major":9,"minor":0,"revision":0,"architecture":"x64","modernui":1},
    "classnamespace":"box",
    "rect":[90.0,70.0,1320.0,820.0],
    "boxes":[
      {"box":{"id":"title","maxclass":"comment","text":"PAULI–BLOCH WORLD CLOCK / COMPLEX SPATIAL MICROSCOPE v1","fontsize":19.0,"fontface":1,"patching_rect":[40.0,25.0,760.0,30.0]}},
      {"box":{"id":"subtitle","maxclass":"comment","text":"Re(psi): east–west    Im(psi): north–south    compressed temporal phase: orbit","fontsize":13.0,"patching_rect":[40.0,60.0,820.0,22.0]}},
      {"box":{"id":"udp","maxclass":"newobj","text":"udpreceive 7490","numinlets":0,"numoutlets":1,"outlettype":["anything"],"patching_rect":[40.0,125.0,105.0,22.0]}},
      {"box":{"id":"route","maxclass":"newobj","text":"route /qmw/blochband/state","numinlets":2,"numoutlets":2,"patching_rect":[40.0,245.0,190.0,22.0]}},
      {"box":{"id":"fork","maxclass":"newobj","text":"t l l","numinlets":1,"numoutlets":2,"patching_rect":[40.0,285.0,42.0,22.0]}},
      {"box":{"id":"converter","maxclass":"newobj","text":"js qmw_bloch_band_state_to_gen.js","numinlets":1,"numoutlets":1,"patching_rect":[40.0,325.0,220.0,22.0]}},
      {"box":{"id":"statehead","maxclass":"newobj","text":"zl slice 2","numinlets":2,"numoutlets":2,"patching_rect":[275.0,325.0,62.0,22.0]}},
      {"box":{"id":"loadbang","maxclass":"newobj","text":"loadbang","patching_rect":[370.0,125.0,60.0,22.0]}},
      {"box":{"id":"defaults","maxclass":"message","text":"amp 0.18, smoothms 80, cellfreq 92, carrier 720, energyscale 34, energyzero 1.5448614","patching_rect":[370.0,165.0,465.0,22.0]}},
      {"box":{"id":"gen","maxclass":"newobj","text":"gen~ qmw_bloch_band_resonator","numinlets":1,"numoutlets":4,"outlettype":["signal","signal","signal","signal"],"patching_rect":[370.0,245.0,205.0,22.0]}},
      {"box":{"id":"genlabel","maxclass":"comment","text":"1 Re(u)   2 Im(u)   3 Re(psi)   4 Im(psi)","patching_rect":[370.0,275.0,300.0,22.0]}},
      {"box":{"id":"hilbert","maxclass":"newobj","text":"hilbert~","numinlets":1,"numoutlets":2,"outlettype":["signal","signal"],"patching_rect":[700.0,245.0,65.0,22.0]}},
      {"box":{"id":"hilbertconj","maxclass":"newobj","text":"*~ -1.","numinlets":2,"numoutlets":1,"outlettype":["signal"],"patching_rect":[785.0,275.0,50.0,22.0]}},
      {"box":{"id":"mode","maxclass":"toggle","patching_rect":[700.0,130.0,24.0,24.0]}},
      {"box":{"id":"modeplus","maxclass":"newobj","text":"+ 1","patching_rect":[735.0,132.0,35.0,22.0]}},
      {"box":{"id":"modeload","maxclass":"newobj","text":"loadmess 0","patching_rect":[790.0,132.0,72.0,22.0]}},
      {"box":{"id":"modelabel","maxclass":"comment","text":"OFF: native complex Gen    ON: conjugated hilbert~ reconstruction","patching_rect":[885.0,130.0,400.0,22.0]}},
      {"box":{"id":"iselect","maxclass":"newobj","text":"selector~ 2","numinlets":3,"numoutlets":1,"outlettype":["signal"],"patching_rect":[650.0,330.0,78.0,22.0]}},
      {"box":{"id":"qselect","maxclass":"newobj","text":"selector~ 2","numinlets":3,"numoutlets":1,"outlettype":["signal"],"patching_rect":[760.0,330.0,78.0,22.0]}},
      {"box":{"id":"ilabel","maxclass":"comment","text":"I / real","patching_rect":[650.0,365.0,80.0,20.0]}},
      {"box":{"id":"qlabel","maxclass":"comment","text":"Q / imaginary","patching_rect":[760.0,365.0,110.0,20.0]}},
      {"box":{"id":"spat","maxclass":"newobj","text":"qmw_bloch_complex_spat5_hoa3~","numinlets":4,"numoutlets":16,"outlettype":["signal","signal","signal","signal","signal","signal","signal","signal","signal","signal","signal","signal","signal","signal","signal","signal"],"patching_rect":[650.0,440.0,245.0,22.0]}},
      {"box":{"id":"dac","maxclass":"newobj","text":"dac~ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16","numinlets":16,"numoutlets":0,"patching_rect":[650.0,555.0,330.0,22.0]}},
      {"box":{"id":"hoa","maxclass":"comment","text":"Third-order HOA: ACN / SN3D. Decode downstream for the room.","patching_rect":[650.0,590.0,430.0,22.0]}},
      {"box":{"id":"instructions","maxclass":"comment","text":"Keep all files together. Enable DSP, then run the package's location-independent StartBlochSpectralMicroscope.command launcher.","linecount":3,"patching_rect":[40.0,410.0,560.0,58.0]}},
      {"box":{"id":"mapping","maxclass":"comment","text":"SPATIAL FIELD\n\nEast / West: +I / -I\nNorth / South: +Q / -Q\nOrbit: 0.32(I+Q)\nDirection: clockwise, matching exp(-iEt/hbar)\nSpeed: compressed relative energy\nOffset: 180q degrees","linecount":9,"patching_rect":[40.0,505.0,390.0,170.0]}},
      {"box":{"id":"warning","maxclass":"comment","text":"The orbit is a perceptual time-scale projection; the complex quadratures remain sample-accurate.","patching_rect":[40.0,700.0,600.0,22.0]}}
    ],
    "lines":[
      {"patchline":{"source":["udp",0],"destination":["route",0]}},{"patchline":{"source":["route",0],"destination":["fork",0]}},{"patchline":{"source":["fork",0],"destination":["converter",0]}},{"patchline":{"source":["fork",1],"destination":["statehead",0]}},{"patchline":{"source":["statehead",0],"destination":["spat",2]}},{"patchline":{"source":["converter",0],"destination":["gen",0]}},
      {"patchline":{"source":["loadbang",0],"destination":["defaults",0]}},{"patchline":{"source":["defaults",0],"destination":["gen",0]}},
      {"patchline":{"source":["gen",2],"destination":["hilbert",0]}},{"patchline":{"source":["gen",2],"destination":["iselect",1]}},{"patchline":{"source":["gen",3],"destination":["qselect",1]}},{"patchline":{"source":["hilbert",0],"destination":["iselect",2]}},{"patchline":{"source":["hilbert",1],"destination":["hilbertconj",0]}},{"patchline":{"source":["hilbertconj",0],"destination":["qselect",2]}},
      {"patchline":{"source":["modeload",0],"destination":["mode",0]}},{"patchline":{"source":["mode",0],"destination":["modeplus",0]}},{"patchline":{"source":["modeplus",0],"destination":["iselect",0]}},{"patchline":{"source":["modeplus",0],"destination":["qselect",0]}},{"patchline":{"source":["iselect",0],"destination":["spat",0]}},{"patchline":{"source":["qselect",0],"destination":["spat",1]}},
      {"patchline":{"source":["spat",0],"destination":["dac",0]}},{"patchline":{"source":["spat",1],"destination":["dac",1]}},{"patchline":{"source":["spat",2],"destination":["dac",2]}},{"patchline":{"source":["spat",3],"destination":["dac",3]}},{"patchline":{"source":["spat",4],"destination":["dac",4]}},{"patchline":{"source":["spat",5],"destination":["dac",5]}},{"patchline":{"source":["spat",6],"destination":["dac",6]}},{"patchline":{"source":["spat",7],"destination":["dac",7]}},{"patchline":{"source":["spat",8],"destination":["dac",8]}},{"patchline":{"source":["spat",9],"destination":["dac",9]}},{"patchline":{"source":["spat",10],"destination":["dac",10]}},{"patchline":{"source":["spat",11],"destination":["dac",11]}},{"patchline":{"source":["spat",12],"destination":["dac",12]}},{"patchline":{"source":["spat",13],"destination":["dac",13]}},{"patchline":{"source":["spat",14],"destination":["dac",14]}},{"patchline":{"source":["spat",15],"destination":["dac",15]}}
    ],
    "dependency_cache":[
      {"name":"qmw_bloch_band_resonator.gendsp","type":"gDSP"},
      {"name":"qmw_bloch_band_state_to_gen.js","type":"TEXT"},
      {"name":"qmw_bloch_complex_spat5_hoa3~.maxpat","type":"JSON"},
      {"name":"spat5.oper.mxo","type":"iLaX"},{"name":"spat5.spat~.mxo","type":"iLaX"}
    ],
    "autosave":0
  }
}
