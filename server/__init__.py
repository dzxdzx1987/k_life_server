import os
from flask import Flask, request
from sqlalchemy import select

from server.settings import config
from server.blueprints.main import main_bp
from server.blueprints.auth import auth_bp
from server.models import User
from server.extensions import db, login_manager
from server.errors import register_errors
from server.commands import register_commands


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    from server.blueprints.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    db.init_app(app)
    login_manager.init_app(app)

    # CORS：为 /api/* 添加跨域支持
    @app.after_request
    def add_cors_headers(response):
        # 仅对 /api 路径添加 CORS 头
        if request.path.startswith('/api'):
            allowed = os.getenv('CORS_ALLOWED_ORIGINS', '*')
            origin = request.headers.get('Origin')

            # 允许任意来源，或仅允许在白名单中的来源
            if allowed == '*':
                response.headers['Access-Control-Allow-Origin'] = '*'
            elif origin and origin in [o.strip() for o in allowed.split(',')]:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'

            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    @app.before_request
    def handle_preflight():
        # 处理跨域预检请求
        if request.method == 'OPTIONS' and request.path.startswith('/api'):
            allowed = os.getenv('CORS_ALLOWED_ORIGINS', '*')
            origin = request.headers.get('Origin')

            resp = app.make_response(('', 204))
            if allowed == '*':
                resp.headers['Access-Control-Allow-Origin'] = '*'
            elif origin and origin in [o.strip() for o in allowed.split(',')]:
                resp.headers['Access-Control-Allow-Origin'] = origin
                resp.headers['Access-Control-Allow-Credentials'] = 'true'

            resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return resp

    register_errors(app)
    register_commands(app)

    @app.context_processor
    def inject_user():
        user = db.session.execute(select(User)).scalar()
        return dict(user=user)

    return app
