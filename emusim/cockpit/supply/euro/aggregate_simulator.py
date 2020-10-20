from __future__ import annotations

from decimal import *
from typing import TYPE_CHECKING, List

from . import EuroEconomy, BalanceEntries
from .. import Simulator, DataGenerator
from emusim.cockpit.utilities.cycles import Period, Interval

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
DEBT_RATIO = "Debt ratio"
SECURITIES_RATIO = "Securities ratio"

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
                      LENDING,
                      DEBT_RATIO,
                      SECURITIES_RATIO]

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
                     REQUIRED_LENDING_RATE, LENDING_RATE, DEBT_RATIO, SECURITIES_RATIO, LENDING_SATISFACTION, MIN_RESERVE,
                     MBS_RESERVE, SECURITIES_RESERVE, RESERVE_IR, SURPLUS_RESERVE_IR, BANK_LOAN_IR]

DEFLATABLE_FIELDS = [IM, IM_TARGET, LENDING, REQUIRED_LENDING]

# Bank category
BANK = "Bank"

# Bank data fields
SAVINGS_IR = "Savings interest rate"
LOAN_IR = "Private loan interest rate"
LOAN_DURATION = "Private loan duration"
INCOME = "Income"
COSTS = "Costs"
PROFIT = "Profit"
INSTALLMENT_RATIO = "Installment"

# Private sector
PRIVATE_SECTOR = "Private sector"
SAVINGS_RATE = "Savings rate"

BANK_STATIC_DATA_FIELDS = [MIN_RESERVE, SAVINGS_IR, LOAN_IR, LOAN_DURATION]
BANK_DATA_FIELDS = [INCOME, COSTS, PROFIT, INSTALLMENT_RATIO]

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
        self.__economy.inflation += self.__economy.inflation * real_growth * self.growth_influence_rate


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
        self.__lending_rate: Decimal = Decimal(0.0)
        self.__debt_ratio: Decimal = Decimal(0.0)
        self.__securities_ratio: Decimal = Decimal(0.0)

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
                data = self.economy.client_interval_growth_rate
            elif data_field == REAL_GROWTH:
                data = self.__real_growth
            elif data_field == NOMINAL_GROWTH:
                data = self.__nominal_growth
            elif data_field == MBS_GROWTH:
                data = self.economy.mbs_growth
            elif data_field == SECURITY_GROWTH:
                data = self.economy.security_growth
            elif data_field == INFLATION:
                data = self.economy.client_interval_inflation_rate
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
            elif data_field == DEBT_RATIO:
                data = self.__debt_ratio
            elif data_field == SECURITIES_RATIO:
                data = self.__securities_ratio
        elif category == CENTRAL_BANK:
            data = Decimal(0.0)
        elif category == BANK:
            if data_field == INCOME:
                data = self.economy.bank.income
            elif data_field == COSTS:
                data = self.economy.bank.costs
            elif data_field == PROFIT:
                data = self.economy.bank.profit
            elif data_field == INSTALLMENT_RATIO:
                data = self.economy.bank.installment / self.economy.bank.balance.assets_value
        elif category == PRIVATE_SECTOR:
            if data_field == INSTALLMENT_RATIO:
                data = self.economy.bank.client_installment / self.economy.client.balance.assets_value
        elif category == CENTRAL_BANK_BS:
            data = self.__balance_entry(self.economy.central_bank, data_field)
        elif category == BANK_BS:
            data = self.__balance_entry(self.economy.bank, data_field)
        elif category == PRIVATE_SECTOR_BS:
            data = self.__balance_entry(self.economy.client, data_field)

        if data_field in DEFLATABLE_FIELDS or category in BALANCE_SHEET_CATEGORIES:
            data = self.deflate(data, True)

        return data

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

        :return True if all balance sheets validate, IM > 0 and required lending rate < 100%."""
        self.economy.start_transactions()

        if cycle == 0 :
            self.__start_im = self.economy.im
            self.__desired_im = self.__start_im

        # aiming for target_im is only done when borrowing happens
        if self.economy.bank.client_interaction_interval.period_complete(cycle):
            self.__desired_im += self.__desired_im * self.economy.client_interval_growth_rate

            # set target im for end of cycle
            self.__target_im = self.__start_im
            self.__target_im += self.__target_im * self.economy.client_interval_growth_rate

            # process inflation
            self.economy.inflate()
            self.__desired_im += self.__desired_im * self.economy.client_interval_inflation_rate
            self.__target_im += self.__target_im * self.economy.client_interval_inflation_rate

            # There is a possibility that target_im > desired_im due to banks buying securities at the start of the sim
            self.__target_im = min(self.__desired_im, self.__target_im)

        # banks actions occur every cycle
        self.economy.update_reserves()
        if self.economy.bank.reserves_interval.period_complete(cycle):
            assert round(self.economy.bank.asset(BalanceEntries.RESERVES), 8)\
                   >= round(self.economy.bank.client_liabilities * (self.economy.central_bank.min_reserve
                                                              - self.economy.central_bank.mbs_real_reserve
                                                              - self.economy.central_bank.securities_real_reserve), 8)

        self.economy.grow_securities()
        self.economy.grow_mbs()
        self.economy.update_risk_assets()
        if self.economy.bank.reserves_interval.period_complete(cycle):
            assert round(self.economy.bank.risk_assets, 8) >= round(self.economy.bank.balance.assets_value * self.economy.bank.min_risk_assets, 8)
            # print(round(self.economy.bank.risk_assets, 8))
            # print(round(self.economy.bank.balance.assets_value * self.economy.bank.max_risk_assets, 8))
            assert round(self.economy.bank.risk_assets, 8) <= round(self.economy.bank.balance.assets_value * self.economy.bank.max_risk_assets, 8)
            assert round(self.economy.bank.asset(BalanceEntries.MBS), 8) <= round(self.economy.bank.risk_assets * self.economy.bank.max_mbs_assets, 8)
            assert round(self.economy.bank.asset(BalanceEntries.SECURITIES), 8) <= round(self.economy.bank.risk_assets * self.economy.bank.max_security_assets, 8)

        # process QE and helicopter money
        self.economy.process_qe()
        self.economy.process_helicopter_money()

        self.economy.process_bank_loans()

        self.economy.process_savings()
        self.economy.process_bank_income_and_spending()

        # calculations which only make sense on client interaction cycles
        if self.economy.bank.client_interaction_interval.period_complete(cycle):
            self.__required_lending = Decimal(max(self.__target_im - self.economy.im, 0.0))
            self.__lending = self.__required_lending * self.economy.lending_satisfaction_rate

            self.economy.process_borrowing(self.__lending)

            # Calculate real total lending
            self.__lending = self.economy.client.borrowed_money

            # multiplier to extrapolate to % per year
            multiplier: Decimal = Decimal(Period.YEAR_DAYS / self.economy.bank.client_interaction_interval.days)

            # calculate required and real lending percentages.
            if self.economy.im > 0.0:
                self.__required_lending_rate = self.__required_lending / self.economy.im * multiplier
                self.__lending_rate = self.__lending / self.economy.im * multiplier
            else:
                self.__required_lending_rate = Decimal('Infinity')
                self.__lending_rate = Decimal('Infinity')

            self.__nominal_growth = round((self.economy.im - self.__start_im) / self.__start_im * multiplier, 8)

            deflated_start_im: Decimal = self.deflate(self.__start_im, True)
            deflated_im: Decimal = self.deflate(self.economy.im)
            self.__real_growth = (deflated_im - deflated_start_im) / deflated_start_im * multiplier

            # set start_im for next growth cycle
            self.__start_im = self.economy.im

        self.__debt_ratio = self.economy.client.liability(BalanceEntries.DEBT) / self.economy.im

        if self.economy.client.balance.asset(BalanceEntries.SECURITIES) > Decimal(0.0):
            self.__securities_ratio = self.economy.client.balance.asset(BalanceEntries.SECURITIES) \
                                      / self.economy.client.balance.assets_value

        return self.economy.end_transactions()\
               and self.economy.im > 0\
               and self.__required_lending_rate <= Decimal(1)

    # only call after initial_inflation_rate has been applied in a cycle
    def deflate(self, amount: Decimal, skip_one: bool = False) -> Decimal:
        inflation_rates: List[Decimal] = self.collector.get_data_series(SYSTEM, INFLATION)

        if not skip_one:
            amount /= 1 + self.economy.client_interval_inflation_rate

        for inflation in inflation_rates:
            amount /= 1 + inflation

        return amount
