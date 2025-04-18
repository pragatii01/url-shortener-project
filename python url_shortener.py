from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            short_id TEXT PRIMARY KEY,
            original_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choices(characters, k=length))
        if not short_id_exists(short_id):
            return short_id

def short_id_exists(short_id):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM urls WHERE short_id = ?', (short_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']
    short_id = generate_short_id()

    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO urls (short_id, original_url) VALUES (?, ?)', (short_id, original_url))
    conn.commit()
    conn.close()

    short_url = request.host_url + short_id
    return render_template('index.html', short_url=short_url)

@app.route('/<short_id>')
def redirect_to_url(short_id):
    conn = sqlite3.connect('urls.db')
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM urls WHERE short_id = ?', (short_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    if not os.path.exists('urls.db'):
        init_db()
    app.run(debug=True)
