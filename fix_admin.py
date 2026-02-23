import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Admin ka naya secure hashed password (yahan 'admin123' ki jagah apna pass likhein)
new_hashed_password = generate_password_hash('admin123')

# Admin ka password update karein
cursor.execute("UPDATE users SET password = ? WHERE role = 'admin'", (new_hashed_password,))

conn.commit()
conn.close()
print("Admin password hash ho gaya hai! Ab aap 'admin123' se login kar sakte hain.")