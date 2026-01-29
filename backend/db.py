import sqlite3

DB_NAME = "filesystem.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('file','folder')) NOT NULL,
            parent_id INTEGER,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(parent_id) REFERENCES nodes(id)
        )
    """)

    conn.commit()
    conn.close()


# Run this file directly to create DB
if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully")
