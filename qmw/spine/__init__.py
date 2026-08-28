"""QMW Dynamical Spine: the single dependency chain

    Generators -> Evolution -> State -> Observables -> Flow -> ...

that every QMW subsystem reads from instead of inventing its own quantum
trajectory. See qmw/spine/experiments/von_neumann_flow_i.py for the first
integrated build: H -> rho -> Pauli/operator velocity -> basis-population
current -> sound, with no projection or geometry layer yet.
"""

from qmw.spine.frame import QuantumFrame, build_frame
from qmw.spine.quantum import Hamiltonian, PauliTerm

__all__ = ["Hamiltonian", "PauliTerm", "QuantumFrame", "build_frame"]
