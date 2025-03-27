import sqlite3
import bcrypt
import os

# Ensure 'db' folder exists
os.makedirs("db", exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create table for users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')
conn.commit()

# Add a sample user (hashed password)
def add_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Decode hashed password to string before inserting into DB
    cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', 
                   (username, hashed.decode('utf-8')))
    conn.commit()

# Example: Adding a test user
add_user('testuser', 'test123')

conn.close()
print("Database created successfully!")
