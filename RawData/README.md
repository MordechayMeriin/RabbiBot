# RawData — Igrot Kodesh (letters of the Lubavitcher Rebbe)

Downloaded from https://www.chabadlibrary.org/books/1200000000 by
`scripts/scrape_igrot_kodesh.py`.

## Layout

```
RawData/
  tomes.json                 # list of tomes: Hebrew + numeric number, source id, folder, letter count
  tome_01/
    letter_00001.json        # one file per letter
    letter_00141.json
    letter_00141a.json       # heading "קמא*"  (an added letter that shares number 141)
    ...
  tome_28/
```

- Folders are `tome_NN` (numeric tome number, zero-padded).
- Files are `letter_NNNNN[a|b].json`. Letter numbers run continuously across
  tomes (tome 2 starts at 169), so they are unique across the whole set.
  A heading with `*` / `**` (letters added after the numbered one) gets the
  suffix `a` / `b`.

## File format

```json
{
  "tome_hebrew": "א",          // tome number as on the site (Hebrew letters)
  "tome_number": 1,             // same, numeric
  "letter_hebrew": "קמא*",     // letter number as on the site, including any '*'
  "letter_number": 141,         // numeric value of the Hebrew number
  "letter_suffix": "*",         // "", "*" or "**"
  "pages": ["קמא*"],            // page markers that appear in the letter
  "source_id": 1200750143,
  "source_url": "https://www.chabadlibrary.org/books/1200750143",
  "language": "he",             // "he" | "yi" | "mixed" | "en" | "fr" | "unknown" (see below)
  "content": "...",             // the letter itself, plain text, paragraphs separated by blank lines
  "notes": "...",               // editor's notes printed after the letter (igroys_comment)
  "footnotes": "..."            // footnotes ("הערות"), when the site has them
}
```

## Language

`language` is a heuristic guess made by `scripts/detect_language.py` from common
function words (and Yiddish word forms for short letters). Letters the
heuristic couldn't decide, and every letter it marked `mixed`, were reviewed by
hand; those decisions live in `scripts/language_overrides.json`. A Hebrew letter
with a few Yiddish sentences or a Yiddish quotation is `he`, and vice versa;
`mixed` is kept only where both languages carry a substantial part of the
letter. Counts: 9,718 `he`, 1,332 `yi`, 6 `mixed`, 4 `fr`, 2 `en`.
Re-tag all files with:

```bash
python3 scripts/detect_language.py
```

To refresh or resume the download (existing files are skipped):

```bash
pip install -r requirements.txt
python3 scripts/scrape_igrot_kodesh.py
```
