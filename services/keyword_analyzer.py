from config.rules import KEYWORDS_FOR_RICHNESS


def keyword_score(text):
    lowered = text.lower()
    return sum(keyword in lowered for keyword in KEYWORDS_FOR_RICHNESS)
