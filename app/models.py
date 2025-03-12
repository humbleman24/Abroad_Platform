# app/models.py

from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
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
