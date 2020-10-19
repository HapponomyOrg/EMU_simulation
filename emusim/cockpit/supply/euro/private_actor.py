from __future__ import annotations

from typing import TYPE_CHECKING, List
from enum import Enum

from decimal import *
from ordered_set import OrderedSet
from random import random, uniform

from . import EconomicActor, DebtPayment, BalanceEntries

if TYPE_CHECKING:
    from . import Bank


class DefaultingMode(Enum):
    NONE = 0
    FIXED = 1
    PROBABILISTIC = 2


class PrivateActor(EconomicActor):

    def __init__(self, bank: Bank):
        super().__init__(
            OrderedSet([BalanceEntries.DEPOSITS, BalanceEntries.UNRESOLVED_DEBT, BalanceEntries.SECURITIES,
                        BalanceEntries.SAVINGS, BalanceEntries.MBS]),
            OrderedSet([BalanceEntries.DEBT, BalanceEntries.UNRESOLVED_DEBT, BalanceEntries.EQUITY,
                        BalanceEntries.MBS_EQUITY]))
        self.__bank: Bank = bank
        self.__bank.client = self

        self.__savings_rate: Decimal = Decimal(0.02)

        self.__borrow_for_securities: Decimal = Decimal(0.0)

        self.defaulting_mode: DefaultingMode = DefaultingMode.FIXED
        self.__fixed_defaulting_rate: Decimal = Decimal(0.0)
        self.__defaulting_probability: Decimal = Decimal(0.0)
        self.__defaulting_min: Decimal = Decimal(0.0) # minimum defaulting percentage for probabilistic mode
        self.__defaulting_max: Decimal = Decimal(0.0) # maximum defaulting percentage for probabilistic mode

        self.__defaults_bought_by_debt_collectors: Decimal = Decimal(0.0) # In %
        self.__unresolved_debt_growth: Decimal = Decimal(0.0) # Net growth of unresolved debt. Can be negative.

        self.__installments: List [Decimal] = [Decimal(0.0)]

        # Cycle attributes.
        self.__installment: Decimal = Decimal(0.0)
        self.__borrowed_money: Decimal = Decimal(0.0)

        # Cycle flags. Some operations can only be executed once per cycle.

    @property
    def bank(self) -> Bank:
        return self.__bank

    @bank.setter
    def bank(self, bank: Bank):
        self.__bank = bank

    @property
    def savings_rate(self) -> Decimal:
        return self.__savings_rate

    @savings_rate.setter
    def savings_rate(self, rate: Decimal):
        self.__savings_rate = Decimal(rate)

    @property
    def borrow_for_securities(self) -> Decimal:
        return self.__borrow_for_securities

    @borrow_for_securities.setter
    def borrow_for_securities(self, percentage: Decimal):
        self.__borrow_for_securities = Decimal(percentage)

    @property
    def fixed_defaulting_rate(self) -> Decimal:
        return self.__fixed_defaulting_rate

    @fixed_defaulting_rate.setter
    def fixed_defaulting_rate(self, rate: Decimal):
        self.__fixed_defaulting_rate = Decimal(rate)

    @property
    def defaulting_probability(self) -> Decimal:
        return self.__defaulting_probability

    @defaulting_probability.setter
    def defaulting_probability(self, probability: Decimal):
        self.__defaulting_probability = Decimal(probability)

    @property
    def defaulting_min(self) -> Decimal:
        return self.__defaulting_min

    @defaulting_min.setter
    def defaulting_min(self, minimum: Decimal):
        self.__defaulting_min = Decimal(minimum)

    @property
    def defaulting_max(self) -> Decimal:
        return self.__defaulting_max

    @defaulting_max.setter
    def defaulting_max(self, maximum: Decimal):
        self.__defaulting_max = Decimal(maximum)

    @property
    def defaults_bought_by_debt_collectors(self) -> Decimal:
        return self.__defaults_bought_by_debt_collectors

    @defaults_bought_by_debt_collectors.setter
    def defaults_bought_by_debt_collectors(self, percentage: Decimal):
        self.__defaults_bought_by_debt_collectors = Decimal(percentage)

    @property
    def unresolved_debt_growth(self) -> Decimal:
        return self.__unresolved_debt_growth

    @unresolved_debt_growth.setter
    def unresolved_debt_growth(self, percentage: Decimal):
        self.__unresolved_debt_growth = Decimal(percentage)

    @property
    def installment(self) -> Decimal:
        return self.__installment

    @property
    def debt(self) -> Decimal:
        return self.liability(BalanceEntries.DEBT)

    @property
    def serviceable_debt(self) -> Decimal:
        return self.debt - self.fixed_defaulting_rate * self.debt

    @property
    def borrowed_money(self) -> Decimal:
        return self.__borrowed_money

    def inflate(self, inflation: Decimal):
        pass

    def start_transactions(self):
        super().start_transactions()

        self.__installment = Decimal(0.0)
        self.__borrowed_money = Decimal(0.0)

        if len(self.__installments) > 0:
            self.__installment = self.__installments.pop(0)

    def process_savings(self):
        total_dep_sav: Decimal = self.asset(BalanceEntries.DEPOSITS) + self.asset(BalanceEntries.SAVINGS)
        savings_target: Decimal = self.savings_rate * total_dep_sav
        savings_transfer: Decimal = savings_target - self.asset(BalanceEntries.SAVINGS)

        self.book_asset(BalanceEntries.SAVINGS, savings_transfer)
        self.book_asset(BalanceEntries.DEPOSITS, -savings_transfer)
        self.bank.book_savings(savings_transfer)

    def borrow(self, amount: Decimal):
        if amount > 0:
            self.__borrowed_money += amount
            self.book_asset(BalanceEntries.DEPOSITS, amount)
            self.book_liability(BalanceEntries.DEBT, amount)

            installment = amount/self.bank.loan_installments

            for i in range(self.bank.loan_installments):
                if len(self.__installments) < i + 1:
                    self.__installments.append(installment)
                else:
                    self.__installments[i] += installment

            self.bank.book_loan(amount)

    def pay_debt(self, debt_payment: DebtPayment):
        """Pay of bank debt. Take defaulting loans into account. This results in not paying a fraction of the amount
        due. Debt only decreases with the amount paid.

        :param debt_payment the debt payment object to record payments in."""

        # Deal with existing unresolved debt.
        self.book_asset(BalanceEntries.UNRESOLVED_DEBT, self.asset(BalanceEntries.UNRESOLVED_DEBT) * self.unresolved_debt_growth)
        self.book_liability(BalanceEntries.UNRESOLVED_DEBT, self.liability(BalanceEntries.UNRESOLVED_DEBT) * self.unresolved_debt_growth)

        unresolved_debt: Decimal = Decimal(0.0)
        debt_payment.debt = self.debt
        debt_payment.full_installment = self.installment

        if self.defaulting_mode == DefaultingMode.PROBABILISTIC and random() < self.defaulting_probability:
            unresolved_debt = Decimal(uniform(float(self.defaulting_min * self.installment),
                                              float(self.defaulting_max * self.installment)))
        elif self.defaulting_mode == DefaultingMode.FIXED:
            unresolved_debt = debt_payment.full_installment * self.fixed_defaulting_rate

        debt_payment.installment_paid = self.__pay_bank(self.installment - unresolved_debt, BalanceEntries.DEBT)
        debt_payment.interest_paid = self.__pay_bank(debt_payment.adjusted_interest, BalanceEntries.EQUITY)

        # Defaults and liquidity shortages do not cancel debt but it won't be owed to the banks anymore.
        # Liquidity shortages are systemic defaults in the context of this simulation.
        self.book_liability(BalanceEntries.DEBT, -unresolved_debt)
        self.book_liability(BalanceEntries.EQUITY, unresolved_debt)

        # Unresolved debt can be bought from the banks by private debt collectors. The price which is paid for that
        # debt is included in the paid off debt since the remaining debt is usually bought at a discount.
        unresolved_debt *= self.defaults_bought_by_debt_collectors
        self.book_asset(BalanceEntries.UNRESOLVED_DEBT, unresolved_debt)
        self.book_liability(BalanceEntries.UNRESOLVED_DEBT, unresolved_debt)

    def pay_bank(self, amount: Decimal) -> Decimal:
        return self.__pay_bank(amount, BalanceEntries.EQUITY)

    def trade_securities_with_bank(self, amount: Decimal, security_type: str = BalanceEntries.SECURITIES) -> Decimal:
        """Attempt to trade the amount of securities, a positive amount indicating a sell, a negative amount
        indicating a buy. When buying, no more than the available deposits + savings can be used."""

        # MBS can only be created by banks. Therefore no more MBS can be sold than those which are on the balance sheet.
        if security_type == BalanceEntries.MBS:
            amount = min(amount, self.asset(BalanceEntries.MBS))

        # check for availability of securities with bank
        if amount < Decimal(0.0):
            amount = -min(-amount, self.bank.asset(BalanceEntries.SECURITIES))

        amount = -self.__pay_bank(-amount, BalanceEntries.EQUITY, self.__borrow_for_securities)
        amount = self.bank.exchange_client_securities(amount, security_type)

        # when selling securities (not MBS), do not subtract more than what was on the balance sheet. The surplus is
        # 'created'. These actually represent securities which were 'hidden' from the books until now.
        securities_delta: Decimal = min(self.asset(security_type), amount)

        self.book_asset(security_type, -securities_delta)
        self.book_liability(BalanceEntries.equity_type(security_type), -securities_delta)

        return amount

    def __pay_bank(self, amount: Decimal, liability_name: str, borrow: Decimal = Decimal(1.0)) -> Decimal:
        """Attempt to pay_bank an amount. Use savings if needed.

        :param amount the amount to pay_bank.
        :param liability_name the name of the liability that needs to be diminished."""

        deposits: Decimal = self.asset(BalanceEntries.DEPOSITS)
        savings: Decimal = self.asset(BalanceEntries.SAVINGS)

        pay_from_deposits: Decimal = min(amount, deposits)
        pay_from_savings: Decimal = min(savings, amount - pay_from_deposits)

        # borrowing can only happen when paying for securities
        to_borrow: Decimal = max(amount - pay_from_deposits - pay_from_savings, Decimal(0.0)) * borrow

        self.borrow(to_borrow)
        pay_from_deposits += to_borrow

        self.book_asset(BalanceEntries.DEPOSITS, -pay_from_deposits)
        self.book_asset(BalanceEntries.SAVINGS, -pay_from_savings)
        self.book_liability(liability_name, -(pay_from_deposits + pay_from_savings))

        self.bank.pay_bank(pay_from_deposits, BalanceEntries.DEPOSITS)
        self.bank.pay_bank(pay_from_savings, BalanceEntries.SAVINGS)

        return pay_from_deposits + pay_from_savings

    def clear(self):
        super().clear()
        self.__installments = [Decimal(0.0)]