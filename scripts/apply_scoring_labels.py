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


def _read_csv_labels(path: Path) -> dict[str, dict]:
    updates: dict[str, dict] = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            document_id = (row.get("document_id") or "").strip()
            if not document_id:
                continue
            updates[document_id] = row
    return updates


def _parse_optional_score(value: str) -> int | None:
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    return int(float(cleaned))


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply CSV scoring labels back into a JSONL training file.")
    parser.add_argument("--jsonl", required=True, help="Original scoring JSONL file.")
    parser.add_argument("--csv", required=True, help="Completed CSV label sheet.")
    parser.add_argument("--output", required=True, help="Output JSONL file with updated labels.")
    args = parser.parse_args()

    jsonl_path = Path(args.jsonl).resolve()
    csv_path = Path(args.csv).resolve()
    output_path = Path(args.output).resolve()

    if not jsonl_path.exists():
        raise SystemExit(f"JSONL file not found: {jsonl_path}")
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    records = _read_jsonl(jsonl_path)
    updates = _read_csv_labels(csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            document_id = record.get("document_id")
            update = updates.get(document_id)
            if update:
                labels = record.setdefault("labels", {})
                labels["overall_score"] = _parse_optional_score(update.get("overall_score", ""))
                labels["reviewer_notes"] = update.get("reviewer_notes", "")
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Applied CSV labels and wrote updated JSONL to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
