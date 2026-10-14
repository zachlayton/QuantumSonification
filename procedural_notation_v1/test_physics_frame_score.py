import json
import xml.etree.ElementTree as ET

import numpy as np
import pytest
from music21 import converter, note
from qmw.core.physics_frame import PhysicsFrame
from procedural_notation_v1.generate_physics_frame_score import example_frame
from procedural_notation_v1.physics_frame_score import build_physics_frame_canon, write_physics_frame_score


def test_selection_preserves_unequal_time_intervals_and_data():
    frame = example_frame()
    before = frame.rho.copy()
    graph = build_physics_frame_canon(frame, sample_indices=[0, 256, 768, 2047])
    p = graph.graph["physics_frame_projection"]
    assert p["snapshot_onset_ticks"][:3] == [0, 68, 204]
    assert np.max(np.abs(p["quantization_error_ticks"])) <= 0.5
    for _, event in graph.nodes(data=True):
        i = event["source_sample_index"]
        assert event["source_physical_time"] == frame.t[i]
        assert event["matrix_magnitude"] == abs(frame.rho[i, event["matrix_row"], event["matrix_column"]])
    np.testing.assert_array_equal(frame.rho, before)


def test_quantization_changes_only_projection():
    frame = example_frame()
    a = build_physics_frame_canon(frame, quantization_ticks=1)
    b = build_physics_frame_canon(frame, quantization_ticks=4)
    assert a.graph["physics_frame_projection"]["physical_times"] == b.graph["physics_frame_projection"]["physical_times"]
    assert all(t % 4 == 0 for t in b.graph["snapshot_onset_ticks"])
    assert a.graph["snapshot_purities"] == b.graph["snapshot_purities"]


@pytest.mark.parametrize("options", [
    {"sample_indices": []}, {"sample_indices": [1, 1]}, {"sample_indices": [-1]},
    {"sample_indices": [2048]}, {"sample_indices": [True]}, {"snapshot_count": 2049},
    {"snapshot_count": 0}, {"quantization_ticks": 0}, {"slot_ticks": 1},
    {"ticks_per_time_unit": float("nan")}, {"ticks_per_time_unit": 0.01},
])
def test_invalid_projection_rejected(options):
    with pytest.raises(ValueError):
        build_physics_frame_canon(example_frame(), **options)


@pytest.mark.parametrize("failure", ["missing", "dimension", "time", "nan", "trace", "negative"])
def test_invalid_physics_rejected(failure):
    frame = example_frame()
    if failure == "missing": frame.rho = None
    if failure == "dimension": frame.rho = frame.rho[:, :4, :4]
    if failure == "time": frame.t[1] = frame.t[0]
    if failure == "nan": frame.rho[0, 0, 0] = np.nan
    if failure == "trace": frame.rho[0] *= 2
    if failure == "negative": frame.rho[0] = np.diag([-1, 2] + [0] * 14)
    with pytest.raises(ValueError):
        build_physics_frame_canon(frame)


def test_musicxml_roundtrip_timing_polyphony_and_sidecar(tmp_path):
    # Mixed states and nonuniform time axis must work without psi.
    frame = PhysicsFrame(t=[10, 11, 13], rho=np.tile(np.eye(16)/16, (3, 1, 1)))
    options = {"sample_indices": [0, 1, 2]}
    graph = build_physics_frame_canon(frame, **options)
    output = write_physics_frame_score(frame, tmp_path / "score.musicxml", **options)
    root = ET.parse(output).getroot()
    assert root.tag == "score-partwise"
    assert len(root.findall("part")) == len(root.findall("part-list/score-part")) == 32
    score = converter.parse(output)
    for part, voice in zip(score.parts, sorted(graph.graph["voices"]), strict=True):
        expected = sorted((d["onset_tick"] / 8, d["pitch_space"]) for _, d in graph.nodes(data=True) if d["voice"] == voice)
        actual = [(float(n.offset), n.pitch.ps) for n in part.flatten().notes
                  if isinstance(n, note.Note) and (n.tie is None or n.tie.type == "start")]
        assert actual == expected
        assert all(float(m.duration.quarterLength) == 4 for m in part.getElementsByClass("Measure"))
    provenance = json.loads(output.with_suffix(".timing.json").read_text())
    assert provenance["physical_times"] == [10, 11, 13]
    assert provenance["snapshot_onset_ticks"] == [0, 68, 204]


def test_single_snapshot():
    g = build_physics_frame_canon(example_frame(), sample_indices=[400])
    assert g.graph["snapshot_onset_ticks"] == (0,)
    assert g.graph["voice_count"] == 32
