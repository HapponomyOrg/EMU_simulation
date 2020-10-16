from __future__ import annotations

from decimal import *
from typing import TYPE_CHECKING, List

from . import EuroEconomy, CentralBank, Bank, PrivateActor
from .. import Simulator, DataGenerator

if TYPE_CHECKING:
    from . import EconomicActor

# System category
SYSTEM: str = "System"

# System data fields
CYCLE = "Cycle"
GROWTH_TARGET = "Growth target"
INFLATION = "Inflation"
IM = "IM"
IM_TARGET = "IM target"
NOMINAL_GROWTH = "Nominal growth"
REAL_GROWTH = "Real growth"
MBS_GROWTH = "MBS growth"
SECURITY_GROWTH = "Security growth"
LENDING_SATISFACTION = "Lending satisfaction rate"
LENDING = "Lending"
REQUIRED_LENDING = "Required lending"
REQUIRED_LENDING_RATE = "Required lending rate"
LENDING_RATE = "Lending rate"

SYSTEM_OBLIGATORY_DATA_FIELDS = [CYCLE,
                                 GROWTH_TARGET,
                                 INFLATION,
                                 REAL_GROWTH,
                                 REQUIRED_LENDING_RATE,
                                 LENDING_RATE]

SYSTEM_DATA_FIELDS = [CYCLE,
                      IM,
                      IM_TARGET,
                      NOMINAL_GROWTH,
                      MBS_GROWTH,
                      SECURITY_GROWTH,
                      LENDING_SATISFACTION,
                      REQUIRED_LENDING,
                      LENDING]

# Central bank category
CENTRAL_BANK = "Central bank"

# Central bank data fields
MIN_RESERVE = "Minimal reserve"
MBS_RESERVE = "MBS reserve"
SECURITIES_RESERVE = "Securities reserve"
RESERVE_IR = "Reserve interest rate"
SURPLUS_RESERVE_IR = "Surplus reserve interest rate"
BANK_LOAN_IR = "Bank loan interest rate"
BANK_LOAN_DURATION = "Bank loan duration"
QE = "QE"

CENTRAL_BANK_DATA_FIELDS = [MIN_RESERVE, MBS_RESERVE, SECURITIES_RESERVE, RESERVE_IR, SURPLUS_RESERVE_IR,
                            BANK_LOAN_IR, BANK_LOAN_DURATION, QE]

PERCENTAGE_FIELDS = [GROWTH_TARGET, INFLATION, NOMINAL_GROWTH, REAL_GROWTH, MBS_GROWTH, SECURITY_GROWTH,
                     REQUIRED_LENDING_RATE, LENDING_RATE, LENDING_SATISFACTION, MIN_RESERVE, MBS_RESERVE,
                     SECURITIES_RESERVE, RESERVE_IR, SURPLUS_RESERVE_IR, BANK_LOAN_IR]

DEFLATABLE_FIELDS = [IM, IM_TARGET, LENDING, REQUIRED_LENDING]

# Bank category
BANK = "Bank"

# Bank data fields
SAVINGS_IR = "Savings interest rate"
LOAN_IR = "Private loan interest rate"
LOAN_DURATION = "Private loan duration"
SPENDING = "Spending"
PROFIT = "Profit"
INCOME = "Income"
INSTALLMENT = "INSTALLMENT"

BANK_STATIC_DATA_FIELDS = [MIN_RESERVE, SAVINGS_IR, LOAN_IR, LOAN_DURATION]
BANK_DATA_FIELDS = [INCOME, SPENDING, PROFIT, INSTALLMENT]

# Balance sheet categories
CENTRAL_BANK_BS: str = "Central bank balance sheet"
BANK_BS: str = "Bank balance sheet"
PRIVATE_SECTOR_BS = "Private sector balance sheet"

BALANCE_SHEET_CATEGORIES = [CENTRAL_BANK_BS, BANK_BS, PRIVATE_SECTOR_BS]


class SimpleDataGenerator(DataGenerator):

    def __init__(self, economy: EuroEconomy):
        self.__economy = economy
        self.__growth_influence_rate: Decimal = Decimal(0.0)

    @property
    def growth_influence_rate(self) -> Decimal:
        return self.__growth_influence_rate

    @growth_influence_rate.setter
    def growth_influence_rate(self, rate: Decimal):
        self.__growth_influence_rate = Decimal(rate)

    def generate_next(self):
        inflation: Decimal = self.data_collector.get_data_series(SYSTEM, INFLATION)[-1]
        real_growth: Decimal = self.data_collector.get_data_series(SYSTEM, REAL_GROWTH)[-1]
        self.__economy.inflation += round(self.__economy.inflation * real_growth * self.growth_influence_rate, 8)


class AggregateSimulator(Simulator):
    # the structure of the data and whether or not it needs to be collected

    def __init__(self, economy: EuroEconomy, generator: DataGenerator):
        self.__economy: EuroEconomy = economy
        self.__desired_im: Decimal = Decimal(0.0) # im if growth_target is maintained
        self.__start_im: Decimal = Decimal(0.0)
        self.__target_im: Decimal = Decimal(0.0)
        self.__nominal_growth = Decimal(0.0)
        self.__real_growth = Decimal(0.0)
        self.__required_lending: Decimal = Decimal(0.0)
        self.__lending: Decimal = Decimal(0.0)
        self.__required_lending_rate: Decimal = Decimal(0.0)
        self.__lending_rate:Decimal = Decimal(0.0)

        super().__init__(generator)
        self.generator.data_collector = self.collector

    def _initialize_data_structure(self):
        for data_field in SYSTEM_OBLIGATORY_DATA_FIELDS:
            self.collector.set_collect_data(SYSTEM, data_field, True)

        for data_field in SYSTEM_DATA_FIELDS:
            self.collector.set_collect_data(SYSTEM, data_field, False)

        for data_field in CENTRAL_BANK_DATA_FIELDS:
            self.collector.set_collect_data(CENTRAL_BANK, data_field, False)

        for data_field in BANK_DATA_FIELDS:
            self.collector.set_collect_data(BANK, data_field, False)

        # Central bank balance sheet
        for asset in self.economy.central_bank.asset_names:
            self.collector.set_collect_data(CENTRAL_BANK_BS, asset, False)

        for liability in self.economy.central_bank.liability_names:
            self.collector.set_collect_data(CENTRAL_BANK_BS, liability, False)

        # Bank balance sheet
        for asset in self.economy.bank.asset_names:
            self.collector.set_collect_data(BANK_BS, asset, False)

        for liability in self.economy.bank.liability_names:
            self.collector.set_collect_data(BANK_BS, liability, False)

        # Private sector balance sheet
        for asset in self.economy.client.asset_names:
            self.collector.set_collect_data(PRIVATE_SECTOR_BS, asset, False)

        for liability in self.economy.client.liability_names:
            self.collector.set_collect_data(PRIVATE_SECTOR_BS, liability, False)

    @property
    def economy(self) -> EuroEconomy:
        return self.__economy

    def data(self, category: str, data_field: str) -> Decimal:
        data: Decimal = Decimal(0.0)

        if category == SYSTEM:
            if data_field == CYCLE:
                data = Decimal(self.economy.central_bank.cycle)
            elif data_field == GROWTH_TARGET:
                data = self.economy.cycle_growth_rate
            elif data_field == REAL_GROWTH:
                data = self.__real_growth
            elif data_field == NOMINAL_GROWTH:
                data = self.__nominal_growth
            elif data_field == MBS_GROWTH:
                data = self.economy.mbs_growth
            elif data_field == SECURITY_GROWTH:
                data = self.economy.security_growth
            elif data_field == INFLATION:
                data = self.economy.cycle_inflation_rate
            elif data_field == IM:
                data = self.economy.im
            elif data_field == IM_TARGET:
                data = self.__target_im
            elif data_field == LENDING_SATISFACTION:
                data = self.economy.lending_satisfaction_rate
            elif data_field == REQUIRED_LENDING:
                data = self.__required_lending
            elif data_field == LENDING:
                data = self.__lending
            elif data_field == REQUIRED_LENDING_RATE:
                data = self.__required_lending_rate
            elif data_field == LENDING_RATE:
                data = self.__lending_rate
        elif category == CENTRAL_BANK:
            data = Decimal(0.0)
        elif category == BANK:
            if data_field == INCOME:
                data = self.economy.bank.income
            elif data_field == SPENDING:
                data = self.economy.bank.spending
            elif data_field == PROFIT:
                data = self.economy.bank.profit
            elif data_field == INSTALLMENT:
                data = self.economy.bank.client_installment
        elif category == CENTRAL_BANK_BS:
            data = self.__balance_entry(self.economy.central_bank, data_field)
        elif category == BANK_BS:
            data = self.__balance_entry(self.economy.bank, data_field)
        elif category == PRIVATE_SECTOR_BS:
            data = self.__balance_entry(self.economy.client, data_field)

        if data_field in DEFLATABLE_FIELDS or category in BALANCE_SHEET_CATEGORIES:
            data = self.deflate(data, True)

        if data_field in PERCENTAGE_FIELDS:
            return round(Decimal(data), 8)
        else:
            return round(Decimal(data), 4)

    def __balance_entry(self, economic_actor: EconomicActor, entry: str) -> Decimal:
        if entry in economic_actor.asset_names:
            data = economic_actor.asset(entry)
        else:
            data = economic_actor.liability(entry)

        return data

    def collect_data(self):
        self.collector.collect_data()

        self.__collect_balance_data(CENTRAL_BANK_BS, self.economy.central_bank)
        self.__collect_balance_data(BANK_BS, self.economy.central_bank.bank)
        self.__collect_balance_data(PRIVATE_SECTOR_BS, self.economy.central_bank.bank.client)

    def __collect_balance_data(self, category: str, actor: EconomicActor):
        for asset_name in actor.asset_names:
            self.collector.add_data(category, asset_name, actor.asset(asset_name))

        for liability_name in actor.liability_names:
            self.collector.add_data(category, liability_name, actor.liability(liability_name))

    def process_cycle(self, cycle: int) -> bool:
        """Process a full cycle.

        :param cycle The current cycle number.

        :return True if all balance sheets validate and IM > 0."""
        self.__start_im = self.economy.im

        # grow im for optimal scenario where growth_target is always achieved
        if cycle == 0:
            self.__desired_im = self.__start_im

        self.__desired_im += round(self.__desired_im * self.economy.cycle_growth_rate, 8)

        # set target im for end of cycle
        self.__target_im = self.economy.im
        self.__target_im += round(self.__target_im * self.economy.cycle_growth_rate, 8)

        # process inflation
        self.economy.start_transactions()
        self.economy.inflate()
        self.__desired_im += round(self.__desired_im * self.economy.cycle_inflation_rate, 8)
        self.__target_im += round(self.__target_im * self.economy.cycle_inflation_rate, 8)

        # There is a possibility that target_im > desired_im due to banks buying securities at the start of the sim
        self.__target_im = min(self.__desired_im, self.__target_im)

        # reflect impact of price changes in securities
        self.economy.grow_securities()
        self.economy.grow_mbs()
        self.economy.update_risk_assets()

        # process QE and helicopter money
        self.economy.process_qe()
        self.economy.process_helicopter_money()

        self.economy.process_savings()
        self.economy.process_bank_income()
        self.economy.process_bank_loans()
        self.economy.process_bank_spending()

        self.__required_lending = Decimal(max(self.__target_im - self.economy.im, 0.0))
        self.__lending = round(Decimal(max(self.__required_lending * self.economy.lending_satisfaction_rate, 0.0)), 8)

        # calculate required and real lending percentages
        if self.economy.im > 0.0:
            self.__required_lending_rate = round(self.__required_lending / self.economy.im, 8)
            self.__lending_rate = round(self.__lending / self.economy.im, 8)
        else:
            self.__required_lending_rate = Decimal('Infinity')
            self.__lending_rate = Decimal('Infinity')

        self.economy.process_borrowing(self.__lending)
        self.economy.update_reserves()

        self.__nominal_growth = round((self.economy.im - self.__start_im) / self.__start_im, 8)

        deflated_start_im: Decimal = self.deflate(self.__start_im, True)
        deflated_im: Decimal = self.deflate(self.economy.im)
        self.__real_growth = round((deflated_im - deflated_start_im) / deflated_start_im, 8)

        return self.economy.end_transactions()\
               and self.economy.im > 0\
               and self.__required_lending_rate != Decimal('Infinity')

    # only call after initial_inflation_rate has been applied in a cycle
    def deflate(self, amount: Decimal, skip_one: bool = False) -> Decimal:
        inflation_rates: List[Decimal] = self.collector.get_data_series(SYSTEM, INFLATION)

        if not skip_one:
            amount /= 1 + self.economy.cycle_inflation_rate

        for inflation in inflation_rates:
            amount /= 1 + inflation

        return round(Decimal(amount), 10)
