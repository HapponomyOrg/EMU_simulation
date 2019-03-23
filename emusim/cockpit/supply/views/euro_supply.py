from flask import Blueprint, render_template, request
from emusim.cockpit.supply.forms.euro_forms import ParameterForm, DataSelectionForm
from emusim.cockpit.supply.constants import *

from emusim.cockpit.utilities import create_chart

from emusim.cockpit.supply.euro_simulation import Euro_MS_Simulation

euro_supply = Blueprint('euro_supply', __name__,
                        template_folder='../templates',
                        static_folder='../static')


@euro_supply.route('/')
def home():
    return render_template('base.html')


@euro_supply.route('/euro_supply_simulation', methods=['GET', 'POST'])
def euro_supply_simulation():
    parameter_form = ParameterForm(request.form)
    data_selection_form = DataSelectionForm(request.form)
    render_graphs = False
    graph_data = []

    if parameter_form.validate_on_submit():
        simulation = Euro_MS_Simulation()

        simulation.desired_initial_im = parameter_form.desired_initial_im.data
        simulation.lending_satisfaction_rate = parameter_form.lending_satisfaction_rate.data / 100

        simulation.minimum_reserve = parameter_form.minimum_reserve.data / 100
        simulation.maximum_reserve = parameter_form.maximum_reserve.data / 100

        if parameter_form.auto_calculate.data:
            lending_satisfaction_rate = simulation.lending_satisfaction_rate

            simulation.initial_debt = parameter_form.initial_debt.data * lending_satisfaction_rate
            simulation.initial_created_im = parameter_form.initial_created_im.data * lending_satisfaction_rate
            simulation.initial_bank_reserve = simulation.initial_created_im * simulation.minimum_reserve
            simulation.initial_bank_debt = simulation.initial_bank_reserve
            simulation.initial_created_reserve = simulation.initial_bank_reserve
        else:
            simulation.initial_debt = parameter_form.initial_debt.data
            simulation.initial_created_im = parameter_form.initial_created_im.data
            simulation.initial_bank_reserve = parameter_form.initial_bank_reserve.data
            simulation.initial_bank_debt = parameter_form.initial_bank_debt.data
            simulation.initial_created_reserve = parameter_form.initial_created_reserves.data

        simulation.initial_private_assets = parameter_form.initial_private_assets.data
        simulation.initial_bank_assets = parameter_form.initial_bank_assets.data

        simulation.desired_growth_rate = parameter_form.desired_growth_rate.data / 100
        simulation.growth_target = parameter_form.growth_target.data
        simulation.inflation_rate = parameter_form.inflation_rate.data / 100

        simulation.spending_mode = parameter_form.spending_mode.data

        simulation.initial_fixed_spending = parameter_form.fixed_spending.data
        simulation.profit_spending = parameter_form.profit_spending.data / 100
        simulation.capital_spending = parameter_form.capital_spending.data / 100
        simulation.max_spending = parameter_form.max_spending.data / 100

        simulation.bank_payback_rate = parameter_form.bank_payback_rate.data / 100
        simulation.private_payback_rate = parameter_form.private_payback_rate.data / 100

        simulation.ecb_ir = parameter_form.ecb_interest_rate.data / 100
        simulation.bank_ir = parameter_form.bank_interest_rate.data / 100

        simulation.ecb_savings_ir_mr = parameter_form.ecb_savings_rate_mr.data / 100
        simulation.ecb_savings_ir_reserve = parameter_form.ecb_savings_rate_excess.data / 100

        simulation.savings_ir = parameter_form.savings_interest_rate.data / 100
        simulation.saving_rate = parameter_form.savings_rate.data / 100
        simulation.saving_asset_percentage = parameter_form.saving_asset_percentage.data / 100

        simulation.minimum_new_money = parameter_form.min_new_money.data / 100
        simulation.maximum_new_money = parameter_form.max_new_money.data / 100

        simulation.no_loss = parameter_form.no_loss.data
        simulation.min_profit = parameter_form.min_profit.data / 100

        simulation.asset_trickle_mode = parameter_form.asset_trickle_mode.data
        simulation.asset_trickle_rate = parameter_form.asset_trickle.data / 100

        simulation.qe_spending_mode = parameter_form.qe_mode.data
        simulation.qe_trickle_rate = parameter_form.qe_trickle_rate.data / 100
        simulation.qe_fixed_initial = parameter_form.qe_fixed.data
        simulation.qe_relative = parameter_form.qe_relative.data / 100

        iterations = parameter_form.num_iterations.data

        simulation.run_simulation(iterations)
        graph_data.clear()

        deflate = data_selection_form.deflate.data

        if data_selection_form.om.data:
            bank_reserve_charts = []
            chart_bank_reserve = create_chart('Bank reserve')

            chart_bank_reserve.add('Bank reserve', simulation.get_data(simulation.bank_reserve, deflate))
            chart_bank_reserve.add('Created bank reserve',
                                   simulation.get_data(simulation.created_bank_reserve, deflate))
            chart_bank_reserve.add('Growth', simulation.get_growth(simulation.bank_reserve, deflate))

            bank_reserve_charts.append(chart_bank_reserve.render_data_uri())
            graph_data.append(bank_reserve_charts)

        if data_selection_form.im.data:
            im_charts = []
            chart_im = create_chart('IM')
            chart_im_growth = create_chart('IM growth')

            chart_im.add('Desired IM', simulation.get_data(simulation.desired_im, deflate))
            chart_im.add('IM', simulation.get_data(simulation.im, deflate))
            chart_im.add('Created IM', simulation.get_data(simulation.created_im, deflate))
            chart_im_growth.add('Growth %', simulation.get_data(simulation.growth))

            im_charts.append(chart_im.render_data_uri())
            im_charts.append(chart_im_growth.render_data_uri())
            graph_data.append(im_charts)

        if data_selection_form.bank.data:
            bank_charts = []
            chart_profit_spending = create_chart('Bank profit & spending')
            chart_debt = create_chart('Bank debt to ECB')
            chart_lending = create_chart('Bank lending from ECB')

            chart_profit_spending.add('Bank income', simulation.get_data(simulation.bank_income, deflate))
            chart_profit_spending.add('Bank spending', simulation.get_data(simulation.bank_spending, deflate))
            chart_profit_spending.add('Profit', simulation.get_data(simulation.bank_profit, deflate))
            chart_debt.add('Debt', simulation.get_data(simulation.bank_debt, deflate))
            chart_debt.add('Payoff', simulation.get_data(simulation.bank_payoff, deflate))
            chart_debt.add('Interest', simulation.get_data(simulation.bank_interest, deflate))
            chart_lending.add('Lending', simulation.get_data(simulation.bank_lending, deflate))

            bank_charts.append(chart_profit_spending.render_data_uri())
            bank_charts.append(chart_debt.render_data_uri())
            bank_charts.append(chart_lending.render_data_uri())
            graph_data.append(bank_charts)

        if data_selection_form.private.data:
            private_charts = []
            chart_debt = create_chart('Debt')
            chart_lending = create_chart('Lending')
            chart_inflow = create_chart('Inflow')

            chart_debt.add('Debt', simulation.get_data(simulation.debt, deflate))
            chart_debt.add('Payoff', simulation.get_data(simulation.payoff, deflate))
            chart_debt.add('Interest', simulation.get_data(simulation.interest, deflate))
            chart_lending.add('Required', simulation.get_data(simulation.required_lending, deflate))
            chart_lending.add('Real', simulation.get_data(simulation.lending, deflate))
            chart_inflow.add('Bank spending', simulation.get_data(simulation.bank_spending, deflate))
            chart_inflow.add('Savings interest', simulation.get_data(simulation.savings_interest, deflate))
            chart_inflow.add('ECB interest', simulation.get_data(simulation.bank_interest, deflate))

            if simulation.qe_spending_mode != QE_NONE and simulation.qe_trickle_rate > 0:
                chart_inflow.add('QE trickle', simulation.get_data(simulation.qe_trickle, deflate))

            if simulation.asset_trickle_rate > 0:
                chart_inflow.add('Asset trickle', simulation.get_data(simulation.asset_trickle, deflate))

            chart_inflow.add('Total inflow', simulation.get_data(simulation.get_total_inflow(), deflate))

            private_charts.append(chart_debt.render_data_uri())
            private_charts.append(chart_lending.render_data_uri())
            private_charts.append(chart_inflow.render_data_uri())
            graph_data.append(private_charts)

        if data_selection_form.assets.data:
            asset_charts = []
            chart_assets = create_chart('Assets')
            chart_assets.add('Bank investments', simulation.get_data(simulation.bank_asset_investments, deflate))
            chart_assets.add('Private investments', simulation.get_data(simulation.private_asset_investments, deflate))
            chart_assets.add('Total investments', simulation.get_data(simulation.total_asset_investments, deflate))
            chart_assets.add('Available', simulation.get_data(simulation.financial_assets, deflate))

            asset_charts.append(chart_assets.render_data_uri())
            graph_data.append(asset_charts)

        if data_selection_form.qe.data and simulation.qe_spending_mode != QE_NONE:
            qe_charts = []
            chart_qe = create_chart('QE')

            chart_qe.add('QE', simulation.get_data(simulation.qe, deflate))

            qe_charts.append(chart_qe.render_data_uri())
            graph_data.append(qe_charts)

        if data_selection_form.income_expenses_percentage.data:
            inflow_outflow_charts = []
            chart_inflow_outflow = create_chart('% inflow & outflow in the real economy')
            chart_inflow_outflow.add('Savings interest', simulation.get_data(simulation.savings_interest_percentage_im))
            chart_inflow_outflow.add('ECB interest', simulation.get_data(simulation.ecb_interest_percentage_im))
            chart_inflow_outflow.add('Asset trickle', simulation.get_data(simulation.asset_trickle_percentage_im))
            chart_inflow_outflow.add('QE trickle', simulation.get_data(simulation.qe_trickle_percentage_im))
            chart_inflow_outflow.add('Bank spending', simulation.get_data(simulation.bank_spending_percentage_im))
            chart_inflow_outflow.add('Total inflow', simulation.get_data(simulation.total_inflow_percentage_im))
            chart_inflow_outflow.add('Payoff due', simulation.get_data(simulation.payoff_percentage_im))
            chart_inflow_outflow.add('Interest due', simulation.get_data(simulation.interest_percentage_im))
            chart_inflow_outflow.add('Total outflow', simulation.get_data(simulation.total_outflow_percentage_im))

            inflow_outflow_charts.append(chart_inflow_outflow.render_data_uri())
            graph_data.append(inflow_outflow_charts)

        if data_selection_form.im_distribution.data:
            im_charts = []
            chart_distribution = create_chart('Money distribution (% of total money)')
            chart_distribution.add('Real economy', simulation.get_data(simulation.im_percentage_total_money))
            chart_distribution.add('Bank reserve', simulation.get_data(simulation.bank_reserve_percentage_total_money))
            chart_distribution.add('Total financial assets', simulation.get_data(simulation.asset_percentage_total_money))

            im_charts.append(chart_distribution.render_data_uri())
            graph_data.append(im_charts)

        if data_selection_form.debt_percentage.data:
            debt_charts = []
            chart_debt = create_chart('Debt')
            chart_debt.add('% of real economy', simulation.get_data(simulation.debt_percentage_im))
            chart_debt.add('% of total money', simulation.get_data(simulation.debt_percentage_total_money))
            chart_debt.add('Bank reserve % of debt', simulation.get_data(simulation.bank_reserve_percentage_debt))

            chart_bank_debt = create_chart('Bank debt')
            chart_bank_debt.add('% of bank reserve', simulation.get_data(simulation.bank_debt_percentage_bank_reserve))
            chart_bank_debt.add('% of total money', simulation.get_data(simulation.bank_debt_percentage_total_money))

            debt_charts.append(chart_debt.render_data_uri())
            debt_charts.append(chart_bank_debt.render_data_uri())
            graph_data.append(debt_charts)

        if data_selection_form.lending_percentage.data:
            lending_charts = []
            chart_lending = create_chart('Required & real lending')
            chart_lending.add('Required % of real economy', simulation.get_data(simulation.required_lending_percentage_im))
            chart_lending.add('Required % of total money', simulation.get_data(simulation.required_lending_percentage_total_money))
            chart_lending.add('Real % of real economy', simulation.get_data(simulation.lending_percentage_im))
            chart_lending.add('Real % of total money', simulation.get_data(simulation.lending_percentage_total_money))

            chart_bank_lending = create_chart('Bank lending')
            chart_bank_lending.add('% of bank reserve',
                                   simulation.get_data(simulation.bank_lending_percentage_bank_reserve))
            chart_bank_lending.add('% of total money',
                                   simulation.get_data(simulation.bank_lending_percentage_total_money))

            lending_charts.append(chart_lending.render_data_uri())
            lending_charts.append(chart_bank_lending.render_data_uri())
            graph_data.append(lending_charts)

        if data_selection_form.created_percentage.data:
            created_charts = []
            chart_created = create_chart('Created money')
            chart_created.add('Banks % of real economy', simulation.get_data(simulation.created_im_percentage_im))
            chart_created.add('ECB % of bank reserve',
                              simulation.get_data(simulation.created_bank_reserve_percentage_bank_reserve))
            chart_created.add('Banks % of total money', simulation.get_data(simulation.created_im_percentage_total_money))
            chart_created.add('ECB % of total money',
                              simulation.get_data(simulation.created_bank_reserve_percentage_total_money))
            chart_created.add('Total % of total money',
                              simulation.get_data(simulation.created_money_percentage_total_money))

            created_charts.append(chart_created.render_data_uri())
            graph_data.append(created_charts)

        if data_selection_form.bank_profit_spending_percentage.data:
            profit_spending_charts = []
            chart_bank_profit_spending = create_chart('Bank profit & spending')
            chart_bank_profit_spending.add('Profit % income', simulation.get_data(simulation.bank_profit_percentage_bank_income))
            chart_bank_profit_spending.add('Profit % of IM', simulation.get_data(simulation.bank_profit_percentage_im))
            chart_bank_profit_spending.add('Spending % profit', simulation.get_data(simulation.bank_spending_percentage_profit))
            chart_bank_profit_spending.add('Spending % IM', simulation.get_data(simulation.bank_spending_percentage_im))

            profit_spending_charts.append(chart_bank_profit_spending.render_data_uri())
            graph_data.append(profit_spending_charts)

        render_graphs = True

    return render_template('euro_simulation.html',
                           parameter_form=parameter_form,
                           data_selection_form=data_selection_form,
                           render_graphs=render_graphs,
                           graph_data=graph_data)
