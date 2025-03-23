# app/main/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SelectField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    file = FileField('文件', validators=[FileRequired()])
    category = SelectField('类别', choices=[
        ('resume', '简历'), 
        ('ps', '个人陈述'),
        ('other', '其他文档')
    ])
    submit = SubmitField('上传')


#新加的，用于管理笔记表单
class NoteForm(FlaskForm):
    content = TextAreaField('笔记内容', validators=[DataRequired(message='笔记内容不能为空')])
    submit = SubmitField('保存')
    