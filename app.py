from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geheim123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reiseplaner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("E-Mail ist bereits registriert.")
            return redirect(url_for("register"))

        new_user = User(email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registrierung erfolgreich. Du kannst dich jetzt einloggen.")
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Erfolgreich eingeloggt.")
            return redirect(url_for("home"))
        else:
            flash("Login fehlgeschlagen. Bitte überprüfe deine Daten.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du wurdest erfolgreich ausgeloggt.")
    return redirect(url_for("login"))

@app.route("/mein-reiseplan")
@login_required
def mein_reiseplan():
    return "Das ist dein geschützter Reiseplan"
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)