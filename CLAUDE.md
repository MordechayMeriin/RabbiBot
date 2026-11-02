# CLAUDE.md

RAG project over the Igrot Kodesh (letters of the Lubavitcher Rebbe). So far
the repo holds the downloaded corpus and the scripts that produced it; the
embedding/retrieval layer hasn't been built yet. See `README.md` for the
overview and `RawData/README.md` for the data format.

## Layout

- `RawData/tome_NN/letter_NNNNN[a|b].json` — one file per letter (11,062 files, 28 tomes).
- `RawData/tomes.json` — tome index, written by the scraper on a full run.
- `scripts/scrape_igrot_kodesh.py` — downloader (chabadlibrary.org JSON API).
- `scripts/detect_language.py` — sets the `language` field on every letter.
- `scripts/language_overrides.json` — hand-made language decisions, keyed `tome_NN/letter_NNNNN`.
- `scripts/hebrew_numerals.py` — Hebrew numeral → int, with a self-test in `__main__`.

## Commands

```bash
pip install -r requirements.txt               # requests + brotli
python3 scripts/hebrew_numerals.py            # self-test, prints "ok"
python3 scripts/scrape_igrot_kodesh.py --tomes 1 --out /tmp/test   # quick scraper check
python3 scripts/detect_language.py            # re-tag all letters; prints counts
```

There is no test suite or linter configured.

## Data conventions

- JSON files are written with `ensure_ascii=False, indent=2` (Hebrew stays readable).
- Field order: tome/letter metadata, `pages`, `source_id`, `source_url`, `language`, `content`, `notes`, `footnotes`. Keep `language` right before `content`.
- Never edit `content`, `notes` or `footnotes` by hand — they are the source text as scraped. Regenerate via the scraper instead.
- File names are numeric only (Hebrew numerals like `ו'תתקסב` contain apostrophes). The Hebrew forms live inside the JSON.
- Letter numbers run continuously across tomes. A heading with `*`/`**` is an added letter sharing the previous number → file suffix `a`/`b`, `letter_suffix` holds the stars.
- `content` is the letter; `notes` are the editor's notes printed after it (`igroys_comment` blocks); `footnotes` come from the site's `haoros` field. One letter (tome 18, 6962) has empty `content` on the site itself.

## Language tagging

- Values: `he`, `yi`, `mixed`, `en`, `fr` (`unknown` is possible for new data the heuristic can't decide).
- Rule agreed with the user: a Hebrew letter with a few Yiddish sentences or a Yiddish quotation is `he`, and vice versa. `mixed` only when both languages carry a substantial part of the letter (currently 6 letters).
- To change a letter's language, add it to `scripts/language_overrides.json` and run `detect_language.py` — don't edit the JSON file directly, or the next re-tag will undo it.
- The heuristic strips niqqud before counting words; short letters without marker words fall back on Yiddish word forms (`-ען`, `גע-`).

## Scraper gotchas

- The site is an Angular SPA; the real data comes from `https://www.chabadlibrary.org/books/api/main?path=<id>`.
- The server always answers with brotli regardless of `Accept-Encoding`, so the `brotli` package must be installed or `requests` returns undecodable bytes.
- Root id `1200000000` lists the tomes; tome ids are not sequential in tome order (tomes 25–28 have lower ids).
- New letters get `language` from the heuristic only; run `detect_language.py` afterwards to apply overrides.

## Decisions already made

- No stored translations of the Yiddish letters and no generated summaries — the user declined both. Yiddish is handled at retrieval/answer time.
- Embedding model not chosen yet. Plan: compare Gemini Embedding 001, Qwen3-Embedding-8B and BGE-M3 on a small Hebrew question set, with hybrid (lexical + dense) search and a reranker.

## Copyright

The letters are a copyrighted Kehot publication. Don't paste full letters into
chat output, commit messages or PR descriptions — refer to them by path and
tome/letter number. The repo should stay private.
