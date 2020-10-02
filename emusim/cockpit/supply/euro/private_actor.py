from __future__ import annotations

from typing import TYPE_CHECKING, List
from enum import Enum

from ordered_set import OrderedSet
from random import random, uniform

from . import EconomicActor, DebtPayment, BalanceEntries

if TYPE_CHECKING:
    from . import Bank


class DefaultingMode(Enum):
    FIXED = 0
    PROBABILISTIC = 1


class PrivateActor(EconomicActor):

    def __init__(self, bank: Bank):
        super().__init__(
            OrderedSet([BalanceEntries.DEPOSITS, BalanceEntries.UNRESOLVED_DEBT, BalanceEntries.SECURITIES,
                        BalanceEntries.SAVINGS, BalanceEntries.MBS]),
            OrderedSet([BalanceEntries.DEBT, BalanceEntries.UNRESOLVED_DEBT, BalanceEntries.EQUITY,
                        BalanceEntries.MBS_EQUITY]))
        self.__bank: Bank = bank
        self.bank.register(self)

        self.savings_rate: float = 0.02

        self.borrow_for_securities: float = 0.0

        self.defaulting_mode: DefaultingMode = DefaultingMode.FIXED
        self.fixed_defaulting_rate = 0.0
        self.defaulting_probability = 0.0
        self.defaulting_min = 0.0 # minimum defaulting percentage for probabilistic mode
        self.defaulting_max = 0.0 # maximum defaulting percentage for probabilistic mode

        self.defaults_bought_by_debt_collectors: float = 0.0 # In %
        self.unresolved_debt_growth: float = 0.0 # Net growth of unresolved debt. Can be negative.

        self.__installments: List [float] = [0.0]

        # Cycle attributes.
        self.__installment: float = 0.0

        # Cycle flags. Some operations can only be executed once per cycle.

    @property
    def bank(self) -> Bank:
        return self.__bank

    @property
    def installment(self) -> float:
        return self.__installment

    @property
    def debt(self) -> float:
        return self.liability(BalanceEntries.DEBT)

    @property
    def serviceable_debt(self) -> float:
        return self.debt - self.fixed_defaulting_rate * self.debt

    def inflate(self, inflation: float):
        pass

    def start_transactions(self):
        super().start_transactions()

        if len(self.__installments) > 0:
            self.__installment = self.__installments.pop(0)

    def save(self, amount: float):
        self.book_asset(BalanceEntries.SAVINGS, amount)
        self.book_asset(BalanceEntries.DEPOSITS, -amount)
        self.bank.book_savings(amount)

    def borrow(self, amount: float):
        if amount > 0:
            self.book_asset(BalanceEntries.DEPOSITS, amount)
            self.book_liability(BalanceEntries.DEBT, amount)

            installment = amount/self.bank.loan_duration

            for i in range(self.bank.loan_duration):
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

        unresolved_debt: float = 0.0
        debt_payment.debt = self.debt
        debt_payment.full_installment = self.installment

        if self.defaulting_mode == DefaultingMode.PROBABILISTIC and random() < self.defaulting_probability:
            unresolved_debt = uniform(self.defaulting_min * self.installment, self.defaulting_max * self.installment)
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

    def pay_bank(self, amount: float) -> float:
        return self.__pay_bank(amount, BalanceEntries.EQUITY)

    def trade_securities_with_bank(self, amount: float, security_type: str = BalanceEntries.SECURITIES):
        """Attempt to trade the amount of securities, a positive amount indicating a sell, a negative amount
        indicating a buy. When buying, no more than the available deposits + savings can be used."""

        equity: float = self.liability(BalanceEntries.EQUITY)
        self.__pay_bank(-amount, BalanceEntries.EQUITY, True)

        traded_securities: float = self.liability(BalanceEntries.EQUITY) - equity

        self.bank.receive_client_securities(traded_securities, security_type)

        # when selling, do not subtract more than what was on the balance sheet. The surplus is 'created'. These
        # actually represent securities which were hidden from the books until now.
        securities_delta: float = min(self.asset(security_type), traded_securities)

        self.book_asset(security_type, -securities_delta)
        self.book_liability(BalanceEntries.equity_type(security_type), -securities_delta)

    def __pay_bank(self, amount: float, liability_name: str, borrow: bool = False) -> float:
        """Attempt to pay_bank an amount. Use savings if needed.

        :param amount the amount to pay_bank.
        :param liability_name the name of the liability that needs to be diminished."""

        deposits: float = self.asset(BalanceEntries.DEPOSITS)
        savings: float = self.asset(BalanceEntries.SAVINGS)

        pay_from_deposits: float = min(amount, deposits)
        pay_from_savings: float = min(savings, amount - pay_from_deposits)

        # borrowing can only happen when paying for securities
        if pay_from_deposits + pay_from_savings < amount and borrow:
            to_borrow: float = round((amount - pay_from_deposits - pay_from_savings) * self.borrow_for_securities, 4)

            self.bank.borrow(to_borrow)
            pay_from_deposits += to_borrow

        self.book_asset(BalanceEntries.DEPOSITS, -pay_from_deposits)
        self.book_asset(BalanceEntries.SAVINGS, -pay_from_savings)
        self.book_liability(liability_name, -(pay_from_deposits + pay_from_savings))

        self.bank.pay_bank(pay_from_deposits, BalanceEntries.DEPOSITS)
        self.bank.pay_bank(pay_from_savings, BalanceEntries.SAVINGS)

        return pay_from_deposits + pay_from_savings

    def clear(self):
        super().clear()
        self.__installments = [0.0]