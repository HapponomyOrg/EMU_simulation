from flask import Blueprint, render_template, request
from emusim.cockpit.abm.forms.abm_forms_d import ParameterForm
from emusim.cockpit.abm.mesa.MoneyModel import *
import pygal
import numpy as np


abm_in_flask = Blueprint('abm_in_flask', __name__,
                         template_folder='../templates',
                         static_folder='../static')

graph_data = []

def model_run(model_params):
    graph_data.clear()
    parameter_form = ParameterForm(request.form)
    parameter_form.initial_wealth.data = model_params.initial_wealth
    parameter_form.wealth_transfer.data = model_params.wealth_transfer
    parameter_form.num_agents.data = model_params.agents_count
    parameter_form.iterations.data = model_params.iterations_count
    gridsize = int(round(parameter_form.num_agents.data / 5))
    model = MoneyModel(parameter_form.num_agents.data, gridsize, gridsize, parameter_form.initial_wealth.data,
                       parameter_form.wealth_transfer.data)
    for i in range(parameter_form.iterations.data):
        model.step()
    gini = model.datacollector.get_model_vars_dataframe()
    arr = np.transpose(gini.values)[0]

    # create gini chart
    gini_charts = []
    chart_gini = pygal.Line(show_dots=True, show_legend=False,
                            range=(0, 1), show_x_labels=True)
    chart_gini.title = 'Gini coefficient'
    chart_gini.add('Gini', arr)
    chart_gini.render()
    gini_charts.append(chart_gini.render_data_uri())
    graph_data.append(gini_charts)
    render_graphs = True
    return render_template('abm_simulation_d.html',
                       parameter_form=parameter_form,
                       graph_data=graph_data,
                       render_graphs=render_graphs)


def moneymodel_model(model, parameter_form):
    render_graphs = True
    graph_data = moneymodel_run(model.num_agents, model.initial_wealth, model.wealth_transfer,
                                model.iterations)
    return render_template('abm_simulation_d.html',
                            parameter_form=parameter_form,
                            graph_data=graph_data,
                            render_graphs=render_graphs)


def moneymodel_run(num_agents, initial_wealth, wealth_transfer, iterations):
    # run model
    graph_data.clear()
    gridsize = int(round(num_agents / 5))
    model = MoneyModel(num_agents, gridsize, gridsize, initial_wealth,
                       wealth_transfer)
    for i in range(iterations):
        model.step()
    gini = model.datacollector.get_model_vars_dataframe()
    arr = np.transpose(gini.values)[0]

    # create gini chart
    gini_charts = []
    chart_gini = pygal.Line(show_dots=True, show_legend=False,
                            range=(0, 1), show_x_labels=True)
    chart_gini.title = 'Gini coefficient'
    chart_gini.add('Gini', arr)
    chart_gini.render()
    gini_charts.append(chart_gini.render_data_uri())
    graph_data.append(gini_charts)
    return graph_data


@abm_in_flask.route('/moneymodel', methods=['GET', 'POST'])
def moneymodel(parameter_form=None):
    if (not parameter_form):
        parameter_form = ParameterForm(request.form)
    render_graphs = False
    graph_data = None

    if parameter_form.validate():
        graph_data = moneymodel_run(parameter_form.num_agents.data, parameter_form.initial_wealth.data,
                                    parameter_form.wealth_transfer.data, parameter_form.iterations.data)
        render_graphs = True

    return render_template('abm_simulation_d.html',
                           parameter_form=parameter_form,
                           graph_data=graph_data,
                           render_graphs=render_graphs)


