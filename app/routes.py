# app/routes.py
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
# from app.models import User, Document, Appointment, db
# from app.forms import UploadForm, AppointmentForm
# from config import Config
# import os

# app/routes.py
# from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, send_file
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
# from app.models.models import User, Document, Appointment, StudentNote, db
# from app.forms import UploadForm, AppointmentForm
# from config import Config
# import os

# #新加的
# from app.models.models import User, Document, Appointment, StudentNote,db


# from flask import current_app, send_file, flash, redirect, url_for
# from flask_login import current_user, login_required
# from app.models import Document  # 确保正确导入你的Document模型
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models.models import User, Document, Appointment, StudentNote, db
from app.forms import UploadForm, AppointmentForm
from config import Config
import os


bp = Blueprint('routes', __name__, template_folder='templates/main')

# bp = Blueprint('routes', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在。')
            return redirect(url_for('routes.register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role=role, full_name=full_name, email=email, phone=phone)
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功！请登录。')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('routes.profile'))
        else:
            flash('无效的用户名或密码。')
    
    return render_template('login.html')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    upload_form = UploadForm()
    
    if current_user.is_student() and upload_form.validate_on_submit():
        file = upload_form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(file_path)
            new_doc = Document(filename=filename, category=upload_form.category.data, user_id=current_user.id)
            db.session.add(new_doc)
            db.session.commit()
            flash('文件上传成功！')
            return redirect(url_for('routes.profile'))
        else:
            flash('不支持的文件类型。仅支持 PDF、DOC、DOCX。')
    
    if request.method == 'POST' and 'full_name' in request.form:
        current_user.full_name = request.form['full_name']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        db.session.commit()
        flash('个人信息更新成功！')
    
    documents = Document.query.filter_by(user_id=current_user.id).all() if current_user.is_student() else []
    return render_template('profile.html', user=current_user, upload_form=upload_form, documents=documents)

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

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))


#查看自己上传的文件
@bp.route('/view_document/<int:document_id>')
@login_required
def view_document(document_id):
    # 获取文档信息
    document = Document.query.get_or_404(document_id)
    
    # 检查当前用户是否有权限查看此文档
    if document.user_id != current_user.id and not current_user.is_admin():
        flash('您没有权限查看此文档')
        return redirect(url_for('routes.profile'))
    
    # 获取文件存储路径
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
    
    # 返回文件
    return send_file(file_path, as_attachment=False)


#删除已上传文件
@bp.route('/delete_document/<int:document_id>')
# @bp.route('/delete_document/<int:document_id>', methods=['POST']) 
@login_required
def delete_document(document_id):
    # 获取文档信息
    document = Document.query.get_or_404(document_id)
    
    # 检查当前用户是否有权限删除此文档
    if document.user_id != current_user.id and not current_user.is_admin():
        flash('您没有权限删除此文档')
        return redirect(url_for('routes.profile'))
    
    try:
        # 获取文件存储路径
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
        
        # 如果文件存在，则从文件系统中删除
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 从数据库中删除记录
        db.session.delete(document)
        db.session.commit()
        
        flash('文件已成功删除')
    except Exception as e:
        db.session.rollback()
        flash(f'删除文件时出错: {str(e)}')
    
    return redirect(url_for('routes.profile'))