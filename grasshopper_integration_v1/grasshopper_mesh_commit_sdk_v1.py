"""Rhino 8 Grasshopper SDK-mode component for QMW mesh commits.

Inputs, in this order:
    meshes, output_directory, revision, source, commit

Keep Grasshopper's standard ``out`` parameter. Add four custom outputs:
    committed_revision, status, vertex_count, face_count

The committed candidate path is printed to the standard ``out`` parameter.
"""

import System
import Grasshopper
import Rhino
import hashlib
import json
import os
import time
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
    return (
        float(Rhino.RhinoMath.UnitScale(units, Rhino.UnitSystem.Meters)),
        str(units),
    )


def _mesh_payload(mesh, revision, source, component_id):
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
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "revision": int(revision),
        "created_at": time.time(),
        "source": source or "grasshopper",
        "units": "meters",
        "vertices": vertices,
        "faces": faces,
        "metadata": {
            "rhino_version": str(Rhino.RhinoApp.Version),
            "document_units": document_units,
            "grasshopper_component": str(component_id),
        },
    }


def _atomic_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, separators=(",", ":"))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


class MyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        meshes: System.Collections.Generic.List[Rhino.Geometry.Mesh],
        output_directory,
        revision,
        source,
        commit,
    ):
        committed_revision = None
        status = "idle"
        vertex_count = 0
        face_count = 0

        default_output_directory = os.path.expanduser(
            "~/QuantumSonification/"
            "grasshopper_candidates"
        )
        resolved_output_directory = (
            str(output_directory).strip()
            if output_directory is not None and str(output_directory).strip()
            else default_output_directory
        )

        component_id = "sdk:{}:{}".format(
            os.path.expanduser(resolved_output_directory),
            str(source or "grasshopper"),
        )
        trigger_key = "qmw_grasshopper_commit_" + component_id
        previous_commit = bool(sc.sticky.get(trigger_key, False))
        current_commit = bool(commit)
        sc.sticky[trigger_key] = current_commit

        if not current_commit:
            return committed_revision, status, vertex_count, face_count
        if previous_commit:
            status = "commit held; toggle off before the next commit"
            return committed_revision, status, vertex_count, face_count

        try:
            mesh = _joined_triangle_mesh(meshes)
            requested_revision = int(revision or 0)
            committed_revision = (
                requested_revision
                if requested_revision >= 1
                else int(time.time() * 1000.0)
            )
            payload = _mesh_payload(
                mesh,
                committed_revision,
                source,
                component_id,
            )
            vertex_count = len(payload["vertices"])
            face_count = len(payload["faces"])
            content = json.dumps(
                payload, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            short_hash = hashlib.sha256(content).hexdigest()[:12]
            filename = "grasshopper_mesh_r{:012d}_{}.json".format(
                committed_revision, short_hash
            )
            candidate_path = os.path.join(
                os.path.expanduser(resolved_output_directory), filename
            )
            _atomic_json(candidate_path, payload)
            print(candidate_path)
            status = "committed"
        except Exception as error:
            status = "error: " + str(error)

        return committed_revision, status, vertex_count, face_count
