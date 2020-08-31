from emusim.cockpit.supply.euro import CentralBank, Bank, PrivateActor
from emusim.cockpit.supply.euro.balance_entries import *

central_bank = CentralBank()
bank = Bank(central_bank)
client = PrivateActor(bank)


def test_pay_savings_interest():
    central_bank.clear()
