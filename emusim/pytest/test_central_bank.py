from emusim.cockpit.supply.euro import CentralBank


def test_creation():
    central_bank: CentralBank = CentralBank()

    central_bank.start_transactions()
    assert central_bank.end_transactions()
