from enum import Enum
from typing import Set, Tuple, List

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.central_bank import CentralBank
from emusim.cockpit.supply.euro.economic_actor import EconomicActor
from emusim.cockpit.supply.euro.private_actor import PrivateActor


class SpendingMode(Enum):
    FIXED = 0
    PROFIT = 1
    EQUITY = 2
    CAPITAL = 3


class Bank(EconomicActor):
    max_reserve: float

    savings_ir: float
    loan_ir: float
    loan_duration: int

    no_loss: bool = True
    income_from_interest: float = 1.0
    min_profit: float = 0.2

    spending_mode: SpendingMode = SpendingMode.PROFIT
    fixed_spending: float = 0.0
    profit_spending: float = 0.0
    equity_spending: float = 0.0
    capital_spending: float = 0.0

    __central_bank: CentralBank
    __clients: Set[PrivateActor] = set()

    __installments: List[float] = [0.0]

    def __init__(self, central_bank: CentralBank):
        self.__central_bank = central_bank
        self.central_bank.register(self)
        self.max_reserve = central_bank.min_reserve

    def register(self, client: PrivateActor):
        self.__clients.add(client)

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def clients(self) -> Set[PrivateActor]:
        return self.__clients

    @property
    def assets(self) -> Set:
        return {RESERVES, LOANS, SECURITIES, MBS}

    @property
    def liabilities(self) -> Set:
        return {DEPOSITS, SAVINGS, DEBT, EQUITY}

    def book_savings(self, amount: float):
        self.book_liabilaty(SAVINGS, amount)
        self.book_liabilaty(DEPOSITS, -amount)

    def process_savings(self):
        interest = self.liability(SAVINGS) * self.savings_ir
        self.book_liabilaty(DEPOSITS, interest)
        self.book_liabilaty(EQUITY, -interest)

        for client in self.clients:
            interest = client.asset(SAVINGS) * self.savings_ir
            client.book_asset(DEPOSITS, interest)
            client.book_liabilaty(EQUITY, interest)

    def book_loan(self, amount: float):
        self.book_asset(LOANS, amount)
        self.book_liabilaty(DEPOSITS, amount)

    def process_private_loans_and_income(self) -> bool:
        success: bool = True
        total_interest: float = 0.0
        total_installment: float = 0.0

        for client in self.clients:
            result: Tuple[bool, float, float] = client.pay_debt(self.loan_ir)
            success = success and result[0]
            total_interest += result[1]
            total_installment += result[2]

        self.book_liabilaty(DEPOSITS, -total_interest)
        self.book_liabilaty(EQUITY, total_interest)

        self.book_asset(LOANS, -total_installment)
        self.book_liabilaty(DEPOSITS, -total_installment)

        # calculate income from other sources than interest
        income: float = total_interest / self.income_from_interest - total_interest
        self.book_liabilaty(DEPOSITS, -income)
        self.book_liabilaty(EQUITY, income)

        return success

    def spend(self):
        expenses: float = 0.0

        if self.spending_mode == SpendingMode.FIXED:
            expenses = self.fixed_spending
        elif self.spending_mode == SpendingMode.PROFIT:
            # calculate profit
            profit: float = 0.0 # TODO
            expenses: float = profit * self.profit_spending

            self.book_liabilaty(EQUITY, -expenses)
            self.book_liabilaty(DEPOSITS, expenses)
        elif self.spending_mode == SpendingMode.EQUITY:
            expenses = self.liability(EQUITY) * self.equity_spending
        elif self.spending_mode == SpendingMode.CAPITAL:
            expenses = (self.liability(EQUITY) + self.liability(SEC_EQUITY)) * self.capital_spending

            if expenses > self.liability(EQUITY):
                securities_to_sell = expenses - self.liability(EQUITY)
                self.book_liabilaty(DEPOSITS, -securities_to_sell)
                self.book_asset(SECURITIES, -securities_to_sell)
                self.book_liabilaty(SEC_EQUITY, -securities_to_sell)
                self.book_liabilaty(EQUITY, securities_to_sell)

        self.book_liabilaty(EQUITY, -expenses)
        self.book_liabilaty(DEPOSITS, expenses)

    def borrow(self, amount: float):
        self.central_bank.book_loan(amount)
        self.book_asset(RESERVES, amount)
        self.book_liabilaty(DEBT, amount)

        installment: float = amount/self.central_bank.loan_duration

        for i in range(self.central_bank.loan_duration):
            if len(self.__installments) < i + 1:
                self.__installments.append(installment)
            else:
                self.__installments[i] += installment

    def pay_debt(self, ir: float) -> Tuple[float, float]:
        interest: float = self.liability(DEBT) * ir
        installment: float = self.__installments.pop(0)
        total: float = interest + installment

        to_borrow: float = max(0.0, total - self.asset(RESERVES))
        self.borrow(to_borrow)
        self.book_asset(RESERVES, -total)
        self.book_liabilaty(DEBT, -installment)
        self.book_liabilaty(EQUITY, -interest)

        return tuple((interest, installment))

    def update_reserves(self):
        min_requirement: float = (self.liability(DEPOSITS) + self.liability(SAVINGS)) * self.central_bank.min_reserve

        max_mbs: float = min_requirement * self.central_bank.mbs_reserve
        new_mbs: float = min(self.asset(LOANS), max_mbs - self.asset(MBS))
        self.book_asset(LOANS, -new_mbs)
        self.book_asset(MBS, new_mbs)

        max_securities: float = min_requirement * self.central_bank.securities_reserve
        new_securities: float = max_securities - self.asset(SECURITIES)
        # TODO securities balance sheet operations

        min_reserves: float = min_requirement\
                              * (1 - self.central_bank.securities_reserve - self.central_bank.mbs_reserve)
        self.borrow(max(0.0, min_reserves - self.asset(RESERVES)))