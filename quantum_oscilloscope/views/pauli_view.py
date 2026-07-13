from __future__ import annotations

from typing import Any

from qmw.core import QuantumStateFrame


class PauliView:
    """Optional semantic Pauli-axis aliases for the Hamiltonian state."""

    def send(self, frame: QuantumStateFrame, osc: Any, visual_osc: Any, config: Any) -> None:
        if not config.send_pauli_aliases:
            return

        hamiltonian = frame.hamiltonian
        if hamiltonian is None or not hasattr(hamiltonian, "as_pauli_terms"):
            return

        terms = hamiltonian.as_pauli_terms()
        osc.send_message("/qmw/hamiltonian/pauli_x", float(terms.get("X", 0.0)))
        osc.send_message("/qmw/hamiltonian/pauli_y", float(terms.get("Y", 0.0)))
        osc.send_message("/qmw/hamiltonian/pauli_z", float(terms.get("Z", 0.0)))

