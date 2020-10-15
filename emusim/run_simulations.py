from decimal import *
from datetime import datetime

from emusim.cockpit.supply import DataCollector
from emusim.cockpit.supply.euro import AggregateSimulator, AggregateEconomy,QEMode,HelicopterMode,\
    SimpleDataGenerator, SpendingMode, DefaultingMode
from emusim.cockpit.supply.euro.aggregate_simulator import PERCENTAGE_FIELDS, SYSTEM_DATA_FIELDS, SYSTEM, \
    CYCLE, BANK, PROFIT, CENTRAL_BANK_BS, BANK_BS, PRIVATE_SECTOR_BS
from emusim.cockpit.utilities.cycles import Period, Interval

economy: AggregateEconomy = AggregateEconomy()
generator: SimpleDataGenerator = SimpleDataGenerator(economy)
simulator: AggregateSimulator = AggregateSimulator(economy, generator)
collector: DataCollector = simulator.collector

YEARS: int = 100


def set_no_sec_parameters(do_print: bool = True):
    if do_print:
        print("initializing no sec")

    # simulator
    simulator.collect_interval = Period(1, Interval.MONTH)

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
    economy.central_bank.surplus_reserve_ir = -0.005
    economy.central_bank.reserve_interest_interval = Period(1, Interval.DAY)
    economy.central_bank.loan_ir = 0.01
    economy.central_bank.loan_duration = Period(3, Interval.DAY)
    economy.central_bank.loan_interval = Period(1, Interval.DAY)
    economy.central_bank.qe_mode = QEMode.NONE
    economy.central_bank.qe_interval = Period(1, Interval.MONTH)
    economy.central_bank.helicopter_mode = HelicopterMode.NONE
    economy.central_bank.helicopter_interval = Period(1, Interval.MONTH)

    # bank
    economy.bank.min_reserve = 0.04
    economy.bank.min_risk_assets = 0.0
    economy.bank.max_risk_assets = 0.0
    economy.bank.max_mbs_assets = 1.0
    economy.bank.max_security_assets = 1.0
    economy.bank.savings_ir = 0.011
    economy.bank.savings_interval = Period(1, Interval.DAY)
    economy.bank.loan_ir = 0.025
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


def set_sec_parameters():
    print("initializing sec")

    set_no_sec_parameters(False)

    economy.central_bank.mbs_relative_reserve = 0.1
    economy.central_bank.securities_relative_reserve = 0.05

    economy.bank.min_risk_assets = 0.1
    economy.bank.max_risk_assets = 0.4
    economy.bank.max_mbs_assets = 0.8
    economy.bank.max_security_assets = 0.4


def init_collector():
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


def dump_data(file_name: str):
    file = open("data/" + sec_no_sec + " - " + file_name + ".csv", "w")

    for category in collector.get_categories():
        for data_field in collector.get_data_fields(category):
            file.write(category + " - " + data_field)

            first_column: bool = True

            for data in collector.get_data_series(category, data_field):
                if not first_column:
                    if data_field == CYCLE:
                        data /= Period.MONTH_DAYS

                    if data_field in PERCENTAGE_FIELDS:
                        data *= 100

                    file.write(",")

                    if data.is_finite():
                        file.write(str(round(data, 4)))
                    else:
                        file.write(str(data))
                else:
                    first_column = False

            file.write("\n")
    file.close()


def run_no_growth_no_save_no_profit(param_initialization):
    param_initialization()

    simulator.economy.growth_rate = 0.0
    simulator.economy.bank.spending_mode = SpendingMode.PROFIT
    simulator.economy.bank.retain_profit = False
    simulator.economy.bank.profit_spending = 1.0
    simulator.economy.client.savings_rate = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("no_growth_no_save_no_profit")


def run_no_growth_no_inflation_no_save_no_profit(param_initialization):
    param_initialization()

    simulator.economy.growth_rate = 0.0
    simulator.economy.inflation = 0.0
    simulator.economy.bank.spending_mode = SpendingMode.PROFIT
    simulator.economy.bank.retain_profit = False
    simulator.economy.bank.profit_spending = 1.0
    simulator.economy.client.savings_rate = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("no_growth_no_inflation_no_save_no_profit")


def run_no_growth(param_initialization):
    param_initialization()

    simulator.economy.growth_rate = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("no_growth")


def run_no_growth_no_inflation(param_initialization):
    param_initialization()

    simulator.economy.growth_rate = 0.0
    simulator.economy.inflation = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("no_growth_no_inflation")


def run_low_growth_no_save_no_profit(param_initialization):
    param_initialization()

    simulator.economy.growth_rate = 0.01
    simulator.economy.bank.spending_mode = SpendingMode.PROFIT
    simulator.economy.bank.retain_profit = False
    simulator.economy.bank.profit_spending = 1.0
    simulator.economy.client.savings_rate = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("low_growth_no_save_no_profit")


def run_low_growth(param_initialization):
    param_initialization()

    simulator.economy.growth_rate = 0.01

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("low_growth")


def run_low_growth_no_inflation(param_initialization):
    param_initialization()

    simulator.economy.growth_rate = 0.01
    simulator.economy.inflation = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("low_growth_no_inflation")


def run_large_growth_no_save_no_profit(param_initialization):
    param_initialization()

    simulator.economy.bank.spending_mode = SpendingMode.PROFIT
    simulator.economy.bank.retain_profit = False
    simulator.economy.bank.profit_spending = 1.0
    simulator.economy.client.savings_rate = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("large_growth_no_save_no_profit")


def run_large_growth(param_initialization):
    param_initialization()

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))

    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("large_growth")


def run_large_growth_no_inflation(param_initialization):
    param_initialization()

    simulator.economy.inflation = 0.0

    economy.central_bank.clear()
    economy.client.borrow(Decimal(1000000.0))
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("large_growth_no_inflation")


def run_batch(param_initialization):
    run_no_growth_no_save_no_profit(param_initialization)
    run_no_growth_no_inflation_no_save_no_profit(param_initialization)
    run_no_growth(param_initialization)
    run_no_growth_no_inflation(param_initialization)

    run_low_growth_no_save_no_profit(param_initialization)
    run_low_growth(param_initialization)
    run_low_growth_no_inflation(param_initialization)

    run_large_growth_no_save_no_profit(param_initialization)
    run_large_growth(param_initialization)
    run_large_growth_no_inflation(param_initialization)


now = datetime.now()
print("Starting")
sec_no_sec: str = "no_sec"
run_batch(set_no_sec_parameters)
sec_no_sec = "sec"
run_batch(set_sec_parameters)
print("Done: " + str(datetime.now() - now))