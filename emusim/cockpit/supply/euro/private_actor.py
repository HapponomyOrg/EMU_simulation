from __future__ import annotations

from typing import TYPE_CHECKING, List

from ordered_set import OrderedSet

from . import EconomicActor
from .balance_entries import *

if TYPE_CHECKING:
    from . import Bank


class PrivateActor(EconomicActor):

    def __init__(self, bank: Bank):
        super().__init__(
            OrderedSet([DEPOSITS, SECURITIES, SAVINGS]),
            OrderedSet([DEBT, EQUITY, SEC_EQUITY]))
        self.__bank: Bank = bank
        self.bank.register(self)

        self.savings_rate: float = 0.02
        self.defaulting_rate = 0.0

        self.__installments: List [float] = [0.0]

        # cycle attributes
        self.__installment: float = 0.0

    @property
    def bank(self) -> Bank:
        return self.__bank

    @property
    def installment(self) -> float:
        return self.__installment

    def inflate(self, inflation: float):
        pass

    def start_transactions(self):
        if len(self.__installments) > 0:
            self.__installment = self.__installments.pop(0)

    def save(self, amount: float):
        self.book_asset(SAVINGS, amount)
        self.book_asset(DEPOSITS, -amount)
        self.bank.book_savings(amount)

    def borrow(self, amount: float):
        if amount > 0:
            self.book_asset(DEPOSITS, amount)
            self.book_liability(DEBT, amount)
            self.bank.book_loan(amount)

            installment = amount/self.bank.loan_duration

            for i in range(self.bank.loan_duration):
                if len(self.__installments) < i + 1:
                    self.__installments.append(installment)
                else:
                    self.__installments[i] += installment

    def pay_debt(self, amount: float):
        self.__pay(amount, DEBT)

    def pay(self, amount: float):
        self.__pay(amount, EQUITY)

    def trade_securities(self, amount: float):
        """Attempt to trade the amount of securities, a positive amount indicating a sell, a negative amount
        indicating a buy. When buying, no more than the available deposits + savings can be used."""

        equity: float = self.liability(EQUITY)
        self.__pay(-amount, EQUITY)

        sold_securities: float = self.liability(EQUITY) - equity

        # when selling, do not subtract more than what was on the balance sheet. The surplus is 'created'. These
        # actually represent securities which were hidden from the books until now.
        securities_delta: float = min(self.asset(SECURITIES), sold_securities)

        self.book_asset(SECURITIES, -securities_delta)
        self.book_liability(SEC_EQUITY, -securities_delta)

    def __pay(self, amount: float, liability_name: str):
        """Attempt to pay an amount. Use savings if needed."""

        deposits: float = self.asset(DEPOSITS)
        savings: float = self.asset(SAVINGS)

        pay_from_deposits: float = min(amount, deposits)
        pay_from_savings: float = min(savings, amount - pay_from_deposits)

        self.book_asset(DEPOSITS, -pay_from_deposits)
        self.book_asset(SAVINGS, -pay_from_savings)
        self.book_liability(liability_name, -(pay_from_deposits + pay_from_savings))
