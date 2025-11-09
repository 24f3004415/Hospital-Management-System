# Hospital-Management-System

Hospital Management System (HMS) web application that allows Admins, Doctors, and Patients to interact with the system based on their roles.

Name- Mohit Kumar Rai
Roll No - 24f3004415

"""
RELATIONSHIP MAPPING:

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
