from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Set, Tuple, List, Callable

from ordered_set import OrderedSet

from . import EconomicActor
from .balance_entries import *

if TYPE_CHECKING:
    from . import CentralBank, PrivateActor, BalanceSheet


class SpendingMode(Enum):
    FIXED = 0
    PROFIT = 1
    EQUITY = 2
    CAPITAL = 3


class Bank(EconomicActor):

    def __init__(self, central_bank: CentralBank):
        super().__init__(
            OrderedSet([RESERVES, LOANS, MBS, SECURITIES]),
            OrderedSet([DEPOSITS, SAVINGS, DEBT, EQUITY, MBS_EQUITY, SEC_EQUITY]))
        self.__central_bank: CentralBank = central_bank
        self.__clients: Set[PrivateActor] = set()
        self.__installments: List[float] = [0.0]

        self.central_bank.register(self)
        self.max_reserve = central_bank.min_reserve

        self.min_liquidity: float = 0.05
        self.max_reserve: float = 0.05

        self.savings_ir: float = 0.02
        self.loan_ir: float = 0.025
        self.loan_duration: int = 20

        self.defaulting_rate: float = 0.0

        self.no_loss: bool = True
        self.income_from_interest: float = 1.0
        self.retain_profit: bool = True
        self.retain_profit_percentage: float = 0.2

        self.spending_mode: SpendingMode = SpendingMode.PROFIT
        self.fixed_spending: float = 0.0
        self.profit_spending: float = 0.0
        self.equity_spending: float = 0.0
        self.capital_spending: float = 0.0

        # Cycle attributes
        self.__client_installment: float = 0.0
        self.__client_installment_shortage: float = 0.0
        self.__income: float = 0.0
        self.__income_shortage: float = 0.0

    def register(self, client: PrivateActor):
        self.__clients.add(client)

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def clients(self) -> Set[PrivateActor]:
        return self.__clients

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
        return self.balance.delta_history[-1].liability(EQUITY)

    @property
    def financial_profit(self) -> float:
        """Return the financial profit (from gains in security and MBS values) for this cycle. Has to be called after
        the state for the current cycle has been saved."""
        delta_balance: BalanceSheet = self.balance.delta_history[-1]
        return delta_balance.liability(SEC_EQUITY) + delta_balance.liability(MBS_EQUITY)

    def start_transactions(self):
        self.__client_installment = 0.0
        self.__client_installment_shortage = 0.0
        self.__income = 0.0
        self.__income_shortage = 0.0

        for client in self.clients:
            client.start_transactions()

    def end_transactions(self) -> bool:
        success: bool = True

        for client in self.clients:
            success = success and client.end_transactions()

        return success

    def inflate(self, inflation: float):
        self.fixed_spending += self.fixed_spending * inflation

        for client in self.clients:
            client.inflate(inflation)

    def book_savings(self, amount: float):
        self.book_liability(SAVINGS, amount)
        self.book_liability(DEPOSITS, -amount)

    def process_client_savings(self):
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

    def process_interest(self, interest: float):
        # It is possible that interest is negative
        if self.asset(RESERVES) + interest < 0:
            self.borrow(abs(self.asset((RESERVES) + interest)))

        self.book_asset(RESERVES, interest)
        self.book_liability(EQUITY, interest)

    def process_income(self):
        """Collect interest, installments and other income.
        :return True if all collections were successful."""

        for client in self.clients:
            # take defaults into account
            adjusted_installment: float = client.installment - client.installment * self.defaulting_rate
            paid_installment: float = self.__process_client_payment(client, adjusted_installment, client.pay_debt)

            self.__client_installment += client.installment
            self.__client_installment_shortage += client.installment - paid_installment

            income: float = 0.0
            expected_interest: float = client.liability(DEBT) * self.loan_ir

            # no interest is paid on defaulting loans
            adjusted_interest: float = expected_interest - expected_interest * self.defaulting_rate
            paid_interest: float = self.__process_client_payment(client, adjusted_interest, client.pay)
            income += paid_interest

            bank_costs: float = expected_interest / self.income_from_interest - expected_interest
            income += self.__process_client_payment(client, bank_costs, client.pay)

            self.__income += income
            self.__income_shortage += expected_interest + bank_costs - income

        self.book_liability(DEPOSITS, -self.income)
        self.book_liability(EQUITY, self.income)

        # subtract installment proportionally from loans and mbs
        loans: float = self.asset(LOANS)
        mbs: float = self.asset(MBS)
        mbs_equity: float = self.liability(MBS_EQUITY)
        total: float = loans + mbs - mbs_equity # take market changes in MBS into account.

        self.book_asset(LOANS, -self.client_installment * loans / total)
        self.book_asset(MBS, -self.client_installment * mbs / total)
        self.book_liability(MBS_EQUITY, -self.client_installment * mbs_equity / total)

    def __process_client_payment(self, client: PrivateActor, amount: float, pay_method: Callable) -> float:
        client_deposits: float = client.asset(DEPOSITS)
        client_savings: float = client.asset(SAVINGS)

        pay_method(amount)

        paid_from_deposits: float = client_deposits - client.asset(DEPOSITS)
        paid_from_savings: float = client_savings - client.asset(SAVINGS)

        self.book_liability(DEPOSITS, -paid_from_deposits)
        self.book_liability(SAVINGS, -paid_from_savings)

        return paid_from_deposits + paid_from_savings

    def spend(self):
        # calculate real_profit
        profit: float = self.balance.delta_history[-1].asset(EQUITY)
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

        self.__trade_client_securities(max_securities - self.asset(SECURITIES))

        # invest a maximum in order to minimise surplus reserves
        max_nominal_reserve: float = self.max_reserve * total_deposits

        if self.asset(RESERVES) > max_nominal_reserve:
            self.__trade_client_securities(max_nominal_reserve - self.asset(RESERVES))

    def trade_central_bank_securities(self, amount: float) -> float:
        """Trade securities with the central bank. A positive amount indicates a sell to the central bank.
        Returns the actual number of securities traded."""

        traded_securities: float = min(amount, self.asset(SECURITIES))

        self.book_asset(SECURITIES, -traded_securities)
        self.book_asset(RESERVES, traded_securities)

        return traded_securities

    def __trade_client_securities(self, amount: float):
        """Trade securities proportionally with each client, if possible."""
        total_deposits: float = self.liability(DEPOSITS) + self.liability(SAVINGS)
        traded_securities: float = 0.0

        for client in self.clients:
            client_deposits = client.asset(DEPOSITS) + client.asset(SAVINGS)
            fraction: float = client_deposits / total_deposits * amount

            traded_securities += self.__process_client_payment(client, fraction, client.trade_securities)

        self.book_liability(EQUITY, -traded_securities)
        self.book_asset(SECURITIES, traded_securities)
        self.book_liability(SEC_EQUITY, traded_securities)

