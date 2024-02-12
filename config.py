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
    BOOTSTRAP_SERVE_LOCAL = True


class ProductionConfig(Config):
    DEBUG = False
    # Дополнительные параметры для продакшна
