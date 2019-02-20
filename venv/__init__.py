# cockpit/__init__.py

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from cockpit.supply.views.euro_supply import euro_supply
from cockpit.supply.views.sumsy_supply import sumsy_supply
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CSRFProtect(app)
# mongo = PyMongo(app)
# client = mongo.cx
app.register_blueprint(euro_supply)
app.register_blueprint(sumsy_supply)

app.run(debug=False)