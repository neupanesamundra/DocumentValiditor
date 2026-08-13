import argparse
import json
import re
import uuid
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.rules import REQUIRED_SECTION_MAP
from config.rubric_schema import empty_label_payload
from core.classifier import classify_document
from core.parser import parse_document

try:
    from core.explanation_engine import evaluate_status
    from core.scoring_engine import score_document
except ModuleNotFoundError:
    evaluate_status = None
    score_document = None

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
KNOWN_DOC_TYPES = {
    "resume": "Resume",
    "report": "Report",
    "thesis": "Thesis",
    "general document": "General Document",
    "general_document": "General Document",
    "cv": "CV",
    "cover letter": "Cover Letter",
    "cover_letter": "Cover Letter",
    "essay": "Essay",
    "proposal": "Proposal",
}


def _collect_documents(input_dir: Path):
    return [p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]


def _extract_features(text: str, sections: list[str], doc_type: str) -> dict:
    words = re.findall(r"\b\w+\b", text)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    long_line_count = sum(1 for ln in lines if len(ln) > 180)
    required = REQUIRED_SECTION_MAP.get(doc_type, [])
    found_required = [sec for sec in required if sec in sections]

    return {
        "word_count": len(words),
        "line_count": len(lines),
        "char_count": len(text),
        "avg_words_per_line": round(len(words) / max(1, len(lines)), 3),
        "long_line_count": long_line_count,
        "detected_sections": sections,
        "detected_sections_count": len(sections),
        "required_sections_total": len(required),
        "required_sections_found": len(found_required),
        "required_sections_ratio": round(len(found_required) / max(1, len(required)), 3) if required else 1.0,
    }


def _infer_classification_label(path: Path) -> str | None:
    folder_name = path.parent.name.strip().lower()
    return KNOWN_DOC_TYPES.get(folder_name)


def _build_record(path: Path, selected_doc_type: str) -> dict:
    parsed = parse_document(path)
    text = parsed.get("text", "")
    sections = parsed.get("sections", [])

    predicted_doc_type = classify_document(text)
    classification_label = _infer_classification_label(path)
    effective_selected_type = selected_doc_type
    if effective_selected_type == "Auto Detect" and classification_label:
        effective_selected_type = classification_label

    doc_type = effective_selected_type if effective_selected_type != "Auto Detect" else predicted_doc_type
    baseline_score = None
    baseline_status = "Unavailable"
    if score_document is not None and evaluate_status is not None:
        score, _analysis, _suggestions, _breakdown = score_document(text, doc_type, sections)
        baseline_score = score
        baseline_status = evaluate_status(score)

    return {
        "document_id": uuid.uuid4().hex,
        "metadata": {
            "filename": path.name,
            "extension": path.suffix.lower().lstrip("."),
            "source_path": str(path.resolve().relative_to(ROOT)),
            "selected_doc_type": effective_selected_type,
            "predicted_doc_type": predicted_doc_type,
            "classification_label": classification_label,
        },
        "features": _extract_features(text, sections, doc_type),
        "model_baseline": {
            "score": baseline_score,
            "status": baseline_status,
        },
        "labels": empty_label_payload(doc_type),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export training features for document quality modeling.")
    parser.add_argument("--input-dir", required=True, help="Directory containing source documents (pdf/docx/txt).")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    parser.add_argument(
        "--selected-doc-type",
        default="Auto Detect",
        choices=["Auto Detect", "Resume", "Report", "Thesis", "General Document"],
        help="Force one doc type for exported rows, or use Auto Detect.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir).resolve()
    output_path = Path(args.output).resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {input_dir}")

    docs = _collect_documents(input_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for path in docs:
            record = _build_record(path, args.selected_doc_type)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Exported {len(docs)} records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
