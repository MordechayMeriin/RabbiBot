"""Download the Igrot Kodesh (letters of the Lubavitcher Rebbe) from chabadlibrary.org.

The site is an Angular app backed by a JSON API:
    api/main?path=1200000000   -> list of tomes ("כרך א", ...)
    api/main?path=<tome id>    -> list of letters in the tome
    api/main?path=<letter id>  -> the letter's HTML text

Output layout (one JSON file per letter):
    RawData/tome_01/letter_00001.json
    RawData/tome_01/letter_00141a.json   <- heading "קמא*" (added letter after 141)

Usage:
    python3 scripts/scrape_igrot_kodesh.py [--out RawData] [--workers 6] [--tomes 1 2]
Already downloaded letters are skipped, so the script can be re-run to resume.
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from detect_language import detect_language  # noqa: E402
from hebrew_numerals import hebrew_to_int  # noqa: E402

API = "https://www.chabadlibrary.org/books/api/main"
SITE = "https://www.chabadlibrary.org/books/"
ROOT_ID = 1200000000
# The server always answers with brotli; requests decodes it when the `brotli` package is installed.
HEADERS = {"Accept": "application/json"}

_session = requests.Session()
_session.headers.update(HEADERS)


def fetch(node_id, retries=5):
    for attempt in range(retries):
        try:
            r = _session.get(API, params={"path": node_id}, timeout=60)
            r.raise_for_status()
            return r.json()["content"]
        except (requests.RequestException, ValueError, KeyError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


class LetterParser(HTMLParser):
    """Split a letter's HTML into blocks of (css class, text)."""

    BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self._cls = None
        self._buf = []

    def _flush(self):
        text = "".join(self._buf)
        text = "\n".join(" ".join(line.split()) for line in text.split("\n")).strip()
        if text:
            self.blocks.append((self._cls or "", text))
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK_TAGS:
            self._flush()
            self._cls = dict(attrs).get("class", "")
        elif tag == "br":
            self._buf.append("\n")

    def handle_endtag(self, tag):
        if tag in self.BLOCK_TAGS:
            self._flush()
            self._cls = None

    def handle_data(self, data):
        self._buf.append(data)

    def close(self):
        super().close()
        self._flush()


def parse_letter_html(html):
    """Return (content, notes, pages) as plain text from the letter's HTML."""
    parser = LetterParser()
    parser.feed(html or "")
    parser.close()
    content, notes, pages = [], [], []
    for cls, text in parser.blocks:
        if "pagenumber" in cls:
            pages.append(text)
        elif cls.startswith("igroys_comment"):
            notes.append(text)
        else:
            content.append(text)
    return "\n\n".join(content), "\n\n".join(notes), pages


def split_heading(heading):
    """'ד'קנא**' -> ('ד'קנא', '**'); the stars mark added letters sharing a number."""
    h = heading.strip()
    base = h.rstrip("* ").strip()
    return base, h[len(base):].replace(" ", "")


def letter_filename(number, suffix):
    # "*" -> "a", "**" -> "b", ...
    extra = chr(ord("a") + len(suffix) - 1) if suffix else ""
    return f"letter_{number:05d}{extra}.json"


def save_letter(tome, item, out_dir):
    base, suffix = split_heading(item["heading"])
    number = hebrew_to_int(base)
    path = out_dir / letter_filename(number, suffix)
    if path.exists():
        return path, False

    node = fetch(item["id"])
    if node.get("type") != "page":
        raise RuntimeError(f"letter {item['id']} has unexpected type {node.get('type')!r}")
    data = node["data"]
    content, notes, pages = parse_letter_html(data.get("text"))
    footnotes = parse_letter_html(data.get("haoros"))[0] if data.get("haoros") else ""

    record = {
        "tome_hebrew": tome["hebrew"],
        "tome_number": tome["number"],
        "letter_hebrew": item["heading"].strip(),
        "letter_number": number,
        "letter_suffix": suffix,
        "pages": pages,
        "source_id": item["id"],
        "source_url": f"{SITE}{item['id']}",
        "language": detect_language(content),
        "content": content,
        "notes": notes,
        "footnotes": footnotes,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return path, True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "RawData"))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--tomes", type=int, nargs="*", help="tome numbers to download (default: all)")
    args = ap.parse_args()
    out_root = Path(args.out)

    tomes = []
    for t in fetch(ROOT_ID)["data"]:
        hebrew = t["heading"].replace("כרך", "").strip()
        tomes.append({"id": t["id"], "hebrew": hebrew, "number": hebrew_to_int(hebrew)})
    tomes.sort(key=lambda t: t["number"])
    if args.tomes:
        tomes = [t for t in tomes if t["number"] in args.tomes]

    manifest = []
    failures = []
    for tome in tomes:
        out_dir = out_root / f"tome_{tome['number']:02d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        listing = fetch(tome["id"])
        items = listing["data"]
        names = [letter_filename(hebrew_to_int(b), sfx) for b, sfx in (split_heading(i["heading"]) for i in items)]
        if len(set(names)) != len(names):
            raise RuntimeError(f"tome {tome['number']}: two letters map to the same filename")
        new = 0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(save_letter, tome, item, out_dir): item for item in items}
            for fut in as_completed(futures):
                try:
                    new += fut.result()[1]
                except Exception as e:  # keep going; report at the end
                    failures.append((tome["number"], futures[fut], repr(e)))
        files = len(list(out_dir.glob("letter_*.json")))
        print(f"tome {tome['number']:2d} ({tome['hebrew']}): {len(items)} listed, {new} new, {files} on disk",
              flush=True)
        manifest.append({"tome_hebrew": tome["hebrew"], "tome_number": tome["number"],
                         "source_id": tome["id"], "folder": out_dir.name, "letters": len(items)})

    if not args.tomes:
        (out_root / "tomes.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    for tome_no, item, err in failures:
        print(f"FAILED tome {tome_no} letter {item['heading']} ({item['id']}): {err}", file=sys.stderr)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
