from flask import jsonify, Blueprint, request
from flask_login import login_required, current_user
from werkzeug import exceptions
from db.db_users import WeatherData, WeatherStation
from datetime import timedelta
from utils import get_moscow_time
from config import WeatherAPICfg, LoggingConfig
from typing import Union, List, Any
from extensions import db
from logger import myLog


log = myLog(__name__)
weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/api/weather/get_current_data', methods=['GET'])
def get_weather_data() -> jsonify:
    """
    Retrieves weather data for a specified weather station.

    Returns:
        jsonify: JSON response containing weather data.

    Raises:
        400 Bad Request: If 'station_id' is missing, incorrect, or no data is available for the station.
    """
    station_id = request.args.get('station_id', default=None)  # string
    stations_ids = WeatherStation.query.with_entities(WeatherStation.id).order_by(WeatherStation.id.desc()).all()
    stations_id_list = [idx[0] for idx in stations_ids]
    if station_id is None:
        log.debug('get_weather_data: station_id is missing')
        return jsonify({'error': 'station_id is required'}), 400
    if station_id not in stations_id_list:
        log.debug('get_weather_data: no such station')
        return jsonify({'error': 'incorrect station_id'}), 400
    latest_data = WeatherData.query.filter_by(station_id=station_id).first()
    if latest_data is None:
        log.debug('get_weather_data: no data for this station')
        return jsonify({'error': 'no data for this station'}), 400
    data_json = make_weather_json(latest_data, True)
    log.debug(f'get_weather_data: data_json: {data_json}')
    return jsonify(data_json), 200


@weather_bp.route('/api/weather/get_all_historical_data', methods=['GET'])
@login_required
def get_all_historical_weather_data() -> jsonify:
    """
    Retrieves historical weather data for a specified number of entries.

    Returns:
        jsonify: JSON response containing historical weather data.

    Raises:
        400 Bad Request: If 'amount' is not provided or not an integer.
    """
    amount = request.args.get('amount', default=10)
    try:
        amount = int(amount)
    except ValueError:
        log.debug('get_all_historical_weather_data: amount must be an integer')
        return jsonify({'error': 'amount must be an integer'}), 400

    if current_user.is_admin():
        latest_data = WeatherData.query.order_by(WeatherData.timestamp.desc()).limit(amount)
        if latest_data is not None:
            data_json = make_weather_json(latest_data)
            log.debug(f'get_all_historical_weather_data: data_json: {data_json}')
            return jsonify(data_json), 200
        else:
            log.debug('get_all_historical_weather_data: no data for this station')
            return jsonify({'error': 'no data for this station'}), 400


@weather_bp.route('/api/weather/get_historical_data', methods=['GET'])
def get_historical_weather_data() -> jsonify:
    """
    Retrieves historical weather data based on specified parameters.

    Returns:
        jsonify: JSON response containing historical weather data.

    Raises:
        400 Bad Request: If 'station_id' is missing, not valid, or no data is available for the station.
        400 Bad Request: If 'hours' is not a positive integer.
        400 Bad Request: If 'amount' is not a positive integer.
    """
    enclosure_json = request.args.get('enclosure', default=0)  # TODO: Дописать варианты формирования json
    station_id = request.args.get('station_id', default=None)
    amount = request.args.get('amount', default=None)
    hours = request.args.get('hours', default=None)

    if amount is None and hours is None:
        amount = WeatherAPICfg.DEFAULT_AMOUNT
        log.debug('get_historical_weather_data: amount is not provided')

    latest_data = None
    stations_ids = WeatherStation.query.with_entities(WeatherStation.id).order_by(WeatherStation.id.desc()).all()
    stations_id_list = [idx[0] for idx in stations_ids]  # idx - id, но с x для избежания конфликта с функцией питона

    if station_id is None:
        log.debug('get_historical_weather_data: station_id is missing')
        return jsonify({'error': 'station_id is required'}), 400
    if station_id not in stations_id_list:
        log.debug('get_historical_weather_data: no such station')
        return jsonify({'error': 'no such station'}), 400

    if amount is None and hours is not None:
        try:
            hours = int(hours)
            if hours < 0:
                log.debug('get_historical_weather_data: hours must be a positive number')
                return jsonify({'error': 'hours must be a positive number'}), 400
            if hours > WeatherAPICfg.MAX_HOURS:
                hours = WeatherAPICfg.DEFAULT_HOURS
        except ValueError:
            log.debug('get_historical_weather_data: hours must be an integer')
            return jsonify({'error': 'hours must be an integer'}), 400
        time_for_query = get_moscow_time() - timedelta(hours=int(hours))
        latest_data = WeatherData.query.where(WeatherData.station_id == station_id).filter(
            WeatherData.timestamp >= time_for_query).order_by(
            WeatherData.timestamp).limit(int(WeatherAPICfg.MAX_LINES)).all()

    if amount is not None:
        try:
            amount = int(amount)
            if amount < 0:
                log.debug('get_historical_weather_data: amount must be a positive number')
                return jsonify({'error': 'amount must be a positive number'}), 400
            if amount > WeatherAPICfg.MAX_AMOUNT:
                log.debug(f'get_historical_weather_data: amount is too high, setting it to {WeatherAPICfg.DEFAULT_AMOUNT}')
                amount = WeatherAPICfg.DEFAULT_AMOUNT
        except ValueError:
            log.debug('get_historical_weather_data: amount must be an integer')
            return jsonify({'error': 'amount must be an integer'}), 400
        latest_data = WeatherData.query.where(WeatherData.station_id == station_id).filter(
            WeatherData.station_id == station_id).order_by(
            WeatherData.id.desc()).limit(int(WeatherAPICfg.MAX_LINES)).all()

    if latest_data is None or len(latest_data) == 0:
        log.debug('get_historical_weather_data: no data for this station')
        return jsonify({'error': 'no data for this station'}), 400
    else:
        data_json = make_weather_json(latest_data)
        log.debug(f'get_historical_weather_data: returned data_json: {data_json}')
        return jsonify(data_json), 200


@weather_bp.route('/api/weather/add_data', methods=['POST'])
def add_historical_weather_data() -> jsonify:
    """
    Adds historical weather data to the database.

    Returns:
        jsonify: JSON response indicating success or failure.

    Raises:
        400 Bad Request: If the JSON body is missing or not valid.
        400 Bad Request: If any value is not within the specified limits or cannot be converted to a number.
        500 Internal Server Error: If there is an unexpected error.
    """
    try:
        try:
            weather_data = request.get_json()
        except (exceptions.UnsupportedMediaType, exceptions.BadRequest):
            log.debug('JSON body is missing or not valid', exc_info=LoggingConfig.ADVANCED_ERROR_OUTPUT)
            return jsonify({'error': 'JSON body is missing or not valid'}), 400
        # Проверки на наличие необходимых полей в JSON
        required_fields = ['station_id', 'temperature', 'humidity', 'pressure', 'wind_speed',
                           'wind_direction']
        for field in required_fields:
            if field not in weather_data:
                log.debug(f'{field} is missing in the JSON body')
                return jsonify({'error': f'{field} is missing in the JSON body'}), 400

        stations_ids = WeatherStation.query.with_entities(WeatherStation.id).order_by(WeatherStation.id.desc()).all()
        stations_id_list = [idx[0] for idx in
                            stations_ids]  # idx - id, но с x для избежания конфликта с функцией питона

        if weather_data['station_id'] not in stations_id_list:
            log.debug(f'There is no stations with that ID on server')
            return jsonify({'error': 'There is no stations with that ID on server'}), 400

        log.debug(f'Json from device: {weather_data}')

        # Проверки значений на лимиты
        try:
            if not (weather_data['temperature'] == "NONE" or WeatherAPICfg.MIN_TEMPERATURE <= float(
                    weather_data['temperature']) <= WeatherAPICfg.MAX_TEMPERATURE):
                return jsonify({
                    'error': f'Invalid temperature value. It should be "NONE" or within the range [{WeatherAPICfg.MIN_TEMPERATURE}, {WeatherAPICfg.MAX_TEMPERATURE}]'}), 400

            if not (weather_data['humidity'] == "NONE" or 0 <= float(weather_data['humidity']) <= 100):
                return jsonify(
                    {'error': 'Invalid humidity value. It should be "NONE" or within the range [0, 100]'}), 400

            if not (weather_data['pressure'] == "NONE" or WeatherAPICfg.MIN_PRESSURE <= float(
                    weather_data['pressure']) <= WeatherAPICfg.MAX_PRESSURE):
                return jsonify({
                    'error': f'Invalid pressure value. It should be "NONE" or within the range [{WeatherAPICfg.MIN_PRESSURE}, {WeatherAPICfg.MAX_PRESSURE}]'}), 400

            if not (weather_data['wind_speed'] == "NONE" or 0 <= float(
                    weather_data['wind_speed']) <= WeatherAPICfg.MAX_WIND_SPEED):
                return jsonify({
                    'error': f'Invalid wind speed value. It should be "NONE" or within the range [0, {WeatherAPICfg.MAX_WIND_SPEED}]'}), 400

            if not (weather_data['wind_direction'] == "NONE" or 0 <= float(weather_data['wind_direction']) <= 360):
                return jsonify(
                    {'error': 'Invalid wind direction value. It should be "NONE" or within the range [0, 360]'}), 400

            if not (weather_data['rain_intensity'] == "NONE" or 0 <= float(
                    weather_data['rain_intensity']) <= WeatherAPICfg.MAX_RAIN_INTENSITY):
                return jsonify({
                    'error': f'Invalid rain intensity value. It should be "NONE" or within the range [0, {WeatherAPICfg.MAX_RAIN_INTENSITY}]'}), 400

            if 'custom_data' in weather_data:
                if len(weather_data['custom_data']) > WeatherAPICfg.CUSTOM_DATA_MAX_LENGTH:
                    return jsonify({'error': 'Custom data is too long'}), 400

        except ValueError:
            log.debug(f'Invalid value in the JSON body: some element contains incorrect symbols', exc_info=LoggingConfig.ADVANCED_ERROR_OUTPUT)
            return jsonify({'error': f'Invalid value in the JSON body: some element contains incorrect symbols'}), 400

        # Добавление данных в базу данных
        result = add_weather_data_to_db(weather_data)

        return result

    except Exception as e:
        log.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        return jsonify({'error': 'Unexpected server-side error'}), 500


def add_weather_data_to_db(weather_data: dict):
    """
    Adds weather data to the database.

    Args:
        weather_data (dict): Weather data in dictionary format.
    """
    new_weather_data = WeatherData(
        station_id=weather_data['station_id'],
        timestamp=get_moscow_time(),
        temperature=float(weather_data['temperature']) if weather_data['temperature'] != "NONE" else None,
        humidity=float(weather_data['humidity']) if weather_data['humidity'] != "NONE" else None,
        pressure=float(weather_data['pressure']) if weather_data['pressure'] != "NONE" else None,
        wind_speed=float(weather_data['wind_speed']) if weather_data['wind_speed'] != "NONE" else None,
        wind_direction=float(weather_data['wind_direction']) if weather_data['wind_direction'] != "NONE" else None,
        rain_intensity=float(weather_data['rain_intensity']) if weather_data['rain_intensity'] != "NONE" else None,
        custom_data=weather_data['custom_data'] if 'custom_data' in weather_data else None
    )

    try:
        db.session.add(new_weather_data)
        db.session.commit()
        log.debug(f'Weather data added successfully')
        return jsonify({'success': 'Weather data added successfully'}), 200
    except Exception:
        db.session.rollback()
        log.error(f"Error occured while adding weather data to the database", exc_info=LoggingConfig.ADVANCED_ERROR_OUTPUT)
        return jsonify({'error': f'Server error occured!'}), 500


def make_weather_json(raw_data: Union[Any, List[Any]], notList: bool = False) -> List[dict]:
    """
    Converts raw weather data into a JSON-compatible format.

    Args:
        raw_data (Union[Any, List[Any]]): Raw weather data, can be a single entry or a list of entries.
        notList (bool, optional): Indicates if the raw_data is not a list. Defaults to False.

    Returns:
        List[dict]: JSON-compatible weather data.

    Note:
        If notList is True, raw_data is treated as a single entry; otherwise, it is treated as a list of entries.
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
