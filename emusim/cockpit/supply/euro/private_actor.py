from typing import Set, List, Tuple

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.bank import Bank
from emusim.cockpit.supply.euro.economic_actor import EconomicActor


class PrivateActor(EconomicActor):
    savings_rate: float = 0.02

    __bank: Bank
    __installments: List [float] = [0.0]

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

    def save(self, amount: float):
        self.book_asset(SAVINGS, amount)
        self.book_asset(DEPOSITS, -amount)
        self.bank.book_savings(amount)

    def borrow(self, amount: float):
        if amount > 0:
            self.book_asset(DEPOSITS, amount)
            self.book_liabilaty(DEBT, amount)
            self.bank.book_loan(amount)

            installment = amount/self.bank.loan_duration

            for i in range(self.bank.loan_duration):
                if len(self.__installments) < i + 1:
                    self.__installments.append(installment)
                else:
                    self.__installments[i] += installment

    def pay_debt(self, ir: float) -> Tuple[bool, float, float]:
        """Pay interest on debt, then pay installment.
        Return a tuple which contains, in order:
        * Bool: indicating whether all payments where successfully made.
        * float: Amount of interest paid.
        * float: Installment amount paid."""

        result: Tuple[bool, float] = self.__pay(self.liability(DEBT) * ir)
        success: bool = result[0]
        interest_paid: float = result[1]
        self.book_liabilaty(EQUITY, -interest_paid)

        result = self.__pay(self.__installments.pop(0))
        success = success and result[0]
        installment_paid: float = result[1]
        self.book_liabilaty(DEBT, -installment_paid)

        return tuple((success, installment_paid, installment_paid))

    def __pay(self, amount: float) -> Tuple[bool, float]:
        deposits: float = self.asset(DEPOSITS)
        savings: float = self.asset(SAVINGS)

        pay_from_deposits: float = min(amount, deposits)
        pay_from_savings: float = min(savings, amount - pay_from_deposits)

        self.book_asset(DEPOSITS, -pay_from_deposits)
        self.book_asset(SAVINGS, -pay_from_savings)

        paid: float = pay_from_deposits + pay_from_savings

        return tuple((paid == amount, paid))
