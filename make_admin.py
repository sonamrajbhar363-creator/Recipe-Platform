import sqlite3

def set_admin_role():
    username = input("Kis username ko admin banana hai? : ")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check karein ki user exist karta hai ya nahi
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        cursor.execute("UPDATE users SET role='admin' WHERE username=?", (username,))
        conn.commit()
        print(f"✅ Badhai ho! '{username}' ab Admin ban gaya hai.")
    else:
        print(f"❌ Error: '{username}' naam ka koi user nahi mila.")
    
    conn.close()

if __name__ == '__main__':
    set_admin_role()