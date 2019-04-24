# cockpit/__init__.py

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from pathlib import Path
import sys

# So we can continue using absolute module paths from within the emusim
# module started with -m: update sys.path to include current path
sys.path.append( str( Path( __file__ ).parent ) )

from emusim.cockpit.supply.views.euro_supply import euro_supply
from emusim.cockpit.supply.views.sumsy_supply import sumsy_supply
from emusim.cockpit.overshoot.views.overshoot import overshoot
from emusim.cockpit.supply.views.home import home
from emusim.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CSRFProtect(app)
# mongo = PyMongo(app)
# client = mongo.cx
app.register_blueprint(euro_supply)
app.register_blueprint(sumsy_supply)
app.register_blueprint(overshoot)
app.register_blueprint(home)

if __name__ == '__main__':
    app.run(debug=False)
