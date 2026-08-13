from flask import Flask, render_template, request, send_from_directory

from config.settings import APP_NAME, DEBUG, IMPROVED_FOLDER, UPLOAD_FOLDER
from core.classifier import classify_document
from core.explanation_engine import evaluate_status, generate_explanation
from core.file_validator import validate_file
from core.improver import improve_document
from core.parser import parse_document
from core.requirement_engine import (
    build_default_requirements,
    merge_requirements,
    parse_custom_requirements,
    resolve_document_type,
    summarize_requirements,
)
from core.scoring_engine import score_document
from models.analysis_result import AnalysisResult
from utils.helpers import ensure_directories
from utils.logger import get_logger
from werkzeug.utils import secure_filename

app = Flask(__name__)
logger = get_logger(__name__)
  

ensure_directories([UPLOAD_FOLDER, IMPROVED_FOLDER])

DOC_TYPE_OPTIONS = [
    "Auto Detect",
    "Report",
    "Resume",
    "CV",
    "Cover Letter",
    "Essay",
    "Proposal",
    "Thesis",
    "General Document",
]

# Store the latest change log for the changes page
_latest_change_log = None
_latest_improved_files = {}
_latest_run_info = {}


@app.route("/", methods=["GET", "POST"])
def index():
    global _latest_change_log, _latest_improved_files, _latest_run_info
    
    if request.method == "POST":
        if "document" not in request.files:
            return render_template("error.html", error="No file part in request.")

        uploaded_file = request.files["document"]
        valid, message = validate_file(uploaded_file)
        if not valid:
            return render_template("error.html", error=message)

        safe_name = secure_filename(uploaded_file.filename)
        saved_path = UPLOAD_FOLDER / safe_name
        uploaded_file.save(saved_path)

        selected_doc_type = request.form.get("doc_type", "Auto Detect")
        requirement_notes = (request.form.get("requirements") or "").strip()
        generate_improved = request.form.get("generate_improved") == "on"

        requirement_file = request.files.get("requirement_file")
        requirement_file_text = ""
        if requirement_file and requirement_file.filename:
            req_valid, req_message = validate_file(requirement_file)
            if not req_valid:
                return render_template("error.html", error=f"Requirement file error: {req_message}")

            req_safe_name = "requirements_" + secure_filename(requirement_file.filename)
            req_saved_path = UPLOAD_FOLDER / req_safe_name
            requirement_file.save(req_saved_path)
            req_parsed = parse_document(req_saved_path)
            requirement_file_text = (req_parsed.get("text") or "").strip()

        try:
            parsed_data = parse_document(saved_path)
            text = parsed_data.get("text", "")
            sections = parsed_data.get("sections", [])

            classified_doc_type = classify_document(text)
            if selected_doc_type not in DOC_TYPE_OPTIONS:
                selected_doc_type = "Auto Detect"
            display_doc_type, profile_doc_type = resolve_document_type(selected_doc_type, classified_doc_type)

            combined_requirement_text = "\n".join(part for part in [requirement_notes, requirement_file_text] if part)
            custom_requirements = parse_custom_requirements(combined_requirement_text)
            default_requirements = build_default_requirements(profile_doc_type)
            active_requirements = merge_requirements(default_requirements, custom_requirements)

            score, analysis, suggestions, breakdown = score_document(
                text,
                profile_doc_type,
                sections,
                requirement_profile=active_requirements,
                file_extension=saved_path.suffix.lower().lstrip("."),
                source_path=saved_path,
            )
            evaluation_status = evaluate_status(score)
            explanation, explanation_diagnostic = generate_explanation(score, analysis, suggestions, display_doc_type)
            requirement_summary = summarize_requirements(display_doc_type, profile_doc_type, active_requirements)
            ai_diagnostics = [explanation_diagnostic]

            improved_docx_filename = ""
            improved_pdf_filename = ""

            if generate_improved:
                if score >= 90:
                    requirement_summary.append("Improved file generation: Skipped (score already 90+).")
                else:
                    from core.change_tracker import reset_change_log, set_document_context
                    
                    # Reset and setup change tracking for this document
                    reset_change_log()
                    set_document_context(profile_doc_type, text, "")
                    
                    improved_files = improve_document(
                        text,
                        saved_path.name,
                        profile_doc_type,
                        source_path=saved_path,
                    )
                    improved_docx_filename = improved_files["docx"].name
                    improved_pdf_filename = improved_files["pdf"].name
                    
                    # Store for the changes page
                    _latest_improved_files = {
                        'docx': improved_docx_filename,
                        'pdf': improved_pdf_filename
                    }
                    _latest_run_info = {
                        'doc_type': display_doc_type,
                        'processed_filename': saved_path.name,
                        'diagnostic': improved_files.get("diagnostic", "AI rewrite: status unavailable."),
                    }
                    from core.change_tracker import get_change_log
                    _latest_change_log = get_change_log()

                    # Fallback: if an improved document was produced but no granular changes were tracked,
                    # record a high-level document change so the changes page is not empty.
                    try:
                        if not _latest_change_log.has_changes():
                            improved_parsed_for_log = parse_document(improved_files["docx"])
                            improved_text_for_log = (improved_parsed_for_log.get("text") or "").strip()
                            original_text_for_log = (text or "").strip()
                            if improved_text_for_log and improved_text_for_log != original_text_for_log:
                                _latest_change_log.add(
                                    "rewrite",
                                    original_text_for_log[:200],
                                    improved_text_for_log[:200],
                                    "document",
                                )
                    except Exception as log_exc:
                        logger.warning("Change-log fallback check failed for %s: %s", saved_path.name, log_exc)
                    
                    ai_diagnostics.append(improved_files.get("diagnostic", "AI rewrite: status unavailable."))

                    # Safeguard: do not offer "improved" output if it scores lower than the original.
                    try:
                        improved_parsed = parse_document(improved_files["docx"])
                        improved_text = improved_parsed.get("text", "")
                        improved_sections = improved_parsed.get("sections", [])
                        improved_score, _ia, _is, _ib = score_document(
                            improved_text,
                            profile_doc_type,
                            improved_sections,
                            requirement_profile=active_requirements,
                            file_extension="docx",
                            source_path=improved_files["docx"],
                        )

                        if improved_score < score:
                            delta = score - improved_score
                            requirement_summary.append(
                                f"Improved file generation: Kept (score changed from {score} to {improved_score}, delta -{delta})."
                            )
                            suggestions.insert(
                                0,
                                f"Auto-improved file was kept even though score dropped by {delta} point(s) because keep-threshold is 90+."
                            )
                        else:
                            requirement_summary.append(
                                f"Improved file generation: Accepted (original {score}, improved {improved_score})."
                            )
                    except Exception as safeguard_exc:
                        logger.warning("Improvement safeguard check failed for %s: %s", saved_path.name, safeguard_exc)
                        requirement_summary.append("Improved file generation: Enabled (safeguard check unavailable).")
            else:
                requirement_summary.append("Improved file generation: Disabled (safe scoring mode).")

            result = AnalysisResult(
                score=score,
                evaluation_status=evaluation_status,
                doc_type=display_doc_type,
                analysis=analysis,
                explanation=explanation,
                suggestions=suggestions,
                score_breakdown=breakdown,
                improved_docx_filename=improved_docx_filename,
                improved_pdf_filename=improved_pdf_filename,
                applied_requirements=requirement_summary,
                ai_diagnostics=ai_diagnostics,
            )

            logger.info(
                "Processed document=%s selected_type=%s profile_type=%s score=%s improved=%s",
                saved_path.name,
                display_doc_type,
                profile_doc_type,
                score,
                bool(improved_docx_filename),
            )
            return render_template("result.html", result=result)
        except Exception as exc:
            logger.exception("Failed to process %s: %s", saved_path.name, exc)
            return render_template("error.html", error="An unexpected error occurred while processing the document.")

    return render_template("index.html", app_name=APP_NAME, doc_type_options=DOC_TYPE_OPTIONS)


@app.route("/download/<path:filename>")
def download_file(filename):
    """Download improved document file"""
    return send_from_directory(IMPROVED_FOLDER, filename, as_attachment=True)


@app.route("/changes")
def show_changes():
    """Show detailed changes made during autocorrect"""
    global _latest_change_log, _latest_improved_files, _latest_run_info
    
    if _latest_change_log is None or not getattr(_latest_change_log, "has_changes", lambda: False)():
        return render_template("changes.html",
            total_changes=0,
            changes=[],
            timestamp=_latest_run_info.get('processed_filename', ''),
            doc_type=_latest_run_info.get('doc_type', ''),
            diagnostic=_latest_run_info.get('diagnostic', 'No tracked changes were detected for this run.'),
            improved_docx_filename=_latest_improved_files.get('docx', ''),
            improved_pdf_filename=_latest_improved_files.get('pdf', '')
        )
    
    return render_template("changes.html",
        total_changes=len(_latest_change_log.changes),
        changes=[{
            'type': c.change_type,
            'original': c.original,
            'corrected': c.corrected,
            'location': c.location
        } for c in _latest_change_log.changes],
        timestamp=_latest_change_log.timestamp,
        doc_type=_latest_change_log.document_type,
        diagnostic=_latest_run_info.get('diagnostic', ''),
        improved_docx_filename=_latest_improved_files.get('docx', ''),
        improved_pdf_filename=_latest_improved_files.get('pdf', '')
    )


if __name__ == "__main__":
    app.run(debug=DEBUG)
