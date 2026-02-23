import sqlite3

def reset():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Pehle purani tables delete karein (agar hain)
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS recipes')

    # 1. Users table (With Role Column)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # 2. Recipes table (With all required columns)
    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            image_url TEXT,
            status TEXT DEFAULT 'pending',
            is_trending INTEGER DEFAULT 0,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database reset successful! Saare columns add ho gaye hain.")

if __name__ == '__main__':
    reset()