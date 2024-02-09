from flask import Flask
from config import DevelopmentConfig
from extensions import db, bootstrap, login_manager, debug_toolbar
from routes import auth, dashboard, weather_api

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db.init_app(app)
bootstrap.init_app(app)
debug_toolbar.init_app(app)
login_manager.init_app(app)

login_manager.login_view = 'auth.login'

app.register_blueprint(auth.auth_bp)
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(weather_api.weather_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
