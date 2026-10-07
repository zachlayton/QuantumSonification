{
  "patcher": {
    "fileversion": 1,
    "appversion": {"major": 9, "minor": 0, "revision": 0, "architecture": "x64", "modernui": 1},
    "classnamespace": "box",
    "rect": [80.0, 80.0, 1220.0, 720.0],
    "boxes": [
      {"box": {"id": "title", "maxclass": "comment", "text": "QMW Native v0.1 — seventeen-object instantiation catalog", "fontsize": 20.0, "patching_rect": [35.0, 25.0, 650.0, 30.0]}},
      {"box": {"id": "note", "maxclass": "comment", "text": "This patch is a class-loading smoke surface, not a connected instrument. Open the Max Console and confirm that no object box is red.", "patching_rect": [35.0, 62.0, 1000.0, 24.0]}},
      {"box": {"id": "message_title", "maxclass": "comment", "text": "MESSAGE-RATE PHYSICS AND ANALYSIS", "fontsize": 14.0, "patching_rect": [45.0, 115.0, 340.0, 22.0]}},
      {"box": {"id": "state", "maxclass": "newobj", "text": "qmw.state 1", "patching_rect": [55.0, 160.0, 120.0, 22.0]}},
      {"box": {"id": "hamiltonian", "maxclass": "newobj", "text": "qmw.hamiltonian 1 model_energy computational_q0_lsb catalog_source catalog_provenance", "patching_rect": [215.0, 160.0, 570.0, 22.0]}},
      {"box": {"id": "evolve", "maxclass": "newobj", "text": "qmw.evolve 1 model_energy", "patching_rect": [825.0, 160.0, 190.0, 22.0]}},
      {"box": {"id": "observe", "maxclass": "newobj", "text": "qmw.observe Z 0 1", "patching_rect": [55.0, 215.0, 150.0, 22.0]}},
      {"box": {"id": "uncertainty", "maxclass": "newobj", "text": "qmw.uncertainty 1", "patching_rect": [245.0, 215.0, 150.0, 22.0]}},
      {"box": {"id": "transition", "maxclass": "newobj", "text": "qmw.transition 1", "patching_rect": [435.0, 215.0, 145.0, 22.0]}},
      {"box": {"id": "measure", "maxclass": "newobj", "text": "qmw.measure Z 1 29 computational_q0_lsb catalog_state catalog_state_provenance catalog_measurement catalog_measurement_provenance", "patching_rect": [620.0, 215.0, 570.0, 22.0]}},
      {"box": {"id": "spectrum", "maxclass": "newobj", "text": "qmw.spectrum 1", "patching_rect": [55.0, 270.0, 135.0, 22.0]}},
      {"box": {"id": "qmm", "maxclass": "newobj", "text": "qmw.qmm 1", "patching_rect": [230.0, 270.0, 110.0, 22.0]}},
      {"box": {"id": "flow", "maxclass": "newobj", "text": "qmw.flow 1", "patching_rect": [380.0, 270.0, 110.0, 22.0]}},
      {"box": {"id": "pauli", "maxclass": "newobj", "text": "qmw.pauli 2 computational_q0_lsb catalog_pauli catalog_provenance", "patching_rect": [530.0, 270.0, 420.0, 22.0]}},

      {"box": {"id": "signal_title", "maxclass": "comment", "text": "SIGNAL-RATE SYNTHESIS AND MEMORY", "fontsize": 14.0, "patching_rect": [45.0, 355.0, 340.0, 22.0]}},
      {"box": {"id": "resonator", "maxclass": "newobj", "text": "qmw.resonator~ 440 1. 0.2", "patching_rect": [55.0, 405.0, 205.0, 22.0]}},
      {"box": {"id": "interference", "maxclass": "newobj", "text": "qmw.interference~ 2 0.5", "patching_rect": [300.0, 405.0, 185.0, 22.0]}},
      {"box": {"id": "excite", "maxclass": "newobj", "text": "qmw.excite~", "patching_rect": [525.0, 405.0, 110.0, 22.0]}},
      {"box": {"id": "lorentz", "maxclass": "newobj", "text": "qmw.lorentz~ model_charge model_E model_velocity model_B model_force catalog_source catalog_provenance", "patching_rect": [675.0, 405.0, 500.0, 22.0]}},
      {"box": {"id": "memory", "maxclass": "newobj", "text": "qmw.memory~ 48000 1200 1208", "patching_rect": [55.0, 465.0, 220.0, 22.0]}},
      {"box": {"id": "modalbank", "maxclass": "newobj", "text": "qmw.modalbank~ 0.8", "patching_rect": [315.0, 465.0, 165.0, 22.0]}},

      {"box": {"id": "boundary", "maxclass": "comment", "text": "DSP objects never mutate rho. Measurement emits a posterior candidate only. Diagnostic activity is not a physical rate. Live audio/listening acceptance is separate.", "fontsize": 13.0, "patching_rect": [120.0, 570.0, 980.0, 40.0]}},
      {"box": {"id": "docs", "maxclass": "comment", "text": "See docs/OBJECT_CATALOG.md and the package validation record for ownership, equations, tests, and unverified boundaries.", "patching_rect": [190.0, 630.0, 820.0, 24.0]}}
    ],
    "lines": []
  }
}
