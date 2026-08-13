import argparse
import json
from pathlib import Path
import sys

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import CLASSIFIER_MODEL_PATH
from core.parser import parse_document


def _read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _resolve_label(record: dict) -> str | None:
    metadata = record.get("metadata") or {}
    explicit_label = (metadata.get("classification_label") or "").strip()
    if explicit_label:
        return explicit_label

    selected_type = (metadata.get("selected_doc_type") or "").strip()
    if selected_type and selected_type != "Auto Detect":
        return selected_type

    return None


def _resolve_text(record: dict) -> str:
    metadata = record.get("metadata") or {}
    source_path = metadata.get("source_path")
    if not source_path:
        return ""

    candidate = ROOT / source_path
    if not candidate.exists():
        return ""

    parsed = parse_document(candidate)
    return (parsed.get("text") or "").strip()


def _build_training_rows(records: list[dict]) -> tuple[list[str], list[str]]:
    texts: list[str] = []
    labels: list[str] = []

    for record in records:
        label = _resolve_label(record)
        text = _resolve_text(record)
        if not label or not text:
            continue
        texts.append(text)
        labels.append(label)

    return texts, labels


def main() -> int:
    parser = argparse.ArgumentParser(description="Train an offline ML document classifier.")
    parser.add_argument("--dataset", required=True, help="Path to labeled JSONL exported from training data.")
    parser.add_argument(
        "--output",
        default=str(CLASSIFIER_MODEL_PATH),
        help="Path to save the trained classifier joblib file.",
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset).resolve()
    output_path = Path(args.output).resolve()

    if not dataset_path.exists():
        raise SystemExit(f"Dataset file not found: {dataset_path}")

    records = _read_jsonl(dataset_path)
    texts, labels = _build_training_rows(records)
    if len(texts) < 4:
        raise SystemExit("Need at least 4 labeled documents to train the classifier.")

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000, lowercase=True)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )
    pipeline.fit(texts, labels)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)
    print(f"Trained classifier on {len(texts)} documents and saved model to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
