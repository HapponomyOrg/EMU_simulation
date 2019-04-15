from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField

from emusim.cockpit.supply.constants import *


class ParameterForm(FlaskForm):
    num_iterations = IntegerField('Iterations', default=500)
    inflation = FloatField('Inflation rate', default=0.0)
    population = IntegerField('Initial population', default=100000)
    population_growth = FloatField('Population growth rate', default=0.0)
    start_at_saturation = BooleanField('Start at saturation')
    money_mass = FloatField('Initial money mass', default=100000)
    income = FloatField('Guaranteed income', default=2000.0)
    num_dem_tiers = SelectField('Inflation tiers',
                                choices=[(5, '5 tiers'),
                                         (4, '4 tiers'),
                                         (3, '3 tiers'),
                                         (2, '2 tiers'),
                                         (1, '1 tier')], coerce=int)

    dem_tier_1 = FloatField('Demurrage tier 1', default=50000.0)
    dem_tier_2 = FloatField('Demurrage tier 2', default=250000.0)
    dem_tier_3 = FloatField('Demurrage tier 3', default=1000000.0)
    dem_tier_4 = FloatField('Demurrage tier 4', default=5000000.0)
    dem_tier_5 = FloatField('Demurrage tier 5', default=10000000.0)

    dem_rate_1 = FloatField('Demurrage rate 1', default=1)
    dem_rate_2 = FloatField('Demurrage rate 2', default=5)
    dem_rate_3 = FloatField('Demurrage rate 3', default=10)
    dem_rate_4 = FloatField('Demurrage rate 4', default=50)
    dem_rate_5 = FloatField('Demurrage rate 5', default=90)

    common_good_spending = SelectField('Common good spending mode',
                                       choices=[(NONE, 'None'),
                                                (FIXED_SPENDING, 'Fixed'),
                                                (PER_CAPITA, 'Per capita')])
    common_good_budget = FloatField('Common good budget', default=0.0)


class DataSelectionForm(FlaskForm):
    population = BooleanField('Population')

    deflate = BooleanField('Deflate')
    demurrage_tiers = BooleanField('Demurrage tiers')
    demurrage = BooleanField('Demurrage')
    per_capita_demurrage = BooleanField('Demurrage per capita')
    money_cycle = BooleanField('Money creation and destruction')
    per_capita_money_cycle = BooleanField('Money creation and destruction per capita')
    money_mass = BooleanField('Money mass')
    per_capita_money_mass = BooleanField('Money mass per capita')
    common_good = BooleanField('Common good spending')

    percentages = BooleanField('Percentages of total money mass')
