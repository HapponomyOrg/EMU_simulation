from decimal import *

from emusim.cockpit.supply.euro import CentralBank, QEMode, HelicopterMode, Bank, SpendingMode, PrivateActor
from emusim.cockpit.supply.euro.balance_entries import BalanceEntries
from emusim.cockpit.utilities.cycles import Period, Interval

central_bank: CentralBank = CentralBank()
bank: Bank = Bank(central_bank)
client: PrivateActor = PrivateActor(bank)


def init_parameters():
    central_bank.clear()

    central_bank.min_reserve = 0.04
    central_bank.mbs_relative_reserve = 0.0
    central_bank.securities_relative_reserve = 0.0

    # set interest rates per day
    central_bank.reserve_ir = 0.0 * Period.YEAR_DAYS
    central_bank.surplus_reserve_ir = -0.005 * Period.YEAR_DAYS
    central_bank.loan_ir = 0.01 * Period.YEAR_DAYS
    central_bank.loan_duration = Period(1, Interval.DAY)
    central_bank.loan_interval = Period(1, Interval.DAY)

    central_bank.qe_mode = QEMode.NONE
    central_bank.qe_fixed = 0.0
    central_bank.qe_debt_related = 0.0
    central_bank.helicopter_mode = HelicopterMode.NONE
    central_bank.helicopter_fixed = 0.0
    central_bank.helicopter_debt_related = 0.0

    bank.max_reserve = 0.04
    bank.min_liquidity = 0.05
    bank.savings_ir = 0.02 * Period.YEAR_DAYS
    bank.loan_ir = 0.025 * Period.YEAR_DAYS
    bank.loan_duration = Period(20, Interval.YEAR)
    bank.loan_interval = Period(1, Interval.DAY)
    bank.no_loss = True
    bank.income_from_interest = 0.8
    bank.retain_profit = True
    bank.retain_profit_percentage = 0.2
    bank.spending_mode = SpendingMode.PROFIT
    bank.fixed_spending = 0.0
    bank.profit_spending = 0.8
    bank.equity_spending = 0.0
    bank.capital_spending = 0.0

    client.savings_rate = 0.02
    client.defaulting_rate = 0.0


def test_creation():
    init_parameters()

    central_bank.book_asset("NO_ENTRY", Decimal(100.0))
    assert round(central_bank.asset("NO_ENTRY"), 8) == round(Decimal(0.0), 8)

    central_bank.start_transactions()
    assert central_bank.end_transactions()


def test_borrowing():
    init_parameters()

    central_bank.start_transactions()
    bank.borrow(Decimal(100.0))
    assert round(central_bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(100.0), 8)
    assert round(central_bank.liability(BalanceEntries.RESERVES), 8) == round(Decimal(100.0), 8)
    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(100.0), 8)
    assert round(bank.liability(BalanceEntries.DEBT), 8) == round(Decimal(100.0), 8)

    client.borrow(Decimal(1000.0))
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1000.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(1000.0), 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(1000.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(1000.0), 8)

    assert central_bank.end_transactions()


def test_interest():
    init_parameters()

    central_bank.start_transactions()
    bank.borrow(Decimal(100.0))
    assert round(central_bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(100.0), 8)
    assert round(central_bank.liability(BalanceEntries.RESERVES), 8) == round(Decimal(100.0), 8)
    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(100.0), 8)
    assert round(bank.liability(BalanceEntries.DEBT), 8) == round(Decimal(100.0), 8)

    client.borrow(Decimal(1000.0))
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1000.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(1000.0), 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(1000.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(1000.0), 8)

    central_bank.process_reserve_interests()

    assert central_bank.end_transactions()

    assert round(central_bank.asset(BalanceEntries.INTEREST), 8) == round(Decimal(0.0), 8)
    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(100.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 1) == round(Decimal(1000.3), 1)
    assert round(client.asset(BalanceEntries.DEPOSITS), 1) == round(Decimal(1000.3), 1)
    assert round(client.liability(BalanceEntries.EQUITY), 1) == round(Decimal(0.3), 1)


def test_inflation():
    init_parameters()
    central_bank.qe_fixed = 1.0
    central_bank.helicopter_fixed = 1.0
    bank.fixed_spending = 1.0

    central_bank.inflate(Decimal(0.1))

    assert round(central_bank.qe_fixed, 8) == round(Decimal(1.1), 8)
    assert round(central_bank.helicopter_fixed, 8) == round(Decimal(1.1), 8)
    assert round(bank.fixed_spending, 8) == round(Decimal(1.1), 8)


def test_fixed_qe():
    init_parameters()
    central_bank.qe_mode = QEMode.FIXED
    central_bank.qe_fixed = 100.0
    central_bank.qe_interval = Period(1, Interval.DAY)

    central_bank.start_transactions()
    client.trade_securities_with_bank(Decimal(10.0))
    assert round(client.balance.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(10.0), 8)
    assert round(client.balance.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(0.0), 8)
    assert round(client.balance.liability(BalanceEntries.EQUITY), 8) == round(Decimal(10.0), 8)
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(50.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(50.0))
    central_bank.process_qe()
    central_bank.end_transactions()

    assert round(central_bank.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(100.0), 8)
    assert round(central_bank.liability(BalanceEntries.RESERVES), 8) == round(Decimal(100.0), 8)
    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(100.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(50.0), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(50.0), 8)


def test_debt_related_qe():
    init_parameters()
    central_bank.qe_mode = QEMode.DEBT_RELATED
    central_bank.qe_debt_related = 0.01

    central_bank.start_transactions()
    client.borrow(Decimal(100.0))
    # TODO
