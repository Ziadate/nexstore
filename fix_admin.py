"""
fix_admin.py - Creates a fresh admin user in store.db.
Run once: python fix_admin.py
"""
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'store.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Remove any existing admin user
c.execute("DELETE FROM users WHERE email = 'admin@nexstore.com'")

# Insert fresh admin with hashed password
c.execute(
    "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
    (
        'Admin',
        'admin@nexstore.com',
        generate_password_hash('nexstore2024'),
        'admin'
    )
)

conn.commit()

# Verify
row = c.execute("SELECT id, name, email, role FROM users WHERE email='admin@nexstore.com'").fetchone()
print("Admin user created successfully!")
print(f"  ID   : {row[0]}")
print(f"  Name : {row[1]}")
print(f"  Email: {row[2]}")
print(f"  Role : {row[3]}")

conn.close()
