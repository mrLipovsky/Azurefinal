from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from datetime import datetime
from models import db, User, Event, Space, Attendance
from flask_migrate import Migrate

from models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login manager
db.init_app(app)
migrate = Migrate(app, db) 
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    events = Event.query.all()
    return render_template("event_management.html", events=events)

@app.route("/create_event", methods=["POST", "GET"])
@login_required
def create_event():
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        location = request.form['location']
        new_event = Event(name=name, description=description, date=date, location=location)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("create_event.html")

if __name__ == "__main__":
    app.run(debug=True)
