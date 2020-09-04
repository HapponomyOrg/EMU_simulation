from emusim.cockpit.supply.euro import CentralBank, Bank, PrivateActor, DefaultingMode
from emusim.cockpit.supply.euro.balance_entries import *

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

    assert client.asset(DEPOSITS) == 900.0
    assert client.asset(SAVINGS) == 110.0
    assert client.liability(DEBT) == 1000.0
    assert client.liability(EQUITY) == 10.0
    assert client.balance.total_balance == 1010.0

    assert bank.asset(LOANS) == 1000.0
    assert bank.liability(DEPOSITS) == 900.0
    assert bank.liability(SAVINGS) == 110.0
    assert bank.liability(EQUITY) == -10.0
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

    assert client.asset(DEPOSITS) == 1675.0
    assert client.liability(DEBT) == 1800.0
    assert client.liability(EQUITY) == -125.0
    assert client.balance.total_balance == 1675.0

    assert bank.asset(LOANS) == 1800.0
    assert bank.liability(DEPOSITS) == 1675.0
    assert bank.liability(EQUITY) == 125.0


def test_partial_income():
    central_bank.clear()
    bank.loan_ir = 0.05
    bank.loan_duration = 10
    bank.income_from_interest = 0.8
    client.defaulting_mode = DefaultingMode.FIXED
    client.fixed_defaulting_rate = 0.25

    central_bank.start_transactions()
    client.borrow(2000.0)
    assert central_bank.end_transactions()
    central_bank.start_transactions()
    bank.process_income()
    assert central_bank.end_transactions()

    assert client.asset(DEPOSITS) == 1727.5
    assert client.liability(DEBT) == 1800.0
    assert client.liability(UNRESOLVED_DEBT) == 50.0
    assert client.liability(EQUITY) == -122.5
    assert client.balance.total_balance == 1727.5

    assert bank.asset(LOANS) == 1800.0
    assert bank.liability(DEPOSITS) == 1727.5
    assert bank.liability(EQUITY) == 72.5
    assert bank.balance.total_balance == 1800.0
