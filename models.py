# Enthält das Datenbankmodell für Benutzer
# E-Mail und Passwort werden gespeichert
# Passwörter werden sicher gehasht -> bcrypt via werkzeug.security
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialisiert die SQLAlchemy-Datenbankinstanz
db = SQLAlchemy()

# Datenbankmodell für Benutzer: beinhaltet ID als Primärschlüssel, eindeutige E-Mail-Adresse sowie Passwort-Hash (verschlüsselt)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    reisen = db.relationship('Reise', backref='benutzer', lazy=True) # Beziehung: ein Benutzer kann mehrere Reisen haben -> mit backref='benutzer' kann man später von einer Reise aus auf den Benutzer zugreifen

# Speichert ein Passwort sicher verschlüsselt und nutzt generate_password_hash() aus werkzeug
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

# Überprüft ein eingegebenes Passwort mit dem gespeicherten Hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modell für eine Reiseplanung pro Benutzer
class Reise(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Eindeutige ID
    zielort = db.Column(db.String(100), nullable=False) # Name des Reiseziels
    anreise = db.Column(db.String(50), nullable=False) # Startdatum der Reise
    abreise = db.Column(db.String(50), nullable=False) # Enddatum der Reise
    notiz = db.Column(db.Text) # Weitere Hinweise oder Planungsdetails
    sehenswuerdigkeiten = db.Column(db.Text)
    unterkunft = db.Column(db.String(200))
    benutzer_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Verknüpfung zum Benutzer