"""FluCoMa-inspired descriptor and corpus tools for QMW."""

from qmw.flucoma.audio_corpus import (
    AUDIO_FEATURE_NAMES,
    audio_descriptor_vector,
    build_audio_corpus,
    nearest_audio_material,
    quantum_descriptor_to_audio_query,
)
from qmw.flucoma.corpus import DescriptorCorpus, SearchResult
from qmw.flucoma.density_mosaic import (
    DensityMosaicSequence,
    DensityMosaicTile,
    density_mosaic_explanation,
    density_cell_to_audio_query,
    density_matrix_to_activation_sequences,
    density_matrix_to_mosaic_tiles,
    density_sequence_to_audio_query,
    explain_density_mosaic_sequence,
    explain_density_mosaic_tile,
    sequence_reason_codes,
    summarize_density_mosaic,
    tile_reason_codes,
)
from qmw.flucoma.quantum_descriptors import (
    DescriptorVector,
    QuantumDescriptorExtractor,
)

__all__ = [
    "DescriptorCorpus",
    "DescriptorVector",
    "DensityMosaicSequence",
    "DensityMosaicTile",
    "QuantumDescriptorExtractor",
    "SearchResult",
    "AUDIO_FEATURE_NAMES",
    "audio_descriptor_vector",
    "build_audio_corpus",
    "nearest_audio_material",
    "quantum_descriptor_to_audio_query",
    "density_cell_to_audio_query",
    "density_mosaic_explanation",
    "density_matrix_to_activation_sequences",
    "density_matrix_to_mosaic_tiles",
    "density_sequence_to_audio_query",
    "explain_density_mosaic_sequence",
    "explain_density_mosaic_tile",
    "sequence_reason_codes",
    "summarize_density_mosaic",
    "tile_reason_codes",
]
