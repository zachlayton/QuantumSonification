# Quantum Graph Canon v1

This experiment connects the repository's NetworkX score research to its
four-qubit density-matrix notation system:

```text
96-node quartic-torus score graph
  -> recursive Kernighan-Lin four-region quotient
  -> four graph-conditioned qubits
  -> cumulative Qiskit circuit snapshots
  -> 16 x 16 density matrices
  -> existing 32-voice bra-ket cable-net canon
  -> MusicXML
```

## Encoding

Each quotient node becomes one qubit. Its aggregate graph features control
local rotations:

- graph-Laplacian eigenfield -> `RY`
- pitch and geometric position -> `RZ`
- onset and source degree -> `RX`

Every quotient edge becomes an `RZZ` interaction. Its angle is proportional to
the summed coupling of source-graph edges crossing between the two regions.

The local control uses exactly the same graph, rotations, partition, number of
layers, and explicit dephasing, but omits `RZZ`. It is therefore an appropriate
control for testing what the entangling layer changes musically.

## Generate

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 --mode both
```

The default output directory contains one MusicXML score and one JSON research
manifest for each mode. The manifest records the partition, rotations,
entangling angles, circuit depths, operation counts, density metrics, and score
event counts.

Useful controls:

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 \
  --mode entangled --layers 6 --entanglement-scale 0.6 --dephasing 0.18
```

## Optional SamplerQNN conditioning

The QNN integration retains all 16 four-bit activation masks rather than
collapsing them to parity. Bit `q` describes quotient region/qubit `q`.

```text
four encoded quotient regions
  -> topology-preserving ZZFeatureMap
  -> topology-preserving RealAmplitudes
  -> SamplerQNN distribution over masks 0..15
  -> four activation marginals
  -> conditioned local rotations and RZZ interactions
  -> density canon and MusicXML
```

Both the feature map and the ansatz use the actual NetworkX quotient edge list.
The default hybrid input compresses each region's eigenfield, onset, pitch, and
geometric position into one bounded feature-map angle.

Generate the optional QNN-conditioned study:

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 --mode qnn
```

The default weights are a reproducible small random initialization and are
explicitly recorded as `seeded_untrained`. This is an integration test and
generative condition, not a learned model. A later trainer can supply weights:

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 \
  --mode qnn --qnn-weights path/to/weights.json
```

The JSON may be a list of weights or an object containing a `weights` list.
Run `--mode all` to generate the base and QNN-conditioned studies together.

## Direct density-matrix audio

The QNN-conditioned density snapshots can also be synthesized directly, with
no MIDI rendering stage:

```text
four evolving 16 x 16 density matrices
  -> row i becomes computational-basis voice i
  -> all 16 complex row entries become harmonics 1..16
  -> one phase-aware 256-point wavetable per row
  -> 16 continuously running, stereo-positioned oscillators
  -> 16-bit stereo PCM WAV
```

For voice `i`, density entry `rho[i,j]` maps to harmonic
`((j - i) mod 16) + 1`. This places the real diagonal population on the
fundamental and retains off-diagonal coherence magnitude and phase in the
higher harmonics. Row energy controls relative amplitude; signed coherence
phase produces a bounded microtonal pitch bend. The four density snapshots are
interpolated continuously while oscillator phases remain continuous.

Generate the default 16-second, 48 kHz render and its JSON manifest:

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 --mode wav
```

Useful audio controls:

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 \
  --mode wav --wav-duration 24 --wav-base-frequency 41.2 \
  --wav-control-rate 80 --wav-output-ceiling 0.8
```

The bank dimensions are deliberately fixed at 16 voices and 256 samples per
wavetable.

### Articulated composition

The continuously running bank is useful as a reference sonification, but its
density evolution is heard mainly as slow timbral change. The articulated
version retains the same wavetables while introducing density-derived musical
events:

- diagonal population and row energy determine attack likelihood and strength;
- coherence magnitude controls note length and additional subdivisions;
- coherence phase controls wavetable phase, vibrato, and microtonal bend;
- NetworkX shortest-path distance from each basis state to the QNN-selected
  mask generates staggered canon entrances;
- the four density matrices are held as distinct sections, with short smooth
  transitions and progressively greater activity as coherence increases.

Generate the default 24-second articulated render:

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 \
  --mode wav-articulated
```

Tempo and duration can be changed independently:

```bash
python -m quantum_graph_canon_v1.quantum_graph_canon_v1 \
  --mode wav-articulated --wav-tempo 76 --wav-duration 32
```

`--mode all` includes both the continuous reference WAV and articulated WAV,
as well as the notation studies.

## Scientific boundary

V1 uses exact Qiskit statevector evolution followed by an explicitly declared
population-dephasing mixture. It does **not** claim that the density matrix came
from quantum hardware. Hardware execution will require either state tomography
or a new score mapping based on measured Pauli observables.

## Test

```bash
python -m unittest quantum_graph_canon_v1.test_quantum_graph_canon_v1 -v
python -m unittest quantum_graph_canon_v1.test_qnn_integration -v
python -m unittest quantum_graph_canon_v1.test_wavetable_audio -v
```
