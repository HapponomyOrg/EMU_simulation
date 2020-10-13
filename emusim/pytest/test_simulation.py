from decimal import *

from emusim.cockpit.supply import DataCollector
from emusim.cockpit.supply.euro import AggregateSimulator, AggregateEconomy,\
    SimpleDataGenerator,SpendingMode
from emusim.cockpit.supply.euro.aggregate_simulator import PERCENTAGE_FIELDS, SYSTEM_DATA_FIELDS, SYSTEM, IM, \
    DEFLATED_IM, REAL_GROWTH
from emusim.cockpit.utilities.cycles import Period, Interval

economy: AggregateEconomy = AggregateEconomy()
generator: SimpleDataGenerator = SimpleDataGenerator(economy)
simulator: AggregateSimulator = AggregateSimulator(economy, generator)
collector: DataCollector = simulator.collector


def dump_data(file_name: str):
    file = open(file_name + ".csv", "w")

    for category in collector.get_categories():
        for data_field in collector.get_data_fields(category):
            file.write(category)
            file.write("," + data_field)

            year: Period = Period(1, Interval.YEAR)
            cycle: int = 0
            for data in collector.get_data_series(category, data_field):
                if year.period_complete(cycle):
                    if data_field in PERCENTAGE_FIELDS:
                        data *= 100

                    file.write("," + str(round(data, 2)))
                cycle += 1
            file.write("\n")
    file.close()


def test_no_growth():
    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    collector.set_collect_data(SYSTEM, IM, True)
    collector.set_collect_data(SYSTEM, DEFLATED_IM, True)

    simulator.economy.growth_rate = 0.0

    simulator.run_simulation(50 * Period.YEAR_DAYS)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert real_growth == 0.0

    for deflated_im in collector.get_data_series(SYSTEM, DEFLATED_IM):
        assert deflated_im == 1000000.0

    dump_data("data/no_growth")


def test_growth_no_save_no_profit():
    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    simulator.economy.growth_rate = 0.025 * Period.YEAR_DAYS
    simulator.economy.bank.income_from_interest = 1.0
    simulator.economy.bank.spending_mode = SpendingMode.PROFIT
    simulator.economy.bank.retain_profit = False
    simulator.economy.bank.profit_spending = 1.0
    simulator.economy.client.savings_rate = 0.0

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    simulator.run_simulation(100)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert round(real_growth, 3) == round(Decimal(0.025), 3)


def test_growth_save():
    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    simulator.economy.growth_rate = 0.03

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    simulator.run_simulation(50 * Period.YEAR_DAYS)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert round(real_growth, 8) == round(Decimal(0.03 / Period.YEAR_DAYS), 8)


def test_no_growth_no_inflation_save():
    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    simulator.economy.growth_rate = 0.0
    simulator.economy.inflation = 0.0
    simulator.economy.client.savings_rate = 0.2

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    simulator.run_simulation(100)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert real_growth == 0.00


def test_no_growth_no_inflation_no_save():
    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    simulator.economy.growth_rate = 0.0
    simulator.economy.inflation = 0.0
    simulator.economy.client.savings_rate = 0.0

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    simulator.run_simulation(100)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert real_growth == 0.0


def test_growth_securities():
    economy.central_bank.clear()
    economy.start_transactions()
    economy.client.borrow(Decimal(1000000.0))
    economy.end_transactions()

    simulator.economy.growth_rate = 0.03 * Period.YEAR_DAYS
    simulator.economy.inflation = 0.019
    simulator.economy.central_bank.securities_relative_reserve = 0.03
    simulator.economy.central_bank.mbs_relative_reserve = 0.05
    simulator.economy.bank.min_risk_assets = 0.1
    simulator.economy.bank.max_risk_assets = 0.4
    simulator.economy.bank.max_mbs_assets = 0.8
    simulator.economy.bank.max_security_assets = 0.5

    for data_label in SYSTEM_DATA_FIELDS:
        collector.set_collect_data(SYSTEM, data_label, True)

    simulator.run_simulation(100)

    for real_growth in collector.get_data_series(SYSTEM, REAL_GROWTH):
        assert real_growth == 0.03