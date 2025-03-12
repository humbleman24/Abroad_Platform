# run.py
from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()  # 确保在 app 上下文中创建表

if __name__ == "__main__":
    app.run(debug=True)
