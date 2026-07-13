# Grasshopper geometry integration v1

This adapter makes Grasshopper a versioned geometry producer for
`LivingSpectralGeometry`. Grasshopper does not run the spectral or acoustic
solvers. It publishes an explicit triangular mesh snapshot at a controlled
commit boundary.

Two component scripts are provided:

- `grasshopper_mesh_commit_component_v1.py` uses the default Script Mode.
- `grasshopper_mesh_commit_sdk_v1.py` uses SDK Mode (`GH_ScriptInstance`).

Do not paste the Script-Mode body below a generated SDK `RunScript` method. Use
the file matching the mode displayed by the Grasshopper editor.

## Grasshopper component

1. Open Rhino 8 and run `Grasshopper`.
2. Add a Python 3 Script component from **Maths → Script**.
3. Copy `grasshopper_mesh_commit_component_v1.py` into the component editor.
4. Configure these inputs:

   - `meshes`: List Access, Mesh
   - `commit`: Item Access, Boolean
   - `output_directory`: Item Access, Text
   - `revision`: Item Access, Integer (optional; use `0` for a timestamp)
   - `source`: Item Access, Text (optional)

5. Configure these outputs:

   - `candidate_path`
   - `committed_revision`
   - `status`
   - `vertex_count`
   - `face_count`

The script joins the input meshes, triangulates faces, combines coincident
vertices, removes unused vertices, converts document coordinates to meters,
and atomically writes a candidate JSON file. It commits only when the Boolean
input changes from false to true.

## Candidate contract

The file contains:

```text
schema / schema_version
revision / created_at / source
units
vertices[n][3]
faces[m][3]
metadata
```

Validate a candidate before connecting it to the living system:

```bash
python grasshopper_geometry_bridge_v1.py /path/to/grasshopper_mesh.json
```

`GrasshopperGeometryBridge.accept_file(...)` rejects stale revisions,
non-finite vertices, invalid indices, degenerate or duplicate triangles,
non-manifold edges, and disconnected surfaces. Open boundary edges are allowed
by default because membrane surfaces may intentionally be open. Set
`MeshValidationPolicy(require_closed=True)` for chamber shells.

## Runtime sequence

```text
OperatorEcologyController emits GeometryMutationEvent
    → Grasshopper previews the mutation continuously
    → commit trigger publishes a mesh candidate
    → GrasshopperGeometryBridge validates and accepts the revision
    → LivingSpectralGeometry receives a LivingOperatorEvent(GEOMETRY)
    → debounced spectral/material/quantum/timing/acoustic recomputation
    → Max receives the candidate IR and performs ready/committed activation
```

The OBJ format remains useful for interchange with Rhino, but the JSON
candidate preserves units, revision identity, source, and metadata and is the
safer live handoff format.

The acoustic material default targets a 4-second T60. Operator-ecology entropy
normally moves damping through approximately 10 seconds down to 1 second, with
no hard clamp preventing shorter impacts or unusually long 20–60+ second
spaces.
