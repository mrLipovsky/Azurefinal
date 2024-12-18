from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with an actual secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Login Manager
login_manager = LoginManager(app)
login_manager.login_view = "login"

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------- Database Models ----------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------- Routes ----------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        email = request.form['email']

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash("Username already taken!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

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

        new_event = Event(name=name, description=description, date=date, location=location, created_by=current_user.id)
        db.session.add(new_event)
        db.session.commit()
        flash("Event created successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("create_event.html")

# ---------------------- Main Entry Point ----------------------

if __name__ == "__main__":
    app.run(debug=True)
