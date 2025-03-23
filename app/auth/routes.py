# app/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.models import User, db
from app.auth.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data
#         role = form.role.data
#         full_name = form.full_name.data
#         email = form.email.data
#         phone = form.phone.data
        
#         if User.query.filter_by(username=username).first():
#             flash('用户名已存在。')
#             return redirect(url_for('auth.register'))
        
#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
#         new_user = User(username=username, password=hashed_password, role=role, full_name=full_name, email=email, phone=phone)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('注册成功！请登录。')
#         return redirect(url_for('auth.login'))
    
#     return render_template('auth/register.html', form=form)
from flask import render_template, flash, redirect, url_for, request
from app import db
from app.auth import auth_bp
from app.auth.forms import RegistrationForm
from app.models.models import User

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(
#             username=form.username.data,
#             role=form.role.data,
#             full_name=form.full_name.data,
#             email=form.email.data,
#             phone=form.phone.data
#         )
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('注册成功！请登录')
#         return redirect(url_for('auth.login'))
#     return render_template('auth/register.html', form=form)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from flask import current_app

    form = RegistrationForm()
    #新加的
    if request.method == 'POST':
        current_app.logger.debug(f"表单数据: {request.form}")
        current_app.logger.debug(f"表单验证结果: {form.validate()}")
        current_app.logger.debug(f"表单错误: {form.errors}")
    
    current_app.logger.debug("==== 进入注册视图函数 ====")
    current_app.logger.debug(f"请求方法: {request.method}")
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        current_app.logger.debug(f"接收到的表单数据: {request.form}")
        valid = form.validate_on_submit()
        current_app.logger.debug(f"表单验证结果: {valid}")
        
        if form.errors:
            current_app.logger.debug(f"表单验证错误: {form.errors}")
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                role=form.role.data,
                full_name=form.full_name.data,
                email=form.email.data,
                phone=form.phone.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            current_app.logger.debug(f"用户创建成功: {user.username}")
            flash('注册成功！请登录')
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f"创建用户时出错: {str(e)}")
            db.session.rollback()
            flash('注册过程中出错，请重试')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    # 打印一些调试信息
    print(f"请求方法: {request.method}")
    print(f"表单验证状态: {form.validate_on_submit()}")

    if form.validate_on_submit():
        # 输出用户提交的数据
        print(f"用户名: {form.username.data}")


        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
         #使用用户模型中定义的check_password方法
        if user and user.check_password(password):
        # if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.profile'))
        else:
            flash('无效的用户名或密码。')
            return redirect(url_for('auth.login'))
    # 这是GET请求或者表单验证失败的情况
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))