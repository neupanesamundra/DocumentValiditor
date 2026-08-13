"""
AI Rewriter Service - Lightweight prompts with comprehensive local preprocessing
"""

from config.settings import AI_REWRITE_TEMPERATURE
from services.ai_client import AIResponse, request_text_completion


def _get_proposal_rewrite_rules() -> str:
    return """
PROPOSAL REWRITE REQUIREMENTS:
- Preserve the original proposal structure exactly; do not scramble section order
- Keep the title as a single title line only; do not duplicate or restate it as a section header
- Keep "Prepared by:" and "Date:" as standalone metadata lines directly below the title when present
- Number section headers consistently as 1., 2., 3., etc. when the source uses numbered sections
- Do not duplicate headers or echo a section name as body content
- Preserve all original tables and their exact data values; do not convert tables into summaries
- Keep budget rows, timeline rows, dates, item names, and currency amounts exactly aligned with the source facts
- Preserve list structure; do not collapse multiple bullets or numbered items into one sentence
- Keep paragraph boundaries intact; do not merge all content into a single block
- Improve wording and correctness without removing detail
- Ensure Executive Summary is 4 sentences max: problem + solution + cost + request
- Make objectives SMART: Specific, Measurable, Achievable, Relevant, Time-bound
- Format tables for Objectives, Action Plan, Budget, Timeline, Success Metrics
- Use active voice throughout
- Replace passive constructions with active
- Use specific numbers and data instead of vague terms
- Break long sentences into shorter ones
- Use present tense for direct statements

APPLY THESE EXACT CORRECTIONS WHEN THEY APPEAR:
- Redusing -> Reducing
- Prepaired -> Prepared
- Janruary -> January
- Backround -> Background
- meny -> many
- plastik -> plastic
- markt -> marked
- Objetives -> Objectives
- bi -> by
- Too teach -> To teach
- importence -> importance
- classerooms -> classrooms
- Activites -> Activities
- Awerness -> Awareness
- Campain -> Campaign
- cheep -> cheap
- throwed -> thrown
- frendly -> friendly
- aprove -> approve
- are school -> our school
- stop climate change -> combating climate change
"""


def _get_tone_instruction(doc_type: str) -> str:
    """Get tone-specific instructions based on document type"""
    
    tone_instructions = {
        "Cover Letter": """
TONE REQUIREMENTS:
- Professional and confident (never desperate)
- Enthusiastic but measured
- Polite and respectful
- Never use: "hire me", "please give me a chance", "I need this job"
- Use: "I am confident", "I am excited", "My qualifications align with"
""",
        "Resume": """
TONE REQUIREMENTS:
- Confident and achievement-oriented
- Use strong action verbs: "Led", "Developed", "Achieved", "Executed"
- Never use: "responsible for", "helped", "worked on" (use stronger alternatives)
- Be specific about accomplishments
""",
        "CV": """
TONE REQUIREMENTS:
- Professional academic tone
- Focus on publications, research, and teaching experience
- Use formal, precise language
""",
        "Thesis": """
TONE REQUIREMENTS:
- Formal academic tone
- Objective and precise
- Avoid emotional or casual language
""",
        "Report": """
TONE REQUIREMENTS:
- Professional and objective
- Clear and concise
- Evidence-based language
""",
        "Proposal": """
TONE REQUIREMENTS:
- Persuasive but professional
- Confident and solution-oriented
- Focus on value and outcomes
- Use active voice, not passive
- Avoid vague words; use specific data
- Use active verbs
- Keep sentences short (break long ones)
- Use present tense for direct statements
- Follow SMART objectives: Specific, Measurable, Achievable, Relevant, Time-bound
- Format tables properly with headers and borders
- Use consistent punctuation in lists
- Single space within sections, double between
- Use digits for numbers and costs
- Show calculations for costs
- Remove: "I think", "Hopefully", "Very good", "We will try"
- Replace with direct statements, "We expect", specific data, "We will"
""",
    }
    
    return tone_instructions.get(doc_type, """
TONE REQUIREMENTS:
- Professional and clear
- Maintain factual accuracy
- Improve readability
""")


def _get_structure_instruction(doc_type: str) -> str:
    """Get structure-preservation rules for each document type."""

    if doc_type in {"Report", "Proposal", "Thesis"}:
        return """
STRUCTURE REQUIREMENTS:
- Preserve the original heading order exactly unless the input itself is broken beyond repair
- Do not add new sections, placeholders, executive summaries, findings, analyses, or recommendations unless they already exist in the source
- Keep each paragraph as its own paragraph; do not merge separate paragraphs together
- Do not move content from one heading into another heading
- Treat the input as an academic/professional document, not casual prose
- Do not summarize, compress, or shorten the document's meaning just to make it sound cleaner
"""

    if doc_type in {"Resume", "CV"}:
        return """
STRUCTURE REQUIREMENTS:
- Preserve section names and entry order
- Keep line-based structure for roles, institutions, dates, and bullets
- Do not merge multiple entries into one paragraph
"""

    if doc_type == "Cover Letter":
        return """
STRUCTURE REQUIREMENTS:
- Preserve the normal cover letter block structure
- Keep salutations, body paragraphs, and closing separate
"""

    return """
STRUCTURE REQUIREMENTS:
- Preserve the document's original structure and paragraph breaks
- Do not invent headings or placeholders
"""


def _get_academic_editing_rules(doc_type: str) -> str:
    """Get detailed academic editing rules for report-like documents."""

    if doc_type not in {"Report", "Proposal", "Thesis"}:
        return ""

    return """
ACADEMIC EDITING RULES:
- Fix grammar, spelling, punctuation, and sentence flow without changing meaning
- Maintain a consistent academic but readable tone
- Keep the original structure, headings, and section order
- Preserve all original examples, definitions, and data
- Do not insert random characters, filler, jokes, or nonsense
- Keep paragraph boundaries intact so the document formatter can apply page breaks and section spacing cleanly
- Treat only top-level headings like "1", "2", "3" or "I", "II", "III" as main sections
- Keep subsection lines such as "1.1" and "1.2" inside their parent section as separate paragraph blocks; do not promote them into new main sections
- Do not output the literal text "[PAGE BREAK]"; real page breaks are handled by the document formatter
- If a section is too short, expand it into fuller academic explanation using only the facts already present in the document
- If a section is already detailed, improve clarity without unnecessarily shortening it
- Preserve citations, references, and source mentions already present in the document
- Do not invent citations, references, statistics, or unsupported claims
- If the document has a front page or cover page before the first main heading, preserve that page as-is
- If the document contains images, diagrams, charts, or figures, keep them untouched and in their original positions
"""


def _get_doc_type_specific_instruction(doc_type: str) -> str:
    """Get document-type-specific academic structure guidance."""

    if doc_type == "Proposal":
        return """
PROPOSAL FORMAT GUIDANCE:
- Prefer this proposal flow when those sections exist: Title, Introduction, Problem Statement, Objectives, Technical Approach, Timeline, Budget, Expected Outcomes, Conclusion
- Keep the proposal persuasive but realistic
- Use simple technical explanation suitable for non-experts
- Do not turn a proposal into a report or thesis
"""

    if doc_type == "Report":
        return """
REPORT FORMAT GUIDANCE:
- Keep the report explanatory and structured
- Maintain section-based academic flow without turning subsection topics into new main sections
"""

    return ""


def _get_section_specific_instruction(section_name: str) -> str:
    """Get section-specific guidance"""
    
    section_instructions = {
        "Opening Paragraph": """
- Start with a strong opening statement
- Express genuine interest in the role/opportunity
- Never start with desperate phrases like "Please hire me"
""",
        "Professional Summary": """
- Write 2-3 powerful sentences highlighting key strengths
- Focus on value you bring
- Be confident, not arrogant
""",
        "Experience": """
- Preserve entry structure
- Keep role/company/date header lines separate from achievement bullets
- Do not turn every line into a bullet point
- Use bullets only for concrete accomplishments or responsibilities
""",
        "Projects": """
- Preserve project title and technology/details as plain lines when appropriate
- Do not force every project line into a separate bullet
- Use bullets only for substantial outcomes, features, or achievements
""",
        "Education": """
- Keep school, degree, and date/location details as plain lines
- Do not convert education details into bullet points unless they are actual achievements
""",
        "Skills": """
- List relevant technical and soft skills
- Be specific, not generic
- Group similar skills together
""",
        "Work Experience": """
- Use action verbs to start each bullet point
- Include quantifiable achievements when possible
- Focus on results, not just duties
""",
        "Closing": """
- End with a professional call to action
- Express willingness to provide additional information
- Thank the reader for consideration
""",
    }
    
    return section_instructions.get(section_name, "")


def build_section_rewrite_prompt(doc_type: str, section_name: str, section_text: str) -> str:
    """
    Lightweight but effective prompt for section rewriting.
    Heavy lifting is done locally in improver.py's phrase replacement.
    """
    
    tone_instruction = _get_tone_instruction(doc_type)
    structure_instruction = _get_structure_instruction(doc_type)
    academic_rules = _get_academic_editing_rules(doc_type)
    doc_type_guidance = _get_doc_type_specific_instruction(doc_type)
    section_instruction = _get_section_specific_instruction(section_name)
    proposal_rules = _get_proposal_rewrite_rules() if doc_type == "Proposal" else ""
    
    # Keep prompt concise - local rules handle specific phrases
    return f"""Document type: {doc_type}
Section: {section_name}

{tone_instruction}

{structure_instruction}

{academic_rules}

{doc_type_guidance}

{section_instruction}

{proposal_rules}

Task: Improve this section's grammar, clarity, and professionalism.
- Fix spelling and grammar errors
- Improve sentence flow
- Preserve ALL factual information
- Preserve the original section structure when it is already meaningful
- Do not add headings, placeholders, or new sections
- Do not duplicate the current section heading inside the body
- Keep bullets, numbered items, and table-like rows as separate lines
- Expand underdeveloped sections into fuller explanation when possible using only existing facts
- Do not summarize or shorten detailed content
- Preserve any citations or references already present
- Return plain text only (no markdown, no asterisks)

Original text:
{section_text.strip()}

Improved text:"""


def build_rewrite_prompt(text: str, doc_type: str) -> str:
    """Lightweight full-document rewrite prompt"""
    
    tone_instruction = _get_tone_instruction(doc_type)
    structure_instruction = _get_structure_instruction(doc_type)
    academic_rules = _get_academic_editing_rules(doc_type)
    doc_type_guidance = _get_doc_type_specific_instruction(doc_type)
    proposal_rules = _get_proposal_rewrite_rules() if doc_type == "Proposal" else ""
    
    return f"""Document type: {doc_type}

{tone_instruction}

{structure_instruction}

{academic_rules}

{doc_type_guidance}

{proposal_rules}

Task: Improve this document professionally.
- Fix grammar and spelling
- Improve sentence flow and readability
- Remove redundant or weak phrasing
- Preserve ALL factual information
- Keep existing headings and paragraph boundaries
- Keep title, metadata lines, bullets, numbered items, and table rows distinct
- Do not invent sections or placeholder text
- Do not duplicate any existing header
- Expand weak or too-short sections into fuller academic explanation using only existing facts
- Do not summarize or condense detailed sections of the report
- Preserve citations, references, and source mentions already present
- Do not invent citations or unsupported factual claims
- Return plain text only (no markdown)

Original document:
{text.strip()}

Improved document:"""


def rewrite_section_with_ai(section_name: str, section_text: str, doc_type: str) -> AIResponse:
    """
    Rewrite a single section using AI.
    Note: Local phrase replacement already happened before this call.
    """
    
    system_prompt = """You are a professional academic document editor. Improve grammar, clarity, and flow while preserving all facts, detail, and the original structure. You may expand underdeveloped sections using only facts already present in the document. Never invent information, headings, sections, placeholders, citations, references, statistics, or unsupported claims. Never summarize or condense detailed content. Return only the improved text."""
    
    user_prompt = build_section_rewrite_prompt(doc_type, section_name, section_text)
    
    return request_text_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=AI_REWRITE_TEMPERATURE,
    )


def rewrite_document_with_ai(text: str, doc_type: str) -> AIResponse:
    """Rewrite entire document using AI"""
    
    system_prompt = """You are a professional academic document editor. Improve grammar, clarity, professional tone, and readability while preserving all facts, detail, headings, and paragraph structure. You may expand weak sections using only facts already present in the document. Never invent new sections, placeholder content, citations, references, statistics, or unsupported claims. Never summarize or condense detailed content. Return only the improved document."""
    
    user_prompt = build_rewrite_prompt(text, doc_type)
    
    return request_text_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=AI_REWRITE_TEMPERATURE,
    )
