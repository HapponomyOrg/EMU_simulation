from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField

from emusim.cockpit.supply.constants import *


class ParameterForm(FlaskForm):
    num_agents = IntegerField('Number of Agents', default=500)
    iterations = IntegerField('Number of Iterations', default=100)

