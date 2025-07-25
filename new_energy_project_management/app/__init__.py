from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'main.login' # 指定登录页面的端点
login.login_message = '请登录以访问此页面。'

def create_app(config_class=Config):
    """应用工厂函数。"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 将扩展实例与应用实例绑定
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # 注册蓝图
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes import main as main_bp
    app.register_blueprint(main_bp)

    return app

# 在底部导入，以避免循环依赖
from app import models