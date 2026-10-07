"""Rhino 8 Grasshopper Python 3 component for QMW mesh commits.

Configure component inputs:
    meshes            List Access, Mesh
    commit            Item Access, bool
    output_directory  Item Access, str
    revision          Item Access, int (optional; 0 selects a timestamp revision)
    source            Item Access, str (optional)

Configure component outputs:
    candidate_path
    committed_revision
    status
    vertex_count
    face_count

The component commits only on the rising edge of ``commit``. Geometry is converted
to meters and written atomically as a versioned JSON mesh candidate.
"""

import hashlib
import json
import os
import time

import Rhino
import scriptcontext as sc


SCHEMA = "qmw.grasshopper_mesh_candidate"
SCHEMA_VERSION = 1


def _joined_triangle_mesh(values):
    if isinstance(values, Rhino.Geometry.Mesh):
        values = [values]
    joined = Rhino.Geometry.Mesh()
    for value in values or []:
        if not isinstance(value, Rhino.Geometry.Mesh):
            raise TypeError("Grasshopper input must contain Mesh objects")
        joined.Append(value.DuplicateMesh())
    if joined.Vertices.Count < 3 or joined.Faces.Count < 1:
        raise ValueError("committed geometry contains no usable mesh")
    joined.Faces.ConvertQuadsToTriangles()
    joined.Vertices.CombineIdentical(True, True)
    joined.Vertices.CullUnused()
    joined.Compact()
    return joined


def _meters_per_document_unit():
    document = Rhino.RhinoDoc.ActiveDoc
    if document is None:
        return 1.0, "unknown"
    units = document.ModelUnitSystem
    return float(Rhino.RhinoMath.UnitScale(units, Rhino.UnitSystem.Meters)), str(units)


def _mesh_payload(mesh, candidate_revision, candidate_source):
    scale, document_units = _meters_per_document_unit()
    vertices = [
        [float(vertex.X) * scale, float(vertex.Y) * scale, float(vertex.Z) * scale]
        for vertex in mesh.Vertices
    ]
    faces = []
    for face in mesh.Faces:
        if not face.IsTriangle:
            raise ValueError("mesh contains a face that was not triangulated")
        faces.append([int(face.A), int(face.B), int(face.C)])
    metadata = {
        "rhino_version": str(Rhino.RhinoApp.Version),
        "document_units": document_units,
        "grasshopper_component": str(ghenv.Component.InstanceGuid),
    }
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "revision": int(candidate_revision),
        "created_at": time.time(),
        "source": candidate_source or "grasshopper",
        "units": "meters",
        "vertices": vertices,
        "faces": faces,
        "metadata": metadata,
    }


def _atomic_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, separators=(",", ":"))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


candidate_path = None
committed_revision = None
status = "idle"
vertex_count = 0
face_count = 0

# The full interface uses the documented names. A newly created Rhino 8 script
# component can also run immediately with its default sockets: x is the mesh
# and y is the commit Boolean. The remaining values receive safe defaults.
_meshes_input = globals().get("meshes", globals().get("x", []))
_commit_input = globals().get("commit", globals().get("y", False))
_default_output_directory = os.path.expanduser(
    "~/QuantumSonification/QMW_Music_of_the_Spheres_Resonator_v1/"
    "grasshopper_candidates"
)
_output_directory_input = globals().get(
    "output_directory", _default_output_directory
) or _default_output_directory
_revision_input = globals().get("revision", 0)
_source_input = globals().get("source", "grasshopper")

_trigger_key = "qmw_grasshopper_commit_" + str(ghenv.Component.InstanceGuid)
_previous_commit = bool(sc.sticky.get(_trigger_key, False))
_current_commit = bool(_commit_input)
sc.sticky[_trigger_key] = _current_commit

if _current_commit and not _previous_commit:
    try:
        mesh = _joined_triangle_mesh(_meshes_input)
        requested_revision = int(_revision_input or 0)
        committed_revision = (
            requested_revision
            if requested_revision >= 1
            else int(time.time() * 1000.0)
        )
        payload = _mesh_payload(mesh, committed_revision, _source_input)
        vertex_count = len(payload["vertices"])
        face_count = len(payload["faces"])
        content = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        short_hash = hashlib.sha256(content).hexdigest()[:12]
        filename = "grasshopper_mesh_r{:012d}_{}.json".format(
            committed_revision, short_hash
        )
        candidate_path = os.path.join(
            os.path.expanduser(_output_directory_input), filename
        )
        _atomic_json(candidate_path, payload)
        status = "committed"
    except Exception as error:
        status = "error: " + str(error)
elif _current_commit:
    status = "commit held; toggle off before the next commit"

# Preserve a useful result on the default Grasshopper output named `a`. Users
# who configure the full five-output interface receive the individual values.
a = status
if candidate_path:
    a = "{}\n{}\nrevision={} vertices={} faces={}".format(
        status,
        candidate_path,
        committed_revision,
        vertex_count,
        face_count,
    )
