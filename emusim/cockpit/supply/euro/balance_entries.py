# balance sheet entries

class BalanceEntries:
    QE = "QE"
    LOANS = "Loans"
    MBS = "Mortgage Backed Ssecurities"
    SECURITIES = "Securities"
    DEPOSITS = "Deposits"
    DEBT = "Debt"
    UNRESOLVED_DEBT = "Unresolved debt"
    SAVINGS = "Savings"
    EQUITY = "Equity"
    MBS_EQUITY = "MBS equity"
    HELICOPTER_MONEY = "Helicopter money"
    RESERVES = "Reserves"
    INTEREST = "Interest"

    @staticmethod
    def equity_type(asset: str) -> str:
        if asset == BalanceEntries.MBS:
            return BalanceEntries.MBS_EQUITY
        else:
            return BalanceEntries.EQUITY
