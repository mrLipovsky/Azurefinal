from app import app, db
from models import User, Event, Space, Attendance

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
