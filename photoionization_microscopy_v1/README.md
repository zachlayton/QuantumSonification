# QMW Photoionization Microscopy v1

This package turns the hydrogen photoionization-microscopy calculation in
Deng et al. (2016) into a first QMW research source.

The initial backend is deliberately narrow and reproducible. It contains the
normalized detector radial distributions digitized from Figure 5 for the red
Stark resonance `(1,28,0)` at `F = 808 V/cm`, after 500 ps of propagation:

```text
B = 0, 2, 4, 6, 8 T
z_detector = -8000 a.u.
```

These arrays are paper-reference traces, not newly calculated TDSE data.
Intermediate fields are linear morphs between neighboring traces. The package
also includes the resonance positions transcribed from Table I.

## Run

From the repository root:

```bash
python examples/photoionization_microscopy_demo.py
python examples/photoionization_microscopy_demo.py --fields 0,1,2,3,4,5,6,7,8
python -m unittest test_photoionization_microscopy_v1.py
```

Publish the sweep over OSC using the included standard-library OSC client:

```bash
python examples/photoionization_microscopy_demo.py --osc-port 7400 --realtime
```

## Processing visualizer

Open and run this Processing 4 sketch:

```text
photoionization_microscopy_v1/processing/
  QMWPhotoionizationMicroscopyV1/QMWPhotoionizationMicroscopyV1.pde
```

It requires the `oscP5` library and listens on UDP `17620`. In another terminal:

```bash
python3 examples/photoionization_processing_stream.py
```

The default stream performs a smooth `0 -> 8 -> 0 T` cycle every 24 seconds.
Useful alternatives:

```bash
python3 examples/photoionization_processing_stream.py --cycle-seconds 12
python3 examples/photoionization_processing_stream.py --field 6
python3 examples/photoionization_processing_stream.py --duration 10
```

Processing controls: `P` or space pauses interpolation; `G` toggles detector
guides. The large `(rho,z)` panel crossfades the paper's calculated Figure 5
spatial distributions. The 0 T and 8 T reference images retain the authors'
representative classical-path overlays. The circular image and radial curve
display the detector flux; the eight bars are the derived renderer lanes.

Press `A` for the Figure 4 state atlas and `M` to return to live microscopy.
Keys `1`-`4` (or the clickable headers) select `(0,29,0)`, `(3,26,0)`,
`(23,0,0)`, and `(20,3,0)`. The atlas deliberately uses the paper's parabolic
Stark labels rather than field-free spherical `(n,l,m)` names. It compares
each state at 0 T and 6 T and identifies its red/blue family and transverse
node count.

Regenerate the spatial reference PNGs from the supplied PDF with the bundled
runtime (which includes `pypdfium2`):

```bash
python3 photoionization_microscopy_v1/tools/extract_figure5_spatial_panels.py
python3 photoionization_microscopy_v1/tools/extract_figure4_state_atlas.py
```

## Axisymmetric OBJ geometry from numerical arrays

The production geometry path does not read or crossfade images. It requires an
NPZ with these numerical arrays:

```bash
rho_um            # shape (nr,), non-negative and increasing
z_um              # shape (nz,), increasing
density_rho_z     # shape (nr,nz), non-negative
# or complex psi_rho_z with the same shape; density is abs(psi)**2
metadata_json     # optional scalar JSON string
```

```bash
python3 examples/photoionization_geometry.py \
  --density-npz path/to/photoionization_density_b6.npz \
  --level 0.001
```

The command writes physical and display-scale OBJ files, a preview, and JSON
metadata. The raster reconstruction remains only as the explicitly named
`generate_raster_proxy_geometry()` research reference; it is not used by the
production command.

## Model boundary

`PhotoionizationMicroscopySource` follows the QMW `QuantumSource` contract and
exports detector arrays, observables, a compact compatibility descriptor, and
an eight-lane radial adapter. Its compact descriptor is a control projection,
not an additional physical claim.

The next backend should be a two-dimensional axisymmetric TDSE solver in
`rho,z` with Coulomb, Stark, and diamagnetic terms, a Gaussian laser source,
absorbing boundaries, and time-integrated detector flux. That solver should
be added behind a backend boundary; it must not silently replace or relabel
the digitized reference data.

## OSC contract

```text
/qmw/photoionization/config
/qmw/photoionization/resonance
/qmw/photoionization/detector/rho_um
/qmw/photoionization/detector/radial_flux
/qmw/photoionization/detector/peaks
/qmw/photoionization/detector/fringe_minima
/qmw/photoionization/detector/lanes
/qmw/photoionization/observables
/qmw/photoionization/reference_status
```

Source: M. Deng et al., *Photoionization microscopy for hydrogen atom in
parallel electric and magnetic fields*, dated May 3, 2016. Figure 5 appears on
page 6 of the supplied PDF; Table I appears on page 5.
