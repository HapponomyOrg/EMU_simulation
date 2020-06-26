from flask import Blueprint, redirect, request, url_for, render_template
from emusim.cockpit.supply.forms.home_forms import LicenseForm

home = Blueprint('home', __name__,
                 template_folder='../templates',
                 static_folder='../static')


@home.route('/cockpit')
def cockpit():
    return render_template('base.html')

#loreco implementation: /dry endpoint iso /
#loreco implementation: endpoint / refers to router between happonomy neat, happonomy design and loreco abm
@home.route('/dry', methods=['GET', 'POST'])
def accept_tc():
    license_form = LicenseForm(request.form)
    if license_form.validate_on_submit() and license_form.license_accept.data == True:
        return redirect(url_for("home.cockpit"))
    return render_template('home.html',
                           license_form=license_form)
