import sqlite3
import time
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__, static_folder='templates/images', static_url_path='/images')
app.secret_key = 'rahasia_super_aman'

DATABASE = 'database.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            ml_id TEXT,
            status TEXT,
            timestamp REAL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('store'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('login.html', error='Username dan password wajib diisi.')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user is None:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()

        conn.close()
        session['username'] = username
        return redirect(url_for('store'))

    return render_template('login.html')


@app.route('/store')
def store():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('store.html', username=session['username'])


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('login'))

    skin_name = request.args.get('skin', 'Skin Mobile Legend')

    if request.method == 'POST':
        ml_id = request.form.get('ml_id', '').strip()
        zone_id = request.form.get('zone_id', '').strip()

        if not ml_id or not zone_id:
            return render_template(
                'checkout.html',
                skin_name=skin_name,
                error='User ID dan Zone ID harus diisi.',
            )

        full_ml_id = f"{ml_id} ({zone_id})"
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (username, ml_id, status, timestamp) VALUES (?, ?, ?, ?)",
            (session['username'], full_ml_id, 'Diproses', time.time()),
        )
        conn.commit()
        conn.close()

        return redirect(url_for('process', ml_id=full_ml_id))

    return render_template('checkout.html', skin_name=skin_name)


@app.route('/process')
def process():
    if 'username' not in session:
        return redirect(url_for('login'))
    ml_id = request.args.get('ml_id', '-')
    return render_template('proses.html', ml_id=ml_id)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


