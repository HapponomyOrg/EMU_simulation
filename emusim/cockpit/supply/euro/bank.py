from __future__ import annotations

import numpy

from emusim.cockpit.utilities.simplex import simplex
from enum import Enum
from typing import TYPE_CHECKING, Set, Tuple, List, Callable

from ordered_set import OrderedSet

from . import EconomicActor, BalanceEntries

if TYPE_CHECKING:
    from . import CentralBank, PrivateActor, BalanceSheet


class SpendingMode(Enum):
    FIXED = 0
    PROFIT = 1
    EQUITY = 2
    CAPITAL = 3


class DebtPayment():

    def __init__(self, interest_rate: float):
        self.__interest_rate: float = interest_rate
        self.__debt: float = 0.0
        self.__adjusted_debt: float = 0.0
        self.__full_installment: float = 0.0
        self.__full_interest: float = 0.0
        self.__adjusted_interest: float = 0.0
        self.__installment_paid: float = 0.0
        self.__interest_paid: float = 0.0

    @property
    def debt(self) -> float:
        return self.__debt

    @debt.setter
    def debt(self, amount: float):
        self.__debt = amount
        self.__adjusted_debt = amount
        self.__full_interest = amount * self.__interest_rate
        self.__adjusted_interest = self.__full_interest

    @property
    def adjusted_debt(self) -> float:
        return self.__adjusted_debt

    @property
    def full_installment(self) -> float:
        return self.__full_installment

    @full_installment.setter
    def full_installment(self, amount: float):
        self.__full_installment = amount

    @property
    def full_interest(self) -> float:
        return self.__full_interest

    @property
    def adjusted_interest(self) -> float:
        return self.__adjusted_interest

    @property
    def installment_paid(self) -> float:
        return self.__installment_paid

    @installment_paid.setter
    def installment_paid(self, paid: float):
        self.__installment_paid = paid

        # No interest is charged on unpaid installments. In the context of the simulation, additional unpaid
        # installments are treated as surplus systemic defaults and thus the adjusted debt, installment and interest
        # might need to be updated.
        self.__adjusted_debt -= self.full_installment - paid
        self.__adjusted_interest = self.__adjusted_debt * self.__interest_rate

    @property
    def interest_paid(self) -> float:
        return self.__interest_paid

    @interest_paid.setter
    def interest_paid(self, paid: float):
        self.__interest_paid = paid


class Bank(EconomicActor):

    def __init__(self, central_bank: CentralBank):
        super().__init__(
            OrderedSet([BalanceEntries.RESERVES, BalanceEntries.LOANS, BalanceEntries.MBS, BalanceEntries.SECURITIES]),
            OrderedSet([BalanceEntries.DEPOSITS, BalanceEntries.SAVINGS, BalanceEntries.DEBT, BalanceEntries.EQUITY,
                        BalanceEntries.MBS_EQUITY]))
        self.__central_bank: CentralBank = central_bank
        self.__clients: Set[PrivateActor] = set()
        self.__installments: List[float] = [0.0]

        self.central_bank.register(self)
        self.__min_reserve = central_bank.min_reserve

        self.__min_risk_assets: float = 0.0
        self.__max_risk_assets: float = 1.0 # Maximum % of assets being MBS and/or Securities

        # The sum of the two following parameters must always be >= 1.0
        self.__max_mbs_assets: float = 1.0 # Max % of risk assets
        self.__max_security_assets: float = 1.0 # Max % of risk assets

        self.savings_ir: float = 0.02
        self.loan_ir: float = 0.025
        self.loan_duration: int = 20

        self.no_loss: bool = True
        self.income_from_interest: float = 0.8
        self.retain_profit: bool = True
        self.retain_profit_percentage: float = 0.2

        self.spending_mode: SpendingMode = SpendingMode.PROFIT
        self.fixed_spending: float = 0.0
        self.profit_spending: float = 0.8
        self.equity_spending: float = 0.0
        self.capital_spending: float = 0.0

        # Cycle flags. Some actions can only be executed once per cycle.
        self.__risk_assets_updated: bool = False
        self.__income_processed: bool = False
        self.__savings_processed: bool = False
        self.__debt_paid: bool = False
        self.__spending_processed: bool = False
        self.__reserves_updated: bool = False

        # Cycle attributes
        self.__client_installment: float = 0.0
        self.__client_installment_shortage: float = 0.0
        self.__income: float = 0.0
        self.__income_shortage: float = 0.0

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def min_reserve(self) -> float:
        return self.__min_reserve

    @min_reserve.setter
    def min_reserve(self, percentage: float):
        self.__min_reserve = max(self.central_bank.min_reserve, percentage)

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
        delta_balance: BalanceSheet = self.balance.delta_history[-1]

        return delta_balance.liability(BalanceEntries.EQUITY) + delta_balance.liability(BalanceEntries.MBS_EQUITY)

    @property
    def client_liabilities(self) -> float:
        return self.liability(BalanceEntries.DEPOSITS) + self.liability(BalanceEntries.SAVINGS)

    @property
    def safe_assets(self) -> float:
        return self.asset(BalanceEntries.RESERVES) + self.asset(BalanceEntries.LOANS)

    @property
    def risk_assets(self) -> float:
        return self.asset(BalanceEntries.MBS) + self.asset(BalanceEntries.SECURITIES)

    @property
    def min_risk_assets(self) -> float:
        return self.__min_risk_assets

    @min_risk_assets.setter
    def min_risk_assets(self, min_percentage: float):
        self.__min_risk_assets = min_percentage
        if self.max_risk_assets < min_percentage:
            self.max_risk_assets = min_percentage

    @property
    def max_risk_assets(self) -> float:
        return self.__max_risk_assets

    @max_risk_assets.setter
    def max_risk_assets(self, max_percentage: float):
        self.__max_risk_assets = max_percentage

        if self.min_risk_assets > max_percentage:
            self.min_risk_assets = max_percentage

    @property
    def max_mbs_assets(self):
        return self.__max_mbs_assets

    @max_mbs_assets.setter
    def max_mbs_assets(self, max_percentage: float):
        self.__max_mbs_assets = max_percentage

        if self.max_security_assets < 1 - max_percentage:
            self.max_security_assets = 1 - max_percentage

    @property
    def max_security_assets(self):
        return self.__max_security_assets

    @max_security_assets.setter
    def max_security_assets(self, max_percentage):
        self.__max_security_assets = max_percentage

        if self.max_mbs_assets < 1 - max_percentage:
            self.max_mbs_assets = 1 - max_percentage

    @property
    def lcr(self) -> float:
        """Return the Liquidity Coverage Ratio of the bank. Must be called before transactions are started or after
        transactions are ended. Results during transactions are not accurate."""
        return 1.0 # TODO

    def register(self, client: PrivateActor):
        self.__clients.add(client)

    def start_transactions(self):
        super().start_transactions()

        self.__client_installment = 0.0
        self.__client_installment_shortage = 0.0
        self.__income = 0.0
        self.__income_shortage = 0.0

        self.__risk_assets_updated = False
        self.__income_processed = False
        self.__savings_processed = False
        self.__debt_paid = False
        self.__spending_processed = False
        self.__reserves_updated = False

        for client in self.clients:
            client.start_transactions()

    def end_transactions(self) -> bool:
        success: bool = super().end_transactions()

        for client in self.clients:
            success = success and client.end_transactions()

        return success

    def inflate(self, inflation: float):
        self.fixed_spending += self.fixed_spending * inflation

        for client in self.clients:
            client.inflate(inflation)

    def grow_mbs(self, growth: float):
        super().grow_mbs(growth)

        for client in self.clients:
            client.grow_mbs(growth)

    def grow_securities(self, growth: float):
        super().grow_securities(growth)

        for client in self.clients:
            client.grow_securities(growth)

    def book_savings(self, amount: float):
        """Transfer depositis to savings. This should only be called by the client."""
        self.book_liability(BalanceEntries.SAVINGS, amount)
        self.book_liability(BalanceEntries.DEPOSITS, -amount)

    def pay_bank(self, amount: float, source: str):
        """Pay the bank an amount of money. Must only be called by clients of the bank.

        :param: amount paid to the bank.
        :param source: indicate whether it comes from DEPOSITS or SAVINGS."""

        self.book_liability(source, -amount)
        self.book_liability(BalanceEntries.EQUITY, amount)

    def process_client_savings(self):
        """Pay interest on client savings."""
        interest = self.liability(BalanceEntries.SAVINGS) * self.savings_ir
        self.book_liability(BalanceEntries.SAVINGS, interest)
        self.book_liability(BalanceEntries.EQUITY, -interest)

        for client in self.clients:
            interest = client.asset(BalanceEntries.SAVINGS) * self.savings_ir
            client.book_asset(BalanceEntries.SAVINGS, interest)
            client.book_liability(BalanceEntries.EQUITY, interest)

    def book_loan(self, amount: float):
        self.book_asset(BalanceEntries.LOANS, amount)
        self.book_liability(BalanceEntries.DEPOSITS, amount)

    def process_interest(self, interest: float):
        # It is possible that interest is negative
        if self.asset(BalanceEntries.RESERVES) + interest < 0:
            self.borrow(abs(self.asset(BalanceEntries.RESERVES) + interest))

        self.book_asset(BalanceEntries.RESERVES, interest)
        self.book_liability(BalanceEntries.EQUITY, interest)

    def process_income(self):
        """Collect interest, installments and other income.
        :return True if all collections were successful."""

        if self._transactions_started and not self.__income_processed:
            for client in self.clients:
                income: float = 0.0
                debt_payment: DebtPayment = DebtPayment(self.loan_ir)

                client.pay_debt(debt_payment)
                income += debt_payment.interest_paid

                self.__client_installment += debt_payment.full_installment
                self.__client_installment_shortage += debt_payment.full_installment - debt_payment.installment_paid

                # if interest on paid installments was not fully paid, add it to the client's debt, which is subject to
                # interest.
                client.borrow(debt_payment.adjusted_interest - debt_payment.interest_paid)

                # bank costs do not decrease due to defaulted loans
                bank_costs: float = debt_payment.full_interest / self.income_from_interest - debt_payment.full_interest
                income += client.pay_bank(bank_costs)

                self.__income += income
                self.__income_shortage += debt_payment.full_interest + bank_costs - income

            # subtract expected installment proportionally from loans and mbs
            loans: float = self.asset(BalanceEntries.LOANS)
            mbs: float = self.asset(BalanceEntries.MBS)
            mbs_equity: float = self.liability(BalanceEntries.MBS_EQUITY)
            total: float = loans + mbs - mbs_equity # take market changes in MBS into account.

            self.book_asset(BalanceEntries.LOANS, -self.client_installment * loans / total)
            self.book_asset(BalanceEntries.MBS, -self.client_installment * mbs / total)
            self.book_liability(BalanceEntries.MBS_EQUITY, -self.client_installment * mbs_equity / total)

            self.book_liability(BalanceEntries.EQUITY, -self.client_installment)

            self.__income_processed = True

    def __trade_securities_with_client(self, client: PrivateActor, amount: float, security_type: str) -> float:
        client_deposits: float = client.asset(BalanceEntries.DEPOSITS)
        client_savings: float = client.asset(BalanceEntries.SAVINGS)

        client.trade_securities_with_bank(amount, security_type)

        paid_from_deposits: float = client_deposits - client.asset(BalanceEntries.DEPOSITS)
        paid_from_savings: float = client_savings - client.asset(BalanceEntries.SAVINGS)

        return paid_from_deposits + paid_from_savings

    def __trade_client_securities(self, amount: float, security_type: str):
        """Trade securities proportionally with each client, if possible."""
        total_deposits: float = self.liability(BalanceEntries.DEPOSITS) + self.liability(BalanceEntries.SAVINGS)
        traded_securities: float = 0.0

        for client in self.clients:
            client_deposits = client.asset(BalanceEntries.DEPOSITS) + client.asset(BalanceEntries.SAVINGS)
            fraction: float = client_deposits / total_deposits * amount

            traded_securities += self.__trade_securities_with_client(client, fraction, security_type)

        self.book_liability(BalanceEntries.EQUITY, -traded_securities)
        self.book_asset(security_type, traded_securities)
        self.book_liability(BalanceEntries.equity_type(security_type), traded_securities)

    def spend(self):
        # calculate real_profit
        profit: float = self.balance.delta_history[-1].asset(BalanceEntries.EQUITY)\
                        + self.balance.delta_history[-1].asset(BalanceEntries.MBS_EQUITY)
        expenses: float = 0.0

        if self.spending_mode == SpendingMode.FIXED:
            expenses = self.fixed_spending
        elif self.spending_mode == SpendingMode.PROFIT:
            expenses: float = max(0.0, profit * self.profit_spending)

            self.book_liability(BalanceEntries.EQUITY, -expenses)
            self.book_liability(BalanceEntries.DEPOSITS, expenses)
        elif self.spending_mode == SpendingMode.EQUITY:
            expenses = self.liability(BalanceEntries.EQUITY) * self.equity_spending
        elif self.spending_mode == SpendingMode.CAPITAL:
            expenses = (self.liability(BalanceEntries.EQUITY) + self.liability(BalanceEntries.MBS_EQUITY))\
                       * self.capital_spending

            if expenses > self.liability(BalanceEntries.EQUITY):
                available_deposits: float = self.liability(BalanceEntries.DEPOSITS) + self.liability(BalanceEntries.SAVINGS)
                mbs_to_sell: float = min(available_deposits, expenses - self.liability(BalanceEntries.EQUITY))

                # TODO review and implement correct sale of MBS
                for client in self.clients:
                    fraction: float = (client.asset(BalanceEntries.DEPOSITS) + client.asset(BalanceEntries.SAVINGS))\
                                      / available_deposits

                    client.pay_bank(fraction * mbs_to_sell)

                self.book_liability(BalanceEntries.DEPOSITS, -mbs_to_sell)
                self.book_asset(BalanceEntries.MBS, -mbs_to_sell)
                self.book_liability(BalanceEntries.MBS_EQUITY, -mbs_to_sell)
                self.book_liability(BalanceEntries.EQUITY, mbs_to_sell)

        if self.retain_profit:
            expenses = min(expenses, max(0.0, profit - profit * self.retain_profit_percentage))

        if self.no_loss:
            expenses = min(expenses, max(0.0, profit))

        self.book_liability(BalanceEntries.EQUITY, -expenses)
        self.book_liability(BalanceEntries.DEPOSITS, expenses)

    def borrow(self, amount: float):
        self.central_bank.book_loan(amount)
        self.book_asset(BalanceEntries.RESERVES, amount)
        self.book_liability(BalanceEntries.DEBT, amount)

        installment: float = amount/self.central_bank.loan_duration

        for i in range(self.central_bank.loan_duration):
            if len(self.__installments) < i + 1:
                self.__installments.append(installment)
            else:
                self.__installments[i] += installment

    def pay_debt(self, ir: float) -> Tuple[float, float]:
        interest: float = self.liability(BalanceEntries.DEBT) * ir
        installment: float = self.__installments.pop(0)
        total: float = interest + installment

        to_borrow: float = max(0.0, total - self.asset(BalanceEntries.RESERVES))
        self.borrow(to_borrow)
        self.book_asset(BalanceEntries.RESERVES, -installment)
        self.book_liability(BalanceEntries.DEBT, -installment)

        # interest is used to fund central bank working costs and the rest is redistributed to member states,
        # eventually resulting in deposits
        self.book_liability(BalanceEntries.EQUITY, -interest)
        self.book_liability(BalanceEntries.DEPOSITS, interest)

        return tuple((interest, installment))

    def update_reserves(self):
        """Update reserves so that they are adequate for the current amount of deposits + savings on the balance
        sheet of the bank. Loans might be converted to MBS if needed but no securities will be purchased. Instead
        extra reserves are borrowed from the central bank if needed."""

        if self._transactions_started and not self.__reserves_updated:
            total_dep_sav: float = self.liability(BalanceEntries.DEPOSITS) + self.liability(BalanceEntries.SAVINGS)
            min_composite_reserve: float =  round(total_dep_sav * self.min_reserve, 4)

            if self.risk_assets + self.balance.asset(BalanceEntries.RESERVES) < min_composite_reserve\
                    or self.risk_assets < self.__min_risk_assets * (self.safe_assets + self.risk_assets)\
                    or self.risk_assets > self.__max_risk_assets * (self.safe_assets + self.risk_assets):
                c = [0, 1, 1]  # (to maximize)

                # inequalities, number of rows equal to number of equations
                # Sequence: [RES SEC MBS]
                max_mbs: float  = self.central_bank.mbs_relative_reserve
                max_securities: float = self.central_bank.securities_relative_reserve

                a = [[1, 1, 1],
                     [1, 0, 0],
                     [-max_mbs, -max_mbs, 1 - max_mbs],
                     [-max_securities, 1 - max_securities, -max_securities]]
                b = [self.min_reserve * total_dep_sav, total_dep_sav, 0, 0]

                # # add slack variables by hand
                a[0] += [0,0,0]
                a[1] += [1,0,0]
                a[2] += [0,1,0]
                a[3] += [0,0,1]
                c += [0,0,0,0]

                t, s, v = simplex(c, a, b)

                target_reserve: float = s[0][1]
                target_securities: float = s[1][1]
                target_mbs: float = s[2][1]

                if target_mbs > self.asset(BalanceEntries.MBS):
                    new_mbs: float = target_mbs - self.asset(BalanceEntries.MBS)

                    if self.asset(BalanceEntries.LOANS) < new_mbs:
                        target_reserve += new_mbs - self.asset(BalanceEntries.LOANS)
                        new_mbs = self.asset(BalanceEntries.LOANS)

                    self.book_asset(BalanceEntries.LOANS, -new_mbs)
                    self.book_asset(BalanceEntries.MBS, new_mbs)
                    self.book_liability(BalanceEntries.EQUITY, -new_mbs)
                    self.book_liability(BalanceEntries.MBS_EQUITY, new_mbs)

                if target_securities > self.asset(BalanceEntries.SECURITIES):
                    target_reserve += target_securities - self.asset(BalanceEntries.SECURITIES)

                if self.asset(BalanceEntries.RESERVES) < target_reserve:
                    self.borrow(target_reserve - self.asset(BalanceEntries.RESERVES))

                # Update MBS
                # if delta_mbs > self.asset(BalanceEntries.LOANS):
                #     delta_res += delta_mbs - self.asset(BalanceEntries.LOANS)
                #     delta_mbs = self.asset(BalanceEntries.LOANS)
                #
                # self.book_asset(BalanceEntries.MBS, delta_mbs)
                # self.book_asset(BalanceEntries.LOANS, -delta_mbs)
                # self.book_liability(BalanceEntries.MBS_EQUITY, delta_mbs)
                # self.book_liability(BalanceEntries.EQUITY, -delta_mbs)
                #
                # self.__trade_client_securities(delta_sec, BalanceEntries.SECURITIES)
                #
                # # Update reserves
                # self.borrow(delta_res)

            self.__reserves_updated = True

    def update_risk_assets(self):
        pass

    def trade_central_bank_securities(self, amount: float) -> float:
        """Trade securities with the central bank. A positive amount indicates a sell to the central bank.
        Returns the actual number of securities traded."""

        traded_securities: float = min(amount, self.asset(BalanceEntries.SECURITIES))

        self.book_asset(BalanceEntries.SECURITIES, -traded_securities)
        self.book_asset(BalanceEntries.RESERVES, traded_securities)

        return traded_securities

    def receive_client_securities(self, amount: float, security_type: str):
        """Changes the balance sheet of the bank in accordance to the traded securities.

        :param amount the value of the securities that needs to be booked. This can be a negative value if securities
        were sold to the client.
        :param security_type the type of security that needs to be booked. Either MBS or SECURITIES."""
        self.book_asset(security_type, amount)
        self.book_liability(BalanceEntries.equity_type(security_type), amount)

    def clear(self):
        super().clear()
        self.__installments = [0.0]

        for client in self.clients:
            client.clear()