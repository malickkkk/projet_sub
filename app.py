from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from flask_migrate import Migrate
from models import db, Erreur, Solution, Outil, ErreurSolution, Utilisateur, Conversation, ConversationUtilisateur, Message
import sqlite3
import requests

app = Flask(__name__)

# Configuration pour SQLAlchemy et Flask-Session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fixitbot.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.secret_key = 'votre_cle_secrete'
db.init_app(app)
migrate = Migrate(app, db)
Session(app)

# Initialiser la base de données SQLite pour les messages
def obtenir_connexion_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = obtenir_connexion_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Fonction de recherche sur l'API Stack Exchange
def rechercher_stack_exchange(description_erreur):
    url = "https://api.stackexchange.com/2.3/search"
    params = {
        "order": "desc",
        "sort": "relevance",
        "intitle": description_erreur,
        "site": "stackoverflow",
        "filter": "withbody",
        "key": "VOTRE_CLE_API_STACK_EXCHANGE"  # Remplacez par votre clé API
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get('items', [])
        return results
    return []

# Traiter le message entrant
def traiter_message(message):
    message_lower = message.lower()  # Convertir le message en minuscules pour la comparaison
    if "erreur" in message_lower:
        erreur_desc = message_lower.split("erreur ")[1].strip()
        solutions = rechercher_stack_exchange(erreur_desc)
        if solutions:
            solutions_desc = [f"{sol['title']}: {sol['link']}" for sol in solutions]
            return f"Pour l'erreur '{erreur_desc}', voici quelques solutions : {', '.join(solutions_desc)}"
        else:
            return f"Je n'ai trouvé aucune solution pour l'erreur '{erreur_desc}'."
    elif "outil" in message_lower:
        outil_nom = message_lower.split("outil ")[1].strip()
        outil = Outil.query.filter_by(nom=outil_nom).first()
        if outil:
            return f"L'outil '{outil_nom}' est décrit comme : {outil.description}"
        else:
            return f"Je n'ai trouvé aucune information sur l'outil '{outil_nom}'."
    else:
        return "Désolé, je ne comprends pas votre demande. Veuillez préciser votre question."


# Routes
@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'user@example.com' and password == 'password': 
            flash('Connexion utilisateur réussie', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Identifiants utilisateur invalides', 'danger')
    return render_template('login.html')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        flash('Inscription réussie', 'success')
        return redirect(url_for('login'))
    return render_template('inscription.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'admin@example.com' and password == 'adminpassword':  
            flash('Connexion admin réussie', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Identifiants admin invalides', 'danger')
    return render_template('admin_login.html')

@app.route('/historique')
def historique():
    conn = obtenir_connexion_db()
    messages = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('historique.html', messages=messages)

@app.route('/message', methods=['POST'])
def message():
    data = request.get_json()
    message = data.get('message', '')
    response = traiter_message(message)
    return jsonify({"response": response})

@app.route('/get_response', methods=['POST'])
def obtenir_reponse():
    user_message = request.form['user_message']
    bot_response = traiter_message(user_message)
    conn = obtenir_connexion_db()
    conn.execute('INSERT INTO messages (sender, message) VALUES (?, ?)', ('user', user_message))
    conn.execute('INSERT INTO messages (sender, message) VALUES (?, ?)', ('bot', bot_response))
    conn.commit()
    conn.close()
    return {'bot_response': bot_response}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
