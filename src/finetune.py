"""Fine-tune a multilingual transformer (run on Colab GPU).
Usage: python src/finetune.py --source data/hindi.csv --model google/muril-base-cased
Other candidates: xlm-roberta-base, ai4bharat/IndicBERTv2-MLM-only, l3cube-pune/hing-bert (Hinglish)
"""
import argparse, os, numpy as np, torch
os.makedirs("results", exist_ok=True)
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import f1_score
from data import load, split, LABELS

ap = argparse.ArgumentParser()
ap.add_argument("--source", required=True); ap.add_argument("--model", default="google/muril-base-cased")
ap.add_argument("--epochs", type=int, default=3); ap.add_argument("--out", default="results/finetuned")
a = ap.parse_args()
l2i = {l: i for i, l in enumerate(LABELS)}
train, dev, test = split(load(a.source))
tok = AutoTokenizer.from_pretrained(a.model)
def enc(df):
    ds = Dataset.from_dict({"text": df.clean.tolist(), "label": [l2i[l] for l in df.label]})
    return ds.map(lambda b: tok(b["text"], truncation=True, max_length=128), batched=True)
model = AutoModelForSequenceClassification.from_pretrained(a.model, num_labels=3)
def metrics(p):
    return {"macro_f1": f1_score(p.label_ids, p.predictions.argmax(-1), average="macro")}
import inspect as _i
_ev = "eval_strategy" if "eval_strategy" in _i.signature(TrainingArguments.__init__).parameters else "evaluation_strategy"
args = TrainingArguments(a.out, per_device_train_batch_size=32, learning_rate=3e-5, num_train_epochs=a.epochs,
                         **{_ev: "epoch"}, save_strategy="epoch", load_best_model_at_end=True,
                         metric_for_best_model="macro_f1", fp16=torch.cuda.is_available(), report_to="none")
import inspect
tok_kw = "processing_class" if "processing_class" in inspect.signature(Trainer.__init__).parameters else "tokenizer"
tr = Trainer(model=model, args=args, train_dataset=enc(train), eval_dataset=enc(dev),
             compute_metrics=metrics, **{tok_kw: tok})
tr.train()
res = tr.evaluate(enc(test), metric_key_prefix="test"); print("TEST:", res)
import json; json.dump({"model": a.model, "test_macro_f1": res["test_macro_f1"]}, open("results/finetune_metrics.json", "w"))
tr.save_model(a.out); tok.save_pretrained(a.out)
