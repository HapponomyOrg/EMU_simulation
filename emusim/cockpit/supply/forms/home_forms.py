from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, FloatField, IntegerField

from emusim.cockpit.supply.constants import *


class LicenseForm(FlaskForm):
    license_accept = BooleanField('I accept the terms and conditions')