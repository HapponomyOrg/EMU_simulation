from abc import ABC, abstractmethod

from emusim.cockpit.supply.data_collector import DataCollector
from emusim.cockpit.supply.data_generator import DataGenerator


class Simulator(ABC, DataGenerator, DataCollector):

    @abstractmethod
    def initialize_generator(self):
        pass

    @abstractmethod
    def initialize_collector(self):
        pass