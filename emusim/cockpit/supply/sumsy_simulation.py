# module sumsy_simulation

from emusim.cockpit.supply.constants import *
from emusim.cockpit.supply.simulation import Simulation


class SumSy_MS_Simulation(Simulation):

    def __init__(self):
        super().__init__()
        self.initial_population = 5000
        self.population_growth = 0.0
        self.start_at_saturation = True
        self.initial_money_mass = 100000.0
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

        self.population = []  # total population
        self.income = []  # income adjusted for inflation rate
        self.money_mass = []  # total monetary mass
        self.per_capita_money_mass = []  # monetary mass per capita
        self.demurrage = []  # amount of demurrage paid
        self.per_capita_demurrage = []  # amount of demurrage paid per capita
        self.money_cycling = []  # money added to or removed from the total monetary mass
        self.per_capita_money_cycling = []  # money added to the total monetary mass per capita
        self.dem_tiers = []  # demurrage tiers
        self.common_good_budget = []  # money needed for the common good project
        self.common_good_money = []  # money available for the common good project

        self.income_percentage = []
        self.demurrage_percentage = []
        self.common_good_percentage = []
        self.money_cycle_percentage = []

        self.equilibrium_balance = 0.0

    def initialize(self):
        super(SumSy_MS_Simulation, self).initialize()

        self.population.clear()
        self.income.clear()
        self.money_mass.clear()
        self.per_capita_money_mass.clear()
        self.demurrage.clear()
        self.per_capita_demurrage.clear()
        self.money_cycling.clear()
        self.per_capita_money_cycling.clear()
        self.dem_tiers.clear()
        self.common_good_budget.clear()
        self.common_good_money.clear()

        self.income_percentage.clear()
        self.demurrage_percentage.clear()
        self.common_good_percentage.clear()
        self.money_cycle_percentage.clear()

        self.population.append(self.initial_population)
        self.income.append(self.initial_income)

        self.money_cycling.append(self.initial_money_mass)
        self.per_capita_money_cycling.append(self.initial_money_mass / self.initial_population)
        self.dem_tiers.append(self.initial_dem_tiers)
        self.common_good_budget.append(self.initial_common_good_budget)
        self.common_good_money.append(0.0)

        if self.start_at_saturation:
            self.money_mass.append(self.calculate_equilibrium_balance() * self.initial_population)
        else:
            self.money_mass.append(self.initial_money_mass)

        self.per_capita_money_mass.append(self.money_mass[0] / self.initial_population)

        self.per_capita_demurrage.append(0.0)
        self.demurrage.append(0.0)

        self.income_percentage.append(self.initial_income * self.initial_population / self.money_mass[0])
        self.demurrage_percentage.append(0.0)

        if self.common_good_spending == FIXED_SPENDING:
            self.common_good_percentage.append(self.initial_common_good_budget / self.money_mass[0])
        else:
            self.common_good_percentage.append(
                self.initial_common_good_budget * self.initial_population / self.money_mass[0])

        self.money_cycle_percentage.append(100.0)

        self.equilibrium_balance = self.calculate_equilibrium_balance()

    def run_simulation(self, iterations):
        for i in range(iterations):
            if i == 0:
                self.initialize()
            else:
                # copy previous money mass
                self.money_mass.append(self.money_mass[i - 1])

                # copy inflation rate
                self.inflation_rate.append(self.inflation_rate[i - 1])

                # calculate demurrage on money mass of previous cycle and apply
                individual_money = self.money_mass[i] / self.population[i - 1]
                individual_demurrage = self.calculate_demurrage(i - 1, individual_money, self.num_dem_tiers)
                total_demurrage = individual_demurrage * self.population[i - 1]
                self.demurrage.append(total_demurrage)
                self.per_capita_demurrage.append(individual_demurrage)
                self.money_mass[i] -= total_demurrage

                # available money for common good services = demurrage from previous cycle
                self.common_good_money.append(self.demurrage[i])

                # grow population
                self.population.append(
                    max(0.0, self.population[i - 1] + round(self.population[i - 1] * self.population_growth)))

                # apply inflation rate
                self.income.append(max(0.0, self.income[i - 1] + self.income[i - 1] * self.inflation_rate[i - 1]))
                self.common_good_budget.append(max(0.0, self.common_good_budget[i - 1]
                                                   + self.common_good_budget[i - 1] * self.inflation_rate[i - 1]))
                cur_dem_tiers = {}

                for tier in range(self.num_dem_tiers):
                    prev_value = self.dem_tiers[i - 1][tier]
                    cur_dem_tiers[tier] = max(0.0, prev_value + prev_value * self.inflation_rate[i - 1])

                self.dem_tiers.append(cur_dem_tiers)

                # distribute income
                self.money_cycling.append(self.income[i] * self.population[i])
                self.money_mass[i] += self.money_cycling[i]

                # top up common good project or destroy surplus
                common_good_expense = 0

                if self.common_good_spending == FIXED_SPENDING:
                    common_good_expense = self.common_good_budget[i]
                elif self.common_good_spending == PER_CAPITA:
                    common_good_expense = self.population[i] * self.common_good_budget[i]

                # determine how much money needs to be created to fund common good services
                self.money_cycling[i] += common_good_expense - self.common_good_money[i]

                # common good expenses for this cycle
                self.common_good_money[i] = common_good_expense

                # spend common good money into society
                self.money_mass[i] += self.common_good_money[i]

                self.per_capita_money_mass.append(self.money_mass[i] / self.population[i])
                self.per_capita_money_cycling.append((self.money_cycling[i] / self.population[i]))

                # calculate percentages
                self.income_percentage.append(self.income[i] * self.population[i] / self.money_mass[i])
                self.common_good_percentage.append(self.common_good_money[i] / self.money_mass[i])
                self.money_cycle_percentage.append(self.money_cycling[i] / self.money_mass[i])
                self.demurrage_percentage.append(self.demurrage[i] / self.money_mass[i])

                # break if any value reaches infinity or money mass per capita reaches 0
                if self.money_mass[i] == INFINITY or self.inflation_rate[i] == INFINITY or self.dem_tiers[i][
                    self.num_dem_tiers - 1] == INFINITY or round(
                    self.per_capita_money_mass[i], 2) == 0:
                    self.crash = True
                    self.cycles_executed -= 1
                    break
                else:
                    self.cycles_executed += 1

    def calculate_per_capita_demurrage(self, cycle):
        individual_money = self.money_mass[cycle] / self.population[cycle]
        individual_demurrage = self.calculate_demurrage(cycle, individual_money, self.num_dem_tiers)

        return individual_demurrage

    def calculate_equilibrium_balance(self):
        tier = 0

        if self.common_good_spending == FIXED_SPENDING:
            total_income = self.initial_income + self.initial_common_good_budget / self.initial_population
        else:
            total_income = self.initial_income + self.initial_common_good_budget

        balance = self.initial_dem_tiers[0]

        while tier < MAX_DEM_TIERS - 1 and self.calculate_demurrage(0, balance, tier) < total_income:
            tier += 1
            balance = self.initial_dem_tiers[tier]

        if self.calculate_demurrage(0, balance, tier) > total_income:
            dem_remaining = total_income - self.calculate_demurrage(0, self.initial_dem_tiers[tier - 1], tier - 1)
            balance = self.initial_dem_tiers[tier - 1] + dem_remaining / self.dem_rates[tier - 1]

        return balance

    def calculate_demurrage(self, cycle, amount, num_tiers):
        demurrage = 0
        tiers = self.dem_tiers[cycle]

        for tier in range(num_tiers):
            calculate_on = amount - tiers[tier]

            if calculate_on > 0:
                if tier < MAX_DEM_TIERS - 1 and amount > tiers[tier + 1]:
                    calculate_on = tiers[tier + 1] - tiers[tier]
            else:
                calculate_on = 0

            demurrage += calculate_on * self.dem_rates[tier]

        return demurrage

    def get_tier(self, tier_nr):
        tier = []

        for tiers in self.dem_tiers:
            tier.append(tiers[tier_nr])

        return tier
