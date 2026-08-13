"""
Document Type Classifier
Uses ML model with rule-based fallback for document type detection
"""

from config.rules import CLASSIFICATION_RULES, KEYWORD_MATCH_THRESHOLD
from services.ml_classifier_service import predict_document_type_ml


def _rule_based_classify_document(text: str) -> str:
    """
    Classify document type using keyword matching rules.
    Returns: 'Resume', 'Thesis', 'Report', 'CV', 'Cover Letter', 'Essay', 'Proposal', or 'General Document'
    """
    if not text:
        return "General Document"
    
    lowered = text.lower()
    
    # Special handling for very short documents (likely cover letters or notes)
    word_count = len(lowered.split())
    if word_count < 50:
        # Short documents are often cover letters or emails
        if "dear" in lowered and ("sincerely" in lowered or "thank you" in lowered or "best regards" in lowered):
            return "Cover Letter"
    
    proposal_score = _proposal_signal_score(lowered)
    if proposal_score >= 5:
        return "Proposal"

    best_type = "General Document"
    best_hits = 0
    
    for doc_type, keywords in CLASSIFICATION_RULES.items():
        hits = sum(keyword in lowered for keyword in keywords)
        
        # Boost scores for strong indicators
        if doc_type == "Cover Letter":
            # Strong cover letter indicators
            if "dear hiring manager" in lowered or "dear sir" in lowered or "dear madam" in lowered:
                hits += 3
            if "i am writing to apply" in lowered or "i am writing to express" in lowered:
                hits += 3
            if "sincerely" in lowered or "best regards" in lowered:
                hits += 2
                
        elif doc_type == "Resume" or doc_type == "CV":
            # Strong resume indicators
            if "work experience" in lowered or "professional experience" in lowered:
                hits += 2
            if "education" in lowered and ("university" in lowered or "college" in lowered or "degree" in lowered):
                hits += 1
            if "skills" in lowered and ("proficient" in lowered or "expertise" in lowered):
                hits += 1
                
        elif doc_type == "Thesis":
            # Strong thesis indicators
            if "abstract" in lowered and ("methodology" in lowered or "results" in lowered or "conclusion" in lowered):
                hits += 2
            if "literature review" in lowered or "research question" in lowered:
                hits += 2
                
        elif doc_type == "Report":
            # Strong report indicators
            if "executive summary" in lowered or "findings" in lowered:
                hits += 2
            if "recommendations" in lowered:
                hits += 1
                
        elif doc_type == "Proposal":
            # Strong proposal indicators
            if "proposed solution" in lowered or "deliverables" in lowered:
                hits += 2
            if "timeline" in lowered and "budget" in lowered:
                hits += 2
        
        if doc_type == "Proposal":
            hits += min(4, proposal_score // 2)

        if hits > best_hits:
            best_hits = hits
            best_type = doc_type
    
    # Apply threshold
    if best_hits >= KEYWORD_MATCH_THRESHOLD:
        return best_type
    
    # If we have some hits but below threshold, still return best match
    if best_hits > 0:
        return best_type
    
    return "General Document"


def _proposal_signal_score(lowered_text: str) -> int:
    """Score proposal-specific structure before generic academic keywords win."""
    strong_phrases = [
        "proposal title",
        "project proposal",
        "research proposal",
        "business proposal",
        "proposed solution",
        "problem statement",
        "technical approach",
        "expected outcomes",
        "expected results",
        "budget summary",
        "estimated budget",
        "resources needed",
        "work plan",
    ]
    section_terms = [
        "objectives",
        "timeline",
        "budget",
        "deliverables",
        "scope",
        "proposed activities",
        "terms and conditions",
    ]

    score = sum(2 for phrase in strong_phrases if phrase in lowered_text)
    score += sum(1 for term in section_terms if term in lowered_text)

    if "proposal" in lowered_text and any(term in lowered_text for term in ("timeline", "budget", "objectives")):
        score += 3
    if "budget" in lowered_text and "timeline" in lowered_text:
        score += 2
    if "objectives" in lowered_text and ("methodology" in lowered_text or "approach" in lowered_text):
        score += 1

    return score


def classify_document(text: str) -> str:
    """
    Main classification function.
    Tries ML model first, falls back to rule-based.
    """
    if not text:
        return "General Document"
    
    # Try ML classifier first (if available and enabled)
    try:
        ml_prediction = predict_document_type_ml(text)
        if ml_prediction and ml_prediction != "General Document":
            return ml_prediction
    except Exception as e:
        # Log error but continue with rule-based
        print(f"ML classifier error: {e}")
    
    # Fallback to rule-based classification
    return _rule_based_classify_document(text)


def get_document_type_confidence(text: str, doc_type: str) -> float:
    """
    Calculate confidence score for a specific document type.
    Returns a float between 0 and 1.
    """
    if not text:
        return 0.0
    
    lowered = text.lower()
    keywords = CLASSIFICATION_RULES.get(doc_type, [])
    
    if not keywords:
        return 0.0
    
    # Calculate hit ratio
    hits = sum(keyword in lowered for keyword in keywords)
    confidence = min(hits / len(keywords), 1.0)
    
    # Boost confidence for strong indicators
    if doc_type == "Cover Letter":
        if "dear" in lowered and ("sincerely" in lowered or "thank you" in lowered):
            confidence = min(confidence + 0.3, 1.0)
    
    return round(confidence, 2)


def suggest_document_type(text: str) -> dict:
    """
    Suggest the most likely document type with confidence scores for all types.
    Returns a dict with all types and their confidence scores.
    """
    if not text:
        return {"suggested": "General Document", "confidences": {}}
    
    confidences = {}
    for doc_type in CLASSIFICATION_RULES.keys():
        confidences[doc_type] = get_document_type_confidence(text, doc_type)
    
    # Add General Document
    general_confidence = 0.5 if max(confidences.values()) < 0.3 else 0.0
    confidences["General Document"] = general_confidence
    
    # Find suggested type
    suggested = max(confidences, key=confidences.get)
    
    return {
        "suggested": suggested,
        "confidences": confidences
    }
