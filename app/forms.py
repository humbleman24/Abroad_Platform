# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField('上传文件', validators=[DataRequired()])
    category = SelectField('文件类别', choices=[('resume', '简历'), ('ps', '个人陈述')], validators=[DataRequired()])
    submit = SubmitField('上传')

class AppointmentForm(FlaskForm):
    teacher = SelectField('选择老师', coerce=int, validators=[DataRequired()])
    time_slot = StringField('预约时间', validators=[DataRequired()])  # 简单实现，可扩展为日期选择器
    submit = SubmitField('提交预约请求')
