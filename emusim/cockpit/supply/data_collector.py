from __future__ import annotations

from decimal import *
from collections import OrderedDict as OrdDict
from typing import List, KeysView, OrderedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Simulator


class DataCollector():

    def __init__(self, simulator: Simulator):
        self.__simulator = simulator
        self.__data_dict: OrderedDict[str, OrderedDict[str, List[Decimal]]] = OrdDict()
        self.__data_structure: OrderedDict[str, OrderedDict[str, bool]] = OrdDict()

    @property
    def simulator(self) -> Simulator:
        return self.__simulator

    @property
    def data_structure(self) -> OrderedDict[str, OrderedDict[str, bool]]:
        return self.__data_structure

    @property
    def size(self) -> int:
        if len(self.get_categories()) > 0:
            category: str = list(self.get_categories())[0]

            if len(self.get_data_fields(category)) > 0:
                return len(self.get_data_series(category, list(self.get_data_fields(category))[0]))

        return 0

    def set_collect_data(self, category: str, data_field: str, collect: bool):
        if not category in self.data_structure:
            self.data_structure[category] = OrdDict()

        self.data_structure[category][data_field] = collect

    def add_data(self, category: str, data_field: str, data: Decimal):
        if not category in self.__data_dict:
            self.__data_dict[category] = OrdDict()

        if not data_field in self.__data_dict[category]:
            self.__data_dict[category][data_field] = []

        self.__data_dict[category][data_field].append(data)

    def get_categories(self) -> KeysView[str]:
        return self.__data_dict.keys()

    def get_data_fields(self, category: str) -> KeysView[str]:
        return self.__data_dict[category].keys()

    def get_data_series(self, category: str, data_field: str) -> List[Decimal]:
        if category in self.__data_dict and data_field in self.__data_dict[category]:
            return self.__data_dict[category][data_field]
        else:
            return []

    def collect_data(self):
        for category in self.data_structure.keys():
            for data_field in self.data_structure[category].keys():
                if self.data_structure[category][data_field]:
                    self.add_data(category, data_field, self.simulator.data(category, data_field))

    def clear(self):
        self.__data_dict.clear()