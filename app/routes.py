# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import User, Document, Appointment, db
from app.forms import UploadForm, AppointmentForm, RegisterForm, LoginForm
from config import Config
import os
import uuid

bp = Blueprint('routes', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功！请登录。')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))  # 如果已登录，跳转到首页

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('routes.home'))  # 登录成功跳转到首页
        else:
            flash('用户名或密码错误。')  # 登录失败显示错误
    return render_template('login.html', form=form)

@bp.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    upload_form = UploadForm()
    
    print("进入 /profile 路由，方法:", request.method)
    
    if request.method == 'POST':
        print("收到 POST 请求，表单数据:", request.form, "文件:", request.files)
        if current_user.is_student():
            if upload_form.validate_on_submit():
                print("表单验证通过")
                file = upload_form.file.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                    
                    print("检查文件路径:", file_path)
                    if os.path.exists(file_path):
                        flash('文件已存在，请更换文件名称后再上传。')
                        return redirect(url_for('routes.profile'))
                    
                    file.save(file_path)
                    new_doc = Document(filename=filename, category=upload_form.category.data, user_id=current_user.id)
                    db.session.add(new_doc)
                    db.session.commit()
                    flash('文件上传成功！')
                    return redirect(url_for('routes.profile'))
                else:
                    flash('不支持的文件类型。仅支持 PDF、DOC、DOCX。')
                    return redirect(url_for('routes.profile'))
            else:
                print("表单验证失败，错误:", upload_form.errors)
                flash('文件上传失败，请检查输入内容。')
                return redirect(url_for('routes.profile'))
    
    if request.method == 'POST' and 'full_name' in request.form:
        print("更新个人信息")
        current_user.full_name = request.form['full_name']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        db.session.commit()
        flash('个人信息更新成功！')
        return redirect(url_for('routes.profile'))
    
    documents = Document.query.filter_by(user_id=current_user.id).all() if current_user.is_student() else []
    return render_template('profile.html', user=current_user, upload_form=upload_form, documents=documents)

@bp.route('/delete/<filename>', methods=['GET'])
@login_required
def delete_file(filename):
    if not current_user.is_student():
        flash('只有学生可以删除自己的文件。')
        return redirect(url_for('routes.profile'))
    
    doc = Document.query.filter_by(filename=filename, user_id=current_user.id).first()
    if not doc:
        flash('文件不存在或无权限删除。')
        return redirect(url_for('routes.profile'))
    
    file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(doc)
    db.session.commit()
    
    flash('文件已成功删除！')
    return redirect(url_for('routes.profile'))

@bp.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if not current_user.is_student():
        flash('只有学生可以发起预约请求。')
        return redirect(url_for('routes.profile'))
    
    form = AppointmentForm()
    form.teacher.choices = [(t.id, t.username) for t in User.query.filter_by(role='teacher').all()]
    
    if form.validate_on_submit():
        new_appointment = Appointment(
            student_id=current_user.id,
            teacher_id=form.teacher.data,
            time_slot=form.time_slot.data
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('预约请求已提交！')
        return redirect(url_for('routes.profile'))
    
    appointments = Appointment.query.filter_by(student_id=current_user.id).all()
    return render_template('appointment.html', form=form, appointments=appointments)

@bp.route('/download/<filename>')
@login_required
def download_file(filename):
    if not current_user.is_student():
        flash('只有学生可以查看自己的文件。')
        return redirect(url_for('routes.profile'))
    
    doc = Document.query.filter_by(filename=filename, user_id=current_user.id).first()
    if not doc:
        flash('文件不存在或无权限访问。')
        return redirect(url_for('routes.profile'))
    
    return send_from_directory(Config.UPLOAD_FOLDER, filename, as_attachment=False)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))
