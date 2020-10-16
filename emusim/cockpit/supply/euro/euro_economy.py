from decimal import *

from . import CentralBank, Bank, PrivateActor, BalanceEntries
from emusim.cockpit.utilities.cycles import Period, Interval


class EuroEconomy():

    def __init__(self):
        self.__central_bank: CentralBank = CentralBank()
        PrivateActor(Bank(self.central_bank))

        self.cycle_length: Period = Period(1, Interval.DAY)
        self.__growth_rate: Decimal = Decimal(0.014)
        self.__inflation: Decimal = Decimal(0.019)
        self.__mbs_growth: Decimal = Decimal(0.0)
        self.__security_growth: Decimal = Decimal(0.0)
        self.__lending_satisfaction_rate = Decimal(1.0)

    @property
    def growth_rate(self) -> Decimal:
        return self.__growth_rate

    @growth_rate.setter
    def growth_rate(self, rate: Decimal):
        self.__growth_rate = Decimal(rate)

    @property
    def inflation(self) -> Decimal:
        return self.__inflation

    @inflation.setter
    def inflation(self, percentage: Decimal):
        self.__inflation = Decimal(percentage)

    @property
    def mbs_growth(self) -> Decimal:
        return self.__mbs_growth

    @mbs_growth.setter
    def mbs_growth(self, percentage: Decimal):
        self.__mbs_growth = Decimal(percentage)

    @property
    def security_growth(self) -> Decimal:
        return self.__security_growth

    @security_growth.setter
    def security_growth(self, percentage: Decimal):
        self.__security_growth = Decimal(percentage)

    @property
    def lending_satisfaction_rate(self) -> Decimal:
        return self.__lending_satisfaction_rate

    @lending_satisfaction_rate.setter
    def lending_satisfaction_rate(self, rate: Decimal):
        self.__lending_satisfaction_rate = Decimal(rate)

    @property
    def cycle_growth_rate(self) -> Decimal:
        return round(Decimal(self.growth_rate * self.cycle_length.days / Period.YEAR_DAYS), 8)

    @property
    def cycle_inflation_rate(self) -> Decimal:
        return round(Decimal(self.inflation * self.cycle_length.days / Period.YEAR_DAYS), 8)

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def bank(self) -> Bank:
        return self.central_bank.bank

    @property
    def client(self) -> PrivateActor:
        return self.bank.client

    def start_transactions(self):
        self.central_bank.start_transactions()

    def end_transactions(self) -> bool:
        return self.central_bank.end_transactions()

    def inflate(self):
        self.central_bank.inflate(self.cycle_inflation_rate)

    def grow_mbs(self):
        self.central_bank.grow_mbs(self.mbs_growth)

    def grow_securities(self):
        self.central_bank.grow_securities(self.security_growth)

    def process_qe(self):
        self.central_bank.process_qe()

    def process_bank_loans(self):
        self.central_bank.process_bank_loans()

    def process_helicopter_money(self):
        self.central_bank.process_helicopter_money()

    def process_savings(self):
        self.central_bank.process_reserve_interests()
        self.bank.process_client_savings()

    def process_bank_income(self):
        self.bank.process_income()

    def process_bank_spending(self):
        self.bank.spend()

    def process_borrowing(self, amount: Decimal):
        self.client.borrow(amount)

    def update_reserves(self):
        self.bank.update_reserves()

    def update_risk_assets(self):
        self.bank.update_risk_assets()

    @property
    def im(self) -> Decimal:
        return self.bank.liability(BalanceEntries.DEPOSITS) + self.bank.liability(BalanceEntries.SAVINGS)

    @property
    def private_debt(self) -> Decimal:
        return self.client.liability(BalanceEntries.DEBT)

    @property
    def bank_debt(self) -> Decimal:
        return self.bank.liability(BalanceEntries.DEBT)
