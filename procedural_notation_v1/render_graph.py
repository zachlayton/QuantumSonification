"""Render the current geometric pitch graph as a PNG."""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from procedural_notation_v1 import apply_pitch_mapping, build_regular_polygon_graph


def main() -> Path:
    graph = apply_pitch_mapping(build_regular_polygon_graph())
    positions = nx.get_node_attributes(graph, "position")
    labels = {
        node_id: f"{node_id}\n{data['pitch']}"
        for node_id, data in graph.nodes(data=True)
    }

    figure, axis = plt.subplots(figsize=(7, 7), facecolor="#f7f7f5")
    axis.set_facecolor("#f7f7f5")
    nx.draw_networkx_edges(graph, positions, ax=axis, width=2.5, edge_color="#59636e")
    nx.draw_networkx_nodes(
        graph,
        positions,
        ax=axis,
        node_size=2200,
        node_color="#2463a5",
        edgecolors="#163a5f",
        linewidths=2.5,
    )
    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        ax=axis,
        font_color="white",
        font_size=13,
        font_weight="bold",
    )

    axis.set_title("Regular Octagon Graph · Current Pitch Mapping", fontsize=16, pad=18)
    axis.text(
        0.5,
        -0.03,
        "Undirected cycle · radius 1.0 · all edge distances ≈ 0.765",
        transform=axis.transAxes,
        ha="center",
        fontsize=10,
        color="#3d4650",
    )
    axis.set_aspect("equal")
    axis.set_axis_off()
    figure.tight_layout()

    output = Path(__file__).parent / "output" / "regular_octagon_graph.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180, bbox_inches="tight", facecolor=figure.get_facecolor())
    plt.close(figure)
    return output


if __name__ == "__main__":
    print(main())
