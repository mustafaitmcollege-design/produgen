"""
ProduGen - Database Module
SQLite database for storing sessions, products, and generated images.
Zero configuration — just works on any device.
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime
from backend.config import Config


DB_PATH = os.path.join(Config.DATA_DIR, "produgen.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        -- Sessions: tracks each product image generation session
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            status TEXT NOT NULL DEFAULT 'in_progress',
            chat_history TEXT DEFAULT '[]',
            brief TEXT DEFAULT NULL,
            product_image_path TEXT DEFAULT NULL
        );

        -- Generated Images: stores info about each generated image
        CREATE TABLE IF NOT EXISTS generated_images (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            filename TEXT NOT NULL,
            variation TEXT NOT NULL,
            variation_description TEXT,
            prompt_used TEXT,
            platform TEXT DEFAULT 'instagram_post',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    """)

    conn.commit()
    conn.close()
    print("💾 Database initialized successfully")


# =============================================================================
# Session Operations
# =============================================================================

def create_session() -> str:
    """Create a new session and return its ID."""
    session_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    conn.execute(
        "INSERT INTO sessions (id) VALUES (?)",
        (session_id,)
    )
    conn.commit()
    conn.close()
    return session_id


def get_session(session_id: str) -> dict | None:
    """Get a session by ID."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE id = ?",
        (session_id,)
    ).fetchone()
    conn.close()

    if row:
        result = dict(row)
        result["chat_history"] = json.loads(result["chat_history"] or "[]")
        result["brief"] = json.loads(result["brief"]) if result["brief"] else None
        return result
    return None


def update_session_chat(session_id: str, chat_history: list):
    """Update the chat history for a session."""
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET chat_history = ? WHERE id = ?",
        (json.dumps(chat_history), session_id)
    )
    conn.commit()
    conn.close()


def update_session_brief(session_id: str, brief: dict):
    """Save the completed generation brief for a session."""
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET brief = ?, status = 'brief_ready' WHERE id = ?",
        (json.dumps(brief), session_id)
    )
    conn.commit()
    conn.close()


def update_session_image(session_id: str, image_path: str):
    """Save the uploaded product image path for a session."""
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET product_image_path = ? WHERE id = ?",
        (image_path, session_id)
    )
    conn.commit()
    conn.close()


def update_session_status(session_id: str, status: str):
    """Update the session status."""
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET status = ? WHERE id = ?",
        (status, session_id)
    )
    conn.commit()
    conn.close()


def list_sessions() -> list[dict]:
    """List all sessions, most recent first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# =============================================================================
# Generated Image Operations
# =============================================================================

def save_generated_image(session_id: str, image_info: dict):
    """Save a generated image record."""
    image_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    conn.execute(
        """INSERT INTO generated_images 
           (id, session_id, file_path, filename, variation, variation_description, prompt_used, platform)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            image_id,
            session_id,
            image_info.get("path", ""),
            image_info.get("filename", ""),
            image_info.get("variation", ""),
            image_info.get("variation_description", ""),
            image_info.get("prompt_used", ""),
            image_info.get("platform", "instagram_post"),
        )
    )
    conn.commit()
    conn.close()
    return image_id


def get_session_images(session_id: str) -> list[dict]:
    """Get all generated images for a session."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM generated_images WHERE session_id = ? ORDER BY created_at",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_images() -> list[dict]:
    """Get all generated images across all sessions."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM generated_images ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize the database on import
init_db()
