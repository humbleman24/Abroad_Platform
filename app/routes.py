from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Document, Appointment
from app.forms import UploadForm, AppointmentForm, RegisterForm, LoginForm
from config import Config
import os

bp = Blueprint('routes', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    back_url = request.referrer or url_for('routes.index')
    return render_template('index.html', back_url=back_url)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    back_url = request.referrer or url_for('routes.index')
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash('注册成功！请登录。')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form, back_url=back_url)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = LoginForm()
    back_url = request.referrer or url_for('routes.index')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('routes.home'))
        else:
            flash('用户名或密码错误。')
    return render_template('login.html', form=form, back_url=back_url)

@bp.route('/home')
@login_required
def home():
    back_url = request.referrer or url_for('routes.index')
    return render_template('home.html', user=current_user, back_url=back_url)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    back_url = request.referrer or url_for('routes.home')
    print("进入 /profile 路由，方法:", request.method)
    
    if request.method == 'POST' and 'full_name' in request.form:
        current_user.full_name = request.form['full_name']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        current_user.major = request.form['major']  # 新增专业
        current_user.grade = request.form['grade']  # 新增年级
        db.session.commit()
        flash('个人信息更新成功！')
        return redirect(url_for('routes.profile'))
    
    return render_template('profile.html', user=current_user, back_url=back_url)


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_student():
        flash('只有学生可以上传文件。')
        return redirect(url_for('routes.profile'))
    
    form = UploadForm()
    back_url = request.referrer or url_for('routes.profile')
    
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                flash('文件已存在，请更换文件名称后再上传。')
                return redirect(url_for('routes.upload'))
            file.save(file_path)
            new_doc = Document(filename=filename, category=form.category.data, user_id=current_user.id)
            db.session.add(new_doc)
            db.session.commit()
            flash('文件上传成功！')
            return redirect(url_for('routes.upload'))
        else:
            flash('不支持的文件类型。仅支持 PDF、DOC、DOCX。')
            return redirect(url_for('routes.upload'))
    
    return render_template('upload.html', form=form, back_url=back_url)

@bp.route('/documents', methods=['GET'])
@login_required
def documents():
    if not current_user.is_student():
        flash('只有学生可以查看已上传文件。')
        return redirect(url_for('routes.profile'))
    
    back_url = request.referrer or url_for('routes.profile')
    category = request.args.get('category', '')
    query = Document.query.filter_by(user_id=current_user.id)
    
    if category:
        query = query.filter_by(category=category)
    
    documents = query.all()
    return render_template('documents.html', documents=documents, category=category, back_url=back_url)

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
    return redirect(url_for('routes.documents'))

@bp.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if not current_user.is_student():
        flash('只有学生可以发起预约请求。')
        return redirect(url_for('routes.profile'))
    
    form = AppointmentForm()
    form.teacher.choices = [(t.id, t.username) for t in User.query.filter_by(role='teacher').all()]
    back_url = request.referrer or url_for('routes.home')
    
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
    return render_template('appointment.html', form=form, appointments=appointments, back_url=back_url)

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

@bp.route('/university_info')
def university_info():
    universities = [
        {
            'name': '麻省理工学院（MIT）',
            'location': '美国',
            'ranking': 1,
            'description': '麻省理工学院以其在科学、工程和技术领域的卓越研究和教育闻名全球。',
        },
        {
            'name': '帝国理工学院（Imperial College London）',
            'location': '英国',
            'ranking': 2,
            'description': '帝国理工学院是世界领先的科学、工程、医学和商业研究型大学。',
        },
        {
            'name': '牛津大学（University of Oxford）',
            'location': '英国',
            'ranking': 3,
            'description': '牛津大学是英语世界中最古老的大学，以其悠久的历史和学术成就著称。',
        },
        {
            'name': '哈佛大学（Harvard University）',
            'location': '美国',
            'ranking': 4,
            'description': '哈佛大学是世界顶尖的私立研究型大学，以其卓越的学术和研究闻名。',
        },
        {
            'name': '剑桥大学（University of Cambridge）',
            'location': '英国',
            'ranking': 5,
            'description': '剑桥大学是世界领先的研究型大学，以其卓越的教育和研究闻名。',
        },
        {
            'name': '斯坦福大学（Stanford University）',
            'location': '美国',
            'ranking': 6,
            'description': '斯坦福大学以其创新精神和在技术领域的卓越研究而闻名。',
        },
        {
            'name': '苏黎世联邦理工学院（ETH Zurich）',
            'location': '瑞士',
            'ranking': 7,
            'description': '苏黎世联邦理工学院是欧洲顶尖的科学和技术大学，以其高质量的研究和教育闻名。',
        },
        {
            'name': '新加坡国立大学（NUS）',
            'location': '新加坡',
            'ranking': 8,
            'description': '新加坡国立大学是亚洲领先的大学，以其多学科研究和全球影响力著称。',
        },
        {
            'name': '伦敦大学学院（UCL）',
            'location': '英国',
            'ranking': 9,
            'description': '伦敦大学学院是世界领先的多学科大学，以其创新研究和教学闻名。',
        },
        {
            'name': '加州理工学院（Caltech）',
            'location': '美国',
            'ranking': 10,
            'description': '加州理工学院以其在科学和工程领域的尖端研究和小规模教学而闻名。',
        },
    ]
    return render_template('university_info.html', universities=universities)

@bp.route('/seminars')
def seminars():
    return render_template('seminars.html')

@bp.route('/interactive_map')
def interactive_map():
    return render_template('interactive_map.html')