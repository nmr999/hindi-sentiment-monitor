"""Error analysis: macro-F1 by script type (Devanagari / romanized / mixed) and dump misclassifications.
Usage: python src/analyze.py results/logreg_test_preds.csv
"""
import sys, pandas as pd
from sklearn.metrics import f1_score
df = pd.read_csv(sys.argv[1])
for s, g in df.groupby("script"):
    print(f"{s:11s} n={len(g):5d} macro-F1={f1_score(g.label, g.pred, average='macro'):.3f}")
err = df[df.label != df.pred]
err.sample(min(40, len(err)), random_state=0).to_csv("results/errors_to_label.csv", index=False)
print("wrote results/errors_to_label.csv -> add a 'cause' column by hand (sarcasm/negation/code-mix/slang/label-noise)")
print(pd.crosstab(df.label, df.pred))
