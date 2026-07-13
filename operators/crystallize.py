from dataclasses import replace

from operators.operator import MaterialOperator


def clamp01(x):
    return max(0.0, min(1.0, x))


class Crystallize(MaterialOperator):
    def __init__(self, amount=0.1):
        self.amount = amount

    def apply(self, descriptor):
        return replace(
            descriptor,
            density=clamp01(descriptor.density + self.amount),
            damping=clamp01(descriptor.damping - self.amount),
            transition_density=clamp01(
                descriptor.transition_density - self.amount
            ),
            balance=clamp01(
                descriptor.balance + self.amount * (0.5 - descriptor.balance)
            ),
        )