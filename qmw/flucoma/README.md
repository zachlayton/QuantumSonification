# QMW FluCoMa-Inspired Python Layer

This package mirrors the useful parts of the FluCoMa workflow inside Python:

1. Analyze state into a numeric descriptor vector.
2. Standardize descriptor data.
3. Project descriptor history into a 2D map.
4. Search for nearest neighbours in a corpus.
5. Translate quantum descriptors into an audio-feature query vector.

Core pieces:

- `QuantumDescriptorExtractor`: converts a `QuantumStateFrame` into a stable descriptor vector.
- `DescriptorCorpus`: in-process DataSet / Standardize / PCA / KDTree-style memory.
- `audio_descriptor_vector`: analyzes an audio file into a FluCoMa-like feature vector.
- `build_audio_corpus`: analyzes a folder of audio files into a searchable corpus.
- `quantum_descriptor_to_audio_query`: maps quantum behavior into the audio feature space.
- `density_matrix_to_mosaic_tiles`: treats a density matrix as a 16x16 audio-mosaicing target.
- `density_matrix_to_activation_sequences`: finds sparse diagonal activation runs.
- `density_mosaic_explanation`: explains why the current tiles/sequences were selected.

The oscilloscope publishes this over OSC through `FluCoMaView`:

- `/qmw/flucoma/projection x y`
- `/qmw/flucoma/novelty value`
- `/qmw/flucoma/corpus/size value`
- `/qmw/flucoma/nearest/id symbol`
- `/qmw/flucoma/nearest/distance value`
- `/qmw/flucoma/descriptor/values ...`
- `/qmw/flucoma/descriptor/names ...`
- `/qmw/flucoma/audio_query/values ...`
- `/qmw/flucoma/audio_query/names ...`
- `/qmw/flucoma/mosaic/count value`
- `/qmw/flucoma/mosaic/summary ...`
- `/qmw/flucoma/mosaic/explanation symbol`
- `/qmw/flucoma/mosaic/tile/N/cell row column`
- `/qmw/flucoma/mosaic/tile/N/role symbol`
- `/qmw/flucoma/mosaic/tile/N/reason_codes ...`
- `/qmw/flucoma/mosaic/tile/N/explanation symbol`
- `/qmw/flucoma/mosaic/tile/N/salience value`
- `/qmw/flucoma/mosaic/tile/N/audio_query ...`
- `/qmw/flucoma/mosaic/sequence/count value`
- `/qmw/flucoma/mosaic/sequence/summary ...`
- `/qmw/flucoma/mosaic/sequence/N/start row column`
- `/qmw/flucoma/mosaic/sequence/N/end row column`
- `/qmw/flucoma/mosaic/sequence/N/length value`
- `/qmw/flucoma/mosaic/sequence/N/continuity value`
- `/qmw/flucoma/mosaic/sequence/N/role symbol`
- `/qmw/flucoma/mosaic/sequence/N/reason_codes ...`
- `/qmw/flucoma/mosaic/sequence/N/explanation symbol`
- `/qmw/flucoma/mosaic/sequence/N/audio_query ...`

Density Mosaic

The density-matrix mosaic layer interprets each matrix cell as a target tile:

- diagonal cells: stable probability anchors
- off-diagonal cells: coherence / transition / phase targets
- amplitude: how strongly the tile should be heard
- phase: spectral color / skew / directional bias
- basis distance: how far the tile moves through computational basis space
- salience: priority for nearest-neighbour audio matching

For a 4-qubit engine, the 16x16 density matrix can drive up to 256 possible
tiles. The OSC view sends the most salient 16 by default.

Activation Sequences

The activation-sequence layer follows the NMF-inspired mosaicing idea that
continuous diagonal activations preserve source character better than isolated
frame matches.

It scans the density matrix for contiguous runs along:

- diagonal bands: source/target continuity
- anti-diagonal bands: mirrored or long-distance transitions

Each sequence reports:

- start and end cell
- direction
- length
- salience
- mean amplitude/coherence/probability
- phase slope
- continuity
- one 24-feature audio query for the whole run

In Max, the tile stream can drive grain-level choices, while the sequence stream
can drive `fluid.bufnmfcross~` source/target decisions or longer slice playback.

Pedagogical Explanations

The mosaic layer can explain the top selections in plain language and as numeric
reason vectors.

Tile reason codes:

```text
[is_diagonal, salience, amplitude, probability, coherence, distance, phase_unit]
```

Sequence reason codes:

```text
[is_diagonal_run, salience, amplitude, coherence, distance, continuity, phase_slope]
```

Use the prose explanation for UI labels and the reason codes for visual meters,
coloring, or Max routing.

Example:

```python
from qmw.flucoma import (
    DescriptorCorpus,
    QuantumDescriptorExtractor,
    build_audio_corpus,
    quantum_descriptor_to_audio_query,
    density_matrix_to_activation_sequences,
    density_mosaic_explanation,
    density_matrix_to_mosaic_tiles,
)

extractor = QuantumDescriptorExtractor()
state_corpus = DescriptorCorpus()
audio_corpus = build_audio_corpus("materials")

descriptor = extractor.extract(frame)
state_corpus.add(descriptor)

audio_query = quantum_descriptor_to_audio_query(descriptor)
nearest_sound = audio_corpus.nearest(audio_query, exclude_self=False)

tiles = density_matrix_to_mosaic_tiles(frame.rho, max_tiles=16)
first_tile_query = tiles[0].query
nearest_tile_sound = audio_corpus.nearest(first_tile_query, exclude_self=False)

sequences = density_matrix_to_activation_sequences(frame.rho, max_sequences=8)
first_sequence_query = sequences[0].query
nearest_sequence_sound = audio_corpus.nearest(first_sequence_query, exclude_self=False)

why = density_mosaic_explanation(frame.rho)
print(why["summary"])
```
