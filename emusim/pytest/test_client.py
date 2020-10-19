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

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(100.0) , 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(100.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(100.0) , 8)

    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(100.0) , 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(100.0) , 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(100.0) , 8)


def test_save():
    client.savings_rate = 0.4

    central_bank.clear()
    central_bank.start_transactions()
    client.borrow(Decimal(100.0))
    client.process_savings()
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(60.0) , 8)
    assert round(client.asset(BalanceEntries.SAVINGS), 8) == round(Decimal(40.0) , 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(100.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(100.0) , 8)

    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(100.0) , 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(60.0) , 8)
    assert round(bank.liability(BalanceEntries.SAVINGS), 8) == round(Decimal(40.0) , 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(100.0) , 8)


def test_sell_securities():
    client.borrow_for_securities = 0.0

    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.SECURITIES, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(150.0), BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(0.0) , 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(150.0) , 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(150.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(150.0) , 8)

    assert round(bank.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(150.0) , 8)
    assert round(bank.client_liabilities, 8) == round(Decimal(150.0) , 8)
    assert round(bank.balance.assets_value, 8) == round(Decimal(150.0) , 8)


def test_buy_securities_none_available():
    client.borrow_for_securities = 0.0

    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    bank.book_liability(BalanceEntries.DEPOSITS, Decimal(100.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(-100.0))
    client.trade_securities_with_bank(Decimal(-150.0), BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(100.0) , 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(100.0) , 8)
    assert round(client.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(0.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(100.0) , 8)

    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(100.0) , 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(-100.0) , 8)
    assert round(bank.balance.total_balance, 8) == round(Decimal(0.0) , 8)


def test_buy_securities_available():
    client.borrow_for_securities = 0.0

    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    bank.book_liability(BalanceEntries.DEPOSITS, Decimal(100.0))
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(200.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(-150.0), BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(0.0) , 8)
    assert round(client.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(100.0) , 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(100.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(100.0) , 8)

    assert round(bank.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(100.0) , 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(0.0) , 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(100.0) , 8)


def test_buy_securities_borrow():
    client.borrow_for_securities = 0.5

    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    bank.book_liability(BalanceEntries.DEPOSITS, Decimal(100.0))
    bank.book_asset(BalanceEntries.SECURITIES, Decimal(200.0))
    bank.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(-150.0), BalanceEntries.SECURITIES)
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(0.0) , 8)
    assert round(client.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(125.0) , 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(100.0) , 8)
    assert round(client.liability(BalanceEntries.DEBT), 8) == round(Decimal(25.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(125.0) , 8)

    assert round(bank.asset(BalanceEntries.SECURITIES), 8) == round(Decimal(75.0) , 8)
    assert round(bank.asset(BalanceEntries.LOANS), 8) == round(Decimal(25.0) , 8)
    assert round(bank.liability(BalanceEntries.DEPOSITS), 8) == round(Decimal(0.0) , 8)
    assert round(bank.liability(BalanceEntries.EQUITY), 8) == round(Decimal(100.0) , 8)


def test_sell_mbs_none_available():
    central_bank.clear()
    central_bank.start_transactions()
    client.trade_securities_with_bank(Decimal(150.0), BalanceEntries.MBS)
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.MBS), 8) == round(Decimal(0.0) , 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(0.0) , 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(0.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(0.0) , 8)


def test_sell_mbs_available():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.MBS, Decimal(100.0))
    client.book_liability(BalanceEntries.MBS_EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(150.0), BalanceEntries.MBS)
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.MBS), 8) == round(Decimal(0.0) , 8)
    assert round(client.asset(BalanceEntries.DEPOSITS), 8) == round(Decimal(100.0) , 8)
    assert round(client.liability(BalanceEntries.EQUITY), 8) == round(Decimal(100.0) , 8)
    assert round(client.liability(BalanceEntries.MBS_EQUITY), 8) == round(Decimal(0.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(100.0) , 8)

    assert round(bank.asset(BalanceEntries.MBS), 8) == round(Decimal(100.0) , 8)
    assert round(bank.liability(BalanceEntries.MBS_EQUITY), 8) == round(Decimal(100.0) , 8)


def buy_mbs():
    central_bank.clear()
    central_bank.start_transactions()
    client.book_asset(BalanceEntries.DEPOSITS, Decimal(100.0))
    client.book_liability(BalanceEntries.EQUITY, Decimal(100.0))
    client.trade_securities_with_bank(Decimal(-150.0), BalanceEntries.MBS)
    assert central_bank.end_transactions()

    assert round(client.asset(BalanceEntries.MBS), 8) == round(Decimal(100.0) , 8)
    assert round(client.liability(BalanceEntries.MBS_EQUITY), 8) == round(Decimal(100.0) , 8)
    assert round(client.balance.total_balance, 8) == round(Decimal(100.0) , 8)

