"""Figures for the revision of "From Relations to Graphs" (deRSE26 / ECEASST). Same style as dh2027/figures/figures.py.

Style: Fira Sans, flat colours, white background, no header or footer in the figure, edge labels as amber chips centred on
the arrow. Width 1700 px = the 420 pt text width of the ECEASST class, so 24 px type arrives at 5.9 pt (minimum: MIN_TYPE).
Everything that the graph states is read from data/ci_findspots.ttl (copy of CI/rdf/ci_findspots.ttl of
Research-Squirrel-Engineers/GeoScience-FAIRification-LOD, commit eec8fe5, CC BY 4.0); nothing of it is typed by hand.

Setup and run (Windows cmd, one line):
  cd /d C:\\git\\wikibase-static-help\\deRSE26\\figures && pip install resvg_py pillow rdflib && python figs.py [fig4] [z2] [z3]
Output: out/<name>.svg and out/<name>.png (use the PNG in LaTeX: the SVG names Fira Sans without embedding it).
"""
import csv, json, math, os, re, sys
import resvg_py
from PIL import ImageFont
from rdflib import Graph, Namespace, URIRef, RDFS

HERE = os.path.dirname(os.path.abspath(__file__))
F4, F5 = os.path.join(HERE, 'fonts/FiraSans-400.ttf'), os.path.join(HERE, 'fonts/FiraSans-500.ttf')
W = 1700
MIN_TYPE = 24
INST, CLS, TERM, AMB = '#e2e8f0', '#9a3412', '#4c1d95', '#fbbf24'
INK, MUT, RED = '#1f1f1d', '#55544f', '#dc2626'
SEA, LAND, COAST = '#dce9f1', '#f3f0e7', '#b3b0a4'

_fonts = {}
def tw(s, size, w=400):
    k = (size, w)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(F5 if w == 500 else F4, size, layout_engine=ImageFont.Layout.BASIC)
    return _fonts[k].getlength(s)
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')

class Fig:
    def __init__(s, name, h):
        s.name, s.h, s.o = name, h, []
    def text(s, x, y, t, size=MIN_TYPE, w=400, fill=INK, anchor='middle', maxw=None):
        if size < MIN_TYPE: raise ValueError(f'{s.name}: type {size} px < {MIN_TYPE}: {t}')
        if maxw and tw(t, size, w) > maxw: raise ValueError(f'{s.name}: overflow {tw(t, size, w):.0f}>{maxw}: {t}')
        s.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Fira Sans" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{esc(t)}</text>')
    def box(s, x, y, w, h, fill, lines, stroke='#000', sw=2, r=14, tc=INK, size=MIN_TYPE, dash=False):
        s.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{" stroke-dasharray=\"10 6\"" if dash else ""}/>')
        n = len(lines); gap = size * 1.28; y0 = y + h / 2 - (n - 1) * gap / 2 + size * 0.34
        for i, l in enumerate(lines): s.text(x + w / 2, y0 + i * gap, l, size, 500 if (i == 0 and n > 1 and fill != '#fff') else 400, tc, maxw=w - 24)
    def chip(s, cx, cy, t, size=MIN_TYPE):
        w = tw(t, size) + 28
        s.o.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - 22:.1f}" width="{w:.1f}" height="44" rx="22" fill="{AMB}" stroke="#000" stroke-width="1.5"/>')
        s.text(cx, cy + size * 0.34, t, size)
    def arrow(s, x1, y1, x2, y2, col='#000', w=2.5):
        s.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" marker-end="url(#a)"/>')
    def done(s):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{s.h}" viewBox="0 0 {W} {s.h}"><rect width="{W}" height="{s.h}" fill="#ffffff"/>'
                '<defs><marker id="a" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="16" refY="9" orient="auto"><path d="M0,0 L18,9 L0,18 z" fill="#000"/></marker></defs>')
        svg = head + '\n'.join(s.o) + '</svg>'
        os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
        open(os.path.join(HERE, f'out/{s.name}.svg'), 'w', encoding='utf8').write(svg)
        open(os.path.join(HERE, f'out/{s.name}.png'), 'wb').write(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[F4, F5], skip_system_fonts=True, zoom=1.0)))
        print('wrote', s.name, f'{W}x{s.h}')

# ---------------------------------------------------------------- data
GL, GEO = Namespace('http://w3id.org/geo-lod/'), Namespace('http://www.opengis.net/ont/geosparql#')
CI = 'http://w3id.org/geo-lod/ci/'
def local(o): return str(o).rstrip('/').split('/')[-1].split('#')[-1]
def load_ci():
    g = Graph(); g.parse(os.path.join(HERE, 'data/ci_findspots.ttl'), format='turtle')
    sites = []
    for s in g.subjects(GL.hasCertaintyLevel, None):
        ss = str(s)
        if not re.search(r'cisite_\d+$', ss): continue
        geom = g.value(s, GEO.hasGeometry)
        m = re.search(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)', str(g.value(geom, GEO.asWKT)))
        sites.append(dict(id=int(ss.rsplit('_', 1)[1]), iri=s, label=str(g.value(s, RDFS.label)), lon=float(m.group(1)), lat=float(m.group(2)),
                          level=local(g.value(geom, GL.hasCertaintyLevel)), wkt=str(g.value(geom, GEO.asWKT))))
    assert len(sites) == 74, len(sites)
    return g, sorted(sites, key=lambda d: d['id'])

def land():
    d = json.load(open(os.path.join(HERE, 'data/ne_50m_land.geojson'), encoding='utf8'))
    return [f['geometry']['coordinates'] for f in d['features'] if f['geometry']['type'] == 'Polygon'] + \
           [p for f in d['features'] if f['geometry']['type'] == 'MultiPolygon' for p in f['geometry']['coordinates']]

# ---------------------------------------------------------------- Fig. 4
def wb_entity(i):
    d = json.load(open(os.path.join(HERE, f'data/wb/{i}.json'), encoding='utf8'))
    return list(d['entities'].values())[0] if 'entities' in d else d
def wb_label(i): return wb_entity(i)['labels']['en']['value']
def wrap(text, width, size=MIN_TYPE):
    out, cur = [], ''
    for w_ in text.split(' '):
        t = (cur + ' ' + w_).strip()
        if tw(t, size) <= width or not cur: cur = t
        else: out.append(cur); cur = w_
    return out + [cur]
def snak_text(sn):
    v = sn['datavalue']['value']
    if isinstance(v, dict) and 'id' in v: return wb_label(v['id'])
    if isinstance(v, dict) and 'latitude' in v: return f"{v['latitude']}, {v['longitude']}"
    return str(v)

def fig4():
    g, S = load_ci()
    H = 960
    f = Fig('fig4_ci_findspots', H)
    arch_iri = URIRef('http://w3id.org/geo-lod/CIArchaeologicalSite')
    for s_ in S: s_['arch'] = (s_['iri'], URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), arch_iri) in g
    # --- the item of panel B, read from the static copy of the fuzzy-sl Wikibase (Q70 = Auel Maar AU3)
    it = wb_entity('Q70'); assert it['labels']['en']['value'] == 'Auel Maar AU3'
    coord = it['claims']['P4'][0]; cv = coord['mainsnak']['datavalue']['value']
    au3 = [s_ for s_ in S if s_['label'] == 'Auel Maar AU3'][0]
    assert abs(au3['lon'] - cv['longitude']) < 1e-6 and abs(au3['lat'] - cv['latitude']) < 1e-6, 'graph and Wikibase disagree on AU3'
    # --- panel A: map
    mx, my, mw = 20, 80, 780
    LON0, LON1, LAT0, LAT1, LATC = 4.0, 46.0, 31.0, 57.0, 44.0
    kx = mw / (LON1 - LON0); ky = kx / math.cos(math.radians(LATC)); mh = (LAT1 - LAT0) * ky
    X = lambda lon: mx + (lon - LON0) * kx
    Y = lambda lat: my + (LAT1 - lat) * ky
    f.o.append(f'<clipPath id="mc"><rect x="{mx}" y="{my}" width="{mw}" height="{mh:.1f}"/></clipPath>')
    f.o.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh:.1f}" fill="{SEA}"/><g clip-path="url(#mc)">')
    for poly in land():
        ring = poly[0]
        if max(p[0] for p in ring) < LON0 - 1 or min(p[0] for p in ring) > LON1 + 1 or max(p[1] for p in ring) < LAT0 - 1 or min(p[1] for p in ring) > LAT1 + 1: continue
        d = ' '.join(('M' if i == 0 else 'L') + f'{X(p[0]):.1f},{Y(p[1]):.1f}' for i, p in enumerate(ring)) + 'Z'
        for hole in poly[1:]:
            d += ' ' + ' '.join(('M' if i == 0 else 'L') + f'{X(p[0]):.1f},{Y(p[1]):.1f}' for i, p in enumerate(hole)) + 'Z'
        f.o.append(f'<path d="{d}" fill="{LAND}" stroke="{COAST}" stroke-width="1.2"/>')
    slon, slat = 14.14, 40.83                       # Phlegraean Fields (wd:Q755123), schematic
    for km in (500, 1000):
        rx = km / (111.2 * math.cos(math.radians(slat))) * kx; ry = km / 111.2 * ky
        f.o.append(f'<ellipse cx="{X(slon):.1f}" cy="{Y(slat):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="#6b7280" stroke-width="1.6" stroke-dasharray="8 7"/>')
    f.o.append('</g>')
    for km in (500, 1000):
        rx = km / (111.2 * math.cos(math.radians(slat))) * kx; ry = km / 111.2 * ky
        tx, ty = X(slon) + rx * math.cos(math.radians(235)), Y(slat) - ry * math.sin(math.radians(235))
        f.o.append(f'<rect x="{tx - 44:.1f}" y="{ty - 18:.1f}" width="88" height="34" rx="6" fill="{SEA}" opacity="0.92"/>')
        f.text(tx, ty + 8, f'{km} km', MIN_TYPE, 400, MUT)
    for s_ in S:                                    # other findspots first, archaeological sites on top
        if s_['arch']: continue
        f.o.append(f'<circle cx="{X(s_["lon"]):.1f}" cy="{Y(s_["lat"]):.1f}" r="9" fill="#fff" stroke="#000" stroke-width="1.8"/>')
    for s_ in S:
        if not s_['arch']: continue
        f.o.append(f'<circle cx="{X(s_["lon"]):.1f}" cy="{Y(s_["lat"]):.1f}" r="9" fill="{CLS}" stroke="#000" stroke-width="1.8"/>')
    ax_, ay_ = X(au3['lon']), Y(au3['lat'])         # the item of panel B
    f.o.append(f'<circle cx="{ax_:.1f}" cy="{ay_:.1f}" r="19" fill="none" stroke="{RED}" stroke-width="4"/>')
    sx, sy = X(slon), Y(slat)
    star = ' '.join(f'{sx + (21 if i % 2 == 0 else 9) * math.sin(i * math.pi / 5):.1f},{sy - (21 if i % 2 == 0 else 9) * math.cos(i * math.pi / 5):.1f}' for i in range(10))
    f.o.append(f'<polygon points="{star}" fill="{TERM}" stroke="#000" stroke-width="2"/>')
    by = {s_['label']: s_ for s_ in S}
    def call(site, text, dx, dy, red=False):
        cx, cy = X(site['lon']), Y(site['lat']); tx, ty = cx + dx, cy + dy
        f.o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{tx:.1f}" y2="{ty - 8:.1f}" stroke="{RED if red else "#000"}" stroke-width="2"/>')
        w = tw(text, MIN_TYPE) + 16
        f.o.append(f'<rect x="{tx - 8:.1f}" y="{ty - 26:.1f}" width="{w:.1f}" height="36" rx="6" fill="#fff" opacity="0.92"/>')
        f.text(tx, ty, text, MIN_TYPE, 400, INK, 'start')
    call(au3, 'Auel Maar AU3', 45, -60, True)
    call(by['Toplitsa Cave (Bulgaria)'], 'Toplitsa Cave', -40, -100)
    call(by['Franchthi Cave (Greece)'], 'Franchthi Cave', 70, 50)
    f.text(sx - 20, sy + 62, 'Phlegraean Fields', MIN_TYPE, 500, TERM, 'middle')
    def panel_title(x, letter, text):
        f.o.append(f'<rect x="{x}" y="16" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, 46, letter, 28, 500, '#fff'); f.text(x + 56, 46, text, 28, 500, INK, 'start')
    na = sum(1 for s_ in S if s_['arch'])
    panel_title(20, 'A', 'The 74 findspots: archaeology or not')
    panel_title(840, 'B', 'One coordinate statement: Auel Maar AU3')
    ly = my + mh + 40; x = mx
    f.o.append(f'<circle cx="{x}" cy="{ly}" r="9" fill="{CLS}" stroke="#000" stroke-width="1.8"/>'); f.text(x + 18, ly + 8, f'archaeological site ({na})', MIN_TYPE, 400, INK, 'start')
    x = mx + 18 + tw(f'archaeological site ({na})', MIN_TYPE) + 46
    f.o.append(f'<circle cx="{x}" cy="{ly}" r="9" fill="#fff" stroke="#000" stroke-width="1.8"/>'); f.text(x + 18, ly + 8, f'no archaeological site ({len(S) - na})', MIN_TYPE, 400, INK, 'start')
    ly += 46
    f.o.append(f'<circle cx="{mx}" cy="{ly}" r="14" fill="none" stroke="{RED}" stroke-width="4"/>'); f.text(mx + 26, ly + 8, 'item of panel B', MIN_TYPE, 400, INK, 'start')
    x = mx + 26 + tw('item of panel B', MIN_TYPE) + 46
    sy2 = ly; star2 = ' '.join(f'{x + (14 if i % 2 == 0 else 6) * math.sin(i * math.pi / 5):.1f},{sy2 - (14 if i % 2 == 0 else 6) * math.cos(i * math.pi / 5):.1f}' for i in range(10))
    f.o.append(f'<polygon points="{star2}" fill="{TERM}" stroke="#000" stroke-width="1.5"/>'); f.text(x + 22, ly + 8, 'source area of the eruption', MIN_TYPE, 400, INK, 'start')
    # --- panel B: the coordinate statement of Q70 with its qualifiers, as the Wikibase has it
    ql = coord['qualifiers-order'] if 'qualifiers-order' in coord else list(coord['qualifiers'].keys())
    rows = []
    for qp in ql:
        sn = coord['qualifiers'][qp][0]
        txt = snak_text(sn)
        rows.append((wb_label(qp), wrap(txt, 350 - 28) if len(txt) > 22 else [txt]))
    ref = coord['references'][0]['snaks']; rp = list(ref.keys())[0]
    rows.append((wb_label(rp), ['doi.org/' + snak_text(ref[rp][0]).split('doi.org/')[1]]))
    heights = [max(64, 24 * 1.28 * len(v) + 26) for _, v in rows]
    top, bottom = 90, H - 24
    gap = (bottom - top - sum(heights)) / (len(rows) - 1)
    ys = []; y = top
    for h_ in heights: ys.append(y); y += h_ + gap
    centres = [y_ + h_ / 2 for y_, h_ in zip(ys, heights)]
    bx0, bw, cx0, cw = 1350, 350, 840, 200
    cy_mid = (centres[0] + centres[-1]) / 2 + 20
    nm = it['labels']['en']['value']; part = nm.rsplit(' ', 1)
    f.box(cx0, 100, cw, 96, INST, [part[0], f'{part[1]} ({it["id"]})'], size=MIN_TYPE)
    f.box(cx0, cy_mid - 70, cw, 140, INST, [wb_label('P4'), f'{cv["latitude"]}', f'{cv["longitude"]}'], size=MIN_TYPE)
    f.arrow(cx0 + cw / 2, 196, cx0 + cw / 2, cy_mid - 70)
    f.chip(cx0 + cw / 2, (196 + cy_mid - 70) / 2, 'has coordinate')
    bus = cx0 + cw + 24
    f.o.append(f'<line x1="{cx0 + cw}" y1="{cy_mid:.1f}" x2="{bus}" y2="{cy_mid:.1f}" stroke="#000" stroke-width="2.5"/>')
    f.o.append(f'<line x1="{bus}" y1="{centres[0]:.1f}" x2="{bus}" y2="{centres[-1]:.1f}" stroke="#000" stroke-width="2.5"/>')
    for (lab, vals), y_, h_, ty in zip(rows, ys, heights, centres):
        f.box(bx0, y_, bw, h_, '#fff', vals, size=MIN_TYPE)
        f.arrow(bus, ty, bx0, ty)
        f.chip((bus + bx0) / 2, ty, lab)
    f.done()
    return S

# ---------------------------------------------------------------- Z3: where the showcases are
PIPE, WBK = CLS, AMB
def pts(setname):
    return [(float(r['lon']), float(r['lat']), r['label']) for r in csv.DictReader(open(os.path.join(HERE, 'data/showcase_points.csv'), encoding='utf8')) if r['set'] == setname]

def basemap(f, mx, my, mw, lon0, lon1, lat0, lat1, latc, clip_id, stroke=1.2):
    kx = mw / (lon1 - lon0); ky = kx / math.cos(math.radians(latc)); mh = (lat1 - lat0) * ky
    X = lambda lon: mx + (lon - lon0) * kx
    Y = lambda lat: my + (lat1 - lat) * ky
    f.o.append(f'<clipPath id="{clip_id}"><rect x="{mx}" y="{my}" width="{mw}" height="{mh:.1f}"/></clipPath>')
    f.o.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh:.1f}" fill="{SEA}"/><g clip-path="url(#{clip_id})">')
    for poly in land():
        ring = poly[0]
        if max(p[0] for p in ring) < lon0 - 1 or min(p[0] for p in ring) > lon1 + 1 or max(p[1] for p in ring) < lat0 - 1 or min(p[1] for p in ring) > lat1 + 1: continue
        step = 1 if kx > 5 else 4
        d = ' '.join(('M' if i == 0 else 'L') + f'{X(p[0]):.1f},{Y(p[1]):.1f}' for i, p in enumerate(ring[::step])) + 'Z'
        f.o.append(f'<path d="{d}" fill="{LAND}" stroke="{COAST}" stroke-width="{stroke}"/>')
    f.o.append('</g>')
    return X, Y, mh

def z3():
    f = Fig('z3_showcase_map', 900)
    f.o.append(f'<rect x="0" y="0" width="{W}" height="900" fill="#fff"/>')
    bb, sl, wbk = pts('bb5kbc'), pts('sisal'), pts('fuzzysl')
    _, S = load_ci(); ci = [(s_['lon'], s_['lat'], s_['label']) for s_ in S]
    def panel_title(x, letter, text):
        f.o.append(f'<rect x="{x}" y="16" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, 46, letter, 28, 500, '#fff'); f.text(x + 56, 46, text, 28, 500, INK, 'start')
    panel_title(20, 'A', 'Europe and the Mediterranean')
    X, Y, mh = basemap(f, 20, 80, 1000, -13, 46, 30, 57, 44, 'za')
    for lon, lat, _ in bb: f.o.append(f'<circle cx="{X(lon):.1f}" cy="{Y(lat):.1f}" r="5" fill="{PIPE}" fill-opacity="0.55" stroke="none"/>')
    for lon, lat, _ in ci: f.o.append(f'<circle cx="{X(lon):.1f}" cy="{Y(lat):.1f}" r="8" fill="{PIPE}" stroke="#000" stroke-width="1.6"/>')
    for lon, lat, _ in wbk:
        if -13 <= lon <= 46 and 30 <= lat <= 57: f.o.append(f'<circle cx="{X(lon):.1f}" cy="{Y(lat):.1f}" r="9" fill="{WBK}" stroke="#000" stroke-width="1.8"/>')
    def call(lon, lat, text, dx, dy):
        cx, cy = X(lon), Y(lat); tx, ty = cx + dx, cy + dy
        f.o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{tx:.1f}" y2="{ty - 8:.1f}" stroke="#000" stroke-width="2"/>')
        w = tw(text, MIN_TYPE) + 16
        f.o.append(f'<rect x="{tx - 8:.1f}" y="{ty - 26:.1f}" width="{w:.1f}" height="36" rx="6" fill="#fff" opacity="0.92"/>')
        f.text(tx, ty, text, MIN_TYPE, 400, INK, 'start')
    call(-9.6, 52.0, 'Ogham stones', 40, 120)
    call(-0.1, 51.5, 'Roman Britain', -20, -60)
    call(15.5, 52.4, 'BB-5KBC findspots', 20, -50)
    call(24.0, 43.2, 'CI findspots (74)', 60, -120)
    call(15.7, 39.2, 'Bruttium coin finds', 90, 100)
    panel_title(1060, 'B', 'World: SISAL caves')
    X2, Y2, mh2 = basemap(f, 1060, 80, 620, -170, 180, -58, 80, 0, 'zb', 0.8)
    for lon, lat, _ in sl: f.o.append(f'<circle cx="{X2(lon):.1f}" cy="{Y2(lat):.1f}" r="4.5" fill="{PIPE}" fill-opacity="0.7" stroke="#000" stroke-width="0.8"/>')
    ex0, ex1, ey0, ey1 = X2(-13), X2(46), Y2(57), Y2(30)
    f.o.append(f'<rect x="{ex0:.1f}" y="{ey0:.1f}" width="{ex1 - ex0:.1f}" height="{ey1 - ey0:.1f}" fill="none" stroke="{RED}" stroke-width="3"/>')
    f.text(1060 + 310, 80 + mh2 + 36, 'red frame = panel A', MIN_TYPE, 400, RED)
    # legend, right column below panel B
    lx, ly = 1070, 80 + mh2 + 100
    f.o.append(f'<circle cx="{lx}" cy="{ly}" r="9" fill="{WBK}" stroke="#000" stroke-width="1.8"/>'); f.text(lx + 24, ly + 8, f'fuzzy-sl Wikibase: {len(wbk)} coordinates', MIN_TYPE, 400, INK, 'start')
    ly += 50
    f.o.append(f'<circle cx="{lx}" cy="{ly}" r="9" fill="{PIPE}" stroke="#000" stroke-width="1.8"/>'); f.text(lx + 24, ly + 8, 'bespoke RDF pipeline:', MIN_TYPE, 400, INK, 'start')
    for t in (f'BB-5KBC findspots ({len(bb)}, small dots)', f'CI findspots ({len(ci)})', f'SISAL caves ({len(sl)})'):
        ly += 40; f.text(lx + 24, ly + 8, t, MIN_TYPE, 400, INK, 'start')
    f.h = int(80 + mh + 24)
    f.done()

# ---------------------------------------------------------------- Z2: one findspot, three paradigms
def z2():
    g, S = load_ci()
    au3 = [s_ for s_ in S if s_['label'] == 'Auel Maar AU3'][0]
    m = re.search(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)', au3['wkt']); lon, lat = m.group(1), m.group(2)
    au4 = wb_entity('Q84'); assert au4['labels']['en']['value'] == 'Auel Maar AU4'
    c4 = au4['claims']['P4'][0]['mainsnak']['datavalue']['value']
    H = 750
    f = Fig('z2_one_findspot_three_paradigms', H)
    def panel_title(x, letter, text):
        f.o.append(f'<rect x="{x}" y="16" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, 46, letter, 28, 500, '#fff'); f.text(x + 56, 46, text, 28, 500, INK, 'start')
    xs = (20, 590, 1160)
    for x in (570, 1140): f.o.append(f'<line x1="{x - 5}" y1="20" x2="{x - 5}" y2="{H - 20}" stroke="#d4d4d0" stroke-width="2"/>')
    panel_title(xs[0], 'A', 'RDF and GeoSPARQL'); panel_title(xs[1], 'B', 'Labelled property graph'); panel_title(xs[2], 'C', 'Heterogeneous information network')
    # A: the coordinate is a literal of a geometry resource
    x0, w = xs[0] + 90, 340; cx = x0 + w / 2
    f.box(x0, 100, w, 96, INST, ['ci:cisite_201', 'Auel Maar AU3']); f.arrow(cx, 196, cx, 300); f.chip(cx, 248, 'geo:hasGeometry')
    f.box(x0, 300, w, 70, INST, ['ci:cisite_201_geom']); f.arrow(cx, 370, cx, 480); f.chip(cx, 425, 'geo:asWKT')
    f.box(x0, 480, w, 96, '#fff', [f'POINT({lon} {lat})', '^^geo:wktLiteral'], stroke=RED, sw=4)
    # B: the coordinate is a property of the node
    x0 = xs[1] + 60; w = 400; cx = x0 + w / 2
    f.box(x0, 100, w, 96, INST, ['(:Findspot)', 'name: "Auel Maar AU3"'])
    f.o.append(f'<line x1="{cx}" y1="196" x2="{cx}" y2="300" stroke="#000" stroke-width="2.5"/>')
    f.box(x0, 300, w, 130, '#fff', ['location:', f'point({{longitude: {lon},', f'latitude: {lat}}})'], stroke=RED, sw=4)
    f.text(cx, 480, 'property of the node, type Point', MIN_TYPE, 400, MUT)
    # C: the coordinate is a node of its own
    bw = 235
    for i, (nm, nid, la, lo) in enumerate((('Auel Maar AU3', 'AU3', lat, lon), ('Auel Maar AU4', 'AU4', c4['latitude'], c4['longitude']))):
        x0 = xs[2] + i * (bw + 50); cx = x0 + bw / 2
        f.box(x0, 100, bw, 70, INST, ['(Findspot)', nm] if False else [nm])
        f.arrow(cx, 170, cx, 320); f.chip(cx, 245, 'located at')
        f.box(x0, 320, bw, 96, '#fff', ['Geolocation', f'{la}_{lo}'], stroke=RED, sw=4)
        f.o.append(f'<line x1="{cx}" y1="416" x2="{cx}" y2="500" stroke="#000" stroke-width="2.5"/>')
    c1, c2 = xs[2] + bw / 2, xs[2] + bw + 50 + bw / 2
    f.o.append(f'<line x1="{c1}" y1="500" x2="{c2}" y2="500" stroke="#000" stroke-width="2.5"/>')
    f.chip((c1 + c2) / 2, 500, 'spatially similar')
    # what each paradigm offers for a distance question
    for x, t in ((xs[0], ['distance question:', 'geof:distance()']), (xs[1], ['distance question:', 'point.distance()']), (xs[2], ['distance question:', 'distance classes in the meta path'])):
        f.text(x + 260, 625, t[0], MIN_TYPE, 400, MUT); f.text(x + 260, 625 + 32, t[1], MIN_TYPE, 500, INK, maxw=520)
    f.text(20, H - 14, 'red outline = where the coordinate sits', MIN_TYPE, 400, RED, 'start')
    f.done()

if __name__ == '__main__':
    want = sys.argv[1:] or ['fig4']
    if 'fig4' in want: fig4()
    if 'z3' in want: z3()
    if 'z2' in want: z2()
