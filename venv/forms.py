from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from constants import *


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ParameterForm(FlaskForm):
    num_iterations = IntegerField('Iterations', default=500)
    initial_im2 = FloatField('Initial IM2', default=100000)

    growth_rate = FloatField('Growth rate', default=0.0)
    inflation_rate = FloatField('Inflation rate', default=1.9)

    minimum_reserve = FloatField('Minimum reserve', default=4.0)

    bank_payback_rate = FloatField('Bank payback rate', default=10.0)
    private_payback_rate = FloatField('Private payback rate', default=5.0)

    ecb_interest = FloatField('ECB interest', default=1.0)
    bank_interest = FloatField('Commercial bank interest', default=2.5)
    savings_interest = FloatField('Savings interest', default=0.5)

    savings_rate = FloatField('Savings rate', default=20.0)

    min_new_money = FloatField('Minimum new money', default=100.0)

    min_desired_reserve = FloatField('Minimum desired bank reserve', default=0.0)

    no_loss = BooleanField('No loss')
    min_profit = FloatField('Minimum profit', default=20.0)

    spending_mode = SelectField('Bank spending mode',
                                choices=[(FIXED, 'Fixed'),
                                         (PROFIT_PERCENTAGE, 'Percentage of profit'),
                                         (CAPITAL_PERCENTAGE, 'Percentage of capital')])

    fixed_spending = FloatField('Fixed spending', default=1000.0)
    profit_spending = FloatField('Profit spending', default=2.0)
    capital_spending = FloatField('Capital spending', default=2.0)

    qe_mode = SelectField('QE mode',
                          choices=[(QE_NONE, 'No QE'),
                                   (QE_FIXED, 'Fixed QE'),
                                   (QE_RELATIVE, 'Percentage of private debt')])
    qe_trickle_rate = FloatField('QE trickle', default=0.0)

    qe_fixed = FloatField('Fixed QE', default=1000.0)
    qe_relative = FloatField('Relative QE', default=2.0)


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
