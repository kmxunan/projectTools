from app import create_app, db
from app.models import User

app = create_app()

# 创建管理员用户
def create_admin_user():
    with app.app_context():
        # 检查是否已存在admin用户
        if User.query.filter_by(username='admin').first() is None:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='管理员'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('管理员用户创建成功')
        else:
            print('admin用户已存在')

if __name__ == '__main__':
    create_admin_user()