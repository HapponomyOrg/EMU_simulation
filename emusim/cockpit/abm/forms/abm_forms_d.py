from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField, StringField

from emusim.cockpit.supply.constants import *


class ParameterForm(FlaskForm):
    id = IntegerField('ID')
    name = StringField('Model name')
    initial_wealth = IntegerField('Initial Wealth of Agents', default=1)
    wealth_transfer = IntegerField('Wealth Transfer Amount', default=1)
    num_agents = IntegerField('Number of Agents', default=50)
    iterations = IntegerField('Number of Iterations', default=100)


