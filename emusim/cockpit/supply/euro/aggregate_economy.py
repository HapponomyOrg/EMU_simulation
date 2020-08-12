from enum import Enum

from emusim.cockpit.supply.euro.balance_entries import *
from emusim.cockpit.supply.euro.bank import Bank
from emusim.cockpit.supply.euro.central_bank import CentralBank
from emusim.cockpit.supply.euro.economic_actor import EconomicActor
from emusim.cockpit.supply.euro.private_actor import PrivateActor


class QEMode(Enum):
    NONE = 0
    FIXED = 1
    DEBT_RELATED = 2


class HelicopterMode(Enum):
    NONE = 0
    FIXED = 1
    DEBT_RELATED = 2


class AggregateEconomy():

    growth_rate: float
    inflation: float

    lending_satisfaction_rate: float = 1.0

    mbs_growth: float = 0.0                     # the growth_target of prices of MBS
    security_growth: float = 0.0                # the growth_target of security prices

    qe_mode: QEMode = QEMode.NONE
    qe_fixed: float = 0.0
    qe_debt_related = 0.0

    helicopter_mode: HelicopterMode = HelicopterMode.NONE
    helicopter_fixed: float = 0.0
    helicopter_debt_related: float = 0.0

    __central_bank: CentralBank
    __bank: Bank
    __private_sector: PrivateActor

    __desired_im: float = 0.0 # im if growth_target is maintained

    # cycle attributes
    __start_im: float = 0.0

    __target_im = 0.0

    __nominal_growth: float = 0.0
    __real_growth: float = 0.0

    __required_lending: float = 0.0
    __lending: float = 0.0

    __required_lending_percentage: float = 0.0
    __lending_percentage: float = 0.0

    def __init__(self,
                 central_bank: CentralBank,
                 bank: Bank,
                 private_sector: PrivateActor,
                 inflation: float,
                 growth_rate: float):
        self.__central_bank = central_bank
        self.__bank = bank
        self.__private_sector = private_sector

        self.__desired_im = self.im

        self.growth_rate = growth_rate
        self.inflation = inflation

    @property
    def desired_im(self) -> float:
        return self.__desired_im

    @property
    def central_bank(self) -> CentralBank:
        return self.__central_bank

    @property
    def bank(self) -> Bank:
        return self.__bank

    @property
    def private_sector(self) -> PrivateActor:
        return self.__private_sector

    @property
    def target_im(self) -> float:
        return self.__target_im

    @property
    def nominal_growth(self) -> float:
        """Returns growth without adjusting for inflation"""
        return self.__nominal_growth

    @property
    def real_growth(self) -> float:
        """Returns growth after adjustment for inflation."""
        return self.__real_growth

    @property
    def required_lending(self) -> float:
        """Returns required lending needed to satisfy growth, not adjusted for inflation."""
        return self.__required_lending

    @property
    def lending(self) -> float:
        """Returns executed lending, not adjusted for inflation."""
        return  self.__lending

    @property
    def required_lending_percentage(self) -> float:
        """Returns required lending needed to satisfy growth as percentage of IM."""
        return self.__required_lending_percentage

    @property
    def lending_percentage(self) -> float:
        """Returns executed lending as percentage of IM."""
        return  self.__lending_percentage

    @property
    def im(self) -> float:
        im = self.bank.liability(DEPOSITS)
        im += self.bank.liability(SAVINGS)

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
        self.bank.book_liability(EQUITY, mbs_growth)

    def grow_securities(self, actor: EconomicActor):
        # grow central bank securities
        security_growth = actor.asset(SECURITIES) * self.security_growth
        actor.book_asset(SECURITIES, security_growth)
        actor.book_liability(EQUITY, security_growth)

    def process_qe(self, qe_amount: float):
        self.central_bank.book_asset(SECURITIES, qe_amount)
        self.central_bank.book_liability(RESERVES, qe_amount)

        # first buy securities from banks
        qe_bank_securities = min(qe_amount, self.bank.asset(SECURITIES))
        self.bank.book_asset(SECURITIES, -qe_bank_securities)
        self.bank.book_asset(RESERVES, qe_bank_securities)

        # get remainder from private sector
        qe_private_securities = qe_amount - qe_bank_securities
        self.bank.book_asset(RESERVES, qe_private_securities)
        self.bank.book_liability(DEPOSITS, qe_private_securities)

    def process_helicopter_money(self, helicopter_amount: float):
        self.central_bank.book_asset(HELICOPTER_MONEY, helicopter_amount)
        self.bank.book_asset(RESERVES, helicopter_amount)
        self.bank.book_liability(DEPOSITS, helicopter_amount)
        self.private_sector.book_asset(DEPOSITS, helicopter_amount)
        self.private_sector.book_liability(EQUITY, helicopter_amount)

    def start_cycle(self):
        self.__start_im = self.im

        # grow im for optimal scenario where growth_target is always achieved
        self.__desired_im += self.desired_im * self.growth_rate

        # set target im for end of cycle
        self.__target_im = self.im
        self.__target_im += self.target_im * self.growth_rate

    def process_cycle(self) -> bool:
        """Process a full cycle. Parameters need to be set before this is called. Cycle parameters can be read after
        the cycle has completed.

        Returns True if all balance sheets validate and IM > 0."""
        self.start_cycle()
        self.inflate_parameters()

        # reflect impact of price changes in securities
        self.grow_securities(self.central_bank)
        self.grow_securities(self.bank)

        # reflect impact of price changes in mbs
        self.grow_mbs()

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

        self.__required_lending = self.target_im - self.bank.liability(DEPOSITS) - self.bank.liability(SAVINGS)
        self.__lending = self.__required_lending * self.lending_satisfaction_rate

        # calculate required and real lending percentages
        self.__required_lending_percentage = self.__required_lending_percentage / self.im
        self.__lending_percentage = self.__lending_percentage / self.im

        self.private_sector.borrow(self.lending)
        self.bank.update_reserves()

        return self.end_cycle() and self.private_sector.asset(DEPOSITS) + self.private_sector.asset(SAVINGS) > 0

    def end_cycle(self) -> bool:
        sucess: bool = self.central_bank.end_cycle() and self.bank.end_cycle() and self.private_sector.end_cycle()

        # calculate nominal and real growth
        end_im = self.im
        self.__nominal_growth = (end_im - self.__start_im) / self.__start_im
        self.__real_growth = (end_im / (1 + self.inflation) - self.__start_im) / self.__start_im

        return sucess