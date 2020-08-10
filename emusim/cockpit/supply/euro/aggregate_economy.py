from enum import Enum

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.bank import Bank
from emusim.cockpit.supply.euro.central_bank import CentralBank
from emusim.cockpit.supply.euro.economic_actor import EconomicActor
from emusim.cockpit.supply.euro.private_actor import PrivateActor


class GrowthModel(Enum):
    CURRENT = 0
    INITIAL = 1


class QEMode(Enum):
    NONE = 0
    FIXED = 1
    DEBT_RELATED = 2


class HelicopterMode(Enum):
    NONE = 0
    FIXED = 1
    DEBT_RELATED = 2


class AggregateEconomy():
    __central_bank: CentralBank
    __bank: Bank
    __private_sector: PrivateActor

    __growth_target: float
    __growth_model: GrowthModel
    __inflation: float

    __desired_im: float = 0.0 # im if growth_target is maintained

    __target_im = 0.0

    nominal_growth: float = 0.0
    real_growth: float = 0.0
    growth_inflation_influence: float = 0.0

    lending_satisfaction_rate: float = 1.0
    required_lending_percentage: float = 0.0    # required lending in order to reach growth target as % of start of
                                                # cycle im
    lending_percentage: float = 0.0             # lending which occurred as % of start of cycle im

    mbs_growth: float = 0.0                     # the growth_target of prices of MBS
    security_growth: float = 0.0                # the growth_target of security prices

    qe_mode: QEMode = QEMode.NONE
    qe_fixed: float = 0.0
    qe_debt_related = 0.0

    helicopter_mode: HelicopterMode = HelicopterMode.NONE
    helicopter_fixed: float = 0.0
    helicopter_debt_related: float = 0.0

    def __init__(self,
                 central_bank: CentralBank,
                 bank: Bank,
                 private_sector: PrivateActor,
                 inflation: float,
                 growth_rate: float,
                 growth_target: GrowthModel = GrowthModel.CURRENT):
        self.__central_bank = central_bank
        self.__bank = bank
        self.__private_sector = private_sector

        self.__desired_im = self.im()

        self.__growth_target = growth_rate
        self.__growth_model = growth_target
        self.__inflation = inflation

    @property
    def growth_target(self) -> float:
        return self.__growth_target

    @property
    def growth_model(self) -> GrowthModel:
        return self.__growth_model

    @property
    def desired_im(self) -> float:
        return self.__desired_im

    @property
    def inflation(self) -> float:
        return self.__inflation

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def bank(self) -> Bank:
        return self.__bank

    @property
    def private_sector(self) -> PrivateActor:
        return self.__private_sector

    def im(self) -> float:
        im = self.bank.liability(DEPOSITS)
        im += self.bank.liability(SAVINGS)
        im += self.bank.liability(EQUITY)

        return im

    def private_debt(self) -> float:
        return self.__private_sector.liability(DEBT)

    def bank_debt(self) -> float:
        return self.__bank.liability(DEBT)

    def inflate_parameters(self):
        self.central_bank.inflate_parameters(self.inflation)
        self.bank.inflate_parameters(self.inflation)
        self.private_sector.inflate_parameters(self.inflation)
        self.__desired_im += self.desired_im * self.inflation
        self.qe_fixed += self.qe_fixed * self.inflation
        self.helicopter_fixed += self.helicopter_fixed * self.inflation

    def grow_mbs(self):
        mbs_growth = self.bank.asset(MBS) * self.mbs_growth
        self.bank.book_asset(MBS, mbs_growth)
        self.bank.book_liabilaty(EQUITY, mbs_growth)

    def grow_securities(self, actor: EconomicActor):
        # grow central bank securities
        security_growth = actor.asset(SECURITIES) * self.security_growth
        actor.book_asset(SECURITIES, security_growth)
        actor.book_liabilaty(EQUITY, security_growth)

    def process_qe(self, qe_amount: float):
        self.central_bank.book_asset(SECURITIES, qe_amount)
        self.central_bank.book_liabilaty(RESERVES, qe_amount)

        # first buy securities from banks
        qe_bank_securities = min(qe_amount, self.bank.asset(SECURITIES))
        self.bank.book_asset(SECURITIES, -qe_bank_securities)
        self.bank.book_asset(RESERVES, qe_bank_securities)

        # get remainder from private sector
        qe_private_securities = qe_amount - qe_bank_securities
        self.bank.book_asset(RESERVES, qe_private_securities)
        self.bank.book_liabilaty(DEPOSITS, qe_private_securities)

    def process_helicopter_money(self, helicopter_amount: float):
        self.central_bank.book_asset(HELICOPTER_MONEY, helicopter_amount)
        self.bank.book_asset(RESERVES, helicopter_amount)
        self.bank.book_liabilaty(DEPOSITS, helicopter_amount)
        self.private_sector.book_asset(DEPOSITS, helicopter_amount)
        self.private_sector.book_liabilaty(EQUITY, helicopter_amount)

    def process_cycle(self) -> bool:
        crashed = False

        start_im = self.im()

        # grow im for optimal scenario where growth_target is always achieved
        self.__desired_im += self.__desired_im * self.growth_target

        if self.growth_model == GrowthModel.CURRENT:
            self.__target_im = self.im()
            self.__target_im += self.__target_im * self.growth_target
        else:
            self.__target_im = self.desired_im

        self.inflate_parameters()

        # reflect impact of price changes in securities
        self.grow_securities(self.central_bank)
        self.grow_securities(self.bank)

        if self.qe_mode == QEMode.FIXED:
            self.process_qe(self.qe_fixed)
        elif self.qe_mode == QEMode.DEBT_RELATED:
            self.process_qe(self.private_sector.liability(DEBT) * self.qe_debt_related)

        if self.helicopter_mode == HelicopterMode.FIXED:
            self.process_helicopter_money(self.helicopter_fixed)
        elif self.helicopter_mode == HelicopterMode.DEBT_RELATED:
            self.process_helicopter_money(self.private_sector.liability(DEBT * self.helicopter_debt_related))

        self.bank.process_savings()
        self.bank.process_private_loans_and_income()
        self.bank.spend()

        required_lending: float = self.__target_im - self.bank.liability(DEPOSITS) - self.bank.liability(SAVINGS)
        lending: float = required_lending * self.lending_satisfaction_rate

        self.private_sector.borrow(lending)
        self.bank.update_reserves()

        self.save_state()

        # calculate nominal and real growth
        end_im = self.im()
        self.nominal_growth = (end_im - start_im) / start_im
        self.real_growth = (end_im / (1 + self.inflation) - start_im) / start_im

        # calculate required and real lending percentages
        self.required_lending_percentage = required_lending / start_im
        self.lending_percentage = lending / start_im

        return crashed

    def save_state(self):
        self.central_bank.save_state()
        self.bank.save_state()
        self.private_sector.save_state()