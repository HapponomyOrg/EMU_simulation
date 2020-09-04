# Settings common to all environments (development|staging|production)
# Place environment specific settings in env_settings.py

import os

# Application settings
APP_NAME = "LoREco"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask settings
CSRF_ENABLED = True

# Flask-SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-User settings
USER_APP_NAME = APP_NAME
USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
USER_ENABLE_CONFIRM_EMAIL = True  # Force users to confirm their email
USER_ENABLE_FORGOT_PASSWORD = True  # Allow users to reset their passwords
USER_ENABLE_EMAIL = True  # Register with Email
USER_ENABLE_REGISTRATION = True  # Allow new users to register
USER_REQUIRE_RETYPE_PASSWORD = True  # Prompt for `retype password` in:
USER_ENABLE_USERNAME = False  # Register and Login with username

#Flask-User Endpoints
USER_AFTER_LOGIN_ENDPOINT = 'abm_in_flask.moneymodel'
USER_AFTER_LOGOUT_ENDPOINT = 'home_d.lorecosimhome'
USER_AFTER_REGISTER_ENDPOINT = 'abm_in_flask.moneymodel'
USER_AFTER_CHANGE_USERNAME_ENDPOINT = 'abm_in_flask.moneymodel'
USER_AFTER_CHANGE_PASSWORD_ENDPOINT = 'abm_in_flask.moneymodel'
USER_AFTER_FORGOT_PASSWORD_ENDPOINT = 'home_d.lorecosimhome'
USER_AFTER_CONFIRM_ENDPOINT = 'abm_in_flask.moneymodel'