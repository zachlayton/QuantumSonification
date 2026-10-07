"""Fixed-length selectable-resolution Gaussian scalar field for QMW QFT V5."""

from __future__ import annotations

from typing import Any

from .live_osc_v3 import (
    LiveScalarFieldEngine as _BaseLiveScalarFieldEngine,
    LiveScalarFieldParameters,
    ScalarFieldFramePublisher as _BaseScalarFieldFramePublisher,
    _install_controls,
    main as _shared_main,
)


OUTPUT_PORT = 17870
CONTROL_PORT = 17871
OSC_VERSION = 5
SITES = 32
SELECTABLE_SITES = (8, 16, 32)
PHYSICAL_LENGTH = 8.0
SCHEMA = "qmw.scalar_field.osc.v5"


def parameters_for_resolution(sites: int = SITES) -> LiveScalarFieldParameters:
    sites = int(sites)
    if sites not in SELECTABLE_SITES:
        raise ValueError(f"V5 sites must be one of {SELECTABLE_SITES}")
    return LiveScalarFieldParameters(
        sites=sites,
        lattice_spacing=PHYSICAL_LENGTH / sites,
        localized_site=sites // 2,
    )


class LiveScalarFieldEngine(_BaseLiveScalarFieldEngine):
    """V5 engine at fixed physical length, defaulting to 32 sites."""

    def __init__(self, parameters: LiveScalarFieldParameters | None = None) -> None:
        parameters = parameters or parameters_for_resolution()
        if parameters.sites not in SELECTABLE_SITES:
            raise ValueError(f"V5 sites must be one of {SELECTABLE_SITES}")
        expected_spacing = PHYSICAL_LENGTH / parameters.sites
        if abs(parameters.lattice_spacing - expected_spacing) > 1e-12:
            raise ValueError("V5 lattice spacing must equal physical_length / sites")
        super().__init__(parameters, osc_version=OSC_VERSION)


class ScalarFieldFramePublisher(_BaseScalarFieldFramePublisher):
    """V5 publisher with row-chunked correlation transport."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
    ) -> None:
        super().__init__(
            client,
            host=host,
            port=port,
            osc_version=OSC_VERSION,
            chunk_correlations=True,
        )


def main() -> None:
    _shared_main(
        default_sites=SITES,
        osc_version=OSC_VERSION,
        default_output_port=OUTPUT_PORT,
        default_control_port=CONTROL_PORT,
        selectable_sites=SELECTABLE_SITES,
        physical_length=PHYSICAL_LENGTH,
    )


__all__ = [
    "CONTROL_PORT",
    "LiveScalarFieldEngine",
    "LiveScalarFieldParameters",
    "OSC_VERSION",
    "OUTPUT_PORT",
    "PHYSICAL_LENGTH",
    "SCHEMA",
    "SELECTABLE_SITES",
    "SITES",
    "ScalarFieldFramePublisher",
    "main",
    "parameters_for_resolution",
    "_install_controls",
]


if __name__ == "__main__":
    main()
