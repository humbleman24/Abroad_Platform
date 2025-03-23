# app/student/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.models import User, Appointment, db
from app.student.forms import AppointmentForm

student_bp = Blueprint('student', __name__)

@student_bp.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if not current_user.is_student():
        flash('只有学生可以发起预约请求。')
        return redirect(url_for('main.profile'))
    
    form = AppointmentForm()
    form.teacher.choices = [(t.id, t.username) for t in User.query.filter_by(role='teacher').all()]
    
    if form.validate_on_submit():
        new_appointment = Appointment(
            student_id=current_user.id,
            teacher_id=form.teacher.data,
            time_slot=form.time_slot.data
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('预约请求已提交！')
        return redirect(url_for('main.profile'))
    
    appointments = Appointment.query.filter_by(student_id=current_user.id).all()
    return render_template('student/appointment.html', form=form, appointments=appointments)