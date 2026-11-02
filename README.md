# RabbiBot

A retrieval-augmented generation (RAG) project whose knowledge base is the
**Igrot Kodesh** — the collected letters of the Lubavitcher Rebbe, Rabbi
Menachem Mendel Schneerson — as published on
[chabadlibrary.org](https://www.chabadlibrary.org/books/1200000000).

## Status

| Stage | State |
|---|---|
| Download the letters | ✅ 28 tomes, 11,062 letters in `RawData/` |
| Tag each letter's language | ✅ `language` field on every letter |
| Embeddings / vector index | ⏳ not started — models still to be evaluated |
| Retrieval + answering bot | ⏳ not started |

## The data

```
RawData/
  README.md          # full description of the file format
  tomes.json         # index: tome number (Hebrew + numeric), folder, letter count
  tome_01/
    letter_00001.json
    letter_00141a.json   # heading "קמא*" – an added letter sharing number 141
    ...
  tome_28/
```

One JSON file per letter. Each file holds the tome and letter number both as
they appear on the site (Hebrew numerals) and as integers, the letter text,
the editor's notes, footnotes, page markers, the source URL and the letter's
language:

```json
{
  "tome_hebrew": "א",
  "tome_number": 1,
  "letter_hebrew": "קמא*",
  "letter_number": 141,
  "letter_suffix": "*",
  "pages": ["קמא*"],
  "source_id": 1200750143,
  "source_url": "https://www.chabadlibrary.org/books/1200750143",
  "language": "he",
  "content": "…",
  "notes": "…",
  "footnotes": ""
}
```

Letter numbers run continuously across tomes (tome 2 starts at 169), so they
are unique across the whole collection.

**Languages:** 9,718 Hebrew (`he`), 1,332 Yiddish (`yi`), 6 mixed, 4 French,
2 English. A Hebrew letter that quotes a Yiddish saying or has a few Yiddish
sentences counts as Hebrew, and vice versa. See [`RawData/README.md`](RawData/README.md)
for details.

## Scripts

| Script | What it does |
|---|---|
| `scripts/scrape_igrot_kodesh.py` | Downloads every tome and letter from the site's JSON API into `RawData/`. Re-runnable: existing files are skipped. |
| `scripts/detect_language.py` | Tags every letter with `language`, using a word-frequency heuristic plus the manual decisions in `scripts/language_overrides.json`. |
| `scripts/hebrew_numerals.py` | Converts Hebrew numerals (`קסט`, `א'רכד`) to integers. Run it directly for a self-test. |

## Setup

```bash
pip install -r requirements.txt
```

Refresh or resume the download:

```bash
python3 scripts/scrape_igrot_kodesh.py
```

Download only some tomes:

```bash
python3 scripts/scrape_igrot_kodesh.py --tomes 1 2 3
```

Re-tag languages (after changing the detector or the overrides):

```bash
python3 scripts/detect_language.py
```

## Copyright

The Igrot Kodesh is a copyrighted publication of Kehot Publication Society;
chabadlibrary.org makes it freely readable online. Keep this repository
private, and get permission before publishing the texts or anything derived
from them (such as translations).
