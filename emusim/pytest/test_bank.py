from emusim.cockpit.supply.euro import CentralBank, Bank, PrivateActor, DefaultingMode
from emusim.cockpit.supply.euro.balance_entries import BalanceEntries

central_bank = CentralBank()
bank = Bank(central_bank)
client = PrivateActor(bank)


def test_pay_savings_interest():
    central_bank.clear()
    bank.savings_ir = 0.1

    central_bank.start_transactions()
    client.borrow(1000.0)
    client.save(100.0)
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
    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.0

    central_bank.start_transactions()
    client.borrow(2000.0)
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
    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.25
    client.defaults_bought_by_debt_collectors = 1.0

    central_bank.start_transactions()
    client.borrow(2000.0)
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
    central_bank.min_reserve = 0.05
    central_bank.mbs_relative_reserve = 0.0
    central_bank.securities_relative_reserve = 0.0
    bank.max_reserve = 0.05
    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.0
    client.defaults_bought_by_debt_collectors = 0.0

    central_bank.start_transactions()
    client.borrow(2000.0)
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.process_income()
    bank.update_reserves_and_risk_assets()
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
    central_bank.min_reserve = 0.05
    central_bank.mbs_relative_reserve = 0.1
    central_bank.securities_relative_reserve = 0.0
    bank.max_reserve = 0.05
    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.0
    client.defaults_bought_by_debt_collectors = 0.0

    central_bank.start_transactions()
    client.borrow(2000.0)
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves_and_risk_assets()
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
    central_bank.min_reserve = 0.05
    central_bank.mbs_relative_reserve = 0.1
    central_bank.securities_relative_reserve = 0.0
    bank.max_reserve = 0.05
    bank.max_mbs_assets = 1.0
    bank.max_security_assets = 1.0
    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.0
    client.defaults_bought_by_debt_collectors = 0.0

    central_bank.start_transactions()
    client.borrow(2000.0)
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves_and_risk_assets()
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    central_bank.grow_mbs(0.1)
    bank.update_reserves_and_risk_assets()
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
    central_bank.min_reserve = 0.05
    central_bank.securities_relative_reserve = 0.1
    central_bank.mbs_relative_reserve = 0.0
    bank.max_reserve = 0.05
    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.0
    client.defaults_bought_by_debt_collectors = 0.0

    central_bank.start_transactions()
    client.borrow(2000.0)
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves_and_risk_assets()
    assert central_bank.end_transactions()

    assert central_bank.asset(BalanceEntries.LOANS) == 90.0
    assert central_bank.liability(BalanceEntries.RESERVES) == 90.0
    assert central_bank.balance.total_balance == 90.0

    assert client.asset(BalanceEntries.DEPOSITS) == 2010.0
    assert client.liability(BalanceEntries.DEBT) == 2000.0
    assert client.liability(BalanceEntries.EQUITY) == 10.0
    assert client.balance.total_balance == 2010.0

    assert bank.asset(BalanceEntries.RESERVES) == 90.0
    assert bank.asset(BalanceEntries.LOANS) == 2000.0
    assert bank.asset(BalanceEntries.MBS) == 0.0
    assert bank.asset(BalanceEntries.SECURITIES) == 10.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 2010.0
    assert bank.liability(BalanceEntries.DEBT) == 90.0
    assert bank.liability(BalanceEntries.MBS_EQUITY) == 0.0
    assert bank.liability(BalanceEntries.EQUITY) == 10.0
    assert bank.liability(BalanceEntries.EQUITY) == -10.0
    assert bank.balance.total_balance == 2100.0


def test_full_reserve_functionality():
    central_bank.clear()
    central_bank.min_reserve = 0.04
    central_bank.mbs_relative_reserve = 0.1
    central_bank.securities_relative_reserve = 0.05
    bank.max_reserve = 0.05
    bank.min_risk_assets = 0.1
    bank.max_risk_assets = 0.5
    bank.max_mbs_assets = 0.7
    bank.max_security_assets = 0.6

    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.0
    client.defaults_bought_by_debt_collectors = 0.0

    central_bank.start_transactions()
    client.borrow(2000.0)
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.update_reserves_and_risk_assets()
    assert central_bank.end_transactions()
