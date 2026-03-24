import numpy as np
import xgboost as xgb
from utils.feature_engineering import expand_features


def classify_rul(rul):
    if rul > 80:
        return "Healthy"
    elif rul > 30:
        return "At Risk"
    else:
        return "Critical"


def _resolve_scaler(scaler_object):
    if hasattr(scaler_object, "transform"):
        return scaler_object, None

    if isinstance(scaler_object, dict):
        for key in sorted(scaler_object):
            candidate = scaler_object[key]
            if hasattr(candidate, "transform"):
                return candidate, str(key)

    raise ValueError("Scaler object is not compatible with transform(X)")


def predict_rul(models, dataset_type, input_data):
    dataset_type = dataset_type.lower()
    model_key = f"model_{dataset_type}"
    scaler_key = f"scaler_{dataset_type}"

    if model_key not in models:
        raise ValueError(f"Missing model artifact: {model_key}")
    if scaler_key not in models:
        raise ValueError(f"Missing scaler artifact: {scaler_key}")

    model = models[model_key]
    scaler_object = models[scaler_key]

    X = expand_features(input_data)
    scaler, scaler_variant = _resolve_scaler(scaler_object)
    X_scaled = scaler.transform(X)

    if isinstance(model, xgb.Booster):
        dmatrix = xgb.DMatrix(X_scaled)
        prediction = model.predict(dmatrix)[0]
    else:
        prediction = model.predict(X_scaled)[0]

    predicted_rul = float(prediction)
    status = classify_rul(predicted_rul)

    response = {
        "dataset": dataset_type,
        "predicted_rul": predicted_rul,
        "status": status,
    }

    if scaler_variant is not None:
        response["scaler_variant"] = scaler_variant

    return response