# cockpit/__init__.py

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_user import UserManager
from flask_user.email_adapters import SendgridEmailAdapter
import sys

# So we can continue using absolute module paths from within the emusim
# module started with -m: update sys.path to include current path
sys.path.append(str(Path(__file__).parent))

from emusim.cockpit.supply.views.euro_supply import euro_supply
from emusim.cockpit.supply.views.sumsy_supply import sumsy_supply
from emusim.cockpit.overshoot.views.overshoot import overshoot
from emusim.cockpit.supply.views.home import home
#from emusim.cockpit.abm.views.abm import abm
from emusim.cockpit.supply.views.euro_supply_d import euro_supply_d
from emusim.cockpit.supply.views.sumsy_supply_d import sumsy_supply_d
from emusim.cockpit.overshoot.views.overshoot_d import overshoot_d
from emusim.cockpit.supply.views.home_d import home_d
from emusim.cockpit.abm.views.abm_d import abm_in_flask

from emusim.config import Config

# Instantiate Flask extensions
db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Load common settings
    app.config.from_object('emusim.settings')
    # Load environment specific settings
    app.config.from_object('emusim.local_settings')

    # Setup Flask-SQLAlchemy
    db.init_app(app)
    # Setup Flask-Mail-SendGrid
    mail.init_app(app)
    # Setup WTForms CSRFProtect
    CSRFProtect(app)



    # Setup an error-logger to send emails to app.config.ADMINS
    #init_email_error_handler(app)
    # Setup Flask-User to handle user account related forms
    from emusim.cockpit.abm.db.user_models import User
    # Setup Flask-User
    user_manager = UserManager(app, db, User)
    # Customize Flask-User
    user_manager.email_adapter = SendgridEmailAdapter(app)

    @app.context_processor
    def context_processor():
        return dict(user_manager=user_manager)

    # mongo = PyMongo(app)
    # client = mongo.cx
    app.register_blueprint(euro_supply)
    app.register_blueprint(sumsy_supply)
    app.register_blueprint(overshoot)
    # app.register_blueprint(abm)
    app.register_blueprint(home)

    app.register_blueprint(euro_supply_d)
    app.register_blueprint(sumsy_supply_d)
    app.register_blueprint(overshoot_d)
    app.register_blueprint(abm_in_flask)
    app.register_blueprint(home_d)
    from emusim.cockpit.abm.views.user_views import user_blueprint
    app.register_blueprint(user_blueprint)

    return app


def init_email_error_handler(app):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to app.config.ADMINS.
    """
    if app.debug: return  # Do not send error emails while developing

    # Retrieve email settings from app.config
    host = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    # Log errors using: app.logger.error('Some error message')


if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
