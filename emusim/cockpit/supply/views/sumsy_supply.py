from flask import Blueprint, render_template, request
from cockpit.supply.forms.sumsy_forms import ParameterForm, DataSelectionForm

from cockpit.supply.constants import *
from cockpit.utilities import create_chart
from cockpit.supply.sumsy_simulation import SumSy_MS_Simulation

sumsy_supply = Blueprint('sumsy_supply', __name__,
                         template_folder='../templates',
                         static_folder='../static')


@sumsy_supply.route('/sumsy_supply_simulation', methods=['GET', 'POST'])
def sumsy_supply_simulation():
    parameter_form = ParameterForm(request.form)
    data_selection_form = DataSelectionForm(request.form)
    render_graphs = False
    graph_data = []

    if parameter_form.validate_on_submit():
        simulation = SumSy_MS_Simulation()
        simulation.initial_population = parameter_form.population.data
        simulation.population_growth = parameter_form.population_growth.data / 100
        simulation.initial_money_mass = parameter_form.money_mass.data
        simulation.inflation_rate = parameter_form.inflation.data / 100
        simulation.initial_income = parameter_form.income.data
        simulation.num_dem_tiers = parameter_form.num_dem_tiers.data

        simulation.initial_dem_tiers[0] = parameter_form.dem_tier_1.data
        simulation.dem_rates[0] = parameter_form.dem_rate_1.data
        simulation.initial_dem_tiers[1] = parameter_form.dem_tier_2.data
        simulation.dem_rates[1] = parameter_form.dem_rate_2.data
        simulation.initial_dem_tiers[2] = parameter_form.dem_tier_3.data
        simulation.dem_rates[2] = parameter_form.dem_rate_3.data
        simulation.initial_dem_tiers[3] = parameter_form.dem_tier_4.data
        simulation.dem_rates[3] = parameter_form.dem_rate_4.data
        simulation.initial_dem_tiers[4] = parameter_form.dem_tier_5.data
        simulation.dem_rates[4] = parameter_form.dem_rate_5.data

        simulation.common_good_spending = parameter_form.common_good_spending.data
        simulation.initial_common_good_budget = parameter_form.common_good_budget.data

        iterations = parameter_form.num_iterations.data

        simulation.run_simulation(iterations)
        graph_data.clear()

        if data_selection_form.population.data:
            population_charts = []
            population_chart = create_chart('Population')
            population_chart.add('Population', simulation.population)

            population_charts.append(population_chart.render_data_uri())
            graph_data.append(population_charts)

        if data_selection_form.money_mass.data:
            money_charts = []
            money_chart = create_chart('Money mass')
            money_chart.add('Money mass',
                            simulation.get_data(simulation.money_mass, data_selection_form.money_mass_deflate.data))

            money_charts.append(money_chart.render_data_uri())
            graph_data.append(money_charts)

        if data_selection_form.per_capita_money_mass.data:
            per_capita_money_charts = []
            per_capita_money_chart = create_chart('Money mass per capita')
            per_capita_money_chart.add('Money mass per capita',
                                       simulation.get_data(simulation.per_capita_money_mass,
                                                           data_selection_form.per_capita_money_mass_deflate.data))

            per_capita_money_charts.append(per_capita_money_chart.render_data_uri())
            graph_data.append(per_capita_money_charts)

        if data_selection_form.demurrage.data:
            demurrage_charts = []
            demurrage_chart = create_chart('Demurrage')
            demurrage_chart.add('Demurrage',
                                simulation.get_data(simulation.demurrage, data_selection_form.demurrage_deflate.data))

            demurrage_charts.append(demurrage_chart.render_data_uri())
            graph_data.append(demurrage_charts)

        if data_selection_form.per_capita_demurrage.data:
            per_capita_demurrage_charts = []
            per_capita_demurrage_chart = create_chart('Demurrage per capita')
            per_capita_demurrage_chart.add('Demurrage per capita',
                                           simulation.get_data(simulation.per_capita_demurrage,
                                                               data_selection_form.per_capita_demurrage_deflate.data, ))

            per_capita_demurrage_charts.append(per_capita_demurrage_chart.render_data_uri())
            graph_data.append(per_capita_demurrage_charts)

        if data_selection_form.new_money.data:
            new_money_charts = []
            new_money_chart = create_chart('New money')
            new_money_chart.add('New money',
                                simulation.get_data(simulation.new_money, data_selection_form.new_money_deflate.data))

            new_money_charts.append(new_money_chart.render_data_uri())
            graph_data.append(new_money_charts)

        if data_selection_form.per_capita_new_money.data:
            per_capita_new_money_charts = []
            per_capita_new_money_chart = create_chart('New money per capita')
            per_capita_new_money_chart.add('New money per capita',
                                           simulation.get_data(simulation.per_capita_new_money,
                                                               data_selection_form.per_capita_new_money_deflate.data))

            per_capita_new_money_charts.append(per_capita_new_money_chart.render_data_uri())
            graph_data.append(per_capita_new_money_charts)

        if data_selection_form.common_good.data:
            common_good_charts = []
            common_good_chart = create_chart('Common good spending')
            common_good_chart.add('Spending', simulation.get_data(simulation.common_good_money,
                                                                  data_selection_form.common_good_deflate.data))
            common_good_charts.append(common_good_chart.render_data_uri())
            graph_data.append(common_good_charts)

        if data_selection_form.percentages.data:
            percentage_charts = []
            percentage_chart = create_chart('Percentages of money mass')
            percentage_chart.add('Income', simulation.get_data(simulation.income_percentage))
            percentage_chart.add('Demurrage', simulation.get_data(simulation.demurrage_percentage))

            if parameter_form.common_good_spending.data != NONE:
                percentage_chart.add('Common good spending', simulation.get_data(simulation.common_good_percentage))

            percentage_chart.add('New money', simulation.get_data(simulation.new_money_percentage))

            percentage_charts.append(percentage_chart.render_data_uri())
            graph_data.append(percentage_charts)

        render_graphs = True

    return render_template('sumsy_simulation.html',
                           parameter_form=parameter_form,
                           data_selection_form=data_selection_form,
                           render_graphs=render_graphs,
                           graph_data=graph_data)
