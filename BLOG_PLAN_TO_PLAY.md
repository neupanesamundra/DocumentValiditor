# From Plan to Play: Building a Document Validation System in Two Phases

Every strong intelligent system starts with structure before it starts learning. That is the idea behind our project. Instead of jumping directly into machine learning, we first built a rule-based document validation system that gives reliable, explainable, and practical results. We call this the **Plan** phase. Later, we will extend it into an **AL/ML-based Play** phase, where the system becomes more adaptive and data-driven.

This blog explains the system we have built so far, why we chose this path, and how it prepares us for the next stage.

## Why We Started With a Rule-Based System

Many projects try to begin with AI immediately, but that often creates problems: unclear logic, weak debugging, and difficulty explaining why the system made a decision. For a document analysis platform, explainability matters. A user should know not only the final score, but also the reason behind it.

That is why our first implementation is fully rule-based. This gives us:

- clear scoring logic
- transparent classification
- easy debugging and testing
- reliable baseline performance
- structured data for future machine learning

In short, the rule-based version is not a temporary shortcut. It is the foundation of the whole system.

## What the Current System Does

Our current application is a Flask-based web system that allows users to upload documents and receive an automated quality evaluation. The system currently supports `PDF`, `DOCX`, and `TXT` files.

Once a document is uploaded, the system processes it through a modular pipeline:

1. file validation
2. text parsing
3. document classification
4. requirement resolution
5. rule-based scoring
6. explanation generation
7. optional improved document generation

This pipeline makes the system simple to understand and easy to extend.

## Step 1: Parsing the Uploaded Document

The first task is extracting readable content from the uploaded file. The parser handles different document types separately:

- `PDF` files are read using text extraction with a fallback for difficult layouts
- `DOCX` files are parsed through paragraph-level extraction
- `TXT` files are read directly

After extracting the text, the system also detects sections and calculates word count. This is important because later scoring depends on structure as well as content.

## Step 2: Rule-Based Document Classification

After parsing, the system tries to identify what kind of document the user uploaded. It checks the presence of domain-specific keywords to classify the file as one of the following:

- Resume
- CV
- Report
- Thesis
- Cover Letter
- Essay
- Proposal
- General Document

For example, a resume is identified using terms like `skills`, `experience`, and `education`, while a thesis is recognized through words like `abstract`, `methodology`, and `references`.

This is a keyword-driven classifier, but it already gives a practical and explainable starting point. The user can also manually select a document type instead of relying only on automatic detection.

## Step 3: Requirement-Aware Validation

One of the more useful parts of the system is its requirement engine. Instead of using only a fixed scoring rubric, the system can also adapt validation based on user-provided requirements.

It builds a default requirement profile for each document type, including:

- preferred file formats
- validation focus areas
- minimum word expectations
- expected sections

Then it can merge custom requirements written by the user or uploaded as a separate file. This means the system is not only checking whether a document is good in general, but also whether it matches the intended purpose.

This is an important bridge between static rules and future intelligent personalization.

## Step 4: Quality Scoring With Explainable Rules

The scoring engine is the core of the current project. It produces a score out of 100 using transparent rule-based logic. The score is built from multiple factors:

- section coverage
- content volume
- grammar quality
- formatting consistency
- readability
- keyword relevance
- custom requirement matching
- heading hierarchy checks for DOCX files

For example:

- missing required sections reduces the score
- low word count reduces the score
- grammar issues create penalties
- better readability can add positive points
- strong structure and relevant keywords improve the result

This design gives the system something very important: **reasoned scoring instead of black-box scoring**.

## Step 5: Human-Readable Feedback

A score alone is not very useful if the user does not know how to improve. That is why the system also generates an explanation layer.

Based on the final score, the document is labeled with statuses such as:

- Excellent
- Good
- Needs Improvement
- Needs Revision

The system also returns analysis points and improvement suggestions. For example, if important sections are missing, it explicitly tells the user which sections should be added. If grammar or formatting is weak, it highlights those areas too.

This makes the application not just an evaluator, but also a guidance tool.

## Step 6: Optional Improved Document Generation

Another useful feature in the current system is automatic document improvement. If enabled, the system can generate improved `DOCX` and `PDF` outputs after analysis.

The improvement module currently focuses on safe and practical transformations such as:

- cleaning noisy text
- normalizing spacing
- improving section organization
- repairing heading hierarchy
- polishing wording conservatively
- preserving layout where possible

There is also a safeguard check: if the improved version scores lower than the original, the system records that outcome instead of blindly presenting it as better. This is a strong design choice because it keeps trust in the system.

## Why This Phase Is Called "Plan"

We call the current phase **Plan** because it defines the intelligence structure of the project before learning begins. The system already knows:

- what to look for
- how to interpret quality
- how to measure compliance
- how to explain decisions

This phase is rule-driven, modular, and controlled. It helps us understand the problem deeply before we let the model learn from data.

In other words, the system first learns the rules from us, and later it will learn patterns from data.

## The Future "Play" Phase: AL/ML-Based Evolution

The next stage of this project will be the **Play** phase. In this phase, the system will move beyond fixed rules and become more adaptive using active learning and machine learning.

The current codebase already hints at this direction through the training scaffold and feature-export workflow. That means the rule-based engine is not separate from the future ML system. It is preparing the dataset, scoring signals, and validation structure that an ML pipeline can later use.

In the Play phase, we plan to convert parts of the current logic into learned models that can:

- predict document quality from labeled examples
- learn better scoring weights from data
- improve classification accuracy
- adapt to domain-specific writing styles
- reduce rigid dependence on keyword matching
- support smarter recommendations

Active learning can make this even stronger by allowing the system to improve from selected user feedback instead of requiring a massive labeled dataset from the beginning.

## Why the Two-Phase Approach Matters

Building this project in two stages gives us both stability and growth.

The **Plan** phase gives us:

- transparency
- baseline accuracy
- modular engineering
- explainable output
- training data preparation

The **Play** phase will give us:

- adaptability
- better generalization
- data-driven optimization
- smarter recommendations
- long-term scalability

This approach is more realistic than jumping directly into ML, especially for academic and production-oriented projects where trust and explainability are essential.

## Final Thoughts

Our project is currently a rule-based document validation and improvement system, but its real strength is that it has been designed as a stepping stone toward a smarter adaptive platform.

Today, it can parse documents, classify them, score them, explain the score, and even generate improved versions. Tomorrow, it can evolve into an AL/ML-powered system that learns from data and user feedback.

That is why this project is best described in two parts:

- **Plan**: build the rule-based intelligence correctly
- **Play**: convert that intelligence into a learning system later

We are not replacing the first phase with the second. We are building the second phase on top of the first one.

And that is what makes this system meaningful: it is not only working now, it is also ready to grow.
