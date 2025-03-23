# app/main/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.models.models import User, Document, db
from app.main.forms import UploadForm  # 注意：已修正导入路径
from config import Config
import os

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    return render_template('main/index.html')  # 注意路径更改

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    upload_form = UploadForm()
    
# 如果是教师角色，重定向到教师主页
    if current_user.role == 'teacher':
        return redirect(url_for('teacher.dashboard'))    
    



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
            return redirect(url_for('main.profile'))  # 注意URL前缀更改
        else:
            flash('不支持的文件类型。仅支持 PDF、DOC、DOCX。')
    
    if request.method == 'POST' and 'full_name' in request.form:
        current_user.full_name = request.form['full_name']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        db.session.commit()
        flash('个人信息更新成功！')
    
    documents = Document.query.filter_by(user_id=current_user.id).all() if current_user.is_student() else []
    return render_template('main/profile.html', user=current_user, upload_form=upload_form, documents=documents)  # 注意路径更改

# 查看自己上传的文件
@main_bp.route('/view_document/<int:document_id>')
@login_required
def view_document(document_id):
    # 获取文档信息
    document = Document.query.get_or_404(document_id)
    
    # 检查当前用户是否有权限查看此文档
    if document.user_id != current_user.id and not current_user.is_admin():
        flash('您没有权限查看此文档')
        return redirect(url_for('main.profile'))  # 注意URL前缀更改
    
    # 获取文件存储路径
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
    
    # 返回文件
    return send_file(file_path, as_attachment=False)

# 删除已上传文件
@main_bp.route('/delete_document/<int:document_id>')
@login_required
def delete_document(document_id):
    # 获取文档信息
    document = Document.query.get_or_404(document_id)
    
    # 检查当前用户是否有权限删除此文档
    if document.user_id != current_user.id and not current_user.is_admin():
        flash('您没有权限删除此文档')
        return redirect(url_for('main.profile'))  # 注意URL前缀更改
    
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
    
    return redirect(url_for('main.profile'))  # 注意URL前缀更改


