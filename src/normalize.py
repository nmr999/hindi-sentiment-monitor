"""Hindi / Hinglish text normalization (Ch. 2 style)."""
import re, unicodedata

URL = re.compile(r"https?://\S+|www\.\S+")
MENTION = re.compile(r"@\w+")
HASH = re.compile(r"#(\w+)")
REPEAT = re.compile(r"(.)\1{2,}")          # sooooo -> soo
SPACES = re.compile(r"\s+")
DEVA = re.compile(r"[ऀ-ॿ]")
LATIN = re.compile(r"[A-Za-z]")
DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

def script_of(text: str) -> str:
    """Rough script/language tag: 'devanagari', 'romanized' (Hinglish/English) or 'mixed'."""
    d, l = len(DEVA.findall(text)), len(LATIN.findall(text))
    if d and l: return "mixed"
    if d: return "devanagari"
    if l: return "romanized"
    return "other"

def normalize(text: str) -> str:
    t = unicodedata.normalize("NFC", str(text))
    t = URL.sub(" ", t)
    t = MENTION.sub(" ", t)
    t = HASH.sub(r"\1", t)                 # keep hashtag text
    t = t.replace("।", " । ").translate(DIGITS)   # danda as its own token
    # lowercase only Latin letters; Devanagari has no case
    t = "".join(c.lower() if c.isascii() else c for c in t)
    t = REPEAT.sub(r"\1\1", t)
    return SPACES.sub(" ", t).strip()
