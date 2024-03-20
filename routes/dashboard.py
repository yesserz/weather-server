from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from db.db_models import WeatherStation, User


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard.user'))

    stations = db.session.query(WeatherStation).all()
    users = db.session.query(User).all()

    return render_template('dashboard_admin.html', stations=stations, users=users)


@dashboard_bp.route('/dashboard/user', methods=['GET', 'POST'])
@login_required
def user():
    if current_user.role != 'user' and current_user.role != 'admin':
        return redirect(url_for('auth.home'))

    if request.method == 'POST':
        station_id = request.form.get('station_id')
        return jsonify(url_for('dashboard.user', station_id=station_id))
    else:
        stations = db.session.query(WeatherStation).filter_by(owner_id=current_user.id).all()
        return render_template('dashboard_user.html', stations=stations)
