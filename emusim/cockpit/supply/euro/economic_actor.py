from typing import Set

from emusim.cockpit.supply.euro.balance_sheet import BalanceSheetTimeline


class EconomicActor:
    __balance: BalanceSheetTimeline = BalanceSheetTimeline()

    @property
    def balance(self):
        return self.__balance

    @property
    def assets(self) -> Set:
        """Returns the possible assets for this entity. Needs to be overridden by subclasses."""
        return set()

    @property
    def liabilities(self) -> Set:
        """Returns the possible liabilities for this entity. Needs to be overridden by subclasses."""
        return set()

    def book_asset(self, name: str, amount: float) -> bool:
        if name in self.assets:
            self.balance.book_asset(name, amount)
            return True
        else:
            return False

    def book_liabilaty(self, name: str, amount: float) -> bool:
        if name in self.liabilities:
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

    def inflate_parameters(self, inflation: float):
        pass

    def save_state(self):
        self.balance.save_state()

    