import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "prognosai.db"


def get_db_path():
	path_from_env = os.getenv("PROGNOSAI_DB_PATH")
	if path_from_env:
		return Path(path_from_env)
	return DEFAULT_DB_PATH


def get_connection():
	db_path = get_db_path()
	db_path.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(db_path)
	conn.row_factory = sqlite3.Row
	return conn


def init_db():
	with get_connection() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS engine_predictions (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				dataset TEXT NOT NULL,
				engine_id INTEGER,
				predicted_rul REAL NOT NULL,
				status TEXT NOT NULL,
				features_json TEXT,
				source TEXT DEFAULT 'api',
				created_at TEXT DEFAULT CURRENT_TIMESTAMP
			)
			"""
		)
		conn.commit()
