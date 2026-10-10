"""Improved model: negation-aware features + hyperparameter tuning on DEV, then one test evaluation.
Also reports 95% bootstrap CIs and 5-fold CV so the numbers carry uncertainty.
Usage: python src/improved.py --source data/hindi.csv
"""
import argparse, json, re, joblib, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import f1_score
from data import load, split, LABELS

NEG = {"नहीं", "नही", "ना", "न", "मत", "बिना", "नहि", "कभी_नहीं"}
TOK = re.compile(r"[\wऀ-ॿ]+|[।.!?,;]")

def neg_mark(texts, window=3):
    """Prefix the `window` tokens after a negation word with NEG_ (stops at punctuation).
    Example: 'कोई सुधार नहीं हुआ' -> 'कोई सुधार नहीं NEG_हुआ'. Also marks the 2 tokens BEFORE the
    negator, because Hindi places it after the noun ('सुधार नहीं')."""
    out = []
    for t in texts:
        toks = TOK.findall(t); res = list(toks)
        for i, w in enumerate(toks):
            if w in NEG:
                for j in range(max(0, i - 2), i):
                    if toks[j] not in "।.!?,;": res[j] = "NEG_" + toks[j]
                for j in range(i + 1, min(len(toks), i + 1 + window)):
                    if toks[j] in "।.!?,;": break
                    res[j] = "NEG_" + toks[j]
        out.append(" ".join(res))
    return out

def feats():
    word = make_pipeline(FunctionTransformer(neg_mark), TfidfVectorizer(ngram_range=(1, 2), min_df=2, token_pattern=r"(?u)[\wऀ-ॿ]+"))
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)
    return make_union(word, char)

def build(kind, C):
    clf = LogisticRegression(max_iter=3000, C=C, class_weight="balanced") if kind == "logreg" else LinearSVC(C=C, class_weight="balanced")
    return make_pipeline(feats(), clf)

def macro(y, p): return f1_score(y, p, average="macro", labels=LABELS, zero_division=0)

def boot_ci(y, p, n=1000, seed=0):
    rng = np.random.default_rng(seed); y = np.array(y); p = np.array(p); s = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y)); s.append(macro(y[i], p[i]))
    return [float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--source", required=True); a = ap.parse_args()
    df = load(a.source); train, dev, test = split(df)
    best = None
    for kind in ["logreg", "svm"]:
        for C in [0.3, 1, 3, 10, 30]:
            m = build(kind, C).fit(train.clean, train.label); d = macro(dev.label, m.predict(dev.clean))
            print(f"dev {kind:6s} C={C:<5} macro-F1={d:.3f}")
            if best is None or d > best[0]: best = (d, kind, C)
    d, kind, C = best; print("selected on DEV:", kind, C, round(d, 3))
    m = build(kind, C).fit(train.clean, train.label); pred = m.predict(test.clean)
    t = macro(test.label, pred); ci = boot_ci(test.label, pred)
    base = joblib.load("results/logreg.joblib"); bp = base.predict(test.clean)
    bt = macro(test.label, bp); bci = boot_ci(test.label, bp)
    nb = joblib.load("results/naive_bayes.joblib"); nbp = nb.predict(test.clean)
    cv = cross_val_score(build(kind, C), df.clean, df.label, cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1_macro")
    cvb = cross_val_score(joblib.load("results/logreg.joblib"), df.clean, df.label, cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1_macro")
    # how many baseline errors involving negation does the improved model fix?
    err = test.assign(base=bp, imp=pred)
    be = err[err.label != err.base]; fixed = int((be.imp == be.label).sum())
    out = {"selected": {"model": kind, "C": C, "dev_macro_f1": d},
           "test": {"naive_bayes": macro(test.label, nbp), "baseline_logreg": bt, "baseline_logreg_ci95": bci,
                    "improved": t, "improved_ci95": ci},
           "cv5_macro_f1": {"baseline_logreg": [float(cvb.mean()), float(cvb.std())], "improved": [float(cv.mean()), float(cv.std())]},
           "baseline_errors": int(len(be)), "baseline_errors_fixed_by_improved": fixed,
           "new_errors_introduced": int(((err.label == err.base) & (err.label != err.imp)).sum())}
    json.dump(out, open("results/improved_metrics.json", "w"), indent=2)
    err.to_csv("results/improved_test_preds.csv", index=False); joblib.dump(m, "results/improved.joblib")
    print(json.dumps(out, indent=1))
