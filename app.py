# app.py
from flask import Flask
from models import db, User, Doctor, Patient, Department, Appointment, DoctorAvailability, PatientHistory, Treatment

app = Flask(__name__)

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

# Initialize database
db.init_app(app)


@app.route('/')
def hello():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)