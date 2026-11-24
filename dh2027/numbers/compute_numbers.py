"""Recompute the numbers of Section 4 of the DH 2027 short paper from the satellite repositories.

Usage (Windows cmd, one line): python compute_numbers.py C:\\git
The directory must hold the clones of n4o-rse/osm-*-static and wd-*-static (benchmarks, sisal, ogham, holywells; govanstones, ogham, irishroundtowers, holywells).
CQ1 versions and users per OSM site; CQ2 links between OSM elements and Wikidata items in both directions; CQ3 distance of the pairs with
coordinates on both sides; effort: lines of site.yaml without comments and blank lines.
CQ4 (needs rdflib, a few minutes): python compute_numbers.py C:\\git --registry C:\\git\\beaverbridge-registry
"""
import csv, math, os, re, sys
from collections import Counter

OSM = ["osm-benchmarks-static", "osm-sisal-static", "osm-ogham-static", "osm-holywells-static"]
WD = ["wd-govanstones-static", "wd-ogham-static", "wd-irishroundtowers-static", "wd-holywells-static"]


def rd(root, repo, name):
    with open(os.path.join(root, repo, "data", "csv", name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


def ll(v):
    p = v.split(",")
    return float(p[0]), float(p[1])


def main():
    root = sys.argv[1]
    out = []
    osm_el = {}
    users_all = Counter(); n_ver = 0
    for r in OSM:
        st = rd(root, r, "statements.csv"); q = rd(root, r, "qualifiers.csv")
        ver = [s for s in st if s["property"] == "P101"]
        sids = {s["sid"] for s in ver}
        users = Counter(x["value"] for x in q if x["property"] == "P105" and x["sid"] in sids)
        els = [s for s in st if s["property"] == "P100"]
        n = sum(users.values()); n_ver += n; users_all.update(users)
        top = users.most_common(1)[0]
        out.append(f"{r}: elements {len(els)}, versions {len(ver)}, users {len(users)}, top user {top[0]} {100*top[1]/n:.1f} %")
        subj = {s["subject"]: s["value"] for s in els}
        wdt = {s["subject"]: s["value"] for s in st if s["property"] == "P113" and s["value"].startswith("wikidata=")}
        pos = {s["subject"]: s["value"] for s in st if s["property"] == "P110"}
        for sub, url in subj.items():
            m = re.search(r"/(node|way|relation)/(\d+)", url)
            if m:
                osm_el[(m.group(1), m.group(2))] = {"site": r, "qid": wdt.get(sub, "")[9:] or None, "pos": ll(pos[sub]) if sub in pos else None}
    out.append(f"OSM total: elements {len(osm_el)}, versions {n_ver}, distinct users {len(users_all)}")
    wd_item = {}
    for r in WD:
        ents = rd(root, r, "entities.csv"); st = rd(root, r, "statements.csv"); idm = rd(root, r, "idmap.csv")
        props = {e["id"]: e["label_en"] for e in ents if e["kind"] == "property"}
        local2qid = {x["id"]: x["key"] for x in idm if x["source"] == "wikidata"}
        osmp = {p: ("node" if "node" in l.lower() else "way" if "way" in l.lower() else "relation" if "relation" in l.lower() else "node") for p, l in props.items() if "OpenStreetMap" in l}
        cp = [p for p, l in props.items() if l == "coordinate location"]
        for s in st:
            qid = local2qid.get(s["subject"])
            if not qid: continue
            d = wd_item.setdefault(qid, {"site": r, "osm": set(), "pos": []})
            if s["property"] in osmp: d["osm"].add((osmp[s["property"]], s["value"].strip()))
            if s["property"] in cp:
                try: d["pos"].append(ll(s["value"]))
                except ValueError: pass
    out.append(f"Wikidata sites: items {len(wd_item)}")
    o2w = {k for k, v in osm_el.items() if v["qid"] and v["qid"] in wd_item}
    w2o = {q for q, v in wd_item.items() if any(k in osm_el for k in v["osm"])}
    both = {k for k in o2w if k in wd_item[osm_el[k]["qid"]]["osm"]}
    out.append(f"CQ2: OSM elements naming a held Wikidata item {len(o2w)}, Wikidata items naming a held OSM element {len(w2o)}, links both ways {len(both)}, one side only {len(o2w)-len(both)} (OSM) and {len(w2o)-len(both)} (Wikidata)")
    pairs = set()
    for k in o2w: pairs.add((k, osm_el[k]["qid"]))
    for q in w2o:
        for k in wd_item[q]["osm"]:
            if k in osm_el: pairs.add((k, q))
    dist = []
    for k, q in pairs:
        a, b = osm_el[k]["pos"], wd_item[q]["pos"]
        if a and b: dist.append(min(hav(a, p) for p in b))   # an item can hold several coordinates (find spot, present location): nearest
    out.append(f"CQ3: pairs {len(pairs)}, with coordinates on both sides {len(dist)}, within 1 m {sum(d<=1 for d in dist)}, >50 m {sum(d>50 for d in dist)}, >500 m {sum(d>500 for d in dist)}")
    for r in OSM + WD:
        with open(os.path.join(root, r, "site.yaml"), encoding="utf-8") as f:
            n = sum(1 for l in f if l.strip() and not l.strip().startswith("#"))
        out.append(f"site.yaml {r}: {n} lines without comments")
    if "--registry" in sys.argv:
        import rdflib
        reg = sys.argv[sys.argv.index("--registry") + 1]
        g = rdflib.Graph(); g.parse(os.path.join(reg, "dist", "beaverbridge-registry.ttl"))
        ns = dict(g.namespaces())
        q = """PREFIX bbr: <%s> PREFIX wikibase: <%s>
        SELECT ?type ?inst (COUNT(DISTINCT ?item) AS ?items) (COUNT(DISTINCT ?anchored) AS ?crm) WHERE {
         ?record a <http://www.w3.org/ns/dcat#CatalogRecord> ; bbr:sourceType ?type ; bbr:prefix ?inst .
         OPTIONAL { ?item bbr:fromInstance ?record ; a wikibase:Item .
           OPTIONAL { ?item bbr:instanceOf/bbr:subclassOf*/bbr:crmClass ?c . BIND(?item AS ?anchored) } } }
        GROUP BY ?type ?inst ORDER BY ?type ?inst""" % (ns["bbr"], ns["wikibase"])
        ti = tc = 0
        for r in g.query(q):
            i, c = int(r.items), int(r.crm); ti += i; tc += c
            out.append(f"CQ4 {r.type} {r.inst}: items {i}, with CRM class {c} ({100*c/i:.0f} %)")
        out.append(f"CQ4 total: {tc} of {ti} items")
    print("\n".join(out))
    with open("numbers_result.txt", "w", encoding="utf-8") as f: f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
