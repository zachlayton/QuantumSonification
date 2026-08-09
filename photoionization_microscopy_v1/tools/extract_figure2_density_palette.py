"""Extract the logarithmic density palette used by the paper's figures."""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "docs" / "Photoionization .pdf"
OUTPUT = ROOT / "photoionization_microscopy_v1" / "data" / "figure2_density_palette.png"


def main() -> None:
    document = pdfium.PdfDocument(str(PDF))
    page = document[2]
    image = page.render(scale=4.0).to_pil().convert("RGB")
    # Interior of the horizontal 10^-4 ... 1 color bar in Figure 2.
    # Keep only the uninterrupted interior; lower rows contain tick marks.
    palette = image.crop((326, 255, 717, 263))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    palette.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
