# run.py
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    try:
        # 尝试执行一个简单的数据库查询
        user_count = User.query.count()
        print(f"数据库连接成功！用户表中共有 {user_count} 个用户。")
    except Exception as e:
        print(f"数据库连接失败：{e}")

    db.create_all()  # 确保在 app 上下文中创建表

if __name__ == "__main__":
    app.run(debug=True)