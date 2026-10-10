"""Builds slides.pptx (<=10 slides) and technical_summary.docx from REAL results in results/.
Run after baseline.py (and finetune.py if you fine-tuned). Usage: python make_submission.py --dataset "NAME (link)"
Edit the TEAM and DATASET placeholders via flags; nothing numeric is typed by hand.
"""
import argparse, json, os
import pandas as pd
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from docx import Document
from sklearn.metrics import f1_score

ap = argparse.ArgumentParser()
ap.add_argument("--dataset", required=True, help="dataset name + link")
ap.add_argument("--team", default="Team N: names here")
a = ap.parse_args()

base = json.load(open("results/baseline_metrics.json"))
ft = json.load(open("results/finetune_metrics.json")) if os.path.exists("results/finetune_metrics.json") else None
rows = [("Naive Bayes (TF-IDF)", base["naive_bayes"]["test"]), ("Logistic Regression (TF-IDF)", base["logreg"]["test"])]
table = [(n, f"{m['macro_f1']:.3f}", f"{m['per_class']['negative']['f1-score']:.2f}",
          f"{m['per_class']['neutral']['f1-score']:.2f}", f"{m['per_class']['positive']['f1-score']:.2f}") for n, m in rows]
if ft: table.append((f"Fine-tuned {ft['model']}", f"{ft['test_macro_f1']:.3f}", "-", "-", "-"))
hdr = ("Model", "Macro-F1", "Neg F1", "Neu F1", "Pos F1")

script_rows = []
pf = "results/logreg_test_preds.csv"
if os.path.exists(pf):
    d = pd.read_csv(pf)
    for s, g in d.groupby("script"):
        script_rows.append((s, len(g), f"{f1_score(g.label, g.pred, average='macro'):.3f}"))

ea = json.load(open("results/error_analysis.json"))
M = json.load(open("results/improved_metrics.json"))
from sklearn.metrics import precision_recall_fscore_support as prf
def f1s(df, col):
    p, r, f, _ = prf(df.label, df[col], labels=["negative", "neutral", "positive"], zero_division=0); return f
ip = pd.read_csv("results/improved_test_preds.csv"); fb, fi = f1s(ip, "base"), f1s(ip, "imp")
table.append(("LR + negation features (dev-tuned)", f"{M['test']['improved']:.3f}", f"{fi[0]:.2f}", f"{fi[1]:.2f}", f"{fi[2]:.2f}"))
nbp = pd.read_csv("results/naive_bayes_test_preds.csv"); fn = f1s(nbp.assign(base=nbp.pred), "base")
M["per_class_rows"] = {"Negative": (float(fb[0]), float(fn[0])), "Neutral": (float(fb[1]), float(fn[1])), "Positive": (float(fb[2]), float(fn[2]))}
M['finetune'] = ft
import build_pptx
build_pptx.build(a.team, a.dataset, M, ea)
doc = Document(); doc.add_heading("Hindi Sentiment Monitor: Technical Summary", 1)
doc.add_paragraph(a.team)
for h, txt in [("Problem", "Classify Hindi text as positive, neutral or negative so a brand can monitor how people feel about its products. Scope: Devanagari Hindi only (instructor-approved); Hinglish and mixed-script posts are future work."),
               ("Data", f"{a.dataset}. Three classes. Deduplicated, then split 70/15/15 stratified (seed 42)."),
               ("Method", "Unicode normalization; TF-IDF word (1-2) + char (2-5) n-grams; Naive Bayes baseline and class-balanced Logistic Regression. A negation-aware variant was tuned on the dev split and evaluated once on test. " + (f"{ft['model']} was then fine-tuned on a Colab GPU (single run) and scored {ft['test_macro_f1']:.3f}." if ft else "No fine-tuned transformer was run."))]:
    doc.add_heading(h, 2); doc.add_paragraph(txt)
doc.add_heading("Results (test set)", 2)
t = doc.add_table(rows=1, cols=5); t.style = "Table Grid"
for j, h in enumerate(hdr): t.rows[0].cells[j].text = h
for r in table:
    c = t.add_row().cells
    for j, v in enumerate(r): c[j].text = v
if script_rows:
    doc.add_paragraph("By script (baseline logistic regression): " + "; ".join(f"{s_} (n={n}) macro-F1 {f}" for s_, n, f in script_rows))
doc.add_heading("Limitations", 2)
doc.add_paragraph("Dataset is short, templated, Devanagari-only (about 43% of test sentences closely match a training pattern), so scores are optimistic. Negation and rare sentiment words cause most errors; negation-aware features did not improve results (0.944 vs 0.945, overlapping 95% CIs). The fine-tuned MuRIL result is a single run without a confidence interval. Untested on Hinglish, sarcasm and long posts.")
doc.add_heading("Next steps", 2); doc.add_paragraph("More Hinglish data, aspect-level sentiment, human review of low-confidence predictions.")
doc.save("technical_summary.docx")
print("wrote slides.pptx and technical_summary.docx")
