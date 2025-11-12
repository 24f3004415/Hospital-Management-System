from app import app, db
from models import User

# Create tables and default admin
with app.app_context():
    db.create_all()
    
    # Create default admin if not exists
    admin = User.query.filter_by(user_role='admin').first()
    if not admin:
        admin = User(
            user_name='admin',
            user_email='admin@hms.com',
            user_password='admin@123',
            user_role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created!")
    else:
        print("Admin already exists!")
