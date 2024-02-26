from flask import jsonify, Blueprint, request
from flask_login import login_required, current_user
from db.db_users import WeatherData, WeatherStation
from datetime import timedelta
from utils import get_moscow_time

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/api/weather/get_current_data', methods=['GET'])
def get_weather_data():
    station_id = request.args.get('station_id', default=None)
    stations_ids = WeatherStation.query.with_entities(WeatherStation.id).order_by(WeatherStation.id.desc()).all()
    stations_id_list = [idx[0] for idx in stations_ids]
    if station_id is None:
        return jsonify({'error': 'station_id is required'}), 400
    if station_id not in stations_id_list:
        return jsonify({'error': 'incorrect station_id'}), 400
    latest_data = WeatherData.query.filter_by(station_id=station_id).first()
    if latest_data is None:
        return jsonify({'error': 'no data for this station'}), 400
    data_json = make_weather_json(latest_data, True)
    return jsonify(data_json), 200


@weather_bp.route('/api/weather/get_all_historical_data', methods=['GET'])
@login_required
def get_all_historical_weather_data():
    amount = request.args.get('amount', default=10)
    try:
        amount = int(amount)
    except ValueError:
        return jsonify({'error': 'amount must be an integer'}), 400

    if current_user.is_admin():
        latest_data = WeatherData.query.order_by(WeatherData.timestamp.desc()).limit(amount)
        if latest_data is not None:
            data_json = make_weather_json(latest_data)
            return jsonify(data_json), 200

        else:
            return jsonify({'error': 'no data for this station'}), 400


@weather_bp.route('/api/weather/get_historical_data', methods=['GET'])
def get_historical_weather_data():
    enclosure_json = request.args.get('enclosure', default=0)  # TODO: Дописать варианты формирования json
    station_id = request.args.get('station_id', default=None)
    amount = request.args.get('amount', default=None)
    hours = request.args.get('hours', default=None)

    if amount is None and hours is None:
        amount = 10

    latest_data = None
    stations_ids = WeatherStation.query.with_entities(WeatherStation.id).order_by(WeatherStation.id.desc()).all()
    stations_id_list = [idx[0] for idx in stations_ids]

    if station_id is None:
        return jsonify({'error': 'station_id is required'}), 400
    if station_id not in stations_id_list:
        return jsonify({'error': 'no such station'}), 400

    if amount is None and hours is not None:
        try:
            hours = int(hours)
        except ValueError:
            return jsonify({'error': 'hours must be an integer'}), 400

        time_for_query = get_moscow_time() - timedelta(hours=int(hours))
        latest_data = WeatherData.query.where(WeatherData.station_id == station_id).filter(
            WeatherData.timestamp >= time_for_query).order_by(
            WeatherData.timestamp).all()
    if amount is not None:
        try:
            amount = int(amount)
        except ValueError:
            return jsonify({'error': 'amount must be an integer'}), 400
        latest_data = WeatherData.query.where(WeatherData.station_id == station_id).filter(
            WeatherData.station_id == station_id).order_by(
            WeatherData.id.desc()).limit(int(amount)).all()

    if latest_data is None or len(latest_data) == 0:
        return jsonify({'error': 'no data for this station'}), 400
    else:
        # Преобразуем данные в формат JSON
        data_json = make_weather_json(latest_data)
        return jsonify(data_json), 200


def make_weather_json(raw_data, notList=False):
    """
    Преобразовывает данные в формат JSON.
    """
    raw_weather_data = []
    if notList:
        raw_weather_data.append(raw_data)
    else:
        raw_weather_data = raw_data

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
    } for data in raw_weather_data]

    return data_json
