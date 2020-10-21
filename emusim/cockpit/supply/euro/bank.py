from __future__ import annotations

from decimal import *

from emusim.cockpit.utilities.simplex import simplex
from emusim.cockpit.utilities.cycles import Interval, Period
from enum import Enum
from typing import TYPE_CHECKING, Tuple, List

from ordered_set import OrderedSet

from . import EconomicActor, BalanceEntries

if TYPE_CHECKING:
    from . import CentralBank, PrivateActor


class SpendingMode(Enum):
    FIXED = 0
    PROFIT = 1
    EQUITY = 2
    CAPITAL = 3


class DebtPayment():

    def __init__(self, interest_rate: Decimal):
        self.__interest_rate: Decimal = Decimal(interest_rate)
        self.__debt: Decimal = Decimal(0.0)
        self.__adjusted_debt: Decimal = Decimal(0.0)
        self.__full_installment: Decimal = Decimal(0.0)
        self.__full_interest: Decimal = Decimal(0.0)
        self.__adjusted_interest: Decimal = Decimal(0.0)
        self.__installment_paid: Decimal = Decimal(0.0)
        self.__interest_paid: Decimal = Decimal(0.0)

    @property
    def debt(self) -> Decimal:
        return self.__debt

    @debt.setter
    def debt(self, amount: Decimal):
        self.__debt = Decimal(amount)
        self.__adjusted_debt = self.debt
        self.__full_interest = self.debt * self.__interest_rate
        self.__adjusted_interest = self.full_interest

    @property
    def adjusted_debt(self) -> Decimal:
        return self.__adjusted_debt

    @property
    def full_installment(self) -> Decimal:
        return self.__full_installment

    @full_installment.setter
    def full_installment(self, amount: Decimal):
        self.__full_installment = Decimal(amount)

    @property
    def full_interest(self) -> Decimal:
        return self.__full_interest

    @property
    def adjusted_interest(self) -> Decimal:
        return self.__adjusted_interest

    @property
    def installment_paid(self) -> Decimal:
        return self.__installment_paid

    @installment_paid.setter
    def installment_paid(self, paid: Decimal):
        self.__installment_paid = Decimal(paid)

        # No interest is charged on unpaid installments. In the context of the simulation, additional unpaid
        # installments are treated as surplus systemic defaults and thus the adjusted debt, installment and interest
        # might need to be updated.
        self.__adjusted_debt -= self.full_installment - paid
        self.__adjusted_interest = Decimal(self.__adjusted_debt * self.__interest_rate)

    @property
    def interest_paid(self) -> Decimal:
        return self.__interest_paid

    @interest_paid.setter
    def interest_paid(self, paid: Decimal):
        self.__interest_paid = Decimal(paid)


class Bank(EconomicActor):

    def __init__(self, central_bank: CentralBank):
        super().__init__(
            OrderedSet([BalanceEntries.RESERVES, BalanceEntries.LOANS, BalanceEntries.MBS, BalanceEntries.SECURITIES]),
            OrderedSet([BalanceEntries.DEPOSITS, BalanceEntries.SAVINGS, BalanceEntries.DEBT, BalanceEntries.EQUITY,
                        BalanceEntries.MBS_EQUITY]))
        self.__central_bank: CentralBank = central_bank
        self.central_bank.bank = self
        self.__installments: List[Decimal] = [Decimal(0.0)]

        self.reserves_interval: Period = Period(1, Interval.MONTH) # Interval when reserves are updated
        self.__min_reserve: Decimal = central_bank.min_reserve

        self.risk_assets_interval: Period = Period(1, Interval.MONTH)
        self.__min_risk_assets: Decimal = Decimal(0.0)
        self.__max_risk_assets: Decimal = Decimal(1.0) # Maximum % of assets being MBS and/or Securities

        # The sum of the two following parameters must always be >= 1.0
        self.__max_mbs_assets: Decimal = Decimal(1.0) # Max % of risk assets
        self.__max_security_assets: Decimal = Decimal(1.0) # Max % of risk assets

        self.client_interaction_interval: Period = Period(1, Interval.MONTH)

        self.__savings_ir: Decimal = Decimal(0.02)
        self.__loan_ir: Decimal = Decimal(0.025)
        self.loan_duration: Period = Period(20, Interval.YEAR)

        self.no_loss: bool = True
        self.__income_from_interest: Decimal = Decimal(0.8)
        self.retain_profit: bool = True
        self.__retain_profit_percentage: Decimal = Decimal(0.2)

        self.spending_mode: SpendingMode = SpendingMode.PROFIT
        self.__fixed_spending: Decimal = Decimal(0.0)
        self.__profit_spending: Decimal = Decimal(0.8)
        self.__equity_spending: Decimal = Decimal(0.0)
        self.__capital_spending: Decimal = Decimal(0.0)

        # Cycle flags. Some actions can only be executed once per cycle.
        self.__risk_assets_updated: bool = False
        self.__income_and_spending_processed: bool = False
        self.__savings_processed: bool = False
        self.__debt_paid: bool = False
        self.__reserves_updated: bool = False

        # Cycle attributes
        self.__installment = Decimal(0.0)
        self.__client_installment: Decimal = Decimal(0.0)
        self.__client_installment_shortage: Decimal = Decimal(0.0)
        self.__expected_income: Decimal = Decimal(0.0)
        self.__income: Decimal = Decimal(0.0)
        self.__costs: Decimal = Decimal(0.0)

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def min_reserve(self) -> Decimal:
        return self.__min_reserve

    @min_reserve.setter
    def min_reserve(self, percentage: Decimal):
        self.__min_reserve = Decimal(max(self.central_bank.min_reserve, percentage))

    @property
    def savings_ir(self) -> Decimal:
        return self.__savings_ir

    @savings_ir.setter
    def savings_ir(self, ir: Decimal):
        self.__savings_ir = Decimal(ir)

    @property
    def loan_ir(self) -> Decimal:
        return self.__loan_ir

    @loan_ir.setter
    def loan_ir(self, ir: Decimal):
        self.__loan_ir = Decimal(ir)

    @property
    def income_from_interest(self) -> Decimal:
        return self.__income_from_interest

    @income_from_interest.setter
    def income_from_interest(self, percentage: Decimal):
        self.__income_from_interest = Decimal(percentage)

    @property
    def retain_profit_percentage(self) -> Decimal:
        return self.__retain_profit_percentage

    @retain_profit_percentage.setter
    def retain_profit_percentage(self, percentage: Decimal):
        self.__retain_profit_percentage = Decimal(percentage)

    @property
    def fixed_spending(self) -> Decimal:
        return self.__fixed_spending

    @fixed_spending.setter
    def fixed_spending(self, amount: Decimal):
        self.__fixed_spending = Decimal(amount)

    @property
    def profit_spending(self) -> Decimal:
        return self.__profit_spending

    @profit_spending.setter
    def profit_spending(self, amount: Decimal):
        self.__profit_spending = Decimal(amount)

    @property
    def capital_spending(self) -> Decimal:
        return self.__capital_spending

    @capital_spending.setter
    def capital_spending(self, amount: Decimal):
        self.__capital_spending = Decimal(amount)

    @property
    def equity_spending(self) -> Decimal:
        return self.__equity_spending

    @equity_spending.setter
    def equity_spending(self, amount: Decimal):
        self.__equity_spending = Decimal(amount)

    @property
    def client(self) -> PrivateActor:
        return self.__client

    @client.setter
    def client(self, client: PrivateActor):
        self.__client: PrivateActor = client

    @property
    def loan_installments(self) -> int:
        return int(self.loan_duration.days / self.client_interaction_interval.days)

    @property
    def installment(self) -> Decimal:
        return self.__installment

    @property
    def client_installment(self) -> Decimal:
        return self.__client_installment

    @property
    def client_installment_shortage(self) -> Decimal:
        return self.__client_installment_shortage

    @property
    def income(self) -> Decimal:
        return self.__income

    @property
    def costs(self) -> Decimal:
        return self.__costs

    @property
    def income_shortage(self) -> Decimal:
        return self.__expected_income - self.income

    @property
    def profit(self) -> Decimal:
        """Return the profit for this cycle."""

        return self.income - self.costs

    @property
    def client_liabilities(self) -> Decimal:
        return self.liability(BalanceEntries.DEPOSITS) + self.liability(BalanceEntries.SAVINGS)

    @property
    def total_equity(self) -> Decimal:
        return self.liability(BalanceEntries.EQUITY) + self.liability(BalanceEntries.MBS_EQUITY)

    @property
    def safe_assets(self) -> Decimal:
        return self.asset(BalanceEntries.RESERVES) + self.asset(BalanceEntries.LOANS)

    @property
    def risk_assets(self) -> Decimal:
        return self.asset(BalanceEntries.MBS) + self.asset(BalanceEntries.SECURITIES)

    @property
    def min_risk_assets(self) -> Decimal:
        return self.__min_risk_assets

    @min_risk_assets.setter
    def min_risk_assets(self, min_percentage: Decimal):
        min_percentage = Decimal(min_percentage)

        self.__min_risk_assets = min_percentage

        if self.max_risk_assets < min_percentage:
            self.max_risk_assets = min_percentage

    @property
    def max_risk_assets(self) -> Decimal:
        return self.__max_risk_assets

    @max_risk_assets.setter
    def max_risk_assets(self, max_percentage: Decimal):
        max_percentage = Decimal(max_percentage)

        self.__max_risk_assets = max_percentage

        if self.min_risk_assets > max_percentage:
            self.min_risk_assets = max_percentage

    @property
    def max_mbs_assets(self):
        return self.__max_mbs_assets

    @max_mbs_assets.setter
    def max_mbs_assets(self, max_percentage: Decimal):
        max_percentage = Decimal(max_percentage)

        self.__max_mbs_assets = max_percentage

        if self.max_security_assets < 1 - max_percentage:
            self.max_security_assets = 1 - max_percentage

    @property
    def max_security_assets(self):
        return self.__max_security_assets

    @max_security_assets.setter
    def max_security_assets(self, max_percentage):
        max_percentage = Decimal(max_percentage)

        self.__max_security_assets = max_percentage

        if self.max_mbs_assets < 1 - max_percentage:
            self.max_mbs_assets = 1 - max_percentage

    @property
    def lcr(self) -> Decimal:
        """Return the Liquidity Coverage Ratio of the bank. Must be called before transactions are started or after
        transactions are ended. Results during transactions are not accurate."""
        return Decimal(1.0) # TODO

    def start_transactions(self):
        super().start_transactions()
        self.__client_installment: Decimal = Decimal(0.0)
        self.__client_installment_shortage: Decimal = Decimal(0.0)
        self.__expected_income = Decimal(0.0)
        self.__income: Decimal = Decimal(0.0)
        self.__costs: Decimal = Decimal(0.0)

        self.__risk_assets_updated = False
        self.__income_and_spending_processed = False
        self.__savings_processed = False
        self.__debt_paid = False
        self.__reserves_updated = False

        self.client.start_transactions()

    def end_transactions(self) -> bool:
        return super().end_transactions() and self.client.end_transactions()

    def inflate(self, inflation: Decimal):
        inflation = Decimal(inflation)

        self.fixed_spending += self.fixed_spending * inflation

        self.client.inflate(inflation)

    def grow_mbs(self, growth: Decimal):
        super().grow_mbs(growth)

        self.client.grow_mbs(growth)

    def grow_securities(self, growth: Decimal):
        super().grow_securities(growth)

        self.client.grow_securities(growth)

    def book_savings(self, amount: Decimal):
        """Transfer deposits to savings. This should only be called by the client."""
        self.book_liability(BalanceEntries.SAVINGS, amount)
        self.book_liability(BalanceEntries.DEPOSITS, -amount)

    def pay_bank(self, amount: Decimal, source: str):
        """Pay the bank an amount of money. Must only be called by clients of the bank.

        :param: amount paid to the bank.
        :param source: indicate whether it comes from DEPOSITS or SAVINGS."""

        self.book_liability(source, -amount)
        self.book_liability(BalanceEntries.EQUITY, amount)

    def process_client_savings(self):
        """Pay interest on client savings."""

        if self._transactions_started\
            and not self.__savings_processed\
            and self.client_interaction_interval.period_complete(self.cycle):

            interest_rate: Decimal = self.savings_ir * self.client_interaction_interval.days / Period.YEAR_DAYS

            self.client.process_savings()

            interest: Decimal = Decimal(self.liability(BalanceEntries.SAVINGS) * interest_rate)
            self.book_liability(BalanceEntries.SAVINGS, interest)
            self.book_liability(BalanceEntries.EQUITY, -interest)
            self.client.book_asset(BalanceEntries.SAVINGS, interest)
            self.client.book_liability(BalanceEntries.EQUITY, interest)

            self.__costs += interest
            self.__savings_processed = True

    def book_loan(self, amount: Decimal):
        self.book_asset(BalanceEntries.LOANS, amount)
        self.book_liability(BalanceEntries.DEPOSITS, amount)

    def process_interest(self, interest: Decimal):
        # It is possible that interest is negative
        if self.asset(BalanceEntries.RESERVES) + interest < 0.0:
            self.borrow(abs(self.asset(BalanceEntries.RESERVES) + interest))

        self.book_asset(BalanceEntries.RESERVES, interest)
        self.book_liability(BalanceEntries.EQUITY, interest)

        if interest > 0.0:
            self.__income += interest
        else:
            self.__costs -= interest

    def distribute_interest(self, interest: Decimal):
        """Distribute interest from central bank to clients"""

        self.book_asset(BalanceEntries.RESERVES, interest)
        self.book_liability(BalanceEntries.DEPOSITS, interest)

        self.client.book_asset(BalanceEntries.DEPOSITS, interest)
        self.client.book_liability(BalanceEntries.EQUITY, interest)

    def process_income_and_spending(self):
        """Collect interest, installments and other income. Spend net expenses."""

        if self._transactions_started\
                and not self.__income_and_spending_processed\
                and self.client_interaction_interval.period_complete(self.cycle):

            debt_payment: DebtPayment = DebtPayment(Decimal(self.loan_ir * self.client_interaction_interval.days
                                                            / Period.YEAR_DAYS))

            self.client.pay_debt(debt_payment)
            self.__expected_income = debt_payment.full_interest / self.income_from_interest

            self.__income = debt_payment.interest_paid
            self.__book_installment(debt_payment)

            # if interest on paid installments was not fully paid, add it to the client's debt, which is subject to
            # interest.
            self.client.borrow(debt_payment.adjusted_interest - debt_payment.interest_paid)

            # bank costs do not decrease due to defaulted loans
            bank_costs: Decimal = self.__expected_income - debt_payment.full_interest
            profit: Decimal = self.income + bank_costs - self.__costs
            bank_spending: Decimal = Decimal(0.0)

            # calculate spending
            if self.spending_mode == SpendingMode.FIXED:
                bank_spending = self.fixed_spending
            elif self.spending_mode == SpendingMode.PROFIT:
                bank_spending = Decimal(max(Decimal(0.0), profit * self.profit_spending))
            elif self.spending_mode == SpendingMode.EQUITY:
                bank_spending = self.liability(BalanceEntries.EQUITY) * self.equity_spending
            elif self.spending_mode == SpendingMode.CAPITAL:
                bank_spending = (self.liability(BalanceEntries.EQUITY) + self.liability(BalanceEntries.MBS_EQUITY))\
                           * self.capital_spending

                if bank_spending > self.liability(BalanceEntries.EQUITY):
                    available_deposits: Decimal = self.liability(BalanceEntries.DEPOSITS) + self.liability(BalanceEntries.SAVINGS)
                    mbs_to_sell: Decimal = min(available_deposits, bank_spending - self.liability(BalanceEntries.EQUITY))

                    # TODO review and implement correct sale of MBS
                    self.client.pay_bank(mbs_to_sell)

                    self.book_liability(BalanceEntries.DEPOSITS, -mbs_to_sell)
                    self.book_asset(BalanceEntries.MBS, -mbs_to_sell)
                    self.book_liability(BalanceEntries.MBS_EQUITY, -mbs_to_sell)
                    self.book_liability(BalanceEntries.EQUITY, mbs_to_sell)

            if self.retain_profit:
                bank_spending = min(bank_spending, max(Decimal(0.0), profit - profit * self.retain_profit_percentage))

            if self.no_loss and profit - bank_spending < 0:
                bank_spending = min(bank_spending, profit)

            self.__costs += bank_spending

            # Calculate net spending. Bank costs are not collected if they are spent again immediately after.
            bank_spending -= bank_costs

            # Only collect when bank spending is negative. Add bank costs.
            self.__income += self.client.pay_bank(max(Decimal(0.0), -bank_spending)) + bank_costs

            self.book_liability(BalanceEntries.DEPOSITS, bank_spending)
            self.client.book_asset(BalanceEntries.DEPOSITS, bank_spending)
            self.book_liability(BalanceEntries.EQUITY, -bank_spending)
            self.client.book_liability(BalanceEntries.EQUITY, bank_spending)

            self.__income_and_spending_processed = True

    def __book_installment(self, debt_payment: DebtPayment):
            self.__client_installment = debt_payment.installment_paid
            self.__client_installment_shortage = debt_payment.full_installment - debt_payment.installment_paid

            # subtract expected installment proportionally from loans and mbs
            loans: Decimal = self.asset(BalanceEntries.LOANS)
            mbs: Decimal = self.asset(BalanceEntries.MBS)
            mbs_equity: Decimal = self.liability(BalanceEntries.MBS_EQUITY)
            total: Decimal = loans + mbs - mbs_equity # take market changes in MBS into account.

            self.book_asset(BalanceEntries.LOANS, -self.client_installment * loans / total)
            self.book_asset(BalanceEntries.MBS, -self.client_installment * mbs / total)
            self.book_liability(BalanceEntries.MBS_EQUITY, -self.client_installment * mbs_equity / total)

            self.book_liability(BalanceEntries.EQUITY, -self.client_installment)

    def __trade_client_securities(self, amount: Decimal, security_type: str) -> Decimal:
        """Trade securities proportionally with each client, if possible.
        A positive amount indicates a buy, a negative amount indicates a sell."""

        if security_type == BalanceEntries.SECURITIES and amount < 0:
            amount = -min(-amount, self.asset(BalanceEntries.SECURITIES))

        return self.client.trade_securities_with_bank(amount, security_type)

    def borrow(self, amount: Decimal):
        self.central_bank.book_loan(amount)
        self.book_asset(BalanceEntries.RESERVES, amount)
        self.book_liability(BalanceEntries.DEBT, amount)

        installment: Decimal = amount / self.__central_bank.loan_installments

        for i in range(self.__central_bank.loan_installments):
            if len(self.__installments) < i + 1:
                self.__installments.append(installment)
            else:
                self.__installments[i] += installment

    def pay_debt(self, ir: Decimal) -> Tuple[Decimal, Decimal]:
        interest: Decimal = self.liability(BalanceEntries.DEBT) * ir
        self.__installment = self.__installments.pop(0)
        total: Decimal = interest + self.installment

        to_borrow: Decimal = max(Decimal(0.0), total - self.asset(BalanceEntries.RESERVES))
        self.borrow(to_borrow)
        self.book_asset(BalanceEntries.RESERVES, -total)
        self.book_liability(BalanceEntries.DEBT, -self.installment)
        self.book_liability(BalanceEntries.EQUITY, -interest)

        return tuple((self.installment, interest))

    def update_reserves(self, force_update: bool = False):
        """Update reserves so that they are adequate for the current amount of deposits + savings on the balance
        sheet of the bank. Loans might be converted to MBS if needed but no securities will be purchased. Instead
        extra reserves are borrowed from the central bank if needed."""

        if force_update or (not self.__reserves_updated and self.reserves_interval.period_complete(self.cycle)):
            min_composite_reserve: Decimal =  self.client_liabilities * self.min_reserve

            target_mbs: Decimal = self.central_bank.mbs_relative_reserve * min_composite_reserve
            target_securities: Decimal = self.central_bank.securities_relative_reserve * min_composite_reserve
            target_reserve: Decimal = min_composite_reserve - target_mbs - target_securities

            cur_reserve: Decimal = self.asset(BalanceEntries.RESERVES)
            cur_mbs = min(target_mbs, self.asset(BalanceEntries.MBS))
            cur_securities = min(target_securities, self.asset(BalanceEntries.SECURITIES))

            if cur_reserve + cur_mbs + cur_securities < min_composite_reserve:
                if target_mbs > self.asset(BalanceEntries.MBS):
                    new_mbs: Decimal = target_mbs - self.asset(BalanceEntries.MBS)

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

            self.__reserves_updated = True

    def update_risk_assets(self, force_update: bool = False):
        # Update risk assets in the same cycles as reserves are updated
        if not self.__risk_assets_updated\
            and self.min_risk_assets > 0.0\
                and (self.risk_assets_interval.period_complete(self.cycle) or force_update):
            if self.max_mbs_assets == 0.0 or self.max_security_assets == 0.0:
                risk_asset: str = BalanceEntries.MBS if self.max_security_assets == 0.0 else BalanceEntries.SECURITIES
                target_risk: Decimal = self.max_risk_assets * self.safe_assets / (1 - self.max_risk_assets)
                new_risk: Decimal = target_risk - self.risk_assets
                self.__trade_client_securities(new_risk, risk_asset)

                if risk_asset == BalanceEntries.MBS and self.asset(BalanceEntries.MBS) < target_risk:
                    c = [1, 0]  # (to maximize)

                    # inequalities, number of rows equal to number of equations
                    # Sequence: [MBS LOAN]

                    # Equations (non normalized):
                    # [0] MBS >= min_risk_assets * total_assets
                    # [1] MBS  <= max_risk_assets * total assets
                    # [2] MBS + LOAN = current_MBS + current_LOAN
                    a = [[1 - self.min_risk_assets, -self.min_risk_assets],
                         [1 - self.max_risk_assets, -self.max_risk_assets],
                         [1, 1]]
                    b = [self.min_risk_assets * self.asset(BalanceEntries.RESERVES),
                         self.max_risk_assets * self.asset(BalanceEntries.RESERVES),
                         self.asset(BalanceEntries.MBS) + self.asset(BalanceEntries.LOANS)]

                    # # add slack variables by hand
                    a[0] += [-1, 0]
                    a[1] += [0, 1]
                    a[2] += [0, 0]

                    c += [0, 0]

                    t, s, v = simplex(c, a, b)

                    new_mbs: Decimal = round(s[0][1], 8) - self.asset(BalanceEntries.MBS)

                    self.book_asset(BalanceEntries.MBS, new_mbs)
                    self.book_asset(BalanceEntries.LOANS, -new_mbs)
            else:
                cur_loans: Decimal = self.asset(BalanceEntries.LOANS)
                cur_mbs: Decimal = self.asset(BalanceEntries.MBS)
                c = [1, 1, 0]  # (to maximize)

                # inequalities, number of rows equal to number of equations
                # Sequence: [MBS SEC LOANS]

                # Equations (non normalized):
                # [0] MBS + SEC >= min_risk_assets * total_assets
                # [1] MBS + SEC <= max_risk_assets * total assets
                # [2] MBS <= max_mbs * risk_assets
                # [3] SEC <= max_sec * risk_assets
                # [4] MBS + LOANS == cur_MBS + cur_LOANS
                a = [[1 - self.min_risk_assets, 1 - self.min_risk_assets, -self.min_risk_assets],
                     [1 - self.max_risk_assets, 1 - self.max_risk_assets, -self.max_risk_assets],
                     [1 - self.max_mbs_assets, -self.max_mbs_assets, 0],
                     [-self.max_security_assets, 1 - self.max_security_assets, 0],
                     [1, 0, 1]]
                b = [self.min_risk_assets * self.asset(BalanceEntries.RESERVES),
                     self.max_risk_assets * self.asset(BalanceEntries.RESERVES),
                     0,
                     0,
                     cur_mbs + cur_loans]

                # # add slack variables by hand
                a[0] += [-1, 0, 0, 0]
                a[1] += [0, 1, 0, 0]
                a[2] += [0, 0, 1, 0]
                a[3] += [0, 0, 0, 1]
                a[4] += [0, 0, 0, 0]

                c += [0, 0, 0, 0]

                t, s, v = simplex(c, a, b)

                new_mbs: Decimal = s[0][1] - self.asset(BalanceEntries.MBS)
                new_securities: Decimal = s[1][1] - self.asset(BalanceEntries.SECURITIES)

                self.__trade_client_securities(new_securities, BalanceEntries.SECURITIES)
                self.book_asset(BalanceEntries.MBS, new_mbs)
                self.book_asset(BalanceEntries.LOANS, -new_mbs)

            self.__risk_assets_updated = True

    def trade_central_bank_securities(self, amount: Decimal) -> Decimal:
        """Trade securities with the central bank. A positive amount indicates a sell to the central bank.
        Returns the actual number of securities traded."""

        traded_securities: Decimal = min(amount, self.asset(BalanceEntries.SECURITIES))

        self.book_asset(BalanceEntries.SECURITIES, -traded_securities)
        self.book_asset(BalanceEntries.RESERVES, traded_securities)

        return traded_securities

    def exchange_client_securities(self, amount: Decimal, security_type: str) -> Decimal:
        """Changes the balance sheet of the bank in accordance to the traded securities.

        :param amount the value of the securities that needs to be booked. This can be a negative value if securities
        are sold to the client. In case of a sell, a check is made whether the adequate amount of securties is
        available.
        :param security_type the type of security that needs to be booked. Either MBS or SECURITIES.

        :return the actual value of the securities that were exchanged."""

        if amount < 0 and security_type == BalanceEntries.SECURITIES:
            amount = -min(-amount, self.asset(BalanceEntries.SECURITIES))

        self.book_asset(security_type, amount)
        self.book_liability(BalanceEntries.equity_type(security_type), amount)

        return amount

    def clear(self):
        super().clear()
        self.__installments = [Decimal(0.0)]

        self.client.clear()