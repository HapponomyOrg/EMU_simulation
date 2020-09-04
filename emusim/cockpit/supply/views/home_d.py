from flask import Blueprint, redirect, request, url_for, render_template
from emusim.cockpit.supply.forms.home_forms import LicenseForm

home_d = Blueprint('home_d', __name__,
                 template_folder='../templates',
                 static_folder='../static')


@home_d.route('/')
def approuter():
    return render_template('approuter.html')

@home_d.route('/cockpit_d')
def cockpit():
    return render_template('base_d.html')


@home_d.route('/design', methods=['GET', 'POST'])
def accept_tc():
    license_form = LicenseForm(request.form)

    if license_form.validate_on_submit() and license_form.license_accept.data == True:
        return redirect(url_for("home_d.cockpit"))

    return render_template('home_d.html',
                           license_form=license_form)


@home_d.route('/home')
def nav():
    return render_template('home_d.html')


@home_d.route('/loreco')
def loreco():
    return redirect('https://www.loreco.be')


@home_d.route('/lorecosimhome')
def lorecosimhome():
    return render_template('lorecosimhome.html')


@home_d.route('/lorecotool')
def lorecotool():
    return render_template('lorecotool.html')