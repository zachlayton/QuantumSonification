#!/usr/bin/env python3
"""Publish graph-density and modal-tracking diagnostics to the Max evaluator."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

import numpy as np
from pythonosc.udp_client import SimpleUDPClient


DEFAULT_FOUNDATIONS_PARENT = Path(__file__).resolve().parents[1]


def load_foundations(parent: Path) -> tuple:
    sys.path.insert(0, str(parent.expanduser().resolve()))
    from quantumsonification_foundations_v1.density.graph_density_state_v1 import (
        GraphDensityState,
        TensorLabeling,
        adjacency_from_edges,
        project_density_to_graph_state,
    )
    from quantumsonification_foundations_v1.geometry.modal_subspace_tracker_v1 import (
        ModalSubspaceTracker,
        ModalTrackingConfig,
        generalized_eigen_residuals,
    )

    return (
        GraphDensityState,
        TensorLabeling,
        adjacency_from_edges,
        project_density_to_graph_state,
        ModalSubspaceTracker,
        ModalTrackingConfig,
        generalized_eigen_residuals,
    )


def send_list(client: SimpleUDPClient, address: str, values: np.ndarray | list) -> None:
    client.send_message(address, np.asarray(values).reshape(-1).tolist())


def publish_graph(client: SimpleUDPClient, api: tuple, phase: float) -> None:
    GraphDensityState, TensorLabeling, adjacency_from_edges, project_density, *_ = api
    weights = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(phase + np.arange(6) * 0.83))
    edges = [(0, 1), (1, 3), (3, 2), (2, 0), (0, 3), (1, 2)]
    adjacency = adjacency_from_edges(4, edges, weights)
    state = GraphDensityState.from_adjacency(
        adjacency,
        labeling=TensorLabeling((2, 2)),
    )
    target = 0.72 * state.rho_graph + 0.28 * np.eye(4) / 4.0
    projection = project_density(target)
    client.send_message("/qsf/graph/dimension", 4)
    send_list(client, "/qsf/graph/rho_real", np.real(state.rho_graph))
    send_list(client, "/qsf/graph/rho_abs", np.abs(state.rho_graph))
    send_list(
        client,
        "/qsf/graph/metrics",
        [state.entropy_bits, state.purity, state.rank, state.nullity, state.component_count],
    )
    send_list(
        client,
        "/qsf/graph/projection",
        [
            projection.frobenius_error,
            projection.trace_distance,
            projection.imaginary_residual,
            projection.rank_deficit,
        ],
    )
    client.send_message("/qsf/graph/negativity", state.negativity(1))


def publish_modal(client: SimpleUDPClient, api: tuple, tracker: object, phase: float) -> None:
    *_, generalized_eigen_residuals = api
    count = 8
    angle = 0.55 * np.sin(phase * 0.7)
    rotation = np.eye(count)
    rotation[:2, :2] = [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    values = np.array([1.0 + 0.0004 * np.sin(phase), 1.0 - 0.0004 * np.sin(phase), 2.2, 3.4, 4.7, 6.1, 7.8, 9.7])
    operator = rotation @ np.diag(values) @ rotation.T
    vectors = rotation
    residuals = generalized_eigen_residuals(operator, None, values, vectors)
    frame = tracker.update(values, vectors, residuals=residuals, topology_id="demo-grid")
    overlap = np.zeros(count)
    angles = np.zeros(count)
    for cluster in frame.clusters:
        cluster_angle = float(np.max(cluster.principal_angles_radians)) if len(cluster.principal_angles_radians) else 0.0
        for index in cluster.basis_indices:
            overlap[index] = cluster.overlap_confidence
            angles[index] = cluster_angle
    client.send_message("/qsf/modal/count", count)
    send_list(client, "/qsf/modal/eigenvalues", frame.eigenvalues)
    send_list(client, "/qsf/modal/stable_ids", frame.mode_stable_ids)
    send_list(client, "/qsf/modal/cluster_ids", frame.cluster_ids_by_mode)
    send_list(client, "/qsf/modal/overlap", overlap)
    send_list(client, "/qsf/modal/angles", angles)
    send_list(client, "/qsf/modal/residuals", frame.residuals)
    client.send_message("/qsf/modal/revision", frame.revision)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7474)
    parser.add_argument("--interval", type=float, default=0.2)
    parser.add_argument("--frames", type=int, default=0, help="0 runs until interrupted")
    parser.add_argument("--foundations-parent", type=Path, default=DEFAULT_FOUNDATIONS_PARENT)
    args = parser.parse_args()

    api = load_foundations(args.foundations_parent)
    ModalSubspaceTracker = api[4]
    ModalTrackingConfig = api[5]
    tracker = ModalSubspaceTracker(ModalTrackingConfig(relative_gap_tolerance=1.0e-2))
    client = SimpleUDPClient(args.host, args.port)
    client.send_message("/qsf/status", "foundations evaluator online")
    frame_index = 0
    try:
        while args.frames == 0 or frame_index < args.frames:
            phase = frame_index * 0.12
            publish_graph(client, api, phase)
            publish_modal(client, api, tracker, phase)
            client.send_message("/qsf/status", f"frame {frame_index} · graph + modal diagnostics")
            frame_index += 1
            time.sleep(max(args.interval, 0.01))
    except KeyboardInterrupt:
        client.send_message("/qsf/status", "publisher stopped")
    finally:
        client._sock.close()


if __name__ == "__main__":
    main()
