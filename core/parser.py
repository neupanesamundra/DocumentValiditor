from pathlib import Path
from typing import List

import pdfplumber
import regex
from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph

from config.rules import SECTION_PATTERNS
from utils.constants import DEFAULT_ENCODING


def _infer_pdf_name(page) -> str:
    """Infer a candidate name from the first page using positioned words."""
    try:
        words = page.extract_words(use_text_flow=True, keep_blank_chars=False) or []
    except Exception:
        return ""

    header_words = []
    for word in words:
        text = (word.get("text") or "").strip()
        if not text:
            continue
        if word.get("top", 999) > 72:
            continue
        if word.get("x0", 999) > 260:
            continue
        if ":" in text or "@" in text or regex.search(r"\d", text):
            continue
        if not regex.fullmatch(r"[A-Za-z][A-Za-z'`.-]*", text):
            continue
        header_words.append(text)

    if not (2 <= len(header_words) <= 4):
        return ""
    return " ".join(header_words)


def _infer_pdf_date(page) -> str:
    """Infer a date from the first page using positioned words."""
    try:
        plain_text = page.extract_text(layout=False) or ""
    except Exception:
        plain_text = ""

    plain_match = regex.search(
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+\d{4}\b|\b[A-Za-z]+\s+\d{1,2},?\s+\d{4}\b",
        plain_text,
        flags=regex.IGNORECASE,
    )
    if plain_match:
        return plain_match.group(0).strip()

    try:
        words = page.extract_words(use_text_flow=True, keep_blank_chars=False) or []
    except Exception:
        return ""

    date_tokens = []
    for word in words:
        text = (word.get("text") or "").strip()
        if not text:
            continue
        if word.get("top", 999) > 190:
            continue
        if not (
            regex.fullmatch(r"\d{1,2}(?:st|nd|rd|th)?", text, flags=regex.IGNORECASE)
            or regex.fullmatch(r"[A-Za-z]+,?", text)
            or regex.fullmatch(r"\d{4}", text)
        ):
            continue
        date_tokens.append((word.get("top", 0), word.get("x0", 0), text))

    if not date_tokens:
        return ""

    date_tokens.sort(key=lambda item: (round(item[0], 0), item[1]))
    grouped: list[list[str]] = []
    current: list[str] = []
    current_top = None
    for top, _x0, text in date_tokens:
        if current_top is None or abs(top - current_top) <= 4:
            current.append(text)
            current_top = top if current_top is None else current_top
        else:
            grouped.append(current)
            current = [text]
            current_top = top
    if current:
        grouped.append(current)

    for group in grouped:
        candidate = " ".join(group)
        candidate = regex.sub(r"\s+,", ",", candidate).strip()
        if regex.search(r"\b\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+\d{4}\b", candidate, flags=regex.IGNORECASE):
            return candidate
        if regex.search(r"\b[A-Za-z]+\s+\d{1,2},?\s+\d{4}\b", candidate, flags=regex.IGNORECASE):
            return candidate
    return ""


def parse_document(filepath):
    path = Path(filepath)
    extension = path.suffix.lower()

    if extension == ".pdf":
        result = parse_pdf(path)
    elif extension == ".docx":
        result = parse_docx(path)
    elif extension == ".txt":
        result = parse_txt(path)
    else:
        result = {"text": ""}

    text = result.get("text", "")
    result["sections"] = detect_sections(text)
    result["word_count"] = len(regex.findall(r"\b\w+\b", text))
    return result


def parse_pdf(filepath: Path):
    page_texts = []
    inferred_header_lines: List[str] = []

    with pdfplumber.open(filepath) as pdf:
        for index, page in enumerate(pdf.pages):
            if index == 0:
                inferred_name = _infer_pdf_name(page)
                if inferred_name:
                    inferred_header_lines.append(inferred_name)
                inferred_date = _infer_pdf_date(page)
                if inferred_date:
                    inferred_header_lines.append(inferred_date)
            extracted = page.extract_text(layout=True) or ""
            if not extracted.strip():
                words = page.extract_words(use_text_flow=True) or []
                extracted = "\n".join(w.get("text", "") for w in words if w.get("text"))
            page_texts.append(extracted.strip())

    text = "\n\n".join(p for p in page_texts if p)
    if inferred_header_lines:
        missing_lines = [line for line in inferred_header_lines if line and line.lower() not in text.lower()]
        if missing_lines:
            header_block = "\n".join(missing_lines)
            text = f"{header_block}\n\n{text}".strip()
    return {"text": text}


def parse_docx(filepath: Path):
    doc = Document(filepath)
    text = "\n".join(_iter_docx_text_blocks(doc))
    return {"text": text}


def parse_txt(filepath: Path):
    with open(filepath, "r", encoding=DEFAULT_ENCODING) as file:
        return {"text": file.read()}


def detect_sections(text: str):
    lowered = text.lower()
    found_sections = []
    for section_name, patterns in SECTION_PATTERNS.items():
        if any(regex.search(pattern, lowered, flags=regex.IGNORECASE) for pattern in patterns):
            found_sections.append(section_name)
    return found_sections


def _iter_block_items(parent):
    """Yield paragraphs and tables in document order, including inside table cells."""
    if isinstance(parent, DocxDocument):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        return

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def _extract_table_text(table: Table) -> str:
    lines = []
    for row in table.rows:
        cell_texts = []
        for cell in row.cells:
            parts = []
            for block in _iter_block_items(cell):
                if isinstance(block, Paragraph):
                    value = (block.text or "").strip()
                    if value:
                        parts.append(value)
                elif isinstance(block, Table):
                    nested_text = _extract_table_text(block).strip()
                    if nested_text:
                        parts.append(nested_text)
            cell_text = "\n".join(parts).strip()
            if cell_text:
                cell_texts.append(cell_text)
        row_text = " | ".join(cell_texts).strip()
        if row_text:
            lines.append(row_text)
    return "\n".join(lines)


def _iter_docx_text_blocks(doc: DocxDocument) -> List[str]:
    blocks: List[str] = []
    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            value = (block.text or "").strip()
            if value:
                blocks.append(value)
        elif isinstance(block, Table):
            table_text = _extract_table_text(block).strip()
            if table_text:
                blocks.append(table_text)
    return blocks
