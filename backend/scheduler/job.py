import os

from database.crud import insert_prediction
from model.predict import predict_rul
from utils.data_loader import get_latest_engine_features


DATASET_FILE_MAP = {
	"fd001": "test_FD001.txt",
	"fd002": "test_FD002.txt",
	"fd003": "test_FD003.txt",
	"fd004": "test_FD004.txt",
}


def default_dataset_file(dataset):
	base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
	return os.path.join(base_dir, "dataset", DATASET_FILE_MAP.get(dataset.lower(), "test_FD001.txt"))


def run_file_batch_job(models, dataset, file_path=None, source="scheduler"):
	dataset = dataset.lower()
	if not file_path:
		file_path = default_dataset_file(dataset)

	rows = get_latest_engine_features(file_path)
	saved = 0
	failures = 0

	for row in rows:
		try:
			result = predict_rul(models, dataset, row["features"])
			insert_prediction(
				dataset=dataset,
				engine_id=row["engine_id"],
				predicted_rul=result["predicted_rul"],
				status=result["status"],
				features=row["features"],
				source=source,
			)
			saved += 1
		except Exception:
			failures += 1

	return {
		"dataset": dataset,
		"file_path": file_path,
		"total_engines": len(rows),
		"saved_predictions": saved,
		"failed_predictions": failures,
	}
