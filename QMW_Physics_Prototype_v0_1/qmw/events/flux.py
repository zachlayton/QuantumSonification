"""Hysteretic articulation on calculated regional flux; no random decisions."""
import numpy as np
from qmw.core import PhysicsFrame, PhysicsEvent, EventType


class FlowEventDetector:
    def __init__(self, threshold: float = 0.01, hysteresis: float = 0.5,
                 refractory: float = 0.08, mode_threshold: float | None = None):
        self.threshold = self._positive(threshold, "threshold")
        if not np.isfinite(hysteresis) or not 0 <= hysteresis < 1:
            raise ValueError("Hysteresis must lie in [0,1)")
        if not np.isfinite(refractory) or refractory < 0:
            raise ValueError("Refractory interval must be finite and nonnegative")
        self.hysteresis, self.refractory = hysteresis, refractory
        self.mode_threshold = None if mode_threshold is None else self._positive(mode_threshold, "mode threshold")
        self.reset()

    @staticmethod
    def _positive(value, name):
        value = float(value)
        if not np.isfinite(value) or value <= 0: raise ValueError(f"{name} must be positive and finite")
        return value

    def reset(self):
        self._armed = None
        self._last_fired = None
        self._mode_armed = None
        self._last_time = None
        self._last_sequence = None

    def update(self, previous: PhysicsFrame | None, current: PhysicsFrame) -> list[PhysicsEvent]:
        # Repeated published snapshots are not new physical samples.
        if self._last_sequence == current.sequence:
            return []
        if self._last_time is not None and current.t < self._last_time:
            raise ValueError("Simulation time moved backward; reset event detector first")
        self._last_time, self._last_sequence = current.t, current.sequence
        events = []
        if current.regions is not None and current.regions.incoming_energy_flux is not None:
            flux = np.asarray(current.regions.incoming_energy_flux, dtype=float)
            if not np.isfinite(flux).all(): raise ValueError("Nonfinite regional energy flux")
            if self._armed is None or self._armed.shape != flux.shape:
                baseline = previous.regions.incoming_energy_flux if previous is not None and previous.regions is not None else None
                self._armed = np.ones(flux.shape, dtype=bool) if baseline is None else np.asarray(baseline) < self.threshold
                self._last_fired = np.full(flux.shape, -np.inf)
            self._armed[flux <= self.hysteresis*self.threshold] = True
            ready = self._armed & (flux >= self.threshold) & (current.t-self._last_fired >= self.refractory)
            for i in np.flatnonzero(ready):
                events.append(PhysicsEvent(EventType.ENERGY_ARRIVAL, current.t, float(flux[i]),
                    "regions.incoming_energy_flux", region=int(i),
                    position=float(current.regions.centers[i]), frame_sequence=current.sequence,
                    detail=f"Incoming energy flux {flux[i]:.6g} crossed threshold {self.threshold:.6g}; rearm at {self.hysteresis*self.threshold:.6g}"))
                self._armed[i] = False; self._last_fired[i] = current.t
        if self.mode_threshold is not None and current.modes is not None:
            population = current.modes.populations
            if self._mode_armed is None or self._mode_armed.shape != population.shape:
                baseline = previous.modes.populations if previous is not None and previous.modes is not None else None
                self._mode_armed = np.ones(population.shape,dtype=bool) if baseline is None else baseline < self.mode_threshold
            self._mode_armed[population <= self.hysteresis*self.mode_threshold] = True
            for i in np.flatnonzero(self._mode_armed & (population >= self.mode_threshold)):
                events.append(PhysicsEvent(EventType.MODE_CROSSING,current.t,float(population[i]),
                    "modes.populations",mode=int(i),frame_sequence=current.sequence,
                    detail=f"Named-basis population crossed {self.mode_threshold:.6g}"))
                self._mode_armed[i] = False
        return events
