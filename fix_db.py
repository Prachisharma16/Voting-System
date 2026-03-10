import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'voting.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current columns
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
print("Current columns:", columns)

# Add missing columns
if 'email' not in columns:
    cursor.execute('ALTER TABLE users ADD COLUMN email TEXT')
    print("Added email column")

if 'google_id' not in columns:
    # SQLite doesn't support adding UNIQUE column directly, so we add it without constraint
    cursor.execute('ALTER TABLE users ADD COLUMN google_id TEXT')
    print("Added google_id column")

conn.commit()

# Verify
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
print("Updated columns:", columns)

conn.close()
print("Done!")

