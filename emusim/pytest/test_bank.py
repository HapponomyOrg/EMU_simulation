from decimal import *

from emusim.cockpit.supply.euro import CentralBank, Bank, SpendingMode, PrivateActor, DefaultingMode
from emusim.cockpit.supply.euro.balance_entries import BalanceEntries
from emusim.cockpit.utilities.cycles import Period, Interval

central_bank: CentralBank = CentralBank()
bank: Bank = Bank(central_bank)
client: PrivateActor = PrivateActor(bank)


def test_pay_savings_interest():
    central_bank.clear()

    # Set interest rate per day
    bank.savings_ir = Decimal(0.1) * Period.YEAR_DAYS
    bank.client_interaction_interval = Period(1, Interval.DAY)

    client.savings_rate = Decimal(0.1)

    central_bank.start_transactions()
    client.borrow(Decimal(1000.0))
    bank.process_client_savings()
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(900.0), 8)
    assert round(client.asset(BalanceEntries.SAVINGS), 8) == round(Decimal(110.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(1000.0), 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(10.0), 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(1010.0), 8)

    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1000.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(900.0), 8)
    assert round(bank.liability(BalanceEntries.SAVINGS), 8) == round(Decimal(110.0), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(-10.0), 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(1000.0), 8)


def test_income_and_spending():
    central_bank.clear()

    bank.loan_ir = Decimal(0.1 * Period.YEAR_DAYS)
    bank.loan_duration = Period(10, Interval.DAY)
    bank.client_interaction_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.5)
    bank.spending_mode = SpendingMode.PROFIT
    bank.profit_spending = 0.8

    bank.savings_ir = Decimal(0.01) * Period.YEAR_DAYS
    bank.client_interaction_interval = Period(1, Interval.DAY)

    client.defaulting_mode = DefaultingMode.NONE
    client.savings_rate = Decimal(0.1)

    client.borrow(Decimal(100000.0))

    central_bank.start_transactions()
    bank.process_client_savings()
    assert round(client.asset(BalanceEntries.SAVINGS), 8) == round(Decimal(10100.0), 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(90000.0), 8)

    bank.process_income_and_spending()
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(90000.0), 8)
    assert round(client.asset(BalanceEntries.SAVINGS), 8) == round(Decimal(10100.0), 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(75920.0), 8)

    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == bank.liability(BalanceEntries.DEPOSITS)
    assert client.asset(BalanceEntries.SAVINGS) == bank.liability(BalanceEntries.SAVINGS)
    assert client.liability(BalanceEntries.DEBT) == bank.asset(BalanceEntries.LOANS)
    assert round(bank.income, 8) == round(Decimal(20000), 8)
    assert round(bank.costs, 8) == round(Decimal(16020), 8)
    assert round(bank.income_shortage, 8) == round(Decimal(0.0), 8)
    assert round(bank.profit, 8) == round(Decimal(3980.0), 8)


def test_full_income():
    central_bank.clear()

    bank.loan_ir = Decimal(0.05 * Period.YEAR_DAYS)
    bank.loan_duration = Period(10, Interval.DAY)
    bank.client_interaction_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.NONE

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.process_income_and_spending()
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(1775.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(1800.0), 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(-25.0), 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(1775.0), 8)

    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1800.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(1775.0), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(25.0), 8)


def test_income_defaulting():
    central_bank.clear()
    bank.loan_ir = Decimal(0.05 * Period.YEAR_DAYS)
    bank.loan_duration = Period(10, Interval.DAY)
    bank.client_interaction_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = Decimal(0.25)
    client.defaults_bought_by_debt_collectors = Decimal(1.0)

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.process_income_and_spending()
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(1727.5), 8)
    assert round(client.asset(BalanceEntries.UNRESOLVED_DEBT), 8) == round(Decimal(50.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(1800.0), 8)
    assert round(client.liability(BalanceEntries.UNRESOLVED_DEBT), 8) == round(Decimal(50.0), 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(-72.5), 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(1777.5), 8)

    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1800.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(1727.5), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(72.5), 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(1800.0), 8)


def test_reserves_no_securities():
    central_bank.clear()
    central_bank.min_reserve = Decimal(0.05)
    central_bank.mbs_relative_reserve = Decimal(0.0)
    central_bank.securities_relative_reserve = Decimal(0.0)
    bank.min_reserve = Decimal(0.05)
    bank.loan_ir = Decimal(0.05 * Period.YEAR_DAYS)
    bank.loan_duration = Period(10, Interval.DAY)
    bank.client_interaction_interval = Period(1, Interval.DAY)
    bank.reserves_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.NONE

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.process_income_and_spending()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert round(central_bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(88.75), 8)
    assert round(central_bank.liability(BalanceEntries.RESERVES), 8) == round(Decimal(88.75), 8)
    assert round(central_bank.balance.total_balance, 8) == round(Decimal(88.75), 8)

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(1775.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(1800.0), 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == -round(Decimal(25.0), 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(1775.0), 8)

    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(88.75), 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1800.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(1775.0), 8)
    assert round(bank.liability(BalanceEntries.DEBT), 8) == round(Decimal(88.75), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(25.0), 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(1888.75), 8)


def test_reserves_mbs():
    central_bank.clear()
    central_bank.min_reserve = Decimal(0.05)
    central_bank.mbs_relative_reserve = Decimal(0.1)
    central_bank.securities_relative_reserve = Decimal(0.0)
    bank.min_reserve = Decimal(0.05)
    bank.loan_ir = Decimal(0.05)
    bank.loan_duration = Period(10, Interval.YEAR)
    bank.reserves_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.NONE

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert round(central_bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(90.0), 8)
    assert round(central_bank.liability(BalanceEntries.RESERVES), 8) == round(Decimal(90.0), 8)
    assert round(central_bank.balance.total_balance, 8) == round(Decimal(90.0), 8)

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(2000.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(2000.0), 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(0.0), 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(2000.0), 8)

    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(90.0), 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1990.0), 8)
    assert round(bank.asset(BalanceEntries.MBS), 8) == round(Decimal(10.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(2000.0), 8)
    assert round(bank.liability(BalanceEntries.DEBT), 8) == round(Decimal(90.0), 8)
    assert round(bank.liability(BalanceEntries.MBS_EQUITY), 8) == round(Decimal(10.0), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(-10.0), 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(2090.0), 8)


def test_reserve_mbs_growth():
    central_bank.clear()
    central_bank.min_reserve = Decimal(0.05)
    central_bank.mbs_relative_reserve = Decimal(0.1)
    central_bank.securities_relative_reserve = Decimal(0.0)
    bank.min_reserve = Decimal(0.05)
    bank.max_mbs_assets = Decimal(1.0)
    bank.max_security_assets = Decimal(1.0)
    bank.loan_ir = Decimal(0.05)
    bank.loan_duration = Period(10, Interval.YEAR)
    bank.reserves_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.NONE

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves()
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    central_bank.grow_mbs(Decimal(0.1))
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert round(bank.asset(BalanceEntries.MBS), 8) == round(Decimal(11.0), 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(1990.0), 8)
    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(90.0), 8)
    assert round(bank.liability(BalanceEntries.MBS_EQUITY), 8) == round(Decimal(11.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(2000.0), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(-10.0), 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(2091.0), 8)


def test_reserve_securities():
    central_bank.clear()
    central_bank.min_reserve = Decimal(0.05)
    central_bank.securities_relative_reserve = Decimal(0.1)
    central_bank.mbs_relative_reserve = Decimal(0.0)
    bank.min_reserve = Decimal(0.05)
    bank.loan_ir = Decimal(0.05)
    bank.loan_duration = Period(10, Interval.YEAR)
    bank.reserves_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.NONE

    central_bank.start_transactions()
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(10.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(10.0))
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert round(central_bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(90.0), 8)
    assert round(central_bank.liability(BalanceEntries.RESERVES), 8) == round(Decimal(90.0), 8)
    assert round(central_bank.balance.total_balance, 8) == round(Decimal(90.0), 8)

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(2000.0), 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(2000.0), 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(0.0), 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(2000.0), 8)

    assert round(bank.asset(BalanceEntries.RESERVES), 8) == round(Decimal(90.0), 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(2000.0), 8)
    assert round(bank.asset(BalanceEntries.MBS), 8) == round(Decimal(0.0), 8)
    assert round(bank.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(10.0), 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(2000.0), 8)
    assert round(bank.liability(BalanceEntries.DEBT), 8) == round(Decimal(90.0), 8)
    assert round(bank.liability(BalanceEntries.MBS_EQUITY), 8) == round(Decimal(0.0), 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(10.0), 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(2100.0), 8)


def test_full_reserve_functionality():
    central_bank.clear()
    central_bank.min_reserve = Decimal(0.04)
    central_bank.mbs_relative_reserve = Decimal(0.1)
    central_bank.securities_relative_reserve = Decimal(0.05)
    bank.min_reserve = Decimal(0.04)

    bank.loan_ir = Decimal(0.05)
    bank.loan_duration = Period(10, Interval.YEAR)
    bank.reserves_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.NONE

    central_bank.start_transactions()
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(10.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(10.0))
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert round(bank.asset(BalanceEntries.RESERVES)\
           + bank.asset(BalanceEntries.MBS)\
           + bank.asset(BalanceEntries.SECURITIES), 8) > round(Decimal(80), 8)
    assert round(bank.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(10.0), 8)
    assert round(bank.asset(BalanceEntries.LOANS) + bank.asset(BalanceEntries.MBS), 8) == round(Decimal(2000.0), 8)
    assert round(bank.asset(BalanceEntries.MBS), 8) == round(Decimal(8.0), 8)


def test_no_risk_assets():
    central_bank.clear()
    bank.min_risk_assets = Decimal(0.0)
    bank.max_risk_assets = Decimal(0.0)

    central_bank.start_transactions()
    client.borrow(Decimal(10000.0))
    bank.update_risk_assets()
    assert central_bank.end_transactions()

    assert round(bank.risk_assets, 8) == round(Decimal(0.0), 8)
    assert round(bank.client_liabilities, 8) == round(Decimal(10000.0), 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(10000.0), 8)


def test_only_securities():
    central_bank.clear()
    bank.min_risk_assets = Decimal(0.1)
    bank.max_risk_assets = Decimal(0.5)
    bank.max_mbs_assets = Decimal(0.0)
    bank.max_security_assets = Decimal(1.0)

    central_bank.start_transactions()
    client.borrow(Decimal(10000.0))
    bank.update_risk_assets()
    assert central_bank.end_transactions()

    assert round(bank.risk_assets, 8) >= Decimal(0.1) * bank.balance.assets_value
    assert round(bank.risk_assets, 8) <= Decimal(0.5) * bank.balance.assets_value
    assert round(bank.risk_assets, 8) == round(bank.asset(BalanceEntries.SECURITIES), 8)
    assert round(bank.client_liabilities, 8) == round(Decimal(10000.0) + bank.risk_assets, 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(10000.0), 8)


def test_only_mbs():
    central_bank.clear()
    bank.min_risk_assets = Decimal(0.1)
    bank.max_risk_assets = Decimal(0.5)
    bank.max_mbs_assets = Decimal(1.0)
    bank.max_security_assets = Decimal(0.0)

    central_bank.start_transactions()
    client.borrow(Decimal(10000.0))
    client.book_asset(BalanceEntries.MBS, Decimal(500.0))
    client.book_liability(BalanceEntries.MBS_EQUITY, Decimal(500.0))
    bank.update_risk_assets()
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.MBS), 8) == round(Decimal(0.0), 8)
    assert round(client.liability(BalanceEntries.MBS_EQUITY), 8) == round(Decimal(0.0), 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(10500.0), 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(500.0), 8)

    assert round(bank.risk_assets, 8) >= round(Decimal(0.1) * bank.balance.assets_value, 8)
    assert round(bank.risk_assets, 8) <= round(Decimal(0.5) * bank.balance.assets_value, 8)
    assert round(bank.risk_assets, 8) == round(bank.asset(BalanceEntries.MBS), 8)
    assert round(bank.client_liabilities, 8) == round(Decimal(10500.0), 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(10500.0) - bank.asset(BalanceEntries.MBS), 8)


def test_risk_assets():
    central_bank.clear()
    bank.min_risk_assets = Decimal(0.1)
    bank.max_risk_assets = Decimal(0.5)
    bank.max_mbs_assets = Decimal(0.7)
    bank.max_security_assets = Decimal(0.6)

    central_bank.start_transactions()
    client.borrow(Decimal(10000.0))
    bank.update_risk_assets(True)
    assert central_bank.end_transactions()

    assert round(bank.risk_assets, 8) >= round(bank.balance.assets_value * bank.min_risk_assets, 8)
    assert round(bank.risk_assets, 8) <= round(bank.balance.assets_value * bank.max_risk_assets, 8)
    assert round(bank.asset(BalanceEntries.MBS), 8) <= round(bank.risk_assets * bank.max_mbs_assets, 8)
    assert round(bank.asset(BalanceEntries.SECURITIES), 8) <= round(bank.risk_assets * bank.max_security_assets, 8)
