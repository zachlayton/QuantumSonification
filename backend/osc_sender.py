from __future__ import annotations

from pythonosc.udp_client import SimpleUDPClient

from engine.process_graph import QuantumProcessGraph

class QMWOSCSender:
    """Sends QMW process topology and material descriptors to Max/MSP."""

    def __init__(self, host: str = "127.0.0.1", port: int = 7400) -> None:
        self.client = SimpleUDPClient(host, port)
        self.visual_osc = SimpleUDPClient("127.0.0.1", 7401)

    def send_graph(self, graph: QuantumProcessGraph) -> None:
        self.client.send_message(
            "/qmw/process/begin",
            [graph.name, len(graph.nodes), len(graph.edges)],
        )

        for node in graph.nodes.values():
            payload = [
                node.node_id,
                node.kind,
                node.label,
                node.depth,
                len(node.qubits),
                *node.qubits,
            ]

            self.client.send_message(
                "/qmw/process/node",
                payload,
            )

        for edge in graph.edges:
            self.client.send_message(
                "/qmw/process/edge",
                [
                    edge.source,
                    edge.target,
                    edge.relation,
                    edge.system,
                ],
            )

        self.client.send_message(
            "/qmw/process/end",
            [graph.name],
        )

    def send_snapshot(self, frame: int, snapshot) -> None:
        self.client.send_message(
            "/qmw/process/frame",
            [
                frame,
                snapshot.shannon_entropy,
                snapshot.phase_dispersion,
                snapshot.process_complexity,
                snapshot.purity_proxy,
            ],
        )

        # Each qubit gets its own OSC address.
        # Max receives:
        # /qmw/process/qubit/0 frame x y z
        # /qmw/process/qubit/1 frame x y z
        # /qmw/process/qubit/2 frame x y z
        # /qmw/process/qubit/3 frame x y z
        for qubit, (x, y, z) in enumerate(snapshot.bloch_vectors):
            self.client.send_message(
                f"/qmw/process/qubit/{qubit}",
                [frame, x, y, z],
            )

        for pair in snapshot.joint_pairs:
            self.client.send_message(
                "/qmw/process/joint",
                [
                    frame,
                    pair["q0"],
                    pair["q1"],
                    pair["mutual_information"],
                    pair["zz_correlation"],
                    pair["shared_resonance"],
                ],
            )

        material = snapshot.material
        
        print(
    		f"OSC → /qmw/process/qubit/{qubit} "
    		f"[{frame}, {x:+.3f}, {y:+.3f}, {z:+.3f}]"
)

        self.client.send_message(
            "/qmw/process/material",
            [
                frame,
                material["mode_family"],
                material["decay"],
                material["brightness"],
                material["damping"],
                material["density"],
                material["space"],
            ],
        )

        self.client.send_message(
            "/qmw/process/state",
            [
                frame,
                snapshot.state_dimension,
                snapshot.schmidt_proxy,
                snapshot.phase_centroid,
                snapshot.entangling_power,
            ],
        )