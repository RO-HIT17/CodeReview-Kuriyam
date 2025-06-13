from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(_name_)
DB_PATH = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return '''
    <form method="POST" action="/login">
        <input name="username" placeholder="Username" />
        <input name="password" placeholder="Password" />
        <input type="submit" />
    </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    if result:
        return render_template_string(f"<h1>Welcome, {username}!</h1>")
    else:
        return "Invalid credentials"

@app.route('/admin')
def admin():
    if request.args.get('key') == 'letmein123':
        return os.popen('cat /etc/passwd').read()
    return "Unauthorized", 403

if _name_ == '_main_':
    init_db()
    app.run(debug=True)
