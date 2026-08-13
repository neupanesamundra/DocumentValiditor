from pathlib import Path

import re

from docx import Document
from config.rules import REQUIRED_SECTION_MAP
from models.analysis_result import ScoreDetail
from services.ml_scoring_service import predict_score_ml
from services.formatting_analyzer import formatting_penalty
from services.grammar_checker import grammar_penalty
from services.keyword_analyzer import keyword_score
from services.readability_analyzer import readability_score

DOC_TYPE_REQUIRED_TERMS = {
    "Report": ["abstract", "introduction", "methodology", "conclusion", "references"],
    "Thesis": ["abstract", "introduction", "methodology", "conclusion", "references"],
    "Resume": ["education", "experience", "skills"],
    "CV": ["education", "experience", "skills"],
    "Cover Letter": ["dear"],
    "Essay": ["introduction", "conclusion"],
    "Proposal": ["introduction", "objectives", "methodology", "timeline", "budget", "conclusion"],
}

SECTION_EQUIVALENTS = {
    "professional summary": {"professional summary", "summary", "objective", "profile"},
    "work experience": {"work experience", "experience", "employment", "employment history", "work history"},
    "experience": {"work experience", "experience", "employment", "employment history", "work history"},
    "skills": {"skills", "technical skills", "technical skill", "soft skills", "soft skill", "key skills"},
    "technical skills": {"skills", "technical skills", "technical skill", "key skills"},
    "education": {"education", "education and qualifications", "academic background", "qualifications"},
    "certifications": {"certifications", "certification", "certificates", "certificate"},
    "projects": {"projects", "project"},
    "relevant coursework": {"relevant coursework", "coursework"},
    "document details": {"document details", "proposal title", "prepared by", "date"},
    "executive summary": {"executive summary", "summary"},
    "introduction": {"introduction", "background", "overview"},
    "problem statement": {"problem statement", "statement of the problem", "background of the problem"},
    "objectives": {"objectives", "objective", "aims", "goals", "purpose"},
    "methodology": {"methodology", "methods", "approach", "technical approach", "proposed methodology", "plan/method"},
    "technical approach": {"technical approach", "approach", "implementation approach", "proposed solution", "methodology", "methods", "plan/method", "proposed activities"},
    "timeline": {"timeline", "schedule", "work plan", "project plan"},
    "budget": {"budget", "budget summary", "estimated budget", "cost estimate", "resources needed", "resources required"},
    "expected outcomes": {"expected outcomes", "expected outcome", "outcomes", "expected results", "deliverables", "outputs"},
    "conclusion": {"conclusion", "conclusions", "closing"},
}

MONTH_PATTERN = r"(?:january|february|march|april|may|june|july|august|september|october|november|december)"


def _dedupe_keep_order(items):
    seen = set()
    out = []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _score_required_terms(text: str, profile_doc_type: str, sections: list[str]):
    lowered = (text or "").lower()
    required = DOC_TYPE_REQUIRED_TERMS.get(profile_doc_type, [])
    section_names = {s.lower() for s in sections}

    if profile_doc_type in REQUIRED_SECTION_MAP and profile_doc_type != "Cover Letter":
        required = list(dict.fromkeys(required + [s.lower() for s in REQUIRED_SECTION_MAP.get(profile_doc_type, [])]))

    if not required:
        return 30, [], [], [ScoreDetail(label="Section Coverage", points=30, kind="base")]

    found = []
    for term in required:
        equivalents = SECTION_EQUIVALENTS.get(term, {term})
        if any(eq in lowered or eq in section_names for eq in equivalents):
            found.append(term)
    missing = [term for term in required if term not in found]

    ratio = len(found) / len(required)
    max_points = 20 if profile_doc_type == "Cover Letter" else 60
    points = int(round(ratio * max_points))

    analysis = [f"Required sections found: {len(found)}/{len(required)}."]
    suggestions = []
    if missing:
        suggestions.append("Add missing sections: " + ", ".join(missing) + ".")

    breakdown = [
        ScoreDetail(label="Section Coverage", points=points, kind="bonus"),
    ]

    return points, analysis, suggestions, breakdown


def _docx_heading_hierarchy_adjustment(source_path: str | Path | None) -> tuple[int, list[str], list[ScoreDetail]]:
    if not source_path:
        return 0, [], []

    path = Path(source_path)
    if path.suffix.lower() != ".docx" or not path.exists():
        return 0, [], []

    try:
        doc = Document(path)
    except Exception:
        return 0, [], []

    samples: list[tuple[int, float]] = []
    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if not text:
            continue

        level = None
        if re.match(r"^\d+\.\d+\.\d+\s+", text):
            level = 3
        elif re.match(r"^\d+\.\d+\s+", text):
            level = 2
        elif re.match(r"^\d+\.\s+", text):
            level = 1

        if level is None:
            continue

        run_sizes = [r.font.size.pt for r in p.runs if getattr(r.font, "size", None) is not None]
        if not run_sizes:
            continue

        avg = sum(run_sizes) / len(run_sizes)
        samples.append((level, avg))

    if len(samples) < 2:
        return 0, [], []

    l1 = [sz for lvl, sz in samples if lvl == 1]
    l2 = [sz for lvl, sz in samples if lvl == 2]
    l3 = [sz for lvl, sz in samples if lvl == 3]

    if not l1 or not l2:
        return 0, [], []

    avg1 = sum(l1) / len(l1)
    avg2 = sum(l2) / len(l2)
    avg3 = (sum(l3) / len(l3)) if l3 else None

    violations = 0
    if avg1 <= avg2:
        violations += 1
    if avg3 is not None and avg2 <= avg3:
        violations += 1

    if violations == 0:
        return 4, ["Heading hierarchy is visually consistent."], [ScoreDetail(label="DOCX Heading Hierarchy", points=4, kind="bonus")]

    penalty = -min(6, violations * 3)
    return penalty, ["Heading hierarchy size inconsistency detected."], [ScoreDetail(label="DOCX Heading Hierarchy", points=penalty, kind="penalty")]


def _score_quality(text: str):
    wc = _word_count(text)
    score = 30
    analysis = []
    suggestions = []
    breakdown = [ScoreDetail(label="Quality Base", points=30, kind="base")]

    if wc < 120:
        score -= 8
        analysis.append(f"Low content volume ({wc} words).")
        suggestions.append("Increase useful detail in core sections.")
        breakdown.append(ScoreDetail(label="Content Volume", points=-8, kind="penalty"))
    elif wc > 350:
        score += 4
        breakdown.append(ScoreDetail(label="Content Volume", points=4, kind="bonus"))

    g_cut = min(16, grammar_penalty(text) * 2)
    if g_cut:
        score -= g_cut
        analysis.append("Grammar and sentence-quality issues detected.")
        suggestions.append("Correct grammar and sentence structure.")
        breakdown.append(ScoreDetail(label="Grammar", points=-g_cut, kind="penalty"))

    f_cut = min(12, formatting_penalty(text) * 2)
    if f_cut:
        score -= f_cut
        analysis.append("Formatting inconsistencies detected.")
        suggestions.append("Use consistent spacing, bullets, and headings.")
        breakdown.append(ScoreDetail(label="Formatting", points=-f_cut, kind="penalty"))

    r_points = readability_score(text)
    score += r_points
    breakdown.append(ScoreDetail(label="Readability", points=r_points, kind="bonus" if r_points >= 0 else "penalty"))

    k_points = min(6, keyword_score(text))
    if k_points:
        score += k_points
        breakdown.append(ScoreDetail(label="Keyword Relevance", points=k_points, kind="bonus"))

    return score, analysis, suggestions, breakdown


def _score_cover_letter_specifics(text: str):
    lowered = (text or "").lower()
    wc = _word_count(text)
    score = 0
    analysis = []
    suggestions = []
    breakdown = []

    top_lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    header_lines = top_lines[:12]
    header_text = "\n".join(header_lines).lower()
    full_lines = [line.strip() for line in (text or "").splitlines()]
    has_sender_placeholder = "[sender information:" in lowered
    has_date_placeholder = "[date:" in lowered
    has_recipient_placeholder = "[recipient information:" in lowered

    date_pattern = rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{MONTH_PATTERN},?\s+\d{{4}}\b|\b{MONTH_PATTERN}\b\s+\d{{1,2}},?\s+\d{{4}}\b"
    has_date = bool(re.search(date_pattern, lowered))
    has_sender_contact = bool(
        re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", header_text)
        or re.search(r"\+?\d[\d\s().-]{7,}\d", header_text)
        or any("," in line and len(line.split()) <= 6 for line in header_lines[:4])
    )
    has_recipient = bool(
        re.search(r"\b(hiring manager|recruiter|human resources|hr manager|talent acquisition)\b", header_text)
        or re.search(r"\b(inc|corp|corporation|company|llc|ltd|university|college|school|hospital|bank)\b", header_text)
        or "to whom it may concern" in header_text
    )
    has_subject = bool(re.search(r"(?mi)^\s*subject\s*:", text or ""))
    has_salutation = bool(re.search(r"\bdear\s+[a-z]", lowered))
    has_closing = bool(re.search(r"\b(sincerely|best regards|respectfully|kind regards)\b", lowered))
    has_signature_name = False
    for idx, line in enumerate(full_lines):
        if re.fullmatch(r"\s*(sincerely|best regards|respectfully|kind regards)\s*,?\s*", line, flags=re.I):
            for next_line in full_lines[idx + 1 : idx + 4]:
                candidate = next_line.strip()
                if re.fullmatch(r"[A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,3}", candidate):
                    has_signature_name = True
                    break
            break

    structure_checks = [
        (
            "Sender Information",
            has_sender_contact,
            4,
            -3,
            has_sender_placeholder,
            "Cover letter sender information is incomplete.",
            "Add your contact details or address block near the top.",
        ),
        (
            "Date",
            has_date,
            4,
            -4,
            has_date_placeholder,
            "Cover letter date line not clearly detected.",
            "Add a full date line near the top of the cover letter.",
        ),
        (
            "Recipient Information",
            has_recipient,
            4,
            -4,
            has_recipient_placeholder,
            "Recipient or company information is missing.",
            "Add the hiring manager name and company information before the salutation.",
        ),
        (
            "Subject Line",
            has_subject,
            2,
            0,
            False,
            "",
            "",
        ),
        (
            "Salutation",
            has_salutation,
            5,
            -6,
            False,
            "Cover letter salutation is missing or weak.",
            "Add a professional salutation such as Dear Hiring Manager:.",
        ),
        (
            "Closing",
            has_closing,
            4,
            -2,
            False,
            "Cover letter closing is missing.",
            "End the letter with a professional closing such as Sincerely,.",
        ),
        (
            "Signature Name",
            has_signature_name,
            3,
            -1,
            False,
            "Sender name is not clearly shown after the closing.",
            "Place your full name on its own line after the closing.",
        ),
    ]

    for label, present, bonus, penalty, placeholder_only, analysis_msg, suggestion_msg in structure_checks:
        if present:
            if bonus:
                score += bonus
                breakdown.append(ScoreDetail(label=label, points=bonus, kind="bonus"))
        else:
            if placeholder_only:
                breakdown.append(ScoreDetail(label=label, points=0, kind="informational"))
                continue
            if penalty:
                score += penalty
                breakdown.append(ScoreDetail(label=label, points=penalty, kind="penalty"))
            if analysis_msg:
                analysis.append(analysis_msg)
            if suggestion_msg:
                suggestions.append(suggestion_msg)

    if re.search(r"\b(sincerely|best regards|respectfully|kind regards)\b", lowered) or re.search(
        r"\b(thank you for your consideration|thank you for considering my application|thank you for considering)\b",
        lowered,
    ):
        score += 2
        breakdown.append(ScoreDetail(label="Closing Tone", points=2, kind="bonus"))

    if re.search(r"\b(apply|applying|application)\b", lowered) and re.search(r"\b(position|role|opportunity|job)\b", lowered):
        score += 7
        breakdown.append(ScoreDetail(label="Application Intent", points=7, kind="bonus"))
    else:
        analysis.append("Opening paragraph does not clearly state the job being applied for.")
        suggestions.append("State the exact role you are applying for in the opening paragraph.")
        breakdown.append(ScoreDetail(label="Application Intent", points=-6, kind="penalty"))
        score -= 6

    if re.search(r"\b\d+%|\b\d+\+|\b\d+\b", text):
        score += 6
        breakdown.append(ScoreDetail(label="Specific Achievements", points=6, kind="bonus"))
    else:
        analysis.append("Cover letter lacks specific quantified achievements.")
        suggestions.append("Include one or two specific achievements or measurable results.")
        breakdown.append(ScoreDetail(label="Specific Achievements", points=-4, kind="penalty"))
        score -= 4

    if wc < 150:
        analysis.append(f"Cover letter is too short ({wc} words).")
        suggestions.append("Expand the letter into a complete one-page structure with 3 to 4 paragraphs.")
        breakdown.append(ScoreDetail(label="Length Suitability", points=-6, kind="penalty"))
        score -= 6
    elif wc > 500:
        analysis.append(f"Cover letter is too long ({wc} words).")
        suggestions.append("Shorten the cover letter to a focused one-page letter.")
        breakdown.append(ScoreDetail(label="Length Suitability", points=-6, kind="penalty"))
        score -= 6
    else:
        score += 4
        breakdown.append(ScoreDetail(label="Length Suitability", points=4, kind="bonus"))

    if re.search(r"(?m)^\s*[-*•]\s+", text):
        analysis.append("Cover letter contains bullet points, which weakens formal letter format.")
        suggestions.append("Convert bullet points into formal paragraphs for cover letters.")
        breakdown.append(ScoreDetail(label="Letter Format", points=-8, kind="penalty"))
        score -= 8
    else:
        score += 4
        breakdown.append(ScoreDetail(label="Letter Format", points=4, kind="bonus"))

    if re.search(r"\b(hey|hello there|hi there)\b", lowered):
        analysis.append("Tone appears too casual for a formal cover letter.")
        suggestions.append("Use a professional and confident tone throughout the letter.")
        breakdown.append(ScoreDetail(label="Professional Tone", points=-4, kind="penalty"))
        score -= 4
    else:
        score += 2
        breakdown.append(ScoreDetail(label="Professional Tone", points=2, kind="bonus"))

    return score, analysis, suggestions, breakdown


def extract_scoring_features(text, profile_doc_type, sections, source_path=None):
    sections = sections or []
    lowered = (text or "").lower()
    required = DOC_TYPE_REQUIRED_TERMS.get(profile_doc_type, [])

    if profile_doc_type in REQUIRED_SECTION_MAP:
        required = list(dict.fromkeys(required + [s.lower() for s in REQUIRED_SECTION_MAP.get(profile_doc_type, [])]))

    section_names = {s.lower() for s in sections}
    found = [
        term
        for term in required
        if any(eq in lowered or eq in section_names for eq in SECTION_EQUIVALENTS.get(term, {term}))
    ]
    grammar_raw = grammar_penalty(text)
    formatting_raw = formatting_penalty(text)
    readability_value = readability_score(text)
    keyword_value = keyword_score(text)
    heading_adj, _analysis, _breakdown = _docx_heading_hierarchy_adjustment(source_path)

    return {
        "doc_type": profile_doc_type,
        "word_count": _word_count(text),
        "char_count": len(text or ""),
        "section_count": len(sections),
        "required_terms_total": len(required),
        "required_terms_found": len(found),
        "required_terms_ratio": round(len(found) / max(1, len(required)), 3) if required else 1.0,
        "grammar_penalty_raw": grammar_raw,
        "formatting_penalty_raw": formatting_raw,
        "readability_score_value": readability_value,
        "keyword_score_value": keyword_value,
        "heading_hierarchy_adjustment": heading_adj,
    }


def score_document(text, profile_doc_type, sections, requirement_profile=None, file_extension=None, source_path=None):
    sections = sections or []

    section_score, a1, s1, b1 = _score_required_terms(text, profile_doc_type, sections)
    quality_score, a2, s2, b2 = _score_quality(text)
    rule_based_score = section_score + quality_score

    score = rule_based_score
    analysis = a1 + a2
    suggestions = s1 + s2
    breakdown = b1 + b2

    if profile_doc_type == "Cover Letter":
        cover_score, cover_analysis, cover_suggestions, cover_breakdown = _score_cover_letter_specifics(text)
        score += cover_score
        analysis.extend(cover_analysis)
        suggestions.extend(cover_suggestions)
        breakdown.extend(cover_breakdown)

    docx_adj, docx_analysis, docx_breakdown = _docx_heading_hierarchy_adjustment(source_path)
    if docx_adj:
        score += docx_adj
        analysis.extend(docx_analysis)
        breakdown.extend(docx_breakdown)

    if requirement_profile:
        required_sections = requirement_profile.get("required_sections") or []
        if required_sections and profile_doc_type != "Cover Letter":
            lowered = (text or "").lower()
            section_names = {s.lower() for s in sections}
            missing = []
            for sec in required_sections:
                normalized = sec.lower()
                equivalents = SECTION_EQUIVALENTS.get(normalized, {normalized})
                if not any(eq in lowered or eq in section_names for eq in equivalents):
                    missing.append(sec)
            if missing:
                penalty = min(12, len(missing) * 3)
                score -= penalty
                suggestions.append("Requirement sections missing: " + ", ".join(missing) + ".")
                breakdown.append(ScoreDetail(label="Requirement Section Check", points=-penalty, kind="penalty"))
            else:
                score += 4
                breakdown.append(ScoreDetail(label="Requirement Section Check", points=4, kind="bonus"))

    score = max(0, min(100, score))
    analysis = _dedupe_keep_order(analysis)
    suggestions = _dedupe_keep_order(suggestions)

    ml_features = extract_scoring_features(text, profile_doc_type, sections, source_path=source_path)
    ml_score = predict_score_ml(ml_features)
    if ml_score is not None:
        ml_score = max(0, min(100, int(round(ml_score))))
        if profile_doc_type == "Cover Letter":
            score = max(0, min(100, int(round(score))))
        else:
            score = max(score, ml_score)
        analysis.insert(0, "ML scoring model applied using document quality features.")
        breakdown.append(ScoreDetail(label="ML Score Prediction", points=ml_score, kind="informational"))

    return score, analysis, suggestions, breakdown
