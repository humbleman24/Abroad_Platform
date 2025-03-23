# app/__init__.py
from flask import Flask, app
from config import Config
from extensions import db, login_manager

import logging
# 设置详细的日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)





# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     #新修改的地方
#     # from extensions import db, login_manager
#     from app.auth.routes import auth_bp

#     db.init_app(app)
#     from app.main.routes import main_bp

#     login_manager.init_app(app)  # 不要放到函数外
#     login_manager.login_view = 'auth.login'
#     @app.errorhandler(Exception)

#     # 注册多个蓝图,这是修改的地方
#     from app.student.routes import student_bp
#     from app.teacher.routes import teacher_bp

#     app.register_blueprint(main_bp)
#     app.register_blueprint(auth_bp, url_prefix='/auth')
#     app.register_blueprint(student_bp, url_prefix='/student')
#     app.register_blueprint(teacher_bp, url_prefix='/teacher')

#     # 创建数据库表
#     with app.app_context():
#         db.create_all()
    
#     return app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 设置用户加载器
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.models import User
        return User.query.get(int(user_id))
    
    # 设置错误处理器 - 移到这里
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"全局异常处理: {str(e)}")
        # 返回简单字符串而非模板
        return f"发生错误: {str(e)}", 500
    
    # 注册多个蓝图
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.teacher.routes import teacher_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
    return app



# @login_manager.user_loader
def load_user(user_id):
    from app.models.models import User
    return User.query.get(int(user_id))
