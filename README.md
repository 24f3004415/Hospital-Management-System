# Hospital-Management-System

Hospital Management System (HMS) web application that allows Admins, Doctors, and Patients to interact with the system based on their roles.

Name- Mohit Kumar Rai
Roll No - 24f3004415

"""
RELATIONSHIP MAPPING (for easy reference):

1. User ←→ Doctor (one-to-one)
   - User.doctor_profile ←→ Doctor.user

2. User ←→ Patient (one-to-one)
   - User.patient_profile ←→ Patient.user

3. Department ←→ Doctor (one-to-many)
   - Department.doctors ←→ Doctor.department

4. Doctor ←→ Appointment (one-to-many)
   - Doctor.appointments ←→ Appointment.doctor

5. Patient ←→ Appointment (one-to-many)
   - Patient.appointments ←→ Appointment.patient

6. Appointment ←→ Treatment (one-to-one)
   - Appointment.treatment ←→ Treatment.appointment

7. Patient ←→ PatientHistory (one-to-many)
   - Patient.medical_history ←→ PatientHistory.patient

8. Doctor ←→ DoctorAvailability (one-to-many)
   - Doctor.availability_slots ←→ DoctorAvailability.doctor

USAGE EXAMPLES:

# Access doctor from user
user = User.query.get(1)
if user.user_role == 'doctor':
    doctor_name = user.doctor_profile.doctor_name
    department = user.doctor_profile.department.department_name

# Access appointments for a patient
patient = Patient.query.get(1)
for appointment in patient.appointments:
    print(appointment.doctor.doctor_name)
    print(appointment.appointment_date)

# Access treatment from appointment
appointment = Appointment.query.get(1)
if appointment.treatment:
    print(appointment.treatment.diagnosis)

# Access patient history
patient = Patient.query.get(1)
for history in patient.medical_history:
    print(history.diagnosis)
    print(history.doctor_name)
"""
