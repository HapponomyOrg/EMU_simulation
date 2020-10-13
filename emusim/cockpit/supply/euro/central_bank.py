from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Set

from decimal import *
from ordered_set import OrderedSet

from emusim.cockpit.utilities.cycles import Interval, Period
from . import EconomicActor, BalanceEntries

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

    def __init__(self, min_reserve: Decimal = 0.04):
        super().__init__(OrderedSet([BalanceEntries.LOANS, BalanceEntries.SECURITIES, BalanceEntries.HELICOPTER_MONEY,
                                     BalanceEntries.INTEREST]),
                         OrderedSet([BalanceEntries.RESERVES, BalanceEntries.EQUITY]))
        self.__registered_banks: Set[Bank] = set()

        self.__min_reserve = Decimal(min_reserve)
        self.__mbs_reserve: Decimal = Decimal(0.0)                # max % of 'reserve' in the form of MBS
        self.__securities_reserve: Decimal = Decimal(0.0)         # max % of 'reserve' in the form of securities

        self.__reserve_ir: Decimal = Decimal(0.0)
        self.__surplus_reserve_ir: Decimal = Decimal(-0.005)
        self.reserve_interest_interval: Period = Period(1, Interval.DAY)

        self.__loan_ir: Decimal = Decimal(0.01)
        self.loan_duration: Period = Period(3, Interval.DAY)
        self.loan_interval: Period = Period(3, Interval.DAY)

        self.qe_mode: QEMode = QEMode.NONE
        self.__qe_fixed: Decimal = Decimal(0.0)
        self.__qe_debt_related = Decimal(0.0)

        self.helicopter_mode: HelicopterMode = HelicopterMode.NONE
        self.__helicopter_fixed: Decimal = Decimal(0.0)
        self.__helicopter_debt_related: Decimal = Decimal(0.0)

    def register(self, bank: Bank):
        self.registered_banks.add(bank)

    @property
    def min_reserve(self) -> Decimal:
        return self.__min_reserve

    @min_reserve.setter
    def min_reserve(self, percentage: Decimal):
        self.__min_reserve = Decimal(percentage)

    @property
    def real_min_reserve(self) -> Decimal:
        return self.min_reserve - self.__mbs_reserve - self.__securities_reserve

    @property
    def mbs_relative_reserve(self) -> Decimal:
        return self.__mbs_reserve / self.min_reserve

    @mbs_relative_reserve.setter
    def mbs_relative_reserve(self, percentage: Decimal):
        self.__mbs_reserve = Decimal(percentage) * self.min_reserve

    @property
    def mbs_real_reserve(self) -> Decimal:
        return self.__mbs_reserve

    @property
    def securities_relative_reserve(self) -> Decimal:
        return self.__securities_reserve / self.min_reserve

    @securities_relative_reserve.setter
    def securities_relative_reserve(self, percentage: Decimal):
        self.__securities_reserve = Decimal(percentage) * self.min_reserve

    @property
    def securities_real_reserve(self) -> Decimal:
        return self.__securities_reserve

    @property
    def reserve_ir(self) -> Decimal:
        return self.__reserve_ir

    @reserve_ir.setter
    def reserve_ir(self, ir: Decimal):
        self.__reserve_ir = Decimal(ir)

    @property
    def surplus_reserve_ir(self) -> Decimal:
        return self.__surplus_reserve_ir

    @surplus_reserve_ir.setter
    def surplus_reserve_ir(self, ir: Decimal):
        self.__surplus_reserve_ir = Decimal(ir)

    @property
    def loan_ir(self) -> Decimal:
        return self.__loan_ir

    @loan_ir.setter
    def loan_ir(self, ir: Decimal):
        self.__loan_ir = Decimal(ir)

    @property
    def qe_fixed(self) -> Decimal:
        return self.__qe_fixed

    @qe_fixed.setter
    def qe_fixed(self, qe: Decimal):
        self.__qe_fixed = Decimal(qe)

    @property
    def qe_debt_related(self) -> Decimal:
        return self.__qe_debt_related

    @qe_debt_related.setter
    def qe_debt_related(self, relative_qe: Decimal):
        self.__qe_debt_related = Decimal(relative_qe)

    @property
    def helicopter_fixed(self) -> Decimal:
        return self.__helicopter_fixed

    @helicopter_fixed.setter
    def helicopter_fixed(self, qe: Decimal):
        self.__helicopter_fixed = Decimal(qe)

    @property
    def helicopter_debt_related(self) -> Decimal:
        return self.__helicopter_debt_related

    @helicopter_debt_related.setter
    def helicopter_debt_related(self, relative_helicopter: Decimal):
        self.__helicopter_debt_related = Decimal(relative_helicopter)

    @property
    def registered_banks(self) -> Set[Bank]:
        return self.__registered_banks

    @property
    def loan_installments(self) -> int:
        return int(self.loan_duration.days / self.loan_interval.days)

    def start_transactions(self):
        super().start_transactions()

        for bank in self.registered_banks:
            bank.start_transactions()

    def end_transactions(self) -> bool:
        # if there are interest assets on the books, spend them to the economy
        success: bool = super().end_transactions()

        for bank in self.registered_banks:
            success = success and bank.end_transactions()

        return success

    def inflate(self, inflation: Decimal):
        inflation = Decimal(inflation)
        self.qe_fixed += Decimal(round(self.qe_fixed * inflation, 8))
        self.helicopter_fixed += Decimal(round(self.helicopter_fixed * inflation, 8))

        for bank in self.registered_banks:
            bank.inflate(inflation)

    def grow_mbs(self, growth: Decimal):
        super().grow_mbs(growth)

        for bank in self.registered_banks:
            bank.grow_mbs(growth)

    def grow_securities(self, growth: Decimal):
        super().grow_securities(growth)

        for bank in self.registered_banks:
            bank.grow_securities(growth)

    def process_reserve_interests(self):
        """Give/collect interest according to a bank's reserve accounts."""
        for bank in self.registered_banks:
            # Banks may hold part of their reserves in another form than the balance of their reserve accounts.
            # Those reserves will always meet the minimum reserves due to the implementation of the Bank class.
            reserve_interest_rate = self.reserve_ir * self.reserve_interest_interval.days / Period.YEAR_DAYS
            surplus_interest_rate = self.surplus_reserve_ir * self.reserve_interest_interval.days / Period.YEAR_DAYS
            reserves: Decimal = bank.asset(BalanceEntries.RESERVES)
            reserve_limit: Decimal = Decimal(round(bank.client_liabilities * self.min_reserve, 8))
            surplus_reserve: Decimal = max(Decimal(0.0), reserves - reserve_limit)
            interest: Decimal = Decimal(round(reserve_limit * reserve_interest_rate
                                              + surplus_reserve * surplus_interest_rate, 8))
            bank.process_interest(interest)

            if interest < 0.0:
                # interest earned from banks is redistributed to the private sector
                bank.distribute_interest(-interest)
            else:
                self.book_asset(BalanceEntries.INTEREST, -interest)
                self.book_liability(BalanceEntries.EQUITY, -interest)

    def book_loan(self, amount: Decimal):
        self.book_asset(BalanceEntries.LOANS, amount)
        self.book_liability(BalanceEntries.RESERVES, amount)

    def process_bank_loans(self):
        for bank in self.registered_banks:
            bank.pay_debt(self.loan_ir * self.loan_interval.days / Period.YEAR_DAYS)

    def process_qe(self):
        qe_amount: Decimal = Decimal(0.0)

        if self.qe_mode == QEMode.FIXED:
            qe_amount = self.qe_fixed
        elif self.qe_mode == QEMode.DEBT_RELATED:
            qe_amount = self.__calculate_private_debt() * self.qe_debt_related

        self.book_asset(BalanceEntries.SECURITIES, qe_amount)
        self.book_liability(BalanceEntries.RESERVES, qe_amount)

        client_count: int = 0

        # first buy securities from banks on a first come, first serve basis
        for bank in self.registered_banks:
            client_count += len(bank.clients)
            qe_amount -= bank.trade_central_bank_securities(qe_amount)

        # get remainder from private sector, distributed among all
        client_qe: Decimal = qe_amount / client_count

        for bank in self.registered_banks:
            for client in bank.clients:
                client.trade_securities_with_bank(client_qe)
                bank.trade_central_bank_securities(client_qe)

    def process_helicopter_money(self):
        helicopter_money: Decimal = Decimal(0.0)

        if self.helicopter_mode == HelicopterMode.FIXED:
            helicopter_money = self.helicopter_fixed
        elif self.helicopter_mode == HelicopterMode.DEBT_RELATED:
            helicopter_money = self.__calculate_private_debt() * self.helicopter_debt_related

        self.book_asset(BalanceEntries.HELICOPTER_MONEY, helicopter_money)
        self.book_liability(BalanceEntries.RESERVES, helicopter_money)

        client_count: int = 0

        for bank in self.registered_banks:
            client_count += len(bank.clients)

        helicopter_fraction: Decimal = helicopter_money / client_count

        for bank in self.registered_banks:
            for client in bank.clients:
                client.book_asset(BalanceEntries.DEPOSITS, helicopter_fraction)
                client.book_liability(BalanceEntries.EQUITY, helicopter_fraction)
                bank.book_asset(BalanceEntries.RESERVES, helicopter_fraction)
                bank.book_liability(BalanceEntries.DEPOSITS, helicopter_fraction)

    def __calculate_private_debt(self) -> Decimal:
        debt: Decimal = Decimal(0.0)

        for bank in self.registered_banks:
            debt += bank.asset(BalanceEntries.LOANS)
            debt += bank.asset(BalanceEntries.MBS)

        return debt

    def clear(self):
        super().clear()

        for bank in self.registered_banks:
            bank.clear()