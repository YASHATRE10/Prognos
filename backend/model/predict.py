import numpy as np
import xgboost as xgb
from sklearn.exceptions import NotFittedError
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


def _apply_scaler(scaler, X):
    try:
        return scaler.transform(X), None
    except NotFittedError:
        # Some legacy artifacts include an unfitted scaler; fallback keeps inference usable.
        return X, "scaler_not_fitted_used_identity"


def _expected_feature_count(model):
    if hasattr(model, "n_features_in_"):
        return int(model.n_features_in_)
    if isinstance(model, xgb.Booster):
        return int(model.num_features())
    return None


def _align_feature_count(X, expected_count):
    current_count = X.shape[1]
    if expected_count is None or current_count == expected_count:
        return X, None

    if current_count < expected_count:
        padded = np.pad(X, ((0, 0), (0, expected_count - current_count)), mode="constant")
        return padded, f"feature_count_padded_{current_count}_to_{expected_count}"

    truncated = X[:, :expected_count]
    return truncated, f"feature_count_truncated_{current_count}_to_{expected_count}"


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
    X_scaled, scaling_note = _apply_scaler(scaler, X)
    expected_count = _expected_feature_count(model)
    X_scaled, feature_note = _align_feature_count(X_scaled, expected_count)

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
    if scaling_note is not None:
        response["preprocessing_note"] = scaling_note
    if feature_note is not None:
        response["feature_note"] = feature_note

    return response