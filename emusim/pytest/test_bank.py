from decimal import *

from emusim.cockpit.supply.euro import CentralBank, Bank, PrivateActor, DefaultingMode
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

    assert client.asset(BalanceEntries.DEPOSITS) == 900.0
    assert client.asset(BalanceEntries.SAVINGS) == 110.0
    assert client.liability(BalanceEntries.DEBT) == 1000.0
    assert client.liability(BalanceEntries.EQUITY) == 10.0
    assert client.balance.total_balance == 1010.0

    assert bank.asset(BalanceEntries.LOANS) == 1000.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 900.0
    assert bank.liability(BalanceEntries.SAVINGS) == 110.0
    assert bank.liability(BalanceEntries.EQUITY) == -10.0
    assert bank.balance.total_balance == 1000.0


def test_full_income():
    central_bank.clear()
    bank.loan_ir = Decimal(0.05 * Period.YEAR_DAYS)
    bank.loan_duration = Period(10, Interval.DAY)
    bank.client_interaction_interval = Period(1, Interval.DAY)
    bank.income_from_interest = Decimal(0.8)
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = Decimal(0.0)

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.process_income()
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == 1675.0
    assert client.liability(BalanceEntries.DEBT) == 1800.0
    assert client.liability(BalanceEntries.EQUITY) == -125.0
    assert client.balance.total_balance == 1675.0

    assert bank.asset(BalanceEntries.LOANS) == 1800.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 1675.0
    assert bank.liability(BalanceEntries.EQUITY) == 125.0


def test_partial_income():
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
    bank.process_income()
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == 1727.5
    assert client.asset(BalanceEntries.UNRESOLVED_DEBT) == 50.0
    assert client.liability(BalanceEntries.DEBT) == 1800.0
    assert client.liability(BalanceEntries.UNRESOLVED_DEBT) == 50.0
    assert client.liability(BalanceEntries.EQUITY) == -72.5
    assert client.balance.total_balance == 1777.5

    assert bank.asset(BalanceEntries.LOANS) == 1800.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 1727.5
    assert bank.liability(BalanceEntries.EQUITY) == 72.5
    assert bank.balance.total_balance == 1800.0


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
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = Decimal(0.0)
    client.defaults_bought_by_debt_collectors = Decimal(0.0)

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.process_income()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert central_bank.asset(BalanceEntries.LOANS) == 83.75
    assert central_bank.liability(BalanceEntries.RESERVES) == 83.75
    assert central_bank.balance.total_balance == 83.75

    assert client.asset(BalanceEntries.DEPOSITS) == 1675.0
    assert client.liability(BalanceEntries.DEBT) == 1800.0
    assert client.liability(BalanceEntries.EQUITY) == -125.0
    assert client.balance.total_balance == 1675.0

    assert bank.asset(BalanceEntries.RESERVES) == 83.75
    assert bank.asset(BalanceEntries.LOANS) == 1800.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 1675.0
    assert bank.liability(BalanceEntries.DEBT) == 83.75
    assert bank.liability(BalanceEntries.EQUITY) == 125.0
    assert bank.balance.total_balance == 1883.75


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
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = Decimal(0.0)
    client.defaults_bought_by_debt_collectors = Decimal(0.0)

    central_bank.start_transactions()
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert central_bank.asset(BalanceEntries.LOANS) == 90.0
    assert central_bank.liability(BalanceEntries.RESERVES) == 90.0
    assert central_bank.balance.total_balance == 90.0

    assert client.asset(BalanceEntries.DEPOSITS) == 2000.0
    assert client.liability(BalanceEntries.DEBT) == 2000.0
    assert client.liability(BalanceEntries.EQUITY) == 0.0
    assert client.balance.total_balance == 2000.0

    assert bank.asset(BalanceEntries.RESERVES) == 90.0
    assert bank.asset(BalanceEntries.LOANS) == 1990.0
    assert bank.asset(BalanceEntries.MBS) == 10.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 2000.0
    assert bank.liability(BalanceEntries.DEBT) == 90.0
    assert bank.liability(BalanceEntries.MBS_EQUITY) == 10.0
    assert bank.liability(BalanceEntries.EQUITY) == -10.0
    assert bank.balance.total_balance == 2090.0


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
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = Decimal(0.0)
    client.defaults_bought_by_debt_collectors = Decimal(0.0)

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

    assert bank.asset(BalanceEntries.MBS) == 11.0
    assert bank.asset(BalanceEntries.LOANS) == 1990.0
    assert bank.asset(BalanceEntries.RESERVES) == 90.0
    assert bank.liability(BalanceEntries.MBS_EQUITY) == 11.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 2000.0
    assert bank.liability(BalanceEntries.EQUITY) == -10.0
    assert bank.balance.total_balance == 2091.0


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
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = Decimal(0.0)
    client.defaults_bought_by_debt_collectors = Decimal(0.0)

    central_bank.start_transactions()
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(10.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(10.0))
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert central_bank.asset(BalanceEntries.LOANS) == 90.0
    assert central_bank.liability(BalanceEntries.RESERVES) == 90.0
    assert central_bank.balance.total_balance == 90.0

    assert client.asset(BalanceEntries.DEPOSITS) == 2000.0
    assert client.liability(BalanceEntries.DEBT) == 2000.0
    assert client.liability(BalanceEntries.EQUITY) == 0.0
    assert client.balance.total_balance == 2000.0

    assert bank.asset(BalanceEntries.RESERVES) == 90.0
    assert bank.asset(BalanceEntries.LOANS) == 2000.0
    assert bank.asset(BalanceEntries.MBS) == 0.0
    assert bank.asset(BalanceEntries.SECURITIES) == 10.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 2000.0
    assert bank.liability(BalanceEntries.DEBT) == 90.0
    assert bank.liability(BalanceEntries.MBS_EQUITY) == 0.0
    assert bank.liability(BalanceEntries.EQUITY) == 10.0
    assert bank.balance.total_balance == 2100.0


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
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = Decimal(0.0)
    client.defaults_bought_by_debt_collectors = Decimal(0.0)

    central_bank.start_transactions()
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(10.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(10.0))
    client.borrow(Decimal(2000.0))
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves()
    assert central_bank.end_transactions()

    assert bank.asset(BalanceEntries.RESERVES)\
           + bank.asset(BalanceEntries.MBS)\
           + bank.asset(BalanceEntries.SECURITIES) > 80
    assert bank.asset(BalanceEntries.SECURITIES) == 10.0
    assert bank.asset(BalanceEntries.LOANS) + bank.asset(BalanceEntries.MBS) == 2000.0
    assert bank.asset(BalanceEntries.MBS) == 8.0


def test_no_risk_assets():
    central_bank.clear()
    bank.min_risk_assets = Decimal(0.0)
    bank.max_risk_assets = Decimal(0.0)

    central_bank.start_transactions()
    client.borrow(Decimal(10000.0))
    bank.update_risk_assets()
    assert central_bank.end_transactions()

    assert bank.risk_assets == 0.0
    assert bank.client_liabilities == 10000.0
    assert bank.asset(BalanceEntries.LOANS) == 10000.0


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

    assert bank.risk_assets >= Decimal(0.1) * bank.balance.assets_value
    assert bank.risk_assets <= Decimal(0.5) * bank.balance.assets_value
    assert bank.risk_assets == bank.asset(BalanceEntries.SECURITIES)
    assert bank.client_liabilities == Decimal(10000.0) + bank.risk_assets
    assert bank.asset(BalanceEntries.LOANS) == 10000.0


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

    assert client.asset(BalanceEntries.MBS) == 0.0
    assert client.liability(BalanceEntries.MBS_EQUITY) == 0.0
    assert client.asset(BalanceEntries.DEPOSITS) == 10500.0
    assert client.liability(BalanceEntries.EQUITY) == 500.0

    assert bank.risk_assets >= Decimal(0.1) * bank.balance.assets_value
    assert bank.risk_assets <= Decimal(0.5) * bank.balance.assets_value
    assert bank.risk_assets == bank.asset(BalanceEntries.MBS)
    assert bank.client_liabilities == 10500.0
    assert bank.asset(BalanceEntries.LOANS) == Decimal(10500.0) - bank.asset(BalanceEntries.MBS)


def test_risk_assets():
    central_bank.clear()
    bank.min_risk_assets = Decimal(0.1)
    bank.max_risk_assets = Decimal(0.5)
    bank.max_mbs_assets = Decimal(0.7)
    bank.max_security_assets = Decimal(0.6)

    central_bank.start_transactions()
    client.borrow(Decimal(10000.0))
    bank.update_risk_assets()
    assert central_bank.end_transactions()
