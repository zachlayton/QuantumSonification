"""Max/MSP-friendly OSC publication for relational snapshots."""

from __future__ import annotations

from typing import Any


class OSCPublisher:
    def __init__(self, host: str, port: int, client: Any = None, root: str = "/qmw/temporal/v1") -> None:
        if client is None:
            try:
                from pythonosc.udp_client import SimpleUDPClient
            except ImportError as exc:
                raise RuntimeError("OSC requested; install python-osc") from exc
            client = SimpleUDPClient(host, port)
        self.client = client
        self.root = root.rstrip("/")

    def publish(self, snapshot: Any) -> None:
        r = self.root
        self.client.send_message(f"{r}/snapshot/begin", snapshot.observation)
        self.client.send_message(f"{r}/clock", [snapshot.clock_phase, snapshot.clock_confidence, snapshot.clock_probability])
        self.client.send_message(f"{r}/conditional/purity", snapshot.conditional_purity)
        for name, state in snapshot.processes.items():
            self.client.send_message(f"{r}/process/{name}", [state["phase"], state["energy"], state["correlation"], state["salience"], state["quantum_drive"]])
        for event in snapshot.events:
            self.client.send_message(f"{r}/event", [event["id"], event["process"], event["midi"], event["velocity"], event["duration_ms"], event["correlation"], event["relational_phase"]])
        for branch in snapshot.branches:
            self.client.send_message(f"{r}/branch", [branch["id"], branch["parent"] or "-", branch["weight"], ",".join(branch["history"])])
        self.client.send_message(f"{r}/snapshot/end", snapshot.observation)
