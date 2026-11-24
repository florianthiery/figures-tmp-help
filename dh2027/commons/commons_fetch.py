"""commons_fetch.py: collect file records and structured data (SDC) of Wikimedia Commons categories.

For the DH 2027 short paper (Wikimedia Commons leaf, masons' marks). Standard library only.
Run (Windows cmd, one line):
    python commons_fetch.py --contact you@example.org --out out

Writes into --out:
    files.csv    one row per file: M-ID, title, URL, uploader, author, licence, date taken, categories, depicts, ...
    summary.md   counts per category, author, uploader, licence, and the depicted Wikidata items
    raw.json     the raw answers, so that nothing has to be fetched twice

Polite by design: a User-Agent with your contact, batches of 50, a pause between requests, maxlag=5.
"""
import argparse, csv, json, os, re, sys, time, html, collections
import urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
CATEGORIES = [
    "Stonecutter marks",
    "Stonecutter marks at Glasgow Cathedral",
    "Masons' marks at Kilcooly Abbey",
    "Stonecutter marks icons",
]
SDC = {"P180": "depicts", "P170": "creator", "P275": "licence", "P571": "inception",
       "P276": "location", "P1259": "viewpoint", "P7482": "source of file"}
META = "Artist|LicenseShortName|LicenseUrl|DateTimeOriginal|ImageDescription|Credit|Attribution|GPSLatitude|GPSLongitude"


class Client:
    def __init__(self, contact, pause=0.5):
        self.ua = f"dh2027-commons-fetch/0.1 (research; {contact})"
        self.pause = pause
        self.n = 0

    def get(self, **params):
        params.update(format="json", formatversion="2", maxlag="5")
        url = API + "?" + urllib.parse.urlencode(params)
        for attempt in range(5):
            time.sleep(self.pause)
            req = urllib.request.Request(url, headers={"User-Agent": self.ua})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.load(r)
            except Exception as e:
                print(f"  retry {attempt + 1}: {e}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
                continue
            if "error" in data and data["error"].get("code") == "maxlag":
                time.sleep(5)
                continue
            self.n += 1
            return data
        raise RuntimeError("API did not answer: " + url[:120])


def members(cl, category, kind):
    """all members of one category (kind = 'file' or 'subcat'), following continuation"""
    out, cont = [], {}
    while True:
        d = cl.get(action="query", list="categorymembers", cmtitle="Category:" + category,
                   cmtype=kind, cmlimit="500", **cont)
        out += d["query"]["categorymembers"]
        if "continue" in d:
            cont = {"cmcontinue": d["continue"]["cmcontinue"]}
        else:
            return out


def walk(cl, root, depth):
    """file members of the root category and of its subcategories down to `depth`; file pageid -> set of categories"""
    files = collections.defaultdict(set)
    titles = {}
    seen, queue = set(), [(root, 0)]
    while queue:
        cat, lvl = queue.pop(0)
        if cat in seen:
            continue
        seen.add(cat)
        for m in members(cl, cat, "file"):
            files[m["pageid"]].add(cat)
            titles[m["pageid"]] = m["title"]
        if lvl < depth:
            for s in members(cl, cat, "subcat"):
                queue.append((s["title"].split(":", 1)[1], lvl + 1))
        print(f"  {cat}: {len(files)} files so far", file=sys.stderr)
    return files, titles


def chunks(seq, n=50):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def strip(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def imageinfo(cl, pageids):
    out = {}
    for ch in chunks(pageids):
        d = cl.get(action="query", pageids="|".join(map(str, ch)), prop="imageinfo|categories", cllimit="max",
                   iiprop="url|user|timestamp|size|mime|extmetadata", iiextmetadatafilter=META)
        for p in d["query"]["pages"]:
            ii = (p.get("imageinfo") or [{}])[0]
            out[p["pageid"]] = dict(title=p["title"], info=ii,
                                    cats=[c["title"].split(":", 1)[1] for c in p.get("categories", [])])
    return out


def sdc(cl, pageids):
    """structured data: {pageid: {property: [value, ...]}}; values are Q-ids or strings"""
    out = {}
    for ch in chunks(pageids):
        d = cl.get(action="wbgetentities", ids="|".join(f"M{p}" for p in ch), props="claims")
        for k, e in (d.get("entities") or {}).items():
            vals = collections.defaultdict(list)
            for prop, claims in (e.get("claims") or {}).items():
                for c in claims:
                    dv = (c.get("mainsnak") or {}).get("datavalue") or {}
                    v = dv.get("value")
                    if isinstance(v, dict):
                        v = v.get("id") or v.get("time") or json.dumps(v)
                    if v is not None:
                        vals[prop].append(str(v))
            out[int(k[1:])] = dict(vals)
    return out


def labels(cl, qids):
    out = {}
    for ch in chunks(sorted(qids)):
        d = cl.get(action="wbgetentities", ids="|".join(ch), props="labels", languages="en")
        for k, e in (d.get("entities") or {}).items():
            out[k] = ((e.get("labels") or {}).get("en") or {}).get("value", "")
    return out


def rows_from(files, base, sd):
    rows = []
    for pid in sorted(files):
        b = base.get(pid, {})
        ii, md = b.get("info", {}), (b.get("info", {}).get("extmetadata") or {})
        v = lambda k: strip((md.get(k) or {}).get("value", ""))
        s = sd.get(pid, {})
        rows.append({
            "m_id": f"M{pid}", "title": b.get("title", ""), "url": ii.get("descriptionurl", ""),
            "file_url": ii.get("url", ""), "width": ii.get("width", ""), "height": ii.get("height", ""),
            "uploader": ii.get("user", ""), "uploaded": ii.get("timestamp", ""),
            "author": v("Artist"), "licence": v("LicenseShortName"), "licence_url": v("LicenseUrl"),
            "date_taken": v("DateTimeOriginal"), "lat": v("GPSLatitude"), "lon": v("GPSLongitude"),
            "description": v("ImageDescription")[:300],
            "categories_queried": " | ".join(sorted(files[pid])),
            "categories_all": " | ".join(b.get("cats", [])),
            "sdc_depicts": " ".join(s.get("P180", [])), "sdc_creator": " ".join(s.get("P170", [])),
            "sdc_licence": " ".join(s.get("P275", [])), "sdc_inception": " ".join(s.get("P571", [])),
            "sdc_statements": sum(len(x) for x in s.values()),
        })
    return rows


def summary(rows, lab):
    n = len(rows)
    top = lambda key, k=15: collections.Counter(r[key] or "(none)" for r in rows).most_common(k)
    L = [f"# Commons categories: {n} files\n"]
    cats = collections.Counter(c for r in rows for c in r["categories_queried"].split(" | ") if c)
    L += ["## Files per queried category (a file can sit in several)"] + [f"- {c}: {k}" for c, k in cats.most_common()]
    for title, key in (("Authors", "author"), ("Uploaders", "uploader"), ("Licences", "licence")):
        L += ["", f"## {title}"] + [f"- {a}: {k}" for a, k in top(key)]
    withsd = sum(1 for r in rows if r["sdc_statements"])
    dep = collections.Counter(q for r in rows for q in r["sdc_depicts"].split() if q)
    L += ["", "## Structured data", f"- files with any SDC statement: {withsd} of {n}",
          f"- files with depicts (P180): {sum(1 for r in rows if r['sdc_depicts'])}",
          f"- files with GPS in the file metadata: {sum(1 for r in rows if r['lat'])}",
          "", "## Depicted items (P180)"] + [f"- {q} {lab.get(q, '')}: {k}" for q, k in dep.most_common(30)]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--contact", required=True, help="e-mail or URL for the User-Agent, as the Wikimedia policy asks")
    ap.add_argument("--out", default="out")
    ap.add_argument("--depth", type=int, default=2, help="levels of subcategories to follow (default 2)")
    ap.add_argument("--category", action="append", help="category name without 'Category:'; repeatable; default: the four masons' marks categories")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    cl = Client(a.contact)
    files, titles = collections.defaultdict(set), {}
    for cat in a.category or CATEGORIES:
        print(f"category {cat}", file=sys.stderr)
        f, t = walk(cl, cat.replace(" ", "_"), a.depth)
        for pid, cs in f.items():
            files[pid] |= cs
        titles.update(t)
    ids = sorted(files)
    print(f"{len(ids)} files; reading image info and structured data", file=sys.stderr)
    base, sd = imageinfo(cl, ids), sdc(cl, ids)
    lab = labels(cl, {q for s in sd.values() for q in s.get("P180", []) + s.get("P170", []) if re.fullmatch(r"Q\d+", q)})
    rows = rows_from(files, base, sd)
    with open(os.path.join(a.out, "files.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["m_id"])
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(a.out, "raw.json"), "w", encoding="utf-8") as fh:
        json.dump({"base": base, "sdc": sd, "labels": lab, "files": {str(k): sorted(v) for k, v in files.items()}},
                  fh, ensure_ascii=False)
    with open(os.path.join(a.out, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write(summary(rows, lab))
    print(f"done: {len(rows)} files, {cl.n} API calls, see {a.out}")


if __name__ == "__main__":
    main()
