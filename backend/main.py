from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from database.crud import insert_prediction, list_recent_predictions
from database.db import init_db
from model.load_model import get_available_datasets, load_all_models
from model.predict import predict_rul
from scheduler.job import run_file_batch_job
from utils.data_loader import get_csv_feature_rows
from utils.schema import SensorInput, BatchInput

app = FastAPI(title="PrognosAI Predictive Maintenance API", version="1.0.0")

models = {}


@app.on_event("startup")
def startup_event():
    global models
    init_db()
    models = load_all_models()


def _ensure_dataset_supported(dataset):
    available = get_available_datasets(models)
    if dataset not in available:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Dataset '{dataset}' is not available",
                "available_datasets": available,
            },
        )

@app.get("/")
def home():
    return {
        "message": "PrognosAI API Running",
        "available_datasets": get_available_datasets(models),
    }


@app.post("/predict_single")
def predict_single(input_data: SensorInput):
    dataset = input_data.dataset.lower()
    features = input_data.features
    _ensure_dataset_supported(dataset)

    try:
        result = predict_rul(models, dataset, features)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    insert_prediction(
        dataset=dataset,
        predicted_rul=result["predicted_rul"],
        status=result["status"],
        features=features,
        source="api_single",
    )

    return result


@app.post("/predict_batch")
def predict_batch(input_data: BatchInput):
    dataset = input_data.dataset.lower()
    batch = input_data.batch
    _ensure_dataset_supported(dataset)

    results = []

    for features in batch:
        try:
            result = predict_rul(models, dataset, features)
            insert_prediction(
                dataset=dataset,
                predicted_rul=result["predicted_rul"],
                status=result["status"],
                features=features,
                source="api_batch",
            )
            result["saved"] = True
        except Exception as exc:
            result = {"error": str(exc), "saved": False}

        results.append(result)

    success_count = sum(1 for item in results if "error" not in item)

    return {"dataset": dataset, "total": len(results), "success": success_count, "results": results}


@app.post("/predict_file/{dataset}")
def predict_file_batch(dataset: str, file_path: str | None = None):
    dataset = dataset.lower()
    _ensure_dataset_supported(dataset)

    try:
        summary = run_file_batch_job(models, dataset=dataset, file_path=file_path, source="api_file")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return summary


@app.post("/predict_csv")
async def predict_csv(
    dataset: str = Form(...),
    file: UploadFile = File(...),
):
    dataset = dataset.lower().strip()
    _ensure_dataset_supported(dataset)

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    try:
        file_bytes = await file.read()
        rows = get_csv_feature_rows(file_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(exc)}") from exc

    results = []
    success = 0

    for row in rows:
        try:
            result = predict_rul(models, dataset, row["features"])
            insert_prediction(
                dataset=dataset,
                engine_id=row.get("engine_id"),
                predicted_rul=result["predicted_rul"],
                status=result["status"],
                features=row["features"],
                source="api_csv",
            )
            results.append({"engine_id": row.get("engine_id"), **result, "saved": True})
            success += 1
        except Exception as exc:
            results.append(
                {
                    "engine_id": row.get("engine_id"),
                    "error": str(exc),
                    "saved": False,
                }
            )

    return {
        "dataset": dataset,
        "file_name": file.filename,
        "total": len(rows),
        "success": success,
        "failed": len(rows) - success,
        "results": results,
    }


@app.get("/predictions/recent")
def recent_predictions(
    dataset: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=500),
):
    records = list_recent_predictions(limit=limit, dataset=dataset.lower() if dataset else None)
    return {
        "count": len(records),
        "predictions": [record.__dict__ for record in records],
    }