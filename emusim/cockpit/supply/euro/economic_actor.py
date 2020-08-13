from abc import ABC, abstractmethod
from typing import List

from ordered_set import OrderedSet

from emusim.cockpit.supply.euro.balance_sheet import BalanceSheetTimeline


class EconomicActor(ABC):
    __asset_names: OrderedSet[str]
    __liability_names: OrderedSet[str]
    __balance: BalanceSheetTimeline = BalanceSheetTimeline()

    @property
    def balance(self):
        return self.__balance

    def _init_asset_names(self, asset_names: List[str]):
        self.__asset_names = OrderedSet(asset_names)

    def _init_liability_names(self, liability_names: List[str]):
        self.__liability_names = OrderedSet(liability_names)

    @property
    def asset_names(self) -> OrderedSet[str]:
        """Returns the possible asset_names for this entity. Needs to be overridden by subclasses."""
        return self.__asset_names

    @property
    def liability_names(self) -> OrderedSet:
        """Returns the possible liability_names for this entity. Needs to be overridden by subclasses."""
        return self.__liability_names

    def book_asset(self, name: str, amount: float) -> bool:
        if name in self.asset_names:
            self.balance.book_asset(name, amount)
            return True
        else:
            return False

    def book_liability(self, name: str, amount: float) -> bool:
        if name in self.liability_names:
            self.balance.book_liability(name, amount)
            return True
        else:
            return False

    def asset(self, name: str) -> float:
        return self.balance.asset(name)

    def liability(self, name: str) -> float:
        return self.balance.liability(name)

    def validate_balance(self) -> bool:
        return self.balance.validate()

    @abstractmethod
    def inflate_parameters(self, inflation: float):
        pass

    def start_cycle(self):
        """Call before performing any action on the economic actor."""
        pass

    def end_cycle(self) -> bool:
        """Call after all actions for a cycle have been concluded.
        Returns whether the cycle was successful."""
        return self.balance.save_state()

    