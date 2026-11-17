import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..core.config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        video_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        duration_sec REAL NOT NULL,
        width INTEGER NOT NULL,
        height INTEGER NOT NULL,
        fps REAL NOT NULL,
        dataset TEXT NOT NULL,
        file_size_mb REAL NOT NULL,
        file_path TEXT NOT NULL,
        highlight_path TEXT,
        status TEXT NOT NULL,
        job_id TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        video_id TEXT PRIMARY KEY,
        submission_json TEXT NOT NULL,
        graph_json TEXT NOT NULL,
        stats_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (video_id) REFERENCES videos (video_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        status TEXT NOT NULL,
        progress INTEGER NOT NULL,
        current_step TEXT NOT NULL,
        error TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def save_video(meta: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO videos (
        video_id, filename, duration_sec, width, height, fps,
        dataset, file_size_mb, file_path, highlight_path, status, job_id, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        meta["video_id"], meta["filename"], meta["duration_sec"],
        meta["width"], meta["height"], meta["fps"],
        meta["dataset"], meta["file_size_mb"], meta["file_path"],
        meta.get("highlight_path", ""), meta["status"], meta["job_id"], meta["created_at"]
    ))
    conn.commit()
    conn.close()


def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def list_videos() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_result(video_id: str, submission: dict, graph: dict, stats: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time_str()
    cursor.execute("""
    INSERT OR REPLACE INTO results (video_id, submission_json, graph_json, stats_json, updated_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        video_id,
        json.dumps(submission),
        json.dumps(graph),
        json.dumps(stats),
        now
    ))
    conn.commit()
    conn.close()


def get_result(video_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results WHERE video_id = ?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "video_id": row["video_id"],
        "submission": json.loads(row["submission_json"]),
        "graph": json.loads(row["graph_json"]),
        "stats": json.loads(row["stats_json"]),
        "updated_at": row["updated_at"]
    }


def save_job(job_id: str, video_id: str, status: str, progress: int, current_step: str, error: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time_str()
    cursor.execute("""
    INSERT OR REPLACE INTO jobs (job_id, video_id, status, progress, current_step, error, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM jobs WHERE job_id = ?), ?), ?)
    """, (job_id, video_id, status, progress, current_step, error, job_id, now, now))
    conn.commit()
    conn.close()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def time_str() -> str:
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

