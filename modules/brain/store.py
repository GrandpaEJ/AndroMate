# modules/brain/store.py
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.expanduser("~/storage/shared/AndroMate/brain.db")
# Ensure directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Conversation history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User Knowledge Base (Facts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                key TEXT PRIMARY KEY,
                value TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Action History
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT,
                details TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

# --- History Operations ---

def add_message(role, content, session_id="default"):
    """Add a message to the history."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO history (role, content, session_id) VALUES (?, ?, ?)",
            (role, content, session_id)
        )
        conn.commit()

def get_recent_history(limit=10, session_id="default"):
    """Retrieve recent history for a session."""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT role, content FROM history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        # Reverse to get chronological order
        return list(reversed([dict(row) for row in cursor.fetchall()]))

def clear_history(session_id="default"):
    """Clear history for a session."""
    with get_connection() as conn:
        conn.execute("DELETE FROM history WHERE session_id = ?", (session_id,))
        conn.commit()

# --- Fact Operations ---

def update_fact(key, value):
    """Update or insert a user fact."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO user_facts (key, value, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (key, value)
        )
        conn.commit()

def get_all_facts():
    """Retrieve all stored user facts as a dictionary."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT key, value FROM user_facts")
        return {row['key']: row['value'] for row in cursor.fetchall()}

# --- Action Operations ---

def log_action(action_type, details, status="success"):
    """Log an action taken by the agent."""
    if isinstance(details, (dict, list)):
        details = json.dumps(details)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO actions (action_type, details, status) VALUES (?, ?, ?)",
            (action_type, details, status)
        )
        conn.commit()

# Initialize on import
init_db()
