from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from sqlalchemy import select

from server.models import User
from server.extensions import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('auth.login'))

        user = db.session.execute(select(User).filter_by(username=username)).scalar()

        if user is not None and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('main.index'))

        flash('Invalid username or password.')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('main.index'))

# 新增：RESTful 登录与登出（JSON输入/输出）
from flask_login import current_user

@auth_bp.post('/api/auth/login')
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    remember = bool(data.get('remember', False))

    if not username or not password:
        return {"error": "Invalid input"}, 400

    user = db.session.execute(select(User).filter_by(username=username)).scalar()
    if user is not None and user.validate_password(password):
        login_user(user, remember=remember)
        return {
            "message": "Login success",
            "user": {"id": user.id, "name": user.name, "username": user.username}
        }, 200

    return {"error": "Invalid credentials"}, 401

@auth_bp.post('/api/auth/logout')
def api_logout():
    if not current_user.is_authenticated:
        return {"error": "Unauthorized"}, 401

    logout_user()
    return {"message": "Logout success"}, 200
