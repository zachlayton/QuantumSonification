# Geometric optimization OSC contract v1

Default destination: UDP `17430`. Root: `/qmw/geometric_opt`.

The problem topology is transactional:

```text
/problem/begin   revision vertex_count edge_count
/problem/vertex  revision index bitmask label complement ratio cents cut energy
/problem/edge    revision edge_index source target
/problem/end     revision
```

Every optimizer state is another complete transaction:

```text
/frame/begin           revision optimizer step
/frame/theta           revision optimizer step theta...
/frame/summary         revision optimizer step objective_before objective_after
                       expected_cut approximation optimal_mass entropy
                       participation phase_order geodesic_step cumulative_geodesic
                       shell_leakage gradient_norm model_evaluations
/frame/probe/begin     revision optimizer step probe delta...
/frame/probe/plus      revision optimizer step probe objective_plus
/frame/probe/minus     revision optimizer step probe objective_minus
/frame/probe/gradient  revision optimizer step probe gradient...
/frame/probe/end       revision optimizer step probe plus_minus_difference
/frame/vertex          revision optimizer step vertex probability phase
/frame/edge            revision optimizer step edge source target current
/frame/feedback        revision optimizer step energy centroid flux balance resonance
/frame/controls        revision optimizer step source_feedback_step epsilon batch lr polarity
/frame/end             revision optimizer step
```

`feedback` and `controls` occur only on the acoustic-feedback trace. Controls
on step `n` name source feedback step `n-1`. Geometry and audio clients should
stage data after `begin` and commit only after the matching `end`.
