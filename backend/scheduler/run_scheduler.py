import argparse
import time

from database.db import init_db
from model.load_model import load_all_models
from scheduler.job import run_file_batch_job


def main():
	parser = argparse.ArgumentParser(description="Run PrognosAI batch scheduler")
	parser.add_argument("--dataset", default="fd001", help="Dataset key (fd001-fd004)")
	parser.add_argument("--file-path", default=None, help="Path to CMAPSS test file")
	parser.add_argument("--interval-seconds", type=int, default=600, help="Run interval in seconds")
	args = parser.parse_args()

	init_db()
	models = load_all_models()

	while True:
		summary = run_file_batch_job(models, dataset=args.dataset, file_path=args.file_path)
		print(summary)
		time.sleep(args.interval_seconds)


if __name__ == "__main__":
	main()
