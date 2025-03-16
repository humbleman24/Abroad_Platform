# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FileField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Email

class UploadForm(FlaskForm):
    file = FileField('上传文件', validators=[DataRequired()])
    category = SelectField('文件类别', choices=[('resume', '简历'), ('ps', '个人陈述')], validators=[DataRequired()])
    submit = SubmitField('上传')

class AppointmentForm(FlaskForm):
    teacher = SelectField('选择老师', coerce=int, validators=[DataRequired()])
    time_slot = StringField('预约时间', validators=[DataRequired()])  # 简单实现，可扩展为日期选择器
    submit = SubmitField('提交预约请求')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('身份', choices=[('student', '学生'), ('teacher', '老师')], validators=[DataRequired()])
    submit = SubmitField('注册')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')
