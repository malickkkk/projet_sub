from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Erreur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False, unique=True)

class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)

class Outil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

class ErreurSolution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    erreur_id = db.Column(db.Integer, db.ForeignKey('erreur.id'), nullable=False)
    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'), nullable=False)

    erreur = db.relationship('Erreur', backref=db.backref('erreur_solutions', lazy=True))
    solution = db.relationship('Solution', backref=db.backref('erreur_solutions', lazy=True))

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    utilisateurs = db.relationship('Utilisateur', secondary='conversation_utilisateur', backref=db.backref('conversations', lazy=True))

class ConversationUtilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenu = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)

    utilisateur = db.relationship('Utilisateur', backref=db.backref('messages', lazy=True))
    conversation = db.relationship('Conversation', backref=db.backref('messages', lazy=True))
