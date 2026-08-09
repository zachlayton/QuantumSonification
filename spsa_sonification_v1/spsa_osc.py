"""Command-line Qiskit to OSC SPSA sonification demo."""

from __future__ import annotations

import argparse
import time

import numpy as np
from pythonosc.udp_client import SimpleUDPClient

from .feedback import (
    AudioFeedbackReceiver,
    AudioFeedbackState,
    controls_from_feedback,
)
from .osc_publisher import SPSAOSCPublisher
from .spsa_engine import build_demo_problem, compute_spsa_step, default_estimator


class NullOSCClient:
    """No-op client used to inspect the optimizer without sending UDP."""

    def send_message(self, address: str, value: object) -> None:
        del address, value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=17420)
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--epsilon", type=float, default=0.12)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=0.18)
    parser.add_argument("--gesture-seconds", type=float, default=0.35)
    parser.add_argument("--step-pause", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=1933)
    parser.add_argument("--feedback-host", default="127.0.0.1")
    parser.add_argument("--feedback-port", type=int, default=17421)
    parser.add_argument("--feedback-mix", type=float, default=0.8)
    parser.add_argument("--no-feedback", action="store_true")
    parser.add_argument("--no-osc", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.steps <= 0:
        raise SystemExit("--steps must be positive")

    circuit, observable, theta = build_demo_problem()
    estimator = default_estimator()
    rng = np.random.default_rng(args.seed)
    client = NullOSCClient() if args.no_osc else SimpleUDPClient(args.host, args.port)
    publisher = SPSAOSCPublisher(client)
    feedback_enabled = not args.no_feedback and not args.no_osc
    feedback_state = AudioFeedbackState()
    receiver = None
    if feedback_enabled:
        receiver = AudioFeedbackReceiver(
            feedback_state, host=args.feedback_host, port=args.feedback_port
        )
        receiver.start()

    controls = controls_from_feedback(
        feedback_state.snapshot(),
        base_epsilon=args.epsilon,
        base_batch_size=args.batch_size,
        base_learning_rate=args.learning_rate,
        mix=0.0,
    )

    print(
        f"SPSA sonification: {args.steps} steps, {args.batch_size} probe pairs/step, "
        f"OSC {args.host}:{args.port}{' disabled' if args.no_osc else ''}, "
        f"feedback {'on' if feedback_enabled else 'off'}"
    )
    try:
        for index in range(args.steps):
            step = compute_spsa_step(
                estimator=estimator,
                circuit=circuit,
                observable=observable,
                theta=theta,
                epsilon=controls.epsilon,
                batch_size=controls.batch_size,
                learning_rate=controls.learning_rate,
                rng=rng,
                step_index=index,
                perturbation_polarity=controls.perturbation_polarity,
            )
            publisher.publish(step, gesture_seconds=args.gesture_seconds)
            direction = "down" if step.objective_after <= step.objective_before else "up"
            time.sleep(max(0.0, args.step_pause))

            feedback = feedback_state.snapshot()
            controls = controls_from_feedback(
                feedback,
                base_epsilon=args.epsilon,
                base_batch_size=args.batch_size,
                base_learning_rate=args.learning_rate,
                mix=args.feedback_mix if feedback.sequence else 0.0,
            )
            print(
                f"{index:03d} objective {step.objective_before:+.5f} -> "
                f"{step.objective_after:+.5f} ({direction}) |g|={step.gradient_norm:.5f} "
                f"audio[e={feedback.energy:.2f} c={feedback.centroid:.2f} "
                f"f={feedback.flux:.2f} r={feedback.resonance:.2f}] "
                f"next[eps={controls.epsilon:.3f} batch={controls.batch_size} "
                f"lr={controls.learning_rate:.3f}]"
            )
            theta = step.theta_after
    finally:
        if receiver is not None:
            receiver.close()


if __name__ == "__main__":
    main()
