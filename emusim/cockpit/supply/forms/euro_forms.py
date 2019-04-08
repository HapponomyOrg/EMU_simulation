from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField

from emusim.cockpit.supply.constants import *


class ParameterForm(FlaskForm):
    num_iterations = IntegerField('Iterations', default=500)
    desired_initial_im = FloatField('Desired initial RIM', default=100000)
    lending_satisfaction_rate = FloatField('Lending satisfaction rate', default=100)
    growth_target = SelectField('Growth target',
                                choices=[(GROW_CURRENT, 'Based on current RIM'),
                                         (GROW_INITIAL, 'Based on initial RIM')])
    auto_calculate = BooleanField('Auto calculate from RIM and lending rate')
    initial_debt = FloatField('Initial debt', default=100000)
    initial_created_im = FloatField('Initial created RIM', default=100000)

    initial_bank_reserve = FloatField('Initial bank reserve', default=4000)
    initial_bank_debt = FloatField('Initial bank debt', default=4000)
    initial_created_reserves = FloatField('Initial created reserves', default=4000)

    initial_private_assets = FloatField('Initial private assets', default=0)
    initial_bank_assets = FloatField('Initial bank assets', default=0)

    desired_growth_rate = FloatField('Desired growth rate', default=1.5)
    inflation_rate = FloatField('Desired inflation rate', default=1.5)

    link_growth_inflation = BooleanField('Link inflation to growth')
    growth_inflation_influence = FloatField('Influence of growth on inflation', default=100)

    ecb_interest_rate = FloatField('ECB interest', default=1.0)
    ecb_savings_rate_mr = FloatField('ECB interest rate on minimal reserve', default=0.0)
    ecb_savings_rate_excess = FloatField('ECB interest rate on excess reserve', default=-0.15)

    minimum_reserve = FloatField('Minimum reserve', default=4.0)
    maximum_reserve = FloatField('Maximum bank reserve', default=5.0)
    min_new_money = FloatField('Minimum new money', default=80.0)
    max_new_money = FloatField('Maximum new money', default=100.0)
    bank_interest_rate = FloatField('Commercial bank interest', default=2.5)
    interest_percentage_bank_income = FloatField('Interest % of bank income', default=100)
    bank_payback_cycles = IntegerField('Bank payback cycles', default=1)
    no_loss = BooleanField('No loss')
    min_profit = FloatField('Minimum profit', default=20.0)
    spending_mode = SelectField('Bank spending mode',
                                choices=[(PROFIT_PERCENTAGE, '% of profit'),
                                         (CAPITAL_PERCENTAGE, '% of capital'),
                                         (FIXED, 'Fixed')])
    max_spending = FloatField('Spending max % of RIM', default=5.0)
    fixed_spending = FloatField('Fixed spending', default=1000.0)
    profit_spending = FloatField('Profit spending', default=80.0)
    capital_spending = FloatField('Capital spending', default=2.0)

    asset_trickle_mode = SelectField('Asset trickle mode',
                          choices=[(ASSET_GROWTH, '% of asset growth'),
                                   (ASSET_CAPITAL, '% of asset capital')])
    asset_trickle = FloatField('Asset trickle', default=5.0)

    qe_mode = SelectField('QE mode',
                          choices=[(QE_NONE, 'No QE'),
                                   (QE_FIXED, 'Fixed QE'),
                                   (QE_RELATIVE, '% of private debt')])
    qe_trickle_rate = FloatField('QE trickle', default=0.0)
    qe_fixed = FloatField('Fixed QE', default=1000.0)
    qe_relative = FloatField('Relative QE', default=2.0)
    qe_profit = BooleanField('QE is bank profit')

    savings_rate = FloatField('Savings rate', default=20.0)
    savings_interest_rate = FloatField('Savings interest', default=0.5)
    saving_asset_percentage = FloatField('% of savings invested in assets', default=5)
    private_payback_cycles = IntegerField('Private payback cycles', default=20)


class DataSelectionForm(FlaskForm):
    deflate = BooleanField('Deflate')

    om = BooleanField('Bank reserve data')
    im = BooleanField('RIM data')
    bank = BooleanField('Bank data')
    private = BooleanField('Private sector data')
    assets = BooleanField('Financial assets data')
    qe = BooleanField('QE data')

    income_expenses_percentage = BooleanField('Inflow & outflow')
    im_distribution = BooleanField('RIM distribution')
    debt_percentage = BooleanField('Debt %')
    lending_percentage = BooleanField('Lending %')
    created_percentage = BooleanField('Created RIM %')
    bank_profit_spending_percentage = BooleanField('Bank profit % spending')
