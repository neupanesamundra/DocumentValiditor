def formatting_penalty(text: str) -> int:
    """
    Calculate formatting penalty score (0 = perfect, higher = worse).
    
    Checks:
    - Double/multiple spaces
    - Tabs instead of spaces
    - Too few line breaks (dense text)
    - Excessive blank lines
    - Inconsistent spacing after periods
    """
    if not text:
        return 0
    
    penalty = 0
    
    # Double or multiple spaces
    if '  ' in text:
        # Count severity - more double spaces = higher penalty
        double_space_count = text.count('  ')
        penalty += min(5, double_space_count)  # Cap at 5
    
    # Tabs (usually from PDF extraction artifacts)
    if '\t' in text:
        penalty += 2
    
    # Too few line breaks for long text
    line_count = text.count('\n') + 1
    word_count = len(text.split())
    
    if word_count > 200 and line_count < 10:
        penalty += 3
    elif word_count > 100 and line_count < 5:
        penalty += 2
    
    # Excessive blank lines (3+ consecutive newlines)
    if '\n\n\n' in text:
        penalty += 2
    
    # Inconsistent spacing after periods (common in extracted text)
    import re
    if re.search(r'\. [a-z]', text):  # period + single space + lowercase
        pass  # This is correct
    if re.search(r'\.  [A-Z]', text):  # period + double space + uppercase
        pass  # Acceptable but old style
    if re.search(r'\. [A-Z]', text) and re.search(r'\.  [A-Z]', text):
        # Mixed spacing styles
        penalty += 1
    
    return min(10, penalty)  # Cap total penalty