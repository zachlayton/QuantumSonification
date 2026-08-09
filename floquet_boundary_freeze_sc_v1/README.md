# Floquet Boundary Freeze v1

This SuperCollider prototype sonifies whether a symmetry-protected boundary
transfer pattern survives a perturbation. The signal path is deliberately not
an amplitude-to-pitch mapper:

1. An effective pair of hybridized boundary states generates left/right edge
   probabilities.
2. Filtered, envelope-shaped pink noise excites two matched resonator banks.
   Resonator index means distance inward from the corresponding boundary.
3. The phase vocoder freezes the resonator magnitudes while replacing source
   phase with deterministic broadband phase carriers.
4. FFT phase continues to accumulate. In pi mode it acquires exactly pi of
   additional phase per compressed Floquet drive period.
5. A symmetry-breaking perturbation detunes the boundary pair, suppressing
   transfer, and triggers relative-bin phase diffusion.
6. The boundary localization ratio generates a geometric scale
   `q = ratio^(-geometryExponent)`. The effective quasienergy splitting and
   Floquet drive phase select quantized degrees of that scale, giving the
   resonator bank a model-governed fundamental.

## Run

The simplest method is to double-click `StartFloquetBoundaryFreeze.command`
in Finder. This launches the complete instrument without selecting or
evaluating any SuperCollider code. Keep its Terminal window open while using
the instrument; press Control-C in that window to stop it completely.

Alternatively, open the source in SuperCollider:

Open `FloquetBoundaryFreezeV1.scd` in SuperCollider and evaluate the entire
outer parenthesized block. Click anywhere inside the file with no text
selected and press Command-Return. The default server boots and a control
window opens.

Begin by alternating these presets:

- **Protected A**: strong symmetry-preserving perturbation; the spatial and
  resonant pattern continues.
- **Broken B**: the same perturbation strength, now symmetry-breaking; edge
  transfer collapses and spectral phase coherence dissolves.
- **Trivial control**: removes the coherent boundary component and leaves a
  centered bulk-noise field.

The comparison, rather than any single sound, is the topological statement.

## Important controls

- **Boundary decay ratio** controls the exponential tail of the boundary
  shape. Smaller values are more sharply localized and also widen the
  model-derived geometric scale.
- **Fundamental anchor** sets only the register. The sounding fundamental is
  selected from the geometric scale by the effective model data.
- **Data pitch motion** controls how many nearby scale steps the compressed
  Floquet micromotion may traverse.
- **Boundary envelope contrast** makes the left/right edge probabilities more
  or less explicit without changing the underlying dynamics.
- **Floquet amplitude motion** applies opposite drive-phase breathing to the
  two edge envelopes.
- **Boundary phase winding** adds opposite coherent phase circulation to the
  two edges.
- **Spectral state** selects live magnitudes, a held frame, or automatic
  stroboscopic recapture.
- **Zero/Pi mode** enables the additional pi phase accumulated per drive
  period.
- **Broken-symmetry diffusion** controls how often a broken perturbation
  selects a new independent phase offset for every FFT bin.

Keep the output moderate for the first run; long-decay resonators can build
considerable energy even though the final signal is limited.
