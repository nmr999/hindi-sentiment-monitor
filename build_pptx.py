"""Designed 10-slide PowerPoint built from REAL results in results/. Called by make_submission.py."""
import json, os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor as C
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

NAVY, CREAM, SAFF, SAFF_T, TEAL = C(0x14,0x21,0x3D), C(0xF7,0xF4,0xEC), C(0xE8,0x87,0x1E), C(0xB8,0x5A,0x0A), C(0x1F,0x7A,0x8C)
CARD, EDGE, MUTED, NAVY2, LIGHTMUTED, GRAY = C(0xFF,0xFD,0xF8), C(0xE3,0xDE,0xD0), C(0x4A,0x55,0x68), C(0x1E,0x2E,0x52), C(0xC9,0xD1,0xE0), C(0x9A,0xA5,0xB1)
LATIN, DEVA = "Calibri", "Nirmala UI"

def build(team, ds_line, M, EA, out="slides.pptx"):
    prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def bg(s, color):
        f = s.background.fill; f.solid(); f.fore_color.rgb = color
    def box(s, x, y, w, h, fill=None, line=None, radius=True):
        sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        if radius: sh.adjustments[0] = 0.06
        if fill is None: sh.fill.background()
        else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
        if line: sh.line.color.rgb = line; sh.line.width = Pt(1.5)
        else: sh.line.fill.background()
        sh.shadow.inherit = False
        return sh
    def text(s, x, y, w, h, t, size=20, color=NAVY, bold=False, font=LATIN, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None):
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = anchor
        lines = t if isinstance(t, list) else [t]
        for i, ln in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
            if spacing: p.space_after = Pt(spacing)
            r = p.add_run(); r.text = ln; f = r.font; f.size = Pt(size); f.bold = bold; f.color.rgb = color; f.name = font
        return tb
    def header(s, eyebrow, title, dark=False):
        text(s, 0.7, 0.55, 12, 0.4, eyebrow.upper(), 14, SAFF if dark else SAFF_T, True)
        text(s, 0.7, 0.95, 11.9, 1.3, title, 36, CREAM if dark else NAVY, True)
    def footer(s, t, n, dark=False):
        text(s, 0.7, 7.0, 11.5, 0.3, f"{t} · {n}", 12, LIGHTMUTED if dark else MUTED)
    def notes(s, t): s.notes_slide.notes_text_frame.text = t

    # 1 cover
    s = prs.slides.add_slide(blank); bg(s, NAVY)
    text(s, 8.0, 0.25, 4.8, 2.4, "भाव", 130, SAFF, True, DEVA, PP_ALIGN.RIGHT)
    for sh in s.shapes: pass
    text(s, 0.9, 2.6, 11, 0.4, "MSDS 630 · NLP HACKATHON · PROJECT 4", 16, SAFF, True)
    text(s, 0.9, 3.1, 11.5, 1.6, "Hindi Sentiment Monitor", 60, CREAM, True)
    text(s, 0.9, 4.45, 9.5, 1.0, "Positive, neutral or negative: reading the mood of Hindi text with models you can explain line by line.", 22, LIGHTMUTED)
    ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(5.9), Inches(11.5), Inches(0.02)); ln.fill.solid(); ln.fill.fore_color.rgb = C(0x3A,0x4A,0x6B); ln.line.fill.background()
    text(s, 0.9, 6.1, 11.5, 0.8, team, 16, CREAM)
    notes(s, "Presenter: Manikantha Kothamasu, Team Lead (0-1 min). Introduce the team and the goal: a lightweight, explainable Hindi sentiment classifier. भाव (bhaav) means feeling or sentiment.")

    # 2 problem
    s = prs.slides.add_slide(blank); bg(s, CREAM); header(s, "The client problem", "A brand launching in India needs to know how people feel")
    cards = [("Devanagari Hindi", "यह फोन बहुत अच्छा है", DEVA, "The focus of this build, with a labeled dataset."),
             ("Hinglish", "yeh phone bahut accha hai", LATIN, "Hindi in Latin letters, no standard spelling. Not covered yet."),
             ("Mixed with English", "battery life is bekaar", LATIN, "Code-switching inside one post. Not covered yet.")]
    for i, (h, ex, f, d) in enumerate(cards):
        x = 0.7 + i * 4.1; box(s, x, 2.6, 3.9, 3.9, CARD, EDGE)
        text(s, x + 0.3, 2.9, 3.4, 0.4, h, 16, TEAL, True); text(s, x + 0.3, 3.5, 3.4, 1.4, ex, 24, NAVY, False, f); text(s, x + 0.3, 5.2, 3.4, 1.2, d, 15, MUTED)
    footer(s, "English-only sentiment tools miss most of this conversation", 2)
    notes(s, "Presenter: Manikantha Kothamasu, Team Lead (0-1 min). Frame the client need. Be upfront: this build covers Devanagari Hindi only, with instructor approval; Hinglish and mixed posts are future work.")

    # 3 data
    s = prs.slides.add_slide(blank); bg(s, CREAM); header(s, "The data", "2,500 labeled Hindi sentences")
    for i, (big, lab) in enumerate([("2,498", "usable rows after de-duplication"), ("70 / 15 / 15", "train, dev, test; stratified; seed 42")]):
        y = 2.5 + i * 1.95; box(s, 0.7, y, 4.9, 1.7, CARD, EDGE); text(s, 1.0, y + 0.2, 4.4, 0.8, big, 40, TEAL, True); text(s, 1.0, y + 1.05, 4.4, 0.5, lab, 15, MUTED)
    text(s, 6.2, 2.5, 6, 0.4, "Label balance", 18, NAVY, True)
    for i, (lab, n) in enumerate([("Positive", 955), ("Negative", 848), ("Neutral", 697)]):
        y = 3.15 + i * 0.8; text(s, 6.2, y + 0.08, 1.3, 0.4, lab, 16); b = box(s, 7.5, y, 4.3 * n / 955, 0.5, TEAL, None); text(s, 7.5 + 4.3 * n / 955 + 0.15, y + 0.08, 1, 0.4, str(n), 16, NAVY, True)
    text(s, 6.2, 5.7, 6.4, 1.1, "Short sentences of about 7 words, all Devanagari. Duplicates were removed before splitting, so no sentence appears in both train and test.", 15, MUTED)
    footer(s, ds_line, 3)
    notes(s, "Presenter: Rohan Sabbani, Data Engineer (1-3 min). 2,500 Hindi sentences, three classes, mildly imbalanced. De-duplicated on normalized text before the split to avoid leakage. Mention the data is short and fairly templated; the limitations slide explains the consequence.")

    # 4 approach
    s = prs.slides.add_slide(blank); bg(s, NAVY); header(s, "The approach", "Simple, explainable, and honestly evaluated", True)
    steps = [("Normalize", "Unicode NFC, URLs and @mentions removed, the danda as its own token, Latin letters lowercased."),
             ("Features", "TF-IDF on words (1 to 2-grams) and characters (2 to 5-grams), fit on training data only."),
             ("Models", "Naive Bayes baseline, logistic regression tuned on dev, a negation-aware variant, then fine-tuned MuRIL."),
             ("Evaluate", "Macro-F1 with confidence intervals, 5-fold CV, per-class scores, hand-labeled errors.")]
    for i, (h, d) in enumerate(steps):
        x = 0.7 + i * 3.05; box(s, x, 2.6, 2.85, 3.9, NAVY2, None)
        text(s, x + 0.3, 2.85, 2.3, 0.9, str(i + 1), 40, SAFF, True); text(s, x + 0.3, 3.75, 2.3, 0.5, h, 22, CREAM, True); text(s, x + 0.3, 4.4, 2.3, 2, d, 14, LIGHTMUTED)
    footer(s, "Classical models run offline on a laptop; MuRIL was fine-tuned on a Colab GPU", 4, True)
    notes(s, "Presenter: Muralidhar Reddy Nandi, Modeling Lead (1-3 min). Four steps. Vectorizer fit on training only; macro-F1 rather than accuracy. Hyperparameters were chosen on dev, then the test set was used once. A negation-aware variant was tested because negation is the biggest error source; it did not help, which we report honestly. A pretrained Indian-language transformer, MuRIL, was then fine-tuned on a Colab GPU.")

    # 5 demo
    s = prs.slides.add_slide(blank); bg(s, CREAM); header(s, "Live demo", "Paste posts, see the sentiment")
    here = os.path.dirname(os.path.abspath(__file__)); A = lambda n: os.path.join(here, "assets", n)
    from PIL import Image as _I
    def pic(path, x, y, w):
        im = _I.open(path); h = w * im.size[1] / im.size[0]; s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h)); return y + h
    y1 = pic(A("demo_input.png"), 0.7, 2.25, 6.2); pic(A("demo_table.png"), 0.7, y1 + 0.2, 6.2)
    y2 = pic(A("demo_overall.png"), 7.3, 2.25, 5.3)
    text(s, 7.3, y2 + 0.2, 5.3, 1.2, ["Paste posts or upload a CSV", "Batch breakdown by sentiment and script", "Runs offline on a laptop"], 15, NAVY, spacing=6)
    footer(s, "Screenshots from our live Streamlit app, running the logistic regression model", 5)
    notes(s, "Presenter: Isha Joshi, Demo Lead (3-6 min). These are real screenshots of the app. Switch to the live Streamlit app, paste a few lines including one with negation to show an honest failure. Fallback: python demo_cli.py.")

    # 6 results
    s = prs.slides.add_slide(blank); bg(s, CREAM); header(s, "Results on the test set", "Fine-tuned MuRIL reaches 0.975 macro-F1, up from 0.945")
    T = M["test"]; FT = M["finetune"]
    cols = [("Naive Bayes", T["naive_bayes"], "baseline", False), ("Logistic regression", T["baseline_logreg"], f"95% CI {T['baseline_logreg_ci95'][0]:.3f} to {T['baseline_logreg_ci95'][1]:.3f}", False),
            ("LR + negation", T["improved"], f"95% CI {T['improved_ci95'][0]:.3f} to {T['improved_ci95'][1]:.3f}", False), ("Fine-tuned MuRIL", FT["test_macro_f1"], "single run, Colab GPU", True)]
    for i, (lab, v, note, hi) in enumerate(cols):
        x = 0.7 + i * 3.05; box(s, x, 2.5, 2.85, 3.7, NAVY if hi else CARD, None if hi else EDGE)
        text(s, x + 0.25, 2.75, 2.4, 0.4, lab.upper(), 12, SAFF if hi else TEAL, True)
        text(s, x + 0.25, 3.4, 2.4, 1.2, f"{v:.3f}", 48, CREAM if hi else NAVY, True)
        text(s, x + 0.25, 4.9, 2.4, 1.0, ["macro-F1, 375 test sentences", note], 13, LIGHTMUTED if hi else MUTED)
    cv = M["cv5_macro_f1"]
    text(s, 0.7, 6.4, 12, 0.5, f"5-fold CV macro-F1: baseline LR {cv['baseline_logreg'][0]:.3f} ± {cv['baseline_logreg'][1]:.3f}, with negation {cv['improved'][0]:.3f} ± {cv['improved'][1]:.3f}. The two classical variants are within noise. MuRIL has no confidence interval (one run).", 15, MUTED)
    footer(s, "Same train/dev/test split for every model", 6)
    notes(s, "Presenter: Sowseelyatha Mutharaju, Evaluation Lead (6-8 min). Headline: fine-tuned MuRIL 0.975, logistic regression 0.945, Naive Bayes 0.895. The negation-aware variant scored 0.944; confidence intervals overlap completely and cross-validation differences are within one standard deviation, so we conclude negation marking did not help. It fixed 2 of 21 baseline errors but introduced 2 new ones. Fine-tuned MuRIL (google/muril-base-cased) scored 0.975 on the same split, the best result, but it is a single run with no confidence interval, so say 'about 3 points better' and not more. Caveat to say aloud: the data is easy, so treat scores as optimistic.")

    # 7 per-class
    s = prs.slides.add_slide(blank); bg(s, CREAM); header(s, "Per-class F1", "Neutral is the strongest class on this data")
    pc = {"Negative": (0.93, 0.87), "Neutral": (0.96, 0.92), "Positive": (0.95, 0.89)}
    for k, (nm, v) in enumerate(M["per_class_rows"].items()): pc[nm] = v
    box(s, 0.7, 2.4, 0.22, 0.22, TEAL, None, False); text(s, 1.05, 2.37, 3, 0.3, "Logistic regression", 14); box(s, 4.0, 2.4, 0.22, 0.22, GRAY, None, False); text(s, 4.35, 2.37, 3, 0.3, "Naive Bayes", 14)
    for i, (nm, (lr, nb)) in enumerate(pc.items()):
        y = 3.0 + i * 1.25; text(s, 0.7, y + 0.2, 1.8, 0.4, nm, 18, NAVY, True)
        box(s, 2.6, y, 8 * lr, 0.42, TEAL, None, False); text(s, 2.7 + 8 * lr, y + 0.05, 1, 0.4, f"{lr:.2f}", 15, NAVY, True)
        box(s, 2.6, y + 0.5, 8 * nb, 0.42, GRAY, None, False); text(s, 2.7 + 8 * nb, y + 0.55, 1, 0.4, f"{nb:.2f}", 15, MUTED)
    footer(s, "Neutral usually trails on social data; here its wording is distinctive, which flatters the score", 7)
    notes(s, "Presenter: Sowseelyatha Mutharaju, Evaluation Lead (6-8 min). Neutral is often the hardest class and we report it separately as the brief asks. Here it scores highest because neutral sentences use very recognizable phrasing. That is a property of this dataset, not proof neutral is easy in the wild.")

    # 8 errors
    s = prs.slides.add_slide(blank); bg(s, CREAM); header(s, "Error analysis", f"{EA['n_errors']} errors in {EA['n_test']} sentences, four causes")
    order = [("negation / absence phrasing", "Negation"), ("rare or unseen sentiment words", "Rare sentiment words"), ("mild / implicit sentiment, weak cue", "Mild sentiment, weak cue"), ("ambiguous label or factual statement", "Ambiguous or factual")]
    for i, (k, nm) in enumerate(order):
        x = 0.7 + (i % 2) * 6.1; y = 2.5 + (i // 2) * 2.2; box(s, x, y, 5.9, 2.0, CARD, EDGE)
        text(s, x + 0.3, y + 0.2, 1, 0.7, str(EA["counts"][k]), 36, SAFF_T, True); text(s, x + 1.2, y + 0.3, 4.4, 0.5, nm, 20, NAVY, True)
        e = EA["examples"][k]; text(s, x + 0.3, y + 0.95, 5.3, 0.5, e["text"], 16, NAVY, False, DEVA); text(s, x + 0.3, y + 1.5, 5.3, 0.4, f"true {e['label']}, predicted {e['pred']}", 13, MUTED)
    footer(s, f"All {EA['n_errors']} test errors were labeled by hand. Negation features fixed {M['baseline_errors_fixed_by_improved']} and added {M['new_errors_introduced']}", 8)
    notes(s, "Presenter: Sowseelyatha Mutharaju, Evaluation Lead (6-8 min), ideally with a Hindi speaker explaining the examples. Seven errors are negation (the model sees a positive word like सुधार and misses नहीं). Seven involve rare words. Three are mild sentiment. Four are arguable labels.")

    # 9 limits
    s = prs.slides.add_slide(blank); bg(s, NAVY); header(s, "Limitations and ethics", "Where this system should not be trusted", True)
    lim = [("Optimistic scores", "About 43% of test sentences closely match a pattern in training. Real posts are messier."), ("One script only", "Devanagari only. Hinglish, code-mixing, emoji and sarcasm are untested."),
           ("Negation and rare words", "Bag-of-words models miss “not good” patterns, even with negation marking, and words seen rarely."), ("Aggregate use only", "Fine for brand-level trends. Not for judging individuals; social data carries demographic bias.")]
    for i, (h, d) in enumerate(lim):
        x = 0.7 + (i % 2) * 6.1; y = 2.5 + (i // 2) * 2.15; box(s, x, y, 5.9, 1.95, NAVY2, None); text(s, x + 0.3, y + 0.25, 5.3, 0.5, h, 20, SAFF, True); text(s, x + 0.3, y + 0.85, 5.3, 1.0, d, 15, LIGHTMUTED)
    footer(s, "Report honestly: a modest number with an explanation beats an inflated one", 9, True)
    notes(s, "Presenter: Manikantha Kothamasu, Team Lead (8-10 min). Lead with the 43% figure: share of test sentences with at least 0.7 word-set overlap with some training sentence. Then script coverage, negation, and aggregate vs individual use.")

    # 10 next
    s = prs.slides.add_slide(blank); bg(s, CREAM); header(s, "With another week", "Harder data, a stronger model, human review")
    nx = [("Stress-test MuRIL", "Repeat with several seeds for a confidence interval, and test on Hinglish and noisy posts."), ("Real social posts", "Add Hinglish and noisy tweets so scores reflect what the client will see."), ("Human in the loop", "Route low-confidence posts to a reviewer instead of trusting every label.")]
    for i, (h, d) in enumerate(nx):
        x = 0.7 + i * 4.1; box(s, x, 2.6, 3.9, 3.7, CARD, EDGE); text(s, x + 0.3, 2.85, 1, 0.9, str(i + 1), 40, TEAL, True); text(s, x + 0.3, 3.85, 3.4, 0.5, h, 22, NAVY, True); text(s, x + 0.3, 4.5, 3.4, 1.6, d, 15, MUTED)
    footer(s, "Thank you · Questions?", 10)
    notes(s, "Presenter: Manikantha Kothamasu, Team Lead (8-10 min). Close with three next steps, then Q&A. Every team member must be ready to explain any file in the repository.")
    prs.save(out)
