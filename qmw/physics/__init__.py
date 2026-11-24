"""QMW physics core: models that evolve a state and report observables.

Models never produce audio parameters. See qmw.physics.engine.FieldEngine for the
loop that turns a model into a stream of FieldFrames.
"""
from qmw.physics.base import ControlState, PhysicsModel
from qmw.physics.engine import FieldEngine

__all__ = ["ControlState", "FieldEngine", "PhysicsModel"]
