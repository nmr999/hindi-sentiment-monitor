"""Baselines: TF-IDF (word + char n-grams) with Naive Bayes and Logistic Regression.
Vectorizer is fit on TRAIN only. Reports macro-F1 and per-class metrics on dev and test.
Usage: python src/baseline.py --source data/hindi.csv
"""
import argparse, json, joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, classification_report
from data import load, split, LABELS

def features():
    return make_union(
        TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, token_pattern=r"(?u)[\wऀ-ॿ]+"),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True))

MODELS = {
    "naive_bayes": lambda: make_pipeline(features(), MultinomialNB(alpha=0.5)),
    "logreg": lambda: make_pipeline(features(), LogisticRegression(max_iter=2000, C=3, class_weight="balanced")),
}

def evaluate(model, df, name):
    pred = model.predict(df.clean)
    rep = classification_report(df.label, pred, labels=LABELS, output_dict=True, zero_division=0)
    return {"split": name, "macro_f1": f1_score(df.label, pred, average="macro", labels=LABELS, zero_division=0),
            "per_class": {k: rep[k] for k in LABELS}}, pred

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True); ap.add_argument("--text_col", default="text")
    ap.add_argument("--label_col", default="label"); ap.add_argument("--hf_config", default=None)
    a = ap.parse_args()
    df = load(a.source, a.text_col, a.label_col, a.hf_config)
    train, dev, test = split(df)
    print(df.label.value_counts(normalize=True).round(3).to_dict(), "n =", len(df))
    out = {}
    for name, mk in MODELS.items():
        m = mk().fit(train.clean, train.label)
        d, _ = evaluate(m, dev, "dev"); t, pred = evaluate(m, test, "test")
        out[name] = {"dev": d, "test": t}
        print(f"{name:12s} dev macro-F1={d['macro_f1']:.3f}  test macro-F1={t['macro_f1']:.3f}  "
              f"neutral F1={t['per_class']['neutral']['f1-score']:.3f}")
        test.assign(pred=pred).to_csv(f"results/{name}_test_preds.csv", index=False)
        joblib.dump(m, f"results/{name}.joblib")
    json.dump(out, open("results/baseline_metrics.json", "w"), indent=2)
