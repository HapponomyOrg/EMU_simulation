from __future__ import annotations

from typing import List, Dict, Set, Optional


class BalanceSheet():
    """Balance sheet"""

    def __init__(self, balance_sheet: Optional[BalanceSheet] = None):
        self.__assets: Dict[str, float] = {}
        self.__liabilities: Dict[str, float] = {}

        if balance_sheet is not None:
            for name in balance_sheet.assets.keys():
                self.book_asset(name, balance_sheet.asset(name))

            for name in balance_sheet.liabilities.keys():
                self.book_liability(name, balance_sheet.liability(name))

    @property
    def assets(self) -> Dict[str, float]:
        return self.__assets

    @property
    def liabilities(self) -> Dict[str, float]:
        return self.__liabilities

    @property
    def assets_value(self) -> float:
        return self.__value(self.assets)

    @property
    def liabilities_value(self) -> float:
        return self.__value(self.liabilities)

    @property
    def total_balance(self) -> float:
        """:return The total balance if the balance sheet validates (assets == liabilities). -1.0 otherwise."""
        if self.validate():
            return self.__value(self.assets)
        else:
            return -1.0

    def clear(self):
        self.assets.clear()
        self.liabilities.clear()

    def book_asset(self, asset_name: str, amount: float):
        if asset_name in self.assets:
            self.__assets[asset_name] += amount
        else:
            self.__assets[asset_name] = amount

    def book_liability(self, liability_name: str, amount: float):
        if liability_name in self.__liabilities:
            self.__liabilities[liability_name] += amount
        else:
            self.__liabilities[liability_name] = amount

    def validate(self) -> bool:
        return self.__value(self.assets) - self.__value(self.liabilities) == 0

    def asset(self, name: str) -> float:
        if name in self.assets:
            return self.assets[name]
        else:
            return 0.0

    def liability(self, name: str) -> float:
        if name in self.liabilities:
            return self.liabilities[name]
        else:
            return 0.0

    def __value(self, entries: Dict[str, float]) -> float:
        total_value = 0.0

        for value in entries.values():
            total_value += value

        return total_value

    def __str__(self):
        string: str = "== Assets ==\n"

        for name in self.assets.keys():
            string += name + ": " + str(self.asset(name)) + "\n"

        string += "== Liabilities ==\n"

        for name in self.liabilities.keys():
            string += name + ": " + str(self.liability(name)) + "\n"

        return string + "\n"


class BalanceSheetTimeline(BalanceSheet):
    """Balance sheet with history"""

    def __init__(self):
        super().__init__()
        self.__history: List[BalanceSheet] = []

    def clear(self):
        super().clear()
        self.__history.clear()

    def save_state(self) -> bool:
        if self.validate():
            self.__history.append(BalanceSheet(self))

            return True
        else:
            return False
    
    def balance_history(self, time_delta: int) -> BalanceSheet:
        """Get a balance sheet from the history.
        
        :param time_delta: int how far back in history"""

        if time_delta == 0:
            return BalanceSheet(self)
        else:
            return self.__history[len(self.__history) - abs(time_delta)]
    
    def asset_history(self, name: str, time_delta: int) -> float:
        return self.balance_history(time_delta).asset(name)
    
    def liability_history(self, name: str, time_delta: int) -> float:
        return self.balance_history(time_delta).liability(name)
    
    def delta_history(self, time_delta: int = 0) -> BalanceSheet:
        if time_delta == 0:
            return self.__calculate_delta(self, self)
        else:
            return self.__calculate_delta(self, self.__history[len(self.__history) - abs(time_delta)])
    
    def __calculate_delta(self, current: BalanceSheet, previous: BalanceSheet) -> BalanceSheet:
            delta: BalanceSheet = BalanceSheet()
            asset_names: Set = set(current.assets.keys())
            liability_names: Set = set(current.liabilities.keys())

            previous_assets: Dict[str, float] = previous.assets
            asset_names.update(previous_assets.keys()) # collect all names

            for name in asset_names:
                if name in previous_assets:
                    delta.book_asset(name, current.assets[name] - previous_assets[name])
                else:
                    delta.book_asset(name, current.assets[name])

            previous_liabilities: Dict[str, float] = previous.liabilities
            liability_names.update(previous_liabilities.keys()) # collect all names

            for name in liability_names:
                if name in previous_liabilities:
                    delta.book_liability(name, current.liabilities[name] - previous_liabilities[name])
                else:
                    delta.book_liability(name, current.liabilities[name])

            return delta

    def __str__(self):
        string: str = super().__str__() + "History\n"

        for balance in self.__history:
            string += balance.__str__()

        return string