from flask import Blueprint, redirect, render_template, flash
from flask_user import current_user, login_required, roles_required

from emusim.cockpit.abm.db.user_models import User, ModelParameters

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')

@admin_blueprint.route('/platformusers')
@login_required  # Limits access to authenticated users
@roles_required('admin')
def platformusers_page():
    users = User.query.all()
    return render_template('admin/platformusers.html', users=users)

@admin_blueprint.route('/platformmodels')
@login_required  # Limits access to authenticated users
@roles_required('admin')
def platformmodels_page():
    models = ModelParameters.query.all()
    return render_template('admin/platformmodels.html', models=models)


