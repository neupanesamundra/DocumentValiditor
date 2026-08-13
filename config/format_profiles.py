from typing import Any, Dict

FORMAT_PROFILES: Dict[str, Dict[str, Any]] = {
    "Resume": {
        "docx_margins": {"top": 0.7, "bottom": 0.7, "left": 0.8, "right": 0.8},
        "docx": {
            "normal_font": "Aptos",
            "normal_size": 10.8,
            "heading_size": 14,
            "heading_space_before": 9,
            "heading_space_after": 3,
            "body_space_after": 2.5,
        },
        "pdf": {
            "title_size": 26,
            "heading_size": 12,
            "body_size": 10,
            "body_leading": 14.5,
        },
        "page_break_before": [],
    },
    "CV": {
        "docx_margins": {"top": 0.7, "bottom": 0.7, "left": 0.8, "right": 0.8},
        "docx": {
            "normal_font": "Aptos",
            "normal_size": 10.8,
            "heading_size": 14,
            "heading_space_before": 9,
            "heading_space_after": 3,
            "body_space_after": 2.5,
        },
        "pdf": {
            "title_size": 26,
            "heading_size": 12,
            "body_size": 10,
            "body_leading": 14.5,
        },
        "page_break_before": [],
    },
    "Thesis": {
        "docx_margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
        "docx": {
            "normal_font": "Times New Roman",
            "normal_size": 12,
            "heading_size": 14,
            "heading_space_before": 12,
            "heading_space_after": 6,
            "body_space_after": 5,
        },
        "pdf": {
            "title_size": 20,
            "heading_size": 13,
            "body_size": 12,
            "body_leading": 18,
        },
        "page_break_before": [
            "Abstract",
            "Introduction",
            "Literature Review",
            "Methodology",
            "Analysis",
            "Results",
            "Discussion",
            "Conclusion",
            "References",
        ],
    },
    "Report": {
        "docx_margins": {"top": 0.9, "bottom": 0.9, "left": 0.9, "right": 0.9},
        "docx": {
            "normal_font": "Calibri",
            "normal_size": 11,
            "heading_size": 13,
            "heading_space_before": 10,
            "heading_space_after": 4,
            "body_space_after": 4,
        },
        "pdf": {
            "title_size": 19.5,
            "heading_size": 12,
            "body_size": 10.5,
            "body_leading": 15,
        },
        "page_break_before": ["Executive Summary", "Introduction", "Analysis", "Conclusion", "References"],
    },
    "Cover Letter": {
        "docx_margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
        "docx": {
            "normal_font": "Times New Roman",
            "normal_size": 11.5,
            "heading_size": 11.5,
            "heading_space_before": 0,
            "heading_space_after": 0,
            "body_space_after": 0,
        },
        "pdf": {
            "title_size": 12,
            "heading_size": 11,
            "body_size": 11,
            "body_leading": 15,
        },
        "page_break_before": [],
    },
    "Essay": {
        "docx_margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
        "docx": {
            "normal_font": "Times New Roman",
            "normal_size": 12,
            "heading_size": 12,
            "heading_space_before": 0,
            "heading_space_after": 0,
            "body_space_after": 0,
        },
        "pdf": {
            "title_size": 14,
            "heading_size": 12,
            "body_size": 12,
            "body_leading": 24,
        },
        "page_break_before": [],
    },
    "Proposal": {
        "docx_margins": {"top": 0.9, "bottom": 0.9, "left": 0.9, "right": 0.9},
        "docx": {
            "normal_font": "Calibri",
            "normal_size": 11,
            "heading_size": 14,
            "heading_space_before": 10,
            "heading_space_after": 4,
            "body_space_after": 4,
        },
        "pdf": {
            "title_size": 18,
            "heading_size": 12.5,
            "body_size": 10.8,
            "body_leading": 15,
        },
        "page_break_before": ["Executive Summary", "Problem Statement", "Objectives", "Action Plan", "Resources Needed", "Budget", "Timeline", "Success Metrics", "Conclusion & Request"],
    },
    "General Document": {
        "docx_margins": {"top": 0.8, "bottom": 0.8, "left": 0.85, "right": 0.85},
        "docx": {
            "normal_font": "Calibri",
            "normal_size": 11,
            "heading_size": 13,
            "heading_space_before": 10,
            "heading_space_after": 4,
            "body_space_after": 3,
        },
        "pdf": {
            "title_size": 19.5,
            "heading_size": 12,
            "body_size": 10,
            "body_leading": 14.5,
        },
        "page_break_before": [],
    },
}


def get_format_profile(doc_type: str) -> Dict[str, Any]:
    return FORMAT_PROFILES.get(doc_type, FORMAT_PROFILES["General Document"])
