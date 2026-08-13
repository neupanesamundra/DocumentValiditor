import textstat


def readability_score(text):
    score = textstat.flesch_reading_ease(text)

    if score > 60:
        return 5
    elif score > 30:
        return 2

    return -3
