# module euro_simulation
# percentages are represented as a fractional number between 0 and 1, 0 being 0%, 0.5 being 50% and 1 being 100%

import os
from cockpit.supply.constants import *
from cockpit.supply.simulation import Simulation

class Euro_MS_Simulation(Simulation):

    def __init__(self):
        super().__init__()
        self.growth_rate = 0.030  # growth rate of available money (IM2). This is money that circulates in the real economy
        self.inflation_rate = 0.019  # inflation_rate

        self.initial_fixed_spending = 1000.0  # initial spending if bank spending mode is FIXED
        self.profit_spending = 0.02  # percentage of profit that banks spend into the real economy
        self.reserve_spending = 0.02  #percentage of bank reserves that are spent in the real economy
        self.capital_spending = 0.02  # percentage of capital (reserves + financial assets) that banks spend into the real economy

        self.minimum_reserve = 0.04  # minimum reserve
        self.maximum_reserve = self.minimum_reserve  # maximum % reserve a bank wants to hold in OM. This influences how much money will be used to buy financial assets.

        self.bank_payback_rate = 0.1  # bank payback rate
        self.private_payback_rate = 0.05  # private payback rate

        self.ecb_ir = 0.01                  # ECB interest rate
        self.ecb_savings_ir_mr = 0.015      # ECB interest rate on minimal bank reserves
        self.ecb_savings_ir_reserve = 0.0   # ECB interest rate on surplus bank reserves

        self.bank_ir = 0.025                # Bank interest rate
        self.asset_trickle_rate = 0.05           # Amount of money in financial assets that trickles to the real economy
        self.savings_ir = 0.005             # Bank interest on savings
        self.saving_rate = 0.2              # % of IM which is saved.

        self.minimum_new_money = 0.80       # minimum % of money of a loan that is newly created. The rest is taken from im if possible.
        self.maximum_new_money = 1.00       # maximium % of money of a loan that is newly created. The rest is taken from im if possible.

        self.no_loss = True  # whether or not banks are ok running a loss
        self.min_profit = 0.20  # minimum % in income (from interest) that is retained as profit (only if no loss is true).

        self.spending_mode = FIXED  # bank spending mode

        self.qe_spending_mode = QE_RELATIVE  # QE spending mode
        self.qe_trickle_rate = 1.00  # percentage of QE that immediately flows through to IM2. Can be interpreted as a form of helicopter money.
        self.qe_profit = False  # whether or not qe is interpreted as bank profit.
        self.qe_fixed_initial = 0.0  # initial fixed QE
        self.qe_relative = 0.025  # relative qe in % of IM2
        self.qe = []  # QE injected by ECB, adjusted for inflation_rate. This amount is subtracted from created_bank_reserve to keep track of money creation by ECB.
        self.qe_trickle = []

        self.asset_trickle_rate = 0.05  # percentage of asset capital that trickles to the real economy
        self.asset_trickle_mode = ASSET_GROWTH  # determines how the asset trickle is calculated
        self.asset_trickle = []
        self.asset_investment = [] # total amount of money that has been invested in assets by banks. Not affected by asset trickle

        self.im = []  # Money available to the real economy

        self.lending = []  # money that has been borrowed per cycle
        self.created_im = []  # money that has been created
        self.debt = []  # outstanding debt on which interest is paid
        self.payoff = []  # payoff of principal debt
        self.interest = []  # interest paid

        self.savings_interest = []  # interest earned from savings

        self.created_bank_reserve = []    # bank reserve money created by the ECB
        self.bank_reserve = []  # Bank reserves
        self.bank_profit = []   # bank profit: income from interest - payoff of loans and interests to ECB
        self.bank_assets = []   # Amount of money banks have invested in financial assets
        self.bank_spending = [] # money banks spend into the real economy
        self.bank_fixed = []    # fixed amount that banks spend into the real economy, adjusted for inflation_rate
        self.bank_lending = []  # money lent by the banks from the ECB
        self.bank_debt = []     # outstanding debt of banks to the ECB
        self.bank_payoff = []   # payoff of principal bank debt
        self.bank_interest = [] # interest paid to ecb

        # initial parameters
        self.initial_im = 100000.0  # initial amount of IM. Needs to be > 0.

        self.lending_percentage_im = []
        self.lending_percentage_total_money = []

        self.bank_reserve_percentage_debt = []
        self.bank_lending_percentage_bank_reserve = []
        self.bank_lending_percentage_total_money = []

        self.im_percentage_total_money = []
        self.bank_reserve_percentage_total_money = []
        self.asset_percentage_total_money = []

        self.savings_interest_percentage_im = []
        self.savings_interest_percentage_total_money = []
        self.ecb_interest_percentage_im = []
        self.ecb_interest_percentage_total_money = []

        self.debt_percentage_im = []
        self.debt_percentage_total_money = []

        self.bank_debt_percentage_bank_reserve = []
        self.bank_debt_percentage_total_money = []

        self.created_im_percentage_im = []
        self.created_im_percentage_total_money = []

        self.created_bank_reserve_percentage_bank_reserve = []
        self.created_bank_reserve_percentage_total_money = []
        self.created_money_percentage_total_money = []


    def initialize(self):
        self.im.clear()
        self.lending.clear()
        self.debt.clear()
        self.payoff.clear()
        self.interest.clear()
        self.created_im.clear()

        self.created_bank_reserve.clear()
        self.bank_reserve.clear()
        self.bank_profit.clear()
        self.bank_assets.clear()
        self.bank_spending.clear()
        self.bank_fixed.clear()
        self.bank_lending.clear()
        self.bank_debt.clear()
        self.bank_payoff.clear()
        self.bank_interest.clear()

        self.qe.clear()
        self.qe_trickle.clear()
        self.savings_interest.clear()

        self.asset_trickle.clear()
        self.asset_investment.clear()

        self.lending_percentage_im.clear()
        self.lending_percentage_total_money.clear()
        self.bank_reserve_percentage_debt.clear()
        self.bank_lending_percentage_bank_reserve.clear()
        self.bank_lending_percentage_total_money.clear()
        self.im_percentage_total_money.clear()
        self.bank_reserve_percentage_total_money.clear()
        self.asset_percentage_total_money.clear()
        self.savings_interest_percentage_im.clear()
        self.savings_interest_percentage_total_money.clear()
        self.ecb_interest_percentage_im.clear()
        self.ecb_interest_percentage_total_money.clear()
        self.debt_percentage_im.clear()
        self.debt_percentage_total_money.clear()
        self.bank_debt_percentage_bank_reserve.clear()
        self.bank_debt_percentage_total_money.clear()
        self.created_im_percentage_im.clear()
        self.created_im_percentage_total_money.clear()
        self.created_bank_reserve_percentage_bank_reserve.clear()
        self.created_bank_reserve_percentage_total_money.clear()
        self.created_money_percentage_total_money.clear()

        self.im.append(self.initial_im)
        self.lending.append(self.initial_im)
        self.debt.append(self.initial_im)
        self.payoff.append(0.0)
        self.interest.append(0.0)
        self.created_im.append(self.initial_im)

        reserve = self.initial_im * self.minimum_reserve
        self.created_bank_reserve.append(reserve)  # reflects bank_reserve money creation
        self.bank_reserve.append(reserve)
        self.bank_profit.append(0.0)
        self.bank_assets.append(0.0)
        self.bank_spending.append(0.0)
        self.bank_lending.append(0.0)
        self.bank_fixed.append(self.initial_fixed_spending)
        self.bank_debt.append(reserve)
        self.bank_payoff.append(0.0)
        self.bank_interest.append(0.0)

        self.qe.append(0.0)
        self.qe_trickle.append(0.0)

        self.savings_interest.append(0.0)
        self.asset_trickle.append(0.0)
        self.asset_investment.append(0.0)

        self.calculate_percentages(0)


    def run_simulation(self, iterations):
        for i in range(iterations):
            if i == 0:
                self.initialize()
            else:
                # copy previous state
                self.im.append(self.im[i - 1])
                self.lending.append(0.0)
                self.debt.append(self.debt[i - 1])
                self.payoff.append(0.0)
                self.interest.append(0.0)
                self.created_im.append(self.created_im[i - 1])

                self.created_bank_reserve.append(self.created_bank_reserve[i - 1])
                self.bank_reserve.append(self.bank_reserve[i - 1])
                self.bank_profit.append(0.0)
                self.bank_assets.append(self.bank_assets[i - 1])
                self.bank_spending.append(0.0)
                self.bank_fixed.append(self.bank_fixed[i - 1] + self.bank_fixed[i - 1] * self.inflation_rate)
                self.bank_lending.append(0.0)
                self.bank_debt.append(self.bank_debt[i - 1])
                self.bank_payoff.append(0.0)
                self.bank_interest.append(0.0)

                if self.qe_spending_mode == QE_FIXED:
                    self.qe.append(self.qe[i - 1] + self.qe[i - 1] * self.inflation_rate)
                else:
                    self.qe.append(0.0)  # determine after debt has been processed

                self.qe_trickle.append(0.0)
                self.asset_trickle.append(0.0)
                self.asset_investment.append(self.asset_investment[i - 1])

                # calculate interest on savings from previous cycle and add to im
                self.savings_interest.append(self.im[i - 1] * self.saving_rate * self.savings_ir)

                # determine growth
                growth = self.im[i] * self.growth_rate + \
                         self.im[i] * self.growth_rate * self.inflation_rate + \
                         self.im[i] * self.inflation_rate
                target_im = self.im[i] + growth

                # earn calculated interest
                self.im[i] += self.savings_interest[i]
                self.bank_reserve[i] -= self.savings_interest[i]
                self.bank_profit[i] -= self.savings_interest[i]

                # calculate debt payoff and interest due
                self.payoff[i] = self.debt[i] * self.private_payback_rate
                self.interest[i] = self.debt[i] * self.bank_ir

                self.bank_payoff[i] = self.bank_debt[i] * self.bank_payback_rate
                self.bank_interest[i] = self.bank_debt[i] * self.ecb_ir

                # pay non bank debts and interests. First clear newly created money
                if self.created_im[i] > self.payoff[i]:
                    self.created_im[i] -= self.payoff[i]
                else:
                    self.bank_reserve[i] += self.payoff[i] - self.created_im[i]
                    self.created_im[i] = 0

                self.im[i] -= self.payoff[i] + self.interest[i]
                self.bank_reserve[i] += self.interest[i]
                self.bank_profit[i] += self.interest[i]
                self.debt[i] -= self.payoff[i]
                self.debt[i] = max(0.0, self.debt[i])  # avoid debt going negative due to rounding

                # generate interest from ECB
                min_reserve = self.debt[i - 1] * self.minimum_reserve

                if self.bank_reserve[i - 1] <= min_reserve:
                    create_interest = self.bank_reserve[i - 1] * self.ecb_savings_ir_mr
                    self.bank_reserve[i] += create_interest
                    self.created_bank_reserve[i] += create_interest
                else:
                    create_interest = min_reserve * self.ecb_savings_ir_mr  # interest on minimum reserve
                    create_interest += (self.bank_reserve[i - 1] - min_reserve) * self.ecb_savings_ir_reserve # interest on surplus
                    self.bank_reserve[i] += create_interest

                    if create_interest > 0:
                        self.created_bank_reserve[i] += create_interest
                    else:
                        self.im[i] -= create_interest # interest paid by banks goes to real economy

                # pay bank debts and interests. If insufficient, sell financial assets or get a new loan
                if self.bank_reserve[i] >= self.bank_payoff[i] + self.bank_interest[i]:
                    self.bank_reserve[i] -= self.bank_payoff[i] + self.bank_interest[i]
                else:
                    remaining_debt = self.bank_payoff[i] + self.bank_interest[i] - self.bank_reserve[i]
                    self.bank_reserve[i] = 0.0

                    if self.bank_assets[i] >= remaining_debt:
                        self.bank_assets[i] -= remaining_debt
                        self.asset_investment[i] -= remaining_debt
                    else:
                        remaining_debt -= self.bank_assets[i]
                        self.asset_investment[i] -= self.bank_assets[i]
                        self.bank_assets[i] = 0.0
                        self.bank_lending[i] = remaining_debt
                        self.bank_debt[i] += remaining_debt
                        self.created_bank_reserve[i] += remaining_debt

                self.bank_debt[i] -= self.bank_payoff[i]
                self.bank_debt[i] = max(0.0, self.bank_debt[i])  # avoid bank debt going negative due to rounding

                self.created_bank_reserve[i] -= self.bank_payoff[i]
                self.created_bank_reserve[i] = max(0.0, self.created_bank_reserve[i])  # avoid created om going negative due to rounding

                self.bank_profit[i] -= self.bank_payoff[i] + self.bank_interest[i]

                # inject QE
                if self.qe_spending_mode != QE_NONE:
                    if self.qe_spending_mode == QE_RELATIVE:
                        self.qe[i] = self.qe_relative * self.debt[i]

                    self.created_bank_reserve[i] += self.qe[i]
                    self.qe_trickle[i] = self.qe[i] * self.qe_trickle_rate
                    self.bank_reserve[i] += self.qe[i] - self.qe_trickle[i]
                    self.im[i] += self.qe_trickle[i]

                    if self.qe_profit:
                        self.bank_profit[i] += self.qe[i] - self.qe_trickle[i]

                # bank spending
                if self.spending_mode == FIXED:
                    # spend the fixed amount if possible, otherwise spend all of im1
                    if self.bank_reserve[i] >= self.bank_fixed[i]:
                        self.bank_spending[i] = self.bank_fixed[i]
                    else:
                        self.bank_spending[i] = self.bank_reserve[i]
                elif self.spending_mode == PROFIT_PERCENTAGE:
                    if self.bank_profit[i] >= 0.0:
                        self.bank_spending[i] = self.profit_spending * self.bank_profit[i]
                    else:  # profit can be negative
                        self.bank_spending[i] = 0.0
                elif self.spending_mode == RESERVE_PERCENTAGE:
                    self.bank_spending[i] = self.bank_reserve[i] * self.reserve_spending
                else:  # spending mode == CAPITAL_PERCENTAGE
                    self.bank_spending[i] = (self.bank_reserve[i] + self.bank_assets[i]) * self.capital_spending

                if self.no_loss:
                    self.bank_spending[i] = min(self.bank_spending[i], (1 - self.min_profit) * self.bank_profit[i])
                    self.bank_spending[i] = max (0.0, self.bank_spending[i])  # bank can not spend negative amounts

                if self.bank_spending[i] + self.im[i] > target_im:  # spending would increase im above desired amount
                    self.bank_spending[i] = max(0.0, target_im - self.im[i])

                if self.spending_mode != CAPITAL_PERCENTAGE:
                    self.bank_reserve[i] -= self.bank_spending[i]
                else: # spend from financial assets first
                    if self.bank_assets[i] >= self.bank_spending[i]:
                        self.bank_assets[i] -= self.bank_spending[i]
                        self.asset_investment[i] -= self.bank_spending[i]
                    else:
                        reserve_spending = self.bank_spending[i] - self.bank_assets[i]
                        self.asset_investment[i] -= self.bank_assets[i]
                        self.bank_assets[i] = 0
                        self.bank_reserve[i] -= reserve_spending

                self.im[i] += self.bank_spending[i]
                self.bank_profit[i] -= self.bank_spending[i]

                # grow economy through lending if needed
                self.lending[i] = max(0.0, target_im - self.im[i])

                if self.lending[i] > 0.0:
                    self.im[i] += self.lending[i]
                    self.debt[i] += self.lending[i]
                    min_create_im = self.lending[i] * self.minimum_new_money
                    max_create_im = self.lending[i] * self.maximum_new_money
                    create_im = max_create_im
                    max_desired_reserve = self.maximum_reserve * self.debt[i]

                    # check bank reserve
                    if self.bank_reserve[i] - self.lending[i] + max_create_im > max_desired_reserve:
                        create_im = max(min_create_im, max_desired_reserve - self.bank_reserve[i] + self.lending[i])

                    self.bank_reserve[i] -= self.lending[i] - create_im
                    self.created_im[i] += create_im

                    if self.bank_reserve[i] > max_desired_reserve:
                        surplus = self.bank_reserve[i] - max_desired_reserve
                        self.bank_assets[i] += surplus
                        self.asset_investment[i] += surplus
                        self.bank_reserve[i] -= surplus

                        if self.asset_trickle_mode == ASSET_GROWTH:
                            self.asset_trickle[i] = surplus * self.asset_trickle_rate
                        else:  # asset trickle mode is ASSET_CAPITAL
                            self.asset_trickle[i] = self.bank_assets[i] * self.asset_trickle_rate

                self.bank_assets[i] -= self.asset_trickle[i]

                # update bank_reserve in accordance to minimum_reserve
                min_reserve = self.minimum_reserve * self.debt[i]

                if self.bank_reserve[i] < min_reserve:
                    ecb_lending = max(0.0, min_reserve - (self.bank_reserve[i] + self.bank_assets[i]))
                    asset_transfer = min(self.bank_assets[i], min_reserve - self.bank_reserve[i])

                    self.asset_investment[i] -= asset_transfer
                    self.bank_assets[i] -= asset_transfer
                    self.bank_reserve[i] += asset_transfer

                    self.created_bank_reserve[i] += ecb_lending
                    self.bank_reserve[i] += ecb_lending
                    self.bank_debt[i] += ecb_lending

                self.calculate_percentages(i)

        #self.write_parameters()
        #self.write_raw_data(iterations)


    def calculate_percentages(self, i):

        total_money = self.bank_assets[i] + self.bank_reserve[i] + self.im[i]

        self.lending_percentage_im.append(self.lending[i] * 100 / self.im[i])
        self.lending_percentage_total_money.append(self.lending[i] * 100 / total_money)

        self.bank_reserve_percentage_debt.append(self.bank_reserve[i] * 100 / self.debt[i])
        self.bank_lending_percentage_bank_reserve.append(self.bank_lending[i] * 100 / self.bank_reserve[i])
        self.bank_lending_percentage_total_money.append(self.bank_lending[i] * 100 / total_money)

        self.im_percentage_total_money.append(self.im[i] * 100 / total_money)
        self.bank_reserve_percentage_total_money.append(self.bank_reserve[i] * 100 / total_money)
        self.asset_percentage_total_money.append(self.bank_assets[i] * 100 / total_money)

        self.savings_interest_percentage_im.append(self.savings_interest[i] * 100 / self.im[i])
        self.savings_interest_percentage_total_money.append(self.savings_interest[i] * 100 / total_money)

        self.ecb_interest_percentage_im.append(self.bank_interest[i] * 100 / self.im[i])
        self.ecb_interest_percentage_total_money.append(self.bank_interest[i] * 100 / total_money)

        self.debt_percentage_im.append(self.debt[i] * 100 / self.im[i])
        self.debt_percentage_total_money.append(self.debt[i] * 100 / total_money)

        self.bank_debt_percentage_bank_reserve.append(self.bank_debt[i] * 100 / self.bank_reserve[i])
        self.bank_debt_percentage_total_money.append(self.bank_debt[i] * 100 / total_money)

        self.created_im_percentage_im.append(self.created_im[i] * 100 / self.im[i])
        self.created_im_percentage_total_money.append(self.created_im[i] * 100 / total_money)

        self.created_bank_reserve_percentage_bank_reserve.append(self.created_bank_reserve[i] * 100 / self.bank_reserve[i])
        self.created_bank_reserve_percentage_total_money.append(self.created_bank_reserve[i] * 100 / total_money)
        self.created_money_percentage_total_money.append((self.created_bank_reserve[i] + self.created_im[i]) * 100 / total_money)


    def get_total_inflow(self, do_deflate=False):
        inflow = []

        for i in range(len(self.savings_interest)):
            if i != 0:  # remove setup step
                total_inflow = self.savings_interest[i] + self.qe_trickle[i] + self.asset_trickle[i]

                if do_deflate:
                    inflow.append(round(self.deflate(total_inflow, i), 2))
                else:
                    inflow.append(round(total_inflow, 2))

        return inflow


    def write_parameters(self):
            if os.path.exists('./cockpit/supply/generated data/parameters.txt'):
                os.remove('./cockpit/supply/generated data/parameters.txt')

            f = open('./cockpit/supply/generated data/parameters.txt', 'w')
            f.write(f'Initial IM2 = {self.initial_im:.2f}\n')
            f.write('\n')
            f.write(f'IM2 growth rate = {self.growth_rate * 100} %\n')
            f.write(f'Inflation = {self.inflation_rate * 100} %\n')
            f.write('\n')
            f.write(f'Commercial payback rate (% of debt) = {self.private_payback_rate * 100} %\n')
            f.write(f'Commercial interest rate (% of debt) = {self.bank_ir * 100} %\n')
            f.write('\n')
            f.write(f'Saving rate (% of IM2) = {self.saving_rate * 100}\n')
            f.write(f'Savings interest rate = {self.savings_ir * 100} %\n')
            f.write('\n')
            f.write(f'Minimal required reserve = {self.minimum_reserve * 100} %\n')
            f.write(f'Maximum desired reserve (IM) = {self.maximum_reserve * 100} %\n')
            f.write('\n')
            f.write(f'Bank payback rate (% of debt) = {self.bank_payback_rate * 100} %\n')
            f.write(f'Bank interest rate (% of debt) = {self.ecb_ir * 100} %\n')
            f.write('\n')
            f.write(f'Minimal \'new IM %\' on loans = {self.minimum_new_money * 100} %\n')
            f.write('\n')
            f.write(f'No loss = {self.no_loss}\n')
            if self.no_loss:
                f.write(f'Minimal profit from interest = {self.min_profit * 100} %\n')
            f.write('\n')
            f.write(f'Initial fixed spending = {self.initial_fixed_spending:.2f}\n')
            f.write(f'% profit spending = {self.profit_spending * 100} %\n')
            f.write(f'% capital spending = {self.capital_spending * 100} %\n')
            f.write('\n')
            f.write(f'QE spending mode: {self.qe_spending_mode}\n')
            if self.qe_spending_mode == QE_FIXED:
                f.write(f'Initial QE = {self.qe_fixed_initial:.2f}\n')
            elif self.qe_spending_mode == QE_RELATIVE:
                f.write(f'QE % of debt = {self.qe_relative * 100} %\n')
            # f.write(f'QE is bank profit = {qe_profit}\n')
            if self.qe_spending_mode != QE_NONE:
                f.write(f'QE trickle = {self.qe_trickle_rate * 100} %\n')
            f.close()


    def write_raw_data(self, iterations):
            if os.path.exists(f'./cockpit/supply/generated data/{self.spending_mode}.csv'):
                os.remove(f'./cockpit/supply/generated data/{self.spending_mode}.csv')

            f = open(f'./cockpit/supply/generated data/{self.spending_mode}.csv', 'w')
            f.write('Created OM,OM,OM growth,')
            f.write('QE,QE trickle,')
            f.write('Bank spending,Bank profit,Bank debt,Bank payoff,Bank interest,')
            f.write('IM 1,IM 2,Earned interest,Created IM,Debt,Payoff,Interest,')
            f.write('Growth,Lending,IM total,')
            f.write('Lending % IM2,Lending % IM total,')
            f.write('IM 1 % IM total,IM 2 % IM total,')
            f.write('Earned interest % IM 2,Earned interest % IM total,')
            f.write('Debt % IM 2,Debt % IM total,')
            f.write('Created % IM 2,Created % IM total\n')

            for i in range(iterations):
                f.write(f'{self.deflate(self.created_bank_reserve[i], i):.2f},\
                    {self.deflate(self.bank_reserve[i], i):.2f},\
                    {self.deflate(self.created_bank_reserve[i] + self.bank_reserve[i], i):.2f},\
                    {self.deflate(self.created_bank_reserve[1] + self.bank_reserve[i], i) - self.deflate(self.created_bank_reserve[i - 1] + self.bank_reserve[i - 1], i - 1):.2f},\
                    {self.deflate(self.qe[i], i):.2f},\
                    {self.deflate(self.qe_trickle_rate * self.qe[i], i):.2f},\
                    {self.deflate(self.bank_spending[i], i):.2f},\
                    {self.deflate(self.bank_profit[i], i):.2f},{self.bank_debt[i]:.2f},\
                    {self.bank_payoff[i]:.2f},\
                    {self.bank_interest[i]:.2f},\
                    {self.deflate(self.savings_interest[i], i):.2f},\
                    {self.deflate(self.created_im[i], i)},\
                    {self.deflate(self.debt[i], i):.2f},\
                    {self.deflate(self.payoff[i], i):.2f},\
                    {self.deflate(self.interest[i], i):.2f},\
                    {self.deflate(self.im[i], i) - self.deflate(self.im[i - 1], i - 1):.2f},\
                    {self.deflate(self.lending[i], i):.2f},\
                    {self.deflate(self.bank_reserve[i] + self.im[i], i):.2f},\
                    {self.lending_percentage_im[i]:.2f},\
                    {self.lending_percentage_total_money[i]:.2f},\
                    {self.im_percentage_total_money[i]:.2f},\
                    {self.savings_interest_percentage_im[i]:.2f},\
                    {self.savings_interest_percentage_total_money[i]:.2f},\
                    {self.debt_percentage_im[i]:.2f},\
                    {self.debt_percentage_total_money[i]:.2f},\
                    {self.created_im_percentage_im[i]:.2f},\
                    {self.created_im_percentage_total_money[i]:.2f}\n')

            f.close()