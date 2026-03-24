import os
import re
import joblib
import xgboost as xgb


MODEL_REGEX = re.compile(r"^model_(fd\d{3})\.(json|pkl)$", re.IGNORECASE)
SCALER_REGEX = re.compile(r"^scaler_(fd\d{3})\.pkl$", re.IGNORECASE)


def _load_model_from_path(path):
    if path.lower().endswith(".json"):
        model = xgb.Booster()
        model.load_model(path)
        return model

    return joblib.load(path)


def load_all_models():
    base_path = os.path.dirname(os.path.dirname(__file__))
    model_dir = os.path.join(base_path, "models")

    models = {}
    discovered = {}

    for file_name in sorted(os.listdir(model_dir)):
        file_path = os.path.join(model_dir, file_name)

        model_match = MODEL_REGEX.match(file_name)
        if model_match:
            dataset = model_match.group(1).lower()
            file_ext = model_match.group(2).lower()
            discovered.setdefault(dataset, {})[f"model_{file_ext}"] = file_path
            continue

        scaler_match = SCALER_REGEX.match(file_name)
        if scaler_match:
            dataset = scaler_match.group(1).lower()
            discovered.setdefault(dataset, {})["scaler"] = file_path

    for dataset, artifacts in discovered.items():
        model_path = artifacts.get("model_json") or artifacts.get("model_pkl")
        scaler_path = artifacts.get("scaler")

        if not model_path or not scaler_path:
            continue

        models[f"model_{dataset}"] = _load_model_from_path(model_path)
        models[f"scaler_{dataset}"] = joblib.load(scaler_path)

    if not models:
        raise RuntimeError(f"No usable model + scaler pairs found in {model_dir}")

    return models


def get_available_datasets(models):
    available = []
    for key in models:
        if key.startswith("model_"):
            available.append(key.replace("model_", ""))
    return sorted(set(available))