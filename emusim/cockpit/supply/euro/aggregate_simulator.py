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
GROWTH_TARGET = "Growth target"
INFLATION = "Inflation"
IM = "IM"
IM_TARGET = "IM target"
DEFLATED_IM = "Deflated IM"
DEFLATED_IM_TARGET = "Deflated IM target"
NOMINAL_GROWTH = "Nominal growth"
REAL_GROWTH = "Real growth"
MBS_GROWTH = "MBS growth"
SECURITY_GROWTH = "Security growth"
LENDING_SATISFACTION = "Lending satisfaction rate"
LENDING = "Lending"
REQUIRED_LENDING = "Required lending"
REQUIRED_LENDING_RATE = "Required lending rate"
LENDING_RATE = "Lending rate"
DEFLATED_LENDING = "Deflated lending"
DEFLATED_REQUIRED_LENDING = "Deflated required lending"

SYSTEM_OBLIGATORY_DATA_FIELDS = [GROWTH_TARGET,
                                 INFLATION,
                                 REAL_GROWTH,
                                 REQUIRED_LENDING_RATE,
                                 LENDING_RATE]

SYSTEM_DATA_FIELDS = [IM,
                      IM_TARGET,
                      NOMINAL_GROWTH,
                      MBS_GROWTH,
                      SECURITY_GROWTH,
                      LENDING_SATISFACTION,
                      REQUIRED_LENDING,
                      LENDING,
                      DEFLATED_REQUIRED_LENDING,
                      DEFLATED_LENDING]

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

# Bank category
BANK = "Bank"

# Bank data fields
MAX_RESERVE = "Max reserve"
SAVINGS_IR = "Savings interest rate"
LOAN_IR = "Private loan interest rate"
LOAN_DURATION = "Private loan duration"
SPENDING = "Spending"
PROFIT = "Profit"

BANK_DATA_FIELDS = [MAX_RESERVE, SAVINGS_IR, LOAN_IR, LOAN_DURATION, SPENDING, PROFIT]

# Balance sheet categories
CENTRAL_BANK_BS: str = "Central bank balance sheet"
BANK_BS: str = "Bank balance sheet"
PRIVATE_SECTOR_BS = "Private sector balance sheet"


class AggregateEconomy(EuroEconomy):

    def __init__(self):
        self.__central_bank: CentralBank = CentralBank()
        self.__bank: Bank = Bank(self.__central_bank)
        self.__client: PrivateActor = PrivateActor(self.__bank)

        super().__init__({self.__central_bank})

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def bank(self) -> Bank:
        return self.__bank

    @property
    def client(self) -> PrivateActor:
        return self.__client


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

    def __init__(self, economy: AggregateEconomy, generator: DataGenerator):
        self.__economy: AggregateEconomy = economy
        self.__desired_im: Decimal = Decimal(0.0) # im if growth_target is maintained
        self.__start_im: Decimal = Decimal(0.0)
        self.__target_im: Decimal = Decimal(0.0)
        self.__deflated_im = Decimal(0.0)
        self.__nominal_growth = Decimal(0.0)
        self.__real_growth = Decimal(0.0)
        self.__required_lending: Decimal = Decimal(0.0)
        self.__lending: Decimal = Decimal(0.0)
        self.__deflated_required_lending: Decimal = Decimal(0.0)
        self.__deflated_lending: Decimal = Decimal(0.0)
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
    def economy(self) -> AggregateEconomy:
        return self.__economy

    def data(self, category: str, data_field: str) -> Decimal:
        data: Decimal = Decimal(0.0)

        if category == SYSTEM:
            if data_field == GROWTH_TARGET:
                data = self.economy.cycle_growth_rate
            elif data_field == INFLATION:
                data = self.economy.cycle_inflation_rate
            elif data_field == IM:
                data = self.economy.im
            elif data_field == DEFLATED_IM:
                data = self.__deflated_im
            elif data_field == REAL_GROWTH:
                data = self.__real_growth
            elif data_field == REQUIRED_LENDING_RATE:
                data = self.__required_lending_rate
            elif data_field == LENDING_RATE:
                data = self.__lending_rate
            elif data_field == DEFLATED_REQUIRED_LENDING:
                data = self.__deflated_required_lending
        elif category == CENTRAL_BANK:
            data = Decimal(0.0)
        elif category == BANK:
            data = Decimal(0.0)

        return data

    def collect_data(self):
        self.collector.collect_data()

        for central_bank in self.economy.central_banks:
            self.__collect_balance_data(CENTRAL_BANK_BS, central_bank)

            for bank in central_bank.registered_banks:
                self.__collect_balance_data(BANK_BS, bank)

                for client in bank.clients:
                    self.__collect_balance_data(PRIVATE_SECTOR_BS, client)

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

        self.__desired_im += self.__desired_im * self.economy.cycle_growth_rate

        # set target im for end of cycle
        self.__target_im = self.economy.im
        self.__target_im += self.__target_im * self.economy.cycle_growth_rate

        # process inflation
        self.economy.start_transactions()
        self.economy.inflate()
        self.__desired_im += self.__desired_im * self.economy.cycle_inflation_rate
        self.__target_im += self.__target_im * self.economy.cycle_inflation_rate

        # reflect impact of price changes in securities
        self.economy.grow_securities()
        self.economy.grow_mbs()
        self.economy.update_risk_assets()

        # process QE and helicopter money
        self.economy.process_qe()
        self.economy.process_helicopter_money()

        self.economy.process_savings()
        self.economy.process_bank_income()
        self.economy.process_bank_spending()

        self.__required_lending = self.__target_im - self.economy.im
        self.__lending = self.__required_lending * self.economy.lending_satisfaction_rate

        self.__deflated_required_lending = self.deflate(self.__required_lending)
        self.__deflated_lending = self.deflate(self.__lending)

        # calculate required and real lending percentages
        self.__required_lending_rate = self.__required_lending / self.economy.im
        self.__lending_rate = self.__lending / self.economy.im

        self.economy.process_borrowing(self.__lending)
        self.economy.update_reserves()

        self.__nominal_growth = round((self.economy.im - self.__start_im) / self.__start_im, 8)

        self.__deflated_im = self.deflate(self.economy.im)
        deflated_start_im: Decimal = self.deflate(self.__start_im, True)
        self.__real_growth = round((self.__deflated_im - deflated_start_im) / deflated_start_im, 8)

        return self.economy.end_transactions() and self.economy.im > 0

    # only call after initial_inflation_rate has been applied in a cycle
    def deflate(self, amount: Decimal, skip_one: bool = False) -> Decimal:
        inflation_rates: List[Decimal] = self.collector.get_data_series(SYSTEM, INFLATION)

        if not skip_one:
            amount /= 1 + self.economy.cycle_inflation_rate

        for inflation in inflation_rates:
            amount /= 1 + inflation

        return round(Decimal(amount), 8)
