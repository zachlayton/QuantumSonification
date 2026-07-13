from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from qmw.core.measurement_event import BitArray, ShotBitArray
from qmw.core.primitives import SamplerResult


BitPredicate = Callable[[BitArray], bool]


def slice_bits(register: ShotBitArray, bit_indices: Sequence[int]) -> ShotBitArray:
    """Select bit positions from every shot of one classical register."""
    return register.slice_bits(bit_indices)


def slice_shots(register: ShotBitArray, shot_indices: Sequence[int]) -> ShotBitArray:
    """Select specific shots from one classical register."""
    return register.slice_shots(shot_indices)


def post_select(
    target: ShotBitArray,
    condition: ShotBitArray,
    *,
    equals: str | BitArray = "1",
) -> ShotBitArray:
    """Keep target shots where the condition register equals a bit pattern."""
    expected = equals if isinstance(equals, BitArray) else BitArray.from_string(equals)
    mask = np.array([shot == expected for shot in condition.shots], dtype=bool)
    return target[mask]


def post_select_where(
    target: ShotBitArray,
    condition: ShotBitArray,
    predicate: BitPredicate,
) -> ShotBitArray:
    """Keep target shots where a predicate accepts the condition register."""
    mask = np.array([bool(predicate(shot)) for shot in condition.shots], dtype=bool)
    return target[mask]


def merge_registers(registers: Sequence[ShotBitArray]) -> ShotBitArray:
    """Concatenate bitstrings from multiple registers shot by shot."""
    return ShotBitArray.concatenate_bits(registers)


def expectation_values(
    register: ShotBitArray,
    observables: Sequence[Any],
) -> list[float]:
    """Evaluate diagonal I/Z observables over shot histories."""
    return register.expectation_values(observables)


@dataclass(frozen=True)
class QuantumDataOperator:
    """First-class compositional operator for quantum data structures."""

    name: str
    function: Callable[..., Any]
    input_kind: str
    output_kind: str
    description: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.function(*args, **kwargs)


DATA_OPERATORS: dict[str, QuantumDataOperator] = {
    "slice_bits": QuantumDataOperator(
        name="slice_bits",
        function=slice_bits,
        input_kind="ShotBitArray",
        output_kind="ShotBitArray",
        description="Select bit positions from every shot of a register.",
    ),
    "slice_shots": QuantumDataOperator(
        name="slice_shots",
        function=slice_shots,
        input_kind="ShotBitArray",
        output_kind="ShotBitArray",
        description="Select specific shots from a register history.",
    ),
    "post_select": QuantumDataOperator(
        name="post_select",
        function=post_select,
        input_kind="ShotBitArray pair",
        output_kind="ShotBitArray",
        description="Filter one register by a condition register bit pattern.",
    ),
    "post_select_where": QuantumDataOperator(
        name="post_select_where",
        function=post_select_where,
        input_kind="ShotBitArray pair",
        output_kind="ShotBitArray",
        description="Filter one register by a predicate over another register.",
    ),
    "merge_registers": QuantumDataOperator(
        name="merge_registers",
        function=merge_registers,
        input_kind="ShotBitArray list",
        output_kind="ShotBitArray",
        description="Concatenate multiple registers shot by shot.",
    ),
    "expectation_values": QuantumDataOperator(
        name="expectation_values",
        function=expectation_values,
        input_kind="ShotBitArray + diagonal observables",
        output_kind="float list",
        description="Compute expectation values for diagonal I/Z observables.",
    ),
}


def data_operator(name: str) -> QuantumDataOperator:
    return DATA_OPERATORS[name]


def data_operator_menu_items() -> list[dict[str, str]]:
    return [
        {
            "name": operator.name,
            "input_kind": operator.input_kind,
            "output_kind": operator.output_kind,
            "description": operator.description,
        }
        for operator in DATA_OPERATORS.values()
    ]


@dataclass
class QuantumDataProcessing:
    """Named processing stage between sampler/state engines and OSC routing."""

    sampler_result: SamplerResult | None = None
    registers: dict[str, ShotBitArray] = field(default_factory=dict)

    @classmethod
    def from_sampler_result(cls, result: SamplerResult) -> "QuantumDataProcessing":
        return cls(
            sampler_result=result,
            registers=dict(result.register_shots),
        )

    @classmethod
    def from_registers(
        cls,
        registers: Mapping[str, ShotBitArray],
    ) -> "QuantumDataProcessing":
        return cls(registers=dict(registers))

    def register(self, name: str) -> ShotBitArray:
        if name in self.registers:
            return self.registers[name]

        alias = name.removeprefix("measurement_")
        return self.registers[alias]

    def slice_bits(self, register_name: str, bit_indices: Sequence[int]) -> ShotBitArray:
        return slice_bits(self.register(register_name), bit_indices)

    def slice_shots(
        self,
        register_name: str,
        shot_indices: Sequence[int],
    ) -> ShotBitArray:
        return slice_shots(self.register(register_name), shot_indices)

    def post_select(
        self,
        target_register: str,
        condition_register: str,
        *,
        equals: str | BitArray = "1",
    ) -> ShotBitArray:
        return post_select(
            self.register(target_register),
            self.register(condition_register),
            equals=equals,
        )

    def merge_registers(self, register_names: Sequence[str]) -> ShotBitArray:
        return merge_registers([self.register(name) for name in register_names])

    def expectation_values(
        self,
        register_name: str,
        observables: Sequence[Any],
    ) -> list[float]:
        return expectation_values(self.register(register_name), observables)
