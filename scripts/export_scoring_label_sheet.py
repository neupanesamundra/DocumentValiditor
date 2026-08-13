import argparse
import csv
import json
from pathlib import Path


def _read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a compact CSV label sheet from scoring JSONL data.")
    parser.add_argument("--input", required=True, help="Input scoring JSONL file.")
    parser.add_argument("--output", required=True, help="Output CSV file for manual labeling.")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    records = _read_jsonl(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "document_id",
                "filename",
                "predicted_doc_type",
                "baseline_score",
                "overall_score",
                "reviewer_notes",
                "source_path",
            ],
        )
        writer.writeheader()

        for record in records:
            metadata = record.get("metadata") or {}
            labels = record.get("labels") or {}
            baseline = record.get("model_baseline") or {}
            writer.writerow(
                {
                    "document_id": record.get("document_id", ""),
                    "filename": metadata.get("filename", ""),
                    "predicted_doc_type": metadata.get("predicted_doc_type", ""),
                    "baseline_score": baseline.get("score", ""),
                    "overall_score": labels.get("overall_score", ""),
                    "reviewer_notes": labels.get("reviewer_notes", ""),
                    "source_path": metadata.get("source_path", ""),
                }
            )

    print(f"Exported label sheet to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
