# app/auth/forms.py
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SelectField, SubmitField
# from wtforms.validators import DataRequired, Email, EqualTo

# class LoginForm(FlaskForm):
#     username = StringField('用户名', validators=[DataRequired()])
#     password = PasswordField('密码', validators=[DataRequired()])
#     submit = SubmitField('登录')

# class RegistrationForm(FlaskForm):
#     username = StringField('用户名', validators=[DataRequired()])
#     password = PasswordField('密码', validators=[DataRequired()])
#     confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
#     role = SelectField('角色', choices=[('student', '学生'), ('teacher', '老师')])
#     full_name = StringField('姓名')
#     email = StringField('邮箱', validators=[Email()])
#     phone = StringField('电话')
#     submit = SubmitField('注册')

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, ValidationError
from app.models.models import User

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    role = SelectField('角色', choices=[('student', '学生'), ('teacher', '教师')], validators=[DataRequired()])
    full_name = StringField('全名', validators=[Optional()])
    # email = StringField('邮箱', validators=[Optional(), Email()])
    email = StringField('邮箱')
    phone = StringField('电话', validators=[Optional()])
    submit = SubmitField('注册')
    
    # 验证用户名是否已存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已被使用')
        
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')       