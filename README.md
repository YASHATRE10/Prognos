# PrognosAI Predictive Maintenance Pipeline

This project implements an end-to-end Remaining Useful Life (RUL) prediction pipeline for CMAPSS-style sensor data.

## Implemented Pipeline

1. Data ingestion
- CMAPSS test files are loaded from the `dataset/` folder.
- Latest cycle data per engine is extracted for prediction.

2. Feature engineering
- Input is validated as 24 features (`3` operational settings + `21` sensors).
- Features are expanded to the model input shape expected by trained artifacts.

3. Model + scaler loading
- Models and scalers are loaded from `backend/models`.
- The loader prefers `.json` model artifacts when available and supports `.pkl` fallback.
- Dataset keys are auto-discovered (`fd001` to `fd004`, based on artifacts present).

4. Inference + risk thresholding
- Prediction returns `predicted_rul` and health `status` (`Healthy`, `At Risk`, `Critical`).
- Dictionary-based scaler artifacts are supported through automatic scaler variant resolution.

5. Persistence
- Predictions are persisted into SQLite (`backend/prognosai.db`) by default.
- Storage table: `engine_predictions`.

6. Scheduling
- A scheduler runner can execute periodic batch file predictions and persist outputs.

## API Endpoints

- `GET /`
	- Service status and available dataset keys.

- `POST /predict_single`
	- Single-sample inference.
	- Stores prediction in DB.

- `POST /predict_batch`
	- Batch inference.
	- Stores successful predictions in DB.

- `POST /predict_file/{dataset}`
	- File-driven batch inference from CMAPSS file.
	- Defaults to `dataset/test_FD00X.txt` mapping.
	- Stores predictions in DB.

- `POST /predict_csv`
	- Multipart CSV upload inference.
	- Form fields: `dataset` and `file`.
	- CSV supports either:
		- `op_setting_1..3` + `sensor_1..21`, or
		- `op1..3` + `s1..21`, or
		- first 24 columns as features.
	- Optional `engine_id` column is persisted when present.

- `GET /predictions/recent?dataset=fd001&limit=20`
	- Returns recent persisted predictions.

## Run

From project root:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Scheduled Batch Job

```bash
python backend/scheduler/run_scheduler.py --dataset fd001 --interval-seconds 600
```

Optional args:
- `--file-path` to override the default dataset file.

## Database Configuration

Environment variable:
- `PROGNOSAI_DB_PATH` to change the SQLite path.

Default:
- `backend/prognosai.db`
