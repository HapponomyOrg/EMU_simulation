from flask import Blueprint, redirect, request, url_for, render_template
from emusim.cockpit.supply.forms.home_forms import LicenseForm

abm = Blueprint('abm', __name__,
                 template_folder='../templates',
                 static_folder='../static')


@abm.route('/cockpit')
def cockpit():
    return render_template('base.html')


@abm.route('/', methods=['GET', 'POST'])
def accept_tc():
    license_form = LicenseForm(request.form)

    if license_form.validate_on_submit() and license_form.license_accept.data == True:
        return redirect(url_for("abm.cockpit"))

    return render_template('abm.html',
                           license_form=license_form)
