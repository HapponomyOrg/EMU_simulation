from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField

from cockpit.supply.constants import *


class ParameterForm(FlaskForm):
    num_iterations = IntegerField('Iterations', default=500)
    initial_im = FloatField('Initial IM', default=100000)

    growth_rate = FloatField('Growth rate', default=0.0)
    inflation_rate = FloatField('Inflation rate', default=1.9)

    ecb_interest_rate = FloatField('ECB interest', default=1.0)
    ecb_savings_rate_mr = FloatField('ECB interest rate on minimal reserve', default=0.0)
    ecb_savings_rate_excess = FloatField('ECB interest rate on excess reserve', default=-0.15)

    minimum_reserve = FloatField('Minimum reserve', default=4.0)
    maximum_reserve = FloatField('Maximum bank reserve', default=8.0)
    min_new_money = FloatField('Minimum new money', default=80.0)
    max_new_money = FloatField('Maximum new money', default=100.0)
    bank_interest_rate = FloatField('Commercial bank interest', default=2.5)
    bank_payback_rate = FloatField('Bank payback rate', default=100.0)
    no_loss = BooleanField('No loss')
    min_profit = FloatField('Minimum profit', default=20.0)
    spending_mode = SelectField('Bank spending mode',
                                choices=[(FIXED, 'Fixed'),
                                         (PROFIT_PERCENTAGE, '% of profit'),
                                         (CAPITAL_PERCENTAGE, '% of capital')])
    fixed_spending = FloatField('Fixed spending', default=1000.0)
    profit_spending = FloatField('Profit spending', default=2.0)
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
    private_payback_rate = FloatField('Private payback rate', default=5.0)


class DataSelectionForm(FlaskForm):
    om = BooleanField('OM data')
    om_deflate = BooleanField('Deflate')

    im = BooleanField('IM data')
    im_deflate = BooleanField('Deflate')

    bank = BooleanField('Bank data')
    bank_deflate = BooleanField('Deflate')

    private = BooleanField('Private sector data')
    private_deflate = BooleanField('Deflate')

    qe = BooleanField('QE data')
    qe_deflate = BooleanField('Deflate')

    im_distribution = BooleanField('IM distribution')
    debt_percentage = BooleanField('Debt %')
    lending_percentage = BooleanField('Lending %')
    created_percentage = BooleanField('Created IM %')
