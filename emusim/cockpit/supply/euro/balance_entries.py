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
    SEC_EQUITY = "Securities equity"
    MBS_EQUITY = "MBS equity"
    HELICOPTER_MONEY = "Helicopter money"
    RESERVES = "Reserves"
    INTEREST = "Interest"

    @staticmethod
    def equity_type(asset: str) -> str:
        if asset == BalanceEntries.SECURITIES:
            return BalanceEntries.SEC_EQUITY
        elif asset == BalanceEntries.MBS:
            return BalanceEntries.MBS_EQUITY
        else:
            return BalanceEntries.EQUITY
