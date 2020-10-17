from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Tuple

from decimal import *
from ordered_set import OrderedSet

from emusim.cockpit.utilities.cycles import Interval, Period
from . import BalanceEntries, EconomicActor

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
        self.qe_interval: Period = Period(1, Interval.MONTH)

        self.helicopter_mode: HelicopterMode = HelicopterMode.NONE
        self.__helicopter_fixed: Decimal = Decimal(0.0)
        self.__helicopter_debt_related: Decimal = Decimal(0.0)
        self.helicopter_interval: Period = Period(1, Interval.MONTH)

        # Cycle parameters
        self.__inflation_processed: bool = False
        self.__mbs_growth_processed: bool = False
        self.__security_growth_processed: bool = False
        self.__reserves_processed: bool = False
        self.__loans_processed: bool = False
        self.__qe_processed: bool = False
        self.__helicopter_money_processed: bool = False

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
    def bank(self) -> Bank:
        return self.__bank

    @bank.setter
    def bank(self, bank: Bank):
        self.__bank: Bank = bank

    @property
    def loan_installments(self) -> int:
        return int(self.loan_duration.days / self.loan_interval.days)

    def start_transactions(self):
        super().start_transactions()

        self.__inflation_processed: bool = False
        self.__mbs_growth_processed: bool = False
        self.__security_growth_processed: bool = False
        self.__reserves_processed: bool = False
        self.__loans_processed: bool = False
        self.__qe_processed: bool = False
        self.__helicopter_money_processed: bool = False

        self.bank.start_transactions()

    def end_transactions(self) -> bool:
        # if there are interest assets on the books, spend them to the economy
        return super().end_transactions() and self.bank.end_transactions()

    def inflate(self, inflation: Decimal):
        if not self.__inflation_processed:
            inflation = Decimal(inflation)
            self.qe_fixed += self.qe_fixed * inflation
            self.helicopter_fixed += self.helicopter_fixed * inflation

            self.bank.inflate(inflation)

            self.__inflation_processed = True

    def grow_mbs(self, growth: Decimal):
        if not self.__mbs_growth_processed:
            super().grow_mbs(growth)

            self.bank.grow_mbs(growth)

            self.__mbs_growth_processed = True

    def grow_securities(self, growth: Decimal):
        if not self.__security_growth_processed:
            super().grow_securities(growth)

            self.bank.grow_securities(growth)

            self.__security_growth_processed = True

    def process_reserve_interests(self):
        """Give/collect interest according to a bank's reserve accounts."""
        if not self.__reserves_processed and self.reserve_interest_interval.period_complete(self.cycle):
            # Banks may hold part of their reserves in another form than the balance of their reserve accounts.
            # Those reserves will always meet the minimum reserves due to the implementation of the Bank class.
            reserve_interest_rate = self.reserve_ir * self.reserve_interest_interval.days / Period.YEAR_DAYS
            surplus_interest_rate = self.surplus_reserve_ir * self.reserve_interest_interval.days / Period.YEAR_DAYS
            reserves: Decimal = self.bank.asset(BalanceEntries.RESERVES)
            reserve_limit: Decimal = self.bank.client_liabilities * self.min_reserve
            surplus_reserve: Decimal = max(Decimal(0.0), reserves - reserve_limit)
            interest: Decimal = reserve_limit * reserve_interest_rate + surplus_reserve * surplus_interest_rate
            self.bank.process_interest(interest)

            if interest < 0.0:
                # interest earned from banks is redistributed to the private sector
                self.bank.distribute_interest(-interest)
            else:
                self.book_asset(BalanceEntries.INTEREST, -interest)
                self.book_liability(BalanceEntries.EQUITY, -interest)

            self.__reserves_processed = True

    def book_loan(self, amount: Decimal):
        self.book_asset(BalanceEntries.LOANS, amount)
        self.book_liability(BalanceEntries.RESERVES, amount)

    def process_bank_loans(self):
        installment: Decimal = Decimal(0.0)

        if not self.__loans_processed and self.loan_interval.period_complete(self.cycle):
            payment: Tuple[Decimal, Decimal] = self.bank.pay_debt(self.loan_ir * self.loan_interval.days / Period.YEAR_DAYS)
            installment += payment[0]
            interest: Decimal = payment[1]
            self.bank.distribute_interest(interest)

            self.book_asset(BalanceEntries.LOANS, -installment)
            self.book_liability(BalanceEntries.RESERVES, -installment)

            self.__loans_processed = True

    def process_qe(self): # TODO: work with qe per year for fixed
        if not self.__qe_processed and self.qe_interval.period_complete(self.cycle):
            qe_amount: Decimal = Decimal(0.0)

            if self.qe_mode == QEMode.FIXED:
                qe_amount = self.qe_fixed
            elif self.qe_mode == QEMode.DEBT_RELATED:
                qe_amount = self.__calculate_private_debt() * self.qe_debt_related

            self.book_asset(BalanceEntries.SECURITIES, qe_amount)
            self.book_liability(BalanceEntries.RESERVES, qe_amount)

            # first buy securities from bank
            qe_amount -= self.bank.trade_central_bank_securities(qe_amount)

            # get remainder from private sector
            self.bank.client.trade_securities_with_bank(qe_amount)
            self.bank.trade_central_bank_securities(qe_amount)

            self.__qe_processed = True

    def process_helicopter_money(self):# TODO: work with helicopter per year for fixed
        if not self.__helicopter_money_processed and self.helicopter_interval.period_complete(self.cycle):
            helicopter_money: Decimal = Decimal(0.0)

            if self.helicopter_mode == HelicopterMode.FIXED:
                helicopter_money = self.helicopter_fixed
            elif self.helicopter_mode == HelicopterMode.DEBT_RELATED:
                helicopter_money = self.__calculate_private_debt() * self.helicopter_debt_related

            self.book_asset(BalanceEntries.HELICOPTER_MONEY, helicopter_money)
            self.book_liability(BalanceEntries.RESERVES, helicopter_money)

            self.bank.client.book_asset(BalanceEntries.DEPOSITS, helicopter_money)
            self.bank.client.book_liability(BalanceEntries.EQUITY, helicopter_money)
            self.bank.book_asset(BalanceEntries.RESERVES, helicopter_money)
            self.bank.book_liability(BalanceEntries.DEPOSITS, helicopter_money)

            self.__helicopter_money_processed = True

    def __calculate_private_debt(self) -> Decimal:
        return self.bank.asset(BalanceEntries.LOANS) + self.bank.asset(BalanceEntries.MBS)

    def clear(self):
        super().clear()

        self.bank.clear()