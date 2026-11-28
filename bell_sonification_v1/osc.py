"""Stream shots to Max over OSC, paced in real time.

Messages (all under /bell):
  /bell/provenance  source backend job_id created
  /bell/shot        index a b agree theta
  /bell/correlation E          running mean of +1 (agree) / -1 (disagree)
"""

from __future__ import annotations

import time
from typing import Sequence

from .source import ShotRun


def stream(runs: Sequence[ShotRun], host: str = "127.0.0.1", port: int = 7400,
           rate: float = 8.0, window: int = 32) -> None:
    from pythonosc.udp_client import SimpleUDPClient
    client = SimpleUDPClient(host, port)
    p = runs[0].provenance
    client.send_message("/bell/provenance", [str(p.get("source", "")), str(p.get("backend", "")),
                                            str(p.get("job_id", "")), str(p.get("created", ""))])
    recent: list[int] = []
    k = 0
    for run in runs:
        for a, b in run.shots:
            agree = int(a == b)
            recent = (recent + [1 if agree else -1])[-window:]
            client.send_message("/bell/shot", [k, int(a), int(b), agree, float(run.theta)])
            client.send_message("/bell/correlation", [sum(recent) / len(recent)])
            k += 1
            time.sleep(1.0 / rate)
