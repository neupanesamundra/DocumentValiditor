from copy import deepcopy
from typing import Dict

RUBRIC_SCHEMA: Dict[str, Dict] = {
    "Resume": {
        "total": 100,
        "criteria": {
            "structure": 25,
            "content_depth": 20,
            "clarity": 15,
            "grammar": 15,
            "impact": 15,
            "formatting": 10,
        },
    },
    "Report": {
        "total": 100,
        "criteria": {
            "structure": 25,
            "analysis_quality": 25,
            "clarity": 15,
            "grammar": 15,
            "evidence": 10,
            "formatting": 10,
        },
    },
    "Thesis": {
        "total": 100,
        "criteria": {
            "structure": 20,
            "research_quality": 25,
            "analysis_quality": 20,
            "clarity": 10,
            "grammar": 10,
            "citations": 10,
            "formatting": 5,
        },
    },
    "Proposal": {
        "total": 100,
        "criteria": {
            "structure": 25,
            "content_depth": 20,
            "clarity": 15,
            "grammar": 15,
            "feasibility": 15,
            "formatting": 10,
        },
    },
    "General Document": {
        "total": 100,
        "criteria": {
            "structure": 25,
            "content_depth": 25,
            "clarity": 20,
            "grammar": 15,
            "formatting": 15,
        },
    },
}


def get_rubric(doc_type: str) -> Dict:
    return deepcopy(RUBRIC_SCHEMA.get(doc_type, RUBRIC_SCHEMA["General Document"]))


def empty_label_payload(doc_type: str) -> Dict:
    rubric = get_rubric(doc_type)
    return {
        "overall_score": None,
        "criterion_scores": {key: None for key in rubric["criteria"]},
        "reviewer_notes": "",
    }
