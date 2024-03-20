from flask import Flask
from config import TestingConfig, DevelopmentConfig
from extensions import db, bootstrap, login_manager, debug_toolbar
from routes import auth, dashboard, weather_api, stations
from logger import myLog
from db.db_models import create_testing_data

log = myLog(__name__)
app = Flask(__name__)

config = DevelopmentConfig  # режим работы приложения
log.info(f'starting app in {config.WEATHER_APP_MODE.lower()} mode')

app.config.from_object(config)
log.info(f'app configurations loaded successfully')

db.init_app(app)
log.info(f'db initialized successfully')
bootstrap.init_app(app)
log.info(f'bootstrap initialized successfully')
login_manager.init_app(app)
log.info(f'login manager initialized successfully')

if config.WEATHER_APP_MODE == 'DEVELOPMENT':
    debug_toolbar.init_app(app)
    log.info(f'debug toolbar initialized successfully')

login_manager.login_view = 'auth.login'

app.register_blueprint(auth.auth_bp)
app.register_blueprint(dashboard.dashboard_bp)
app.register_blueprint(weather_api.weather_bp)
app.register_blueprint(stations.stations_bp)
log.info(f'blueprints registered successfully')

with app.app_context():
    db.create_all()
    log.info(f'database created successfully')

    if config.TESTING:
        create_testing_data()
        log.info(f'testing data created successfully')

log.info(f'app started successfully!')

if __name__ == '__main__':
    app.run(debug=True)
