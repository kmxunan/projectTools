import os
from dotenv import load_dotenv

# 基于项目根目录确定基准目录
basedir = os.path.abspath(os.path.dirname(__file__))
# 加载 .env 文件中的环境变量
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """应用的基础配置类。"""
    # 从环境变量获取密钥，如果未设置则使用一个硬编码的默认值（仅限开发）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    
    # 数据库配置
    # 设置数据库路径，优先使用环境变量，否则使用项目根目录下的 app.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    # 关闭 SQLAlchemy 的事件通知系统，以节省资源
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 其他应用相关的配置可以添加在这里
    # 例如：每页显示的项目数量
    ITEMS_PER_PAGE = 10