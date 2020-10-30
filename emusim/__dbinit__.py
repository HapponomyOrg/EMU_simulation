# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime
import os

from flask import current_app

from emusim import db
from emusim.__main__ import create_app
from emusim.cockpit.abm.db.user_models import User, Role, ModelParameters



def init_db():
   # app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')
    """ Initialize the database."""
    db.drop_all()
    db.create_all()
    create_users()


def create_users():
    """ Create users """

    # Create all tables
    db.create_all()

    # Adding roles
    admin_role = find_or_create_role('admin', u'Admin')


    # Add users
    user = find_or_create_user(u'Admin', u'Example', u'admin@example.com', 'Password1', admin_role)
    user = find_or_create_user(u'Member', u'Example', u'member@example.com', 'Password1')
    user = find_or_create_user(u'Lansen', u'Puttemans', u'lansen.puttemans@howest.be', 'Password1', admin_role)
    user = find_or_create_user(u'Jonas', u'Van Lancker', u'jonas.van.lancker@howest.be', 'Password1')
    user = find_or_create_user(u'Geert', u'Hofman', u'geert.hofman@howest.be', 'Password1')
    user = find_or_create_user(u'Stef', u'Kuypers', u'stef@happonomy.org', 'Password1')
    user = find_or_create_user(u'Bruno', u'Delepierre', u'bruno@happonomy.org', 'Password1')
    user = find_or_create_user(u'Hugo', u'Wanner', u'hugo@muntuit.be', 'Password1')
    user = find_or_create_user(u'Sander', u'Van Parijs', u'sander@muntuit.be', 'Password1')

    # Add modelparams
    users = User.query.all()
    for user in users:
        model_params = find_or_create_modelparams(user.id, 'Lichtervelde base', initial_wealth=None, wealth_transfer=None,
                                                  num_agents=200, iterations=100)
        model_params = find_or_create_modelparams(user.id, 'Lichtervelde 50%', initial_wealth=1, wealth_transfer=1,
                                                  num_agents=100, iterations=100)
        model_params = find_or_create_modelparams(user.id, 'Lichtervelde 200%', initial_wealth=1, wealth_transfer=1,
                                                  num_agents=400, iterations=100)
        model_params = find_or_create_modelparams(user.id, 'Lichtervelde base wealthy', initial_wealth=10, wealth_transfer=2,
                                                  num_agents=200, iterations=100)

    # Save to DB
    db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role


def find_or_create_user(first_name, last_name, email, password, role=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=current_app.user_manager.password_manager.hash_password(password),
                    active=True,
                    email_confirmed_at=datetime.datetime.utcnow())
        if role:
            user.roles.append(role)
        db.session.add(user)
    return user


def find_or_create_modelparams(user_id, name, initial_wealth=None, wealth_transfer=None, num_agents=None, iterations=None):
    """ Find existing role or create new role """
    params = ModelParameters.query.filter(ModelParameters.user_id == user_id, ModelParameters.name == name).first()
    if not params:
        params = ModelParameters(user_id=user_id,name=name, initial_wealth=initial_wealth,wealth_transfer=wealth_transfer,
                                 num_agents=num_agents,iterations=iterations)
        db.session.add(params)
    return params


if __name__ == '__main__':
    app = create_app()
    app.app_context().push() #Alternatively, use the with-statement to take care of setup and teardown: with app.app_context():
    init_db()
    print('Database has been initialized.')
