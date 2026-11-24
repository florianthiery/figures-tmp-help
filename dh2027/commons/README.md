# commons_fetch.py: stonecutter marks on Wikimedia Commons

Fetches all files of four Commons categories with metadata and structured data (SDC) via the Commons API.
Standard library only, no `pip install`. Supports the Commons leaf of the DH 2027 short paper.

Categories (default): Stonecutter marks; Stonecutter marks at Glasgow Cathedral; Masons' marks at Kilcooly Abbey; Stonecutter marks icons.

## Run (Windows cmd, one line)

```
cd /d C:\git\wikibase-static-help\dh2027\commons && python commons_fetch.py --contact you@example.org --out out
```

`--contact` is required (goes into the User-Agent, as the Wikimedia policy asks). `--depth 3` follows deeper subcategories, `--category "Name"` (repeatable) fetches other categories.

## Output in `out\`

- `files.csv`: one row per file (M-ID, title, URL, uploader, author, licence, date, GPS, categories, `sdc_depicts`, `sdc_creator`, `sdc_licence`, `sdc_inception`)
- `summary.md`: counts per category, author, uploader, licence; how many files carry structured data and which Wikidata items they depict
- `raw.json`: raw API responses

## Notes

- Tested against mock responses only, not yet against the live API. Report any error output.
- Polite settings: 0.5 s pause, batches of 50, `maxlag=5`. A few hundred files take a few minutes.

## Results (run of 24 Nov 2026)

`results/summary.md` and `results/files.csv` hold the run: 526 files (depth 2, including country subcategories), 0 files with structured data. `raw.json` is not kept in the repository.
