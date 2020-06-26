
from flask import Blueprint, render_template, request
from emusim.cockpit.abm.forms.abm_forms_d import ParameterForm

from emusim.cockpit.abm.mesa.MoneyModel import *
import pygal
import numpy as np

abm_in_flask = Blueprint('abm_in_flask', __name__,
                        template_folder='../templates',
                        static_folder='../static')

@abm_in_flask.route('/moneymodel', methods=['GET', 'POST'])
def moneymodel():
    parameter_form = ParameterForm(request.form)
    render_graphs = False
    graph_data = []

    if parameter_form.validate_on_submit():
        model = MoneyModel(parameter_form.num_agents.data, 10, 10)
        for i in range(parameter_form.iterations.data):
            model.step()
        gini = model.datacollector.get_model_vars_dataframe()
        #print(gini)
        #gini.plot() #plot to show in sciview
        #plt.show() #plot to show in sciview
        arr = np.transpose(gini.values)[0]

        gini_charts = []

        #create gini chart
        chart_gini = pygal.Line(show_dots=True,  show_legend=False,
                                range=(0,1), show_x_labels=True)

        chart_gini.title = 'Gini coefficient'

        chart_gini.add('Gini', arr)
        chart_gini.render()


        gini_charts.append(chart_gini.render_data_uri())
        graph_data.append(gini_charts)
        render_graphs = True
        #print(graph_data)

    return render_template('abm_simulation_d.html',
                           parameter_form=parameter_form,
                               graph_data=graph_data,
                           render_graphs=render_graphs)

def create_chart(title):
    chart = pygal.Line(include_x_axis=True, show_y_labels=True)
    chart.y_labels = .0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1
    chart.title = title
    return chart