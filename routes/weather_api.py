from flask import jsonify, Blueprint, request
from db.db_users import WeatherData
from datetime import timedelta
from utils import get_moscow_time

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/api/weather/get_current_data', methods=['GET'])
def get_weather_data():
    station_id = request.args.get('station_id', default=None)
    if station_id is None:
        return jsonify({'error': 'station_id is required'}), 400
    data = WeatherData.query.filter_by(station_id=station_id).first()
    if data is None:
        return jsonify({'error': 'no data for this station'}), 400
    data_json = {
        'id': data.id,
        'station_id': data.station_id,
        'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'temperature': data.temperature,
        'humidity': data.humidity,
        'pressure': data.pressure,
        'wind_speed': data.wind_speed,
        'wind_direction': data.wind_direction,
        'rain_intensity': data.rain_intensity
    }
    return jsonify(data_json), 200


@weather_bp.route('/api/weather/get_historical_data', methods=['GET'])
def get_historical_weather_data():
    enclosure_json = request.args.get('enclosure', default=0)  # TODO: Дописать варианты формирования json
    amount = request.args.get('amount', default=None)
    hours = request.args.get('hours', default=None)

    latest_data = None

    if amount is None and hours is not None:
        try:
            hours = int(hours)
        except ValueError:
            return jsonify({'error': 'days must be an integer'}), 400

        time_for_query = get_moscow_time() - timedelta(hours=int(hours))
        latest_data = WeatherData.query.filter(WeatherData.timestamp >= time_for_query).order_by(
            WeatherData.timestamp).all()
    if amount is not None:
        try:
            amount = int(amount)
        except ValueError:
            return jsonify({'error': 'amount must be an integer'}), 400
        latest_data = WeatherData.query.order_by(WeatherData.id.desc()).limit(int(amount)).all()

    if latest_data is None:
        return jsonify({'error': 'no data for this station'}), 400
    else:
        # Преобразуем данные в формат JSON
        data_json = [{
            'id': data.id,
            'station_id': data.station_id,
            'timestamp': data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': data.temperature,
            'humidity': data.humidity,
            'pressure': data.pressure,
            'wind_speed': data.wind_speed,
            'wind_direction': data.wind_direction,
            'rain_intensity': data.rain_intensity
        } for data in latest_data]

        return jsonify(data_json), 200
