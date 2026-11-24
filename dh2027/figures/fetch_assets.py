"""Fetch the photographs and the map crop for the figures (run on your own computer).

Needs Pillow (pip install pillow). Commons and the OSM tile server are not reachable from the cloud sandbox.
  python fetch_assets.py --contact you@example.org
Default: the benchmark photograph on Albert Bridge (Commons) and an OSM map crop around the node.
Extra Commons files:  --commons "File:Some mark.jpg=masons_mark.jpg"   (repeatable, name after '=' is the target file)
Writes photos/*.jpg|png and photos/credits.md (author and licence from the file page, OSM attribution).
"""
import argparse, io, json, math, os, re, urllib.parse, urllib.request
from PIL import Image, ImageDraw

API = "https://commons.wikimedia.org/w/api.php"


def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def commons(title, target, out, ua, width=1000):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
                                "iiprop": "url|extmetadata", "iiurlwidth": width, "maxlag": 5})
    d = json.loads(get(f"{API}?{q}", ua))
    page = next(iter(d["query"]["pages"].values()))
    ii = (page.get("imageinfo") or [None])[0]
    if not ii:
        raise SystemExit(f"not found on Commons: {title}")
    img = Image.open(io.BytesIO(get(ii.get("thumburl") or ii["url"], ua))).convert("RGB")
    img.save(os.path.join(out, target), quality=88)
    m = ii.get("extmetadata", {})
    strip = lambda k: re.sub(r"<[^>]+>", "", (m.get(k) or {}).get("value", "")).strip()
    return f"- `{target}`: {title}; author: {strip('Artist')}; licence: {strip('LicenseShortName')}; {ii['descriptionurl']}"


def osm_crop(lat, lon, z, target, out, ua, n=3, size=256):
    x = (lon + 180) / 360 * 2 ** z
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2 ** z
    x0, y0 = int(x) - n // 2, int(y) - n // 2
    canvas = Image.new("RGB", (n * size, n * size))
    for i in range(n):
        for j in range(n):
            tile = get(f"https://tile.openstreetmap.org/{z}/{x0 + i}/{y0 + j}.png", ua)
            canvas.paste(Image.open(io.BytesIO(tile)).convert("RGB"), (i * size, j * size))
    px, py = (x - x0) * size, (y - y0) * size
    ImageDraw.Draw(canvas).ellipse((px - 14, py - 14, px + 14, py + 14), outline="#dc2626", width=5)
    canvas.save(os.path.join(out, target))
    return f"- `{target}`: map data © OpenStreetMap contributors (ODbL), tiles by the OpenStreetMap Foundation; node at {lat}, {lon}, zoom {z}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--contact", required=True)
    ap.add_argument("--out", default="photos")
    ap.add_argument("--commons", action="append", default=[], help='"File:Name.jpg=target.jpg"')
    ap.add_argument("--commons-file", help="text file, one 'File:Name.jpg=target.jpg' per line (avoids cmd quoting problems)")
    ap.add_argument("--osm", default="55.852799,-4.247294,18", help="lat,lon,zoom of the OSM crop")
    ap.add_argument("--no-defaults", action="store_true")
    ap.add_argument("--node-id-only", action="store_true", help="only look up the OSM survey-point node next to --osm and write photos/osm_node_id.txt")
    a = ap.parse_args()
    ua = f"wikibase-static-help-figures/1.0 ({a.contact})"
    os.makedirs(a.out, exist_ok=True)
    if a.node_id_only:
        lat, lon, _ = a.osm.split(",")
        q = f'[out:json];node(around:40,{lat},{lon})["survey_point"];out;'
        req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": ua})
        els = json.load(urllib.request.urlopen(req, timeout=90)).get("elements", [])
        for e in els: print(e["id"], e.get("lat"), e.get("lon"), e.get("tags"))
        if not els: raise SystemExit("no survey_point node within 40 m")
        els.sort(key=lambda e: (e["lat"] - float(lat)) ** 2 + (e["lon"] - float(lon)) ** 2)
        open(os.path.join(a.out, "osm_node_id.txt"), "w").write(str(els[0]["id"]))
        print("nearest:", els[0]["id"], "->", os.path.join(a.out, "osm_node_id.txt")); return
    jobs = [] if a.no_defaults else ["File:Benchmark on Albert Bridge.jpg=albert_bridge_benchmark.jpg"]
    lines = []
    extra = [l.strip() for l in open(a.commons_file, encoding="utf-8")] if a.commons_file else []
    for j in jobs + a.commons + [e for e in extra if e and not e.startswith("#")]:
        t, target = j.split("=", 1)
        lines.append(commons(t, target, a.out, ua)); print("ok", target)
    if not a.no_defaults:
        lat, lon, z = a.osm.split(",")
        lines.append(osm_crop(float(lat), float(lon), int(z), "albert_bridge_osm.png", a.out, ua)); print("ok albert_bridge_osm.png")
    with open(os.path.join(a.out, "credits.md"), "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("done, see", a.out)


if __name__ == "__main__":
    main()
