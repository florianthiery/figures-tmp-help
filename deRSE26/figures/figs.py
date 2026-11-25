"""Figures for the revision of "From Relations to Graphs" (deRSE26 / ECEASST). Same style as dh2027/figures/figures.py.

Style: Fira Sans, flat colours, white background, no header or footer in the figure, edge labels as amber chips centred on
the arrow. Width 1700 px = the 420 pt text width of the ECEASST class, so 24 px type arrives at 5.9 pt (minimum: MIN_TYPE).
Everything that the graph states is read from data/ci_findspots.ttl (copy of CI/rdf/ci_findspots.ttl of
Research-Squirrel-Engineers/GeoScience-FAIRification-LOD, commit eec8fe5, CC BY 4.0); nothing of it is typed by hand.

Setup and run (Windows cmd, one line):
  cd /d C:\\git\\wikibase-static-help\\deRSE26\\figures && pip install resvg_py pillow rdflib && python figs.py [fig4]
Output: out/<name>.svg and out/<name>.png (use the PNG in LaTeX: the SVG names Fira Sans without embedding it).
"""
import json, math, os, re, sys
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
def fig4():
    g, S = load_ci()
    H = 930
    f = Fig('fig4_ci_findspots', H)
    # --- panel a: map
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
    # distance rings around the source area (Phlegraean Fields, wd:Q755123)
    slon, slat = 14.14, 40.83
    for km in (500, 1000, 1500, 2000):
        rx = km / (111.2 * math.cos(math.radians(slat))) * kx; ry = km / 111.2 * ky
        f.o.append(f'<ellipse cx="{X(slon):.1f}" cy="{Y(slat):.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="#6b7280" stroke-width="1.6" stroke-dasharray="8 7"/>')
    f.o.append('</g>')
    for km, ang in ((500, 235), (1000, 235)):
        rx = km / (111.2 * math.cos(math.radians(slat))) * kx; ry = km / 111.2 * ky
        tx, ty = X(slon) + rx * math.cos(math.radians(ang)), Y(slat) - ry * math.sin(math.radians(ang))
        if mx + 60 < tx < mx + mw - 60 and my + 30 < ty < my + mh - 30:
            f.o.append(f'<rect x="{tx - 44:.1f}" y="{ty - 18:.1f}" width="88" height="34" rx="6" fill="{SEA}" opacity="0.92"/>')
            f.text(tx, ty + 8, f'{km} km', MIN_TYPE, 400, MUT)
    # findspots by certainty level (fuzzy-sl vocabulary), drawn from the graph
    style = {'high': dict(fill=CLS, stroke='#000', shape='c'), 'medium': dict(fill='#e8a46a', stroke='#000', shape='c'),
             'low': dict(fill='#fff', stroke=CLS, shape='c'), 'dubious': dict(fill='#fff', stroke=CLS, shape='d'),
             'representative': dict(fill=TERM, stroke='#000', shape='s')}
    order = ['dubious', 'low', 'medium', 'high', 'representative']
    for lv in order:
        for s_ in S:
            if s_['level'] != lv: continue
            st, x, y = style[lv], X(s_['lon']), Y(s_['lat'])
            if st['shape'] == 's':
                f.o.append(f'<rect x="{x - 9:.1f}" y="{y - 9:.1f}" width="18" height="18" fill="{st["fill"]}" stroke="{st["stroke"]}" stroke-width="2"/>')
            else:
                f.o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{st["fill"]}" stroke="{st["stroke"]}" stroke-width="{3 if lv in ("low", "dubious") else 1.6}"{" stroke-dasharray=\"4 3\"" if st["shape"] == "d" else ""}/>')
    # source area: star
    sx, sy = X(slon), Y(slat)
    star = ' '.join(f'{sx + (21 if i % 2 == 0 else 9) * math.sin(i * math.pi / 5):.1f},{sy - (21 if i % 2 == 0 else 9) * math.cos(i * math.pi / 5):.1f}' for i in range(10))
    f.o.append(f'<polygon points="{star}" fill="{TERM}" stroke="#000" stroke-width="2"/>')
    # callouts for the findspots that the text names
    by = {s_['id']: s_ for s_ in S}
    def call(ids, text, dx, dy, anchor='start'):
        pts = [(X(by[i]['lon']), Y(by[i]['lat'])) for i in ids]
        cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        tx, ty = cx + dx, cy + dy
        f.o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{tx:.1f}" y2="{ty - 8:.1f}" stroke="#000" stroke-width="1.6"/>')
        w = tw(text, MIN_TYPE) + 16; x0 = tx if anchor == 'start' else tx - w
        f.o.append(f'<rect x="{x0 - 8 if anchor == "start" else x0:.1f}" y="{ty - 26:.1f}" width="{w:.1f}" height="36" rx="6" fill="#fff" opacity="0.92"/>')
        f.text(tx if anchor == 'start' else tx - 8, ty, text, MIN_TYPE, 400, INK, anchor)
    call([44], 'Toplitsa Cave', -40, -100, 'start')
    call([52], 'Urluia', 60, 60)
    call([45], 'Franchthi Cave', 70, 50)
    call([65], 'Haua Fteah', 45, 8)
    call([60], 'Kostenki', -150, 60)
    call([201, 202, 203], 'Auel and Dehner Maar', 40, -75)
    f.text(sx - 20, sy + 62, 'Phlegraean Fields', MIN_TYPE, 500, TERM, 'middle')
    # panel titles: black square with a white letter, then a bold title (as in the figures of the other paper)
    def panel_title(x, letter, text):
        f.o.append(f'<rect x="{x}" y="16" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, 46, letter, 28, 500, '#fff')
        f.text(x + 56, 46, text, 28, 500, INK, 'start')
    panel_title(20, 'a', 'The 74 findspots and the certainty of their coordinates')
    panel_title(840, 'b', 'One coordinate statement and its qualifiers')
    # legend under the map
    ly = my + mh + 40
    cnt = {lv: sum(1 for s_ in S if s_['level'] == lv) for lv in order}
    items = [('high', 'high'), ('medium', 'medium'), ('low', 'low'), ('dubious', 'dubious'), ('representative', 'representative point')]
    x = mx
    for lv, name in items:
        st = style[lv]; label = f'{name} ({cnt[lv]})'
        if x + 18 + tw(label, MIN_TYPE) > mx + mw: x = mx; ly += 46
        if st['shape'] == 's':
            f.o.append(f'<rect x="{x - 9:.1f}" y="{ly - 9:.1f}" width="18" height="18" fill="{st["fill"]}" stroke="#000" stroke-width="2"/>')
        else:
            f.o.append(f'<circle cx="{x:.1f}" cy="{ly:.1f}" r="9" fill="{st["fill"]}" stroke="{st["stroke"]}" stroke-width="{3 if lv in ("low", "dubious") else 1.6}"{" stroke-dasharray=\"4 3\"" if st["shape"] == "d" else ""}/>')
        f.text(x + 18, ly + 8, label, MIN_TYPE, 400, INK, 'start'); x += 18 + tw(label, MIN_TYPE) + 46
    # --- panel b: one coordinate statement (Urluia), read from the graph
    it = URIRef(CI + 'cisite_52'); geom = URIRef(CI + 'cisite_52_geom'); act = URIRef(CI + 'cisite_52_activity')
    FSL = 'http://fuzzy-sl.squirrel.link/ontology/'
    wkt = re.search(r'POINT\(([-\d.]+) ([-\d.]+)\)', str(g.value(geom, GEO.asWKT)))
    lit = sorted({str(o) for o in g.objects(act, GL.hasLiteratureReference)})
    def refs(l):  # "Fitzsimmons et al., 2014" -> author set with years
        d = {}
        for x_ in l:
            m = re.match(r'(.+?),+ (\d{4})$', x_)
            d.setdefault(m.group(1), []).append(m.group(2))
        return d
    rd = refs(lit)
    ref_lines = [f'{a} {", ".join(sorted(set(y)))}' for a, y in rd.items()]
    ref_lines = [l.replace('et al.', 'et al.') for l in ref_lines]
    desc = str(g.value(act, URIRef(FSL + 'activityDesc')))
    assert desc.startswith('set a representative point'), desc
    acting = str(g.value(act, URIRef('http://www.w3.org/ns/prov#wasAssociatedWith'))).rstrip('/').split('/')[-1]
    cdesc = str(g.value(geom, GL.hasCertaintyDescription))
    quote_src = re.match(r'(.+?\(\d{4}\), p\.\s?\d+)', cdesc).group(1).replace('p.76', 'p. 76')
    rows = [
        ('certainty level', [local(g.value(geom, GL.hasCertaintyLevel))]),
        ('certainty description', ['quotation from', quote_src.split(', p.')[0], 'p.' + quote_src.split(', p.')[1]]),
        ('method', [local([o for o in g.objects(act, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')) if FSL in str(o)][0])]),
        ('method description', ['set a representative point', 'based on scientific papers', 'using Google Maps']),
        ('source type', [local(g.value(act, URIRef(FSL + 'hasSourceType')))]),
        ('literature reference', ref_lines),
        ('acting person', [f'ORCID {acting}']),
    ]
    bx0, bw = 1350, 350          # value boxes
    cx0, cw = 840, 200           # coordinate box
    top, bottom = 90, H - 30
    heights = [max(70, 24 * 1.28 * len(v) + 30) for _, v in rows]
    gap = (bottom - top - sum(heights)) / (len(rows) - 1)
    ys = []; y = top
    for h_ in heights: ys.append(y); y += h_ + gap
    cy_mid = (top + bottom) / 2 + 40
    # item box and coordinate box
    lab_ = str(g.value(it, RDFS.label)); nm_, ct_ = re.match(r'(.+?) \((.+)\)', lab_).groups()
    f.box(cx0, 100, cw, 96, INST, [nm_, f'({ct_})'], size=MIN_TYPE)
    f.box(cx0, cy_mid - 60, cw, 120, INST, ['sf:Point', f'POINT({wkt.group(1)}', f'{wkt.group(2)})'], size=MIN_TYPE)
    f.arrow(cx0 + cw / 2, 196, cx0 + cw / 2, cy_mid - 60)
    f.chip(cx0 + cw / 2, (196 + cy_mid - 60) / 2, 'geo:hasGeometry')
    bus = cx0 + cw + 24
    centres = [y_ + h_ / 2 for y_, h_ in zip(ys, heights)]
    f.o.append(f'<line x1="{cx0 + cw}" y1="{cy_mid}" x2="{bus}" y2="{cy_mid}" stroke="#000" stroke-width="2.5"/>')
    f.o.append(f'<line x1="{bus}" y1="{centres[0]:.1f}" x2="{bus}" y2="{centres[-1]:.1f}" stroke="#000" stroke-width="2.5"/>')
    for (lab, vals), y_, h_, ty in zip(rows, ys, heights, centres):
        f.box(bx0, y_, bw, h_, '#fff', vals, size=MIN_TYPE)
        f.arrow(bus, ty, bx0, ty)
        f.chip((bus + bx0) / 2, ty, lab)
    f.done()
    return S

if __name__ == '__main__':
    want = sys.argv[1:] or ['fig4']
    if 'fig4' in want: fig4()
