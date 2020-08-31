from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Set

from ordered_set import OrderedSet

from . import EconomicActor
from .balance_entries import *

if TYPE_CHECKING:
    from . import Bank


class QEMode(Enum):
    NONE = 0
    FIXED = 1
    DEBT_RELATED = 2


class HelicopterMode(Enum):
    NONE = 0
    FIXED = 1
    DEBT_RELATED = 2


class CentralBank(EconomicActor):

    def __init__(self, min_reserve: float = 0.04):
        super().__init__(OrderedSet([LOANS, SECURITIES, HELICOPTER_MONEY, INTEREST]),
                         OrderedSet([RESERVES, EQUITY, SEC_EQUITY]))
        self.__registered_banks: Set[Bank] = set()

        self.__min_reserve = min_reserve
        self.__mbs_reserve: float = 0.0                # max % of 'reserve' in the form of MBS
        self.__securities_reserve: float = 0.0         # max % of 'reserve' in the form of securities

        self.reserve_ir: float = 0.0
        self.surplus_reserve_ir: float = -0.005

        self.loan_ir: float = 0.01
        self.loan_duration: int = 1

        self.qe_mode: QEMode = QEMode.NONE
        self.qe_fixed: float = 0.0
        self.qe_debt_related = 0.0

        self.helicopter_mode: HelicopterMode = HelicopterMode.NONE
        self.helicopter_fixed: float = 0.0
        self.helicopter_debt_related: float = 0.0

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

    def start_transactions(self):
        for bank in self.registered_banks:
            bank.start_transactions()

    def end_transactions(self) -> bool:
        # if there are interest assets on the books, spend them to the economy
        success: bool = True

        for bank in self.registered_banks:
            success = success and bank.end_transactions()

        return success

    def inflate(self, inflation: float):
        self.qe_fixed += self.qe_fixed * inflation
        self.helicopter_fixed += self.helicopter_fixed * inflation

        for bank in self.registered_banks:
            bank.inflate(inflation)

    def process_reserve_interests(self):
        """Give/collect interest according to a bank's reserve accounts."""
        for bank in self.registered_banks:
            # Banks may hold part of their reserves in another form than the balance of their reserve accounts.
            # Those reserves will always meet the minimum reserves due to the implementation of the Bank class.
            reserves: float = bank.asset(RESERVES)
            deposits: float = bank.liability(DEPOSITS) + bank.liability(SAVINGS)
            required_reserve: float = min(reserves, deposits * self.min_reserve)
            surplus_reserve: float = max (0.0, reserves - required_reserve)
            interest: float = required_reserve * self.reserve_ir + surplus_reserve * self.surplus_reserve_ir
            self.book_asset(INTEREST, interest)
            self.book_liability(EQUITY, interest)
            bank.process_interest(interest)

    def book_loan(self, amount: float):
        self.book_asset(LOANS, amount)
        self.book_liability(RESERVES, amount)

    def process_bank_loans(self):
        for bank in self.registered_banks:
            bank.pay_debt(self.loan_ir)

    def process_qe(self):
        qe_amount: float = 0.0

        if self.qe_mode == QEMode.FIXED:
            qe_amount = self.qe_fixed
        elif self.qe_mode == QEMode.DEBT_RELATED:
            qe_amount = self.__calculate_private_debt() * self.qe_debt_related

        self.book_asset(SECURITIES, qe_amount)
        self.book_liability(RESERVES, qe_amount)

        client_count: int = 0

        # first buy securities from banks on a first come, first serve basis
        for bank in self.registered_banks:
            client_count += len(bank.clients)
            qe_amount -= bank.trade_central_bank_securities(qe_amount)

        # get remainder from private sector, distributed among all
        client_qe: float = qe_amount / client_count

        for bank in self.registered_banks:
            for client in bank.clients:
                bank.book_asset(RESERVES, client_qe)
                bank.book_liability(DEPOSITS, client_qe)
                client.trade_securities(client_qe)

    def process_helicopter_money(self):
        helicopter_money: float = 0.0

        if self.helicopter_mode == HelicopterMode.FIXED:
            helicopter_money = self.helicopter_fixed
        elif self.helicopter_mode == HelicopterMode.DEBT_RELATED:
            helicopter_money = self.__calculate_private_debt() * self.helicopter_debt_related

        self.book_asset(HELICOPTER_MONEY, helicopter_money)
        self.book_liability(RESERVES, helicopter_money)

        client_count: int = 0

        for bank in self.registered_banks:
            client_count += len(bank.clients)

        helicopter_fraction: float = helicopter_money / client_count

        for bank in self.registered_banks:
            for client in bank.clients:
                client.book_asset(DEPOSITS, helicopter_fraction)
                client.book_liability(EQUITY, helicopter_fraction)
                bank.book_asset(RESERVES, helicopter_fraction)
                bank.book_liability(DEPOSITS, helicopter_fraction)

    def __calculate_private_debt(self) -> float:
        debt: float = 0.0

        for bank in self.registered_banks:
            debt += bank.asset(LOANS)
            debt += bank.asset(MBS)

        return debt

    def clear(self):
        super().clear()

        for bank in self.registered_banks:
            bank.clear()