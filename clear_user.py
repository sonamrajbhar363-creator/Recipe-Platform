import sqlite3

def clear_old_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. Sabhi recipes delete karein
    cursor.execute("DELETE FROM recipes")
    
    # 2. Sabhi users delete karein (admin ko chhod kar)
    cursor.execute("DELETE FROM users WHERE role != 'admin'")
    
    conn.commit()
    conn.close()
    print("All old users and recipes deleted successfully! (Admin preserved)")

if __name__ == '__main__':
    clear_old_data()