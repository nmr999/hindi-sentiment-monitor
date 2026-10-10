"""Load labelled Hindi sentiment data from a CSV or a Hugging Face dataset.

CSV needs columns `text` and `label`. Labels are mapped to negative/neutral/positive.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from normalize import normalize, script_of

LABELS = ["negative", "neutral", "positive"]
ALIASES = {"0": "negative", "1": "neutral", "2": "positive", "neg": "negative", "pos": "positive",
           "neu": "neutral", "negative": "negative", "positive": "positive", "neutral": "neutral"}

def load(source: str, text_col="text", label_col="label", hf_config=None, hf_split=None) -> pd.DataFrame:
    if source.endswith(".csv"):
        df = pd.read_csv(source)
    else:  # Hugging Face dataset id
        from datasets import load_dataset
        ds = load_dataset(source, hf_config)
        df = pd.concat([ds[s].to_pandas() for s in ds], ignore_index=True) if hf_split is None else ds[hf_split].to_pandas()
    cols = {c.lower(): c for c in df.columns}
    def pick(want, cands):
        if want in df.columns: return want
        for c in cands:
            if c in cols: return cols[c]
        raise KeyError(f"No {want} column among {list(df.columns)}; pass --text_col/--label_col")
    tcol = pick(text_col, ["text", "review", "indic review", "sentence", "tweet", "content", "comment"])
    lcol = pick(label_col, ["label", "labels", "sentiment", "polarity", "target"])
    df = df.rename(columns={tcol: "text", lcol: "label"})[["text", "label"]].dropna()
    df["label"] = df["label"].astype(str).str.lower().map(ALIASES)
    df = df.dropna()
    df["clean"] = df["text"].map(normalize)
    df["script"] = df["text"].map(script_of)
    # dedupe BEFORE splitting to avoid leakage
    return df.drop_duplicates(subset="clean").reset_index(drop=True)

def split(df, seed=42):
    train, tmp = train_test_split(df, test_size=0.3, stratify=df.label, random_state=seed)
    dev, test = train_test_split(tmp, test_size=0.5, stratify=tmp.label, random_state=seed)
    return train.reset_index(drop=True), dev.reset_index(drop=True), test.reset_index(drop=True)
