from flask import Flask
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
    # 注册 REST API 蓝图
    from server.blueprints.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    db.init_app(app)
    login_manager.init_app(app)

    register_errors(app)
    register_commands(app)

    @app.context_processor
    def inject_user():
        user = db.session.execute(select(User)).scalar()
        return dict(user=user)

    return app
