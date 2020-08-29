from collections import OrderedDict as OrdDict
from typing import OrderedDict

from . import EconomicActor, EuroEconomy
from .. import Simulator, DataGenerator, DataCollector

# System category
SYSTEM: str = "System"

# System data fields
IM = "IM"
DESIRED_IM = "Desired IM"
INFLATION = "Inflation"
NOMINAL_GROWTH = "Nominal growth"
REAL_GROWTH = "Real growth"
MBS_GROWTH = "MBS growth"
SECURITY_GROWTH = "Security growth"
LENDING_SATISFACTION = "Lending satisfaction rate"
REQUIRED_LENDING_RATE = "Required lending rate"
LENDING_RATE = "Lending rate"
REQUIRED_LENDING = "Required lending"
LENDING = "Lending"

SYSTEM_DATA_FIELDS = [IM, DESIRED_IM, NOMINAL_GROWTH, REAL_GROWTH, MBS_GROWTH, SECURITY_GROWTH, LENDING_SATISFACTION,
                      REQUIRED_LENDING_RATE, LENDING_RATE, REQUIRED_LENDING, LENDING]

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


class AggregateSimulator(Simulator):
    # the structure of the data and whether or not it needs to be collected

    def __init__(self, economy: EuroEconomy, generator: DataGenerator, collector: DataCollector):
        super().__init__(generator, collector)
        self.__data_structure: OrderedDict[str, OrderedDict[str, bool]] = OrdDict()
        self.__economy: EuroEconomy = economy
        self.__desired_im: float = 0.0 # im if growth_target is maintained
        self.__start_im: float = 0.0
        self.__target_im: float = 0.0
        self.__lending: float = 0.0
        self.__lending_rate:float = 0.0
        self.__required_lending: float = 0.0
        self.__required_lending_rate: float = 0.0

    def initialize_data_structure(self):
        for data_field in SYSTEM_DATA_FIELDS:
            self.collector.set_collect_data(SYSTEM, data_field, False)

        for data_field in CENTRAL_BANK_DATA_FIELDS:
            self.collector.set_collect_data(CENTRAL_BANK, data_field, False)

        for data_field in BANK_DATA_FIELDS:
            self.collector.set_collect_data(BANK, data_field, False)

    def initialize_collector(self):
        self.collector.add_data(SYSTEM, INFLATION, self.economy.inflation)
        self.__collect_balance_sheet_data()

    @property
    def data_structure(self) -> OrderedDict[str, OrderedDict[str, bool]]:
        return self.__data_structure

    @property
    def economy(self) -> EuroEconomy:
        return self.__economy

    def _data(self, category: str, data_field: str) -> float:
        if category == SYSTEM:
            return 0.0
        elif category == CENTRAL_BANK:
            return 0.0
        elif category == BANK:
            return 0.0
        else:
            return 0.0

    def collect_data(self):
        self.collector.collect_data()
        self.__collect_balance_sheet_data()

    def __collect_balance_sheet_data(self):
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
        self.__desired_im += self.__desired_im * self.economy.growth_rate

        # set target im for end of cycle
        self.__target_im = self.economy.im
        self.__target_im += self.__target_im * self.economy.growth_rate

        # process inflation
        self.economy.inflate()
        self.__desired_im += self.__desired_im * self.economy.inflation
        self.__target_im += self.__target_im * self.economy.inflation

        # reflect impact of price changes in securities
        self.economy.grow_securities()
        self.economy.grow_mbs()

        # process QE and helicopter money
        self.economy.process_qe()
        self.economy.process_helicopter_money()

        self.economy.process_savings()
        self.economy.process_bank_income()
        self.economy.process_bank_spending()

        self.__required_lending = self.__target_im - self.economy.im
        self.__lending = self.__required_lending * self.economy.lending_satisfaction_rate

        # calculate required and real lending percentages
        self.__required_lending_rate = self.__required_lending / self.economy.im
        self.__lending_rate = self.__lending / self.economy.im

        self.economy.process_borrowing(self.__lending)
        self.economy.update_reserves()

        return self.economy.end_transactions() and self.economy.im > 0