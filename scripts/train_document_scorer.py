import argparse
import json
from pathlib import Path
import sys

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import SCORER_MODEL_PATH


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _build_training_rows(records: list[dict]) -> tuple[list[dict], list[float]]:
    features = []
    labels = []

    for record in records:
        label = (record.get("labels") or {}).get("overall_score")
        if label is None:
            continue

        feature_row = dict(record.get("features") or {})
        if not feature_row:
            continue

        features.append(feature_row)
        labels.append(float(label))

    return features, labels


def main() -> int:
    parser = argparse.ArgumentParser(description="Train an ML regressor for document scoring.")
    parser.add_argument("--dataset", required=True, help="Path to labeled JSONL scoring dataset.")
    parser.add_argument(
        "--output",
        default=str(SCORER_MODEL_PATH),
        help="Path to save the trained scorer model.",
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset).resolve()
    output_path = Path(args.output).resolve()

    if not dataset_path.exists():
        raise SystemExit(f"Dataset file not found: {dataset_path}")

    records = _read_jsonl(dataset_path)
    features, labels = _build_training_rows(records)
    if len(features) < 5:
        raise SystemExit("Need at least 5 labeled documents to train the scorer.")

    pipeline = Pipeline(
        steps=[
            ("vectorizer", DictVectorizer(sparse=False)),
            ("regressor", RandomForestRegressor(n_estimators=200, random_state=42)),
        ]
    )
    pipeline.fit(features, labels)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)
    print(f"Trained scorer on {len(features)} labeled documents and saved model to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
