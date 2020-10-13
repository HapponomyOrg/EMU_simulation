from typing import Set
from decimal import *

from . import CentralBank, BalanceEntries
from emusim.cockpit.utilities.cycles import Period, Interval


class EuroEconomy():

    def __init__(self, central_banks: Set[CentralBank]):
        self.__central_banks: Set[CentralBank] = set(central_banks)
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
    def central_banks(self) -> Set[CentralBank]:
        return self.__central_banks

    def start_transactions(self):
        for central_bank in self.central_banks:
            central_bank.start_transactions()

    def end_transactions(self) -> bool:
        success: bool = True

        for central_bank in self.central_banks:
            success = success and central_bank.end_transactions()

        return success

    def inflate(self):
        for central_bank in self.central_banks:
            central_bank.inflate(self.cycle_inflation_rate)

    def grow_mbs(self):
        for central_bank in self.central_banks:
            central_bank.grow_mbs(self.mbs_growth)

    def grow_securities(self):
        for central_bank in self.central_banks:
            central_bank.grow_securities(self.security_growth)

    def process_qe(self):
        for central_bank in self.central_banks:
            central_bank.process_qe()

    def process_helicopter_money(self):
        for central_bank in self.central_banks:
            central_bank.process_helicopter_money()

    def process_savings(self):
        for central_bank in self.central_banks:
            central_bank.process_reserve_interests()

            for bank in central_bank.registered_banks:
                bank.process_client_savings()

    def process_bank_income(self):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                bank.process_income()

    def process_bank_spending(self):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                bank.spend()

    def process_borrowing(self, amount: Decimal):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                for client in bank.clients:
                    client.borrow(amount)

    def process_saving(self):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                for client in bank.clients:
                    client.process_savings()

    def update_reserves(self):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                bank.update_reserves()

    def update_risk_assets(self):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                bank.update_risk_assets()

    @property
    def im(self) -> Decimal:
        im: Decimal = Decimal(0.0)

        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                im += bank.liability(BalanceEntries.DEPOSITS)
                im += bank.liability(BalanceEntries.SAVINGS)

        return im

    @property
    def private_debt(self) -> Decimal:
        debt: Decimal = Decimal(0.0)

        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                for client in bank.clients:
                    debt += client.liability(BalanceEntries.DEBT)

        return debt

    @property
    def bank_debt(self) -> Decimal:
        debt: Decimal = Decimal(0.0)

        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                debt += bank.liability(BalanceEntries.DEBT)

        return debt
