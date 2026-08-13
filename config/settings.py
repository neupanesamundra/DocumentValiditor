import os
from pathlib import Path

APP_NAME = "Document Validator Pro"
DEBUG = True

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv_file(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = value.strip()

        if not key:
            continue

        if value and len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        # Project-level .env should define the app's runtime defaults consistently,
        # even when the IDE/session injected stale values earlier.
        os.environ[key] = value


_load_dotenv_file(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
MODEL_DATA_DIR = DATA_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_FOLDER = OUTPUT_DIR / "temp_uploads"
IMPROVED_FOLDER = OUTPUT_DIR / "improved_docs"
LANGUAGETOOL_DIR = DATA_DIR / "languagetool"
LANGUAGETOOL_ENABLED = True
LANGUAGETOOL_LOCAL_SERVER_URL = "http://127.0.0.1:8081"
CLASSIFIER_MODEL_PATH = MODEL_DATA_DIR / "document_classifier.joblib"
SCORER_MODEL_PATH = MODEL_DATA_DIR / "document_scorer.joblib"

AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").strip().lower()
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
AI_REQUEST_TIMEOUT_SECONDS = int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "45"))
AI_MAX_INPUT_CHARS = int(os.getenv("AI_MAX_INPUT_CHARS", "12000"))
AI_RETRY_ATTEMPTS = int(os.getenv("AI_RETRY_ATTEMPTS", "3"))
AI_RETRY_BACKOFF_SECONDS = float(os.getenv("AI_RETRY_BACKOFF_SECONDS", "1.5"))
AI_REWRITE_TEMPERATURE = float(os.getenv("AI_REWRITE_TEMPERATURE", "0.3"))
AI_EXPLANATION_TEMPERATURE = float(os.getenv("AI_EXPLANATION_TEMPERATURE", "0.2"))
ML_CLASSIFIER_ENABLED = os.getenv("ML_CLASSIFIER_ENABLED", "true").lower() == "true"
ML_SCORER_ENABLED = os.getenv("ML_SCORER_ENABLED", "true").lower() == "true"

MAX_FILE_SIZE_MB = 0
