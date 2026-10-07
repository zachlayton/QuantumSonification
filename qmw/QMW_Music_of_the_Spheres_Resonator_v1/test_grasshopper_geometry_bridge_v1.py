from __future__ import annotations

from pathlib import Path
import tempfile

import numpy as np

from grasshopper_geometry_bridge_v1 import (
    GrasshopperGeometryBridge,
    GrasshopperMeshCandidate,
    MeshValidationPolicy,
)
from living_spectral_geometry_v1 import LivingEventType


def square_mesh() -> tuple[np.ndarray, np.ndarray]:
    vertices = np.array(
        [
            [0.0, 0.0, 0.0],
            [1000.0, 0.0, 0.0],
            [1000.0, 1000.0, 0.0],
            [0.0, 1000.0, 0.0],
        ]
    )
    faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int64)
    return vertices, faces


class StubLivingGeometry:
    def __init__(self) -> None:
        self.events = []

    def apply_event(self, event, *, schedule=True):
        self.events.append((event, schedule))
        return 100 + len(self.events) if schedule else None


def test_candidate_roundtrip_normalizes_units(tmp_path: Path) -> None:
    vertices, faces = square_mesh()
    candidate = GrasshopperMeshCandidate(
        7,
        vertices,
        faces,
        units="millimeters",
        metadata={"definition": "test"},
    )
    diagnostics = candidate.validate()
    assert diagnostics.vertex_count == 4
    assert diagnostics.face_count == 2
    assert diagnostics.boundary_edge_count == 4
    assert diagnostics.nonmanifold_edge_count == 0
    assert diagnostics.connected_components == 1
    assert np.isclose(diagnostics.surface_area_m2, 1.0)

    path = candidate.save_json(tmp_path / "candidate.json")
    restored = GrasshopperMeshCandidate.load_json(path)
    np.testing.assert_allclose(restored.vertices_m, candidate.vertices_m)
    np.testing.assert_array_equal(restored.faces, candidate.faces)
    assert restored.geometry_hash == candidate.geometry_hash


def test_candidate_policy_rejects_invalid_topology() -> None:
    vertices, faces = square_mesh()
    open_candidate = GrasshopperMeshCandidate(1, vertices, faces, units="mm")
    try:
        open_candidate.validate(MeshValidationPolicy(require_closed=True))
    except ValueError as error:
        assert "boundary edge" in str(error)
    else:
        raise AssertionError("closed-surface policy accepted an open mesh")

    duplicate = GrasshopperMeshCandidate(
        2, vertices, np.vstack((faces, faces[0])), units="mm"
    )
    try:
        duplicate.validate()
    except ValueError as error:
        assert "duplicate face" in str(error)
    else:
        raise AssertionError("duplicate triangle was accepted")


def test_bridge_orders_and_deduplicates_candidates(tmp_path: Path) -> None:
    vertices, faces = square_mesh()
    target = StubLivingGeometry()
    bridge = GrasshopperGeometryBridge(target)
    first = GrasshopperMeshCandidate(1, vertices, faces, units="mm")
    first_path = first.save_json(tmp_path / "first.json")

    accepted = bridge.accept_file(first_path)
    assert accepted.status == "accepted"
    assert accepted.living_revision == 101
    assert len(target.events) == 1
    event, schedule = target.events[0]
    assert event.type is LivingEventType.GEOMETRY
    assert schedule is True
    np.testing.assert_allclose(event.payload["vertices"], first.vertices_m)

    assert bridge.accept(first) is accepted
    assert len(target.events) == 1

    unchanged = bridge.accept(
        GrasshopperMeshCandidate(2, vertices, faces, units="mm")
    )
    assert unchanged.status == "unchanged"
    assert unchanged.living_revision is None
    assert len(target.events) == 1

    changed_vertices = vertices.copy()
    changed_vertices[2, 2] = 50.0
    changed = bridge.accept(
        GrasshopperMeshCandidate(3, changed_vertices, faces, units="mm"),
        schedule=False,
    )
    assert changed.status == "accepted"
    assert changed.living_revision is None
    assert len(target.events) == 2
    assert target.events[-1][1] is False

    try:
        bridge.accept(first)
    except ValueError as error:
        assert "stale Grasshopper revision" in str(error)
    else:
        raise AssertionError("stale candidate revision was accepted")


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        test_candidate_roundtrip_normalizes_units(path)
        test_bridge_orders_and_deduplicates_candidates(path)
    test_candidate_policy_rejects_invalid_topology()
    print("all Grasshopper geometry bridge v1 tests passed")


if __name__ == "__main__":
    main()
