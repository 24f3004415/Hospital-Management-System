# 🏥 Matrix HMS — Hospital Management System

> A full-stack **Flask + SQLite3** web application for managing hospital operations — including admin, doctor, and patient dashboards.  
> Built with a clean MVC architecture and Bootstrap UI

---

## 📋 Project Overview

Matrix HMS (Hospital Management System) is designed to streamline hospital workflows by enabling three major roles — **Admin**, **Doctor**, and **Patient** — each with their own dedicated dashboard and functionality.

This project focuses on user authentication, appointment management, patient history tracking, and doctor availability scheduling, all within a simple, database-driven web interface.

---

## 🚀 Features by Role

### 👨‍💼 Admin
- Create and manage **Doctors** and **Departments**
- View all registered **Patients** and **Doctors**
- Monitor upcoming **Appointments**
- Access **Patient medical history**
- Assign doctors to departments

### 👨‍⚕️ Doctor
- View assigned **Appointments**
- Mark appointments as **Completed** or **Cancelled**
- Add **Diagnosis**, **Treatment**, and **Prescriptions**
- View complete **Patient Medical History**
- Manage and provide **Availability Schedule** (next 7 days)
- User-friendly dashboard with Bootstrap UI

### 🧑‍🤝‍🧑 Patient
- Register and log in 
- Update **Profile** details (name, email, etc.)
- View and search **Doctors by specialization**
- Book, reschedule, or cancel **Appointments**
- View upcoming and past **Appointments**
- Access complete **Medical History**

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend Framework** | Flask (Python) |
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Database** | SQLite3 (via SQLAlchemy ORM) |
| **Templating Engine** | Jinja2 |
| **Version Control** | Git + GitHub |
| **Virtual Environment** | venv (Python 3.x) |

---

## 📂 Folder Structure
```
HOSPITAL-MANAGEMENT-SYSTEM/
│
├── 📄 app.py                    # Main Flask application
├── 📄 models.py                 # Database models using SQLAlchemy
├── 📄 init_db.py                # Database initialization script
│
├── 📁 instance/
│   └── 🗄️ hospital.db           # SQLite database file
│
├── 📁 static/
│   ├── 🎨 css/                  # Custom CSS files
│   └── 🖼️ images/               # Image assets
│
├── 📁 templates/
│   ├── 👨‍💼 AdminUI/              # Admin dashboards and forms
│   ├── 👨‍⚕️ DoctorUI/             # Doctor dashboards and forms
│   ├── 🧑‍🤝‍🧑 PatientUI/            # Patient dashboards and forms
│   ├── 📄 base.html             # Common layout for all pages
│   ├── 🔐 login.html            # User login page
│   ├── ✍️ signup.html           # Registration page
│   └── 🏠 landing.html          # Home/landing page
│
├── 🐍 Venv/                     # Python virtual environment
├── 📖 README.md                 # Project documentation
└── 📋 requirements.txt          # Python dependencies
```
---

## 🧩 Database Models

- **User** → Base model (Admin / Doctor / Patient)
- **Doctor** → Extends `User`, linked to `Department`
- **Patient** → Extends `User`, linked to `Appointments` & `PatientHistory`
- **Appointment** → Doctor-Patient booking
- **PatientHistory** → Stores diagnosis, treatment, prescription details
- **DoctorAvailability** → Tracks available slots for next 7 days
- **Department** → Specializations (Cardiology, ENT, etc.)

