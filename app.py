from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.weather_api import weather_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(weather_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
