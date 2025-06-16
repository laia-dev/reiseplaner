from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Reise
import os

# Flask-App Setup & Konfiguration: erstellt die Flask-Anwendung und definiert globale Einstellungen -> der SECRET_KEY wird für sichere Sessions und Login verwendet
# Die SQLite-Datenbank "reiseplaner.db" speichert Benutzer- und Reisedaten
app = Flask(__name__)
# Sicherheitsschlüssel für Session-Verwaltung und Login
app.config['SECRET_KEY'] = 'geheim123'
# Datenbank-Konfiguration: Lokale SQLite-Datenbank für dieses Projekt
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reiseplaner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Flask-Login Setup: der LoginManager verwaltet den Login-Status der Benutzer -> user_loader lädt den Benutzer aus der Datenbank anhand seiner ID
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Startseite: diese Route ist öffentlich und zeigt die Begrüßungsseite
@app.route("/")
def home():
    return render_template("home.html")

# Benutzerregistrierung: diese Route zeigt das Registrierungsformular (GET) und verarbeitet neue Benutzeranmeldungen (POST) -> bei erfolgreicher Registrierung wird der User gespeichert & zur Login-Seite weitergeleitet
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

# Login-Route: verarbeitet das Login-Formular -> wenn E-Mail und Passwort korrekt sind -> Login & Weiterleitung zur Startseite
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

# Logout-Route: nur für eingeloggte Benutzer -> meldet Benutzer ab und leitet zur Login-Seite
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du wurdest erfolgreich ausgeloggt.")
    return redirect(url_for("login"))

# Geschützte Benutzerseite: Mein Reiseplan: diese Route darf nur aufgerufen werden, wenn der Nutzer eingeloggt ist -> zeigt persönliche Reisedaten oder Eingabeformular
@app.route("/mein-reiseplan")
@login_required
def mein_reiseplan():
    return "Das ist dein geschützter Reiseplan"

# Route für Reiseformular: verarbeitet neue Reisen und speichert sie für den eingeloggten Benutzer
@app.route("/reise-hinzufuegen", methods=["GET", "POST"])
@login_required
def reise_hinzufuegen():
    if request.method == "POST":
        zielort = request.form["zielort"]
        datum = request.form["datum"]
        notiz = request.form["notiz"]

        neue_reise = Reise(zielort=zielort, datum=datum, notiz=notiz, benutzer=current_user)
        db.session.add(neue_reise)
        db.session.commit()

        flash("Reise wurde gespeichert!")
        return redirect(url_for("home"))

    return render_template("reiseformular.html")

# Startpunkt der Anwendung
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)