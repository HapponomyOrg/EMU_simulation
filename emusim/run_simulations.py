from decimal import *
from datetime import datetime

from emusim.cockpit.supply import DataCollector
from emusim.cockpit.supply.euro import AggregateSimulator, EuroEconomy,QEMode,HelicopterMode,\
    SimpleDataGenerator, SpendingMode, DefaultingMode, BalanceEntries, Bank, PrivateActor
from emusim.cockpit.supply.euro.aggregate_simulator import PERCENTAGE_FIELDS, SYSTEM_DATA_FIELDS, SYSTEM, \
    CYCLE, REAL_GROWTH, DEBT_RATIO, REQUIRED_LENDING,REQUIRED_LENDING_RATE, BANK, BANK_DATA_FIELDS, CENTRAL_BANK_BS, BANK_BS, \
    PRIVATE_SECTOR_BS
from emusim.cockpit.utilities.cycles import Period, Interval

economy: EuroEconomy
generator: SimpleDataGenerator
simulator: AggregateSimulator
collector: DataCollector

YEARS: int = 100

def reset():
    global economy
    global generator
    global simulator
    global collector

    economy = EuroEconomy()
    generator = SimpleDataGenerator(economy)
    simulator = AggregateSimulator(economy, generator)
    collector = simulator.collector


def set_no_sec_parameters():
    reset()

    # simulator
    simulator.collect_interval = Period(1, Interval.MONTH)

    # economy
    economy.cycle_length = Period(1, Interval.DAY)
    economy.growth_rate = 0.03
    economy.inflation = 0.0
    economy.mbs_growth = 0.0
    economy.security_growth = 0.0
    economy.lending_satisfaction_rate = 1.0

    # central bank
    economy.central_bank.min_reserve = 0.01
    economy.central_bank.mbs_relative_reserve = 0.0
    economy.central_bank.securities_relative_reserve = 0.0
    economy.central_bank.reserve_ir = 0.0
    economy.central_bank.surplus_reserve_ir = -0.005
    economy.central_bank.reserve_interest_interval = Period(1, Interval.DAY)
    economy.central_bank.loan_ir = 0.0025
    economy.central_bank.loan_duration = Period(1, Interval.DAY)
    economy.central_bank.loan_interval = Period(1, Interval.DAY)
    economy.central_bank.qe_mode = QEMode.NONE
    economy.central_bank.qe_interval = Period(1, Interval.MONTH)
    economy.central_bank.helicopter_mode = HelicopterMode.NONE
    economy.central_bank.helicopter_interval = Period(1, Interval.MONTH)

    # bank
    economy.bank.min_reserve = 0.01
    economy.bank.reserves_interval = Period(1, Interval.DAY)
    economy.bank.min_risk_assets = 0.0
    economy.bank.max_risk_assets = 0.0
    economy.bank.max_mbs_assets = 1.0
    economy.bank.max_security_assets = 1.0
    economy.bank.client_interaction_interval = Period(1, Interval.MONTH)
    economy.bank.savings_ir = 0.0
    economy.bank.loan_ir = 0.025
    economy.bank.loan_duration = Period(20, Interval.YEAR)
    economy.bank.no_loss = True
    economy.bank.income_from_interest = 0.2
    economy.bank.retain_profit_percentage = 0.2
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 0.8

    # private sector
    economy.client.savings_rate = 0.0
    economy.client.borrow_for_securities = 0.0
    economy.client.defaulting_mode = DefaultingMode.NONE


def set_sec_parameters():
    set_no_sec_parameters()

    economy.central_bank.mbs_relative_reserve = 0.0
    economy.central_bank.securities_relative_reserve = 0.05

    economy.bank.min_risk_assets = 0.1
    economy.bank.max_risk_assets = 0.4
    economy.bank.max_mbs_assets = 0.0
    economy.bank.max_security_assets = 1.0


def init_collector():
    collector.set_collect_data(SYSTEM, CYCLE, True)
    collector.set_collect_data(SYSTEM, REAL_GROWTH, True)
    collector.set_collect_data(SYSTEM, DEBT_RATIO, True)
    collector.set_collect_data(SYSTEM, REQUIRED_LENDING, True)
    collector.set_collect_data(SYSTEM, REQUIRED_LENDING_RATE, True)
    collector.set_collect_data(BANK_BS, BalanceEntries.EQUITY, True)
    collector.set_collect_data(PRIVATE_SECTOR_BS, BalanceEntries.EQUITY, True)

    # for data_label in SYSTEM_DATA_FIELDS:
    #     collector.set_collect_data(SYSTEM, data_label, True)
    #
    # for data_label in BANK_DATA_FIELDS:
    #     collector.set_collect_data(BANK, data_label, True)
    #
    # # Central bank balance sheet
    # for asset in economy.central_bank.asset_names:
    #     collector.set_collect_data(CENTRAL_BANK_BS, asset, True)
    #
    # for liability in economy.central_bank.liability_names:
    #     collector.set_collect_data(CENTRAL_BANK_BS, liability, True)
    #
    # # Bank balance sheet
    # for asset in economy.bank.asset_names:
    #     collector.set_collect_data(BANK_BS, asset, True)
    #
    # for liability in economy.bank.liability_names:
    #     collector.set_collect_data(BANK_BS, liability, True)
    #
    # # Private sector balance sheet
    # for asset in economy.client.asset_names:
    #     collector.set_collect_data(PRIVATE_SECTOR_BS, asset, True)
    #
    # for liability in economy.client.liability_names:
    #     collector.set_collect_data(PRIVATE_SECTOR_BS, liability, True)


# debt percentage of money stock
def init_bank_balance(debt):
    bank: Bank = economy.bank
    client: PrivateActor = economy.client

    bank.set_asset(BalanceEntries.RESERVES, Decimal(1000000.0 * (1 - debt)) * economy.central_bank.min_reserve)
    bank.set_liability(BalanceEntries.DEPOSITS, Decimal(1000000.0 * (1 - debt)))
    bank.set_liability(BalanceEntries.EQUITY,
                       bank.balance.assets_value - bank.liability(BalanceEntries.DEPOSITS)
                       - bank.liability(BalanceEntries.DEBT))
    client.set_asset(BalanceEntries.DEPOSITS, Decimal(1000000.0 * (1 - debt)))
    client.set_liability(BalanceEntries.EQUITY, client.balance.assets_value - client.liability(BalanceEntries.DEBT))

    client.borrow(Decimal(1000000.0 * debt))
    bank.update_reserves(True)
    bank.update_risk_assets()

    assert bank.balance.validate()
    assert client.balance.validate()


def dump_data(file_name: str):
    file_name = sec_no_sec + " - " + file_name
    file = open("data/" + file_name + ".csv", "w")

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

                    if data_field == CYCLE:
                        file.write(str(round(data, 0)))
                    elif data.is_finite():
                        try:
                            file.write(str(round(data, 4)))
                        except Exception:
                            file.write(str(data))
                    else:
                        file.write(str(data))
                else:
                    first_column = False

            if data_field == CYCLE:
                print(file_name
                      + ": "
                      + str(round(collector.get_data_series(category, data_field)[-1] / Period.YEAR_DAYS, 2)))

            file.write("\n")
    file.close()


def run_base_high_growth(param_initialization, debt):
    param_initialization()

    economy.growth_rate = 0.1

    # central bank
    economy.central_bank.min_reserve = 0.01
    economy.central_bank.surplus_reserve_ir = 0.0
    economy.central_bank.loan_ir = 0.0

    # bank
    economy.bank.min_reserve = 0.0
    economy.bank.loan_ir = 0.0
    economy.bank.income_from_interest = 1.0
    economy.bank.retain_profit_percentage = 0.0
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 1

    economy.central_bank.clear()
    init_bank_balance(debt)
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("base_high_growth")


def run_base_low_growth(param_initialization, debt):
    param_initialization()

    economy.growth_rate = 0.03

    # central bank
    economy.central_bank.min_reserve = 0.0
    economy.central_bank.surplus_reserve_ir = 0.0
    economy.central_bank.loan_ir = 0.0

    # bank
    economy.bank.min_reserve = 0.0
    economy.bank.loan_ir = 0.0
    economy.bank.income_from_interest = 1.0
    economy.bank.retain_profit_percentage = 0.0
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 1

    economy.central_bank.clear()
    init_bank_balance(debt)
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("base_low_growth")


def run_long_base_low_growth(param_initialization, debt):
    param_initialization()

    economy.growth_rate = 0.03

    # central bank
    economy.central_bank.min_reserve = 0.0
    economy.central_bank.surplus_reserve_ir = 0.0
    economy.central_bank.loan_ir = 0.0

    # bank
    economy.bank.min_reserve = 0.0
    economy.bank.loan_ir = 0.0
    economy.bank.income_from_interest = 1.0
    economy.bank.retain_profit_percentage = 0.0
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 1

    economy.central_bank.clear()
    init_bank_balance(debt)
    init_collector()
    simulator.run_simulation(500 * Period.YEAR_DAYS)

    dump_data("long_base_low_growth")


def run_base_no_growth(param_initialization, debt):
    param_initialization()

    economy.growth_rate = 0.0

    # central bank
    economy.central_bank.min_reserve = 0.0
    economy.central_bank.surplus_reserve_ir = 0.0
    economy.central_bank.loan_ir = 0.0

    # bank
    economy.bank.min_reserve = 0.0
    economy.bank.loan_ir = 0.0
    economy.bank.income_from_interest = 1.0
    economy.bank.retain_profit_percentage = 0.0
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 1

    economy.central_bank.clear()
    init_bank_balance(debt)
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("base_no_growth")


def run_no_growth(param_initialization, debt):
    param_initialization()

    simulator.economy.growth_rate = 0.0

    # central bank
    economy.central_bank.min_reserve = 0.0
    economy.central_bank.surplus_reserve_ir = 0.0
    economy.central_bank.loan_ir = 0.0

    # bank
    economy.bank.min_reserve = 0.0
    economy.bank.loan_ir = 0.025
    economy.bank.income_from_interest = 1.0
    economy.bank.retain_profit_percentage = 1.0
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 0.0

    economy.lending_satisfaction_rate = 1

    economy.central_bank.clear()
    init_bank_balance(debt)
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("no_growth")


def run_equal_growth_interest(param_initialization, debt):
    param_initialization()

    simulator.economy.growth_rate = 0.025

    # central bank
    economy.central_bank.min_reserve = 0.0
    economy.central_bank.surplus_reserve_ir = 0.0
    economy.central_bank.loan_ir = 0.0

    # bank
    economy.bank.min_reserve = 0.0
    economy.bank.loan_ir = 0.025
    economy.bank.income_from_interest = 1.0
    economy.bank.retain_profit_percentage = 1.0
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 0.0

    economy.lending_satisfaction_rate = 0.95

    economy.central_bank.clear()
    init_bank_balance(debt)
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("equal_growth_interest - 95%")


def run_high_growth(param_initialization, debt):
    param_initialization()

    simulator.economy.growth_rate = 0.1

    # central bank
    economy.central_bank.min_reserve = 0.0
    economy.central_bank.surplus_reserve_ir = 0.0
    economy.central_bank.loan_ir = 0.0

    # bank
    economy.lending_satisfaction_rate = 1
    economy.bank.min_reserve = 0.0
    economy.bank.loan_ir = 0.025
    economy.bank.income_from_interest = 1.0
    economy.bank.retain_profit_percentage = 1.0
    economy.bank.spending_mode = SpendingMode.PROFIT
    economy.bank.profit_spending = 0.0

    economy.central_bank.clear()
    init_bank_balance(debt)
    init_collector()
    simulator.run_simulation(YEARS * Period.YEAR_DAYS)

    dump_data("high_growth")


def run_batch(param_initialization, initial_debt):
    # run_base_no_growth(param_initialization, initial_debt)
    # run_no_growth(param_initialization, initial_debt)
    #
    # run_base_low_growth(param_initialization, initial_debt)
    # run_long_base_low_growth(param_initialization, initial_debt)
    #
    # run_base_high_growth(param_initialization, initial_debt)
    # run_high_growth(param_initialization, initial_debt)

    run_equal_growth_interest(param_initialization, initial_debt)

now = datetime.now()
print("Starting")

# sec_no_sec: str = "debt = 0.1"
# run_batch(set_no_sec_parameters, 0.1)
#
# sec_no_sec: str = "debt = 0.5"
# run_batch(set_no_sec_parameters, 0.5)

sec_no_sec: str = "debt = 0.9"
run_batch(set_no_sec_parameters, 0.9)

# sec_no_sec = "sec"
# run_batch(set_sec_parameters)
print("Done: " + str(datetime.now() - now))

