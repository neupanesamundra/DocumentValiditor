import argparse
import json
import uuid
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.rubric_schema import empty_label_payload
from core.classifier import classify_document
from core.parser import parse_document
from core.scoring_engine import extract_scoring_features, score_document

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _collect_documents(input_dir: Path):
    return [p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]


def _build_record(path: Path) -> dict:
    parsed = parse_document(path)
    text = parsed.get("text", "")
    sections = parsed.get("sections", [])
    predicted_doc_type = classify_document(text)
    baseline_score, _analysis, _suggestions, _breakdown = score_document(
        text,
        predicted_doc_type,
        sections,
        source_path=path,
    )

    return {
        "document_id": uuid.uuid4().hex,
        "metadata": {
            "filename": path.name,
            "extension": path.suffix.lower().lstrip("."),
            "source_path": str(path.resolve().relative_to(ROOT)),
            "predicted_doc_type": predicted_doc_type,
        },
        "features": extract_scoring_features(text, predicted_doc_type, sections, source_path=path),
        "model_baseline": {
            "score": baseline_score,
        },
        "labels": empty_label_payload(predicted_doc_type),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export scoring features for ML regression training.")
    parser.add_argument("--input-dir", required=True, help="Directory containing source documents.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_path = Path(args.output).resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {input_dir}")

    docs = _collect_documents(input_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for path in docs:
            handle.write(json.dumps(_build_record(path), ensure_ascii=False) + "\n")

    print(f"Exported {len(docs)} scoring records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
