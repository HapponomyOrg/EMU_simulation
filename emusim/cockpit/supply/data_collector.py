from abc import ABC, abstractmethod
from collections import OrderedDict as OrdDict
from typing import List, KeysView, OrderedDict


class DataCollector(ABC):

    def __init__(self):
        self.__data_dict: OrderedDict[str, OrderedDict[str, List[float]]] = OrdDict()

    @property
    @abstractmethod
    def data_structure(self) -> OrderedDict[str, OrderedDict[str, bool]]:
        pass

    def set_collect_data(self, category: str, data_field: str, collect: bool):
        self.data_structure[category][data_field] = collect

    def add_category(self, category: str):
        if category not in self.__data_dict:
            self.__data_dict[category] = OrdDict()

    def add_data(self, category: str, data_field: str, data: float):
        if not category in self.__data_dict:
            self.__data_dict[category] = OrdDict([(data_field, [])])

        if not data_field in self.__data_dict[category]:
            self.__data_dict[category][data_field] = []

        self.__data_dict[category][data_field].append(data)

    def get_categories(self) -> KeysView[str]:
        return self.__data_dict.keys()

    def get_data_fields(self, category: str) -> KeysView[str]:
        return self.__data_dict[category].keys()

    def get_data_series(self, category: str, data_field: str) -> List[float]:
        if category in self.__data_dict and data_field in self.__data_dict[category]:
            return self.__data_dict[category][data_field]
        else:
            return []

    def collect_data(self):
        for category in self.data_structure.keys():
            for data_field in self.data_structure[category].keys():
                if self.data_structure[category][data_field]:
                    self.add_data(category, data_field, self._data(category, data_field))

    @abstractmethod
    def _data(self, category: str, data_field: str) -> float:
        pass

    def clear(self):
        self.__data_dict.clear()