import sqlite3
import bcrypt

# Подключаемся к базе данных
conn = sqlite3.connect('db/posts.db')

# Логин и пароль администратора
username = 'shikov'
password = 'bokov006'

# Хеширование пароля
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Вставляем данные в таблицу пользователей
conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
conn.commit()
conn.close()

print(f'Пользователь {username} успешно добавлен.')
