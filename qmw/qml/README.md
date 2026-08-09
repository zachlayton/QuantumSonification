# QMW Qiskit Machine Learning adapter

This package turns the existing QMW `QuantumStateFrame` stream into learned,
named sonic/material regimes. It uses the current 22-value
`QuantumDescriptorExtractor`, selects four bounded descriptors, encodes them
as angles, and trains a Qiskit `QSVC` with an exact
`FidelityStatevectorKernel`.

By default, confidence values are normalized QSVC decision weights: fast and
useful for control interpolation, but not statistically calibrated. Construct
the classifier with `probability=True` when calibrated libsvm probabilities
are worth the additional training cost.

The default QML features are:

- `coherence_l1` — off-diagonal coherence;
- `participation` — population spread across basis states;
- `mean_spin_length` — local-state focus versus mixing/entanglement;
- `pair_abs_mean` — mean two-qubit correlation strength.

Qiskit Machine Learning remains optional. Core engines, state buses, and OSC
routes import normally without it.

## Install and run

Use the same Python environment as the QMW engine:

```bash
python -m pip install -r qmw/qml/requirements.txt
python examples/qml_material_regimes.py
```

Save a reusable model and optionally send the demonstration prediction to Max:

```bash
python examples/qml_material_regimes.py --model models/qmw_material_qsvc.dill
python examples/qml_material_regimes.py --osc --port 7400
```

## Attach to the QMW state bus

Train from labeled rehearsal frames, then subscribe the classifier to the
continuous state stream. Rate division is important because a quantum-kernel
decision is a control-rate operation rather than an audio-rate operation.

```python
from qmw.qml import (
    QMLMaterialOSCSender,
    QMLStateSubscriber,
    QuantumKernelMaterialClassifier,
)

classifier = QuantumKernelMaterialClassifier().fit_frames(
    rehearsal_frames,
    rehearsal_labels,
)
subscriber = QMLStateSubscriber(
    classifier,
    osc_sender=QMLMaterialOSCSender(port=7400),
    every_n_frames=8,
)
quantum_data_bus.state_bus.subscribe(subscriber)
```

The adapter publishes:

- `/qmw/qml/regime` — `[time, label, confidence]`;
- `/qmw/qml/probabilities` — `[time, label_0, p_0, ...]`;
- `/qmw/qml/features` — `[time, coherence, participation, spin_length, pair_correlation]`.

Labels are intentionally supplied by the project rather than imposed by the
library. They can describe orchestration states (`sparse`, `granular`,
`resonant`), physical regimes (`localized`, `coherent`, `entangled`), or
scene-level controls.

## Load a trained model

```python
classifier = QuantumKernelMaterialClassifier.load(
    "models/qmw_material_qsvc.dill"
)
prediction = classifier.predict_frame(frame)
```

The `.dill.json` sidecar stores the QMW feature projection and versioned schema.
