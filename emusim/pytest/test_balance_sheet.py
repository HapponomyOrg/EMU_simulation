from emusim.cockpit.supply.euro import BalanceSheet, BalanceSheetTimeline
from emusim.cockpit.supply.euro.balance_entries import *


def test_entries():
    balance_sheet: BalanceSheetTimeline = BalanceSheetTimeline()

    print(balance_sheet)

    assert balance_sheet.asset(SECURITIES) == 0.0
    assert balance_sheet.liability(DEPOSITS) == 0.0
    balance_sheet.book_asset(SECURITIES, 100.0)
    assert balance_sheet.asset(SECURITIES) == 100.0
    balance_sheet.book_asset(DEPOSITS, 25.0)
    assert balance_sheet.asset(DEPOSITS) == 25.0
    balance_sheet.book_asset(DEPOSITS, 25.0)
    assert balance_sheet.asset(DEPOSITS) == 50.0
    assert balance_sheet.assets_value == 150.0
    assert not balance_sheet.validate()
    balance_sheet.book_liability(EQUITY, 150.0)
    assert balance_sheet.liability(EQUITY) == 150.0
    assert balance_sheet.total_balance == 150.0
    assert balance_sheet.validate()


def test_history():
    balance: BalanceSheetTimeline = BalanceSheetTimeline()

    balance.book_asset(DEPOSITS, 100.00)
    assert balance.asset(DEPOSITS) == 100.0

    balance.book_liability(EQUITY, 100.0)
    assert balance.liability(EQUITY) == 100.0

    balance.save_state()

    history: BalanceSheet = balance.balance_history(-1)
    assert history.asset(DEPOSITS) == 100.0

    assert history.liability(EQUITY) == 100.0

    delta: BalanceSheet = balance.delta_history(-1)

    print(delta)

    assert delta.asset(DEPOSITS) == 0.0
    assert delta.liability(EQUITY) == 0.0

    balance.book_asset(DEPOSITS, 50.0)
    assert balance.asset(DEPOSITS) == 150.0
    balance.book_asset(SECURITIES, 50.0)
    assert balance.asset(SECURITIES) == 50.0

    balance.book_liability(EQUITY, 100.0)
    assert balance.liability(EQUITY) == 200.00

    delta = balance.delta_history(-1)

    assert delta.asset(DEPOSITS) == 50.0
    assert delta.asset(SECURITIES) == 50.0
    assert delta.liability(EQUITY) == 100.0
