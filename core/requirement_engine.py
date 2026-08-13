import re
from typing import Dict, List, Tuple

from config.rules import REQUIRED_SECTION_MAP

DOC_TYPE_PROFILE_MAP = {
    "Resume": "Resume",
    "CV": "CV",
    "Thesis": "Thesis",
    "Research Paper": "Thesis",
    "Report": "Report",
    "Memo": "Report",
    "Cover Letter": "Cover Letter",
    "Essay": "Essay",
    "Proposal": "Proposal",
    "Letter": "Cover Letter",
    "General Document": "General Document",
}

DEFAULT_REQUIREMENTS_BY_PROFILE = {
    "Resume": {
        "preferred_formats": ["pdf", "docx"],
        "validation_terms": ["grammar", "readability", "formatting", "keywords", "sections"],
        "min_words": 120,
    },
    "Thesis": {
        "preferred_formats": ["pdf", "docx"],
        "validation_terms": ["grammar", "readability", "formatting", "sections", "references"],
        "min_words": 600,
    },
    "Report": {
        "preferred_formats": ["pdf", "docx"],
        "validation_terms": ["grammar", "readability", "formatting", "analysis", "sections"],
        "min_words": 300,
    },
    "Cover Letter": {
        "preferred_formats": ["pdf", "docx"],
        "validation_terms": ["grammar", "readability", "formatting", "sections"],
        "min_words": 180,
    },
    "Essay": {
        "preferred_formats": ["pdf", "docx"],
        "validation_terms": ["grammar", "readability", "formatting", "sections"],
        "min_words": 400,
    },
    "Proposal": {
        "preferred_formats": ["pdf", "docx"],
        "validation_terms": ["grammar", "readability", "formatting", "analysis", "sections"],
        "min_words": 500,
    },
    "General Document": {
        "preferred_formats": ["pdf", "docx", "txt"],
        "validation_terms": ["grammar", "readability", "formatting"],
        "min_words": 150,
    },
}

VALIDATION_TERM_PATTERNS = {
    "grammar": [r"\bgrammar\b", r"\bsentence\b"],
    "readability": [r"\breadability\b", r"\bclarity\b", r"\bclear\b"],
    "formatting": [r"\bformat(?:ting)?\b", r"\blayout\b", r"\bstyle\b"],
    "keywords": [r"\bkeyword(?:s)?\b", r"\bterms?\b"],
    "sections": [r"\bsection(?:s)?\b", r"\bheadings?\b", r"\bstructure\b"],
    "references": [r"\breferences?\b", r"\bcitations?\b", r"\bbibliography\b"],
    "analysis": [r"\banalysis\b", r"\bfindings?\b"],
}

KNOWN_SECTION_TERMS = {
    "Abstract": [r"\babstract\b"],
    "Introduction": [r"\bintroduction\b"],
    "Methodology": [r"\bmethodology\b", r"\bmethods?\b"],
    "Analysis": [r"\banalysis\b"],
    "Conclusion": [r"\bconclusion\b"],
    "References": [r"\breferences?\b", r"\bbibliography\b"],
    "Professional Summary": [r"\bprofessional summary\b", r"\bsummary\b", r"\bobjective\b"],
    "Experience": [r"\bexperience\b", r"\bemployment\b", r"\bwork experience\b"],
    "Education": [r"\beducation\b", r"\bacademic\b"],
    "Technical Skills": [r"\btechnical skills\b", r"\bskills\b"],
    "Projects": [r"\bprojects?\b"],
    "Executive Summary": [r"\bexecutive summary\b"],
    "Problem Statement": [r"\bproblem statement\b", r"\bstatement of the problem\b"],
    "Objectives": [r"\bobjectives?\b", r"\baims?\b", r"\bgoals?\b"],
    "Technical Approach": [r"\btechnical approach\b", r"\bproposed solution\b", r"\bimplementation approach\b"],
    "Timeline": [r"\btimeline\b", r"\bschedule\b", r"\bwork plan\b"],
    "Budget": [r"\bbudget\b", r"\bcost estimate\b", r"\bresources needed\b"],
    "Expected Outcomes": [r"\bexpected outcomes?\b", r"\bexpected results?\b", r"\bdeliverables\b"],
}


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    output = []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            output.append(item.strip())
    return output


def resolve_document_type(selected_doc_type: str, classified_doc_type: str) -> Tuple[str, str]:
    selected = (selected_doc_type or "").strip()
    if not selected or selected == "Auto Detect":
        display = classified_doc_type
    else:
        display = selected
    profile = DOC_TYPE_PROFILE_MAP.get(display, "General Document")
    return display, profile


def build_default_requirements(profile_doc_type: str) -> Dict:
    base = DEFAULT_REQUIREMENTS_BY_PROFILE.get(profile_doc_type, DEFAULT_REQUIREMENTS_BY_PROFILE["General Document"])
    default_sections = REQUIRED_SECTION_MAP.get(profile_doc_type, [])
    return {
        "source": "default",
        "preferred_formats": list(base["preferred_formats"]),
        "validation_terms": list(base["validation_terms"]),
        "required_sections": list(default_sections),
        "min_words": base["min_words"],
    }


def _extract_preferred_formats(text_lower: str) -> List[str]:
    formats = []
    for fmt in ("pdf", "docx", "txt"):
        if re.search(rf"\b{fmt}\b", text_lower):
            formats.append(fmt)
    return formats


def _extract_validation_terms(text_lower: str) -> List[str]:
    terms = []
    for term, patterns in VALIDATION_TERM_PATTERNS.items():
        if any(re.search(pattern, text_lower) for pattern in patterns):
            terms.append(term)
    return terms


def _extract_min_words(text_lower: str):
    match = re.search(r"(?:at\s+least|minimum|min)\D{0,10}(\d{2,5})\s+words?", text_lower)
    if match:
        return int(match.group(1))
    return None


def _extract_required_sections(text_lower: str) -> List[str]:
    sections = []
    for section_name, patterns in KNOWN_SECTION_TERMS.items():
        if any(re.search(pattern, text_lower) for pattern in patterns):
            sections.append(section_name)
    return sections


def parse_custom_requirements(requirements_text: str) -> Dict:
    raw = (requirements_text or "").strip()
    if not raw:
        return {}

    text_lower = raw.lower()
    return {
        "source": "user",
        "preferred_formats": _extract_preferred_formats(text_lower),
        "validation_terms": _extract_validation_terms(text_lower),
        "required_sections": _extract_required_sections(text_lower),
        "min_words": _extract_min_words(text_lower),
    }


def merge_requirements(default_profile: Dict, custom_profile: Dict) -> Dict:
    if not custom_profile:
        return default_profile

    merged = dict(default_profile)
    merged["source"] = "user"
    for key in ("preferred_formats", "validation_terms", "required_sections"):
        values = custom_profile.get(key) or default_profile.get(key) or []
        merged[key] = _dedupe_keep_order(values)
    merged["min_words"] = custom_profile.get("min_words") or default_profile.get("min_words")
    return merged


def summarize_requirements(display_doc_type: str, profile_doc_type: str, requirements: Dict) -> List[str]:
    lines = []
    if display_doc_type == profile_doc_type:
        lines.append(f"Document type selected: {display_doc_type}.")
    else:
        lines.append(f"Document type selected: {display_doc_type} (validated with {profile_doc_type} rules).")

    source = requirements.get("source", "default")
    lines.append("Requirement source: User-provided requirements." if source == "user" else "Requirement source: Default system requirements.")

    formats = requirements.get("preferred_formats") or []
    if formats:
        lines.append("Preferred formats: " + ", ".join(fmt.upper() for fmt in formats) + ".")

    terms = requirements.get("validation_terms") or []
    if terms:
        lines.append("Validation terms: " + ", ".join(term.title() for term in terms) + ".")

    min_words = requirements.get("min_words")
    if min_words:
        lines.append(f"Minimum length requirement: {min_words} words.")

    sections = requirements.get("required_sections") or []
    if sections:
        lines.append("Required sections: " + ", ".join(sections) + ".")

    return lines
