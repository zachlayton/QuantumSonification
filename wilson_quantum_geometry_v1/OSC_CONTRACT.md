# Wilson CPS OSC contract v1

Prefix: `/qmw/wilson/cps`

The topology is sent once per publisher lifetime. Dynamic state uses a
strictly increasing revision. Receivers should collect all `vertex` messages
for a revision and commit them when `end` arrives.

## Static topology

### `/definition`

```text
revision grade factor_count factors_csv vertex_count fundamental_hz
```

### `/edge`

```text
revision source target interval_num interval_den
harmonic_distance harmonic_intersection coupling
```

`source` and `target` are CPS vertex indices. `coupling` is the v1
compositional weight `intersection / (1 + distance)`. Adjacency and perceptual
weight remain separate fields so a renderer may define a different musical
Hamiltonian.

## Dynamic state transaction

### `/frame`

```text
revision time dt shell_probability leakage_probability
conditional_shell_purity reference_vertex vertex_count
```

`reference_vertex` is `-1` when the shell is empty.

### `/vertex`

```text
revision vertex_index bitmask factors_csv ratio_num ratio_den frequency_hz
absolute_probability conditional_probability activation relative_phase
phase_coherence complement_vertex
```

- `absolute_probability` preserves population relative to the full register.
- `conditional_probability` is normalized only within the CPS shell.
- `activation` adds attack integration and post-release persistence; it is a
  renderer control, not a quantum probability.
- `relative_phase` is smoothed auditory phase memory.
- `phase_coherence` states whether density-matrix evidence supports that
  phase. It is zero for a diagonal mixture away from the reference vertex.
- `complement_vertex` is `-1` when the CPS is not self-mirroring.

### `/end`

```text
revision vertex_count
```

This is the transaction commit marker.

## Measurement event

### `/measurement`

```text
revision basis_index cps_vertex probability belongs_to_shell
```

`cps_vertex` is `-1` and `belongs_to_shell` is `0` when measurement lands in
another Hamming-weight sector. Measurement is kept separate from continuous
state publication so renderers do not mistake every update for collapse.

## Directed compositional flow

### `/flow`

```text
revision generation source_vertex destination_vertex source_basis destination_basis
absolute_flow conditional_flow theta beta relative_phase
```

This is an event lane, not another state description. The initial Phase 3
instrument uses it to articulate probability current between adjacent Hexany
vertices while the continuous `/vertex` activation field keeps sounding.
