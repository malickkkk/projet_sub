from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
      
        if email == 'user@example.com' and password == 'password': 
            flash('User login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid user credentials', 'danger')
    return render_template('login.html')

@app.route('/inscription', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
   
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    return render_template('inscription.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
       
        if email == 'admin@example.com' and password == 'adminpassword':  
            flash('Admin login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid admin credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/historique')
def historique():
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('historique.html', messages=messages)

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['user_message']
    bot_response = "Ceci est une réponse automatique." 

 
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (sender, message) VALUES (?, ?)', ('user', user_message))
    conn.execute('INSERT INTO messages (sender, message) VALUES (?, ?)', ('bot', bot_response))
    conn.commit()
    conn.close()

    return {'bot_response': bot_response}

if __name__ == '__main__':
    app.run(debug=True)
