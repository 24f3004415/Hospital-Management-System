from flask import Flask, redirect, url_for,render_template,request,session,flash
from models import db, User, Doctor, Patient, Department, Appointment, DoctorAvailability, PatientHistory
from datetime import datetime, date, timedelta

app = Flask(__name__)

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'supersecretkey'

# Initializing database
db.init_app(app)


@app.route('/')
def landing_page():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')

        user = User.query.filter_by(user_email=user_email).first()

        if user and user.user_password == user_password:

            session['user_id'] = user.id
            session['user_name'] = user.user_name

            if user.user_role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.user_role == 'doctor':
                return redirect(url_for('doctor_dashboard', username=user.user_name))
            elif user.user_role == 'patient':
                return redirect(url_for('patient_dashboard', username=user.user_name))
            elif user.user_role == 'blacklisted':
                flash('Your account has been blacklisted. Please contact the administrator.')

                session.pop('user_id', None)
                session.pop('user_name', None)
                return redirect(url_for('login'))
        else:
            flash('Invalid email or password. Please try again.')
            return redirect(url_for('login'))
    


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(user_email=email).first()
        
        if existing_user:
            flash('Email already registered!')
            return redirect(url_for('register'))
        
        new_user = User(
            user_name=name,
            user_email=email,
            user_password=password,
            user_role='patient'
        )
        db.session.add(new_user)
        db.session.commit()


        new_patient = Patient(
            id=new_user.id,            
            patient_name=name            
        )

        db.session.add(new_patient)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')



@app.route('/admin_dashboard')
def admin_dashboard():
    search_query = request.args.get('search', '').strip()

    if search_query:
        doctors = Doctor.query.join(User).filter(
            (User.user_name.contains(search_query)) |
            (Doctor.department_id.in_(
                [d.id for d in Department.query.filter(Department.department_name.contains(search_query))]
            ))
        ).all()

        patients = Patient.query.join(User).filter(
            User.user_name.contains(search_query)
        ).all()
    else:
        doctors = Doctor.query.all()
        patients = Patient.query.all()


    # upcoming appointments
    today = datetime.now().date()
    appointments = Appointment.query.filter(Appointment.appointment_date >= today).all()

    # all appointments
    all_appointments = Appointment.query.all()

    return render_template(
        'AdminUI/admin_dashboard.html',
        doctors=doctors,
        patients=patients,
        appointments=appointments,
        all_appointments=all_appointments
    )


@app.route('/admin/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        experience_years = request.form.get('experience_years')

        # Checking for new or existing department
        selected_department = request.form.get('department_name')
        if selected_department == '__new__':
            department_name = request.form.get('new_department')
        else:
            department_name = selected_department

        
        new_user = User(
            user_name=name,
            user_email=email,
            user_password=password,
            user_role='doctor'
        )
        db.session.add(new_user)
        db.session.commit()

        
        department = Department.query.filter_by(department_name=department_name).first()
        if not department:
            department = Department(department_name=department_name)
            db.session.add(department)
            db.session.commit()

        
        new_doctor = Doctor(
            id=new_user.id,
            department_id=department.id,
            experience_years=int(experience_years)
        )
        db.session.add(new_doctor)
        db.session.commit()

        flash("Doctor added successfully!")
        return redirect(url_for('admin_dashboard'))

    
    departments = Department.query.all()
    return render_template('AdminUI/add_doctor.html', departments=departments)


# Route to delete a doctor
@app.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    # (Optional) check admin authorization here

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        flash("Doctor not found!")
        return redirect(url_for('admin_dashboard'))

    # 1) Remove dependent rows first (histories, appointments, availability)
    PatientHistory.query.filter_by(doctor_id=doctor.id).delete()
    Appointment.query.filter_by(doctor_id=doctor.id).delete()
    DoctorAvailability.query.filter_by(doctor_id=doctor.id).delete()

    # 2) Delete doctor row
    db.session.delete(doctor)

    # 3) Delete associated user row (if User.id == Doctor.id)
    user = User.query.get(doctor.id)
    if user:
        db.session.delete(user)

    # 4) Commit once
    db.session.commit()

    flash("Doctor and related records deleted successfully!")
    return redirect(url_for('admin_dashboard'))



# Route to edit a doctor
@app.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    # Find the doctor
    doctor = Doctor.query.get(doctor_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        experience_years = request.form.get('experience_years')
        department_id = request.form.get('department_id')
        
        # Update user information
        doctor.user.user_name = name
        doctor.user.user_email = email
        
        # Update doctor information
        doctor.experience_years = int(experience_years)
        doctor.department_id = int(department_id)
        
        # Save changes
        db.session.commit()
        flash("Doctor updated successfully!")
        return redirect(url_for('admin_dashboard'))
    
    # GET request - show edit form
    departments = Department.query.all()
    return render_template('AdminUI/edit_doctor.html', doctor=doctor, departments=departments)


# Route to blacklist a doctor
@app.route('/admin/blacklist_doctor/<int:doctor_id>', methods=['POST'])
def blacklist_doctor(doctor_id):
    # Find the doctor
    doctor = Doctor.query.get(doctor_id)
    
    if doctor:
        # Change the user's role to 'blacklisted'
        doctor.user.user_role = 'blacklisted'
        
        # Save changes
        db.session.commit()
        flash("Doctor blacklisted successfully!")
    else:
        flash("Doctor not found!")
    
    return redirect(url_for('admin_dashboard'))


# Route to edit a patient
@app.route('/admin/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    # Find the patient
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash("Patient not found!")
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Update user information
        patient.user.user_name = name
        patient.user.user_email = email
        
        # Save changes
        db.session.commit()
        flash("Patient updated successfully!")
        return redirect(url_for('admin_dashboard'))
    
    # GET request - show edit form
    return render_template('AdminUI/edit_patient.html', patient=patient)


# Route to delete a patient
@app.route('/admin/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    # (Optional) ensure current user is admin here

    patient = Patient.query.get(patient_id)
    if not patient:
        flash("Patient not found!")
        return redirect(url_for('admin_dashboard'))

    # 1) Remove dependent rows first
    PatientHistory.query.filter_by(patient_id=patient.id).delete()
    Appointment.query.filter_by(patient_id=patient.id).delete()

    # 2) Delete patient row
    db.session.delete(patient)

    # 3) Delete corresponding user record (if applicable)
    user = User.query.get(patient.id)
    if user:
        db.session.delete(user)

    # 4) Commit once
    db.session.commit()

    flash("Patient and related records deleted successfully!")
    return redirect(url_for('admin_dashboard'))



# Route to blacklist a patient
@app.route('/admin/blacklist_patient/<int:patient_id>', methods=['POST'])
def blacklist_patient(patient_id):
    # Find the patient
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash("Patient not found!")
        return redirect(url_for('admin_dashboard'))
    
    # Change the user's role to 'blacklisted'
    patient.user.user_role = 'blacklisted'
    
    # Save changes
    db.session.commit()
    flash("Patient blacklisted successfully!")
    
    return redirect(url_for('admin_dashboard'))


@app.route('/doctor_dashboard/<username>')
def doctor_dashboard(username):
    # Fetch doctor details based on username
    user = User.query.filter_by(user_name=username, user_role='doctor').first()
    if not user:
        flash("Doctor not found.", "danger")
        return redirect(url_for('login'))

    doctor = Doctor.query.filter_by(id=user.id).first()
    if not doctor:
        flash("Doctor not found", "danger")
        return redirect(url_for('login'))

    # Fetch upcoming appointments (today and future)
    today = date.today()
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= today,
        Appointment.status == 'booked'
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()

    # Assigned patients
    patient_ids = {appt.patient_id for appt in doctor.appointments}
    assigned_patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []

    return render_template('DoctorUI/doctor_dashboard.html',
                           username=username,
                           doctor=doctor,
                           upcoming=upcoming,
                           assigned_patients=assigned_patients)


#route to mark appointment as completed or cancelled
@app.route('/update_appointment_status/<int:appointment_id>/<action>/<string:username>', methods=['POST'])
def update_appointment_status(appointment_id, action, username):
    # validate doctor user
    user = User.query.filter_by(user_name=username, user_role='doctor').first()
    if not user:
        flash("Doctor not found.", "danger")
        return redirect(url_for('login'))

    doctor = Doctor.query.filter_by(id=user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for('login'))

    appt = Appointment.query.get_or_404(appointment_id)
    # ensure this doctor owns the appointment
    if appt.doctor_id != doctor.id:
        flash("Not authorized to update this appointment.", "danger")
        return redirect(url_for('doctor_dashboard', username=username))

    if action == 'complete':
        appt.status = 'completed'
    elif action in ('cancel', 'cancelled'):
        appt.status = 'cancelled'
    else:
        flash("Unknown action.", "warning")
        return redirect(url_for('doctor_dashboard', username=username))

    db.session.commit()
    flash(f"Appointment {action}d.", "success")
    return redirect(url_for('doctor_dashboard', username=username))


#route to view completed appointments
@app.route('/doctor/<string:username>/completed_appointments')
def completed_appointments(username):
    user = User.query.filter_by(user_name=username, user_role='doctor').first()
    if not user:
        flash("Doctor not found.", "danger")
        return redirect(url_for('login'))

    doctor = Doctor.query.filter_by(id=user.id).first()
    completed = Appointment.query.filter_by(doctor_id=doctor.id, status='completed').all()

    return render_template('DoctorUI/completed_appointments.html', username=username, doctor=doctor, completed=completed)

#route to add patient history after appointment completion
@app.route('/doctor/<string:username>/add_history/<int:appointment_id>', methods=['GET', 'POST'])
def add_history(username, appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    user = User.query.filter_by(user_name=username, user_role='doctor').first()
    if not user:
        flash("Doctor not found.", "danger")
        return redirect(url_for('login'))

    doctor = Doctor.query.filter_by(id=user.id).first()
    patient = appointment.patient

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        prescription = request.form.get('prescription')
        test_done = request.form.get('test_done')
        visit_type = request.form.get('visit_type')

        new_record = PatientHistory(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_id=appointment.id,
            diagnosis=diagnosis,
            treatment=treatment,
            prescription=prescription,
            test_type=test_done,
            visit_type=visit_type
        )
        db.session.add(new_record)
        db.session.commit()

        flash('Patient history successfully recorded.', 'success')
        return redirect(url_for('doctor_dashboard', username=username))

    return render_template('DoctorUI/add_history.html',
                           username=username,
                           appointment=appointment,
                           patient=patient)

#route to view patient history
@app.route('/<string:role>/<string:username>/patient/<int:patient_id>/history')
def view_patient_history(role, username, patient_id):
    """
    Displays complete medical history of a selected patient for any role:
    Admin / Doctor / Patient
    """
    # Verify valid user
    user = User.query.filter_by(user_name=username, user_role=role).first()
    if not user:
        flash(f"{role.capitalize()} not found.", "danger")
        return redirect(url_for('login'))

    # Fetch patient
    patient = Patient.query.get_or_404(patient_id)

    # Fetch all medical history records for this patient
    history_records = (
        PatientHistory.query
        .filter_by(patient_id=patient.id)
        .order_by(PatientHistory.created_at.desc())
        .all()
    )

    # Determine redirect URL based on role
    if role == 'doctor':
        back_url = url_for('doctor_dashboard', username=username)
    elif role == 'admin':
        back_url = url_for('admin_dashboard')
    elif role == 'patient':
        back_url = url_for('patient_dashboard', username=username)
    else:
        back_url = url_for('login')

    return render_template(
        'DoctorUI/view_patient_history.html',
        role=role,
        username=username,
        patient=patient,
        history_records=history_records,
        back_url=back_url
    )


#route to manage doctor availability
@app.route('/doctor/<string:username>/availability', methods=['GET', 'POST'])
def manage_availability(username):
    """Show and update availability for next 7 days."""
    user = User.query.filter_by(user_name=username, user_role='doctor').first()
    if not user:
        flash("Doctor not found.", "danger")
        return redirect(url_for('login'))

    doctor = Doctor.query.filter_by(id=user.id).first()

    # Generate next 7 days list (including today)
    today = date.today()
    next_week = [today + timedelta(days=i) for i in range(7)]

    # Handle form submission
    if request.method == 'POST':
        for d in next_week:
            start_str = request.form.get(f"start_{d}")
            end_str = request.form.get(f"end_{d}")
            available = request.form.get(f"avail_{d}") == 'on'

            # Only save if both times are provided
            if start_str and end_str:
                start_time = datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M").time()

                slot = DoctorAvailability.query.filter_by(doctor_id=doctor.id, date=d).first()
                if not slot:
                    slot = DoctorAvailability(
                        doctor_id=doctor.id,
                        date=d,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=available
                    )
                    db.session.add(slot)
                else:
                    slot.start_time = start_time
                    slot.end_time = end_time
                    slot.is_available = available

        db.session.commit()
        flash("Availability updated successfully!", "success")
        return redirect(url_for('manage_availability', username=username))

    # Fetch existing availability records for display
    availability = {
        slot.date: slot for slot in DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
    }

    return render_template(
        'DoctorUI/manage_availability.html',
        username=username,
        doctor=doctor,
        next_week=next_week,
        availability=availability
    )


# Patient dashboard
@app.route('/patient_dashboard/<string:username>')
def patient_dashboard(username):
    # Getting logged-in patient user
    user = User.query.filter_by(user_name=username, user_role='patient').first()

    patient = Patient.query.filter_by(id=user.id).first()

    # Loading all departments
    departments = Department.query.order_by(Department.department_name).all()

    # Simple search: ?q=name or ?dept=dept_id
    q = request.args.get('q', '').strip()
    dept_id = request.args.get('dept', type=int)
    doctors_query = Doctor.query.join(User, Doctor.id == User.id)  # join to access user_name

    if q:
        doctors_query = doctors_query.filter(User.user_name.ilike(f"%{q}%"))
    if dept_id:
        doctors_query = doctors_query.filter(Doctor.department_id == dept_id)

    found_doctors = doctors_query.all() if (q or dept_id) else []

    # Upcoming appointments (today & future)
    today = date.today()
    upcoming = (Appointment.query
        .filter_by(patient_id=patient.id)
        .filter(
            (Appointment.appointment_date >= today) &
            (Appointment.status == 'booked'))
            .order_by(Appointment.appointment_date, Appointment.appointment_time)
            .all())

    # Past appointments (before today) to show in dashboard (or status completed)
    past = (Appointment.query
        .filter_by(patient_id=patient.id)
        .filter(
            (Appointment.appointment_date < today) |
            Appointment.status.in_(['completed', 'cancelled'])
        )
        .order_by(Appointment.appointment_date.desc())
        .all())

    return render_template('PatientUI/patient_dashboard.html',
                           username=username,
                           user=user,
                           patient=patient,
                           departments=departments,
                           found_doctors=found_doctors,
                           upcoming=upcoming,
                           past=past,
                           q=q,
                           dept_id=dept_id)


# Department detail + list of doctors in that department
@app.route('/department/<int:dept_id>/<string:username>')
def department_detail(dept_id, username):

    dept = Department.query.get_or_404(dept_id)
    doctors = Doctor.query.filter_by(department_id=dept.id).all()
    return render_template('PatientUI/department_detail.html', 
                          department=dept, 
                          doctors=doctors, 
                          username=username)


# Doctor detail and  availability and booking page
@app.route('/doctor/<int:doctor_id>/view/<string:username>', methods=['GET'])
def doctor_view(doctor_id, username):
    doctor = Doctor.query.get_or_404(doctor_id)
    # next 7 days
    today = date.today()
    next_week = [today + timedelta(days=i) for i in range(7)]
    # load availability slots for this doctor
    slots = DoctorAvailability.query.filter_by(doctor_id=doctor.id).filter(
        DoctorAvailability.date.in_(next_week)
    ).order_by(DoctorAvailability.date).all()
    # map date -> list of slots
    slots_map = {}
    for s in slots:
        slots_map.setdefault(s.date, []).append(s)
    return render_template('PatientUI/doctor_view.html', 
                          username=username, 
                          doctor=doctor, 
                          next_week=next_week, 
                          slots_map=slots_map)


# Apppointment Booking route 
@app.route('/book_appointment/<string:username>/<int:doctor_id>/<string:slot_date>/<string:start_time>', methods=['POST'])
def book_appointment(username, doctor_id, slot_date, start_time):
    # Find patient
    user = User.query.filter_by(user_name=username, user_role='patient').first()
    if not user:
        flash("Patient not found.", "danger")
        return redirect(url_for('login'))

    patient = Patient.query.filter_by(id=user.id).first()
    doctor = Doctor.query.get_or_404(doctor_id)

    slot_date_obj = datetime.strptime(slot_date, "%Y-%m-%d").date()
    start_time_obj = datetime.strptime(start_time, "%H:%M").time()

    # Checking if slot exists and is available or not
    slot = DoctorAvailability.query.filter_by(
        doctor_id=doctor.id,
        date=slot_date_obj,
        start_time=start_time_obj,
        is_available=True
    ).first()

    # Checking if the same slot is already booked by anyone (for the same doctor/date/time)
    exists = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_date=slot_date_obj,
        appointment_time=start_time_obj,
        status='booked'
    ).first()

    # checking if the patient already has an appointment that day
    patient_same_day = Appointment.query.filter_by(
        patient_id=patient.id,
        appointment_date=slot_date_obj
    ).filter(Appointment.status.in_(['booked', 'completed'])).first()

    if patient_same_day:
        flash("You already have an appointment booked on this date with another doctor. Please choose a different day.", "warning")
        return redirect(url_for('doctor_view', doctor_id=doctor.id, username=username))

    # Unified unavailable slot check
    if not slot or exists:
        flash("This slot has already been booked or is unavailable. Please choose another.", "warning")
        return redirect(url_for('doctor_view', doctor_id=doctor.id, username=username))

    #creating a new appointment when everything is valid
    new_appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=slot.date,
        appointment_time=slot.start_time,
        status='booked'
    )
    db.session.add(new_appt)

    # Mark slot unavailable
    slot.is_available = False
    db.session.commit()

    flash("Appointment booked successfully.", "success")
    return redirect(url_for('patient_dashboard', username=username))



# Cancel appointment (patient)
@app.route('/patient_cancel/<string:username>/<int:appointment_id>', methods=['POST'])
def patient_cancel_appointment(username, appointment_id):
    user = User.query.filter_by(user_name=username, user_role='patient').first()
    if not user:
        flash("Patient not found.", "danger")
        return redirect(url_for('login'))
    patient = Patient.query.filter_by(id=user.id).first()

    appt = Appointment.query.get_or_404(appointment_id)
    if appt.patient_id != patient.id:
        flash("Not authorized to cancel this appointment.", "danger")
        return redirect(url_for('patient_dashboard', username=username))

    appt.status = 'cancelled'
    db.session.commit()
    flash("Appointment cancelled.", "info")
    return redirect(url_for('patient_dashboard', username=username))


# Route to edit a patient's profile
@app.route('/patient/edit_profile/<int:patient_id>', methods=['GET', 'POST'])
def edit_profile(patient_id):
    # Find the patient
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash("Patient not found!")
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Update user information
        patient.user.user_name = name
        patient.user.user_email = email
        
        # Save changes
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('patient_dashboard', username=patient.user.user_name))
    
    # GET request - show edit form
    return render_template('PatientUI/edit_profile.html', patient=patient)



if __name__ == '__main__':
    app.run(debug=True)