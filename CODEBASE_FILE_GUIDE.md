# Codebase File Guide

This document explains the important files in the project, what each file is responsible for, and how the code flows from upload to scoring, explanation, improvement, and export.

## 1. Main App Entry

### `app.py`

This is the Flask entry point and the coordinator of the whole application.

What it does:

- creates the Flask app
- loads app settings like upload and output folders
- defines supported document types shown in the UI
- handles the upload form on `/`
- validates the uploaded document
- parses document content
- classifies the document type
- merges default and custom requirements
- scores the document
- generates explanation text
- optionally creates improved DOCX and PDF files
- stores the latest change-tracking data for the `/changes` page
- serves improved files from `/download/<filename>`

Important routes:

- `/`: upload, analyze, and optionally improve a document
- `/download/<filename>`: download generated output
- `/changes`: show tracked changes made during improvement

In short, `app.py` is the traffic controller of the project.

## 2. Config Files

### `config/settings.py`

Stores project-wide settings such as:

- app name
- debug mode
- upload and output folder paths
- AI rewrite temperature
- LanguageTool configuration

This file centralizes environment-level configuration so the rest of the code can import settings instead of hardcoding them.

### `config/rules.py`

Contains the rule-based logic definitions used across the app.

Examples:

- allowed file extensions
- keyword-based classification rules
- required sections for each document type
- unprofessional phrase replacements
- stronger action verb replacements
- document structure templates

This file is the backbone of the rule-based system.

### `config/format_profiles.py`

Defines layout and export profiles for different document types.

Examples:

- font sizes
- spacing
- margins
- section heading behavior
- page-break preferences

This is used mainly by the exporter so resumes, reports, proposals, and theses do not all look the same.

### `config/rubric_schema.py`

Defines the scoring/label structure used for training-data workflows and rubric consistency.

This matters more in the AI and model-training side of the project than in the web request path.

## 3. Core Processing Pipeline

### `core/file_validator.py`

Checks whether the uploaded file is valid before processing.

It typically verifies:

- file exists in the request
- extension is allowed
- file size is acceptable

This prevents bad input from entering the main pipeline.

### `core/parser.py`

Extracts readable text and sections from uploaded files.

It handles different file types such as:

- PDF
- DOCX
- TXT

This file is critical because every later stage depends on the extracted text quality.

### `core/classifier.py`

Classifies the uploaded document into a document type such as:

- Resume
- CV
- Cover Letter
- Report
- Proposal
- Thesis
- Essay
- General Document

The classifier uses rule-based signals and can also cooperate with the ML classifier service when available.

### `core/requirement_engine.py`

Builds and merges requirement profiles.

It is responsible for:

- mapping selected UI document types to scoring profiles
- parsing user-written requirement notes
- merging user requirements with default system requirements
- summarizing the active requirement set for display

This helps the system score documents against the right expectations.

### `core/scoring_engine.py`

Computes the document score and score breakdown.

It combines:

- required-section checks
- grammar penalties
- formatting penalties
- readability score
- keyword relevance
- document-specific scoring logic
- optional ML score assistance

This file is the main scoring brain of the app.

### `core/explanation_engine.py`

Turns raw scoring output into user-friendly status and explanation text.

It helps answer:

- Is the document excellent, good, average, or weak?
- Why did it receive this score?
- What improvements should the user make?

This is where the system becomes understandable instead of only numerical.

### `core/improver.py`

Generates improved document content and repair logic.

This is one of the most complex files in the project.

Responsibilities include:

- extracting structured sections from text
- cleaning noisy text
- improving resume, cover letter, report, proposal, and thesis content
- applying local spelling and grammar fixes
- using AI rewrite services when available
- preserving academic document layout when needed
- generating tracked changes for the UI
- preparing content for export

This file is the main improvement engine.

### `core/exporter.py`

Exports improved documents into:

- DOCX
- PDF

It contains document-type-specific layout logic for:

- resumes
- cover letters
- essays
- reports
- proposals
- theses
- general documents

This file handles the final polished output the user downloads.

### `core/change_tracker.py`

Tracks every change made during the improvement process.

Examples:

- phrase replacement
- section added
- spelling fix
- grammar fix
- formatting fix
- rewrite
- reorder

The `/changes` page reads from this log.

## 4. Models

### `models/analysis_result.py`

Defines the data structures used to pass results into the UI.

This usually includes:

- total score
- evaluation status
- document type
- suggestions
- explanation text
- score breakdown
- output filenames

This gives the templates a clean result object instead of many loose variables.

## 5. Services

### `services/grammar_checker.py`

Provides grammar penalty calculation.

It uses LanguageTool if available, and falls back to offline heuristic checks if not.

### `services/languagetool_service.py`

Handles initialization of a local LanguageTool server connection.

This keeps grammar checking offline and controlled.

### `services/formatting_analyzer.py`

Calculates formatting penalties based on text-level structure issues such as inconsistent bullets, spacing, or weak layout signals.

### `services/readability_analyzer.py`

Measures how readable the text is and contributes to the final score.

### `services/keyword_analyzer.py`

Measures keyword richness or required keyword relevance depending on the document type and context.

### `services/ai_client.py`

Handles the low-level AI request flow used by rewriting and explanation services.

This is the shared gateway for AI calls.

### `services/ai_rewriter.py`

Builds prompts and sends AI rewrite requests for:

- full-document rewrite
- section rewrite

It contains different guidance rules for proposals, reports, theses, resumes, and cover letters.

### `services/ai_explainer.py`

Supports AI-generated explanation text when that path is used.

### `services/ml_classifier_service.py`

Loads and applies the machine-learning document classifier when trained model files are available.

### `services/ml_scoring_service.py`

Loads and applies the machine-learning scoring model when available.

These ML services are part of the later AI/ML phase built on top of the rule-based baseline.

## 6. Utilities

### `utils/helpers.py`

Contains helper functions such as directory creation and small reusable utilities.

### `utils/logger.py`

Creates the application logger used across the project.

### `utils/constants.py`

Stores reusable constants shared by multiple modules.

## 7. Templates

### `templates/index.html`

The upload page.

This is where the user:

- chooses a document
- picks a document type or auto detect
- adds requirement notes
- uploads a requirements file
- chooses whether to generate improved output

### `templates/result.html`

Displays the analysis result after processing.

It shows:

- score
- evaluation status
- explanation
- suggestions
- score breakdown
- requirement summary
- AI diagnostics
- download links

### `templates/error.html`

Shows a friendly error page when something goes wrong.

### `templates/changes.html`

Displays tracked changes made during improvement.

This is especially useful for showing what was corrected in resumes, cover letters, reports, and proposals.

## 8. Static Files

### `static/style.css`

Contains the main styling for the web UI.

### `static/script.js`

Contains any client-side UI behavior used by the frontend.

## 9. Training and ML Scripts

### `scripts/export_training_features.py`

Exports feature rows from documents so they can be labeled or used for training.

### `scripts/export_scoring_features.py`

Exports features specifically for scoring-model workflows.

### `scripts/export_scoring_label_sheet.py`

Creates a label sheet for human review and scoring annotation.

### `scripts/apply_scoring_labels.py`

Applies manually entered labels back into the training data pipeline.

### `scripts/train_document_classifier.py`

Trains the ML classifier used to predict document type.

### `scripts/train_document_scorer.py`

Trains the ML model used for quality-score prediction.

Together, these scripts support the AI/ML phase that comes after the original rule-based system.

## 10. How the Code Flows End to End

The normal request flow is:

1. `app.py` receives the uploaded document.
2. `core/file_validator.py` checks whether the file is allowed.
3. `core/parser.py` extracts text and sections.
4. `core/classifier.py` predicts the document type.
5. `core/requirement_engine.py` builds the active requirement profile.
6. `core/scoring_engine.py` calculates the score and breakdown.
7. `core/explanation_engine.py` generates explanation text.
8. `core/improver.py` creates improved content if the user requested it.
9. `core/exporter.py` writes the improved DOCX and PDF.
10. `core/change_tracker.py` feeds the changes view shown in `templates/changes.html`.

## 11. Which Files Matter Most

If someone wants to understand the project quickly, start with these files in this order:

1. `app.py`
2. `core/parser.py`
3. `core/classifier.py`
4. `core/scoring_engine.py`
5. `core/improver.py`
6. `core/exporter.py`
7. `services/ai_rewriter.py`
8. `services/ml_classifier_service.py`
9. `services/ml_scoring_service.py`

These files explain most of the behavior of the application.

## 12. Final Summary

This project is built in layers:

- Flask handles the web flow
- `core/` handles the document pipeline
- `services/` provides grammar, AI, and ML helpers
- `config/` defines rules and formatting profiles
- `templates/` and `static/` define the UI
- `scripts/` support training and data preparation

The rule-based system is still the foundation, while the AI and ML files extend that foundation rather than replacing it.
