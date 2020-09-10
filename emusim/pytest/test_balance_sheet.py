from emusim.cockpit.supply.euro import BalanceSheet, BalanceSheetTimeline
from emusim.cockpit.supply.euro.balance_entries import BalanceEntries


def test_entries():
    balance_sheet: BalanceSheetTimeline = BalanceSheetTimeline()

    print(balance_sheet)

    assert balance_sheet.asset(BalanceEntries.SECURITIES) == 0.0
    assert balance_sheet.liability(BalanceEntries.DEPOSITS) == 0.0
    balance_sheet.book_asset(BalanceEntries.SECURITIES, 100.0)
    assert balance_sheet.asset(BalanceEntries.SECURITIES) == 100.0
    balance_sheet.book_asset(BalanceEntries.DEPOSITS, 25.0)
    assert balance_sheet.asset(BalanceEntries.DEPOSITS) == 25.0
    balance_sheet.book_asset(BalanceEntries.DEPOSITS, 25.0)
    assert balance_sheet.asset(BalanceEntries.DEPOSITS) == 50.0
    assert balance_sheet.assets_value == 150.0
    assert not balance_sheet.validate()
    balance_sheet.book_liability(BalanceEntries.EQUITY, 150.0)
    assert balance_sheet.liability(BalanceEntries.EQUITY) == 150.0
    assert balance_sheet.total_balance == 150.0
    assert balance_sheet.validate()


def test_history():
    balance: BalanceSheetTimeline = BalanceSheetTimeline()

    balance.book_asset(BalanceEntries.DEPOSITS, 100.00)
    assert balance.asset(BalanceEntries.DEPOSITS) == 100.0

    balance.book_liability(BalanceEntries.EQUITY, 100.0)
    assert balance.liability(BalanceEntries.EQUITY) == 100.0

    balance.save_state()

    history: BalanceSheet = balance.balance_history(-1)
    assert history.asset(BalanceEntries.DEPOSITS) == 100.0

    assert history.liability(BalanceEntries.EQUITY) == 100.0

    delta: BalanceSheet = balance.delta_history(-1)

    print(delta)

    assert delta.asset(BalanceEntries.DEPOSITS) == 0.0
    assert delta.liability(BalanceEntries.EQUITY) == 0.0

    balance.book_asset(BalanceEntries.DEPOSITS, 50.0)
    assert balance.asset(BalanceEntries.DEPOSITS) == 150.0
    balance.book_asset(BalanceEntries.SECURITIES, 50.0)
    assert balance.asset(BalanceEntries.SECURITIES) == 50.0

    balance.book_liability(BalanceEntries.EQUITY, 100.0)
    assert balance.liability(BalanceEntries.EQUITY) == 200.00

    delta = balance.delta_history(-1)

    assert delta.asset(BalanceEntries.DEPOSITS) == 50.0
    assert delta.asset(BalanceEntries.SECURITIES) == 50.0
    assert delta.liability(BalanceEntries.EQUITY) == 100.0
