import json

import numpy as np
import pytest

from qmw_metric import QuantumMetricConfig, QuantumMetricEngine
from qmw_metric.live_transport import (
    ARRAY_FIELDS,
    CONTRACT,
    FrameContractError,
    RevisionGate,
    decode_binary_frame,
    encode_binary_frame,
    encode_json_frame,
    shader_frame_to_payload,
)


def _shader():
    engine = QuantumMetricEngine(QuantumMetricConfig(grid_size=(10, 10), mode_count=3))
    engine.update_quantum_frame(
        np.eye(16, dtype=np.complex128) / 16.0,
        time=0.25,
        source_revision=3,
    )
    return engine.system_frame.shader


@pytest.mark.parametrize("compress", [False, True])
def test_binary_transport_round_trip_is_typed_and_complete(compress):
    frame = _shader()
    decoded = decode_binary_frame(encode_binary_frame(frame, compress=compress))
    assert decoded["contract"] == CONTRACT
    assert tuple(decoded["arrays"]) == ARRAY_FIELDS
    assert decoded["arrays"]["density"].dtype == np.dtype("float32")
    for name in ARRAY_FIELDS:
        assert np.allclose(decoded["arrays"][name], getattr(frame, name), atol=1e-6)


def test_json_fallback_is_inspectable_and_has_same_inventory():
    decoded = json.loads(encode_json_frame(_shader()))
    assert decoded["contract"] == CONTRACT
    assert tuple(decoded["arrays"]) == ARRAY_FIELDS


def test_revision_gate_rejects_duplicate_and_source_regression():
    payload = shader_frame_to_payload(_shader())
    gate = RevisionGate()
    assert gate.accept(payload)
    assert not gate.accept(payload)
    newer = dict(payload, revision=payload["revision"] + 1)
    assert gate.accept(newer)
    regressed = dict(newer, revision=newer["revision"] + 1, source_revision=-1)
    with pytest.raises(FrameContractError, match="source_revision"):
        gate.accept(regressed)


def test_binary_decoder_rejects_bad_envelope():
    encoded = bytearray(encode_binary_frame(_shader()))
    encoded[0] ^= 0xFF
    with pytest.raises(FrameContractError, match="envelope"):
        decode_binary_frame(bytes(encoded))
