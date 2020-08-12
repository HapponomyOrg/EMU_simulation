from typing import Set

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.bank import Bank
from emusim.cockpit.supply.euro.economic_actor import EconomicActor


class CentralBank(EconomicActor):
    reserve_ir: float = 0.0
    surplus_reserve_ir: float = -0.005

    loan_ir: float = 0.01
    loan_duration: int = 1

    __min_reserve: float = 4.0
    __mbs_reserve: float = 0.0                # max % of 'reserve' in the form of MBS
    __securities_reserve: float = 0.0         # max % of 'reserve' in the form of securities

    __registered_banks: Set[Bank] = set()

    def __init__(self, min_reserves: float = 4.0):
        self.__min_reserve = min_reserves

    def register(self, bank: Bank):
        self.registered_banks.add(bank)

    @property
    def min_reserve(self) -> float:
        return self.__min_reserve

    @min_reserve.setter
    def min_reserve(self, percentage: float):
        self.__min_reserve = percentage

    @property
    def real_min_reserve(self) -> float:
        return self.min_reserve - self.__mbs_reserve - self.__securities_reserve

    @property
    def mbs_relative_reserve(self) -> float:
        return self.__mbs_reserve / self.min_reserve

    @mbs_relative_reserve.setter
    def mbs_relative_reserve(self, percentage: float):
        self.__mbs_reserve = percentage * self.min_reserve

    @property
    def mbs_real_reserve(self) -> float:
        return self.__mbs_reserve

    @property
    def securities_relative_reserve(self) -> float:
        return self.__securities_reserve / self.min_reserve

    @securities_relative_reserve.setter
    def securities_relative_reserve(self, percentage: float):
        self.__securities_reserve = percentage * self.min_reserve

    @property
    def securities_real_reserve(self) -> float:
        return self.__securities_reserve

    @property
    def registered_banks(self) -> Set[Bank]:
        return self.__registered_banks

    @property
    def assets(self) -> Set:
        return {LOANS, SECURITIES, HELICOPTER_MONEY, FUNDING}

    @property
    def liabilities(self) -> Set:
        return {RESERVES, EQUITY}

    def book_loan(self, amount: float):
        self.book_asset(LOANS, amount)
        self.book_liability(RESERVES, amount)

    def process_bank_loans(self):
        for bank in self.registered_banks:
            bank.pay_debt(self.loan_ir)
