from app import create_app, db
from app.models import User, Project # 导入模型以便于 shell 上下文使用

# 创建 Flask 应用实例
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """为 Flask shell 提供上下文，方便调试。"""
    return {'db': db, 'User': User, 'Project': Project}

if __name__ == '__main__':
    # 仅在直接运行此脚本时启动服务器
    # 生产环境中应使用 Gunicorn 或 uWSGI 等 WSGI 服务器
    app.run(debug=True)