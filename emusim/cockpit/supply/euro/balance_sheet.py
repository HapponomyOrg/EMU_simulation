from copy import deepcopy
from typing import List, Dict, Tuple, Set

BALANCE = 0
DELTA = 1

class BalanceSheet():
    """Balance sheet"""

    __assets: Dict[str, float] = {}
    __liabilities: Dict[str, float] = {}

    def clear(self):
        self.assets.clear()
        self.liabilities.clear()

    def book_asset(self, asset_name: str, amount: float):
        if asset_name in self.__assets:
            self.__assets[asset_name] += amount
        else:
            self.__assets[asset_name] = amount

    def book_liability(self, liability_name: str, amount: float):
        if liability_name in self.__liabilities:
            self.__liabilities[liability_name] += amount
        else:
            self.__liabilities[liability_name] = amount

    def validate(self) -> bool:
        total_assets = 0.0
        total_liabilities = 0.0

        for value in self.assets.values():
            total_assets += value

        for value in self.liabilities.values():
            total_liabilities += value

        return total_assets - total_liabilities == 0

    @property
    def assets(self) -> Dict[str, float]:
        return self.__assets

    @property
    def liabilities(self) -> Dict[str, float]:
        return self.__liabilities

    def asset(self, name: str) -> float:
        return self.assets[name]

    def liability(self, name: str) -> float:
        return self.liabilities[name]


class BalanceSheetTimeline():
    """Balance sheet with history"""

    __current_balance: BalanceSheet = BalanceSheet()
    __history: List[Tuple[BalanceSheet, BalanceSheet]] = []

    def clear(self):
        self.__current_balance.clear()
        self.history.clear()

    def book_asset(self, name: str, amount: float):
        self.__current_balance.book_asset(name, amount)

    def book_liability(self, name: str, amount: float):
        self.__current_balance.book_liability(name, amount)

    def validate(self) -> bool:
        return self.__current_balance.validate()

    def save_state(self) -> bool:
        if self.validate():
            balance_delta: BalanceSheet = BalanceSheet()
            asset_names: Set = set(self.assets.keys())
            liability_names: Set = set(self.liabilities.keys())

            if self.history: # not empty
                previous_balance: BalanceSheet = self.history[-1][BALANCE]

                previous_assets: Dict = previous_balance.assets
                asset_names.update(previous_assets.keys()) # collect all names

                for name in asset_names:
                    if name in previous_assets:
                        balance_delta.book_asset(name, self.assets[name] - previous_assets[name])
                    else:
                        balance_delta.book_asset(name, self.assets[name])

                previous_liabilities: Dict = previous_balance.liabilities
                liability_names.update(previous_liabilities.keys()) # collect all names

                for name in liability_names:
                    if name in previous_liabilities:
                        balance_delta.book_liability(name, self.liabilities[name] - previous_liabilities[name])
                    else:
                        balance_delta.book_liability(name, self.liabilities[name])

            self.history.append((deepcopy(self.__current_balance), balance_delta))

            return True
        else:
            return False

    @property
    def history(self) -> List[Tuple[BalanceSheet, BalanceSheet]]:
        return self.__history

    @property
    def assets(self) -> Dict[str, float]:
        return self.__current_balance.assets

    @property
    def liabilities(self) -> Dict[str, float]:
        return self.__current_balance.liabilities

    def asset(self, name: str) -> float:
        return self.__current_balance.asset(name)

    def liability(self, name: str) -> float:
        return self.__current_balance.liability(name)