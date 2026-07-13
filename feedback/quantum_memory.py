from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class QuantumSnapshot:
    timestamp: str
    rho: object
    hamiltonian: object = None
    audio_descriptor: object = None
    events: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


@dataclass
class QuantumMemory:
    decay: float = 0.7
    snapshots: list = field(default_factory=list)

    def encode(self, rho, hamiltonian=None, audio_descriptor=None, events=None, metrics=None):
        snapshot = QuantumSnapshot(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            rho=np.array(rho, dtype=complex),
            hamiltonian=hamiltonian,
            audio_descriptor=audio_descriptor,
            events=events or [],
            metrics=metrics or {},
        )
        self.snapshots.append(snapshot)
        return snapshot

    def size(self):
        return len(self.snapshots)

    def latest(self):
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def weighted_density_matrix(self):
        if not self.snapshots:
            return None

        weights = []
        total = np.zeros_like(self.snapshots[0].rho, dtype=complex)

        for i, snapshot in enumerate(reversed(self.snapshots)):
            weight = self.decay ** i
            weights.append(weight)
            total += weight * snapshot.rho

        total = total / sum(weights)

        trace = np.trace(total)
        if abs(trace) > 1e-12:
            total = total / trace

        return total

    def purity(self, rho=None):
        if rho is None:
            rho = self.weighted_density_matrix()
        if rho is None:
            return 0.0
        return float(np.real(np.trace(rho @ rho)))

    def coherence_l1(self, rho=None):
        if rho is None:
            rho = self.weighted_density_matrix()
        if rho is None:
            return 0.0

        off_diag = rho.copy()
        np.fill_diagonal(off_diag, 0.0)
        return float(np.sum(np.abs(off_diag)))

    def populations(self, rho=None):
        if rho is None:
            rho = self.weighted_density_matrix()
        if rho is None:
            return []
        return np.real(np.diag(rho)).tolist()
    
    def annotate_latest(self, events=None, metrics=None):
        if not self.snapshots:
         return

        if events is not None:
           self.snapshots[-1].events = list(events)

        if metrics is not None:
           self.snapshots[-1].metrics = dict(metrics)

    def highest_purity(self):
        if not self.snapshots:
            return None
        return max(
            self.snapshots,
            key=lambda s: self.purity(s.rho),
        )

    def highest_coherence(self):
        if not self.snapshots:
            return None
        return max(
            self.snapshots,
            key=lambda s: self.coherence_l1(s.rho),
        )

    def snapshots_with_event(self, event_name):
        return [
            s for s in self.snapshots
            if event_name in s.events
        ]