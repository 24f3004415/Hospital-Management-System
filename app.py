from flask import Flask, redirect, url_for,render_template,request,session,flash
from models import db, User, Doctor, Patient, Department, Appointment, DoctorAvailability, PatientHistory
from datetime import datetime, date

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

            if user.user_role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.user_role == 'doctor':
                return redirect(url_for('doctor_dashboard', username=user.user_name))
            elif user.user_role == 'patient':
                return redirect(url_for('patient_dashboard', username=user.user_name))
            elif user.user_role == 'blacklisted':
                flash('Your account has been blacklisted. Please contact the administrator.')
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
    
    doctor = Doctor.query.get(doctor_id)
    
    if doctor:
       
        user_id = doctor.id

        db.session.delete(doctor)
        db.session.commit() 
        
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
        
        flash("Doctor deleted successfully!")
    
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
    # Find the patient
    patient = Patient.query.get(patient_id)
    
    if not patient:
        flash("Patient not found!")
        return redirect(url_for('admin_dashboard'))
    
    # Get user id before deleting patient
    user_id = patient.id
    
    # Delete patient first
    db.session.delete(patient)
    db.session.commit()
    
    # Delete user
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    
    flash("Patient deleted successfully!")
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
@app.route('/update_appointment_status/<int:appointment_id>/<string:action>/<username>', methods=['POST'])
def update_appointment_status(appointment_id, action, username):
    appointment = Appointment.query.get_or_404(appointment_id)

    # Update appointment status
    if action == 'complete':
        appointment.status = 'completed'
        flash(f"Appointment #{appointment.id} marked as completed.", "success")
    elif action == 'cancel':
        appointment.status = 'cancelled'
        flash(f"Appointment #{appointment.id} cancelled.", "info")
    else:
        flash("Invalid action.", "warning")
        return redirect(url_for('doctor_dashboard', username=username))

    db.session.commit()
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

        new_record = PatientHistory(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_id=appointment.id,
            diagnosis=diagnosis,
            treatment=treatment,
            prescription=prescription
        )
        db.session.add(new_record)
        db.session.commit()

        flash('Patient history successfully recorded.', 'success')
        return redirect(url_for('completed_appointments', username=username))

    return render_template('DoctorUI/add_history.html',
                           username=username,
                           appointment=appointment,
                           patient=patient)


@app.route('/patient_dashboard/<username>')
def patient_dashboard(username):
    return render_template('PatientUI/patient_dashboard.html', username=username)




if __name__ == '__main__':
    app.run(debug=True)