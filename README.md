# Hindi Sentiment Monitor
MSDS 630 Residency NLP Hackathon, Project 4 (Sauti ya Soko) adapted to **Hindi only** (instructor-approved).
Classifies Hindi text as negative / neutral / positive and shows a sentiment breakdown for a batch of posts.

## Data
`data/hindi.csv`: SentiHin-2500, Hugging Face dataset `MLap/SentiHin-2500` (https://huggingface.co/datasets/MLap/SentiHin-2500, `train.csv`; we first received the same file via Kaggle as "hindi_sentiment_analysis_dedup"). 2,500 short Devanagari sentences (positive 955, negative 848, neutral 697).
After our own normalization-based de-duplication: 2,498 rows. Split 70/15/15, stratified, seed 42.
**License:** the dataset page lists no license, only the link above. We used it as public data for coursework under the hackathon's public-data rule and do not redistribute it beyond this repository. Check the page for any later license or citation notice.
Caveat: sentences are short and templated, so scores are optimistic (about 43% of test sentences have a close pattern match in train).

## Setup
Use **Python 3.10 or newer** (3.7 is too old). Demo only: `pip install -r requirements-demo.txt`.
Full pipeline and fine-tuning (best on Colab): `pip install -r requirements.txt`.

## Reproduce everything
    python run_all.py --csv data/hindi.csv --team "Isha Joshi, Manikantha Kothamasu, Sowseelyatha Mutharaju, Muralidhar Reddy Nandi, Rohan Sabbani" --name "SentiHin-2500 (Hugging Face MLap/SentiHin-2500)"
Writes `results/*`, `slides.pptx`, `technical_summary.docx`. Optional on a Colab GPU: add `--finetune` (MuRIL).

## Demo
    streamlit run app.py          # batch dashboard (paste posts or upload CSV with a `text` column)
    python demo_cli.py "यह फोन बहुत अच्छा है"     # no-Streamlit fallback
Runs offline. If `results/logreg.joblib` can't load, `app.py` retrains from `data/hindi.csv` automatically.

## Results (test set, 375 sentences, macro-F1)
| Model | Macro-F1 | 95% CI | Neg F1 | Neu F1 | Pos F1 |
|---|---|---|---|---|---|
| Naive Bayes (TF-IDF word+char) | 0.895 | n/a | 0.87 | 0.92 | 0.89 |
| Logistic Regression (baseline) | 0.945 | 0.921 to 0.966 | 0.93 | 0.96 | 0.95 |
| LR + negation-aware features (tuned on dev) | 0.944 | 0.920 to 0.965 | see results/improved_metrics.json | | |
| **Fine-tuned MuRIL (`google/muril-base-cased`)** | **0.975** | single run, none computed | not recorded | | |

5-fold CV macro-F1: baseline 0.958 ± 0.006, with negation features 0.963 ± 0.008 (difference within noise).
Negation-aware features fixed 2 of the baseline's 21 errors and introduced 2 new ones, so we report **no improvement**.
MuRIL was fine-tuned on a Colab T4 GPU with `src/finetune.py` (same split, best epoch chosen on dev, test used once). It is a single run, so we report no confidence interval and treat the roughly 3-point gain over logistic regression as likely but not proven. The live demo uses the logistic regression model, which runs offline on a laptop.
Error analysis: `results/errors_labeled.csv` (all 21 baseline errors hand-labeled by cause), summary in `results/error_analysis.json`.

## Layout
`src/normalize.py` text normalization · `src/data.py` loading, de-dup, split · `src/baseline.py` baselines + metrics · `src/improved.py` negation-aware model, tuning, CIs, CV ·
`src/analyze.py` per-script breakdown · `src/finetune.py` transformer fine-tuning · `app.py` demo · `make_submission.py` slides + summary.

## Team and roles
Roles confirmed by the team; this table is the final split.

| Member | Role | Contribution |
|---|---|---|
| Manikantha Kothamasu | Team Lead / PM | Scope, timeline, stand-ups, cut decisions; presents the problem (0-1 min), limitations and next steps (8-10 min) |
| Rohan Sabbani | Data Engineer | Dataset selection, cleaning, normalization, de-duplication, splits (`src/normalize.py`, `src/data.py`); presents the data slide |
| Muralidhar Reddy Nandi | Modeling Lead | Naive Bayes, logistic regression, negation-aware model, fine-tuning script (`src/baseline.py`, `src/improved.py`, `src/finetune.py`); presents the approach |
| Sowseelyatha Mutharaju | Evaluation Lead | Macro-F1 harness, confidence intervals, CV, leakage checks, error analysis (`src/analyze.py`, `results/errors_labeled.csv`); presents results (6-8 min) |
| Isha Joshi | Product & Demo Lead | Streamlit dashboard, CLI fallback, slides (`app.py`, `demo_cli.py`); runs the live demo (3-6 min) |

## AI tool disclosure
**Tool used:** Claude (Anthropic), an AI assistant, helped draft the starter code, the slide deck, the one-page technical summary, the Colab fine-tuning notebook and the first labeling of model errors.

**What Claude produced:** `src/normalize.py`, `src/data.py`, `src/baseline.py`, `src/improved.py`, `src/finetune.py`, `src/analyze.py`, `app.py`, `demo_cli.py`, `run_all.py`, `make_submission.py`, `build_pptx.py`, the Colab notebook, and drafts of the slides, summary and README.

**What our team did ourselves:**
- Chose the project, got instructor approval to work on Hindi only, and found and supplied the dataset (SentiHin-2500).
- Ran the fine-tuning of `google/muril-base-cased` ourselves on a Colab GPU and reported its test macro-F1 (0.975).
- Installed Python 3.12 on a team laptop, ran the Streamlit demo, and took the demo screenshots used on slide 5.
- A Hindi speaker on the team checked and validated all 21 error-cause labels in `results/errors_labeled.csv`.
- Reviewed the slides, summary and code, and assigned and confirmed roles.

**Accountability:** every member has read the code and can explain any line in Q&A. Numbers in the slides and summary are generated from the result files in `results/`, not typed by hand.
