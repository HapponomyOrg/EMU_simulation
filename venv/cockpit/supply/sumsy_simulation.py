# module sumsy_simulation

from cockpit.supply.constants import *

class SumSy_MS_Simulation:

    def __init__(self):
        self.initial_population = 5000
        self.population_growth = 0.0
        self.initial_money_mass = 100000.0
        self.inflation = 0.0
        self.initial_income = 2000.0
        self.num_dem_tiers = MAX_DEM_TIERS
        self.initial_dem_tiers = {0: 50000.0,
                                  1: 250000.0,
                                  2: 1000000.0,
                                  3: 5000000.0,
                                  4: 10000000.0}
        self.dem_rates = {0: 0.01,
                          1: 0.05,
                          2: 0.1,
                          3: 0.5,
                          4: 0.9}
        self.common_good_spending = NONE
        self.initial_common_good_budget = 0.0

        self.population = []            # total population
        self.income = []                # income adjusted for inflation
        self.money_mass = []            # total monetary mas
        self.demurrage = []             # amount of demurrage paid
        self.dem_tiers = []             # demurrage tiers
        self.new_money = []             # money added to the total monetary mass
        self.common_good_budget = []    # money needed for the common good project
        self.common_good_money = []     # money available for the common good project

        self.income_percentage = []
        self.demurrage_percentage = []
        self.common_good_percentage = []
        self.new_money_percentage = []


    def initialize(self):
        self.population.clear()
        self.income.clear()
        self.money_mass.clear()
        self.demurrage.clear()
        self.dem_tiers.clear()
        self.new_money.clear()
        self.common_good_budget.clear()
        self.common_good_money.clear()

        self.income_percentage.clear()
        self.demurrage_percentage.clear()
        self.common_good_percentage.clear()
        self.new_money_percentage.clear()

        self.population.append(self.initial_population)
        self.income.append(self.initial_income)
        self.money_mass.append(self.initial_money_mass)
        self.demurrage.append(0.0)
        self.dem_tiers.append(self.initial_dem_tiers)
        self.new_money.append(self.initial_money_mass)
        self.common_good_budget.append(self.initial_common_good_budget)
        self.common_good_money.append(0.0)

        self.income_percentage.append(0.0)
        self.demurrage_percentage.append(0.0)
        self.common_good_percentage.append(0.0)
        self.new_money_percentage.append(100.0)


    def run_simulation(self, iterations):
        for i in range(iterations):
            if i == 0:
                self.initialize()
            else:
                # apply inflation
                self.income.append(self.income[i - 1] + self.income[i - 1] * self.inflation)
                self.common_good_budget.append(self.common_good_budget[i - 1]
                                               + self.common_good_budget[i - 1] * self.inflation)
                cur_dem_tiers = {}

                for tier in range(self.num_dem_tiers - 1):
                    prev_value = self.dem_tiers[i - 1][tier]
                    cur_dem_tiers[tier] =  prev_value + prev_value * self.inflation

                self.dem_tiers.append(cur_dem_tiers)

                # calculate demurrage and apply
                individual_money = self.money_mass[i - 1] / self.population[i - 1]
                individual_demurrage = self.calculate_demurrage(i, individual_money)
                total_demurrage = individual_demurrage * self.population[i - 1]
                self.demurrage.append(total_demurrage)
                self.money_mass.append(self.money_mass[i - 1] - total_demurrage)
                self.common_good_money.append(total_demurrage)

                # grow population
                self.population.append(self.population[i - 1] + self.population[i - 1] * self.population_growth)

                # distribute income
                self.new_money.append(self.income[i] * self.population[i])
                self.money_mass[i] += self.new_money[i]

                # top up common good project or destroy surplus
                common_good_expense = 0

                if self.common_good_spending == FIXED_SPENDING:
                    common_good_expense = self.common_good_budget[i]
                elif self.common_good_spending == PER_CAPITA:
                    common_good_expense = self.population[i] * self.common_good_budget[i]

                if self.common_good_money[i] > common_good_expense:
                    self.new_money[i] -= self.common_good_money[i] - common_good_expense
                else:
                    self.new_money[i] += common_good_expense - self.common_good_money[i]

                self.common_good_money[i] = common_good_expense

                # spend common good money into society
                self.money_mass[i] += self.common_good_money[i]

                # calculate percentages
                self.income_percentage.append(self.income[i] * 100 / self.money_mass[i])
                self.demurrage_percentage.append(self.demurrage[i] * 100 / self.money_mass[i])
                self.common_good_percentage.append(self.common_good_money[i] * 100 / self.money_mass[i])
                self.new_money_percentage.append(self.new_money[i] * 100 / self.money_mass[i])


    def calculate_demurrage(self, cycle, amount):
        demurrage = 0

        for tier in range(self.num_dem_tiers - 1):
            calculate_on = amount - self.dem_tiers[cycle][tier]

            if calculate_on > 0:
                if tier < MAX_DEM_TIERS - 1 and calculate_on > self.dem_tiers[cycle][tier + 1]:
                    calculate_on = self.dem_tiers[tier + 1] = self.dem_tiers[cycle][tier]
            else:
                 calculate_on = 0

            demurrage += calculate_on * self.dem_rates[tier]

        return demurrage
