from emusim.cockpit.supply.euro import CentralBank, Bank, PrivateActor
from emusim.cockpit.supply.euro.balance_entries import *

central_bank = CentralBank()
bank = Bank(central_bank)
client = PrivateActor(bank)


def test_borrow():
    central_bank.clear()
    central_bank.start_transactions()
    client.borrow(100.0)
    assert central_bank.end_transactions()

    assert client.asset(DEPOSITS) == 100.0
    assert client.liability(DEBT) == 100.0
    assert client.balance.total_balance == 100.0

    assert bank.asset(LOANS) == 100.0
    assert bank.liability(DEPOSITS) == 100.0
    assert bank.balance.total_balance == 100.0


def test_save():
    central_bank.clear()
    central_bank.start_transactions()
    client.borrow(100.0)
    client.save(40.0)
    assert central_bank.end_transactions()

    assert client.asset(DEPOSITS) == 60.0
    assert client.asset(SAVINGS) == 40.0
    assert client.liability(DEBT) == 100.0
    assert client.balance.total_balance == 100.0

    assert bank.asset(LOANS) == 100.0
    assert bank.liability(DEPOSITS) == 60.0
    assert bank.liability(SAVINGS) == 40.0
    assert bank.balance.total_balance == 100.0


def test_sell_securities():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(SECURITIES, 100.0)
    client.book_liability(SEC_EQUITY, 100.0)
    client.trade_securities_with_bank(150.0)
    assert central_bank.end_transactions()

    assert client.asset(SECURITIES) == 0.0
    assert client.asset(DEPOSITS) == 150.0
    assert client.liability(SEC_EQUITY) == 0.0
    assert client.liability(EQUITY) == 150.0
    assert client.balance.total_balance == 150.0


def test_buy_securities():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(DEPOSITS, 100.0)
    client.book_liability(EQUITY, 100.0)
    client.trade_securities_with_bank(-150.0)
    assert central_bank.end_transactions()

    assert client.asset(SECURITIES) == 100.0
    assert client.liability(SEC_EQUITY) == 100.0
    assert client.balance.total_balance == 100.0