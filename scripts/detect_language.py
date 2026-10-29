"""Guess the language of a letter from common function words.

Returns one of:
    "he"       Hebrew
    "yi"       Yiddish
    "mixed"    substantial Hebrew and Yiddish together
    "en", "fr" English / French (Latin script is the majority)
    "unknown"  too short or no clear signal

Usage (tags every letter file in place):
    python3 scripts/detect_language.py [RawData]
"""

import json
import re
import sys
from pathlib import Path

YIDDISH = set(
    "און איז פון מיט דער דאס ניט נישט האט זיין זייער אויף אויך וואס ווי איך מען צו "
    "ער זי זיי וועט וועלכע געווען האבן איר אייער ביי פאר נאך דעם".split()
)
HEBREW = set('של את על כי זה גם אשר הוא היא עם אל אבל כמו כל מה או בזה ע"ד אודות הנה וכן להיות'.split())
LATIN = {
    "en": set("the and of to in is that your you with for this be which".split()),
    "fr": set("le la et de les des est que vous pour".split()),
}
NIQQUD = re.compile("[֑-ׇ]")
MIN_MARKERS = 3
MIN_WORDS = 10


def _yiddish_forms(words):
    """Words with typical Yiddish morphology: -ען endings or the גע- past participle prefix."""
    return sum(w.endswith("ען") or (w.startswith("גע") and len(w) > 4) for w in words)


def detect_language(text):
    text = NIQQUD.sub("", text or "")
    latin = re.findall(r"[A-Za-z]+", text)
    hebrew_chars = len(re.findall("[א-ת]", text))
    latin_chars = sum(map(len, latin))

    if latin_chars > hebrew_chars:
        words = [w.lower() for w in latin]
        counts = {lang: sum(w in vocab for w in words) for lang, vocab in LATIN.items()}
        lang, hits = max(counts.items(), key=lambda kv: kv[1])
        return lang if hits >= MIN_MARKERS else "unknown"

    words = re.findall('[א-ת"]+', text)
    yi = sum(w in YIDDISH for w in words)
    he = sum(w in HEBREW for w in words)
    if yi + he < MIN_MARKERS:
        # Short letters often lack the marker words; fall back on word forms.
        forms = _yiddish_forms(words)
        if forms >= 2:
            return "yi"
        if forms == 0 and len(words) >= MIN_WORDS:
            return "he"
        return "unknown"
    share = yi / (yi + he)
    return "yi" if share > 0.7 else "he" if share < 0.3 else "mixed"


# Manual classifications (by "tome_NN/letter_NNNNN") for letters the heuristic can't decide.
OVERRIDES_FILE = Path(__file__).resolve().parent / "language_overrides.json"


def tag_files(root):
    overrides = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8")) if OVERRIDES_FILE.exists() else {}
    counts = {}
    for path in sorted(Path(root).glob("tome_*/letter_*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        rel = f"{path.parent.name}/{path.stem}"
        lang = overrides.get(rel) or detect_language(record["content"])
        counts[lang] = counts.get(lang, 0) + 1
        if record.get("language") == lang:
            continue
        # Insert "language" right before "content" to keep metadata first.
        record.pop("language", None)
        ordered = {}
        for key, value in record.items():
            if key == "content":
                ordered["language"] = lang
            ordered[key] = value
        path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
    return counts


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "RawData"
    print(tag_files(root))
