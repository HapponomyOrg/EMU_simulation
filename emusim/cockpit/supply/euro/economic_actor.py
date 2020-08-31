from __future__ import annotations

from abc import ABC, abstractmethod

from ordered_set import OrderedSet

from . import BalanceSheetTimeline
from .balance_entries import *


class EconomicActor(ABC):

    def __init__(self, asset_names: OrderedSet[str], liability_names: OrderedSet[str]):
        self.__asset_names: OrderedSet[str] = asset_names
        self.__liability_names: OrderedSet[str] = liability_names
        self.__balance: BalanceSheetTimeline = BalanceSheetTimeline()

    @property
    def balance(self):
        return self.__balance

    @property
    def asset_names(self) -> OrderedSet[str]:
        """Returns the possible asset_names for this entity. Needs to be overridden by subclasses."""
        return self.__asset_names

    @property
    def liability_names(self) -> OrderedSet:
        """Returns the possible liability_names for this entity. Needs to be overridden by subclasses."""
        return self.__liability_names

    def grow_securities(self, growth: float):
        security_growth = self.asset(SECURITIES) * growth
        self.book_asset(SECURITIES, security_growth)
        self.book_liability(SEC_EQUITY, security_growth)

    def grow_mbs(self, growth: float):
        mbs_growth = self.asset(MBS) * growth
        self.book_asset(MBS, mbs_growth)
        self.book_liability(MBS_EQUITY, mbs_growth)

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
    def inflate(self, inflation: float):
        pass

    def start_transactions(self):
        """Call before performing any transactions on the economic actor."""
        pass

    def end_transactions(self) -> bool:
        """Call after all transactions have been concluded.
        :return True if the state of the economic actor is validated."""
        return self.balance.save_state()

    def clear(self):
        self.balance.clear()