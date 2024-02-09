from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_debugtoolbar import DebugToolbarExtension


db = SQLAlchemy()
bootstrap = Bootstrap5()
debug_toolbar = DebugToolbarExtension()
login_manager = LoginManager()
