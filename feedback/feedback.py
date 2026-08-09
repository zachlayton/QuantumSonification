from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FeedbackFrame:
    timestamp: str
    audio_descriptor: object
    hamiltonian: object
    bloch: dict


@dataclass
class FeedbackHistory:
    frames: list = field(default_factory=list)
    # Real-time engines can run indefinitely. Keeping every frame makes RSS
    # grow linearly even though all live consumers use only the recent path.
    max_frames: int | None = 512

    def add(self, audio_descriptor, hamiltonian, bloch):
        frame = FeedbackFrame(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            audio_descriptor=audio_descriptor,
            hamiltonian=hamiltonian,
            bloch=bloch,
        )

        self.frames.append(frame)
        if self.max_frames is not None and self.max_frames > 0:
            overflow = len(self.frames) - self.max_frames
            if overflow > 0:
                del self.frames[:overflow]
        return frame

    def size(self):
        return len(self.frames)

    def latest(self):
        if not self.frames:
            return None
        return self.frames[-1]

    def hamiltonian_path(self):
        return [
            frame.hamiltonian.as_pauli_terms()
            for frame in self.frames
        ]

    def bloch_path(self):
        return [
            frame.bloch
            for frame in self.frames
        ]
