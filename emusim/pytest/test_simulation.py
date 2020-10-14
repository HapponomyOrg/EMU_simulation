from decimal import *

from emusim.cockpit.supply import DataCollector
from emusim.cockpit.supply.euro import AggregateSimulator, AggregateEconomy,QEMode,HelicopterMode,\
    SimpleDataGenerator, SpendingMode, DefaultingMode
from emusim.cockpit.supply.euro.aggregate_simulator import PERCENTAGE_FIELDS, SYSTEM_DATA_FIELDS, SYSTEM, INFLATION, \
    IM,REAL_GROWTH, REQUIRED_LENDING_RATE, BANK, PROFIT, CENTRAL_BANK_BS, BANK_BS, PRIVATE_SECTOR_BS
from emusim.cockpit.utilities.cycles import Period, Interval

economy: AggregateEconomy = AggregateEconomy()
generator: SimpleDataGenerator = SimpleDataGenerator(economy)
simulator: AggregateSimulator = AggregateSimulator(economy, generator)
collector: DataCollector = simulator.collector


def set_default_parameters():
    # economy
    economy.cycle_length = Period(1, Interval.DAY)
    economy.growth_rate = 0.03
    economy.inflation = 0.019
    economy.mbs_growth = 0.0
    economy.security_growth = 0.0
    economy.lending_satisfaction_rate = 1.0

    # central bank
    economy.central_bank.min_reserve = 0.04
    economy.central_bank.mbs_relative_reserve = 0.0
    economy.central_bank.securities_relative_reserve = 0.0
    economy.central_bank.reserve_ir = 0.0
    economy.central_bank.surplus_reserve_ir = -0.005 * Period.YEAR_DAYS
    economy.central_bank.reserve_interest_interval = Period(1, Interval.DAY)
    economy.central_bank.loan_ir = 0.01 * Period.YEAR_DAYS
    economy.central_bank.loan_duration = Period(1, Interval.DAY)
    economy.central_bank.loan_interval = Period(1, Interval.DAY)
    economy.central_bank.qe_mode = QEMode.NONE
    economy.central_bank.qe_interval = Period(1, Interval.MONTH)
    economy.central_bank.helicopter_mode = HelicopterMode.NONE
    economy.central_bank.helicopter_interval = Period(1, Interval.MONTH)

    # bank
    economy.bank.min_reserve = 0.04
    economy.bank.min_risk_assets = 0.0
    economy.bank.min_risk_assets = 0.0
    economy.bank.max_mbs_assets = 1.0
    economy.bank.max_security_assets = 1.0
    economy.bank.savings_ir = 0.011 * Period.YEAR_DAYS
    economy.bank.savings_interval = Period(1, Interval.DAY)
    economy.bank.loan_ir = 0.025 * Period.YEAR_DAYS
    economy.bank.loan_duration = Period(20, Interval.DAY)
    economy.bank.loan_interval = Period(1, Interval.DAY)
    economy.bank.no_loss = True
    economy.bank.income_from_interest = 0.2
    economy.bank.retain_profit = True
    economy.bank.retain_profit_percentage = 0.2
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 0.8

    # private sector
    economy.client.savings_rate = 0.2
    economy.client.borrow_for_securities = 0.0
    economy.client.defaulting_mode = DefaultingMode.NONE


def init_collector():
    collector.clear()

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    # Central bank balance sheet
    for asset in economy.central_bank.asset_names:
        collector.set_collect_data(CENTRAL_BANK_BS, asset, True)

    for liability in economy.central_bank.liability_names:
        collector.set_collect_data(CENTRAL_BANK_BS, liability, True)

    # Bank balance sheet
    for asset in economy.bank.asset_names:
        collector.set_collect_data(BANK_BS, asset, True)

    for liability in economy.bank.liability_names:
        collector.set_collect_data(BANK_BS, liability, True)

    # Private sector balance sheet
    for asset in economy.client.asset_names:
        collector.set_collect_data(PRIVATE_SECTOR_BS, asset, True)

    for liability in economy.client.liability_names:
        collector.set_collect_data(PRIVATE_SECTOR_BS, liability, True)

    collector.set_collect_data(BANK, PROFIT, True)


def test_no_growth_no_save_no_profit():
    init_collector()
    set_default_parameters()

    simulator.economy.growth_rate = 0.0
    simulator.economy.inflation = 0.019
    simulator.economy.bank.income_from_interest = 1.0
    simulator.economy.bank.spending_mode = SpendingMode.PROFIT
    simulator.economy.bank.retain_profit = False
    simulator.economy.bank.profit_spending = 1.0
    simulator.economy.client.savings_rate = 0.0

    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    init_collector()
    simulator.run_simulation(Period.YEAR_DAYS)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert real_growth == 0.0

    for inflation in collector.get_data_series(SYSTEM, INFLATION):
        assert inflation == round(Decimal(0.019 / Period.YEAR_DAYS), 8)

    for deflated_im in collector.get_data_series(SYSTEM, IM):
        assert deflated_im == 1000000.0


def test_growth_save():
    init_collector()
    set_default_parameters()

    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    simulator.run_simulation(Period.YEAR_DAYS)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert round(real_growth, 8) == round(Decimal(0.03 / Period.YEAR_DAYS), 8)


def test_growth_securities():
    init_collector()
    set_default_parameters()
    simulator.economy.growth_rate = 0.03 * Period.YEAR_DAYS
    simulator.economy.central_bank.securities_relative_reserve = 0.03
    simulator.economy.central_bank.mbs_relative_reserve = 0.05
    simulator.economy.bank.min_risk_assets = 0.1
    simulator.economy.bank.max_risk_assets = 0.4
    simulator.economy.bank.max_mbs_assets = 0.8
    simulator.economy.bank.max_security_assets = 0.5

    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    simulator.run_simulation(Period.YEAR_DAYS)

    cycle: int = 0
    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        if cycle > 5: # allow for simulation to stabilize
            assert round(real_growth, 2) == round(Decimal(0.03), 2)

        cycle += 1