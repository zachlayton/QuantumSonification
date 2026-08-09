"""OSC contract for correlation/differentiation clock v2."""

from __future__ import annotations

from typing import Any


class CorrelationClockOSCPublisher:
    def __init__(
        self,
        host: str,
        port: int,
        client: Any = None,
        root: str = "/qmw/temporal/v2",
    ) -> None:
        if client is None:
            from pythonosc.udp_client import SimpleUDPClient

            client = SimpleUDPClient(host, port)
        self.client = client
        self.root = root.rstrip("/")

    def publish(self, snapshot: Any) -> None:
        root = self.root
        self.client.send_message(
            f"{root}/snapshot/begin",
            [snapshot.observation, snapshot.relational_time],
        )
        self.client.send_message(
            f"{root}/condition",
            [
                snapshot.clock_phase,
                snapshot.clock_confidence,
                snapshot.conditional_purity,
            ],
        )
        for edge, relation in snapshot.relations.items():
            self.client.send_message(
                f"{root}/relation",
                [
                    edge,
                    relation["correlation"],
                    relation["differentiation"],
                    relation["correlating_accumulator"],
                    relation["differentiating_accumulator"],
                    relation["edge_time"],
                ],
            )
        for tick in snapshot.ticks:
            self.client.send_message(
                f"{root}/tick",
                [
                    tick.tick_id,
                    tick.edge,
                    tick.kind,
                    tick.edge_time,
                    tick.relational_time,
                    tick.correlation,
                    tick.differentiation,
                    tick.strength,
                    tick.midi,
                    tick.velocity,
                    tick.duration_ms,
                ],
            )
        self.client.send_message(
            f"{root}/snapshot/end",
            [snapshot.observation, snapshot.relational_time, len(snapshot.ticks)],
        )
