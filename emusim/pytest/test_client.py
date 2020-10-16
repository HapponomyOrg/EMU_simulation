from decimal import *

from emusim.cockpit.supply.euro import CentralBank, Bank, PrivateActor
from emusim.cockpit.supply.euro.balance_entries import BalanceEntries

central_bank: CentralBank = CentralBank()
bank: Bank = Bank(central_bank)
client: PrivateActor = PrivateActor(bank)


def test_borrow():
    central_bank.clear()
    central_bank.start_transactions()
    client.borrow(Decimal(100.0))
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == 100.0
    assert client.liability(BalanceEntries.DEBT) == 100.0
    assert client.balance.total_balance == 100.0

    assert bank.asset(BalanceEntries.LOANS) == 100.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 100.0
    assert bank.balance.total_balance == 100.0


def test_save():
    client.savings_rate = 0.4

    central_bank.clear()
    central_bank.start_transactions()
    client.borrow(Decimal(100.0))
    client.process_savings()
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
    client.book_asset(BalanceEntries.SECURITIES, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(150.0), BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.SECURITIES) == 0.0
    assert client.asset(BalanceEntries.DEPOSITS) == 150.0
    assert client.liability(BalanceEntries.EQUITY) == 150.0
    assert client.balance.total_balance == 150.0

    assert bank.asset(BalanceEntries.SECURITIES) == 150.0
    assert bank.client_liabilities == 150.0
    assert bank.balance.assets_value == 150.0


def test_buy_securities_none_available():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    bank.book_liability(BalanceEntries.DEPOSITS, Decimal(100.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(-100.0))
    client.trade_securities_with_bank(Decimal(-150.0), BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == 100.0
    assert client.liability(BalanceEntries.EQUITY) == 100.0
    assert client.asset(BalanceEntries.SECURITIES) == 0.0
    assert client.balance.total_balance == 100.0

    assert bank.liability(BalanceEntries.DEPOSITS) == 100.0
    assert bank.liability(BalanceEntries.EQUITY) == -100.0
    assert bank.balance.total_balance == 0.0


def test_buy_securities_available():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    bank.book_liability(BalanceEntries.DEPOSITS, Decimal(100.0))
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(200.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(-150.0), BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.DEPOSITS) == 0.0
    assert client.asset(BalanceEntries.SECURITIES) == 100.0
    assert client.liability(BalanceEntries.EQUITY) == 100.0
    assert client.balance.total_balance == 100.0

    assert bank.asset(BalanceEntries.SECURITIES) == 100.0
    assert bank.liability(BalanceEntries.DEPOSITS) == 0.0
    assert bank.liability(BalanceEntries.EQUITY) == 100.0


def test_sell_mbs_none_available():
    central_bank.clear()
    central_bank.start_transactions()
    client.trade_securities_with_bank(Decimal(150.0), BalanceEntries.MBS)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.MBS) == 0.0
    assert client.asset(BalanceEntries.DEPOSITS) == 0.0
    assert client.liability(BalanceEntries.EQUITY) == 0.0
    assert client.balance.total_balance == 0.0


def test_sell_mbs_available():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.MBS, Decimal(100.0))
    client.book_liability(BalanceEntries.MBS_EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(150.0), BalanceEntries.MBS)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.MBS) == 0.0
    assert client.asset(BalanceEntries.DEPOSITS) == 100.0
    assert client.liability(BalanceEntries.EQUITY) == 100.0
    assert client.liability(BalanceEntries.MBS_EQUITY) == 0.0
    assert client.balance.total_balance == 100.0

    assert bank.asset(BalanceEntries.MBS) == 100.0
    assert bank.liability(BalanceEntries.MBS_EQUITY) == 100.0


def buy_mbs():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(-150.0), BalanceEntries.MBS)
    assert central_bank.end_transactions()

    assert client.asset(BalanceEntries.MBS) == 100.0
    assert client.liability(BalanceEntries.MBS_EQUITY) == 100.0
    assert client.balance.total_balance == 100.0

