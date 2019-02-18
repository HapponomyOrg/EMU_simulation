from flask import Flask, render_template, request, flash, redirect
from cockpit.euro.money_supply.forms import LoginForm, ParameterForm, DataSelectionForm
from flask_wtf.csrf import CsrfProtect

import pygal

# from flask_pymongo import PyMongo

from cockpit.euro.money_supply import Config
from cockpit.euro.money_supply import MS_Simulation

app = Flask(__name__)
app.config.from_object(Config)
CsrfProtect(app)
# mongo = PyMongo(app)
# client = mongo.cx


@app.route('/')
def home():
    return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/ms_simulation')

    return render_template('login.html', title='Sign In', form=form)


@app.route('/ms_simulation', methods=['GET', 'POST'])
def ms_simulation():
    parameter_form = ParameterForm(request.form)
    data_selection_form = DataSelectionForm(request.form)
    render_graphs = False
    graph_data = []

    if parameter_form.validate_on_submit():
        simulation = MS_Simulation()
        simulation.growth_rate = parameter_form.growth_rate.data / 100
        simulation.inflation_rate = parameter_form.inflation_rate.data / 100
        simulation.initial_fixed_spending = parameter_form.fixed_spending.data
        simulation.pp = parameter_form.profit_spending.data / 100
        simulation.cp = parameter_form.capital_spending.data / 100
        simulation.mr = parameter_form.minimum_reserve.data / 100
        simulation.pbdr = parameter_form.bank_payback_rate.data / 100
        simulation.nbdr = parameter_form.private_payback_rate.data / 100
        simulation.ecbi = parameter_form.ecb_interest.data / 100
        simulation.pbi = parameter_form.bank_interest.data / 100
        simulation.savei = parameter_form.savings_interest.data / 100
        simulation.saving_rate = parameter_form.savings_rate.data / 100
        simulation.nmr = parameter_form.min_new_money.data / 100
        simulation.min_bank_reserve = parameter_form.min_desired_reserve.data / 100
        simulation.no_loss = parameter_form.no_loss.data
        simulation.min_profit = parameter_form.min_profit.data / 100
        simulation.qe_spending = parameter_form.qe_mode.data
        simulation.qe_trickle_rate = parameter_form.qe_trickle_rate.data / 100
        simulation.qe_fixed_initial = parameter_form.qe_fixed.data
        simulation.qe_relative = parameter_form.qe_relative.data / 100
        simulation.initial_im2 = parameter_form.initial_im2.data

        iterations = parameter_form.num_iterations.data

        simulation.run_simulation(iterations)
        graph_data.clear()

        if data_selection_form.om.data:
            om_charts = []
            chart_om = create_chart("OM")
            chart_om_growth = create_chart('OM growth')
            deflate = data_selection_form.om_deflate.data

            chart_om.add('OM 1', simulation.get_data(simulation.om1, deflate))
            chart_om.add('OM 2', simulation.get_data(simulation.om2, deflate))
            chart_om_growth.add('OM 1', simulation.get_om1_growth(deflate))
            chart_om_growth.add('OM 2', simulation.get_om2_growth(deflate))
            chart_om_growth.add('OM total', simulation.get_om_growth(deflate))

            om_charts.append(chart_om.render_data_uri())
            om_charts.append(chart_om_growth.render_data_uri())
            graph_data.append(om_charts)

        if data_selection_form.im.data:
            im_charts = []
            chart_im = create_chart("IM")
            chart_im_growth = create_chart("IM growth")
            deflate = data_selection_form.im_deflate.data

            chart_im.add('IM 1', simulation.get_data(simulation.im1, deflate))
            chart_im.add('IM 2', simulation.get_data(simulation.im2, deflate))
            chart_im_growth.add('IM 1', simulation.get_im1_growth(deflate))
            chart_im_growth.add('IM 2', simulation.get_im2_growth(deflate))
            chart_im_growth.add('IM total', simulation.get_im_growth(deflate))

            im_charts.append(chart_im.render_data_uri())
            im_charts.append(chart_im_growth.render_data_uri())
            graph_data.append(im_charts)

        if data_selection_form.bank.data:
            bank_charts = []
            chart_profit = create_chart("Bank profit")
            chart_debt = create_chart("Bank debt to ECB")
            chart_spending = create_chart("Benk spending")
            deflate = data_selection_form.bank_deflate.data

            chart_profit.add("Profit", simulation.get_data(simulation.bank_profit, deflate))
            chart_profit.add("Created IM", simulation.get_data(simulation.new_im, deflate))
            chart_debt.add("Debt", simulation.get_data(simulation.bank_debt, deflate))
            chart_debt.add("Payoff", simulation.get_data(simulation.bank_payoff, deflate))
            chart_debt.add("Interest", simulation.get_data(simulation.bank_interest, deflate))
            chart_spending.add("Bank spending", simulation.get_data(simulation.bank_spending, deflate))

            bank_charts.append(chart_profit.render_data_uri())
            bank_charts.append(chart_debt.render_data_uri())
            bank_charts.append(chart_spending.render_data_uri())
            graph_data.append(bank_charts)

        if data_selection_form.private.data:
            private_charts = []
            chart_debt = create_chart('Debt')
            chart_lending = create_chart('Lending')
            chart_interest = create_chart('Earned interest')
            deflate = data_selection_form.private_deflate

            chart_debt.add('Debt', simulation.get_data(simulation.debt, deflate))
            chart_debt.add('Payoff', simulation.get_data(simulation.payoff, deflate))
            chart_debt.add('Interest', simulation.get_data(simulation.interest, deflate))
            chart_lending.add('Lending', simulation.get_data(simulation.lending, deflate))
            chart_interest.add('Earned interest', simulation.get_data(simulation.savings_interest, deflate))

            private_charts.append(chart_debt.render_data_uri())
            private_charts.append(chart_lending.render_data_uri())
            private_charts.append(chart_interest.render_data_uri())
            graph_data.append(private_charts)

        if data_selection_form.qe.data:
            qe_charts = []
            chart_qe = create_chart('QE')
            deflate = data_selection_form.qe_deflate.data

            chart_qe.add('QE', simulation.get_data(simulation.qe, deflate))
            chart_qe.add('QE trickle', simulation.get_data(simulation.qe_trickle, deflate))

            qe_charts.append(chart_qe.render_data_uri())
            graph_data.append(qe_charts)

        if data_selection_form.im_distribution.data:
            im_charts = []
            chart_im1_im2 = create_chart('IM distribution (% of IM total)')
            chart_im1_im2.add('IM 1', simulation.get_data(simulation.im1_percentage_im_total, False))
            chart_im1_im2.add('IM 2', simulation.get_data(simulation.im2_percentage_im_total, False))

            im_charts.append(chart_im1_im2.render_data_uri())
            graph_data.append(im_charts)

        if data_selection_form.debt_percentage.data:
            debt_charts = []
            chart_debt = create_chart('Debt (% of IM)')
            chart_debt.add('% of IM 2', simulation.get_data(simulation.debt_percentage_im2, False))
            chart_debt.add('% of IM total', simulation.get_data(simulation.debt_percentage_im_total, False))

            debt_charts.append(chart_debt.render_data_uri())
            graph_data.append(debt_charts)

        if data_selection_form.lending_percentage.data:
            lending_charts = []
            chart_lending = create_chart('Lending % of IM')
            chart_lending.add('% of IM2', simulation.get_data(simulation.lending_percentage_im2, False))
            chart_lending.add('% of IM total', simulation.get_data(simulation.lending_percentage_im_total, False))

            lending_charts.append(chart_lending.render_data_uri())
            graph_data.append(lending_charts)

        if data_selection_form.created_percentage.data:
            created_charts = []
            chart_created = create_chart('Created IM')
            chart_created.add('% of IM 2', simulation.get_data(simulation.created_percentage_im2, False))
            chart_created.add('% of IM total', simulation.get_data(simulation.created_percentage_im_total, False))

            created_charts.append(chart_created.render_data_uri())
            graph_data.append(created_charts)

        render_graphs = True
    else:
        flash('Error')

    return render_template('ms_simulation.html',
                           parameter_form=parameter_form,
                           data_selection_form=data_selection_form,
                           render_graphs=render_graphs,
                           graph_data=graph_data)

def create_chart(title):
    chart = pygal.Line()
    chart.title = title
    return chart


if __name__ == '__main__':
    app.run(debug=False)
