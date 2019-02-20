# module euro_simulation
# percentages are represented as a fractional number between 0 and 1, 0 being 0%, 0.5 being 50% and 1 being 100%

import os
from cockpit.supply.constants import *
from cockpit.utilities import deflate, get_growth

class Euro_MS_Simulation:

    def __init__(self):
        self.growth_rate = 0.030  # growth rate of available money (IM2). This is money that circulates in the real economy
        self.inflation_rate = 0.019  # inflation

        self.initial_fixed_spending = 1000.0  # initial spending if bank spending mode is FIXED
        self.pp = 0.02  # percentage of profit that banks spend into the real economy
        self.cp = 0.02  # percentage of capital that banks spend into the real economy

        self.mr = 0.04  # minimum reserve

        self.pbdr = 0.1  # bank payback rate
        self.nbdr = 0.05  # non bank payback rate

        self.ecbi = 0.01  # ECB interest rate
        self.pbi = 0.025  # commercial bank interest rate
        self.savei = 0.005  # interest on savings
        self.saving_rate = 0.2  # % of IM2 which is saved.

        self.nmr = 1.00  # minimum % of money of a loan that is newly created. The rest is taken from im1 if possible.
        self.min_bank_reserve = 0.00  # minimum % reserve a bank wants to hold in im1. This influences how much money will be created.

        self.no_loss = True  # whether or not banks are ok running a loss
        self.min_profit = 0.20  # minimum % in income (from interest) that is retained as profit (only if no loss is true).

        self.spending_mode = FIXED  # bank spending mode

        self.qe_spending = QE_RELATIVE  # QE spending mode
        self.qe_trickle_rate = 1.00  # percentage of QE that immediately flows through to IM2. Can be interpreted as a form of helicopter money.
        self.qe_profit = False  # whether or not qe is interpreted as bank profit.
        self.qe_fixed_initial = 0.0  # initial fixed QE
        self.qe_relative = 0.025  # relative qe in % of IM2
        self.qe = []  # QE injected by ECB, adjusted for inflation. This amount is subtracted from om1 to keep track of money creation by ECB.
        self.qe_trickle = []

        self.im1 = []  # inside money on bank's account
        self.im2 = []  # inside money that is on non bank accounts

        self.lending = []  # money that has been borrowed per cycle
        self.new_im = []  # money that has been created
        self.debt = []  # outstanding debt on which interest is paid
        self.payoff = []  # payoff of principal debt
        self.interest = []  # interest paid

        self.savings_interest = []  # interest earned from savings

        self.om1 = []  # outside money on ECB account. Can be negative when new om money is created
        self.om2 = []  # outside money on private banks' account
        self.bank_profit = []  # bank profit: income from interest - payoff of loans and interests to ECB
        self.bank_spending = []  # money banks spend into the real economy
        self.bank_fixed = []  # fixed amount that banks spend into the real economy, adjusted for inflation
        self.bank_debt = []  # outstanding debt of banks to the ECB
        self.bank_payoff = []  # payoff of principal bank debt
        self.bank_interest = []  # interest paid to ecb

        # initial parameters
        self.initial_im2 = 100000.0  # initial amount of IM2. Needs to be > 0.

        self.lending_percentage_im2 = []
        self.lending_percentage_im_total = []
        self.im1_percentage_im_total = []
        self.im2_percentage_im_total = []
        self.savings_interest_percentage_im2 = []
        self.savings_interest_percentage_im_total = []
        self.debt_percentage_im2 = []
        self.debt_percentage_im_total = []
        self.created_percentage_im2 = []
        self.created_percentage_im_total = []


    def initialize(self):
        self.im1.clear()
        self.im2.clear()
        self.lending.clear()
        self.debt.clear()
        self.payoff.clear()
        self.interest.clear()
        self.new_im.clear()

        self.om1.clear()
        self.om2.clear()
        self.bank_profit.clear()
        self.bank_spending.clear()
        self.bank_fixed.clear()
        self.bank_debt.clear()
        self.bank_payoff.clear()
        self.bank_interest.clear()

        self.qe.clear()
        self.qe_trickle.clear()
        self.savings_interest.clear()

        self.lending_percentage_im2.clear()
        self.lending_percentage_im_total.clear()
        self.im1_percentage_im_total.clear()
        self.im2_percentage_im_total.clear()
        self.savings_interest_percentage_im2.clear()
        self.savings_interest_percentage_im_total.clear()
        self.debt_percentage_im2.clear()
        self.debt_percentage_im_total.clear()
        self.created_percentage_im2.clear()
        self.created_percentage_im_total.clear()

        self.im1.append(0.0)
        self.im2.append(self.initial_im2)
        self.lending.append(self.initial_im2)
        self.debt.append(self.initial_im2)
        self.payoff.append(0.0)
        self.interest.append(0.0)
        self.new_im.append(self.initial_im2)

        reserve = self.initial_im2 * self.mr
        self.om1.append(0.0 - reserve)  # reflects om money creation
        self.om2.append(reserve)
        self.bank_profit.append(0.0)
        self.bank_spending.append(0.0)
        self.bank_fixed.append(self.initial_fixed_spending)
        self.bank_debt.append(reserve)
        self.bank_payoff.append(0.0)
        self.bank_interest.append(0.0)

        self.qe.append(0.0)
        self.qe_trickle.append(0.0)

        self.savings_interest.append(0.0)

        self.calculate_percentages(0)


    def run_simulation(self, iterations):
        # write parameters
        if os.path.exists('./cockpit/supply/generated data/parameters.txt'):
            os.remove('./cockpit/supply/generated data/parameters.txt')

        f = open('./cockpit/supply/generated data/parameters.txt', 'w')
        f.write(f'Initial IM2 = {self.initial_im2:.2f}\n')
        f.write('\n')
        f.write(f'IM2 growth rate = {self.growth_rate * 100} %\n')
        f.write(f'Inflation = {self.inflation_rate * 100} %\n')
        f.write('\n')
        f.write(f'Commercial payback rate (% of debt) = {self.nbdr * 100} %\n')
        f.write(f'Commercial interest rate (% of debt) = {self.pbi * 100} %\n')
        f.write('\n')
        f.write(f'Saving rate (% of IM2) = {self.saving_rate * 100}\n')
        f.write(f'Savings interest rate = {self.savei * 100} %\n')
        f.write('\n')
        f.write(f'Minimal required reserve = {self.mr * 100} %\n')
        f.write(f'Minimal desired reserve (IM) = {self.min_bank_reserve * 100} %\n')
        f.write('\n')
        f.write(f'Bank payback rate (% of debt) = {self.pbdr * 100} %\n')
        f.write(f'Bank interest rate (% of debt) = {self.ecbi * 100} %\n')
        f.write('\n')
        f.write(f'Minimal \'new IM %\' on loans = {self.nmr * 100} %\n')
        f.write('\n')
        f.write(f'No loss = {self.no_loss}\n')
        if self.no_loss:
            f.write(f'Minimal profit from interest = {self.min_profit * 100} %\n')
        f.write('\n')
        f.write(f'Initial fixed spending = {self.initial_fixed_spending:.2f}\n')
        f.write(f'% profit spending = {self.pp * 100} %\n')
        f.write(f'% capital spending = {self.cp * 100} %\n')
        f.write('\n')
        f.write(f'QE spending mode: {self.qe_spending}\n')
        if self.qe_spending == QE_FIXED:
            f.write(f'Initial QE = {self.qe_fixed_initial:.2f}\n')
        elif self.qe_spending == QE_RELATIVE:
            f.write(f'QE % of debt = {self.qe_relative * 100} %\n')
        # f.write(f'QE is bank profit = {qe_profit}\n')
        if self.qe_spending != QE_NONE:
            f.write(f'QE trickle = {self.qe_trickle_rate * 100} %\n')
        f.close()

        # initialize data output file
        if os.path.exists(f'./cockpit/supply/generated data/{self.spending_mode}.csv'):
            os.remove(f'./cockpit/supply/generated data/{self.spending_mode}.csv')

        f = open(f'./cockpit/supply/generated data/{self.spending_mode}.csv', 'w')
        f.write('OM 1,OM 2,OM total,OM growth,')
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
            if i == 0:
                self.initialize()
            else:
                # copy previous state
                self.im1.append(self.im1[i - 1])
                self.im2.append(self.im2[i - 1])
                self.lending.append(0.0)
                self.debt.append(self.debt[i - 1])
                self.payoff.append(0.0)
                self.interest.append(0.0)
                self.new_im.append(self.new_im[i - 1])

                self.om1.append(self.om1[i - 1])
                self.om2.append(self.om2[i - 1])
                self.bank_profit.append(0.0)
                self.bank_spending.append(0.0)
                self.bank_fixed.append(self.bank_fixed[i - 1] + self.bank_fixed[i - 1] * self.inflation_rate)
                self.bank_debt.append(self.bank_debt[i - 1])
                self.bank_payoff.append(0.0)
                self.bank_interest.append(0.0)

                if self.qe_spending == QE_FIXED:
                    self.qe.append(self.qe[i - 1] + self.qe[i - 1] * self.inflation_rate)
                else:
                    self.qe.append(0.0)  # determine after debt has been processed

                self.qe_trickle.append(0.0)

                # calculate interest on savings from previous cycle and add to im2
                self.savings_interest.append(self.im2[i - 1] * self.saving_rate * self.savei)

                # determine growth
                growth = self.im2[i] * self.growth_rate +\
                                 self.im2[i] * self.growth_rate * self.inflation_rate +\
                                 self.im2[i] * self.inflation_rate
                target_im2 = self.im2[i] + growth

                # earn calculated interest
                self.im2[i] += self.savings_interest[i]
                self.im1[i] -= self.savings_interest[i]
                self.bank_profit[i] -= self.savings_interest[i]

                # calculate debt payoff and interest due
                self.payoff[i] = self.debt[i] * self.nbdr
                self.interest[i] = self.debt[i] * self.pbi

                self.bank_payoff[i] = self.bank_debt[i] * self.pbdr
                self.bank_interest[i] = self.bank_debt[i] * self.ecbi

                # pay non bank debts and interests. First clear newly created money
                if self.new_im[i] > self.payoff[i]:
                    self.new_im[i] -= self.payoff[i]
                else:
                    self.im1[i] += self.payoff[i] - self.new_im[i]
                    self.new_im[i] = 0

                self.im2[i] -= self.payoff[i] + self.interest[i]
                self.im1[i] += self.interest[i]
                self.debt[i] -= self.payoff[i]
                self.debt[i] = max(0.0, self.debt[i])  # avoid debt going negative due to rounding

                self.bank_profit[i] += self.interest[i] - self.bank_payoff[i] - self.bank_interest[i]

                # pay bank debts and interests, first use om2, then im1. If insufficient, get a new loan
                if self.om2[i] >= self.bank_payoff[i] + self.bank_interest[i]:
                    self.om2[i] -= self.bank_payoff[i] + self.bank_interest[i]
                else:
                    remaining_debt = self.bank_payoff[i] + self.bank_interest[i] - self.om2[i]
                    self.om2[i] = 0.0
                    if self.im1[i] >= remaining_debt:
                        self.im1[i] -= remaining_debt
                    else:
                        remaining_debt -= self.im1[i]
                        self.im1[i] = 0.0
                        self.bank_debt[i] += remaining_debt

                self.om1[i] += self.bank_interest[i]
                self.bank_debt[i] -= self.bank_payoff[i]
                self.bank_debt[i] = max(0.0, self.bank_debt[i])  # avoid bank debt going negative due to rounding

                # inject QE
                if self.qe_spending == QE_RELATIVE:
                    self.qe[i] = self.qe_relative * self.debt[i]

                self.qe_trickle[i] = self.qe[i] * self.qe_trickle_rate
                self.im1[i] += self.qe[i] - self.qe_trickle[i]
                self.im2[i] += self.qe_trickle[i]

                if self.qe_profit:
                    self.bank_profit[i] += self.qe[i] - self.qe_trickle[i]

                # bank spending
                if self.spending_mode == FIXED:
                    # spend the fixed amount if possible, otherwise spend all of im1
                    if self.im1[i] >= self.bank_fixed[i]:
                        self.bank_spending[i] = self.bank_fixed[i]
                    else:
                        self.bank_spending[i] = self.im1[i]
                elif self.spending_mode == PROFIT_PERCENTAGE:
                    if self.bank_profit[i] >= 0.0:
                        self.bank_spending[i] = self.pp * self.bank_profit[i]
                    else:  # profit can be negative
                        self.bank_spending[i] = 0, 0
                else:  # spending mode == CAPITAL_PERCENTAGE
                    self.bank_spending[i] = self.cp * self.im1[i]

                if self.no_loss:
                    self.bank_spending[i] = min(self.bank_spending[i], (1 - self.min_profit) * self.bank_profit[i])

                if self.bank_spending[i] + self.im2[i] > target_im2:  # spending would increase ima above desired amount
                    self.bank_spending[i] = max(0.0, target_im2 - self.im2[i])

                self.im1[i] -= self.bank_spending[i]
                self.im2[i] += self.bank_spending[i]
                self.bank_profit[i] -= self.bank_spending[i]

                # grow economy through lending if needed
                self.lending[i] = max(0.0, target_im2 - self.im2[i])

                if self.lending[i] > 0.0:
                    self.im2[i] += self.lending[i]
                    self.debt[i] += self.lending[i]
                    create_im = self.lending[i] * self.nmr
                    min_desired_reserve = self.min_bank_reserve * self.debt[i]

                    # check im1 reserve
                    if self.im1[i] - self.lending[i] + create_im < min_desired_reserve:
                        if self.im1[i] >= min_desired_reserve:
                            create_im += self.lending[i] - create_im - self.im1[i] + min_desired_reserve
                        else:
                            create_im = self.lending[i]

                    self.im1[i] -= self.lending[i] - create_im
                    self.new_im[i] += create_im

                # update om in accordance to mr
                min_reserve = self.mr * self.debt[i]

                if self.om2[i] + self.im1[i] < min_reserve:
                    reserve_need = min_reserve - self.om2[i] - self.im1[i]
                    om_growth = max(0.0, reserve_need)

                    self.om1[i] -= reserve_need
                    self.om2[i] += reserve_need
                    self.bank_debt[i] += reserve_need
                else:
                    om_growth = 0.0

                self.calculate_percentages(i)

                f.write(f'{deflate(self.inflation_rate, self.om1[i], i):.2f},\
                    {deflate(self.inflation_rate, self.om2[i], i):.2f},\
                    {deflate(self.inflation_rate, self.om1[i] + self.om2[i], i):.2f},\
                    {deflate(self.inflation_rate, self.om1[1] + self.om2[i], i) - deflate(self.inflation_rate, self.om1[i - 1] + self.om2[i - 1], i - 1):.2f},\
                    {deflate(self.inflation_rate, self.qe[i], i):.2f},\
                    {deflate(self.inflation_rate, self.qe_trickle_rate * self.qe[i], i):.2f},\
                    {deflate(self.inflation_rate, self.bank_spending[i], i):.2f},\
                    {deflate(self.inflation_rate, self.bank_profit[i], i):.2f},{self.bank_debt[i]:.2f},\
                    {self.bank_payoff[i]:.2f},\
                    {self.bank_interest[i]:.2f},\
                    {deflate(self.inflation_rate, self.im1[i], i):.2f},\
                    {deflate(self.inflation_rate, self.im2[i], i):.2f},\
                    {deflate(self.inflation_rate, self.savings_interest[i], i):.2f},\
                    {deflate(self.inflation_rate, self.new_im[i], i)},\
                    {deflate(self.inflation_rate, self.debt[i], i):.2f},\
                    {deflate(self.inflation_rate, self.payoff[i], i):.2f},\
                    {deflate(self.inflation_rate, self.interest[i], i):.2f},\
                    {deflate(self.inflation_rate, self.im2[i], i) - deflate(self.inflation_rate, self.im2[i - 1], i - 1):.2f},\
                    {deflate(self.inflation_rate, self.lending[i], i):.2f},\
                    {deflate(self.inflation_rate, self.im1[i] + self.im2[i], i):.2f},\
                    {self.lending_percentage_im2[i]:.2f},\
                    {self.lending_percentage_im_total[i]:.2f},\
                    {self.im1_percentage_im_total[i]:.2f},\
                    {self.im2_percentage_im_total[i]:.2f},\
                    {self.savings_interest_percentage_im2[i]:.2f},\
                    {self.savings_interest_percentage_im_total[i]:.2f},\
                    {self.debt_percentage_im2[i]:.2f},\
                    {self.debt_percentage_im_total[i]:.2f},\
                    {self.created_percentage_im2[i]:.2f},\
                    {self.created_percentage_im_total[i]:.2f}\n')

        f.close()


    def calculate_percentages(self, i):
        im_total = self.im1[i] + self.im2[i]
        self.lending_percentage_im2.append(self.lending[i] * 100 / self.im2[i])
        self.lending_percentage_im_total.append(self.lending[i] * 100 / im_total)

        self.im1_percentage_im_total.append(self.im1[i] * 100 / im_total)
        self. im2_percentage_im_total.append(self.im2[i] * 100 / im_total)

        self.savings_interest_percentage_im2.append(self.savings_interest[i] * 100 / self.im2[i])
        self.savings_interest_percentage_im_total.append(self.savings_interest[i] * 100 / im_total)

        self.debt_percentage_im2.append(self.debt[i] * 100 / self.im2[i])
        self.debt_percentage_im_total.append(self.debt[i] * 100 / im_total)

        self.created_percentage_im2.append(self.new_im[i] * 100 / self.im2[i])
        self.created_percentage_im_total.append(self.new_im[i] * 100 / im_total)


    def get_im1_growth(self, do_deflate):
        return get_growth(self.im1, do_deflate, self.inflation_rate)


    def get_im2_growth(self, do_deflate):
        return get_growth(self.im2, do_deflate, self.inflation_rate)


    def get_im_growth(self, do_deflate):
        im = []

        for cycle in range(len(self.im1)):
            im.append(self.im1[cycle] + self.im2[cycle])

        return get_growth(im, do_deflate, self.inflation_rate)


    def get_om1_growth(self, do_deflate):
        return get_growth(self.om1, do_deflate, self.inflation_rate)


    def get_om2_growth(self, do_deflate):
        return get_growth(self.om2, do_deflate, self.inflation_rate)


    def get_om_growth(self, do_deflate):
        om = []

        for cycle in range(len(self.om1)):
            om.append(self.om1[cycle] + self.om2[cycle])

        return get_growth(om, do_deflate, self.inflation_rate)
