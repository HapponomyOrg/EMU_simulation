from emusim.cockpit.supply.euro import CentralBank, Bank, PrivateActor
from emusim.cockpit.supply.euro.balance_entries import BalanceEntries

central_bank = CentralBank()
bank = Bank(central_bank)
client = PrivateActor(bank)


def test_borrow():
    central_bank.clear()
    central_bank.start_transactions()
    client.borrow(100.0)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == 100.0
    assert client.liability(BalanceEntries.DEBT) == 100.0
    assert client.balance.total_balance == 100.0

    assert bank.asset(BalanceEntries.LOANS) == 100.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 100.0
    assert bank.balance.total_balance == 100.0


def test_save():
    central_bank.clear()
    central_bank.start_transactions()
    client.borrow(100.0)
    client.save(40.0)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == 60.0
    assert client.asset(BalanceEntries.SAVINGS) == 40.0
    assert client.liability(BalanceEntries.DEBT) == 100.0
    assert client.balance.total_balance == 100.0

    assert bank.asset(BalanceEntries.LOANS) == 100.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 60.0
    assert bank.liability(BalanceEntries.SAVINGS) == 40.0
    assert bank.balance.total_balance == 100.0


def test_sell_securities():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.SECURITIES, 100.0)
    client.book_liability(BalanceEntries.EQUITY, 100.0)
    client.trade_securities_with_bank(150.0, BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.SECURITIES) == 0.0
    assert client.asset(BalanceEntries.DEPOSITS) == 150.0
    assert client.liability(BalanceEntries.EQUITY) == 150.0
    assert client.balance.total_balance == 150.0


def test_buy_securities():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, 100.0)
    client.book_liability(BalanceEntries.EQUITY, 100.0)
    client.trade_securities_with_bank(-150.0, BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.SECURITIES) == 100.0
    assert client.liability(BalanceEntries.EQUITY) == 100.0
    assert client.balance.total_balance == 100.0

