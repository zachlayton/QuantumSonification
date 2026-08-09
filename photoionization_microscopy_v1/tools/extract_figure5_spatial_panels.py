"""Extract the five Figure 5 (rho,z) reference panels from the supplied PDF.

Generated PNGs retain the paper's calculated density colors. At 0 T and 8 T
they also retain the representative classical-path overlays printed by the
authors. They are reference images, not reconstructed TDSE arrays.
"""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "docs" / "Photoionization .pdf"
OUTPUT = (
    ROOT
    / "photoionization_microscopy_v1"
    / "processing"
    / "QMWPhotoionizationMicroscopyV1"
    / "data"
)

# Coordinates measured from a scale=1.5 render of PDF page 6. The tighter
# vertical crop removes printed axes while preserving the full density field.
BASE_SCALE = 1.5
RENDER_SCALE = 4.0
PANELS = {
    0: (242, 100, 440, 159),
    2: (242, 183, 440, 242),
    4: (242, 266, 440, 325),
    6: (242, 350, 440, 408),
    8: (242, 433, 440, 492),
}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(PDF)
    page = document[5]
    image = page.render(scale=RENDER_SCALE).to_pil().convert("RGB")
    factor = RENDER_SCALE / BASE_SCALE
    for field_t, box in PANELS.items():
        scaled = tuple(round(value * factor) for value in box)
        image.crop(scaled).save(OUTPUT / f"figure5_spatial_b{field_t}.png")


if __name__ == "__main__":
    main()
