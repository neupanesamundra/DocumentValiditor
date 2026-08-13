from pathlib import Path

from config.settings import ML_SCORER_ENABLED, SCORER_MODEL_PATH

try:
    import joblib
except ModuleNotFoundError:
    joblib = None

_scorer_model = None
_scorer_model_failed = False


def _load_scorer_model():
    global _scorer_model, _scorer_model_failed

    if not ML_SCORER_ENABLED:
        return None
    if _scorer_model_failed:
        return None
    if _scorer_model is not None:
        return _scorer_model
    if joblib is None:
        return None

    model_path = Path(SCORER_MODEL_PATH)
    if not model_path.exists():
        return None

    try:
        _scorer_model = joblib.load(model_path)
        return _scorer_model
    except Exception:
        _scorer_model_failed = True
        _scorer_model = None
        return None


def predict_score_ml(features: dict) -> float | None:
    model = _load_scorer_model()
    if model is None:
        return None

    try:
        prediction = model.predict([features])
    except Exception:
        return None

    if len(prediction) == 0:
        return None

    return float(prediction[0])
