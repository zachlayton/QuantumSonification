"""Render the spatiotemporal dodecahedron used by the MusicXML score."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np

from procedural_notation_v1 import build_dodecahedron_graph
from procedural_notation_v1.dodecahedron_score import TEMPORAL_AXIS, apply_dodecahedron_mapping


def main() -> Path:
    graph = apply_dodecahedron_mapping(build_dodecahedron_graph())
    positions = nx.get_node_attributes(graph, "position")
    node_ids = list(graph.nodes)
    onset_ticks = [graph.nodes[node_id]["onset_tick"] for node_id in node_ids]
    tied_nodes = {
        node_id
        for node_id, data in graph.nodes(data=True)
        if data["onset_tick"] // 32
        != (data["onset_tick"] + data["duration_ticks"] - 1) // 32
    }

    figure = plt.figure(figsize=(8.5, 8.5), facecolor="#f7f7f5")
    axis = figure.add_subplot(111, projection="3d")
    axis.set_facecolor("#f7f7f5")

    for start, end in graph.edges:
        x_values = (positions[start][0], positions[end][0])
        y_values = (positions[start][1], positions[end][1])
        z_values = (positions[start][2], positions[end][2])
        axis.plot(x_values, y_values, z_values, color="#66717d", alpha=0.58, linewidth=1.7)

    coordinates = np.asarray([positions[node_id] for node_id in node_ids])
    nodes = axis.scatter(
        coordinates[:, 0],
        coordinates[:, 1],
        coordinates[:, 2],
        c=onset_ticks,
        cmap="viridis",
        vmin=0,
        vmax=127,
        s=145,
        edgecolors="#17212b",
        linewidths=1.2,
        depthshade=False,
    )
    for node_id, (x, y, z) in positions.items():
        axis.text(x, y, z + 0.065, str(node_id), ha="center", va="bottom", fontsize=8, color="#101820")

    for node_id in tied_nodes:
        x, y, z = positions[node_id]
        axis.scatter(
            [x], [y], [z],
            s=245,
            facecolors="none",
            edgecolors="#c43b64",
            linewidths=2.2,
            depthshade=False,
        )

    time_axis = np.asarray(TEMPORAL_AXIS, dtype=float)
    time_axis /= np.linalg.norm(time_axis)
    axis.plot(
        [-1.25 * time_axis[0], 1.25 * time_axis[0]],
        [-1.25 * time_axis[1], 1.25 * time_axis[1]],
        [-1.25 * time_axis[2], 1.25 * time_axis[2]],
        color="#c43b64",
        linestyle="--",
        linewidth=1.5,
        alpha=0.85,
    )
    axis.text(
        1.3 * time_axis[0],
        1.3 * time_axis[1],
        1.3 * time_axis[2],
        "later",
        color="#8f2444",
        fontsize=9,
    )

    colorbar = figure.colorbar(nodes, ax=axis, shrink=0.67, pad=0.04)
    colorbar.set_label("onset tick · 0–127 across four measures")
    legend_item = Line2D(
        [0], [0], marker="o", color="none", markerfacecolor="none",
        markeredgecolor="#c43b64", markeredgewidth=2, markersize=10,
        label="duration crosses a barline → tie",
    )
    axis.legend(handles=[legend_item], loc="upper left", frameon=False)

    axis.set_title("Dodecahedral Time Field No. 1", pad=18, fontsize=16)
    axis.set_xlabel("x → duration")
    axis.set_ylabel("y")
    axis.set_zlabel("z → 24-EDO pitch")
    axis.set_box_aspect((1, 1, 1))
    axis.view_init(elev=20, azim=35)
    axis.grid(False)
    for pane in (axis.xaxis.pane, axis.yaxis.pane, axis.zaxis.pane):
        pane.set_alpha(0.0)
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_zticks([])
    figure.text(
        0.5,
        0.035,
        "20 vertices · 30 edges · node color encodes time, not adjacency",
        ha="center",
        color="#3d4650",
        fontsize=10,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 1))

    output = Path(__file__).parent / "output" / "dodecahedral_time_field_1_graph.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=190, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return output


if __name__ == "__main__":
    print(main())
