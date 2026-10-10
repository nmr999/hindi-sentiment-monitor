"""No-Streamlit fallback demo: python demo_cli.py "यह फोन बहुत अच्छा है" "आज मौसम सामान्य है" """
import sys; sys.path.insert(0, "src")
from normalize import normalize, script_of
try:
    import joblib; m = joblib.load("results/logreg.joblib")
except Exception:                       # different scikit-learn version: retrain in a few seconds
    from data import load
    from baseline import MODELS
    d = load("data/hindi.csv"); m = MODELS["logreg"]().fit(d.clean, d.label)
for t in sys.argv[1:] or ["यह फोन बहुत अच्छा है", "मुझे यह बिल्कुल पसंद नहीं आया", "आज मौसम सामान्य है"]:
    p = m.predict_proba([normalize(t)])[0]
    print(f"{t}  ->  {m.classes_[p.argmax()]} ({p.max():.2f}) [{script_of(t)}]")
