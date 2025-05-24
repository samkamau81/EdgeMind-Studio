import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS projects
                (id INTEGER PRIMARY KEY, name TEXT, created_at TIMESTAMP, model_path TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS logs
                (id INTEGER PRIMARY KEY, device_id TEXT, timestamp TIMESTAMP, log TEXT)""")
    conn.commit()
    conn.close()
