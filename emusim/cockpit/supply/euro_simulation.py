# module euro_simulation
# percentages are represented as a fractional number between 0 and 1, 0 being 0%, 0.5 being 50% and 1 being 100%

import os
from emusim.cockpit.supply.constants import *
from emusim.cockpit.supply.simulation import Simulation

class Euro_MS_Simulation(Simulation):

    def __init__(self):
        super().__init__()

        # initial parameters
        self.crash = False
        self.crash_cycle = 0

        self.minimum_reserve = 0.04  # minimum reserve
        self.maximum_reserve = self.minimum_reserve  # maximum % reserve a bank wants to hold in OM. This influences how much money will be used to buy financial assets.

        self.lending_satisfaction_rate = 1.0  # percentage of required lending that is actually executed

        self.desired_initial_im = 100000.0  # initial desired amount of IM. Needs to be > 0.
        self.initial_im = self.desired_initial_im * self.lending_satisfaction_rate  # initial real amount of IM
        self.initial_debt = self.initial_im
        self.initial_created_im = self.initial_im

        self.initial_private_assets = 0.0

        self.initial_created_reserve = self.initial_im * self.minimum_reserve
        self.initial_bank_reserve = self.initial_created_reserve
        self.initial_bank_debt = self.initial_created_reserve

        self.initial_bank_assets = 0.0

        self.desired_growth_rate = 0.030  # desired actual_growth rate of available money (IM2). This is money that circulates in the real economy
        self.growth_target = GROW_CURRENT

        self.link_growth_inflation = False
        self.growth_inflation_influence = 1.0

        self.interest_percentage_bank_income = 1.0  # how much of the bank's income comes from interest

        self.initial_fixed_spending = 1000.0  # initial spending if bank spending mode is FIXED
        self.profit_spending = 0.02  # percentage of profit that banks spend into the real economy
        self.reserve_spending = 0.02  #percentage of bank reserves that are spent in the real economy
        self.capital_spending = 0.02  # percentage of capital (reserves + financial assets) that banks spend into the real economy

        self.bank_payback_cycles = 1  # bank payback cycles
        self.private_payback_cycles = 20  # private payback cycles

        self.ecb_ir = 0.01                  # ECB interest rate
        self.ecb_savings_ir_mr = 0.015      # ECB interest rate on minimal bank reserves
        self.ecb_savings_ir_reserve = 0.0   # ECB interest rate on surplus bank reserves

        self.bank_ir = 0.025                # Bank interest rate
        self.asset_trickle_rate = 0.05      # Amount of money in financial assets that trickles to the real economy
        self.savings_ir = 0.005             # Bank interest on savings
        self.saving_rate = 0.2              # % of IM which is saved.
        self.saving_asset_percentage = 0.2  # % of savings that are invested in financial assets

        self.minimum_new_money = 0.80       # minimum % of money of a loan that is newly created. The rest is taken from im if possible.
        self.maximum_new_money = 1.00       # maximium % of money of a loan that is newly created. The rest is taken from im if possible.

        self.no_loss = True  # whether or not banks are ok running a loss
        self.min_profit = 0.20  # minimum % in income (from interest) that is retained as profit (only if no loss is true).

        self.spending_mode = FIXED  # bank spending mode
        self.max_spending = 0.2     # max bank spending % of im

        self.qe_spending_mode = QE_RELATIVE  # QE spending mode
        self.qe_trickle_rate = 1.00  # percentage of QE that immediately flows through to IM2. Can be interpreted as a form of helicopter money.
        self.qe_profit = False  # whether or not qe is interpreted as bank profit.
        self.qe_fixed_initial = 0.0  # initial fixed QE
        self.qe_relative = 0.025  # relative qe in % of IM2
        self.qe = []  # QE injected by ECB, adjusted for inflation rate. This amount is subtracted from created_bank_reserve to keep track of money creation by ECB.
        self.qe_trickle = []

        self.asset_trickle_rate = 0.05          # percentage of asset capital that trickles to the real economy
        self.asset_trickle_mode = ASSET_GROWTH  # determines how the asset trickle is calculated

        self.financial_assets = []              # Total money available in financial assets from banks and IM
        self.bank_asset_investments = []        # total amount of money that has been invested in assets by banks. Not affected by asset trickle
        self.private_asset_investments = []     # IM that has been invested in financial assets. Not affected by asset trickle.
        self.total_asset_investments = []       # Sum of bank and private asset investments
        self.asset_investment_growth = []       # Total amount of money that flows into financial assets per cycle
        self.asset_trickle = []                 # amount of money that trickles back to IM. From both bank and private assets

        self.desired_im = []  # Money that would be available in the real economy if required lending would be met exactly.
        self.im = []  # Money actually available to the real economy

        self.required_lending = []  # lending amount that is required to maintain money supply
        self.lending = []  # money that has been borrowed per cycle
        self.banking_costs = []  # money spent on banking costs other than paying off loans
        self.created_im = []  # money that has been created
        self.debt = []  # outstanding debt on which interest is paid
        self.private_payoff = []  # private_payoff of principal debt
        self.interest = []  # interest paid

        self.savings = []           # amount that has been saved. This is part of IM
        self.savings_interest = []  # interest earned from savings

        self.total_inflow = []      # total inflow in im
        self.total_outflow = []     # total outflow from im

        self.created_bank_reserve = []      # bank reserve money created by the ECB
        self.bank_reserve = []              # Bank reserves
        self.bank_income = []               # Bank income
        self.bank_profit = []               # bank profit: income from interest - private_payoff of loans and interests to ECB
        self.bank_spending = []             # money banks spend into the real economy
        self.bank_fixed = []                # fixed amount that banks spend into the real economy, adjusted for inflation rate
        self.bank_lending = []              # money lent by the banks from the ECB
        self.bank_debt = []                 # outstanding debt of banks to the ECB
        self.bank_payoff = []               # private_payoff of principal bank debt
        self.bank_interest = []             # interest paid to ecb

        # Percentages
        self.required_growth = [] # required growth to fulfill initial parameters
        self.actual_growth = []  # actual actual_growth
        self.actual_inflation = []  # actual inflation

        self.required_lending_percentage_im = []
        self.lending_percentage_im = []
        self.lending_percentage_total_money = []
        self.required_lending_percentage_total_money = []

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
        self.asset_trickle_percentage_im = []
        self.qe_trickle_percentage_im = []

        self.total_inflow_percentage_im = []

        self.payoff_percentage_im = []
        self.interest_percentage_im = []
        self.banking_costs_percentage_im = []

        self.total_outflow_percentage_im = []

        self.debt_percentage_im = []
        self.debt_percentage_total_money = []

        self.bank_debt_percentage_bank_reserve = []
        self.bank_debt_percentage_total_money = []

        self.bank_profit_percentage_bank_income = []
        self.bank_profit_percentage_im = []

        self.bank_spending_percentage_profit = []
        self.bank_spending_percentage_im = []

        self.created_im_percentage_im = []
        self.created_im_percentage_total_money = []

        self.created_bank_reserve_percentage_bank_reserve = []
        self.created_bank_reserve_percentage_total_money = []
        self.created_money_percentage_total_money = []


    def initialize(self):
        super(Euro_MS_Simulation, self).initialize()

        self.crash = False

        self.desired_im.clear()
        self.im.clear()

        self.required_growth.clear()
        self.actual_growth.clear()

        self.required_lending.clear()
        self.lending.clear()
        self.banking_costs.clear()
        self.debt.clear()
        self.private_payoff.clear()
        self.interest.clear()
        self.created_im.clear()

        self.created_bank_reserve.clear()
        self.bank_reserve.clear()
        self.bank_income.clear()
        self.bank_profit.clear()
        self.bank_spending.clear()
        self.bank_fixed.clear()
        self.bank_lending.clear()
        self.bank_debt.clear()
        self.bank_payoff.clear()
        self.bank_interest.clear()

        self.financial_assets.clear()
        self.bank_asset_investments.clear()
        self.private_asset_investments.clear()
        self.total_asset_investments.clear()
        self.asset_investment_growth.clear()
        self.asset_trickle.clear()

        self.qe.clear()
        self.qe_trickle.clear()

        self.savings_interest.clear()

        self.total_inflow.clear()
        self.total_outflow.clear()

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
        self.asset_trickle_percentage_im.clear()
        self.qe_trickle_percentage_im.clear()

        self.total_inflow_percentage_im.clear()

        self.debt_percentage_im.clear()
        self.debt_percentage_total_money.clear()

        self.payoff_percentage_im.clear()
        self.interest_percentage_im.clear()
        self.banking_costs_percentage_im.clear()

        self.total_outflow_percentage_im.clear()

        self.bank_profit_percentage_bank_income.clear()
        self.bank_profit_percentage_im.clear()

        self.bank_spending_percentage_profit.clear()
        self.bank_spending_percentage_im.clear()

        self.bank_debt_percentage_bank_reserve.clear()
        self.bank_debt_percentage_total_money.clear()

        self.created_im_percentage_im.clear()
        self.created_im_percentage_total_money.clear()

        self.created_bank_reserve_percentage_bank_reserve.clear()
        self.created_bank_reserve_percentage_total_money.clear()
        self.created_money_percentage_total_money.clear()

        self.desired_im.append(self.desired_initial_im)
        self.im.append(self.initial_im)
        self.required_growth.append(self.desired_growth_rate * 100)
        self.actual_growth.append(self.desired_growth_rate * 100)  # percentage
        self.required_lending.append(self.initial_im)
        self.lending.append(self.initial_im)
        self.banking_costs.append(0.0)
        self.debt.append(self.initial_debt)
        self.private_payoff.append(0.0)

        for cycle in range(0, self.private_payback_cycles):
            self.private_payoff.append(self.initial_debt / self.private_payback_cycles)

        self.interest.append(0.0)
        self.created_im.append(self.initial_created_im)

        self.created_bank_reserve.append(self.initial_created_reserve)  # reflects bank_reserve money creation
        self.bank_reserve.append(self.initial_bank_reserve)
        self.bank_income.append(0.0)
        self.bank_profit.append(0.0)
        self.bank_spending.append(0.0)
        self.bank_lending.append(self.initial_bank_reserve)
        self.bank_fixed.append(self.initial_fixed_spending)
        self.bank_debt.append(self.initial_bank_debt)
        self.bank_payoff.append(0.0)

        for cycle in range(0, self.bank_payback_cycles):
            self.bank_payoff.append(self.initial_bank_debt / self.bank_payback_cycles)

        self.bank_interest.append(0.0)

        self.financial_assets.append(self.initial_bank_assets + self.initial_private_assets)
        self.bank_asset_investments.append(self.initial_bank_assets)
        self.private_asset_investments.append(self.initial_private_assets)
        self.total_asset_investments.append(self.initial_bank_assets + self.initial_private_assets)
        self.asset_investment_growth.append(0.0)
        self.asset_trickle.append(0.0)

        if self.qe_spending_mode == QE_FIXED:
            self.qe.append(self.qe_fixed_initial)
        else:
            self.qe.append(0.0)

        self.qe_trickle.append(0.0)

        self.savings.append(0.0)
        self.savings_interest.append(0.0)

        self.total_inflow.append(0.0)
        self.total_outflow.append(0.0)

        self.calculate_percentages(0)


    def run_simulation(self, iterations):
        for i in range(iterations):
            self.crash_cycle = i

            if i == 0:
                self.initialize()
            else:
                if self.im[i - 1] <= 0:
                    self.crash = True
                    self.crash_cycle -= 1
                    break

                # copy previous state
                if len(self.private_payoff) <= i:
                    self.private_payoff.append(0.0)

                if len(self.bank_payoff) <= i:
                    self.bank_payoff.append(0.0)

                self.desired_im.append(self.desired_im[i - 1])
                self.im.append(self.im[i - 1])
                self.actual_growth.append(0.0)
                self.inflation_rate.append(self.inflation_rate[i - 1])
                self.required_lending.append(0.0)
                self.lending.append(0.0)
                self.banking_costs.append(0.0)
                self.debt.append(self.debt[i - 1])
                self.interest.append(0.0)
                self.created_im.append(self.created_im[i - 1])

                self.created_bank_reserve.append(self.created_bank_reserve[i - 1])
                self.bank_reserve.append(self.bank_reserve[i - 1])
                self.bank_income.append(0.0)
                self.bank_profit.append(0.0)
                self.bank_spending.append(0.0)
                self.bank_fixed.append(self.bank_fixed[i - 1] + self.bank_fixed[i - 1] * self.inflation_rate[i])
                self.bank_lending.append(0.0)
                self.bank_debt.append(self.bank_debt[i - 1])
                self.bank_interest.append(0.0)
                self.savings.append(self.savings[i - 1])

                self.financial_assets.append(self.financial_assets[i - 1])
                self.bank_asset_investments.append(self.bank_asset_investments[i - 1])
                self.private_asset_investments.append(self.private_asset_investments[i - 1])
                self.total_asset_investments.append(0.0)
                self.asset_investment_growth.append(0.0)

                self.total_inflow.append(0.0)
                self.total_outflow.append(0.0)

                self.qe_trickle.append(0.0)

                # determine asset trickle
                if self.asset_trickle_mode == ASSET_GROWTH:
                    self.asset_trickle.append(max(0.0, self.asset_investment_growth[i - 1] * self.asset_trickle_rate))
                else:  # ASSET_CAPITAL
                    self.asset_trickle.append(max(0.0, self.financial_assets[i - 1] * self.asset_trickle_rate))

                if self.qe_spending_mode == QE_FIXED:
                    self.qe.append(self.qe[i - 1] + self.qe[i - 1] * self.inflation_rate[i])
                else:
                    self.qe.append(0.0)  # determine after debt has been processed

                # calculate interest on savings from previous cycle and add to im
                self.savings_interest.append(self.savings[i - 1] * self.savings_ir)

                # determine desired growth
                self.desired_im[i] += self.desired_im[i] * self.desired_growth_rate + \
                                      self.desired_im[i] * self.desired_growth_rate * self.inflation_rate[i] + \
                                      self.desired_im[i] * self.inflation_rate[i]

                desired_growth = 0

                if self.growth_target == GROW_CURRENT:
                    desired_growth = self.im[i] * self.desired_growth_rate + \
                                     self.im[i] * self.desired_growth_rate * self.inflation_rate[i] + \
                                     self.im[i] * self.inflation_rate[i]
                else:  # self.growth_target == GROW_INITIAL:
                    desired_growth = self.desired_im[i] - self.im[i]

                target_im = max(0.0, self.im[i] + desired_growth)

                # earn calculated interest
                self.im[i] += self.savings_interest[i]
                self.bank_reserve[i] -= self.savings_interest[i]
                self.bank_profit[i] -= self.savings_interest[i]

                # calculate debt, interest due and banking costs
                self.interest[i] = self.debt[i] * self.bank_ir
                self.banking_costs[i] = self.interest[i] / self.interest_percentage_bank_income * (1 - self.interest_percentage_bank_income)

                self.bank_interest[i] = self.bank_debt[i] * self.ecb_ir

                # pay non bank debts, interests and banking costs. First clear newly created money
                if self.created_im[i] > self.private_payoff[i]:
                    self.created_im[i] -= self.private_payoff[i]
                else:
                    self.bank_reserve[i] += self.private_payoff[i] - self.created_im[i]
                    self.created_im[i] = 0

                self.im[i] -= self.private_payoff[i] + self.interest[i] + self.banking_costs[i]
                self.debt[i] -= self.private_payoff[i]
                self.debt[i] = max(0.0, self.debt[i])  # avoid debt going negative due to rounding

                self.bank_income[i] += self.interest[i] + self.banking_costs[i]
                self.bank_reserve[i] += self.interest[i] + self.banking_costs[i]
                self.bank_profit[i] += self.interest[i] + self.banking_costs[i]

                # generate interest from ECB
                min_reserve = self.debt[i - 1] * self.minimum_reserve
                create_interest = 0

                if self.bank_reserve[i - 1] <= min_reserve:
                    create_interest = self.bank_reserve[i - 1] * self.ecb_savings_ir_mr
                else:
                    create_interest = min_reserve * self.ecb_savings_ir_mr  # interest on minimum reserve
                    create_interest += (self.bank_reserve[i - 1] - min_reserve) * self.ecb_savings_ir_reserve # interest on surplus

                self.bank_reserve[i] += create_interest
                self.bank_profit[i] += create_interest

                if create_interest > 0:
                    self.created_bank_reserve[i] += create_interest
                    self.bank_income[i] += create_interest
                else:
                    self.im[i] -= create_interest # interest paid by banks goes to real economy

                # pay bank debts and interests. If insufficient, sell financial assets (first) or get a new loan
                if self.bank_reserve[i] >= self.bank_payoff[i] + self.bank_interest[i]:
                    self.bank_reserve[i] -= self.bank_payoff[i] + self.bank_interest[i]
                else:
                    remaining_debt = self.bank_payoff[i] + self.bank_interest[i] - self.bank_reserve[i]
                    self.bank_reserve[i] = 0.0

                    asset_reserve = min(self.financial_assets[i], self.bank_asset_investments[i])

                    if asset_reserve >= remaining_debt:
                        self.financial_assets[i] -= remaining_debt
                        self.bank_asset_investments[i] -= remaining_debt
                    else:
                        remaining_debt -= asset_reserve
                        self.bank_asset_investments[i] -= asset_reserve
                        self.financial_assets[i] -= asset_reserve
                        self.bank_lending[i] = remaining_debt
                        self.bank_debt[i] += remaining_debt
                        self.created_bank_reserve[i] += remaining_debt

                self.bank_debt[i] -= self.bank_payoff[i]
                self.bank_debt[i] = max(0.0, self.bank_debt[i])  # avoid bank debt going negative due to rounding

                self.created_bank_reserve[i] -= self.bank_payoff[i]
                self.created_bank_reserve[i] = max(0.0, self.created_bank_reserve[i])  # avoid created om going negative due to rounding

                self.bank_profit[i] -= self.bank_payoff[i] + self.bank_interest[i]

                # trickle assets
                self.financial_assets[i] -= self.asset_trickle[i]
                self.im[i] += self.asset_trickle[i]

                # inject QE
                if self.qe_spending_mode != QE_NONE:
                    if self.qe_spending_mode == QE_RELATIVE:
                        self.qe[i] = self.qe_relative * self.debt[i]

                    self.qe_trickle[i] = self.qe[i] * self.qe_trickle_rate
                    self.bank_reserve[i] += self.qe[i] - self.qe_trickle[i]
                    self.created_bank_reserve[i] += self.qe[i] - self.qe_trickle[i]
                    self.created_im[i] += self.qe_trickle[i]
                    self.im[i] += self.qe_trickle[i]

                    if self.qe_profit:
                        self.bank_profit[i] += self.qe[i] - self.qe_trickle[i]

                # bank spending
                if self.spending_mode == FIXED:
                    # spend the fixed amount if possible, otherwise spend all of bank reserve
                    if self.bank_reserve[i] >= self.bank_fixed[i]:
                        self.bank_spending[i] = min(self.bank_fixed[i], self.max_spending * target_im)
                    else:
                        self.bank_spending[i] = min(self.bank_reserve[i], self.max_spending * target_im)
                elif self.spending_mode == PROFIT_PERCENTAGE:
                    if self.bank_profit[i] >= 0.0:
                        self.bank_spending[i] = min(self.profit_spending * self.bank_profit[i], self.max_spending * target_im)
                    else:  # profit can be negative
                        self.bank_spending[i] = 0.0
                elif self.spending_mode == RESERVE_PERCENTAGE:
                    self.bank_spending[i] = min(self.bank_reserve[i] * self.reserve_spending, self.max_spending * target_im)
                else:  # spending mode == CAPITAL_PERCENTAGE
                    self.bank_spending[i] = min((self.bank_reserve[i] + min(self.financial_assets[i], self.bank_asset_investments[i])) * self.capital_spending, self.max_spending * target_im)

                if self.no_loss:
                    self.bank_spending[i] = min(self.bank_spending[i], (1 - self.min_profit) * self.bank_profit[i])
                    self.bank_spending[i] = max (0.0, self.bank_spending[i])  # bank can not spend negative amounts

                if self.bank_spending[i] + self.im[i] > target_im:  # spending would increase im above desired amount
                    self.bank_spending[i] = max(0.0, target_im - self.im[i])

                if self.spending_mode != CAPITAL_PERCENTAGE:
                    self.bank_reserve[i] -= self.bank_spending[i]
                else: # spend from financial assets first
                    if self.financial_assets[i] >= self.bank_spending[i]:
                        self.financial_assets[i] -= self.bank_spending[i]
                        self.bank_asset_investments[i] -= self.bank_spending[i]
                    else:
                        reserve_spending = self.bank_spending[i] - self.financial_assets[i]
                        self.bank_asset_investments[i] -= self.financial_assets[i]
                        self.financial_assets[i] = 0
                        self.bank_reserve[i] -= reserve_spending

                self.im[i] += self.bank_spending[i]
                self.bank_profit[i] -= self.bank_spending[i]

                # save money and invest in financial assets (IM)
                target_savings = target_im * self.saving_rate
                self.savings[i] += target_savings * (1 - self.saving_asset_percentage) - self.savings[i]
                target_private_assets = target_savings * self.saving_asset_percentage
                asset_investment = target_private_assets - self.private_asset_investments[i]
                self.private_asset_investments[i] += asset_investment
                self.financial_assets[i] += asset_investment
                self.im[i] -= asset_investment
                self.asset_investment_growth[i] += asset_investment

                # grow economy through lending if needed
                max_desired_reserve = self.maximum_reserve * self.debt[i]
                self.required_lending[i] = max(0.0, target_im - self.im[i])
                self.lending[i] = self.required_lending[i] * self.lending_satisfaction_rate

                if self.lending[i] > 0.0:  # distribute payback tranches
                    payback_tranch = self.lending[i] / self.private_payback_cycles

                    for cycle in range(i + 1, i + 1 + self.private_payback_cycles):
                        if len(self.private_payoff) > cycle:
                            self.private_payoff[cycle] += payback_tranch
                        else:
                            self.private_payoff.append(payback_tranch)

                    self.im[i] += self.lending[i]
                    self.debt[i] += self.lending[i]
                    min_create_im = self.lending[i] * self.minimum_new_money
                    max_create_im = self.lending[i] * self.maximum_new_money
                    create_im = max_create_im

                    max_desired_reserve = self.maximum_reserve * self.debt[i] # update max reserve

                    # check bank reserve
                    if self.bank_reserve[i] - self.lending[i] + max_create_im > max_desired_reserve:
                        create_im = max(min_create_im, max_desired_reserve - self.bank_reserve[i] + self.lending[i])

                    self.bank_reserve[i] -= self.lending[i] - create_im
                    self.created_im[i] += create_im

                if self.bank_reserve[i] > max_desired_reserve:
                    surplus = self.bank_reserve[i] - max_desired_reserve
                    self.financial_assets[i] += surplus
                    self.bank_asset_investments[i] += surplus
                    self.asset_investment_growth[i] += surplus
                    self.bank_reserve[i] -= surplus

                # update bank_reserve in accordance to minimum_reserve
                min_reserve = self.minimum_reserve * self.debt[i]

                if self.bank_reserve[i] < min_reserve:
                    available_assets = min(self.bank_asset_investments[i], self.financial_assets[i])
                    ecb_lending = max(0.0, min_reserve - (self.bank_reserve[i] + available_assets))

                    if ecb_lending > 0:  # distribute payback tranches
                        payback_tranch = ecb_lending / self.bank_payback_cycles

                        for cycle in range(i + 1, i + 1 + self.bank_payback_cycles):
                            if len(self.bank_payoff) > cycle:
                                self.bank_payoff[cycle] += payback_tranch
                            else:
                                self.bank_payoff.append(payback_tranch)

                    asset_transfer = min(available_assets, min_reserve - self.bank_reserve[i])

                    self.bank_asset_investments[i] -= asset_transfer
                    self.financial_assets[i] -= asset_transfer
                    self.asset_investment_growth[i] -= asset_transfer
                    self.bank_reserve[i] += asset_transfer

                    self.created_bank_reserve[i] += ecb_lending
                    self.bank_reserve[i] += ecb_lending
                    self.bank_debt[i] += ecb_lending

                # calculate totals
                self.total_inflow[i] = self.bank_interest[i] + self.savings_interest[i] + self.asset_trickle[i] + self.qe_trickle[i] + self.bank_spending[i]
                self.total_outflow[i] = self.private_payoff[i] + self.interest[i] + self.banking_costs[i]
                self.total_asset_investments[i] = self.bank_asset_investments[i] + self.private_asset_investments[i]

                self.calculate_percentages(i)

        #self.write_parameters()
        #self.write_raw_data(iterations)


    def calculate_percentages(self, i):
        total_money = self.financial_assets[i] + self.bank_reserve[i] + self.im[i]

        if i > 0:
            self.actual_growth[i] = (self.im[i] - (self.im[i - 1] + self.im[i - 1] * self.inflation_rate[i])) * 100 \
                                    / (self.im[i - 1] + self.im[i - 1] * self.inflation_rate[i])
            self.required_growth.append((self.desired_im[i] - (self.im[i - 1] + self.im[i - 1] * self.inflation_rate[i])) * 100 \
                                    / (self.im[i - 1] + self.im[i - 1] * self.inflation_rate[i]))

            if self.link_growth_inflation:
                growth_gap = self.actual_growth[i] / 100 - self.desired_growth_rate
                self.inflation_rate[i] = self.initial_inflation_rate + growth_gap * self.growth_inflation_influence

        self.actual_inflation.append(self.inflation_rate[i] * 100)

        self.required_lending_percentage_im.append(self.required_lending[i] * 100 / self.im[i])
        self.lending_percentage_im.append(self.lending[i] * 100 / self.im[i])
        self.required_lending_percentage_total_money.append(self.required_lending[i] * 100 / total_money)
        self.lending_percentage_total_money.append(self.lending[i] * 100 / total_money)

        if self.debt[i] != 0:
            self.bank_reserve_percentage_debt.append(self.bank_reserve[i] * 100 / self.debt[i])
        else:
            self.bank_reserve_percentage_debt.append(0.0)

        if self.bank_reserve[i] != 0:
            self.bank_lending_percentage_bank_reserve.append(self.bank_lending[i] * 100 / self.bank_reserve[i])
        else:
            self.bank_lending_percentage_bank_reserve.append(0.0)

        self.bank_lending_percentage_total_money.append(self.bank_lending[i] * 100 / total_money)

        self.im_percentage_total_money.append(self.im[i] * 100 / total_money)
        self.bank_reserve_percentage_total_money.append(self.bank_reserve[i] * 100 / total_money)
        self.asset_percentage_total_money.append(self.financial_assets[i] * 100 / total_money)

        if self.bank_income[i] != 0:
            self.bank_profit_percentage_bank_income.append(self.bank_profit[i] * 100 / self.bank_income[i])
        else:
            self.bank_profit_percentage_bank_income.append(100.0)

        if self.bank_profit[i] != 0:
            self.bank_spending_percentage_profit.append(self.bank_spending[i] * 100 / self.bank_profit[i])
        else:
            self.bank_spending_percentage_profit.append(100.0)

        self.bank_spending_percentage_im.append(self.bank_spending[i] * 100 / self.im[i])

        self.bank_profit_percentage_im.append(self.bank_profit[i] * 100 / self.im[i])

        self.savings_interest_percentage_im.append(self.savings_interest[i] * 100 / self.im[i])
        self.savings_interest_percentage_total_money.append(self.savings_interest[i] * 100 / total_money)

        self.ecb_interest_percentage_im.append(self.bank_interest[i] * 100 / self.im[i])
        self.ecb_interest_percentage_total_money.append(self.bank_interest[i] * 100 / total_money)

        self.asset_trickle_percentage_im.append(self.asset_trickle[i] * 100 / self.im[i])
        self.qe_trickle_percentage_im.append(self.qe_trickle[i] * 100 / self.im[i])

        self.total_inflow_percentage_im.append(self.total_inflow[i] * 100 / self.im[i])

        self.payoff_percentage_im.append(self.private_payoff[i] * 100 / self.im[i])
        self.interest_percentage_im.append(self.interest[i] * 100 / self.im[i])
        self.banking_costs_percentage_im.append(self.banking_costs[i] * 100 / self.im[i])

        self.total_outflow_percentage_im.append(self.total_outflow[i] * 100 / self.im[i])

        self.debt_percentage_im.append(self.debt[i] * 100 / self.im[i])
        self.debt_percentage_total_money.append(self.debt[i] * 100 / total_money)

        if self.bank_reserve[i] != 0:
            self.bank_debt_percentage_bank_reserve.append(self.bank_debt[i] * 100 / self.bank_reserve[i])
            self.created_bank_reserve_percentage_bank_reserve.append(self.created_bank_reserve[i] * 100 / self.bank_reserve[i])
        else:
            self.bank_debt_percentage_bank_reserve.append(0.0)
            self.created_bank_reserve_percentage_bank_reserve.append(0.0)

        self.bank_debt_percentage_total_money.append(self.bank_debt[i] * 100 / total_money)

        self.created_im_percentage_im.append(self.created_im[i] * 100 / self.im[i])
        self.created_im_percentage_total_money.append(self.created_im[i] * 100 / total_money)

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
            f.write(f'IM2 actual_growth rate = {self.desired_growth_rate * 100} %\n')
            f.write(f'Inflation = {self.initial_inflation_rate * 100} %\n')
            f.write('\n')
            f.write(f'Commercial payback rate (% of debt) = {self.private_payback_cycles} %\n')
            f.write(f'Commercial interest rate (% of debt) = {self.bank_ir * 100} %\n')
            f.write('\n')
            f.write(f'Saving rate (% of IM2) = {self.saving_rate * 100}\n')
            f.write(f'Savings interest rate = {self.savings_ir * 100} %\n')
            f.write('\n')
            f.write(f'Minimal required reserve = {self.minimum_reserve * 100} %\n')
            f.write(f'Maximum desired reserve (IM) = {self.maximum_reserve * 100} %\n')
            f.write('\n')
            f.write(f'Bank payback rate (% of debt) = {self.bank_payback_cycles * 100} %\n')
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
            f.write('Created OM,OM,OM actual_growth,')
            f.write('QE,QE trickle,')
            f.write('Bank spending,Bank profit,Bank debt,Bank private_payoff,Bank interest,')
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
                    {self.deflate(self.private_payoff[i], i):.2f},\
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