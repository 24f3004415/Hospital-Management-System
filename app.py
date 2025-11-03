# app.py
from flask import Flask, redirect, url_for,render_template,request,session,flash
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')
        user_role = request.form.get('user_role')

        user = User.query.filter_by(user_email=user_email).first()

        if user:
            flash(f'Welcome, {user.user_name}!')

            if user.user_role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.user_role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user.user_role == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('AdminUI/admin_dashboard.html')




if __name__ == '__main__':
    app.run(debug=True)