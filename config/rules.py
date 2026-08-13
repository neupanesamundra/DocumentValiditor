"""
Document Validation Rules Configuration
Supports autocorrect, scoring, and document enhancement
"""

from typing import Dict, List, Set, Tuple

# ============================================
# FILE HANDLING
# ============================================

ALLOWED_EXTENSIONS: Set[str] = {"pdf", "docx", "txt"}
MAX_FILE_SIZE_MB: int = 10
KEYWORD_MATCH_THRESHOLD: int = 2

# ============================================
# DOCUMENT CLASSIFICATION RULES
# ============================================

CLASSIFICATION_RULES: Dict[str, List[str]] = {
    "Resume": ["skills", "experience", "education", "work history", "employment"],
    "Thesis": ["abstract", "methodology", "references", "literature review", "research"],
    "Report": ["introduction", "conclusion", "analysis", "findings", "executive summary"],
    "CV": ["curriculum vitae", "publications", "education", "experience", "research"],
    "Cover Letter": ["dear", "sincerely", "position", "hiring manager", "enclosed"],
    "Essay": ["thesis statement", "argument", "conclusion", "references"],
    "Proposal": [
        "proposal", "proposed", "objective", "objectives", "scope", "timeline",
        "budget", "deliverables", "problem statement", "action plan",
        "resources needed", "success metrics", "executive summary", "conclusion", "request",
        "smart", "specific", "measurable", "achievable", "relevant", "time-bound",
    ],
}

# ============================================
# REQUIRED SECTIONS (for scoring validation)
# ============================================

REQUIRED_SECTIONS_FOR_SCORING: Dict[str, Tuple[str, int, str, str]] = {
    "Resume": ("skills", 10, "Missing Skills Section", "Add a Skills section with your technical and soft skills"),
    "Thesis": ("abstract", 10, "Missing Abstract", "Include an Abstract summarizing your research"),
    "Report": ("conclusion", 8, "Missing Conclusion", "Add a Conclusion section with key findings"),
    "Cover Letter": ("body", 10, "Missing Body Paragraphs", "Add paragraphs explaining your interest and qualifications"),
    "CV": ("experience", 10, "Missing Experience", "Add Work Experience section"),
    "Essay": ("thesis statement", 10, "Missing Thesis Statement", "Add a clear thesis statement"),
    "Proposal": ("objectives", 10, "Missing Objectives", "Add clear, SMART objectives with specific targets and deadlines"),
}

# ============================================
# COMPLETE REQUIRED SECTION MAP (for autocorrect to ADD missing sections)
# ============================================

REQUIRED_SECTION_MAP: Dict[str, List[str]] = {
    "Resume": [
        "Professional Summary",
        "Skills",
        "Work Experience",
        "Education",
    ],
    "Thesis": [
        "Abstract",
        "Introduction",
        "Literature Review",
        "Methodology",
        "Results",
        "Discussion",
        "Conclusion",
        "References",
    ],
    "Report": [
        "Executive Summary",
        "Introduction",
        "Findings",
        "Analysis",
        "Recommendations",
        "Conclusion",
        "References",
    ],
    "CV": [
        "Professional Summary",
        "Skills",
        "Work Experience",
        "Education",
        "Publications",
        "Certifications",
    ],
    "Cover Letter": [
        "Contact Information",
        "Date",
        "Salutation",
        "Opening Paragraph (Interest in Role)",
        "Skills & Qualifications Paragraph",
        "Company Interest Paragraph",
        "Call to Action",
        "Closing",
        "Signature",
    ],
    "Essay": [
        "Introduction",
        "Thesis Statement",
        "Body Paragraphs",
        "Conclusion",
        "References",
    ],
    "Proposal": [
        "Title",
        "Executive Summary",
        "Problem Statement",
        "Objectives",
        "Action Plan",
        "Resources Needed",
        "Budget",
        "Timeline",
        "Success Metrics",
        "Conclusion & Request",
    ],
    "General Document": [
        "Introduction",
        "Body",
        "Conclusion",
    ],
}

# ============================================
# SECTION PATTERNS FOR DETECTION (regex patterns)
# ============================================

SECTION_PATTERNS: Dict[str, List[str]] = {
    "Professional Summary": [
        r"\b(professional\s+summary|summary|objective|profile|about me)\b"
    ],
    "Skills": [
        r"\b(skills|technical skills|core competencies|qualifications)\b"
    ],
    "Work Experience": [
        r"\b(experience|work experience|employment|work history|internships?)\b"
    ],
    "Education": [
        r"\b(education|academic background|qualifications|degrees?)\b"
    ],
    "Projects": [
        r"\b(projects?|key projects?|portfolio)\b"
    ],
    "Certifications": [
        r"\b(certifications?|certificates?|licenses?)\b"
    ],
    "Publications": [
        r"\b(publications?|papers?|research papers?)\b"
    ],
    "References": [
        r"\b(references?|referees?)\b"
    ],
    "Abstract": [
        r"\b(abstract|summary|synopsis)\b"
    ],
    "Introduction": [
        r"\b(introduction|background|overview)\b"
    ],
    "Methodology": [
        r"\b(methodology|methods|approach|implementation|technical\s+approach|proposed\s+methodology)\b"
    ],
    "Problem Statement": [
        r"\b(problem\s+statement|statement\s+of\s+the\s+problem|background\s+of\s+the\s+problem)\b"
    ],
    "Objectives": [
        r"\b(objectives?|aims?|goals?)\b"
    ],
    "Timeline": [
        r"\b(timeline|schedule|work\s+plan|project\s+plan)\b"
    ],
    "Budget": [
        r"\b(budget|budget\s+summary|estimated\s+budget|cost\s+estimate|resources\s+needed|resources\s+required)\b"
    ],
    "Expected Outcomes": [
        r"\b(expected\s+outcomes?|expected\s+results?|deliverables|outputs)\b"
    ],
    "Results": [
        r"\b(results|findings|outcomes)\b"
    ],
    "Discussion": [
        r"\b(discussion|analysis|interpretation)\b"
    ],
    "Conclusion": [
        r"\b(conclusion|summary|recommendations|future work)\b"
    ],
    "References": [
        r"\b(references|bibliography|works cited|sources)\b"
    ],
    "Salutation": [
        r"\b(dear|to whom it may concern|hello|greetings)\b"
    ],
    "Closing": [
        r"\b(sincerely|best regards|yours truly|cordially|thank you)\b"
    ],
}

# ============================================
# UNPROFESSIONAL PHRASES (for autocorrect to replace)
# ============================================

UNPROFESSIONAL_PHRASES: Dict[str, str] = {
    # ===== DESPERATE / BEGGING LANGUAGE =====
    "hire me": "I am confident my qualifications align with your needs",
    "please hire me": "I would welcome the opportunity to contribute to your team",
    "i need this job": "I am very interested in this position",
    "i need a job": "I am seeking a position where I can contribute my skills",
    "i need job": "I am seeking a position",
    "give me a chance": "I am eager to demonstrate my abilities",
    "give me an opportunity": "I would value the opportunity to contribute",
    "i'll take anything": "I am selective about positions that match my expertise",
    "i'm desperate": "",  # Remove entirely
    "i am desperate": "",  # Remove entirely
    "any job will do": "I am seeking a role that aligns with my qualifications",
    "just need a job": "I am actively seeking professional opportunities",
    
    # ===== UNPROFESSIONAL SELF-DESCRIPTION =====
    "im a looker": "",  # Remove entirely
    "i'm a looker": "",  # Remove entirely
    "looker": "strong candidate",
    "attractive": "dedicated professional",
    "good looking": "professional appearance",
    "i'm the best": "I bring strong qualifications and proven results",
    "i am the best": "My skills and experience make me a strong candidate",
    "better than everyone": "highly competitive and results-driven",
    "i'm awesome": "I am highly capable",
    "i am awesome": "I am highly capable",
    "i'm amazing": "I have a strong track record",
    "awesome graduate of life": "motivated entry-level candidate",
    "cool girl": "professional candidate",
    "great sense of humor and style": "strong interpersonal skills",
    "shot pics of my friends": "Photographed events and subjects",
    "added cute details in photoshop": "Edited images in Adobe Photoshop",
    "deal with annoying costumer requests": "Handled customer requests professionally",
    "deal with annoying customer requests": "Handled customer requests professionally",
    "liked chocolate best": "",
    
    # ===== CASUAL / SLANG =====
    "gonna": "going to",
    "wanna": "want to",
    "kinda": "somewhat",
    "sorta": "somewhat",
    "ain't": "is not",
    "y'all": "you all",
    "gotta": "have to",
    "lots of": "extensive",
    "a lot of": "significant",
    "tons of": "extensive",
    "stuff": "responsibilities",
    "things": "tasks and projects",
    "pretty good": "strong",
    "okay": "proficient",
    "fine": "satisfactory",
    
    # ===== WEAK / PASSIVE PHRASES =====
    "i think": "",  # Remove - be confident
    "i believe": "",  # Remove - state facts
    "i feel": "",  # Remove
    "maybe": "",  # Remove - be decisive
    "perhaps": "",  # Remove
    "sort of": "",  # Remove
    "kind of": "",  # Remove
    "a little bit": "",  # Remove
    "quite": "",  # Remove - weak modifier
    "very": "",  # Remove - use stronger word instead
    "really": "",  # Remove
    
    # ===== NEGATIVE / COMPLAINING LANGUAGE =====
    "bad": "challenging",
    "terrible": "difficult",
    "awful": "suboptimal",
    "hate": "prefer to avoid",
    "dislike": "do not prefer",
    "problem": "opportunity for improvement",
    "issue": "consideration",
    "failed": "learned from",
    "mistake": "learning experience",
    
    # ===== OVERLY CASUAL GREETINGS/CLOSINGS =====
    "hey": "Dear",
    "what's up": "To the hiring team",
    "cheers": "Sincerely",
    "thanks": "Thank you for your consideration",
    "thx": "Thank you",
    "bye": "Sincerely",
    
    # ===== EXAGGERATED / EMOTIONAL LANGUAGE =====
    "literally": "",  # Remove
    "absolutely": "",  # Remove or replace with specific
    "extremely": "",  # Let the adjective stand alone
    "incredibly": "",  # Remove
    "unbelievably": "",  # Remove
    "amazingly": "",  # Remove
    "fantastic": "strong",
    "perfect": "well-suited",
    "flawless": "high-quality",
}


# ============================================
# ACTION VERB REPLACEMENTS (for strengthening language)
# ============================================

ACTION_VERB_REPLACEMENTS: Dict[str, str] = {
     "worked on": "Delivered",
    "responsible for": "Led",
    "helped": "Enabled",
    "did": "Executed",
    "made": "Built",
    "handled": "Managed",
    "dealt with": "Resolved",
    "tried to": "Successfully",
    "attempted": "Executed",
    "participated in": "Contributed to",
    "assisted with": "Supported",
    "was part of": "Played key role in",
    "tasked with": "Accountable for",
    "in charge of": "Directed",
    "worked with": "Collaborated with",
}

# ============================================
# KEYWORDS FOR CONTENT RICHNESS SCORING
# ============================================

KEYWORDS_FOR_RICHNESS: List[str] = [
    "analysis", "project", "skills", "research",
    "achieved", "delivered", "implemented", "designed",
    "developed", "managed", "led", "created",
    "improved", "increased", "reduced", "optimized"
]

# ============================================
# DOCUMENT STRUCTURE TEMPLATES (for autocorrect to follow)
# ============================================

DOCUMENT_TEMPLATES: Dict[str, str] = {
    "Cover Letter": """
[Your Full Name]
[Your Phone Number] | [Your Email] | [Your LinkedIn/Portfolio]

[Date]

[Hiring Manager Name]
[Company Name]
[Company Address]

Dear [Hiring Manager Name],

[Opening paragraph: Express enthusiasm for the position and briefly introduce yourself]

[Middle paragraph 1: Highlight relevant skills and experience that match the job requirements]

[Middle paragraph 2: Show knowledge of the company and explain why you're interested]

[Closing paragraph: Call to action - request an interview and mention follow-up]

Sincerely,

[Your Name]
""",

    "Resume": """
[Your Name]
[Phone] | [Email] | [Location] | [LinkedIn]

PROFESSIONAL SUMMARY
[2-3 sentences summarizing your experience and key strengths]

SKILLS
• [Technical skill 1]
• [Technical skill 2]
• [Soft skill 1]
• [Soft skill 2]

WORK EXPERIENCE
[Job Title] | [Company Name] | [Dates]
• [Achievement 1]
• [Achievement 2]

EDUCATION
[Degree] | [University] | [Year]

CERTIFICATIONS (optional)
• [Certification name]
""",

    "Thesis": """
TITLE: [Thesis Title]

ABSTRACT
[Brief summary of research question, methods, results, and conclusion]

INTRODUCTION
[Background, problem statement, research questions, significance]

LITERATURE REVIEW
[Review of existing research and identified gaps]

METHODOLOGY
[Research design, data collection, analysis methods]

RESULTS
[Findings presented objectively]

DISCUSSION
[Interpretation of results, implications, limitations]

CONCLUSION
[Summary of findings, contributions, future work]

REFERENCES
[List of cited sources]
""",
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_required_sections(doc_type: str) -> List[str]:
    """Get required sections for a document type (for autocorrect to add)"""
    return REQUIRED_SECTION_MAP.get(doc_type, REQUIRED_SECTION_MAP["General Document"])


def get_unprofessional_phrase(phrase: str) -> str:
    """Get replacement for unprofessional phrase, or None if not found"""
    phrase_lower = phrase.lower().strip()
    return UNPROFESSIONAL_PHRASES.get(phrase_lower, None)


def get_action_verb_replacement(verb: str) -> str:
    """Get stronger action verb replacement"""
    verb_lower = verb.lower().strip()
    return ACTION_VERB_REPLACEMENTS.get(verb_lower, verb)


def get_document_template(doc_type: str) -> str:
    """Get template for document type (for adding missing sections)"""
    return DOCUMENT_TEMPLATES.get(doc_type, DOCUMENT_TEMPLATES.get("Resume", ""))


def get_all_unprofessional_phrases() -> Dict[str, str]:
    """Return all unprofessional phrases for bulk processing"""
    return UNPROFESSIONAL_PHRASES.copy()


def get_section_patterns() -> Dict[str, List[str]]:
    """Return all section detection patterns"""
    return SECTION_PATTERNS.copy()


def is_cover_letter(text: str) -> bool:
    """Quick check if document appears to be a cover letter"""
    text_lower = text.lower()
    indicators = ["dear", "sincerely", "position", "hiring manager"]
    return sum(1 for word in indicators if word in text_lower) >= 2


def get_missing_sections(doc_type: str, detected_sections: List[str]) -> List[str]:
    """Return list of sections that are missing from the document"""
    required = get_required_sections(doc_type)
    detected_lower = [s.lower() for s in detected_sections]
    missing = []
    
    for section in required:
        if not any(section.lower() in d or d in section.lower() for d in detected_lower):
            missing.append(section)
    
    return missing


def get_section_placeholder(section_name: str) -> str:
    """Generate placeholder text for a missing section"""
    placeholders = {
        "Professional Summary": "[Professional Summary: Add 2-3 sentences highlighting your key strengths and experience]",
        "Skills": "[Skills: List your relevant technical and soft skills as bullet points]",
        "Work Experience": "[Work Experience: List your relevant positions with achievements]",
        "Education": "[Education: List your degrees and certifications]",
        "Opening Paragraph (Interest in Role)": "[Opening paragraph: Express your interest in the position and briefly introduce yourself]",
        "Skills & Qualifications Paragraph": "[Skills paragraph: Describe how your skills match the job requirements]",
        "Company Interest Paragraph": "[Company interest: Explain why you want to work for this specific company]",
        "Call to Action": "[Call to action: Request an interview and indicate you will follow up]",
        "Executive Summary": "[Executive Summary: State the problem, solution, cost, and request in 4 sentences max]",
        "Problem Statement": "[Problem Statement: Describe what's wrong with specific data and consequences]",
        "Objectives": "[Objectives: List SMART objectives with targets and deadlines in a table]",
        "Action Plan": "[Action Plan: Detail step-by-step actions with who, what, and when in a table]",
        "Resources Needed": "[Resources Needed: List required items with quantities]",
        "Budget": "[Budget: Show itemized costs with calculations in a table]",
        "Timeline": "[Timeline: Provide a timeline with start and end dates in a table]",
        "Success Metrics": "[Success Metrics: Define how success will be measured with baselines and targets in a table]",
        "Conclusion & Request": "[Conclusion & Request: Summarize and make a specific request for approval]",
    }
    return placeholders.get(section_name, f"[{section_name}: Add content here]")
