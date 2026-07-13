import numpy as np


class EventDetector:
    def __init__(
        self,
        purity_threshold=0.03,
        coherence_threshold=0.05,
        entropy_threshold=0.03,
        entanglement_threshold=0.05,
        steady_state_threshold=0.01,
        trajectory_speed_threshold=0.25,
        trajectory_acceleration_threshold=0.25,
        trajectory_turn_threshold=1.2,
    ):
        self.purity_threshold = purity_threshold
        self.coherence_threshold = coherence_threshold
        self.entropy_threshold = entropy_threshold
        self.entanglement_threshold = entanglement_threshold
        self.steady_state_threshold = steady_state_threshold
        self.trajectory_speed_threshold = trajectory_speed_threshold
        self.trajectory_acceleration_threshold = trajectory_acceleration_threshold
        self.trajectory_turn_threshold = trajectory_turn_threshold
        self.previous = None

    def purity(self, rho):
        return float(np.real(np.trace(rho @ rho)))

    def coherence_l1(self, rho):
        off_diag = rho.copy()
        np.fill_diagonal(off_diag, 0.0)
        return float(np.sum(np.abs(off_diag)))

    def entropy(self, rho):
        eigenvalues = np.linalg.eigvalsh(rho)
        eigenvalues = np.clip(eigenvalues, 1e-12, 1.0)
        return float(-np.sum(eigenvalues * np.log2(eigenvalues)))

    def detect(self, rho=None, metrics=None, audio_descriptor=None):
        if metrics is None:
            metrics = {}

        if rho is not None:
            metrics.setdefault("purity", self.purity(rho))
            metrics.setdefault("coherence", self.coherence_l1(rho))
            metrics.setdefault("entropy", self.entropy(rho))

        events = []

        if self.previous is not None:
            dp = metrics.get("purity", 0.0) - self.previous.get("purity", 0.0)
            dc = metrics.get("coherence", 0.0) - self.previous.get("coherence", 0.0)
            de = metrics.get("entropy", 0.0) - self.previous.get("entropy", 0.0)

            if abs(dp) >= self.purity_threshold:
                events.append("purity_shift")
                if dp > 0:
                    events.append("recoherence_tendency")
                else:
                    events.append("decoherence_tendency")

            if abs(dc) >= self.coherence_threshold:
                events.append("coherence_shift")
                if dc > 0:
                    events.append("coherence_birth")
                else:
                    events.append("coherence_loss")

            if abs(de) >= self.entropy_threshold:
                events.append("entropy_shift")
                if de > 0:
                    events.append("entropy_growth")
                else:
                    events.append("entropy_reduction")

            if "entanglement" in metrics and "entanglement" in self.previous:
                dent = metrics["entanglement"] - self.previous["entanglement"]

                if abs(dent) >= self.entanglement_threshold:
                    events.append("entanglement_shift")
                    if dent > 0:
                        events.append("entanglement_birth")
                    else:
                        events.append("entanglement_death")

            total_change = abs(dp) + abs(dc) + abs(de)

            if total_change <= self.steady_state_threshold:
                events.append("steady_state")

        if audio_descriptor is not None:
            if audio_descriptor.loudness > 0.08:
                events.append("audio_excitation")

            if audio_descriptor.groove_stability > 0.9:
                events.append("rhythmic_lock")
            # trajectory-based events
            speed = metrics.get("trajectory_speed", 0.0)
            acceleration = metrics.get("trajectory_acceleration", 0.0)
            turn = metrics.get("trajectory_direction_change", 0.0)

            if speed >= self.trajectory_speed_threshold:
                events.append("trajectory_motion")

            if acceleration >= self.trajectory_acceleration_threshold:
                events.append("trajectory_acceleration")

            if turn >= self.trajectory_turn_threshold:
                events.append("trajectory_turn")

            if (
                speed < self.steady_state_threshold
                and acceleration < self.steady_state_threshold
            ):
                events.append("stable_attractor")

        self.previous = dict(metrics)

        return {
            "events": events,
            "metrics": metrics,
        }