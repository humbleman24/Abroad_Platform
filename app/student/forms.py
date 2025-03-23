# app/student/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class AppointmentForm(FlaskForm):
    teacher = SelectField('老师', coerce=int, validators=[DataRequired()])
    time_slot = StringField('时间段', validators=[DataRequired()])
    submit = SubmitField('预约')