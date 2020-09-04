# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import Blueprint, redirect, render_template, flash
from flask import request, url_for
from flask_user import current_user, login_required, roles_required

from emusim import db
from emusim.cockpit.abm.db.user_models import UserProfileForm, ModelParameters
from emusim.cockpit.abm.forms.abm_forms_d import ParameterForm
from emusim.cockpit.abm.views.abm_d import moneymodel_model

user_blueprint = Blueprint('main', __name__, template_folder='templates')


# The Home page is accessible to anyone
@user_blueprint.route('/main')
def home_page():
    return render_template('main/home_page.html')


# The User page is accessible to authenticated users (users that have logged in)
@user_blueprint.route('/models')
@login_required  # Limits access to authenticated users
def models_page():
    models = ModelParameters.query.filter(ModelParameters.user_id == current_user.id).all()
    return render_template('main/models_page.html', models=models)

@user_blueprint.route('/modeldelete/<modelID>', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def delete_model(modelID):
    modelparams = ModelParameters.query.filter(ModelParameters.id == modelID).first()
    if modelparams.user_id == current_user.id:
        db.session.delete(modelparams)
        db.session.commit()
        flash('Your model has been deleted.')
        return redirect(url_for('main.models_page'))
    else:
        flash('Sorry, you have no access to this model')
        return redirect(url_for('abm_in_flask.moneymodel'))


@user_blueprint.route('/modeledit/<modelID>', methods=['GET', 'POST'])
@user_blueprint.route('/modeledit', methods=['GET', 'POST'])
@login_required  # Limits access to authenticated users
def edit_model(modelID=None):
    parameter_form = ParameterForm(request.form)
    if modelID:
        print(modelID)
        modelparams = ModelParameters.query.filter(ModelParameters.id == modelID).first()
        if request.method == 'GET':
            if modelparams.user_id == current_user.id:
                parameter_form = ParameterForm(obj=modelparams)
                return render_template('main/models_edit_page.html', parameter_form=parameter_form)
            else:
                flash('Sorry, you have no access to this model')
                return redirect(url_for('abm_in_flask.moneymodel'))
        if request.method == 'POST':
            parameter_form.populate_obj(modelparams)
            modelparams.id = modelID
            db.session.commit()
            flash('Your model has been updated.')
            return redirect(url_for('main.models_page'))
    # change existing model with the new params
    else:
        if request.method == 'GET':
            return render_template('main/models_edit_page.html', parameter_form=parameter_form)
        # Process valid POST
        if request.method == 'POST' and parameter_form.validate():
            # Copy form fields to user_profile fields

            modelparams = ModelParameters(name=parameter_form.name.data, user_id=current_user.id,
                                          initial_wealth=parameter_form.initial_wealth.data,
                                          wealth_transfer=parameter_form.wealth_transfer.data,
                                          num_agents=parameter_form.num_agents.data,
                                          iterations=parameter_form.iterations.data)
            db.session.add(modelparams)
            db.session.commit()
            # Redirect to models list
            return redirect(url_for('main.models_page'))


@user_blueprint.route('/models/<modelID>')
@login_required  # Limits access to authenticated users
def models_run(modelID):
    model = ModelParameters.query.filter(ModelParameters.id == modelID,
                                         ModelParameters.user_id == current_user.id).first()
    if (not model):
        flash('Model doesn\'t exist or is not accessible')
        return models_page()
    parameter_form = ParameterForm(obj=model)
    return moneymodel_model(model, parameter_form)


# The Admin page is accessible to users with the 'admin' role
@user_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('main/admin_page.html')


@user_blueprint.route('/main/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('abm_in_flask.moneymodel'))

    # Process GET or invalid POST
    return render_template('flask_user/edit_user_profile.html',
                           form=form)
