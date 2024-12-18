from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Event
from datetime import datetime  

from flask_migrate import Migrate
from models import db

from flask import Flask
from flask_migrate import Migrate
from models import db
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://sqladmin:MyNewStrongP@ssword123@finalsqlserver.database.windows.net:1433/FinalDB"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)

db.init_app(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please use a different email.", "error")
            return redirect(url_for('register'))

        # Add the new user if email doesn't exist
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_event', methods=["GET", "POST"])
@login_required
def create_event():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')  # Convert to datetime object
        new_event = Event(title=title, description=description, date=date, created_by=current_user.id)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template("create_event.html")


@app.route('/dashboard')
@login_required
def dashboard():
    events = Event.query.all()
    return render_template("dashboard.html", events=events)

if __name__ == "__main__":
    app.run(debug=True)
