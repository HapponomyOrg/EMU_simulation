from __future__ import annotations

from typing import TYPE_CHECKING

from .. import DataGenerator

if TYPE_CHECKING:
    from . import EuroEconomy


class SimpleDataGenerator(DataGenerator):

    def __init__(self, economy: EuroEconomy):
        self.__economy = economy
        self.growth_influence_rate: float = 0.0

    def generate_next(self):
        self.__economy.inflation += self.__economy.inflation * self.__economy.real_growth * self.growth_influence_rate