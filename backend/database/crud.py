import json

from database.db import get_connection
from database.models import PredictionRecord


def insert_prediction(dataset, predicted_rul, status, features=None, engine_id=None, source="api"):
	features_json = json.dumps(features) if features is not None else None

	with get_connection() as conn:
		cursor = conn.execute(
			"""
			INSERT INTO engine_predictions (dataset, engine_id, predicted_rul, status, features_json, source)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			(dataset, engine_id, predicted_rul, status, features_json, source),
		)
		conn.commit()
		return cursor.lastrowid


def list_recent_predictions(limit=100, dataset=None):
	query = """
		SELECT id, dataset, engine_id, predicted_rul, status, features_json, source, created_at
		FROM engine_predictions
	"""
	params = []

	if dataset:
		query += " WHERE dataset = ?"
		params.append(dataset)

	query += " ORDER BY id DESC LIMIT ?"
	params.append(int(limit))

	with get_connection() as conn:
		rows = conn.execute(query, params).fetchall()

	records = []
	for row in rows:
		records.append(
			PredictionRecord(
				id=row["id"],
				dataset=row["dataset"],
				engine_id=row["engine_id"],
				predicted_rul=row["predicted_rul"],
				status=row["status"],
				features_json=row["features_json"],
				source=row["source"],
				created_at=row["created_at"],
			)
		)
	return records
