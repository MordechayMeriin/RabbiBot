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
  "content": "...",             // the letter itself, plain text, paragraphs separated by blank lines
  "notes": "...",               // editor's notes printed after the letter (igroys_comment)
  "footnotes": "..."            // footnotes ("הערות"), when the site has them
}
```

To refresh or resume the download (existing files are skipped):

```bash
pip install -r requirements.txt
python3 scripts/scrape_igrot_kodesh.py
```
