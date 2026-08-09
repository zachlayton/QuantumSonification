"""Expand an eigenfield contour into numerically grouped repeated-note phrases."""

from __future__ import annotations

from itertools import accumulate, cycle
from typing import Sequence

import networkx as nx


DEFAULT_PHRASE_CELLS = (3, 5, 8, 5, 3)
DEFAULT_REPETITION_CYCLE = (1, 2, 3, 5, 3, 2)
DEFAULT_INTERPHRASE_RESTS = (1, 2, 3, 2)


def build_numerical_phrase_graph(
    eigenfield_graph: nx.Graph,
    phrase_cells: Sequence[int] = DEFAULT_PHRASE_CELLS,
    repetition_cycle: Sequence[int] = DEFAULT_REPETITION_CYCLE,
    interphrase_rests: Sequence[int] = DEFAULT_INTERPHRASE_RESTS,
) -> nx.DiGraph:
    """Return timed note attacks grouped by integer phrase and rest patterns."""
    _validate_positive_integers("phrase_cells", phrase_cells)
    _validate_positive_integers("repetition_cycle", repetition_cycle)
    _validate_positive_integers("interphrase_rests", interphrase_rests)
    if len(interphrase_rests) != len(phrase_cells) - 1:
        raise ValueError("interphrase_rests must contain one value per phrase boundary")

    path = eigenfield_graph.graph.get("traversal_path")
    if not path:
        raise ValueError("eigenfield_graph must define a traversal_path")
    for node_id in path:
        if "pitch" not in eigenfield_graph.nodes[node_id]:
            raise ValueError(f"node {node_id!r} has no pitch mapping")

    change_anchors = [path[0]]
    for node_id in path[1:]:
        if eigenfield_graph.nodes[node_id]["pitch"] != eigenfield_graph.nodes[change_anchors[-1]]["pitch"]:
            change_anchors.append(node_id)

    cell_count = sum(phrase_cells)
    if len(change_anchors) < cell_count:
        raise ValueError("the eigenfield contour has too few pitch changes for the phrase design")
    anchor_indices = [
        round(index * (len(change_anchors) - 1) / (cell_count - 1))
        for index in range(cell_count)
    ]
    selected_anchors = [change_anchors[index] for index in anchor_indices]
    repetitions = [count for count, _ in zip(cycle(repetition_cycle), range(cell_count))]
    phrase_ends = set(accumulate(phrase_cells))

    event_graph = nx.DiGraph()
    onset_tick = 0
    event_id = 0
    previous_event: int | None = None
    phrase_index = 0
    rest_index = 0
    for cell_index, (source_node, repetition_count) in enumerate(
        zip(selected_anchors, repetitions, strict=True),
        start=1,
    ):
        source_data = eigenfield_graph.nodes[source_node]
        for repetition_index in range(repetition_count):
            event_graph.add_node(
                event_id,
                pitch=source_data["pitch"],
                pitch_space=source_data["pitch_space"],
                onset_tick=onset_tick,
                duration_ticks=1,
                source_vertex=source_node,
                field_value=source_data["field_value"],
                phrase_index=phrase_index,
                cell_index=cell_index - 1,
                repetition_index=repetition_index,
                repetition_count=repetition_count,
            )
            if previous_event is not None:
                previous_end = (
                    event_graph.nodes[previous_event]["onset_tick"]
                    + event_graph.nodes[previous_event]["duration_ticks"]
                )
                event_graph.add_edge(
                    previous_event,
                    event_id,
                    intervening_rest_ticks=onset_tick - previous_end,
                )
            previous_event = event_id
            event_id += 1
            onset_tick += 1

        if cell_index in phrase_ends and cell_index != cell_count:
            onset_tick += interphrase_rests[rest_index]
            rest_index += 1
            phrase_index += 1

    event_graph.graph.update(
        geometry="laplacian_eigenfield_numerical_phrases",
        source_eigenmode=eigenfield_graph.graph.get("eigenmode_index"),
        source_eigenvalue=eigenfield_graph.graph.get("eigenvalue"),
        pitch_collection=eigenfield_graph.graph.get("pitch_collection"),
        phrase_cells=tuple(phrase_cells),
        repetition_cycle=tuple(repetition_cycle),
        repetition_counts=tuple(repetitions),
        interphrase_rests=tuple(interphrase_rests),
        selected_source_nodes=tuple(selected_anchors),
        rhythm_subdivisions_per_quarter=8,
        total_ticks=onset_tick,
    )
    return event_graph


def _validate_positive_integers(name: str, values: Sequence[int]) -> None:
    if not values or any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in values
    ):
        raise ValueError(f"{name} must contain positive integers")
