from typing import Set, Tuple

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.bank import Bank
from emusim.cockpit.supply.euro.economic_actor import EconomicActor


class CentralBank(EconomicActor):
    reserve_ir: float = 0.0
    surplus_reserve_ir: float = -0.005

    loan_ir: float = 0.01
    loan_duration: int = 1

    min_reserve: float = 4.0
    mbs_reserve: float = 0.0                # max % of 'reserve' in the form of MBS
    securities_reserve: float = 0.0         # max % of 'reserve' in the form of securities

    __registered_banks: Set[Bank] = set()

    def __init__(self, min_reserves: float):
        self.__min_reserves = min_reserves

    def register(self, bank: Bank):
        self.registered_banks.add(bank)

    @property
    def registered_banks(self) -> Set[Bank]:
        return self.__registered_banks

    @property
    def assets(self) -> Set:
        return {LOANS, SECURITIES, HELICOPTER_MONEY, FUNDING}

    @property
    def liabilities(self) -> Set:
        return {RESERVES, EQUITY}

    def book_loan(self, amount: float):
        self.book_asset(LOANS, amount)
        self.book_liabilaty(RESERVES, amount)

    def process_bank_loans(self):
        for bank in self.registered_banks:
            paid: Tuple[float, float] = bank.pay_debt(self.loan_ir)
            interest: float = paid[0]
            installment: float = paid[1]

            # TODO interest goes to cost spending and governments => results in deposits in the real economy?

            self.book_asset(LOANS, -installment)
            self.book_liabilaty(RESERVES, -installment)
