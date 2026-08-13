from services.ai_explainer import generate_explanation_with_ai


def evaluate_status(score: int) -> str:
    """Return short status label"""
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 55:
        return "Needs Improvement"
    return "Needs Revision"


def get_status_message(score: int) -> str:
    """Return detailed status message for display"""
    if score >= 85:
        return "Document is professional and ready for submission"
    if score >= 70:
        return "Minor improvements may enhance quality"
    if score >= 55:
        return "Significant revisions recommended"
    return "Major revision required"


def _generate_rule_based_explanation(score: int, analysis: list[str], suggestions: list[str]) -> list[str]:
    lines = [f"Overall quality score: {score}/100 ({evaluate_status(score)})."]

    if analysis:
        lines.extend(analysis[:6])
    else:
        lines.append("No critical structural issues detected.")

    if suggestions:
        lines.append("Priority action: " + suggestions[0])

    return lines


def generate_explanation(
    score: int,
    analysis: list[str],
    suggestions: list[str],
    doc_type: str = "General Document",
) -> tuple[list[str], str]:
    ai_response = generate_explanation_with_ai(score, doc_type, analysis, suggestions)
    if ai_response.ok and ai_response.content:
        return (
            [f"Overall quality score: {score}/100 ({evaluate_status(score)}).", ai_response.content],
            f"AI explanation: used ({ai_response.provider}:{ai_response.model}).",
        )

    reason = ai_response.error or "unknown reason"
    return (
        _generate_rule_based_explanation(score, analysis, suggestions),
        f"AI explanation: fallback used ({reason}).",
    )