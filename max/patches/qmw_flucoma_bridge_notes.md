# QMW FluCoMa Bridge

Open `qmw_flucoma_quantum_router.maxpat` in Max while `quantum_population_osc_v7.py` is running.

The Python oscilloscope now publishes a normalized FluCoMa namespace on UDP 7400:

- `/qmw/flucoma/cursor x y`
- `/qmw/flucoma/depth value`
- `/qmw/flucoma/stability value`
- `/qmw/flucoma/scatter value`
- `/qmw/flucoma/rate value`
- `/qmw/flucoma/q0/cursor x y`
- `/qmw/flucoma/q0/depth value`
- `/qmw/flucoma/q0/purity value`
- `/qmw/flucoma/q0/entropy value`
- `/qmw/flucoma/q0/speed value`
- `/qmw/flucoma/q0/raw_bloch x y z`

The same per-qubit addresses are emitted for `q1`, `q2`, and `q3`.

Suggested first mappings:

- `qmw.flucoma.cursor` -> 2D nearest-neighbour query into a `fluid.kdtree~` fitted to a PCA/UMAP corpus map.
- `qmw.flucoma.depth` -> brightness, spectral tilt, or forward/reverse bias.
- `qmw.flucoma.stability` -> stable/clean sample selection.
- `qmw.flucoma.scatter` -> search radius, randomness, or slice variety.
- `qmw.flucoma.rate` -> trigger density, grain rate, or interpolation speed.

FluCoMa workflow sketch:

1. Analyze a folder of buffers with `fluid.bufmfcc~`, `fluid.spectralshape~`, `fluid.loudness~`, or similar.
2. Store descriptors in a `fluid.dataset~`.
3. Reduce descriptors to 2D with `fluid.pca~` or `fluid.umap~`.
4. Fit `fluid.kdtree~` to the 2D dataset.
5. Query the tree with the quantum cursor.
6. Use the nearest identifier to choose a buffer/slice for playback.
