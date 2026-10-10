"""ONE COMMAND to produce everything: python run_all.py [--hf ai4bharat/IndicSentiment --hf_config translation-hi]
or: python run_all.py --csv data/hindi.csv     (any CSV with text,label columns, e.g. from Kaggle)
Runs baselines, error export, optional fine-tune (--finetune), then builds slides.pptx + technical_summary.docx.
"""
import argparse, subprocess, sys
ap = argparse.ArgumentParser()
ap.add_argument("--csv"); ap.add_argument("--hf"); ap.add_argument("--hf_config")
ap.add_argument("--finetune", action="store_true"); ap.add_argument("--model", default="google/muril-base-cased")
ap.add_argument("--team", default="Team N: names"); ap.add_argument("--name", default=None)
a = ap.parse_args()
src = a.csv or a.hf
if not src: sys.exit("give --csv or --hf")
run = lambda *c: subprocess.run([sys.executable, *c], check=True)
b = ["src/baseline.py", "--source", src] + (["--hf_config", a.hf_config] if a.hf_config else [])
run(*b); run("src/analyze.py", "results/logreg_test_preds.csv"); run("src/improved.py", "--source", src)
if a.finetune: run("src/finetune.py", "--source", src, "--model", a.model)
run("make_submission.py", "--dataset", a.name or src, "--team", a.team)
print("DONE. Now: label results/errors_to_label.csv, fill error-analysis slide + README roles, push to GitHub.")
