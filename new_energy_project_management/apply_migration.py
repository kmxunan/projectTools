#!/usr/bin/env python
"""手动应用数据库迁移脚本"""

from app import create_app, db
from flask_migrate import upgrade

# 创建应用实例
app = create_app()

with app.app_context():
    try:
        # 执行数据库升级
        upgrade()
        print("数据库迁移成功完成！")
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        # 手动执行SQL
        try:
            db.engine.execute("""
                ALTER TABLE project ADD COLUMN longitude REAL;
                ALTER TABLE project ADD COLUMN latitude REAL;
                ALTER TABLE project ADD COLUMN address VARCHAR(500);
                ALTER TABLE project ADD COLUMN province VARCHAR(50);
                ALTER TABLE project ADD COLUMN city VARCHAR(50);
                ALTER TABLE project ADD COLUMN district VARCHAR(50);
            """)
            db.session.commit()
            print("手动SQL执行成功！")
        except Exception as sql_error:
            print(f"手动SQL执行失败: {sql_error}")
            db.session.rollback()