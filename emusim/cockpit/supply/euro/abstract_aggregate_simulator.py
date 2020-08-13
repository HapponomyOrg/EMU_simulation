from abc import abstractmethod
from collections import OrderedDict

from emusim.cockpit.supply.simulator import Simulator
from .aggregate_economy import AggregateEconomy
from .economic_actor import EconomicActor

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


class AbstractAggregateSimulator(Simulator, AggregateEconomy):
    # the structure of the data and whether or not it needs to be collected
    __data_structure: OrderedDict[str, OrderedDict[str, bool]]

    @abstractmethod
    def initialize_economy(self):
        pass

    def initialize_data_structure(self):
        for data_field in SYSTEM_DATA_FIELDS:
            self.set_collect_data(SYSTEM, data_field, False)

        for data_field in CENTRAL_BANK_DATA_FIELDS:
            self.set_collect_data(CENTRAL_BANK, data_field, False)

        for data_field in BANK_DATA_FIELDS:
            self.set_collect_data(BANK, data_field, False)

    def initialize_collector(self):
        self.add_data(SYSTEM, INFLATION, self.inflation)
        self.__collect_balance_sheet_data()

    @property
    def data_strcture(self) -> OrderedDict[str, OrderedDict[str, bool]]:
        return self.__data_structure

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
        Simulator.collect_data()
        self.__collect_balance_sheet_data()

    def __collect_balance_sheet_data(self):
        self.__collect_balance_data(CENTRAL_BANK_BS, self.central_bank)
        self.__collect_balance_data(BANK_BS, self.bank)
        self.__collect_balance_data(PRIVATE_SECTOR_BS, self.private_sector)

    def __collect_balance_data(self, category: str, actor: EconomicActor):
        for asset_name in actor.asset_names:
            self.add_data(category, asset_name, actor.asset(asset_name))

        for liability_name in actor.liability_names:
            self.add_data(category, liability_name, actor.liability(liability_name))