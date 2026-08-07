# QMW I Ching Network Visualizer V1

Processing 4 visual mirror for committed I Ching density/Laplacian revisions.

## Requirements

- Processing 4
- `oscP5` library installed through Processing's Contribution Manager
- UDP port `7404` available

## Run

Open `QMW_IChing_Network_Visualizer_v1.pde` and press Run. The sketch starts
with a deterministic seed-42 demo. Publish a live revision from the repository
root with:

```bash
python qmw_iching_processing_visualizer_publisher_v1.py --seed 42 --revision 108
```

This mirrors the identical atomic transaction to the density engine on `7403`
and the visualizer on `7404`. Use `--no-engine` for visual-only replay.

## Controls

- Drag: rotate
- Mouse wheel: zoom
- `R`: reset view
- `D`: restore deterministic demo
- `H`: toggle help

The scene changes only after a complete matching `/qmw/iching/network/end`
message. Incomplete frames never become visible.
