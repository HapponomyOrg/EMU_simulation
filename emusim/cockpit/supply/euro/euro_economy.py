from abc import ABC, abstractmethod
from typing import Set

from . import CentralBank
from .balance_entries import *


class EuroEconomy(ABC):

    @classmethod
    def from_central_bank(cls, central_bank: CentralBank):
        return EuroEconomy({central_bank})

    def __init__(self, central_banks: Set[CentralBank]):
        self.__central_banks: Set[CentralBank] = set(central_banks)
        self.growth_rate: float = 0.014
        self.inflation: float = 0.019
        self.mbs_growth: float = 0.0
        self.security_growth: float = 0.0
        self.lending_satisfaction_rate = 1.0

    @property
    @abstractmethod
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
            central_bank.inflate(self.inflation)

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

    def process_borrowing(self, amount: float):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                for client in bank.clients:
                    client.borrow(amount)

    def update_reserves(self):
        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                bank.update_reserves()

    @property
    def im(self) -> float:
        im: float = 0.0

        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                im += bank.liability(DEPOSITS)
                im += bank.liability(SAVINGS)

        return im

    @property
    def private_debt(self) -> float:
        debt: float = 0.0

        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                for client in bank.clients:
                    debt += client.liability(DEBT)

        return debt

    @property
    def bank_debt(self) -> float:
        debt: float = 0.0

        for central_bank in self.central_banks:
            for bank in central_bank.registered_banks:
                debt += bank.liability(DEBT)

        return debt

    @property
    @abstractmethod
    def nominal_growth(self) -> float:
        pass

    @property
    @abstractmethod
    def real_growth(self) -> float:
        pass

    @abstractmethod
    def get_required_lending(self, target_im: float):
        pass