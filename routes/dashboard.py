from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from db.db_users import WeatherStation, User

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        return redirect(url_for('auth.home'))

    stations = db.session.query(WeatherStation).all()
    users = db.session.query(User).all()

    return render_template('dashboard_admin.html', stations=stations, users=users)


@dashboard_bp.route('/dashboard/user')
@login_required
def user():
    if current_user.role != 'user':
        return redirect(url_for('auth.home'))

    return render_template('dashboard_user.html')
