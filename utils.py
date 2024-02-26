from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

moscow_tz = pytz.timezone('Europe/Moscow')


def check_hash(password, hashed_password):
    """
    Проверяет соответствие пароля хешу.
    """
    return check_password_hash(hashed_password, password)


def generate_hash(password):
    """
    Генерирует хеш для пароля.
    """
    return generate_password_hash(password, method='sha256')


def check_weather_limits(temperature, humidity, pressure):
    pass


def get_moscow_time():
    """
    Получение времени МСК (сдвиг по часовому поясу)
    """
    now = datetime.now()
    moscow_time = now.astimezone(moscow_tz)
    moscow_time = moscow_time.replace(tzinfo=None)
    return moscow_time
