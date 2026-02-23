import sqlite3
from werkzeug.security import generate_password_hash

def setup_fresh_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Purane tables saaf karein (Data reset)
    cursor.execute("DELETE FROM recipes")
    cursor.execute("DELETE FROM users")

    # 2. Naya Admin banayein jiska password Secure (Hashed) ho
    # Username: admin, Password: password123
    hashed_admin_pass = generate_password_hash('password123')
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                   ('admin', hashed_admin_pass, 'admin'))

    conn.commit()
    conn.close()
    print("Database Reset Successful!")
    print("Username: admin | Password: password123")

if __name__ == '__main__':
    setup_fresh_db()