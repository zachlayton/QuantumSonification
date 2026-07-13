from dataclasses import replace

from operators.operator import MaterialOperator


class Interpolate(MaterialOperator):

    def __init__(self, target, amount):

        self.target = target
        self.amount = amount

    def lerp(self, a, b):

        return a + (b - a) * self.amount

    def apply(self, descriptor):

        return replace(

            descriptor,

            decay=self.lerp(descriptor.decay,
                            self.target.decay),

            brightness=self.lerp(
                descriptor.brightness,
                self.target.brightness),

            damping=self.lerp(
                descriptor.damping,
                self.target.damping),

            density=self.lerp(
                descriptor.density,
                self.target.density),

            space=self.lerp(
                descriptor.space,
                self.target.space),

            balance=self.lerp(
                descriptor.balance,
                self.target.balance),

            transition_density=self.lerp(
                descriptor.transition_density,
                self.target.transition_density),
        )