"""Optional Everett-style possibility/history bookkeeping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Branch:
    branch_id: str
    parent_id: str | None
    weight: float
    history: list[str] = field(default_factory=list)


class BranchTracker:
    def __init__(self, enabled: bool, threshold: float) -> None:
        self.enabled = enabled
        self.threshold = threshold
        self.active = [Branch("b0", None, 1.0)]
        self.counter = 1

    def update(self, observation: int, candidates: list[tuple[float, Any, float]], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        event_names = [e["process"] for e in events]
        ambiguity = sorted(((score, process.config.name) for score, process, _ in candidates), reverse=True)
        if len(ambiguity) > 1 and ambiguity[1][0] >= self.threshold:
            parent = max(self.active, key=lambda b: b.weight)
            total = max(ambiguity[0][0] + ambiguity[1][0], 1e-12)
            children = []
            for score, name in ambiguity[:2]:
                branch = Branch(f"b{self.counter}", parent.branch_id, parent.weight * score / total, (parent.history + [name])[-32:])
                self.counter += 1
                children.append(branch)
            self.active.remove(parent)
            self.active.extend(children)
            self.active = sorted(self.active, key=lambda b: b.weight, reverse=True)[:16]
        elif event_names:
            for branch in self.active:
                branch.history = (branch.history + event_names)[-32:]
        norm = sum(b.weight for b in self.active) or 1.0
        for branch in self.active:
            branch.weight /= norm
        return [{"id": b.branch_id, "parent": b.parent_id, "weight": b.weight, "history": list(b.history)} for b in self.active]
