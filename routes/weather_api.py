from flask import jsonify, Blueprint
from db.db_users import WeatherData

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/api/weather/get_latest_weather_data')
def get_latest_weather_data():
    # Получаем последние данные из базы данных
    latest_data = WeatherData.query.order_by(WeatherData.timestamp.desc()).limit(10).all()

    # Преобразуем данные в формат JSON
    data_json = [{
        'id': data.id,
        'station_name': data.id,
        'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'temperature': data.temperature,
        'humidity': data.humidity,
        'pressure': data.pressure,
        'wind_speed': data.wind_speed,
        'wind_direction': data.wind_direction,
        'rain_intensity': data.rain_intensity
    } for data in latest_data]

    return jsonify(data_json)
