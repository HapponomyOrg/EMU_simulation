from abc import ABC, abstractmethod

from . import DataCollector


class DataGenerator(ABC):

    @abstractmethod
    def generate_next(self):
        pass

    @property
    def data_collector(self) -> DataCollector:
        return self.__data_collector

    @data_collector.setter
    def data_collector(self, data_collector):
        self.__data_collector = data_collector
