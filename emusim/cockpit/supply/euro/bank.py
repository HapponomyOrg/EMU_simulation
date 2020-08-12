from enum import Enum
from typing import Set, Tuple, List

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.balance_sheet import BALANCE, DELTA
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

    defaulting_rate: float = 0.0

    no_loss: bool = True
    income_from_interest: float = 1.0
    retain_profit: bool = True
    retain_profit_percentage: float = 0.2

    spending_mode: SpendingMode = SpendingMode.PROFIT
    fixed_spending: float = 0.0
    profit_spending: float = 0.0
    equity_spending: float = 0.0
    capital_spending: float = 0.0

    __central_bank: CentralBank
    __clients: Set[PrivateActor] = set()

    __installments: List[float] = [0.0]

    # Cycle attributes
    __client_installment: float = 0.0
    __client_installment_shortage: float = 0.0
    __income: float = 0.0
    __income_shortage: float = 0.0

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

    @property
    def client_installment(self) -> float:
        return self.__client_installment

    @property
    def client_installment_shortage(self) -> float:
        return self.__client_installment_shortage

    @property
    def income(self) -> float:
        return self.__income

    @property
    def income_shortage(self) -> float:
        return self.__income_shortage

    @property
    def real_profit(self) -> float:
        """Return the profit for this cycle. Has to be called after the state for the current cycle has been saved."""
        return self.balance.history[-1][DELTA].liability(EQUITY)

    @property
    def financial_profit(self) -> float:
        """Return the financial profit (from gains in security values) for this cycle. Has to be called after the state
        for the current cycle has been saved."""
        return self.balance.history[-1][DELTA].liability(SEC_EQUITY)

    def start_cycle(self):
        self.__client_installment = 0.0
        self.__client_installment_shortage = 0.0
        self.__income = 0.0
        self.__income_shortage = 0.0

    def inflate_parameters(self, inflation: float):
         self.fixed_spending += self.fixed_spending * inflation

    def book_savings(self, amount: float):
        self.book_liability(SAVINGS, amount)
        self.book_liability(DEPOSITS, -amount)

    def process_savings(self):
        interest = self.liability(SAVINGS) * self.savings_ir
        self.book_liability(DEPOSITS, interest)
        self.book_liability(EQUITY, -interest)

        for client in self.clients:
            interest = client.asset(SAVINGS) * self.savings_ir
            client.book_asset(DEPOSITS, interest)
            client.book_liability(EQUITY, interest)

    def book_loan(self, amount: float):
        self.book_asset(LOANS, amount)
        self.book_liability(DEPOSITS, amount)

    def process_private_loans_and_income(self):
        """Collect interest, installments and other income.
        Return True if all collections were successful."""

        for client in self.clients:
            # take defaults into account
            adjusted_installment: float = client.installment - client.installment * self.defaulting_rate
            paid_installment: float = self.__process_client_payment(client, adjusted_installment)

            client.settle_debt()
            self.__client_installment += client.installment
            self.__client_installment_shortage += client.installment - paid_installment

            income: float = 0.0
            expected_interest: float = client.liability(DEBT) * self.loan_ir

            # no interest is paid on defaulting loans
            adjusted_interest: float = expected_interest - expected_interest * self.defaulting_rate
            paid_interest: float = self.__process_client_payment(client, adjusted_interest)
            income += paid_interest

            bank_costs: float = expected_interest / self.income_from_interest - expected_interest
            income += self.__process_client_payment(client, bank_costs)

            self.__income += income
            self.__income_shortage += expected_interest + bank_costs - income

        self.book_liability(DEPOSITS, -self.income)
        self.book_liability(EQUITY, self.income)

        # subtract installment proportionally from loans and mbs
        loans: float = self.asset(LOANS)
        mbs: float = self.asset(MBS)
        total: float = loans + mbs

        self.book_asset(LOANS, -self.client_installment * loans / total)
        self.book_asset(MBS, -self.client_installment * mbs / total)

    def __process_client_payment(self, client: PrivateActor, amount: float) -> float:
        client_deposits: float = client.asset(DEPOSITS)
        client_savings: float = client.asset(SAVINGS)

        client.pay(amount)

        paid_from_deposits: float = client_deposits - client.asset(DEPOSITS)
        paid_from_savings: float = client_savings - client.asset(SAVINGS)

        self.book_liability(DEPOSITS, -paid_from_deposits)
        self.book_liability(SAVINGS, -paid_from_savings)

        return paid_from_deposits + paid_from_savings

    def spend(self):
        # calculate real_profit
        profit: float = self.liability(EQUITY) - self.balance.history[-1][BALANCE].asset(EQUITY)
        expenses: float = 0.0

        if self.spending_mode == SpendingMode.FIXED:
            expenses = self.fixed_spending
        elif self.spending_mode == SpendingMode.PROFIT:
            expenses: float = max(0.0, profit * self.profit_spending)

            self.book_liability(EQUITY, -expenses)
            self.book_liability(DEPOSITS, expenses)
        elif self.spending_mode == SpendingMode.EQUITY:
            expenses = self.liability(EQUITY) * self.equity_spending
        elif self.spending_mode == SpendingMode.CAPITAL:
            expenses = (self.liability(EQUITY) + self.liability(SEC_EQUITY)) * self.capital_spending

            if expenses > self.liability(EQUITY):
                available_deposits: float = self.liability(DEPOSITS) + self.liability(SAVINGS)
                securities_to_sell: float = min(available_deposits, expenses - self.liability(EQUITY))

                for client in self.clients:
                    fraction: float = (client.asset(DEPOSITS) + client.asset(SAVINGS)) / available_deposits

                    client.pay(fraction * securities_to_sell)

                self.book_liability(DEPOSITS, -securities_to_sell)
                self.book_asset(SECURITIES, -securities_to_sell)
                self.book_liability(SEC_EQUITY, -securities_to_sell)
                self.book_liability(EQUITY, securities_to_sell)

        if self.retain_profit:
            expenses = min(expenses, max(0.0, profit - profit * self.retain_profit_percentage))

        if self.no_loss:
            expenses = min(expenses, max(0.0, profit))

        self.book_liability(EQUITY, -expenses)
        self.book_liability(DEPOSITS, expenses)

    def borrow(self, amount: float):
        self.central_bank.book_loan(amount)
        self.book_asset(RESERVES, amount)
        self.book_liability(DEBT, amount)

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
        self.book_asset(RESERVES, -installment)
        self.book_liability(DEBT, -installment)

        # interest is used to fund central bank working costs and the rest is redistributed to member states,
        # eventually resulting in deposits
        self.book_liability(EQUITY, -interest)
        self.book_liability(DEPOSITS, interest)

        return tuple((interest, installment))

    def update_reserves(self):
        """Update reserves so that they are adequate for the current amount of deposits + savings on the balance
        sheet of the bank. If this results in changes in deposits held on the balance sheet, these changes are
        carried over to the next reserve calculations."""
        total_deposits: float = self.liability(DEPOSITS) + self.liability(SAVINGS)

        min_reserves: float = total_deposits * self.central_bank.real_min_reserve
        self.borrow(max(0.0, min_reserves - self.asset(RESERVES)))

        max_mbs: float = total_deposits * self.central_bank.mbs_real_reserve
        new_mbs: float = min(self.asset(LOANS), max_mbs - self.asset(MBS))
        self.book_asset(LOANS, -new_mbs)
        self.book_asset(MBS, new_mbs)

        max_securities: float = total_deposits * self.central_bank.securities_real_reserve

        # when selling securities, enough money needs to be available in the economy to pay for them.
        available_deposits: float = self.liability(DEPOSITS) + self.liability(SAVINGS)

        self.__buy_securities(max(-available_deposits, max_securities - self.asset(SECURITIES)))

        # invest a maximum in order to minimise surplus reserves
        max_nominal_reserve: float = self.max_reserve * total_deposits

        if self.asset(RESERVES) > max_nominal_reserve:
            self.__buy_securities(max_nominal_reserve - self.asset(RESERVES))

    def __buy_securities(self, amount: float):
        self.book_asset(SECURITIES, amount)
        self.book_liability(DEPOSITS, amount)
        self.book_liability(EQUITY, -amount)
        self.book_liability(SEC_EQUITY, amount)
