# app/models.py

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin
# from app import db
from datetime import datetime 
# app/models/models.py
from extensions import db
# 其他导入...

# 定义模型...

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' 或 'teacher'
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    
    # 关系：一个用户可以有多个文档和预约
    documents = db.relationship('Document', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='student', foreign_keys='Appointment.student_id', lazy=True)
    received_appointments = db.relationship('Appointment', backref='teacher', foreign_keys='Appointment.teacher_id', lazy=True)
    
    def is_student(self):
        return self.role == 'student'
    
    def is_teacher(self):
        return self.role == 'teacher'

    #对象比较代码，防止递归调用
    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return hash(self.id)
    
class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'resume', 'ps'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)  # e.g., '2025-03-15 10:00'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'

# 学生笔记
class StudentNote(db.Model):
    __tablename__ = 'student_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 笔记内容
    note_type = db.Column(db.String(20), nullable=False)  # 笔记类型：'timeline', 'completed', 'todo'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系 - 使用不同的backref名称避免与现有关系冲突
    student = db.relationship('User', foreign_keys=[student_id], backref='notes_received')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='notes_created')

    # 在 User 类中添加：
def is_admin(self):
    return self.role == 'admin'  # 如果您的系统没有admin角色，可以改为 return False



def __repr__(self):
        return f'<StudentNote {self.id}: {self.teacher.username} -> {self.student.username}>'