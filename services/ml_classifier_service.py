from pathlib import Path

from config.settings import CLASSIFIER_MODEL_PATH, ML_CLASSIFIER_ENABLED

try:
    import joblib
except ModuleNotFoundError:
    joblib = None

_classifier_model = None
_classifier_model_failed = False


def _load_classifier_model():
    global _classifier_model, _classifier_model_failed

    if not ML_CLASSIFIER_ENABLED:
        return None
    if _classifier_model_failed:
        return None
    if _classifier_model is not None:
        return _classifier_model

    if joblib is None:
        return None

    model_path = Path(CLASSIFIER_MODEL_PATH)
    if not model_path.exists():
        return None

    try:
        _classifier_model = joblib.load(model_path)
        return _classifier_model
    except Exception:
        _classifier_model_failed = True
        _classifier_model = None
        return None


def predict_document_type_ml(text: str) -> str | None:
    model = _load_classifier_model()
    if model is None:
        return None

    normalized_text = (text or "").strip()
    if not normalized_text:
        return None

    try:
        prediction = model.predict([normalized_text])
    except Exception:
        return None

    if len(prediction) == 0:
        return None

    predicted_type = str(prediction[0]).strip()
    return predicted_type or None
