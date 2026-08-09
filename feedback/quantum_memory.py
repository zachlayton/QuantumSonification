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
    # At 100 Hz, an unbounded list retains hundreds of megabytes within
    # minutes. With decay=0.7, contributions older than this window are far
    # below floating-point relevance, so bounding it does not alter the live
    # musical behaviour.
    max_snapshots: int | None = 512
    _weighted_total: object = field(default=None, init=False, repr=False)
    _weight_total: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self):
        if self.max_snapshots is not None and self.max_snapshots > 0:
            overflow = len(self.snapshots) - self.max_snapshots
            if overflow > 0:
                del self.snapshots[:overflow]
        self._rebuild_weighted_cache()

    def _rebuild_weighted_cache(self):
        self._weighted_total = None
        self._weight_total = 0.0
        for snapshot in self.snapshots:
            rho = np.asarray(snapshot.rho, dtype=complex)
            if self._weighted_total is None:
                self._weighted_total = rho.copy()
                self._weight_total = 1.0
            else:
                self._weighted_total = rho + self.decay * self._weighted_total
                self._weight_total = 1.0 + self.decay * self._weight_total

    def encode(self, rho, hamiltonian=None, audio_descriptor=None, events=None, metrics=None):
        rho_array = np.array(rho, dtype=complex)
        snapshot = QuantumSnapshot(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            rho=rho_array,
            hamiltonian=hamiltonian,
            audio_descriptor=audio_descriptor,
            events=events or [],
            metrics=metrics or {},
        )
        if self._weighted_total is None:
            self._weighted_total = rho_array.copy()
            self._weight_total = 1.0
        else:
            self._weighted_total = rho_array + self.decay * self._weighted_total
            self._weight_total = 1.0 + self.decay * self._weight_total
        self.snapshots.append(snapshot)
        if self.max_snapshots is not None and self.max_snapshots > 0:
            overflow = len(self.snapshots) - self.max_snapshots
            if overflow > 0:
                if overflow == 1:
                    dropped = self.snapshots[0]
                    dropped_weight = self.decay ** self.max_snapshots
                    self._weighted_total = (
                        self._weighted_total - dropped_weight * dropped.rho
                    )
                    self._weight_total -= dropped_weight
                    del self.snapshots[0]
                else:
                    del self.snapshots[:overflow]
                    self._rebuild_weighted_cache()
        return snapshot

    def size(self):
        return len(self.snapshots)

    def latest(self):
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def weighted_density_matrix(self):
        if self._weighted_total is None or self._weight_total <= 0.0:
            return None

        total = self._weighted_total / self._weight_total

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
