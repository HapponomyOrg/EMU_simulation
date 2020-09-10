from __future__ import annotations

from abc import ABC, abstractmethod

from ordered_set import OrderedSet

from . import BalanceSheetTimeline, BalanceEntries


class EconomicActor(ABC):

    def __init__(self, asset_names: OrderedSet[str], liability_names: OrderedSet[str]):
        self.__asset_names: OrderedSet[str] = asset_names
        self.__liability_names: OrderedSet[str] = liability_names
        self.__balance: BalanceSheetTimeline = BalanceSheetTimeline()

        # Cycle flags. Operations can not be executed before transactiosn have started. Some operations can only be
        # executed once per cycle.
        self.__transactions_started: bool = False
        self.__security_growth_processed = False
        self.__mbs_growth_processed = False

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

    @property
    def _transactions_started(self) -> bool:
        return self.__transactions_started

    def grow_securities(self, growth: float):
        if self._transactions_started and not self.__security_growth_processed:
            security_growth = self.asset(BalanceEntries.SECURITIES) * growth
            self.book_asset(BalanceEntries.SECURITIES, security_growth)
            self.book_liability(BalanceEntries.SEC_EQUITY, security_growth)
            self.__security_growth_processed = True

    def grow_mbs(self, growth: float):
        if self._transactions_started and not self.__mbs_growth_processed:
            mbs_growth = self.asset(BalanceEntries.MBS) * growth
            self.book_asset(BalanceEntries.MBS, mbs_growth)
            self.book_liability(BalanceEntries.MBS_EQUITY, mbs_growth)
            self.__mbs_growth_processed = True

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

        self.__transactions_started = True
        self.__security_growth_processed = False
        self.__mbs_growth_processed = False

    def end_transactions(self) -> bool:
        """Call after all transactions have been concluded.
        :return True if the state of the economic actor is validated."""

        self.__transactions_started = False
        return self.balance.save_state()

    def clear(self):
        self.balance.clear()