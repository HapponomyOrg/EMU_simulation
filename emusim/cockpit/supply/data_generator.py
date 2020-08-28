from abc import ABC, abstractmethod


class DataGenerator(ABC):

    @abstractmethod
    def generate_next(self):
        pass
