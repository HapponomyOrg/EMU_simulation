import os

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
#SECRET_KEY = 'This is an UNSECURE Secret. CHANGE THIS for production environments.'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
#MAIL_SERVER = 'smtp.sendgrid.net'
#MAIL_PORT = 587
#MAIL_USE_SSL = False
#MAIL_USE_TLS = True
#MAIL_USERNAME = 'apikey'
#MAIL_PASSWORD = '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'

# Sendgrid settings
#SENDGRID_API_KEY=''
#api key not hardcoded, but loaded from the os environment

# Flask-User settings
USER_APP_NAME = 'LoREco'
#USER_EMAIL_SENDER_NAME = 'Jonas Van Lancker'
USER_EMAIL_SENDER_EMAIL = 'jonas.vanlancker@howest.be'

ADMINS = [
    '"Admin One" <lansen.puttemans@howest.be>',
    ]
