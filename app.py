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
    reisen = Reise.query.filter_by(benutzer=current_user).all()
    return render_template("reiseplan.html", reisen=reisen)

# Route für Reiseformular: verarbeitet neue Reisen und speichert sie für den eingeloggten Benutzer
@app.route("/reise-hinzufuegen", methods=["GET", "POST"])
@login_required
def reise_hinzufuegen():
    if request.method == "POST":
        zielort = request.form.get("zielort")
        anreise = request.form.get("anreise")
        abreise = request.form.get("abreise")
        notiz = request.form.get("notiz")
        sehenswuerdigkeiten = request.form.get("sehenswuerdigkeiten")
        unterkunft = request.form.get("unterkunft")
        foodspots = request.form.get("foodspots")
        packliste = request.form.get("packliste")

        neue_reise = Reise(zielort=zielort, anreise=anreise, abreise=abreise, notiz=notiz, sehenswuerdigkeiten=sehenswuerdigkeiten, unterkunft=unterkunft, foodspots=foodspots, packliste=packliste, benutzer_id=current_user.id)
        db.session.add(neue_reise)
        db.session.commit()

        flash("Reise wurde gespeichert!")
        return redirect(url_for("home"))

    return render_template("reiseformular.html")

# Löschen einer Reise: diese Route erlaubt es eingeloggten Benutzern, eine ihrer gespeicherten Reisen zu löschen -> vor dem Löschen wird serverseitig geprüft, ob die Reise dem eingeloggten Benutzer gehört, andernfalls wird der Zugriff verweigert
@app.route("/reise_loeschen/<int:reise_id>")
@login_required
def reise_loeschen(reise_id):
    reise = Reise.query.get_or_404(reise_id)

    if reise.benutzer_id != current_user.id:
        flash("Du darfst diese Reise nicht löschen.")
        return redirect(url_for('mein_reiseplan'))

    db.session.delete(reise)
    db.session.commit()
    flash("Reise wurde gelöscht.")
    return redirect(url_for('mein_reiseplan'))

# Route zum Bearbeiten einer Reise: zeigt ein Formular mit bestehenden Reisedaten, speichert Änderungen in der Datenbank -> nur für eingeloggte Benutzer
@app.route("/reise-bearbeiten/<int:reise_id>", methods=["GET", "POST"])
@login_required
def reise_bearbeiten(reise_id):
    reise = Reise.query.get_or_404(reise_id)

    if reise.benutzer_id != current_user.id:
        flash("Du darfst diese Reise nicht bearbeiten.")
        return redirect(url_for('mein_reiseplan'))

    if request.method == "POST":
        reise.zielort = request.form.get("zielort")
        reise.anreise = request.form.get("anreise")
        reise.abreise = request.form.get("abreise")
        reise.notiz = request.form.get("notiz")
        reise.packliste = request.form.get("packliste")
        reise.sehenswuerdigkeiten = request.form.get("sehenswuerdigkeiten")
        reise.unterkunft = request.form.get("unterkunft")
        reise.foodspots = request.form.get("foodspots")
        db.session.commit()
        flash("Reise wurde aktualisiert.")
        return redirect(url_for('mein_reiseplan'))

    return render_template("reise_bearbeiten.html", reise=reise)

# Startpunkt der Anwendung
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)