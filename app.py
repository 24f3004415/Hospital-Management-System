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
        user_email = request.form.get('user_email')
        user_password = request.form.get('user_password')

        user = User.query.filter_by(user_email=user_email).first()

        if user and user.user_password == user_password:

            if user.user_role == 'admin':
                return redirect(url_for('admin_dashboard', username=user.user_name))
            elif user.user_role == 'doctor':
                return redirect(url_for('doctor_dashboard', username=user.user_name))
            elif user.user_role == 'patient':
                return redirect(url_for('patient_dashboard', username=user.user_name))
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
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/admin_dashboard/<username>')
def admin_dashboard(username):
    return render_template('AdminUI/admin_dashboard.html', username=username)

@app.route('/doctor_dashboard/<username>')
def doctor_dashboard(username):
    return render_template('DoctorUI/doctor_dashboard.html', username=username)

@app.route('/patient_dashboard/<username>')
def patient_dashboard(username):
    return render_template('PatientUI/patient_dashboard.html', username=username)




if __name__ == '__main__':
    app.run(debug=True)