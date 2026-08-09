# QAC → QuantumSonification Bridge v1

This bundle makes The QAC Toolkit's `och.microqiskit` object the Max-native
circuit-score layer for QuantumSonification. It is a new versioned integration;
it does not replace the existing QASM registry, circuit bridge, density engine,
Pauli synth, timing layer, or geometry engines.

## Signal path

```text
och.microqiskit
    ↓  sim get_qasm
qac_quantumsonification_sender_v1.maxpat
    ↓  OSC 127.0.0.1:7401
qac_quantumsonification_bridge_v1.py
    ↓  statevector → rho → Bloch / Pauli / MI / coherence
OSC 127.0.0.1:7400
    ↓
Max / Complex Pauli Synth / timing / geometry / convolution
```

The default is the canonical four-qubit system. `q0` is the least-significant
computational-basis bit, so basis labels are written `|q3 q2 q1 q0>`.

## Installation

1. Copy this folder into `/Users/zlayton/QuantumSonification/`.
2. In the existing `music` Conda environment:

   ```bash
   cd /Users/zlayton/QuantumSonification/qac_quantumsonification_bridge_v1
   python -m pip install -r requirements.txt
   ```

3. Put `max/qac_qasm_sender_v1.js` and
   `max/qac_quantumsonification_sender_v1.maxpat` somewhere in Max's search
   path, such as `/Users/zlayton/QuantumSonification/max/patches/`.
4. Install **The QAC Toolkit** from Max's Package Manager. On this machine it
   is already installed as version 1.0.4 at:

   ```text
   /Users/zlayton/Documents/Max 9/Packages/The QAC Toolkit
   ```

   Max 9 discovers the package automatically; do not copy its externals into
   this bridge.

## First test

Start the Python bridge:

```bash
conda activate music
cd /Users/zlayton/QuantumSonification
python -m qac_quantumsonification_bridge_v1.qac_quantumsonification_bridge_v1
```

To reseed the canonical resonator whenever QAC exports an accepted circuit:

```bash
python -m qac_quantumsonification_bridge_v1.qac_quantumsonification_bridge_v1 \
  --engine-control-host 127.0.0.1 \
  --engine-control-port 7402
```

The `presets/resonator_full.json` conductor preset supplies these options and
launches the bridge automatically.

It should print:

```text
OSC in:   127.0.0.1:7401
OSC out:  127.0.0.1:7400
qubits:   4
ordering: |q3 q2 q1 q0> (q0 is LSB)
```

In Max:

1. Open `max/qac_quantumsonification_qac_demo_v1.maxpat`. It instantiates
   `och.microqiskit qc 4 4 sim 1024 1`, creates a Bell circuit, and connects
   the QAC object's outlet directly to the sender abstraction.
2. Click **1. reset/create Bell circuit**.
3. Click **2. sim get_qasm**.
4. For your own patch, connect the outlet of `och.microqiskit` to the inlet of
   `qac_quantumsonification_sender_v1.maxpat` and send `sim get_qasm`.
5. Receive the enriched result with:

   ```text
   [udpreceive 7400]
   |
   [oscparse]
   |
   [route list]
   |
   [route qmw]
   |
   [route qac]
   ```

   Or open `max/qac_quantumsonification_monitor_v1.maxpat`; it prints every
   `/qmw/qac/*` result to the Max Console for the first connection test.

The sender automatically URL-encodes and chunks QASM so spaces, line breaks,
commas, and long circuits survive Max/OSC transport. Every transmission gets a
monotonically increasing revision number. The Python side rejects stale results.
Only `qasm`, explicit `append`, or messages beginning with `OPENQASM` modify the
sender buffer; QAC statevector, counts, memory, and other outlet messages are
ignored so they cannot contaminate a later circuit transmission.
The sender initializes its revision from Unix time, preventing a Max patch
reload from restarting at revision 1 while a long-running bridge retains a
newer accepted revision.

The Max sender uses odot with one complete address per packer—`o.pack
/qmw/qac/begin`, `/qmw/qac/chunk`, and `/qmw/qac/end`—then the standard
`udpsend`. Splitting an address into multiple `o.pack` arguments creates
separate bundle fields and will not match the Python bridge routes.

The final constructor argument `1` enables QAC's simulator auto-update mode.
Without it, recreate the simulator after changing `qc`, or the simulator may
export the earlier circuit snapshot. QAC 1.0.4 documents QASM as a printed or
textbox representation and exposes a general outlet; the supplied sender
accepts either a `qasm <text>` message, a message beginning with `OPENQASM`, or
line-oriented output. If a future QAC build changes its QASM outlet behavior,
the sender also accepts pasted QASM via `qasm <complete text>`.

## Bell-state circuit

The included `example_qac_bell_4q.qasm` applies:

```text
H q0 → CX q0,q1
```

For a matching QAC circuit, expect approximately:

```text
/qmw/qac/probabilities       0.5 0 0 0.5 0 ...
/qmw/qac/qubit/0/bloch       0 0 0
/qmw/qac/qubit/1/bloch       0 0 0
/qmw/qac/qubit/2/bloch       0 0 1
/qmw/qac/qubit/3/bloch       0 0 1
/qmw/qac/mi/01               2.0
/qmw/qac/pauli/IIXX          1.0
/qmw/qac/pauli/IIZZ          1.0
/qmw/qac/global/purity       1.0
```

## OSC input

| Address | Arguments | Purpose |
|---|---|---|
| `/qmw/qac/begin` | `revision total_chunks` | Begin atomic transfer |
| `/qmw/qac/chunk` | `revision index total encoded_text` | Add one QASM chunk |
| `/qmw/qac/end` | `revision` | Validate, simulate, and publish |
| `/qmw/qac/qasm` | `[revision] qasm_text` | Direct short-message path |
| `/qmw/qac/run` | none | Republish current frame |
| `/qmw/qac/clear` | none | Clear bridge state |
| `/qmw/qac/shots` | integer | Change deterministic sampling count |
| `/qmw/qac/ping` | none | Request status |

## OSC output

| Address family | Payload |
|---|---|
| `/qmw/qac/statevector/{real,imag}` | 16-value lists |
| `/qmw/qac/probabilities` | 16-value list |
| `/qmw/qac/rho/{real,imag}` | flattened 256-value lists |
| `/qmw/qac/qubit/<q>/bloch` | `x y z` |
| `/qmw/qac/qubit/<q>/entropy` | single-qubit entropy |
| `/qmw/qac/mi/<pair>` | six pairwise mutual informations |
| `/qmw/qac/pauli/<TERM>` | 34 Pauli expectation values |
| `/qmw/qac/global/{purity,entropy,coherence_l1}` | global state descriptors |
| `/qmw/qac/dominant` | `index bitstring probability` |
| `/qmw/qac/counts` | alternating `bitstring count` atoms |
| `/qmw/qac/accepted` | `revision qubits operations measurements` |
| `/qmw/qac/error` | validation or execution error text |
| `/qmw/circuit/euler/{begin,gate,end}` | Atomic verified one-qubit ZXZ decompositions |

The 34 Pauli terms are identity, twelve local axes, eighteen same-axis pair
correlations, and the three global strings `XXXX`, `YYYY`, and `ZZZZ`.

Every accepted circuit also decomposes each numeric one-qubit instruction into
`theta phi lambda gamma`, independently reconstructs its 2×2 matrix, and sends
the shared Euler transaction. Multi-qubit gates and measurements remain
explicit skipped records in offline JSON. Use `--no-euler` to disable this or
`--euler-mirror-host 127.0.0.1 --euler-mirror-port 7497` to drive the
Processing Euler lens.

## QASM support in v1

The built-in simulator accepts flattened OpenQASM 2 and OpenQASM 3 containing:

- `id`, `x`, `y`, `z`, `h`, `s`, `sdg`, `t`, `tdg`, `sx`
- `rx`, `ry`, `rz`, `p`/`u1`, `u`/`u3`
- `cx`/`cnot`, `cy`, `cz`, `ch`, `swap`, `ccx`/`toffoli`
- barriers and final measurements

It intentionally rejects custom gate bodies, mid-circuit reset, and OpenQASM 3
control-flow blocks. Those require the later density-matrix/Qiskit execution
backend because they are not pure unitary statevector operations. The rejection
is explicit; the bridge never silently approximates them.

QAC-specific open-control gates (`ox`, `oh`, `oox`, `ocx`, `ooh`, `och`),
`crx`, `cccx`, `initialize`, and experimental `matrix` operations are outside
this v1 parser. QAC's own documentation also notes incomplete QASM translation
for multi-qubit `matrix` gates. Use the listed standard gate family for this
bridge; unsupported exported operations fail explicitly at validation.

## Offline validation

Run the included tests without Max or `python-osc`:

```bash
python -m unittest discover -s tests -v
```

Analyze a QASM file and write the complete material frame as JSON:

```bash
python qac_quantumsonification_bridge_v1.py \
  --qasm example_qac_bell_4q.qasm \
  --json-out example_qac_bell_4q_analysis.json
```

## Canonical resonator density injection

The `/qmw/qac/pauli/<TERM>` outputs can feed the existing Complex Pauli Synth,
while the accepted density can now seed the canonical resonator directly.
With `--engine-control-host` enabled, publication also sends:

```text
/qmw/state/begin     revision 4 q0_lsb
/qmw/state/rho/real  revision <256 floats>
/qmw/state/rho/imag  revision <256 floats>
/qmw/state/commit    revision
```

The resonator accepts only complete, newer, finite, Hermitian,
positive-semidefinite, trace-one matrices. It reverses QAC's q0-LSB tensor
axes into the existing engine's q0-most-significant-axis convention, then
swaps the density between evolution steps. Success appears on
`/qmw/state/committed`; rejection appears on `/qmw/state/error`.
