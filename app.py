from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import bcrypt
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('db/posts.db')
    conn.row_factory = sqlite3.Row
    return conn

# Главная страница
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# Страница авторизации
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return redirect(url_for('dashboard'))
        else:
            return 'Неправильный логин или пароль'
    return render_template('login.html')

# Админ панель с возможностью добавления и удаления постов
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    
    if request.method == 'POST':
        image = request.form['image']
        description = request.form['description']
        price = request.form['price']
        link = request.form['link']
        
        # Если загружается файл
        if 'image_file' in request.files:
            image_file = request.files['image_file']
            if image_file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
                image_file.save(filepath)
                image = f'/static/uploads/{image_file.filename}'
        
        conn.execute('INSERT INTO posts (image, description, price, link) VALUES (?, ?, ?, ?)', 
                     (image, description, price, link))
        conn.commit()
    
    conn.close()
    return render_template('dashboard.html', posts=posts)

# Удаление поста
@app.route('/admin/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# Создание базы данных (если таблицы не существует)
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image TEXT NOT NULL,
                        description TEXT NOT NULL,
                        price TEXT NOT NULL,
                        link TEXT NOT NULL
                    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    init_db()
    app.run(debug=True)
