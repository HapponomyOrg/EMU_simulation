from flask_wtf import FlaskForm
from wtforms import DateField
from datetime import date


class DateForm(FlaskForm):
    target_date = DateField('Consumption date', default=date.today())