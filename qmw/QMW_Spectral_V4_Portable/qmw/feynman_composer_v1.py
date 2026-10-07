"""Constrained interactive composer for QMW Feynman-inspired process graphs.

The composer selects from typed, arity-compatible graph templates and requires
an explicit commit to attach one topology to a declared Pauli channel. It is a
performance/compositional configuration layer, not quantum evolution and not
a free-form claim that any drawn graph is a calculated field-theory process.
"""

from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import TYPE_CHECKING, Any, Sequence

from .feynman_process_graph import ExternalLeg, InternalLine, ProcessGraph, ProcessVertex, tree_graph

if TYPE_CHECKING:
    from .qmw_interaction_engine import InteractionEngine


COMPOSER_CONTROL_PORT = 17874
COMPOSER_ROOT = "/qmw/interaction/composer/v1"


@dataclass(frozen=True)
class ComposerTemplate:
    """One permitted graph topology for one existing Pauli interaction channel."""

    identifier: str
    display_name: str
    pauli_label: str
    inputs: int
    outputs: int
    graph: ProcessGraph

    def __post_init__(self) -> None:
        if self.graph.input_count != self.inputs or self.graph.output_count != self.outputs:
            raise ValueError("composer template graph ports must match its declared interaction arity.")


def _one_loop_graph(identifier: str, *, inputs: int, outputs: int, coupling_label: str) -> ProcessGraph:
    """A typed symbolic one-loop correction sharing a tree's external ports."""

    vertices = (
        ProcessVertex("entry", coupling_label),
        ProcessVertex("loop", coupling_label),
        ProcessVertex("exit", coupling_label),
    )
    legs = tuple(
        [ExternalLeg(f"in{index}", "entry", "incoming", "modal_excitation") for index in range(inputs)]
        + [ExternalLeg(f"out{index}", "exit", "outgoing", "modal_excitation") for index in range(outputs)]
    )
    lines = (
        InternalLine("entry_to_loop", "entry", "loop", "modal_excitation", "modal", "G_entry"),
        InternalLine("loop_to_exit", "loop", "exit", "modal_excitation", "modal", "G_exit"),
        InternalLine("loop_return", "exit", "loop", "modal_excitation", "modal", "G_loop"),
    )
    return ProcessGraph(identifier, vertices, legs, lines, symmetry_factor=2.0, model_level="symbolic")


def default_composer_templates() -> tuple[ComposerTemplate, ...]:
    """Return the deliberately small initial performance vocabulary."""

    channel_specs = (
        ("XYXY", "scattering", 2, 2),
        ("ZZXX", "scattering", 2, 2),
        ("IXXX", "splitting", 1, 2),
        ("XXIX", "fusion", 2, 1),
    )
    templates: list[ComposerTemplate] = []
    for label, kind, inputs, outputs in channel_specs:
        tree_id = f"{label.lower()}_tree_{kind}"
        templates.append(ComposerTemplate(
            tree_id, f"{label}  tree {kind}", label, inputs, outputs,
            tree_graph(tree_id, inputs=inputs, outputs=outputs, coupling_label=label),
        ))
        loop_id = f"{label.lower()}_one_loop_{kind}"
        templates.append(ComposerTemplate(
            loop_id, f"{label}  one-loop {kind}", label, inputs, outputs,
            _one_loop_graph(loop_id, inputs=inputs, outputs=outputs, coupling_label=label),
        ))
    return tuple(templates)


class FeynmanComposerV1:
    """Select and explicitly commit one permitted topology at a time."""

    def __init__(self, templates: Sequence[ComposerTemplate] | None = None) -> None:
        selected = tuple(default_composer_templates() if templates is None else templates)
        if not selected:
            raise ValueError("a Feynman composer needs at least one template.")
        identifiers = [template.identifier for template in selected]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("composer template identifiers must be unique.")
        self.templates = {template.identifier: template for template in selected}
        self.selected_identifier = identifiers[0]
        self._lock = threading.RLock()

    @property
    def selected(self) -> ComposerTemplate:
        with self._lock:
            return self.templates[self.selected_identifier]

    def select(self, identifier: str) -> ComposerTemplate:
        with self._lock:
            if identifier not in self.templates:
                raise ValueError(f"unknown composer graph template {identifier!r}.")
            self.selected_identifier = identifier
            return self.templates[identifier]

    def commit(self, engine: "InteractionEngine") -> ComposerTemplate:
        """Apply the selected topology through the engine's guarded channel seam."""

        with self._lock:
            template = self.templates[self.selected_identifier]
            engine.set_process_graph(template.pauli_label, template.graph)
            return template


class FeynmanComposerOSCControlV1:
    """Small persistent OSC control server for the native composer front end."""

    def __init__(self, composer: FeynmanComposerV1, engine: "InteractionEngine", *, host: str = "127.0.0.1", port: int = COMPOSER_CONTROL_PORT) -> None:
        self.composer = composer
        self.engine = engine
        self.host = host
        self.port = int(port)
        self.last_status = "ready"
        self._server: Any | None = None
        self._thread: threading.Thread | None = None

    def select(self, identifier: str) -> ComposerTemplate:
        template = self.composer.select(str(identifier))
        self.last_status = f"selected {template.identifier}"
        return template

    def commit(self) -> ComposerTemplate:
        template = self.composer.commit(self.engine)
        self.last_status = f"committed {template.identifier}"
        return template

    def _select_message(self, _address: str, *values: object) -> None:
        try:
            self.select(str(values[0]))
        except (IndexError, ValueError) as error:
            self.last_status = f"selection rejected: {error}"

    def _commit_message(self, _address: str, *_values: object) -> None:
        try:
            self.commit()
        except ValueError as error:
            self.last_status = f"commit rejected: {error}"

    def start(self) -> None:
        if self._server is not None:
            return
        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import ThreadingOSCUDPServer

        dispatcher = Dispatcher()
        dispatcher.map(f"{COMPOSER_ROOT}/select", self._select_message)
        dispatcher.map(f"{COMPOSER_ROOT}/commit", self._commit_message)
        self._server = ThreadingOSCUDPServer((self.host, self.port), dispatcher)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self._server = None
        self._thread = None


__all__ = [
    "COMPOSER_CONTROL_PORT", "COMPOSER_ROOT", "ComposerTemplate", "FeynmanComposerOSCControlV1",
    "FeynmanComposerV1", "default_composer_templates",
]
