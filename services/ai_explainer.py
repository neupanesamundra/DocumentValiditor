from config.settings import AI_EXPLANATION_TEMPERATURE
from services.ai_client import AIResponse, request_text_completion


def build_explanation_prompt(
    score: int,
    doc_type: str,
    analysis: list[str],
    suggestions: list[str],
) -> str:
    analysis_lines = "\n".join(f"- {line}" for line in analysis[:8]) or "- No analysis provided."
    suggestion_lines = "\n".join(f"- {line}" for line in suggestions[:8]) or "- No suggestions provided."
    return (
        f"Document type: {doc_type}\n"
        f"Score: {score}/100\n"
        "Task: Write a short, polished explanation of the document quality.\n"
        "Rules:\n"
        "- Be clear, professional, and constructive.\n"
        "- Explain the main strengths and weaknesses.\n"
        "- Include the highest-priority next step.\n"
        "- Keep it concise and suitable for a results page.\n"
        "- Return plain text only.\n\n"
        "Analysis points:\n"
        f"{analysis_lines}\n\n"
        "Suggestions:\n"
        f"{suggestion_lines}"
    )


def generate_explanation_with_ai(
    score: int,
    doc_type: str,
    analysis: list[str],
    suggestions: list[str],
) -> AIResponse:
    system_prompt = (
        "You are an academic and professional writing evaluator. "
        "You explain document quality clearly and give constructive, realistic guidance."
    )
    user_prompt = build_explanation_prompt(score, doc_type, analysis, suggestions)
    return request_text_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=AI_EXPLANATION_TEMPERATURE,
    )
