from abc import ABC, abstractmethod
from decimal import *

from emusim.cockpit.supply import DataCollector, DataGenerator
from emusim.cockpit.utilities.cycles import Period, Interval


class Simulator(ABC):

    def __init__(self, generator: DataGenerator):
        self.collect_interval: Period = Period(1, Interval.DAY)
        self.__generator: DataGenerator = generator
        self.__collector = DataCollector(self)
        self._initialize_data_structure()

    @property
    def generator(self) -> DataGenerator:
        return self.__generator

    @property
    def collector(self) -> DataCollector:
        return self.__collector

    @collector.setter
    def collector(self, collector: DataCollector):
        self.__collector = collector

    @abstractmethod
    def _initialize_data_structure(self):
        """Initialize the data structure with flags on what data needs to be collected.
        This must only be done once."""
        pass

    @abstractmethod
    def data(self, category: str, data_field: str) -> Decimal:
        pass

    @abstractmethod
    def process_cycle(self, cycle: int) -> bool:
        pass

    def run_simulation(self, cycles: int):
        current_cycle: int = 0
        success: bool = True

        self.collector.clear()

        while success and current_cycle < cycles:
            success = self.process_cycle(current_cycle)

            if current_cycle == 0 or self.collect_interval.period_complete(current_cycle) or not success:
                self.collector.collect_data()

            self.generator.generate_next()
            current_cycle += 1