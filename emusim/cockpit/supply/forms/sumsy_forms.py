from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField

from emusim.cockpit.supply.constants import *


class ParameterForm(FlaskForm):
    num_iterations = IntegerField('Iterations', default=500)
    inflation = FloatField('Inflation rate', default=0.0)
    population = IntegerField('Population', default=5000)
    population_growth = FloatField('Population growth rate', default=0.0)
    money_mass = FloatField('Money mass', default=100000)
    income = FloatField('Guaranteed income', default=2000.0)
    num_dem_tiers = SelectField('Common good spending mode',
                                choices=[(1, '1 tier'),
                                         (2, '2 tiers'),
                                         (3, '3 tiers'),
                                         (4, '4 tiers'),
                                         (5, '5 tiers')], coerce=int)

    dem_tier_1 = FloatField('Demurrage tier 1', default=50000.0)
    dem_tier_2 = FloatField('Demurrage tier 2', default=250000.0)
    dem_tier_3 = FloatField('Demurrage tier 3', default=1000000.0)
    dem_tier_4 = FloatField('Demurrage tier 4', default=5000000.0)
    dem_tier_5 = FloatField('Demurrage tier 5', default=10000000.0)

    dem_rate_1 = FloatField('Demurrage rate 1', default=0.01)
    dem_rate_2 = FloatField('Demurrage rate 2', default=0.05)
    dem_rate_3 = FloatField('Demurrage rate 3', default=0.1)
    dem_rate_4 = FloatField('Demurrage rate 4', default=0.5)
    dem_rate_5 = FloatField('Demurrage rate 5', default=0.9)

    common_good_spending = SelectField('Common good spending mode',
                                       choices=[(NONE, 'None'),
                                                (FIXED_SPENDING, 'Fixed'),
                                                (PER_CAPITA, 'Per capita')])
    common_good_budget = FloatField('Common good budget', default=0.0)


class DataSelectionForm(FlaskForm):
    population = BooleanField('Population')

    demurrage = BooleanField('Demurrage')
    demurrage_deflate = BooleanField('Deflate')

    per_capita_demurrage = BooleanField('Demurrage per capita')
    per_capita_demurrage_deflate = BooleanField('Deflate')

    new_money = BooleanField('New money')
    new_money_deflate = BooleanField('Deflate')

    per_capita_new_money = BooleanField('New money per capita')
    per_capita_new_money_deflate = BooleanField('Deflate')

    money_mass = BooleanField('Money mass')
    money_mass_deflate = BooleanField('Deflate')

    per_capita_money_mass = BooleanField('Money mass per capita')
    per_capita_money_mass_deflate = BooleanField('Deflate')

    common_good = BooleanField('Common good spending')
    common_good_deflate = BooleanField('Deflate')

    percentages = BooleanField('Percentages of total money mass')
