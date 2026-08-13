from dataclasses import dataclass, field
from typing import List


@dataclass
class ScoreDetail:
    label: str
    points: int
    kind: str


@dataclass
class AnalysisResult:
    score: int
    evaluation_status: str
    doc_type: str
    analysis: List[str]
    explanation: List[str]
    suggestions: List[str]
    score_breakdown: List[ScoreDetail]
    improved_docx_filename: str
    improved_pdf_filename: str
    applied_requirements: List[str] = field(default_factory=list)
    ai_diagnostics: List[str] = field(default_factory=list)
