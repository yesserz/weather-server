from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    telegram_id = db.Column(db.String(80), unique=True, nullable=True)
    role = db.Column(db.String(10), nullable=False, default='user')
    stations = db.relationship('WeatherStation', backref='owner', lazy=True)

    def is_admin(self):
        return self.role == 'admin'


class WeatherStation(db.Model):
    __tablename__ = 'weather_stations'
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class WeatherData(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    station_id = db.Column(db.String(16), db.ForeignKey('weather_stations.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    pressure = db.Column(db.Float, nullable=True)
    wind_speed = db.Column(db.Float, nullable=True)
    wind_direction = db.Column(db.String(10), nullable=True)
    rain_intensity = db.Column(db.Float, nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)