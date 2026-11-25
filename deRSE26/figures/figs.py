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
    H = 990
    f = Fig('fig4_ci_findspots', H)
    arch_iri = URIRef('http://w3id.org/geo-lod/CIArchaeologicalSite')
    for s_ in S: s_['arch'] = (s_['iri'], URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), arch_iri) in g
    # --- the item of panel B, read from the static copy of the fuzzy-sl Wikibase (Q70 = Auel Maar AU3)
    it = wb_entity('Q70'); assert it['labels']['en']['value'] == 'Auel Maar AU3'
    coord = it['claims']['P4'][0]; cv = coord['mainsnak']['datavalue']['value']
    au3 = [s_ for s_ in S if s_['label'] == 'Auel Maar AU3'][0]
    assert abs(au3['lon'] - cv['longitude']) < 1e-6 and abs(au3['lat'] - cv['latitude']) < 1e-6, 'graph and Wikibase disagree on AU3'
    # --- panel A: map
    mx, my, mw = 90, 80, 710
    LON0, LON1, LAT0, LAT1, LATC = 4.0, 46.0, 31.0, 57.0, 44.0
    X, Y, mh = basemap(f, mx, my, mw, LON0, LON1, LAT0, LAT1, LATC, 'mc', grid=(5, 5))
    kx = mw / (LON1 - LON0); ky = kx / math.cos(math.radians(LATC))
    f.o.append('<g clip-path="url(#mc)">')
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
    panel_title(90, 'A', 'The 74 findspots: archaeology or not')
    panel_title(840, 'B', 'One coordinate statement: Auel Maar AU3')
    ly = my + mh + 84; x = 20
    f.o.append(f'<circle cx="{x}" cy="{ly}" r="9" fill="{CLS}" stroke="#000" stroke-width="1.8"/>'); f.text(x + 18, ly + 8, f'archaeological site ({na})', MIN_TYPE, 400, INK, 'start')
    x = 20 + 18 + tw(f'archaeological site ({na})', MIN_TYPE) + 46
    f.o.append(f'<circle cx="{x}" cy="{ly}" r="9" fill="#fff" stroke="#000" stroke-width="1.8"/>'); f.text(x + 18, ly + 8, f'no archaeological site ({len(S) - na})', MIN_TYPE, 400, INK, 'start')
    ly += 46
    f.o.append(f'<circle cx="{20 + 14}" cy="{ly}" r="14" fill="none" stroke="{RED}" stroke-width="4"/>'); f.text(20 + 38, ly + 8, 'item of', MIN_TYPE, 400, INK, 'start'); badge(f, 20 + 38 + tw('item of ', MIN_TYPE) + 10, ly - 18, 'B', 34)
    x = 20 + 38 + tw('item of ', MIN_TYPE) + 10 + 34 + 46
    sy2 = ly; star2 = ' '.join(f'{x + (14 if i % 2 == 0 else 6) * math.sin(i * math.pi / 5):.1f},{sy2 - (14 if i % 2 == 0 else 6) * math.cos(i * math.pi / 5):.1f}' for i in range(10))
    f.o.append(f'<polygon points="{star2}" fill="{TERM}" stroke="#000" stroke-width="1.5"/>'); f.text(x + 22, ly + 8, 'source area of the eruption', MIN_TYPE, 400, INK, 'start')
    ky_ = ly + 62
    for i, (fl, tcx, t) in enumerate(((TERM, '#fff', 'vocabulary term'), (INST, INK, 'item'), ('#fff', INK, 'literal'))):
        bxx = 20 + i * 0 ; xx = 20 + [0, 250, 400][i]
        f.o.append(f'<rect x="{xx}" y="{ky_ - 16}" width="44" height="32" rx="8" fill="{fl}" stroke="#000" stroke-width="2"/>'); f.text(xx + 56, ky_ + 8, t, MIN_TYPE, 400, INK, 'start')
    # --- panel B: the coordinate statement of Q70 with its qualifiers, as the Wikibase has it
    ql = coord['qualifiers-order'] if 'qualifiers-order' in coord else list(coord['qualifiers'].keys())
    rows = []
    for qp in ql:
        sn = coord['qualifiers'][qp][0]
        txt = snak_text(sn)
        isitem = isinstance(sn['datavalue']['value'], dict) and 'id' in sn['datavalue']['value']
        fill, tc = ((INST, INK) if qp == 'P14' else (TERM, '#fff')) if isitem else ('#fff', INK)   # agent grey, vocabulary term purple, literal white
        rows.append((wb_label(qp), wrap(txt, 350 - 28) if len(txt) > 22 else [txt], fill, tc))
    ref = coord['references'][0]['snaks']; rp = list(ref.keys())[0]
    rows.append((wb_label(rp), ['doi.org/' + snak_text(ref[rp][0]).split('doi.org/')[1]], '#fff', INK))
    heights = [max(64, 24 * 1.28 * len(r_[1]) + 26) for r_ in rows]
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
    # minimap of the item (Central Europe), below the coordinate node
    MX, MY, MW = cx0, cy_mid + 90, cw
    mX, mY, mmh = basemap(f, MX, MY, MW, 3, 13, 47, 55, 51, 'mm4', 1.0, grid=(5, 4), labels=False)
    for s_ in S:
        if s_ is au3 or not (3 <= s_['lon'] <= 13 and 47 <= s_['lat'] <= 55): continue
        f.o.append(f'<circle cx="{mX(s_["lon"]):.1f}" cy="{mY(s_["lat"]):.1f}" r="4.5" fill="{CLS if s_["arch"] else "#fff"}" stroke="#000" stroke-width="1"/>')
    f.o.append(f'<circle cx="{mX(au3["lon"]):.1f}" cy="{mY(au3["lat"]):.1f}" r="15" fill="none" stroke="{RED}" stroke-width="4"/>')
    f.o.append(f'<circle cx="{mX(au3["lon"]):.1f}" cy="{mY(au3["lat"]):.1f}" r="6" fill="{CLS if au3["arch"] else "#fff"}" stroke="#000" stroke-width="1.2"/>')
    f.arrow(cx0 + cw / 2, 196, cx0 + cw / 2, cy_mid - 70)
    f.chip(cx0 + cw / 2, (196 + cy_mid - 70) / 2, 'has coordinate')
    bus = cx0 + cw + 24
    f.o.append(f'<line x1="{cx0 + cw}" y1="{cy_mid:.1f}" x2="{bus}" y2="{cy_mid:.1f}" stroke="#000" stroke-width="2.5"/>')
    f.o.append(f'<line x1="{bus}" y1="{centres[0]:.1f}" x2="{bus}" y2="{centres[-1]:.1f}" stroke="#000" stroke-width="2.5"/>')
    for (lab, vals, fl, tc_), y_, h_, ty in zip(rows, ys, heights, centres):
        f.box(bx0, y_, bw, h_, fl, vals, tc=tc_, size=MIN_TYPE)
        f.arrow(bus, ty, bx0, ty)
        f.chip((bus + bx0) / 2, ty, lab)
    f.done()
    return S

def badge(f, x, y, letter, size=36):
    f.o.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
    f.text(x + size / 2, y + size * 0.72, letter, 26, 500, '#fff')

# ---------------------------------------------------------------- Z3: where the showcases are
PIPE, WBK = CLS, AMB
def pts(setname):
    return [(float(r['lon']), float(r['lat']), r['label']) for r in csv.DictReader(open(os.path.join(HERE, 'data/showcase_points.csv'), encoding='utf8')) if r['set'] == setname]

def basemap(f, mx, my, mw, lon0, lon1, lat0, lat1, latc, clip_id, stroke=1.2, grid=None, labels=True):
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
    if grid:                                        # graticule inside, degree labels outside the frame
        dlon, dlat = grid
        for lo in range(math.ceil(lon0 / dlon) * dlon, int(lon1) + 1, dlon):
            f.o.append(f'<line x1="{X(lo):.1f}" y1="{my}" x2="{X(lo):.1f}" y2="{my + mh:.1f}" stroke="#fff" stroke-width="1.6" stroke-dasharray="3 6" opacity="0.95"/>')
        for la in range(math.ceil(lat0 / dlat) * dlat, int(lat1) + 1, dlat):
            f.o.append(f'<line x1="{mx}" y1="{Y(la):.1f}" x2="{mx + mw}" y2="{Y(la):.1f}" stroke="#fff" stroke-width="1.6" stroke-dasharray="3 6" opacity="0.95"/>')
    f.o.append('</g>')
    f.o.append(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh:.1f}" fill="none" stroke="#000" stroke-width="2"/>')
    if grid and labels:
        fmt = lambda v, p, n: f'{abs(v)}°{p if v >= 0 else n}'
        for lo in range(math.ceil(lon0 / dlon) * dlon, int(lon1) + 1, dlon):
            f.o.append(f'<line x1="{X(lo):.1f}" y1="{my + mh:.1f}" x2="{X(lo):.1f}" y2="{my + mh + 8:.1f}" stroke="#000" stroke-width="2"/>')
            if X(lo) + tw(fmt(lo, 'E', 'W'), MIN_TYPE) / 2 <= W - 4: f.text(X(lo), my + mh + 34, fmt(lo, 'E', 'W'), MIN_TYPE, 400, MUT)
        for la in range(math.ceil(lat0 / dlat) * dlat, int(lat1) + 1, dlat):
            f.o.append(f'<line x1="{mx - 8}" y1="{Y(la):.1f}" x2="{mx}" y2="{Y(la):.1f}" stroke="#000" stroke-width="2"/>')
            f.text(mx - 12, Y(la) + 8, fmt(la, 'N', 'S'), MIN_TYPE, 400, MUT, 'end')
    return X, Y, mh

def z3():
    f = Fig('z3_showcase_map', 900)
    f.o.append(f'<rect x="0" y="0" width="{W}" height="900" fill="#fff"/>')
    bb, sl, wbk = pts('bb5kbc'), pts('sisal'), pts('fuzzysl')
    _, S = load_ci(); ci = [(s_['lon'], s_['lat'], s_['label']) for s_ in S]
    def panel_title(x, letter, text):
        f.o.append(f'<rect x="{x}" y="16" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, 46, letter, 28, 500, '#fff'); f.text(x + 56, 46, text, 28, 500, INK, 'start')
    panel_title(90, 'A', 'Europe and the Mediterranean')
    X, Y, mh = basemap(f, 90, 80, 930, -13, 46, 30, 57, 44, 'za', grid=(10, 5))
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
    panel_title(1100, 'B', 'World: SISAL caves')
    X2, Y2, mh2 = basemap(f, 1140, 80, 540, -170, 180, -58, 80, 0, 'zb', 0.8, grid=(60, 30))
    for lon, lat, _ in sl: f.o.append(f'<circle cx="{X2(lon):.1f}" cy="{Y2(lat):.1f}" r="4.5" fill="{PIPE}" fill-opacity="0.7" stroke="#000" stroke-width="0.8"/>')
    ex0, ex1, ey0, ey1 = X2(-13), X2(46), Y2(57), Y2(30)
    f.o.append(f'<rect x="{ex0:.1f}" y="{ey0:.1f}" width="{ex1 - ex0:.1f}" height="{ey1 - ey0:.1f}" fill="none" stroke="{RED}" stroke-width="3"/>')
    badge(f, ex0, ey0 - 44, 'A')                      # the red frame is panel A
    f.text(1140 + 270, 80 + mh2 + 78, 'red frame: extent of the map in', MIN_TYPE, 400, RED, 'end'); badge(f, 1140 + 280, 80 + mh2 + 48, 'A')
    # legend, right column below panel B
    lx, ly = 1150, 80 + mh2 + 130
    f.o.append(f'<circle cx="{lx}" cy="{ly}" r="9" fill="{WBK}" stroke="#000" stroke-width="1.8"/>'); f.text(lx + 24, ly + 8, f'fuzzy-sl Wikibase: {len(wbk)} coordinates', MIN_TYPE, 400, INK, 'start')
    ly += 50
    f.o.append(f'<circle cx="{lx}" cy="{ly}" r="9" fill="{PIPE}" stroke="#000" stroke-width="1.8"/>'); f.text(lx + 24, ly + 8, 'bespoke RDF pipeline:', MIN_TYPE, 400, INK, 'start')
    for t in (f'BB-5KBC findspots ({len(bb)}, small dots)', f'CI findspots ({len(ci)})', f'SISAL caves ({len(sl)})'):
        ly += 40; f.text(lx + 24, ly + 8, t, MIN_TYPE, 400, INK, 'start')
    f.h = int(80 + mh + 52)
    f.done()

# ---------------------------------------------------------------- Z2: one finding, five modelling styles
def wd_data():
    p = os.path.join(HERE, 'data/wd/Q126503090.json')
    if not os.path.exists(p): return None, None
    return json.load(open(p, encoding='utf8')), json.load(open(os.path.join(HERE, 'data/wd/labels.json'), encoding='utf8'))

def z2():
    it = wb_entity('Q131'); assert it['labels']['en']['value'] == 'Ogham Stone Coumeenole North'
    st = it['claims']['P4'][1]; v = st['mainsnak']['datavalue']['value']          # the statement from Macalister (1945)
    lat, lon = round(v['latitude'], 4), round(v['longitude'], 4)
    quals = [(wb_label(p), snak_text(st['qualifiers'][p][0])) for p in ('P5', 'P7', 'P23', 'P24')]
    wd, wdl = wd_data()
    H = 1230
    f = Fig('z2_one_stone_five_models', H)
    def panel_title(x, y, letter, text):
        f.o.append(f'<rect x="{x}" y="{y}" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, y + 30, letter, 28, 500, '#fff'); f.text(x + 56, y + 30, text, 28, 500, INK, 'start')
    cols = (20, 590, 1160); rows = (16, 676)
    for x in (570, 1140): f.o.append(f'<line x1="{x - 5}" y1="20" x2="{x - 5}" y2="{H - 20}" stroke="#d4d4d0" stroke-width="2"/>')
    f.o.append(f'<line x1="20" y1="{rows[1] - 20}" x2="{W - 20}" y2="{rows[1] - 20}" stroke="#d4d4d0" stroke-width="2"/>')
    # A: Wikidata (read from data/wd/, see fetch_wd.py)
    x0, w = cols[0] + 50, 440; cx = x0 + w / 2; y = rows[0]
    panel_title(cols[0], y, 'A', 'Wikidata')
    if wd:
        c = wd['claims']['P625'][0]; cv = c['mainsnak']['datavalue']['value']
        lab = lambda i: wdl.get(i, i)
        lines = [f"{round(cv['latitude'], 4)}, {round(cv['longitude'], 4)}"]
        for qp, sn in c.get('qualifiers', {}).items():
            vv = sn[0]['datavalue']['value']; lines.append(f"{lab(qp)}: " + (lab(vv['id']) if isinstance(vv, dict) and 'id' in vv else str(vv)))
        f.box(x0, y + 90, w, 96, INST, [wd['labels']['en']['value'], 'Q126503090'])
        f.arrow(cx, y + 186, cx, y + 290); f.chip(cx, y + 238, 'coordinate location')
        f.box(x0, y + 290, w, 60 + 36 * len(lines), '#fff', lines, stroke=RED, sw=4)
    else:
        f.box(x0, y + 90, w, 200, '#fff', ['data/wd/ missing:', 'run fetch_wd.py'], stroke=RED, sw=4, dash=True)
    # B: fuzzy-sl Wikibase
    x0, w = cols[1] + 50, 440; cx = x0 + w / 2
    panel_title(cols[1], y, 'B', 'fuzzy-sl Wikibase')
    f.box(x0, y + 90, w, 96, INST, ['Ogham Stone', 'Coumeenole North (Q131)'])
    f.arrow(cx, y + 186, cx, y + 290); f.chip(cx, y + 238, 'has coordinate')
    f.box(x0, y + 290, w, 60 + 36 * 5, '#fff', [f'{lat}, {lon}'] + [f'{a}: {b}' for a, b in quals], stroke=RED, sw=4)
    f.text(cx, y + 290 + 60 + 36 * 5 + 50, 'qualifiers on the statement', MIN_TYPE, 400, MUT)
    # C: RDF / GeoSPARQL
    x0, w = cols[2] + 50, 440; cx = x0 + w / 2
    panel_title(cols[2], y, 'C', 'RDF and GeoSPARQL')
    f.box(x0, y + 90, w, 96, INST, ['lod.ogham.link/data/Y50000178', 'Ogham Stone Coumeenole North'])
    f.arrow(cx, y + 186, cx, y + 290); f.chip(cx, y + 238, 'geo:hasGeometry')
    f.box(x0, y + 290, w, 70, INST, ['_:geometry']); f.arrow(cx, y + 360, cx, y + 470); f.chip(cx, y + 415, 'geo:asWKT')
    f.box(x0, y + 470, w, 96, '#fff', [f'POINT({lon} {lat})', '^^geo:wktLiteral'], stroke=RED, sw=4)
    # D: labelled property graph
    y = rows[1]; x0, w = cols[0] + 50, 440; cx = x0 + w / 2
    panel_title(cols[0], y, 'D', 'Labelled property graph')
    f.box(x0, y + 90, w, 96, INST, ['(:OghamStone)', 'name: "Coumeenole North"'])
    f.o.append(f'<line x1="{cx}" y1="{y + 186}" x2="{cx}" y2="{y + 290}" stroke="#000" stroke-width="2.5"/>')
    f.box(x0, y + 290, w, 130, '#fff', ['location:', f'point({{longitude: {lon},', f'latitude: {lat}}})'], stroke=RED, sw=4)
    f.text(cx, y + 470, 'property of the node, type Point', MIN_TYPE, 400, MUT)
    # E: heterogeneous information network
    x0, w = cols[1] + 50, 440; cx = x0 + w / 2
    panel_title(cols[1], y, 'E', 'Heterogeneous information network')
    f.box(x0, y + 90, w, 70, INST, ['OghamStone', 'Coumeenole North'] if False else ['Coumeenole North'])
    f.arrow(cx, y + 160, cx, y + 290); f.chip(cx, y + 225, 'located at')
    f.box(x0, y + 290, w, 96, '#fff', ['Geolocation', f'{lat}_{lon}'], stroke=RED, sw=4)
    f.text(cx, y + 440, 'a node of its own; nearby geolocations', MIN_TYPE, 400, MUT); f.text(cx, y + 472, 'can be linked by distance classes', MIN_TYPE, 400, MUT)
    # F: key
    x0 = cols[2] + 30
    f.o.append(f'<rect x="{x0}" y="{y + 20}" width="46" height="30" rx="8" fill="#fff" stroke="{RED}" stroke-width="4"/>'); f.text(x0 + 66, y + 44, 'where the coordinate sits', MIN_TYPE, 400, INK, 'start')
    f.text(x0, y + 130, 'One coordinate: 52.1103 N, 10.4732 W', MIN_TYPE, 500, INK, 'start')
    f.text(x0, y + 170, 'Macalister (1945), textual description', MIN_TYPE, 400, MUT, 'start')
    f.text(x0, y + 220, 'Panels A to C are RDF-based,', MIN_TYPE, 400, MUT, 'start'); f.text(x0, y + 252, 'D and E are not.', MIN_TYPE, 400, MUT, 'start')
    f.done()

# ---------------------------------------------------------------- Fig. 7: CI instances
PFX = {'http://fuzzy-sl.squirrel.link/ontology/': 'fsl:', 'http://w3id.org/geo-lod/': 'geolod:', 'http://www.cidoc-crm.org/extensions/crmarchaeo/': 'crmarchaeo:',
       'http://wikidata.org/entity/': 'wd:', 'http://openstreetmap.org/node/': 'osm-node:', 'http://w3id.org/geo-lod/ci/': 'ci:'}
def short(iri):
    for k in sorted(PFX, key=len, reverse=True):
        if str(iri).startswith(k): return PFX[k] + str(iri)[len(k):]
    return str(iri)

def fig7():
    g, S = load_ci()
    SKOS = Namespace('http://www.w3.org/2004/02/skos/core#'); PROV = Namespace('http://www.w3.org/ns/prov#')
    RDFT = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    KEEP = ('http://fuzzy-sl.squirrel.link/ontology/Site', 'http://w3id.org/geo-lod/CIArchaeologicalSite', 'http://w3id.org/geo-lod/CIFindspot',
            'http://www.cidoc-crm.org/extensions/crmarchaeo/A2_Stratigraphic_Volume_Unit')
    arch_iri = URIRef('http://w3id.org/geo-lod/CIArchaeologicalSite')
    for s_ in S: s_['arch'] = (s_['iri'], RDFT, arch_iri) in g
    PH = 800; H = 2 * PH + 40
    f = Fig('fig7_ci_instances', H)
    def panel(y0, letter, n):
        site = [x for x in S if x['id'] == n][0]; iri = site['iri']; gi = g.value(iri, GEO.hasGeometry)
        title = site['label']
        f.o.append(f'<rect x="20" y="{y0}" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(40, y0 + 30, letter, 28, 500, '#fff'); f.text(76, y0 + 30, title, 28, 500, INK, 'start')
        types = [short(t) for t in KEEP if (iri, RDFT, URIRef(t)) in g]
        assert len(types) == 4, types
        wkt = re.search(r'POINT\s*\([^)]*\)', site['wkt']).group(0)
        level = short(g.value(iri, GL.hasCertaintyLevel)); desc = str(g.value(iri, GL.hasCertaintyDescription)); lit = str(g.value(iri, GL.hasLiteratureReference))
        cm = sorted(short(o) for o in g.objects(iri, SKOS.closeMatch)); gen = short(g.value(iri, PROV.wasGeneratedBy))
        bus, bx0, bw = 360, 840, 560
        rows = [('rdf:type', 'box', types, CLS, '#fff'), ('geo:hasGeometry', 'geom', None, None, None), ('geolod:hasCertaintyLevel', 'box', [level], TERM, '#fff'),
                ('geolod:hasCertaintyDescription', 'box', wrap(desc, bw - 40), '#fff', INK), ('geolod:hasLiteratureReference', 'box', [lit], '#fff', INK),
                ('skos:closeMatch', 'box', cm, '#fff', INK), ('prov:wasGeneratedBy', 'box', [gen], '#fff', INK)]
        hs = [max(64, len(r[2]) * 30.7 + 26) if r[2] else 96 for r in rows]
        top, bottom = y0 + 80, y0 + PH - 20
        gap = (bottom - top - sum(hs)) / (len(rows) - 1)
        ys = []; y = top
        for h_ in hs: ys.append(y); y += h_ + gap
        cs = [a + h_ / 2 for a, h_ in zip(ys, hs)]; mid = cs[2]
        sw_, sh_ = 300, 110
        f.box(20, mid - sh_ / 2, sw_, sh_, INST, [short(iri), site['label']], size=MIN_TYPE)
        f.o.append(f'<line x1="{20 + sw_}" y1="{mid:.1f}" x2="{bus}" y2="{mid:.1f}" stroke="#000" stroke-width="2.5"/>')
        MX, MY, MW = 20, mid + 85, 300                  # minimap below the instance node
        X, Y, mh = basemap(f, MX, MY, MW, 4, 46, 31, 57, 44, f'mm{n}', 1.0, grid=(10, 10), labels=False)
        for o in S:
            if o['id'] == n: continue
            f.o.append(f'<circle cx="{X(o["lon"]):.1f}" cy="{Y(o["lat"]):.1f}" r="4.5" fill="{CLS if o["arch"] else "#fff"}" stroke="#000" stroke-width="1"/>')
        f.o.append(f'<circle cx="{X(site["lon"]):.1f}" cy="{Y(site["lat"]):.1f}" r="15" fill="none" stroke="{RED}" stroke-width="4"/>')
        f.o.append(f'<circle cx="{X(site["lon"]):.1f}" cy="{Y(site["lat"]):.1f}" r="6" fill="{CLS if site["arch"] else "#fff"}" stroke="#000" stroke-width="1.2"/>')
        f.o.append(f'<line x1="{bus}" y1="{cs[0]:.1f}" x2="{bus}" y2="{cs[-1]:.1f}" stroke="#000" stroke-width="2.5"/>')
        for (lab, kind, val, fill, tc), a, h_, c in zip(rows, ys, hs, cs):
            if kind == 'box':
                f.box(bx0, a, bw, h_, fill, val, tc=tc, size=MIN_TYPE)
                f.arrow(bus, c, bx0, c); f.chip((bus + bx0) / 2, c, lab)
            else:
                f.box(bx0, a, 250, h_, INST, [short(gi), 'a sf:Point'][:2], size=MIN_TYPE)
                f.arrow(bus, c, bx0, c); f.chip((bus + bx0) / 2, c, lab)
                f.box(1380, a, 300, h_, '#fff', [wkt], size=MIN_TYPE)
                f.arrow(bx0 + 250, c, 1380, c); f.chip((bx0 + 250 + 1380) / 2, c, 'geo:asWKT')
    panel(16, 'A', 44); panel(16 + PH + 40, 'B', 45)
    f.o.append(f'<line x1="20" y1="{PH + 20}" x2="{W - 20}" y2="{PH + 20}" stroke="#d4d4d0" stroke-width="2"/>')
    f.done()

# ---------------------------------------------------------------- Fig. 6: the place classes of the taxonomy
def fig6():
    onto = Graph()
    base = '/home/claude/research-squirrel-engineers/geoscience-fairification-lod'
    for p in ('ontology/geo_lod_core.ttl', 'ontology/crm_bridging.ttl', 'SISAL/rdf/sisal_ontology.ttl', 'EPICA/rdf/epica_ontology.ttl'):
        onto.parse(os.path.join(os.environ.get('GEOLOD_DIR', base), p), format='turtle')
    EX = {'geolod:': 'http://w3id.org/geo-lod/', 'crm:': 'http://www.cidoc-crm.org/cidoc-crm/', 'crmarchaeo:': 'http://www.cidoc-crm.org/extensions/crmarchaeo/', 'geo:': 'http://www.opengis.net/ont/geosparql#', 'fsl:': 'http://fuzzy-sl.squirrel.link/ontology/'}
    def iri(q): return URIRef(next(v + q[len(k):] for k, v in EX.items() if q.startswith(k)))
    RS = URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf')
    f = Fig('fig6_place_taxonomy', 900)
    nodes = {   # label: (x centre, y top, kind, lines)
        'crm:E53_Place': (150, 30, 'x', None), 'geo:Feature': (470, 30, 'x', None), 'crm:E27_Site': (800, 30, 'x', None),
        'geolod:SamplingLocation': (330, 250, 'c', None), 'geolod:CIFindspot': (1030, 250, 'c', None), 'fsl:Site': (1330, 250, 'x', None),
        'geolod:DrillingSite': (125, 470, 'c', None), 'geolod:Borehole': (410, 470, 'c', None), 'geolod:Cave': (720, 470, 'c', None),
        'geolod:CIArchaeologicalSite': (1030, 470, 'c', None),
        'crmarchaeo:A2_Stratigraphic_Volume_Unit': (1480, 705, 'x', ['crmarchaeo:A2_', 'Stratigraphic_Volume_Unit']),
        'geolod:ArchaeologicalCaveSite': (720, 720, 'c', None)}
    edges = [('geolod:SamplingLocation', 'crm:E53_Place'), ('geolod:SamplingLocation', 'geo:Feature'), ('geolod:SamplingLocation', 'crm:E27_Site'),
             ('geolod:CIFindspot', 'crm:E27_Site'), ('fsl:Site', 'crm:E27_Site'),
             ('geolod:DrillingSite', 'geolod:SamplingLocation'), ('geolod:Borehole', 'geolod:SamplingLocation'), ('geolod:Cave', 'geolod:SamplingLocation'),
             ('geolod:ArchaeologicalCaveSite', 'geolod:Cave'), ('geolod:ArchaeologicalCaveSite', 'crmarchaeo:A2_Stratigraphic_Volume_Unit'),
             ('geolod:CIArchaeologicalSite', 'geolod:CIFindspot'), ('geolod:CIArchaeologicalSite', 'crmarchaeo:A2_Stratigraphic_Volume_Unit')]
    for a, b in edges:
        assert (iri(a), RS, iri(b)) in onto, (a, b)
    geom = {}
    for lab, (cx, y, kind, lines) in nodes.items():
        ls = lines or [lab]; geom[lab] = (cx, y, max(tw(l, MIN_TYPE) for l in ls) + 44, 80 if len(ls) == 1 else 110)
    def edge_pt(g_, tx, ty):                          # point where the line from the centre of g_ towards (tx, ty) leaves the box
        cx, y, w, h = g_; cy = y + h / 2; dx, dy = tx - cx, ty - cy
        k = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
        return cx + dx * k, cy + dy * k
    for a, b in edges:
        ga, gb = geom[a], geom[b]
        x1, y1 = edge_pt(ga, gb[0], gb[1] + gb[3] / 2); x2, y2 = edge_pt(gb, ga[0], ga[1] + ga[3] / 2)
        t_ = 0.62 if a == 'geolod:Borehole' else 0.5
        f.arrow(x1, y1, x2, y2); f.chip(x1 + (x2 - x1) * t_, y1 + (y2 - y1) * t_, 'subClassOf')
    for lab, (cx, y, w, h) in geom.items():
        k = nodes[lab][2]
        f.box(cx - w / 2, y, w, h, CLS if k == 'c' else '#fff', nodes[lab][3] or [lab], tc='#fff' if k == 'c' else INK)
    ly = 850
    f.o.append(f'<rect x="20" y="{ly - 16}" width="44" height="32" rx="8" fill="{CLS}" stroke="#000" stroke-width="2"/>'); f.text(76, ly + 8, 'class of the geo-lod ontologies', MIN_TYPE, 400, INK, 'start')
    f.o.append(f'<rect x="560" y="{ly - 16}" width="44" height="32" rx="8" fill="#fff" stroke="#000" stroke-width="2"/>'); f.text(616, ly + 8, 'class of CIDOC CRM, CRMarchaeo, GeoSPARQL or fuzzy-sl', MIN_TYPE, 400, INK, 'start')
    f.done()

if __name__ == '__main__':
    want = sys.argv[1:] or ['fig4']
    if 'fig4' in want: fig4()
    if 'z3' in want: z3()
    if 'z2' in want: z2()
    if 'fig7' in want: fig7()
    if 'fig6' in want: fig6()
