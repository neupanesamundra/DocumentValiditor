import re

from services.languagetool_service import get_languagetool


def grammar_penalty(text: str) -> int:
    """
    Calculate grammar penalty score (0 = perfect, higher = worse).
    Uses LanguageTool if available, otherwise fallback heuristics.
    """
    if not text:
        return 0
    
    # First try offline LanguageTool (local server)
    lt_tool = get_languagetool()
    if lt_tool is not None:
        try:
            matches = lt_tool.check(text)
            grammar_matches = [
                m for m in matches
                if str(getattr(m, "ruleIssueType", "")).lower() in {"grammar", "misspelling", "typographical"}
            ]
            return min(20, len(grammar_matches))
        except Exception:
            pass  # Fall through to heuristic fallback
    
    # Fallback heuristic checks
    penalty = 0
    sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
    
    for s in sentences:
        words = s.split()
        token_count = len(words)
        
        # Sentence length issues
        if token_count < 3:
            penalty += 1
        if token_count > 45:
            penalty += 1
        
        # Check for missing capitalization at start of sentence
        if s and s[0].islower() and len(s) > 3:
            penalty += 1
        
        # Check for common grammar errors using regex
        lowered = s.lower()
        
        # Subject-verb agreement heuristics
        if re.search(r'\b(he|she|it)\s+go\b', lowered):
            penalty += 1  # "he go" → should be "he goes"
        if re.search(r'\b(they|we|i)\s+goes\b', lowered):
            penalty += 1  # "they goes" → should be "they go"
        
        # Double words (typo: "the the")
        if re.search(r'\b(\w+)\s+\1\b', lowered):
            penalty += 1
        
        # Missing space after comma (common extraction artifact)
        if re.search(r',[a-zA-Z]', s):
            penalty += 1
    
    # Check entire text for common issues
    lowered_text = text.lower()
    
    # Common typos
    common_typos = {
        r'\bteh\b': 'the',
        r'\badn\b': 'and',
        r'\bwhcih\b': 'which',
        r'\bthier\b': 'their',
        r'\bthats\b': "that's",
        r'\bdont\b': "don't",
        r'\bcant\b': "can't",
        r'\bwont\b': "won't",
    }
    for pattern in common_typos:
        if re.search(pattern, lowered_text):
            penalty += 1
    
    # Missing periods at end of sentences (within reason)
    sentences_end = [s for s in sentences if s and not s[-1] in '.!?']
    if len(sentences_end) > len(sentences) * 0.3:  # More than 30% missing ending punctuation
        penalty += 2
    
    return min(20, penalty)