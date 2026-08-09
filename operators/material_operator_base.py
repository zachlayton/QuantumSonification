from abc import ABC, abstractmethod


class MaterialOperator(ABC):

    @abstractmethod
    def apply(self, descriptor):
        pass