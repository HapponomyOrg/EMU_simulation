from abc import ABC, abstractmethod

from emusim.cockpit.supply.data_collector import DataCollector
from emusim.cockpit.supply.data_generator import DataGenerator


class Simulator(ABC):

    def __init__(self, generator: DataGenerator, collector: DataCollector):
        self.__cycles: int = 0
        self.__generator: DataGenerator = generator
        self.__collector: DataCollector = collector

    @property
    def generator(self) -> DataGenerator:
        return self.__generator

    @property
    def collector(self) -> DataCollector:
        return self.__collector

    @abstractmethod
    def process_cycle(self, cycle: int) -> bool:
        pass

    def run_simulation(self):
        current_cycle: int = 0

        while current_cycle < self.__cycles and self.process_cycle(current_cycle):
            self.collector.collect_data()
            self.generator.generate_next()
            current_cycle += 1

        self.collector.collect_data()