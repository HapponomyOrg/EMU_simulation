from .euro_economy import EuroEconomy
from ..data_generator import DataGenerator


class SimpleDataGenerator(DataGenerator):

    def __init__(self, economy: EuroEconomy):
        self.__economy = economy
        self.growth_influence_rate: float = 0.0

    def generate_next(self):
        self.__economy.inflation += self.__economy.inflation * self.__economy.real_growth * self.growth_influence_rate