from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Creating the database
db = SQLAlchemy()

# ------------------ Model Users (Base Class) ------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), unique=True, nullable=False)
    user_password = db.Column(db.String(200), nullable=False)
    user_role = db.Column(db.String(20), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (one-to-one with Doctor and Patient)
    doctor_profile = db.relationship('Doctor', back_populates='user', uselist=False)
    patient_profile = db.relationship('Patient', back_populates='user', uselist=False)

# ------------------ Model Department ------------------
class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    # Relationships
    doctors = db.relationship('Doctor', back_populates='department', lazy=True)

# ------------------ Doctor Model ------------------
class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    experience_years = db.Column(db.Integer)

    # Relationships
    user = db.relationship('User', back_populates='doctor_profile')
    department = db.relationship('Department', back_populates='doctors')
    appointments = db.relationship('Appointment', back_populates='doctor', lazy=True)
    availability_slots = db.relationship('DoctorAvailability', back_populates='doctor', cascade='all, delete-orphan')
    patient_histories = db.relationship('PatientHistory', back_populates='doctor', lazy=True)

# ------------------ Patient Model ------------------
class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='patient_profile')
    appointments = db.relationship('Appointment', back_populates='patient', lazy=True)
    medical_history = db.relationship('PatientHistory', back_populates='patient', cascade='all, delete-orphan')

# ------------------ Appointment Model ------------------
class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='booked')  # booked, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    history_record = db.relationship('PatientHistory', back_populates='appointment', uselist=False)

# ------------------ Patient History Model ------------------
class PatientHistory(db.Model):
    __tablename__ = 'patient_history'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), unique=True)   
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))             
    
    # Medical information
    visit_type = db.Column(db.String(50))       
    test_type = db.Column(db.String(100))       
    diagnosis = db.Column(db.Text)              
    treatment = db.Column(db.Text)              
    prescription = db.Column(db.Text)
    doctor_name = db.Column(db.String(100))     
    department = db.Column(db.String(100))      
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    patient = db.relationship('Patient', back_populates='medical_history')
    doctor = db.relationship('Doctor', back_populates='patient_histories')
    appointment = db.relationship('Appointment', back_populates='history_record')


# ------------------ Doctor Availability Model ------------------
class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationship
    doctor = db.relationship('Doctor', back_populates='availability_slots')