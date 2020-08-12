from typing import Set, List

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.bank import Bank
from emusim.cockpit.supply.euro.economic_actor import EconomicActor


class PrivateActor(EconomicActor):
    savings_rate: float = 0.02

    __bank: Bank
    __installments: List [float] = [0.0]

    # cycle attributes
    __installment: float

    def __init__(self, bank: Bank):
        self.bank.register(self)

    @property
    def bank(self) -> Bank:
        return self.__bank

    @property
    def assets(self) -> Set:
        return {DEPOSITS, SECURITIES, SAVINGS}

    @property
    def liabilities(self) -> Set:
        return {DEBT, EQUITY}

    @property
    def installment(self) -> float:
        return self.__installment

    def start_cycle(self):
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

    def settle_debt(self):
        """Eliminate the amount of debt from the balance sheet. Non paid debt is suprlus equity because the debt
        could not be collected and can therefore never be settled."""

        self.book_liability(DEBT, -self.installment)
        self.book_liability(EQUITY, self.installment)

    def pay(self, amount: float):
        self.__pay(amount, EQUITY)

    def __pay(self, amount: float, liability_name: str):
        """Attampt tp pay an amount. Use savings if needed."""

        deposits: float = self.asset(DEPOSITS)
        savings: float = self.asset(SAVINGS)

        pay_from_deposits: float = min(amount, deposits)
        pay_from_savings: float = min(savings, amount - pay_from_deposits)

        self.book_asset(DEPOSITS, -pay_from_deposits)
        self.book_asset(SAVINGS, -pay_from_savings)
        self.book_liability(liability_name, -(pay_from_deposits + pay_from_savings))
