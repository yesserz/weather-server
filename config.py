# config.py

class Config:
    pass
    # Общая конфигурация


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = '/RYa97dGYjQ8(_-g'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://yesserz:egor2008224183@localhost:5432/weather_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    BOOTSTRAP_SERVE_LOCAL = True


class ProductionConfig(Config):
    DEBUG = False
    # Дополнительные параметры для продакшна


class LoggingConfig:
    LOGGING_LEVEL = 10
    ADVANCED_ERROR_OUTPUT = True



class WeatherAPICfg:
    MAX_HOURS = 240
    DEFAULT_HOURS = 1
    MAX_AMOUNT = 1000
    DEFAULT_AMOUNT = 10

    MIN_TEMPERATURE = -60
    MAX_TEMPERATURE = 60

    MIN_HUMIDITY = 0
    MAX_HUMIDITY = 100

    MIN_PRESSURE = 400
    MAX_PRESSURE = 1200

    MIN_WIND_SPEED = 0
    MAX_WIND_SPEED = 100

    MAX_RAIN_INTENSITY = 100

    MAX_LINES = 1000

    CUSTOM_DATA_MAX_LENGTH = 256  # DON'T CHANGE!
