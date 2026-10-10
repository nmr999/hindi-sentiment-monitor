import pandas as pd, joblib, streamlit as st, sys
sys.path.insert(0, "src")
from normalize import normalize, script_of
st.title("Hindi Sentiment Monitor")
@st.cache_resource
def get_model():
    try: return joblib.load("results/logreg.joblib")
    except Exception:   # sklearn version mismatch or missing file: retrain quickly
        from data import load
        from baseline import MODELS
        d = load("data/hindi.csv"); return MODELS["logreg"]().fit(d.clean, d.label)
model = get_model()
txt = st.text_area("Paste posts (one per line)") 
up = st.file_uploader("...or upload CSV with a `text` column", type="csv")
posts = [l for l in txt.splitlines() if l.strip()]
if up: posts += pd.read_csv(up)["text"].astype(str).tolist()
if posts:
    df = pd.DataFrame({"text": posts}); df["clean"] = df.text.map(normalize)
    df["script"] = df.text.map(script_of); df["sentiment"] = model.predict(df.clean)
    st.subheader("Overall"); st.bar_chart(df.sentiment.value_counts())
    st.subheader("By script (Devanagari vs Hinglish)")
    st.dataframe(pd.crosstab(df.script, df.sentiment))
    st.dataframe(df[["text", "script", "sentiment"]])
    st.caption("Not reliable for sarcasm, slang, very short posts, or brand-specific jargon.")
