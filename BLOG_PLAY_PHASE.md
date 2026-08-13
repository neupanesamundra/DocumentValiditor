# Play Phase Completed: Turning Our Rule-Based System Into an AL/ML-Powered Document Intelligence Pipeline

In the first phase of our project, we built the **Plan** system: a rule-based document validator that could parse files, classify document types, score quality, explain results, and generate improved outputs. That phase gave us structure, transparency, and a dependable baseline.

Now the next phase, which we call **Play**, is done.

This phase transforms the project from a fixed rule engine into a more adaptive **AL/ML-based system**. Instead of depending only on manually written rules, the platform can now learn from labeled examples, predict document types using trained models, and estimate document quality through machine learning.

This blog explains what the Play phase adds, how it works, and why it is an important step forward for the project.

## Why We Needed the Play Phase

Rule-based systems are excellent for building a foundation, but they have limits. They are precise only for the patterns they already know. If the writing style changes, if the document structure is unusual, or if two document categories share similar keywords, a rule-only system can become rigid.

That is where the Play phase becomes important.

The goal of this phase was to make the system:

- more adaptive
- more data-driven
- less dependent on fixed keyword rules
- more scalable for future datasets
- ready for active learning and continuous improvement

The Play phase does not remove the original system. It builds on top of it. The rule-based engine still acts as the baseline, while the ML layer adds learned intelligence.

## What Is Completed in the Play Phase

The project now includes a full offline AL/ML workflow:

1. document collection for training
2. feature export for classification and scoring
3. human labeling structure
4. classifier training
5. scoring model training
6. model loading inside the application
7. ML-assisted prediction during runtime

This means the Play phase is no longer a future idea. It is now part of the working architecture.

## Training Data Preparation

One of the strongest parts of this phase is the training pipeline. The project now contains a dedicated `data/training` structure with:

- classification sample documents
- scoring datasets in JSONL format
- a labeling template
- scoring label sheets
- exported unlabeled feature data

This matters because machine learning is only as good as its training data. Instead of treating data collection as an afterthought, the system now includes a proper training workflow from the start.

For classification, the dataset includes categorized samples such as:

- Resume
- CV
- Cover Letter
- Essay
- Proposal
- Report
- Thesis

For scoring, the dataset stores not only extracted features but also:

- baseline rule-based scores
- human-reviewed overall scores
- criterion-level labels
- reviewer notes

This is a major shift from static engineering to learnable intelligence.

## Classification Model: From Keywords to Learned Prediction

In the Plan phase, document classification was done using keyword matching. That was useful and explainable, but limited.

In the Play phase, the project now includes an **offline machine learning document classifier**. The training script builds a text classification pipeline using:

- `TF-IDF` vectorization
- `Logistic Regression`

This model learns directly from document text instead of depending only on a hardcoded keyword list.

At runtime, the application first tries the ML classifier. If a trained model is available, it predicts the document type from the content. If the model is unavailable, the system safely falls back to the original rule-based classifier.

This is a strong design choice because it gives the project both:

- intelligence when the trained model is available
- reliability when the model is missing or disabled

So the system has become smarter without becoming fragile.

## Scoring Model: Learning Document Quality From Features

Another major upgrade in the Play phase is the ML-based scoring system.

In the earlier version, the score came only from rule-based logic such as:

- section coverage
- grammar penalties
- formatting penalties
- readability
- keyword relevance
- heading hierarchy

Now, those same signals are also converted into machine-readable features through the scoring feature extractor. These features are used to train a regression model that predicts overall document quality.

The scoring model uses:

- structured feature dictionaries
- `DictVectorizer`
- `RandomForestRegressor`

This means the system is no longer limited to manually fixed weight values. Instead, it can learn scoring behavior from labeled examples.

At runtime, the scoring engine still computes the original rule-based score first. Then, if the trained ML scorer is available, the system applies the ML prediction and uses it as the final score. It also records that ML scoring was applied.

This hybrid design is important because it gives us:

- interpretable feature engineering
- data-driven score prediction
- continuity with the original rule system

## The Role of Active Learning

The Play phase is also meaningful from an **active learning** perspective.

The project now has the components needed for a feedback-driven loop:

- documents can be exported into training-ready records
- baseline predictions can be captured
- humans can review and label outputs
- reviewer notes can be stored with scores
- new labels can be fed back into retraining

This creates the foundation for active learning, where the model improves gradually from curated feedback instead of needing a perfect large dataset from the beginning.

In other words, the project now supports a realistic path for continuous model improvement.

## Why This Phase Is Called "Play"

We call this phase **Play** because this is where the system starts learning from experience.

In the Plan phase, we taught the system using handcrafted logic. In the Play phase, we allow the system to observe examples, discover patterns, and improve predictions using trained models.

This is the point where the project becomes more than a rule engine. It becomes a learning system.

The word "play" fits well because the system is no longer only following instructions. It is now interacting with data, testing learned patterns, and producing decisions that come from both engineering and training.

## Key Strengths of the Current Play Phase

The completed Play phase gives the project several major strengths:

- ML classification with safe fallback to rules
- ML-based score prediction built on extracted quality features
- offline training workflow
- reusable labeled datasets
- support for human-in-the-loop review
- clear separation between feature extraction, training, and runtime prediction
- scalable architecture for future retraining

This is especially useful for an academic project because it demonstrates both software engineering depth and machine learning integration.

## How Plan and Play Work Together

The most important thing about this project is that Plan and Play are not competing ideas. They work together.

The **Plan** phase provides:

- domain rules
- document parsing
- baseline scoring logic
- explainability
- structured feature generation

The **Play** phase adds:

- learned classification
- learned score prediction
- labeling workflows
- retraining capability
- future active learning support

The first phase made the system understandable. The second phase made it adaptive.

That combination is what makes the project strong.

## Final Thoughts

The Play phase is now complete, and it marks a big milestone in the evolution of the project.

What started as a rule-based document validation tool has now grown into a hybrid document intelligence system that combines:

- software engineering
- explainable rules
- machine learning models
- human labeling workflows
- future active learning capability

This phase proves that the project is not only able to analyze documents, but also able to learn from them.

So if the first phase was about planning intelligence, the second phase is about making that intelligence learn in practice.

That is the real meaning of our project journey:

- **Plan** built the logic
- **Play** taught the system to learn

And together, they turn the project into a smarter and more scalable document evaluation platform.
