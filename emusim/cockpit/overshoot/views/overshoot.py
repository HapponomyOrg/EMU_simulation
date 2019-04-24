from flask import Blueprint, render_template, request
from emusim.cockpit.overshoot.forms.overshoot_forms import DateForm

from emusim.cockpit.utilities import create_chart
from emusim.cockpit.overshoot.earth_overshoot import Earth_Overshoot

overshoot = Blueprint('overshoot', __name__,
                         template_folder='../templates',
                         static_folder='../static')

simulation = Earth_Overshoot()


@overshoot.route('/overshoot_simulation', methods=['GET', 'POST'])
def overshoot_simulation():
    date_form = DateForm(request.form)
    depletion_date = None
    overshoot_date = None
    show_dates = False

    target_date = date_form.target_date.data
    depletion_date = simulation.calculate_past_date(target_date)
    overshoot_date = simulation.calculate_future_date(target_date)

    overshoot_data = simulation.overshoot_data
    overshoot_days = []
    cumulative_overshoot_days = []
    weights = []

    for year in sorted(overshoot_data.keys()):
        data = overshoot_data[year]
        overshoot_days.append(data.get_overshoot_days())
        cumulative_overshoot_days.append(data.get_cumulative_overshoot_days())
        weights.append(round(data.weight, 2))

    graph_data = []

    overshoot_per_year_chart = create_chart('Earth overshoot days per year')
    overshoot_per_year_chart.add('Overshoot days', overshoot_days)
    overshoot_per_year_chart.x_labels = map(str, range(Earth_Overshoot.FIRST_YEAR, Earth_Overshoot.LAST_YEAR))
    graph_data.append(overshoot_per_year_chart.render_data_uri())

    cumulative_overshoot_chart = create_chart('Cumulative overshoot days')
    cumulative_overshoot_chart.add('Overshoot days', cumulative_overshoot_days)
    cumulative_overshoot_chart.x_labels = map(str, range(Earth_Overshoot.FIRST_YEAR, Earth_Overshoot.LAST_YEAR))
    graph_data.append(cumulative_overshoot_chart.render_data_uri())

    weight_chart = create_chart('Day weight per year')
    weight_chart.add('Weight', weights)
    weight_chart.x_labels = map(str, range(Earth_Overshoot.FIRST_YEAR, Earth_Overshoot.LAST_YEAR))
    graph_data.append(weight_chart.render_data_uri())

    return render_template('overshoot_simulation.html',
                           date_form=date_form,
                           graph_data=graph_data,
                           depletion_date=depletion_date,
                           overshoot_date=overshoot_date)
