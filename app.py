from flask import Flask
from config import DevelopmentConfig
from extensions import db, bootstrap, login_manager, debug_toolbar
from routes import auth, dashboard, weather_api
from logger import myLog

log = myLog(__name__)
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
log.info(f'app onfigurations loaded successfully')

db.init_app(app)
log.info(f'db initialized successfully')
bootstrap.init_app(app)
log.info(f'bootstrap initialized successfully')
debug_toolbar.init_app(app)
log.info(f'debug toolbar initialized successfully')
login_manager.init_app(app)
log.info(f'login manager initialized successfully')

login_manager.login_view = 'auth.login'

app.register_blueprint(auth.auth_bp)
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(weather_api.weather_bp)
log.info(f'blueprints registered successfully')


with app.app_context():
    db.create_all()
    log.info(f'database created successfully')

if __name__ == '__main__':
    app.run(debug=True)
