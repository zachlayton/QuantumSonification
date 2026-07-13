from dataclasses import replace

from operators.operator import MaterialOperator


class Diffuse(MaterialOperator):

    def __init__(self, amount=0.1):

        self.amount = amount

    def apply(self, descriptor):

        return replace(

            descriptor,

            density=max(
                0.0,
                descriptor.density-self.amount),

            damping=min(
                1.0,
                descriptor.damping+self.amount)
        )