
# 在 app/teacher/routes.py 或创建这个文件
from app.main.forms import NoteForm
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, StudentNote
from app import db
from datetime import datetime
from functools import wraps

teacher_bp = Blueprint('teacher', __name__)

# 装饰器：确保只有教师可以访问
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('只有教师可以访问此页面')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    return render_template('teacher/dashboard.html')

@teacher_bp.route('/students')
@login_required
@teacher_required
#改成只传
def student_list():
    # 获取所有学生（角色为student的用户）
    students_query = User.query.filter_by(role='student').all()
    students_data = []
    
    for student in students_query:
        students_data.append({
            'id': student.id,
            'name': student.full_name or student.username,
            'email': student.email
        })
    
    return render_template('teacher/student_list.html', students=students_data)



@teacher_bp.route('/student/<int:student_id>')
@login_required
@teacher_required
def student_profile(student_id):
    # 获取学生信息
    student = User.query.get_or_404(student_id)
    
    # 确保是学生角色
    if student.role != 'student':
        flash('只能查看学生档案')
        return redirect(url_for('teacher.student_list'))

    # 提取学生数据为字典
    student_data = {
        'id': student.id,
        'name': student.full_name or student.username,
        'email': student.email,
        'phone': student.phone
    }    

    # 获取教师对该学生的所有笔记
    notes = StudentNote.query.filter_by(
        teacher_id=current_user.id,
        student_id=student_id
    ).order_by(StudentNote.created_at.desc()).all()
    
    return render_template('teacher/student_profile.html', student=student, notes=notes)

@teacher_bp.route('/student/<int:student_id>/add_note', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_note(student_id): 
    # 获取学生信息
    student = User.query.get_or_404(student_id)
    
# 提取所需字段，新增
    student_id = student.id
    student_name = student.full_name or student.username
    student_email = student.email
    student_phone = student.phone    
    # 确保是学生角色
    if student.role != 'student':
        flash('只能为学生添加笔记')
        return redirect(url_for('teacher.student_list'))
    
    # 创建表单
    form = NoteForm()
    
    if form.validate_on_submit():
        # 创建新笔记
        note = StudentNote(
            student_id=student_id,
            teacher_id=current_user.id,
            content=form.content.data,
            note_type='timeline'  # 添加笔记类型，可以根据实际需求修改
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash('笔记已添加成功')
        return redirect(url_for('teacher.student_profile', student_id=student_id))
    
    return render_template('teacher/edit_note.html', 
                          form=form,
                          student_id=student_id,
                          student_name=student_name,
                          student_email=student_email,
                          student_phone=student_phone,
                          student=student)    

        
    # if request.method == 'POST':
    #     content = request.form.get('content')
        
    #     if not content:
    #         flash('笔记内容不能为空')
    #         return redirect(url_for('teacher.add_note', student_id=student_id))
        
    #     # 创建新笔记
    #     note = StudentNote(
    #         student_id=student_id,
    #         teacher_id=current_user.id,
    #         content=content
    #     )
        
    #     db.session.add(note)
    #     db.session.commit()
        
    #     flash('笔记已添加成功')
    #     return redirect(url_for('teacher.student_profile', student_id=student_id))
    
    # return render_template('teacher/edit_note.html', student=student)





@teacher_bp.route('/student/note/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required



def edit_note(note_id):
    # 获取笔记
    note = StudentNote.query.get_or_404(note_id)
    
    # 确保当前教师是笔记的作者
    if note.teacher_id != current_user.id:
        flash('你只能编辑自己的笔记')
        return redirect(url_for('teacher.student_profile', student_id=note.student_id))
    # 查询学生并只提取所需字段
    student = User.query.get(note.student_id)
    student_id = student.id
    student_name = student.full_name or student.username
    student_email = student.email
    student_phone = student.phone
    
    # 创建表单并设置默认值
    form = NoteForm()
    if not form.content.data and note.content:
        form.content.data = note.content
    
    if form.validate_on_submit():
        # 更新笔记
        note.content = form.content.data
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('笔记已更新成功')
        return redirect(url_for('teacher.student_profile', student_id=note.student_id))
    
    # 传递表单和学生信息
    return render_template('teacher/edit_note.html', 
                          form=form,
                          note=note, 
                          student_id=student_id,
                          student_name=student_name,
                          student_email=student_email,
                          student_phone=student_phone)    

    
    # if request.method == 'POST':
    #     content = request.form.get('content')
        
    #     if not content:
    #         flash('笔记内容不能为空')
    #         return redirect(url_for('teacher.edit_note', note_id=note_id))
        
    #     # 更新笔记
    #     note.content = content
    #     note.updated_at = datetime.utcnow()
        
    #     db.session.commit()
        
    #     flash('笔记已更新成功')
    #     return redirect(url_for('teacher.student_profile', student_id=note.student_id))
    
    # return render_template('teacher/edit_note.html', note=note, student=note.student)

@teacher_bp.route('/student/note/<int:note_id>/delete')
@login_required
@teacher_required
def delete_note(note_id):
    # 获取笔记
    note = StudentNote.query.get_or_404(note_id)
    
    # 确保当前教师是笔记的作者
    if note.teacher_id != current_user.id:
        flash('你只能删除自己的笔记')
        return redirect(url_for('teacher.student_profile', student_id=note.student_id))
    
    student_id = note.student_id
    
    db.session.delete(note)
    db.session.commit()
    
    flash('笔记已删除')
    return redirect(url_for('teacher.student_profile', student_id=student_id))

# 在 app/__init__.py 中注册蓝图
# from app.teacher.routes import teacher_bp
# app.register_blueprint(teacher_bp, url_prefix='/teacher')

@teacher_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@teacher_required
def teacher_profile():
    """教师个人资料页面"""
    if request.method == 'POST':
        current_user.full_name = request.form['full_name']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        db.session.commit()
        flash('个人信息更新成功！')
        return redirect(url_for('teacher.teacher_profile'))
        
    return render_template('teacher/profile.html')