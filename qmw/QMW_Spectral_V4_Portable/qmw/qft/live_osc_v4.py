"""Sixteen-site live Gaussian scalar-field instrument for QMW QFT V4."""

from __future__ import annotations

from typing import Any

from .live_osc_v3 import (
    LiveScalarFieldEngine as _BaseLiveScalarFieldEngine,
    LiveScalarFieldParameters,
    ScalarFieldFramePublisher as _BaseScalarFieldFramePublisher,
    _install_controls,
    main as _shared_main,
)


OUTPUT_PORT = 17860
CONTROL_PORT = 17861
OSC_VERSION = 4
SITES = 16
SCHEMA = "qmw.scalar_field.osc.v4"


class LiveScalarFieldEngine(_BaseLiveScalarFieldEngine):
    """V4 engine with sixteen sites and the V4 control namespace by default."""

    def __init__(self, parameters: LiveScalarFieldParameters | None = None) -> None:
        super().__init__(
            parameters
            or LiveScalarFieldParameters(sites=SITES, localized_site=SITES // 2),
            osc_version=OSC_VERSION,
        )


class ScalarFieldFramePublisher(_BaseScalarFieldFramePublisher):
    """V4 publisher with an isolated OSC schema and port."""

    def __init__(
        self,
        client: Any | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = OUTPUT_PORT,
    ) -> None:
        super().__init__(
            client, host=host, port=port, osc_version=OSC_VERSION
        )


def main() -> None:
    _shared_main(
        default_sites=SITES,
        osc_version=OSC_VERSION,
        default_output_port=OUTPUT_PORT,
        default_control_port=CONTROL_PORT,
    )


__all__ = [
    "CONTROL_PORT",
    "LiveScalarFieldEngine",
    "LiveScalarFieldParameters",
    "OSC_VERSION",
    "OUTPUT_PORT",
    "SCHEMA",
    "SITES",
    "ScalarFieldFramePublisher",
    "main",
    "_install_controls",
]


if __name__ == "__main__":
    main()
