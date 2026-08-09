"""Extract the Figure 4 Stark-resonance comparison atlas from the PDF."""

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
BASE_SCALE = 1.5
RENDER_SCALE = 4.0
PANELS = {
    "red_0_29_0_b0": (126, 96, 272, 158),
    "red_0_29_0_b6": (291, 96, 436, 158),
    "red_3_26_0_b0": (126, 169, 272, 231),
    "red_3_26_0_b6": (291, 169, 436, 231),
    "blue_23_0_0_b0": (126, 269, 199, 417),
    "blue_23_0_0_b6": (291, 269, 363, 417),
    "blue_20_3_0_b0": (207, 269, 278, 417),
    "blue_20_3_0_b6": (370, 269, 440, 417),
}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    image = pdfium.PdfDocument(PDF)[4].render(scale=RENDER_SCALE).to_pil().convert("RGB")
    factor = RENDER_SCALE / BASE_SCALE
    for name, box in PANELS.items():
        scaled = tuple(round(value * factor) for value in box)
        image.crop(scaled).save(OUTPUT / f"figure4_{name}.png")


if __name__ == "__main__":
    main()
