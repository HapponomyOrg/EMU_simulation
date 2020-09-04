# cockpit/__init__.py
from pathlib import Path
import sys

from emusim import create_app
# So we can continue using absolute module paths from within the emusim
# module started with -m: update sys.path to include current path
sys.path.append(str(Path(__file__).parent))


app = create_app()


if __name__ == '__main__':
    app.run(debug=False)
