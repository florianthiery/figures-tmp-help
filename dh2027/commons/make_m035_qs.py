#!/usr/bin/env python3
"""Write a QuickStatements (v1, tab-separated) file that creates a Wikidata item for the mason's-mark type M035
(Wallace 2020, MRes thesis, University of Glasgow, https://theses.gla.ac.uk/81713/).

The class ("mason's mark") and the place (Glasgow Cathedral) are looked up on Wikidata and printed for checking;
override them with --cls / --place if the first hit is wrong.

  cd /d C:\\git\\wikibase-static-help\\dh2027\\commons && python make_m035_qs.py --contact thiery.florian@gmail.com
Then paste m035.qs into https://quickstatements.toolforge.org/ (New batch, "Import V1 commands").
"""
import argparse, json, urllib.parse, urllib.request

API = "https://www.wikidata.org/w/api.php"
THESIS = "https://theses.gla.ac.uk/81713/"


def search(term, ua, n=5):
    q = urllib.parse.urlencode({"action": "wbsearchentities", "search": term, "language": "en",
                                "limit": n, "format": "json"})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": ua})
    return json.load(urllib.request.urlopen(req, timeout=30)).get("search", [])


def pick(term, given, ua):
    if given:
        return given
    hits = search(term, ua)
    for h in hits:
        print(f"  {term!r}: {h['id']}  {h.get('label','')} - {h.get('description','')}")
    if not hits:
        raise SystemExit(f"no Wikidata hit for {term!r}; pass the Q-id explicitly")
    return hits[0]["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contact", required=True)
    ap.add_argument("--cls", help="Q-id of 'mason's mark' (default: first search hit)")
    ap.add_argument("--place", help="Q-id of Glasgow Cathedral (default: first search hit)")
    ap.add_argument("--out", default="m035.qs")
    a = ap.parse_args()
    ua = f"wikibase-static-help/1.0 ({a.contact})"
    cls = pick("mason's mark", a.cls, ua)
    place = pick("Glasgow Cathedral", a.place, ua)
    ref = f'S854\t"{THESIS}"'
    rows = [
        ["CREATE"],
        ["LAST", "Len", '"mason\'s mark type M035 (Wallace)"'],
        ["LAST", "Lde", '"Steinmetzzeichen-Typ M035 (Wallace)"'],
        ["LAST", "Aen", '"M035"'],
        ["LAST", "Aen", '"butterfly mason\'s mark"'],
        ["LAST", "Den", '"type of mason\'s mark: an X between two vertical lines, catalogued as M035 by Wallace (2020)"'],
        ["LAST", "Dde", '"Typ eines Steinmetzzeichens: X zwischen zwei senkrechten Strichen, bei Wallace (2020) als M035 verzeichnet"'],
        ["LAST", "P31", cls, ref],
        ["LAST", "P973", f'"{THESIS}"'],
        ["LAST", "P1114", "35", "P276", place, ref],
    ]
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join("\t".join(r) for r in rows) + "\n")
    print(f"class {cls}, place {place} -> {a.out}")


if __name__ == "__main__":
    main()
