# app.py
from flask import Flask, redirect, url_for,render_template
from models import db, User, Doctor, Patient, Department, Appointment, DoctorAvailability, PatientHistory, Treatment

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


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')




if __name__ == '__main__':
    app.run(debug=True)