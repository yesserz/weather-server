from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_user, current_user, logout_user
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from db.db_users import User
from logger import myLog


log = myLog(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/")
def home():
    return render_template('home.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            return redirect(url_for('auth.login'))

        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        log.info(f'User {form.username.data} created successfully')
        flash('Your account has been created!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            log.info(f'User {form.username.data} is logged in successfully')
            flash('Login successful!', 'success')
            return redirect(url_for('auth.home'))
        else:
            log.info(f'User {form.username.data} is not logged in successfully')
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

