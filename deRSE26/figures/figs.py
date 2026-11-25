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
F4, F5, F7 = (os.path.join(HERE, 'fonts/FiraSans-%d.ttf' % n) for n in (400, 500, 700))
W = 1700
MIN_TYPE = 24
INST, CLS, TERM, AMB = '#e2e8f0', '#9a3412', '#4c1d95', '#fbbf24'
INK, MUT, RED = '#1f1f1d', '#55544f', '#dc2626'
SEA, LAND, COAST = '#dce9f1', '#f3f0e7', '#b3b0a4'

_fonts = {}
def tw(s, size, w=400):
    k = (size, w)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype({500: F5, 700: F7}.get(w, F4), size, layout_engine=ImageFont.Layout.BASIC)
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
        da = ' stroke-dasharray="10 6"' if dash else ''
        s.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
        n = len(lines); gap = size * 1.28; y0 = y + h / 2 - (n - 1) * gap / 2 + size * 0.34
        for i, l in enumerate(lines): s.text(x + w / 2, y0 + i * gap, l, size, 500 if (i == 0 and n > 1 and fill != '#fff') else 400, tc, maxw=w - 24)
    def chip(s, cx, cy, t, size=MIN_TYPE):
        w = tw(t, size) + 28
        s.o.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - 22:.1f}" width="{w:.1f}" height="44" rx="22" fill="{AMB}" stroke="#000" stroke-width="1.5"/>')
        s.text(cx, cy + size * 0.34, t, size)
    def arrow(s, x1, y1, x2, y2, col='#000', w=2.5):
        s.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" marker-end="url(#a)"/>')
    def done(s):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{s.h}" viewBox="0 0 {W} {s.h}">' + ('' if getattr(s, 'transparent', False) else f'<rect width="{W}" height="{s.h}" fill="#ffffff"/>') + ''
                '<defs><marker id="a" markerUnits="userSpaceOnUse" markerWidth="18" markerHeight="18" refX="16" refY="9" orient="auto"><path d="M0,0 L18,9 L0,18 z" fill="#000"/></marker></defs>')
        svg = head + '\n'.join(s.o) + '</svg>'
        os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
        open(os.path.join(HERE, f'out/{s.name}.svg'), 'w', encoding='utf8').write(svg)
        open(os.path.join(HERE, f'out/{s.name}.png'), 'wb').write(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[F4, F5, F7], skip_system_fonts=True, zoom=1.0)))
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
    X, Y, mh = basemap(f, mx, my, mw, LON0, LON1, LAT0, LAT1, LATC, 'mc', grid=(5, 5), detail=(4, True))
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
    lx0, lx1, lt, lb = 90, 800, my + mh + 70, my + mh + 70 + 190          # legend card under the map, same width as the map
    f.o.append(f'<rect x="{lx0}" y="{lt}" width="{lx1 - lx0}" height="{lb - lt}" rx="14" fill="#fff" stroke="#d4d4d0" stroke-width="2"/>')
    def lbadge(y, letter):
        f.o.append(f'<rect x="{lx0 + 20}" y="{y - 18}" width="36" height="36" rx="6" fill="#000"/>'); f.text(lx0 + 38, y + 8, letter, 26, 500, '#fff')
    r1_, r2_, r3_ = lt + 40, lt + 92, lt + 160
    lbadge(r1_, 'A'); lbadge(r2_, 'A')
    cxa, cxb = lx0 + 80, lx0 + 400
    f.o.append(f'<circle cx="{cxa}" cy="{r1_}" r="9" fill="{CLS}" stroke="#000" stroke-width="1.8"/>'); f.text(cxa + 20, r1_ + 8, f'archaeological site ({na})', MIN_TYPE, 400, INK, 'start')
    f.o.append(f'<circle cx="{cxb}" cy="{r1_}" r="9" fill="#fff" stroke="#000" stroke-width="1.8"/>'); f.text(cxb + 20, r1_ + 8, f'other findspot ({len(S) - na})', MIN_TYPE, 400, INK, 'start')
    f.o.append(f'<circle cx="{cxa}" cy="{r2_}" r="14" fill="none" stroke="{RED}" stroke-width="4"/>'); f.text(cxa + 26, r2_ + 8, 'item of', MIN_TYPE, 400, INK, 'start'); badge(f, cxa + 26 + tw('item of ', MIN_TYPE) + 8, r2_ - 17, 'B', 34)
    sx2 = cxb; star2 = ' '.join(f'{sx2 + (14 if i % 2 == 0 else 6) * math.sin(i * math.pi / 5):.1f},{r2_ - (14 if i % 2 == 0 else 6) * math.cos(i * math.pi / 5):.1f}' for i in range(10))
    f.o.append(f'<polygon points="{star2}" fill="{TERM}" stroke="#000" stroke-width="1.5"/>'); f.text(sx2 + 22, r2_ + 8, 'eruption source', MIN_TYPE, 400, INK, 'start')
    f.o.append(f'<line x1="{lx0 + 20}" y1="{lt + 126}" x2="{lx1 - 20}" y2="{lt + 126}" stroke="#d4d4d0" stroke-width="2"/>')
    lbadge(r3_, 'B')
    xx = lx0 + 80
    for fl, t in ((TERM, 'vocabulary term'), (INST, 'item'), ('#fff', 'literal')):
        f.o.append(f'<rect x="{xx}" y="{r3_ - 16}" width="44" height="32" rx="8" fill="{fl}" stroke="#000" stroke-width="2"/>'); f.text(xx + 56, r3_ + 8, t, MIN_TYPE, 400, INK, 'start'); xx += 56 + tw(t, MIN_TYPE) + 36
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
    MX, MY, MW = cx0, cy_mid + 140, cw
    mX, mY, mmh = basemap(f, MX, MY, MW, 4.5, 9.0, 48.9, 51.7, 50.3, 'mm4', 1.0, grid=(1, 1), labels=False, detail=(8, True), cities=(0, {'Cologne': 'end', 'Daun': 'start'}))
    for s_ in S:
        if s_ is au3 or not (4.5 <= s_['lon'] <= 9.0 and 48.9 <= s_['lat'] <= 51.7): continue
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

EXTRA_PLACES = {'Daun': (6.833, 50.199)}      # not in Natural Earth; added for orientation next to the Auel Maar (Daun, Eifel; coordinates from OpenStreetMap)

def basemap(f, mx, my, mw, lon0, lon1, lat0, lat1, latc, clip_id, stroke=1.2, grid=None, labels=True, detail=None, cities=None):
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
    if detail:                                      # lakes, rivers and country borders: (max min_zoom of the rivers, borders yes/no)
        zmax, bord = detail
        P = lambda c: ' '.join(('M' if i == 0 else 'L') + f'{X(p[0]):.1f},{Y(p[1]):.1f}' for i, p in enumerate(c))
        for lk in json.load(open(os.path.join(HERE, 'data/ne_eu_lakes.json'), encoding='utf8')):
            for poly in lk['p']: f.o.append(f'<path d="{P(poly[0])}Z" fill="{SEA}" stroke="{COAST}" stroke-width="{stroke}"/>')
        for rv in json.load(open(os.path.join(HERE, 'data/ne_eu_rivers.json'), encoding='utf8')):
            if rv['z'] <= zmax:
                for l in rv['l']: f.o.append(f'<path d="{P(l)}" fill="none" stroke="#8fb4cf" stroke-width="{2.2 if zmax > 5 else 1.6}" stroke-linejoin="round"/>')
        if bord:
            for l in json.load(open(os.path.join(HERE, 'data/ne_eu_borders.json'), encoding='utf8')): f.o.append(f'<path d="{P(l)}" fill="none" stroke="#8a877d" stroke-width="{1.6 if zmax > 5 else 1.2}" stroke-dasharray="7 5"/>')
    if cities:                                      # {name: label anchor}; places come from Natural Earth plus EXTRA_PLACES
        wanted = cities[1]
        for c in json.load(open(os.path.join(HERE, 'data/ne_eu_places.json'), encoding='utf8')) + [dict(n=k, x=v[0], y=v[1]) for k, v in EXTRA_PLACES.items()]:
            if c['n'] in wanted and lon0 <= c['x'] <= lon1 and lat0 <= c['y'] <= lat1:
                f.o.append(f'<rect x="{X(c["x"]) - 5:.1f}" y="{Y(c["y"]) - 5:.1f}" width="10" height="10" fill="{MUT}" stroke="#fff" stroke-width="1.5"/>')
                dx = -10 if wanted[c['n']] == 'end' else 10
                f.o.append(f'<text x="{X(c["x"]) + dx:.1f}" y="{Y(c["y"]) + 8:.1f}" text-anchor="{wanted[c["n"]]}" font-family="Fira Sans" font-size="{MIN_TYPE}" font-weight="400" fill="{INK}" stroke="{LAND}" stroke-width="5" paint-order="stroke">{esc(c["n"])}</text>')
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
    X, Y, mh = basemap(f, 90, 80, 930, -13, 46, 30, 57, 44, 'za', grid=(10, 5), detail=(4, True))
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
    H = 1280
    f = Fig('z2_one_stone_five_models', H)
    def panel_title(x, y, letter, text):
        f.o.append(f'<rect x="{x}" y="{y}" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, y + 30, letter, 28, 500, '#fff'); f.text(x + 56, y + 30, text, 28, 500, INK, 'start')
    cols = (20, 590, 1160); rows = (16, 726)
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
        wl = wd['labels']['en']['value'].split(' / ') + ['Q126503090']
        f.box(x0, y + 90, w, 30 + 31 * len(wl), INST, wl)
        f.arrow(cx, y + 120 + 31 * len(wl), cx, y + 290); f.chip(cx, y + (120 + 31 * len(wl) + 290) / 2, 'coordinate location')
        lines = [t for l in lines for t in wrap(l, w - 30)]
        f.box(x0, y + 290, w, 40 + 31 * len(lines), '#fff', lines, stroke=RED, sw=4)
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
    f.text(x0, y + 130, f'One coordinate: {lat} N, {abs(lon)} W', MIN_TYPE, 500, INK, 'start')
    f.text(x0, y + 170, 'Macalister (1945), textual description', MIN_TYPE, 400, MUT, 'start')
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
        X, Y, mh = basemap(f, MX, MY, MW, 4, 46, 31, 57, 44, f'mm{n}', 1.0, grid=(10, 10), labels=False, detail=(3, True))
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

# ---------------------------------------------------------------- Fig. 6: place classes and the geometry pattern
def fig6():
    onto = Graph()
    base = os.environ.get('GEOLOD_DIR', '/home/claude/research-squirrel-engineers/geoscience-fairification-lod')
    for p in ('ontology/geo_lod_core.ttl', 'ontology/crm_bridging.ttl', 'SISAL/rdf/sisal_ontology.ttl', 'EPICA/rdf/epica_ontology.ttl'):
        onto.parse(os.path.join(base, p), format='turtle')
    EX = {'geolod:': 'http://w3id.org/geo-lod/', 'crm:': 'http://www.cidoc-crm.org/cidoc-crm/', 'crmarchaeo:': 'http://www.cidoc-crm.org/extensions/crmarchaeo/',
          'geo:': 'http://www.opengis.net/ont/geosparql#', 'fsl:': 'http://fuzzy-sl.squirrel.link/ontology/', 'crmgeo:': 'http://www.ics.forth.gr/isl/CRMgeo/', 'sf:': 'http://www.opengis.net/ont/sf#'}
    def iri(q): return URIRef(next(v + q[len(k):] for k, v in EX.items() if q.startswith(k)))
    RS = URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf')
    H = 1560
    f = Fig('fig6_place_taxonomy', H)
    GRP = '<marker id="h" markerUnits="userSpaceOnUse" markerWidth="1" markerHeight="1"/>'
    def box(cx, y, label, kind, lines=None, h=80):
        ls = lines or [label]; w = max(tw(l, MIN_TYPE) for l in ls) + 44
        f.box(cx - w / 2, y, w, h, CLS if kind == 'c' else '#fff', ls, tc='#fff' if kind == 'c' else INK)
        return (cx, y, w, h)
    def seg(x1, y1, x2, y2): f.o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="2.5"/>')
    def inherit(x, y_from, y_tip):                    # vertical line up to the parent, hollow triangle at the parent
        seg(x, y_from, x, y_tip + 26)
        f.o.append(f'<polygon points="{x},{y_tip} {x - 15},{y_tip + 27} {x + 15},{y_tip + 27}" fill="#fff" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/>')
    def title(x, y, letter, text):
        f.o.append(f'<rect x="{x}" y="{y}" width="40" height="40" rx="6" fill="#000" stroke="#000" stroke-width="1"/>')
        f.text(x + 20, y + 30, letter, 28, 500, '#fff'); f.text(x + 56, y + 30, text, 28, 500, INK, 'start')
    # ---- A: class hierarchy, every edge vertical (horizontal only on a bus); every inheritance is asserted in the ontology files
    title(20, 16, 'A', 'Place classes and their anchors')
    y1, y2, y3, y4 = 100, 320, 540, 770
    n = {}
    n['crm:E53_Place'] = box(150, y1, 'crm:E53_Place', 'x'); n['geo:Feature'] = box(450, y1, 'geo:Feature', 'x'); n['crm:E27_Site'] = box(1150, y1, 'crm:E27_Site', 'x')
    n['geolod:SamplingLocation'] = box(300, y2, 'geolod:SamplingLocation', 'c'); n['geolod:CIFindspot'] = box(1230, y2, 'geolod:CIFindspot', 'c'); n['fsl:Site'] = box(1560, y2, 'fsl:Site', 'x')
    n['geolod:DrillingSite'] = box(150, y3, 'geolod:DrillingSite', 'c'); n['geolod:Borehole'] = box(440, y3, 'geolod:Borehole', 'c'); n['geolod:Cave'] = box(700, y3, 'geolod:Cave', 'c')
    n['crmarchaeo:A2_Stratigraphic_Volume_Unit'] = box(1000, y3, '', 'x', ['crmarchaeo:A2_', 'Stratigraphic_Volume_Unit'], 110)
    n['geolod:ArchaeologicalCaveSite'] = box(700, y4, 'geolod:ArchaeologicalCaveSite', 'c'); n['geolod:CIArchaeologicalSite'] = box(1230, y4, 'geolod:CIArchaeologicalSite', 'c')
    for a_, b_ in [('geolod:SamplingLocation', 'crm:E53_Place'), ('geolod:SamplingLocation', 'geo:Feature'), ('geolod:SamplingLocation', 'crm:E27_Site'), ('geolod:CIFindspot', 'crm:E27_Site'), ('fsl:Site', 'crm:E27_Site'),
                   ('geolod:DrillingSite', 'geolod:SamplingLocation'), ('geolod:Borehole', 'geolod:SamplingLocation'), ('geolod:Cave', 'geolod:SamplingLocation'),
                   ('geolod:ArchaeologicalCaveSite', 'geolod:Cave'), ('geolod:ArchaeologicalCaveSite', 'crmarchaeo:A2_Stratigraphic_Volume_Unit'),
                   ('geolod:CIArchaeologicalSite', 'geolod:CIFindspot'), ('geolod:CIArchaeologicalSite', 'crmarchaeo:A2_Stratigraphic_Volume_Unit')]:
        assert (iri(a_), RS, iri(b_)) in onto, (a_, b_)
    bot = y1 + 80                                      # bottom of the top row
    seg(300, y2, 300, 250); seg(150, 250, 1090, 250)   # SamplingLocation bus
    inherit(150, 250, bot); inherit(450, 250, bot); inherit(1090, 250, bot)
    inherit(1170, y2, bot)                             # CIFindspot straight up
    seg(1560, y2, 1560, 285); seg(1560, 285, 1230, 285); inherit(1230, 285, bot)   # fsl:Site
    seg(150, y3, 150, 470); seg(440, y3, 440, 470); seg(700, y3, 700, 470); seg(150, 470, 700, 470); inherit(300, 470, y2 + 80)   # drilling, borehole, cave -> SamplingLocation
    inherit(660, y4, y3 + 80)                          # ArchaeologicalCaveSite -> Cave
    seg(800, y4, 800, 710); seg(1100, y4, 1100, 710); seg(800, 710, 1100, 710); inherit(1000, 710, y3 + 110)   # both archaeological classes -> A2
    inherit(1230, y4, y2 + 80)                         # CIArchaeologicalSite -> CIFindspot (passes between A2 and the right margin)
    # ---- B: how the geometry is modelled; starts at geolod:SamplingLocation of panel A, which inherits from geo:Feature
    yb = 920
    f.o.append(f'<line x1="20" y1="{yb - 30}" x2="{W - 20}" y2="{yb - 30}" stroke="#d4d4d0" stroke-width="2"/>')
    title(20, yb, 'B', 'Geometry pattern (GeoSPARQL, Simple Features, CRMgeo)')
    r0, r1, r2 = yb + 90, yb + 250, yb + 470
    ft = box(250, r0, 'geo:Feature', 'x'); sl = box(250, r1, 'geolod:SamplingLocation', 'c')
    inherit(250, r1, r0 + 80)
    ge = box(900, r1, 'geo:Geometry', 'x'); sp = box(1430, r1, 'crmgeo:SP6_Declarative_Place', 'x')
    wk = box(880, r2, 'geo:wktLiteral', 'x'); pt = box(1200, r2, 'sf:Point', 'x')
    f.arrow(sl[0] + sl[2] / 2, r1 + 40, ge[0] - ge[2] / 2, r1 + 40); f.chip((sl[0] + sl[2] / 2 + ge[0] - ge[2] / 2) / 2, r1 + 40, 'geo:hasGeometry')
    f.arrow(880, r1 + 80, 880, r2); f.chip(880, (r1 + 80 + r2) / 2 - 10, 'geo:asWKT')
    seg(1200, r2, 1200, r2 - 70); seg(970, r2 - 70, 1430, r2 - 70); inherit(970, r2 - 70, r1 + 80); inherit(1430, r2 - 70, r1 + 80)
    for a_, b_ in (('sf:Point', 'crmgeo:SP6_Declarative_Place'), ('geolod:SamplingLocation', 'geo:Feature')): assert (iri(a_), RS, iri(b_)) in onto, (a_, b_)
    # ---- key
    ly = H - 55
    f.o.append(f'<rect x="20" y="{ly - 16}" width="44" height="32" rx="8" fill="{CLS}" stroke="#000" stroke-width="2"/>'); f.text(76, ly + 8, 'class of the geo-lod ontologies', MIN_TYPE, 400, INK, 'start')
    f.o.append(f'<rect x="520" y="{ly - 16}" width="44" height="32" rx="8" fill="#fff" stroke="#000" stroke-width="2"/>'); f.text(576, ly + 8, 'external class', MIN_TYPE, 400, INK, 'start')
    f.o.append(f'<polygon points="860,{ly - 14} 845,{ly + 13} 875,{ly + 13}" fill="#fff" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/>'); f.text(895, ly + 8, 'inherits from (rdfs:subClassOf)', MIN_TYPE, 400, INK, 'start')
    f.o.append(f'<rect x="1360" y="{ly - 20}" width="60" height="40" rx="20" fill="{AMB}" stroke="#000" stroke-width="1.5"/>'); f.text(1436, ly + 8, 'property', MIN_TYPE, 400, INK, 'start')
    f.done()

# ---------------------------------------------------------------- Fig. 3: data model of the fuzzy-sl Wikibase
def fig3():
    """Redraw of fuzzy-sl_Wikibase.jpg: coordinate metadata (CM) and geolocation metadata (GLM) of a fuzzy-sl entity.
    Properties, labels, datatypes and the class of every value are read from the static Wikibase copy (data/wb/); the item Q70
    (Auel Maar AU3) is the witness that every statement, qualifier and reference of the picture really occurs."""
    it = wb_entity('Q70'); assert it['labels']['en']['value'] == 'Auel Maar AU3'
    cl = it['claims']
    def plabel(p): return wb_label(p)
    def itemid(sn): return sn['datavalue']['value']['id']
    def cls(q):                                         # class of a value item: its P1 (instance of)
        c = itemid(wb_entity(q)['claims']['P1'][0]['mainsnak'])
        return f'{wb_label(c)} ({c})'
    coord = cl['P4'][0]; quals, refs = coord['qualifiers'], coord['references'][0]['snaks']
    QL = ['P5', 'P13', 'P7', 'P14', 'P6', 'P16', 'P15', 'P24', 'P33', 'P23']
    RL = ['P17', 'P25', 'P31']
    assert set(QL) == set(quals), set(QL) ^ set(quals)
    assert set(refs) == {'P17'} and all(wb_entity(p)['descriptions']['en']['value'] == 'reference property' for p in ('P25', 'P31'))
    assert all(wb_entity(p)['descriptions']['en']['value'] == 'coordinate qualifier' for p in QL if p not in ('P12',))
    assert wb_entity('P4')['datatype'] == 'globe-coordinate'
    LIT = {'P13': 'Certainty Description', 'P15': 'Method Description', 'P23': 'WGS precision', 'P11': 'Reference String', 'P25': 'Reference String'}
    def target(p, snak=None):                           # (text, kind) of the value node of property p
        d = wb_entity(p)['datatype']
        if d == 'wikibase-item': return (cls(itemid(snak)) if snak else 'fuzzy-sl Entity', 'term' if snak else 'inst')
        if d == 'string': return LIT[p], 'lit'
        if d == 'url': return 'External Resource URI', 'ext'
        raise ValueError(p)
    GM = ['P1', 'P3', 'P11', 'P10']                     # main statements of the entity (picture order), then P8 and P32
    for p in GM + ['P8', 'P26', 'P32']: assert p in cl, p
    assert 'P12' in cl['P10'][0]['qualifiers'] and wb_entity('P12')['datatype'] == 'url'
    assert 'wikidata.org/entity/' in cl['P32'][0]['mainsnak']['datavalue']['value']
    assert 'P17' in cl['P11'][0]['references'][0]['snaks']

    def pr(prefix, p): return f'{prefix}{p}: {plabel(p)}'
    BX, NH = 700, 44
    chip_max = tw(pr('', 'P32'), MIN_TYPE) + 28
    GZ = chip_max + 76                                   # zone between bus and the value nodes on the right
    GW = 300
    assert BX + GZ + GW <= 1660, (BX + GZ + GW)
    f = Fig('fig3_fuzzysl_datamodel', 1630)
    FILL = {'inst': (INST, INK, False), 'term': (TERM, '#fff', False), 'ext': ('#fff', INK, True), 'lit': ('#fff', INK, False), 'wkt': (INK, '#fff', False)}
    def node(x, cy, w, text, kind):
        fill, tc, dash = FILL[kind]
        f.box(x, cy - NH / 2, w, NH, fill, [text], '#000', 2, 22 if kind in ('inst', 'term') else 8, tc, dash=dash)
    def line(x1, y1, x2, y2, dashed=False, arrow=True):
        da = ' stroke-dasharray="10 7"' if dashed else ''
        mk = ' marker-end="url(#a)"' if arrow else ''
        f.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000" stroke-width="2.5"{da}{mk}/>')
    def edge(x1, y1, x2, y2, label, dashed=False):
        line(x1, y1, x2, y2, dashed); f.chip((x1 + x2) / 2, (y1 + y2) / 2, label)
    def title(x, y, tag, text):
        bw = 24 + tw(tag, 26, 500)
        f.o.append(f'<rect x="{x}" y="{y}" width="{bw:.1f}" height="40" rx="6" fill="#000"/>')
        f.text(x + bw / 2, y + 29, tag, 26, 500, '#fff')
        f.text(x + bw + 16, y + 30, text, 28, 500, INK, 'start')
    def frame(y0, y1):
        f.o.append(f'<rect x="20" y="{y0}" width="1660" height="{y1 - y0}" rx="16" fill="none" stroke="#d4d4d0" stroke-width="3"/>')

    # ---- GLM (top)
    frame(20, 930); title(44, 40, 'GLM', 'Geolocation Metadata')
    yl, yd, ye = 140, 215, 290
    node(BX - 130, yl, 260, 'label (en)', 'lit'); node(BX - 130, yd, 260, 'description (en)', 'lit'); node(BX - 130, ye, 260, 'fuzzy-sl Entity', 'inst')
    line(BX, ye - NH / 2, BX, yd + NH / 2 + 2); line(BX, yd - NH / 2, BX, yl + NH / 2 + 2)
    rows = [(360, 'P1'), (420, 'P3'), (480, 'P11'), (540, 'P10'), (750, 'P8'), (810, 'P26'), (870, 'P32')]
    y_p12 = 690
    line(BX, ye + NH / 2, BX, rows[-1][0], arrow=False)
    tx = BX + GZ
    for cy, p in rows:
        snak = cl[p][0]['mainsnak']
        if p == 'P32': text, kind = 'Wikidata Entity', 'ext'
        else: text, kind = target(p, snak if wb_entity(p)['datatype'] == 'wikibase-item' else None)
        node(tx, cy, GW, text, kind)
        edge(BX, cy, tx, cy, pr('', p))
    node(tx, y_p12, GW, 'External Resource URI', 'ext')
    cxm = tx + GW / 2
    edge(cxm, 540 + NH / 2, cxm, y_p12 - NH / 2, pr('q', 'P12'))
    # legend (left)
    lx0, ly0, lw = 44, 330, 440
    f.o.append(f'<rect x="{lx0}" y="{ly0}" width="{lw}" height="480" rx="12" fill="#fafaf8" stroke="#d4d4d0" stroke-width="2" stroke-dasharray="10 6"/>')
    f.text(lx0 + 20, ly0 + 40, 'Legend', 24, 500, INK, 'start')
    for i, (text, kind) in enumerate([('Instance', 'inst'), ('Vocabulary item (Q)', 'term'), ('External resource', 'ext'), ('Literal', 'lit'), ('Coordinate (WKT literal)', 'wkt')]):
        node(lx0 + 30, ly0 + 90 + i * 58, lw - 60, text, kind)
    for j, (t, d) in enumerate([('qualifier of the coordinate', False), ('reference of the coordinate', True)]):
        y = ly0 + 90 + (5 + j) * 58
        line(lx0 + 30, y, lx0 + 100, y, d); f.text(lx0 + 118, y + 8, t, 24, 400, INK, 'start', maxw=lw - 130)

    # ---- CM (bottom)
    frame(950, 1610); title(44, 970, 'CM', 'Coordinate Metadata')
    yc = 1110
    node(BX - 130, yc, 260, '@LAT/LON', 'wkt')
    edge(BX, rows[-1][0], BX, yc - NH / 2, pr('', 'P4'))
    r0 = 1190; pitch = 60
    line(BX, yc + NH / 2, BX, r0 + 6 * pitch, arrow=False)
    NW = 280; lxn, rxn = 40, 1700 - 40 - NW
    def cmrow(i, side, p, dashed):
        cy = r0 + i * pitch
        snak = (refs if dashed else quals)[p][0] if p in (refs if dashed else quals) else None
        text, kind = target(p, snak if (snak and wb_entity(p)['datatype'] == 'wikibase-item') else None)
        pre = 'r' if dashed else 'q'
        if side == 'L': node(lxn, cy, NW, text, kind); edge(BX, cy, lxn + NW, cy, pr(pre, p), dashed)
        else: node(rxn, cy, NW, text, kind); edge(BX, cy, rxn, cy, pr(pre, p), dashed)
    for i, p in enumerate(QL[:7]): cmrow(i, 'L', p, False)
    for i, p in enumerate(QL[7:]): cmrow(i, 'R', p, False)
    for k, p in enumerate(RL): cmrow(4 + k, 'R', p, True)
    f.done()

# ---------------------------------------------------------------- Fig. 10: spatial classes of ArNO and the Poseidon network schema
def fig10():
    """Redraw of ARNONetworkSchema: (A) the spatial part of the ArNO class hierarchy, (B) the spatial node types of the Poseidon HIN.
    Classes, labels, subclass edges, properties, domains and ranges are read from data/ArNO.ttl (archaeonatural-cloud/archaeonatural-ontology)
    and asserted. What the Poseidon data really contain follows poseidon2lod/py/Poseidon2LOD.py (geometry only at the Discovery Site)."""
    from rdflib import OWL
    g = Graph(); g.parse(os.path.join(HERE, 'data/ArNO.ttl'), format='turtle')
    AR, LADO, PL, CRM, GS, SFN = ('http://archaeonatural.cloud/ont/', 'http://archaeology.link/ontology#', 'http://pleiades.stoa.org/places/vocab#',
                                  'http://www.cidoc-crm.org/cidoc-crm/', 'http://www.opengis.net/ont/geosparql#', 'http://www.opengis.net/ont/sf#')
    def lab(iri):
        v = [str(l) for l in g.objects(URIRef(iri), RDFS.label) if l.language == 'en']
        assert v, iri
        return v[0].replace('disovery', 'discovery')      # ArNO.ttl spells "disovery" in the label of foundAtDiscoverySite
    def sub(c, p): assert (URIRef(c), RDFS.subClassOf, URIRef(p)) in g, (c, p)
    # tree: parent -> children (x centre, row)
    N = {  # key: (iri, x, row)
        'e1': (CRM + 'E1_CRM_Entity', 1045, 0), 'ppl': (PL + 'Place', 1045, 1), 'e53': (CRM + 'E53_Place', 640, 2), 'lplace': (LADO + 'Place', 1450, 2),
        'cty': (AR + 'Country', 1330, 3), 'plc': (AR + 'Place', 1580, 3), 'so': (GS + 'SpatialObject', 640, 3),
        'feat': (GS + 'Feature', 175, 4), 'geom': (GS + 'Geometry', 470, 4), 'ploc': (PL + 'Location', 1230, 4),
        'sfg': (SFN + 'Geometry', 470, 5), 'sfp': (SFN + 'Point', 470, 6),
        'lloc': (LADO + 'Location', 960, 5), 'ds': (AR + 'DiscoverySite', 1260, 5), 'site': (AR + 'Site', 1480, 5),
        'lds': (LADO + 'DiscoverySite', 690, 6), 'kiln': (LADO + 'KilnRegion', 960, 6), 'rep': (LADO + 'RepositoryLocation', 1290, 6), 'prod': (LADO + 'ProductionCentre', 960, 7)}
    TREE = {'e1': ['ppl'], 'ppl': ['e53', 'lplace'], 'lplace': ['cty', 'plc'], 'e53': ['so'], 'so': ['feat', 'geom', 'ploc'], 'geom': ['sfg'], 'sfg': ['sfp'],
            'ploc': ['lloc', 'ds', 'site'], 'lloc': ['lds', 'kiln', 'rep'], 'kiln': ['prod']}
    for p, cs in TREE.items():
        for c in cs: sub(N[c][0], N[p][0])
    ARNO_CLS = {'cty', 'plc', 'ds', 'site'}
    f = Fig('fig10_arno_spatial', 1690)
    def frame(y0, y1): f.o.append(f'<rect x="20" y="{y0}" width="1660" height="{y1 - y0}" rx="16" fill="none" stroke="#d4d4d0" stroke-width="3"/>')
    def title(x, y, tag, text):
        f.o.append(f'<rect x="{x}" y="{y}" width="40" height="40" rx="6" fill="#000"/>'); f.text(x + 20, y + 30, tag, 28, 500, '#fff'); f.text(x + 56, y + 30, text, 28, 500, INK, 'start')
    def node(cx, cy, text, fill, tc, red=False, dash=False, w=None):
        w = w or tw(text, MIN_TYPE) + 40
        f.box(cx - w / 2, cy - 22, w, 44, fill, [text], RED if red else '#000', 4 if red else 2, 22 if fill == CLS else 8, tc, dash=dash)
        return w
    def line(x1, y1, x2, y2, d=False, mk=True):
        da = ' stroke-dasharray="10 7"' if d else ''
        mk_ = ' marker-end="url(#a)"' if mk else ''
        f.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000" stroke-width="2.5"{da}{mk_}/>')
    def edge(x1, y1, x2, y2, label): line(x1, y1, x2, y2); f.chip((x1 + x2) / 2, (y1 + y2) / 2, label)
    # ---- A: class hierarchy
    frame(10, 840); title(44, 28, 'A', 'ArNO class hierarchy, spatial part')
    PITCH, Y0 = 92, 140
    cy = lambda r: Y0 + r * PITCH
    W_ = {}
    for k, (iri, x, r) in N.items():
        W_[k] = node(x, cy(r), lab(iri), CLS, '#fff', red=k in ARNO_CLS)
    for p, cs in TREE.items():
        px, pr = N[p][1], N[p][2]; pb = cy(pr) + 22; bus = pb + 18 + 22
        f.o.append(f'<path d="M{px - 13},{pb + 20} L{px + 13},{pb + 20} L{px},{pb} Z" fill="#fff" stroke="#000" stroke-width="2.5"/>')
        xs = [N[c][1] for c in cs] + [px]
        line(px, pb + 20, px, bus, mk=False)
        if len(cs) > 1 or cs[0] and N[cs[0]][1] != px: line(min(xs), bus, max(xs), bus, mk=False)
        for c in cs: line(N[c][1], bus, N[c][1], cy(N[c][2]) - 22, mk=False)
    # key
    kx, ky = 60, 110
    f.o.append(f'<rect x="{kx}" y="{ky}" width="470" height="230" rx="12" fill="#fafaf8" stroke="#d4d4d0" stroke-width="2" stroke-dasharray="10 6"/>')
    f.text(kx + 20, ky + 40, 'Key', 24, 500, INK, 'start')
    node(kx + 110, ky + 88, 'Class', CLS, '#fff', w=160)
    node(kx + 110, ky + 146, 'ArNO class', CLS, '#fff', red=True, w=160)
    f.o.append(f'<path d="M{kx + 40},{ky + 208} L{kx + 66},{ky + 208} L{kx + 53},{ky + 188} Z" fill="#fff" stroke="#000" stroke-width="2.5"/>'); f.text(kx + 90, ky + 206, 'is a subclass of', 24, 400, INK, 'start')
    f.text(kx + 220, ky + 96, 'class of an ontology', 24, 400, INK, 'start', maxw=240); f.text(kx + 220, ky + 154, 'defined in ArNO', 24, 400, INK, 'start', maxw=240)
    # ---- B: network schema
    frame(860, 1670); title(44, 878, 'B', 'Network schema of the Poseidon data, spatial part')
    for p, dom, rng in [('foundAtDiscoverySite', 'Sample', 'DiscoverySite'), ('atSite', 'DiscoverySite', 'Site'), ('atPlace', 'Site', 'Place'), ('inCountry', 'Place', 'Country')]:
        P = URIRef(AR + p); assert (P, RDFS.domain, URIRef(AR + dom)) in g and (P, RDFS.range, URIRef(AR + rng)) in g, p
    assert (URIRef(AR + 'aDNASample'), RDFS.subClassOf, URIRef(AR + 'BiologicalSample')) in g and (URIRef(AR + 'BiologicalSample'), RDFS.subClassOf, URIRef(AR + 'Sample')) in g
    assert (URIRef(AR + 'hasISOCode'), RDFS.domain, URIRef(AR + 'Country')) in g and (URIRef(AR + 'hasLabel'), RDFS.domain, None) in g
    assert (URIRef(GS + 'asWKT'), RDFS.domain, URIRef(GS + 'SpatialObject')) in g
    BX = 800; rows = [1010, 1150, 1290, 1430, 1570]
    chain = [(AR + 'aDNASample', None), (AR + 'DiscoverySite', 'foundAtDiscoverySite'), (AR + 'Site', 'atSite'), (AR + 'Place', 'atPlace'), (AR + 'Country', 'atPlace')]
    props = [None, AR + 'foundAtDiscoverySite', AR + 'atSite', AR + 'atPlace', AR + 'inCountry']
    wd_ = []
    for (iri, _), y in zip(chain, rows): wd_.append(node(BX, y, lab(iri), CLS, '#fff'))
    for i in range(1, 5): edge(BX, rows[i - 1] + 22, BX, rows[i] - 22, lab(props[i]))
    # labels (left) and ISO code (right)
    for i in range(1, 5):
        lw = node(300, rows[i], 'Label', '#fff', INK, w=130)
        edge(BX - wd_[i] / 2, rows[i], 300 + lw / 2, rows[i], lab(AR + 'hasLabel'))
    iw = node(1210, rows[4], 'ISO code', '#fff', INK, w=170)
    edge(BX + wd_[4] / 2, rows[4], 1210 - iw / 2, rows[4], lab(AR + 'hasISOCode'))
    # geometry of the Discovery Site (poseidon2lod: geo:hasGeometry -> sf:Point -> geo:asWKT)
    pw = node(1210, rows[1], lab(SFN + 'Point'), CLS, '#fff')
    edge(BX + wd_[1] / 2, rows[1], 1210 - pw / 2, rows[1], lab(GS + 'hasGeometry'))
    ww = node(1560, rows[1], 'WKT literal', '#fff', INK)
    edge(1210 + pw / 2, rows[1], 1560 - ww / 2, rows[1], lab(GS + 'asWKT'))
    f.done()

# ---------------------------------------------------------------- Fig. 5: spatial model of BB-5KBC
def fig5():
    """Redraw of bb-5kbc-ontology.jpg with a spatial focus: (A) the classes and properties around the place of a findspot, (B) one findspot as an instance.
    Everything is read from data/bb5kbc-bundle.ttl (Research-Squirrel-Engineers/bb-5kbc-public, rdf/bb5kbc-bundle.ttl): labels, CRM super classes,
    the properties that the 540 findspots and their georeferencing activities really use, and the values of the example findspot."""
    from rdflib import OWL, Literal
    from rdflib.namespace import RDF as RDFNS
    g = Graph(); g.parse(os.path.join(HERE, 'data/bb5kbc-bundle.ttl'), format='turtle')
    B, D, FSL, CRM, GEO, SFN = ('http://w3id.org/bb5kbc/ont/', 'http://w3id.org/bb5kbc/', 'http://fuzzy-sl.squirrel.link/ontology/', 'http://www.cidoc-crm.org/cidoc-crm/',
                                'http://www.opengis.net/ont/geosparql#', 'http://www.opengis.net/ont/sf#')
    U = URIRef
    def lab(iri, lang=None):
        ls = [l for l in g.objects(U(iri), RDFS.label)]
        pick = [l for l in ls if l.language == 'en'] or ls
        return str(pick[0]).split(' / ')[0]
    def types(x): return {str(t) for t in g.objects(x, RDFNS.type)}
    # ---- what the data really use
    F = [s_ for s_ in g.subjects(RDFNS.type, U(B + 'Fundstelle'))]; assert len(F) == 540
    ACT = [s_ for s_ in g.subjects(RDFNS.type, U(B + 'GeoreferenzierungsAktivitaet'))]; assert len(ACT) == 540
    def used(subjects, pred): return all((s_, U(pred), None) in g for s_ in subjects)
    for p in ('inGemeinde', 'wurdeGeoreferenziertDurch'): assert used(F, B + p), p
    for p in ('hasGeometry',): assert used(F, GEO + p)
    for p in ('representativeGeometry', 'certaintyLevel', 'hasLocationType'): assert used(F, FSL + p), p
    for p in ('activityDesc', 'methodUsed', 'hasSourceType', 'hasSourceTypeDetail', 'georeferencingBy', 'hasReference'): assert used(ACT, FSL + p), p
    CH = [('Gemeinde', 'inKreis', 'Kreis'), ('Kreis', 'inBundesland', 'Bundesland'), ('Bundesland', 'inLand', 'Land')]
    assert any((s_, U(B + 'hasExternalIdentifier'), None) in g for s_ in g.subjects(RDFNS.type, U(B + 'Gemeinde')))
    for a, p, b in CH:
        assert (U(B + p), RDFS.domain, U(B + a)) in g and (U(B + p), RDFS.range, U(B + b)) in g, p
    assert (U(B + 'inGemeinde'), RDFS.domain, U(B + 'Fundstelle')) in g and (U(B + 'inGemeinde'), RDFS.range, U(B + 'Gemeinde')) in g
    for c in ('Gemeinde', 'Kreis', 'Bundesland', 'Land'): assert (U(B + c), RDFS.subClassOf, U(CRM + 'E53_Place')) in g
    assert (U(B + 'Fundstelle'), RDFS.subClassOf, U(CRM + 'E27_Site')) in g and (U(SFN + 'Point'), RDFS.subClassOf, U(GEO + 'Geometry')) in g
    assert (U(B + 'GeoreferenzierungsAktivitaet'), RDFS.subClassOf, U(CRM + 'E13_Attribute_Assignment')) in g
    EN = {'Fundstelle': 'findspot', 'Gemeinde': 'municipality', 'Kreis': 'district', 'Bundesland': 'state', 'Land': 'country', 'GeoreferenzierungsAktivitaet': 'georeferencing activity'}
    def dt(prop):                                        # range of a data property; if the ontology gives none, the datatype of the literals in the data
        r = list(g.objects(U(prop), RDFS.range))
        if r: return str(r[0]).split('#')[-1]
        lit = next(o for o in g.objects(None, U(prop)) if isinstance(o, Literal))
        return str(lit.datatype).split('#')[-1] if lit.datatype else 'string'
    f = Fig('fig5_bb5kbc_spatial', 1900)
    def frame(y0, y1): f.o.append(f'<rect x="20" y="{y0}" width="1660" height="{y1 - y0}" rx="16" fill="none" stroke="#d4d4d0" stroke-width="3"/>')
    def title(x, y, tag, text):
        f.o.append(f'<rect x="{x}" y="{y}" width="40" height="40" rx="6" fill="#000"/>'); f.text(x + 20, y + 30, tag, 28, 500, '#fff'); f.text(x + 56, y + 30, text, 28, 500, INK, 'start')
    def line(x1, y1, x2, y2, mk=True):
        f.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000" stroke-width="2.5"{" marker-end=" + chr(34) + "url(#a)" + chr(34) if mk else ""}/>')
    def uml(cx, y, w, head, body):
        hh = 28 + 31 * len(head); bh = 20 + 31 * len(body) if body else 0
        f.o.append(f'<rect x="{cx - w / 2}" y="{y}" width="{w}" height="{hh}" rx="10" fill="{CLS}" stroke="#000" stroke-width="2"/>')
        for i, t in enumerate(head): f.text(cx, y + 38 + 31 * i, t, MIN_TYPE, 500 if i == 0 else 400, '#fff', maxw=w - 20)
        if body:
            f.o.append(f'<rect x="{cx - w / 2}" y="{y + hh}" width="{w}" height="{bh}" fill="#fff" stroke="#000" stroke-width="2"/>')
            for i, t in enumerate(body): f.text(cx - w / 2 + 16, y + hh + 34 + 31 * i, t, MIN_TYPE, 400, INK, 'start', maxw=w - 30)
        return hh + bh
    # ---- A
    title(44, 28, 'A', 'Spatial classes of the BB-5KBC ontology')
    fcx, w3 = 850, 460
    cx1, cx2, cx3 = 270, 850, 1430
    f_body = ['hatFID : ' + dt(B + 'hatFID'), 'hatFundstellenID : ' + dt(B + 'hatFundstellenID'), 'hatGenauigkeit : ' + dt(B + 'hatGenauigkeit'), 'hatKatalognummer : ' + dt(B + 'hatKatalognummer'),
              'fsl:certaintyLevel : CertaintyType', 'fsl:hasLocationType : LocationType', 'fsl:representativeGeometry : Point']
    fh = uml(fcx, 90, w3, ['Fundstelle', f"{EN['Fundstelle']} · crm:E27_Site"], f_body)
    ybus, ytop = 90 + fh + 60, 90 + fh + 170
    line(fcx, 90 + fh, fcx, ybus, mk=False); line(cx1, ybus, cx3, ybus, mk=False)
    def drop(cx, label):
        line(cx, ybus, cx, ytop); f.chip(cx, (ybus + ytop) / 2, label)
    drop(cx1, 'inGemeinde'); drop(cx2, 'geo:hasGeometry'); drop(cx3, 'wurdeGeoreferenziertDurch')
    # administrative chain
    y = ytop
    names = ['Gemeinde', 'Kreis', 'Bundesland', 'Land']
    for i, n in enumerate(names):
        h = uml(cx1, y, w3, [n, f"{EN[n]} · crm:E53_Place"], ['hasExternalIdentifier : URI'] if n == 'Gemeinde' else None)
        if i < 3:
            y2 = y + h + 90; line(cx1, y + h, cx1, y2); f.chip(cx1, (y + h + y2) / 2, CH[i][1]); y = y2
    # geometry
    gh = uml(cx2, ytop, w3, ['Point', 'sf:Point · geo:Geometry'], ['geo:asWKT : ' + dt(GEO + 'asWKT'), 'fsl:hasPointType : PointType'])
    # georeferencing activity
    a_body = ['fsl:activityDesc : ' + dt(FSL + 'activityDesc'), 'fsl:methodUsed : MethodType', 'fsl:hasSourceType : SourceType', 'fsl:hasSourceTypeDetail : SourceType',
              'fsl:georeferencingBy : Person', 'fsl:hasReference : URI, string']
    uml(cx3, ytop, w3, ['GeoreferenzierungsAktivitaet', EN['GeoreferenzierungsAktivitaet'], 'crm:E13_Attribute_Assignment'], a_body)
    yA = y + h + 30
    frame(10, yA)
    kx, ky = 620, ytop + 260
    f.o.append(f'<rect x="{kx}" y="{ky}" width="460" height="190" rx="12" fill="#fafaf8" stroke="#d4d4d0" stroke-width="2" stroke-dasharray="10 6"/>')
    f.text(kx + 20, ky + 38, 'Key', 24, 500, INK, 'start')
    f.box(kx + 30, ky + 56, 150, 44, CLS, ['Class'], '#000', 2, 10, '#fff')
    f.text(kx + 200, ky + 86, 'ontology class', 24, 400, INK, 'start')
    f.box(kx + 30, ky + 118, 150, 44, '#fff', ['name : type'], '#000', 2, 4, INK)
    f.text(kx + 200, ky + 148, 'attribute', 24, 400, INK, 'start')
    # ---- B
    y0 = yA + 20; title(44, y0 + 18, 'B', 'One findspot: Seelow 20')
    site = [s_ for s_ in F if str(g.value(s_, RDFS.label)) == 'Seelow 20']; assert len(site) == 1
    S = site[0]; sid = str(S).replace(D, '')
    L = lambda x: str(g.value(x, RDFS.label))
    geom = g.value(S, U(GEO + 'hasGeometry')); wkt = str(g.value(geom, U(GEO + 'asWKT')))
    m = re.match(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\)', wkt); lon, lat = float(m.group(1)), float(m.group(2))
    act = g.value(S, U(B + 'wurdeGeoreferenziertDurch'))
    prec = g.value(S, U(B + 'hatGenauigkeit'))  # the bundle still stores 0.0; the published value (coordinates rounded to 2 decimals, up to 1000 m) is set by hand, as is the planned precision of 0.01 degrees
    assert float(prec) == 0.0
    rows = [('geo:hasGeometry', f'POINT({m.group(1)} {m.group(2)})', 'lit'), ('hatGenauigkeit', '\u00b1 1000 m', 'lit'), ('precision', '\u00b1 0.01\u00b0', 'lit'),
            ('fsl:certaintyLevel', L(g.value(S, U(FSL + 'certaintyLevel'))), 'term'), ('fsl:hasLocationType', L(g.value(S, U(FSL + 'hasLocationType'))), 'term'),
            ('inGemeinde', L(g.value(S, U(B + 'inGemeinde'))), 'inst'), ('wurdeGeoreferenziertDurch', L(act), 'inst')]
    # map of the 540 findspots
    mx, my, mw = 100, y0 + 100, 620
    X, Y, mh = basemap(f, mx, my, mw, 10, 22, 49.5, 55, 52.3, 'bb', 1.0, grid=(2, 1), labels=True, detail=(5, True))
    f.o.append('<g clip-path="url(#bb)">')
    for lo_, la_, _l in pts('bb5kbc'): f.o.append(f'<circle cx="{X(lo_):.1f}" cy="{Y(la_):.1f}" r="3.4" fill="{CLS}" fill-opacity="0.85" stroke="#fff" stroke-width="0.8"/>')
    f.o.append('</g>')
    f.o.append(f'<circle cx="{X(lon):.1f}" cy="{Y(lat):.1f}" r="17" fill="none" stroke="{RED}" stroke-width="4"/>')
    # instance card
    BX, ix = 1000, 780
    n = len(rows); pitch = 74; top = my + (mh - (n - 1) * pitch) / 2; cyc = top + (n - 1) * pitch / 2
    f.box(ix, cyc - 50, 190, 100, INST, [L(S), sid])
    ys = [top + i * pitch for i in range(n)]
    line(ix + 190, cyc, BX, cyc, mk=False); line(BX, ys[0], BX, ys[-1], mk=False)
    vx, vw = 1370, 300
    FILLS = {'lit': ('#fff', INK), 'term': (TERM, '#fff'), 'inst': (INST, INK)}
    for (p, v, k), yy in zip(rows, ys):
        line(BX, yy, vx, yy); f.chip((BX + vx) / 2, yy, p)
        fl, tc = FILLS[k]
        vl = wrap(v, vw - 34); hb = 50 if len(vl) == 1 else 20 + 31 * len(vl)
        f.box(vx, yy - hb / 2, vw, hb, fl, vl, '#000', 2, 22 if k == 'term' else 8, tc)
    yB = int(my + mh + 75); frame(y0, yB); f.h = int(yB + 20)
    f.done()

def fig9():
    """1:1 redraw of ARNO.png (thor Straten et al.): hexagon with the CIDOC CRM core and six surrounding concept domains. No content added or changed; only type and colours follow the common style."""
    import math
    f = Fig('fig9_arno_modules', 1670)
    BLUE = '#2f5597'
    cx, cy, R, r = 850, 780, 770, 250
    ap = R * math.cos(math.radians(30))
    def V(rad, deg): return (cx + rad * math.cos(math.radians(deg)), cy - rad * math.sin(math.radians(deg)))
    ang = [0, 60, 120, 180, 240, 300]
    outer = [V(R, a) for a in ang]; inner = [V(r, a) for a in ang]
    pts_ = lambda P: ' '.join(f'{x:.1f},{y:.1f}' for x, y in P)
    PAST, NAVY = ['#dce6f5', '#b9cbe8'], '#1f3a6b'      # six outer sectors in alternating pastel blues, dark blue core
    for i in range(6):
        q = [outer[i], outer[(i + 1) % 6], inner[(i + 1) % 6], inner[i]]
        f.o.append(f'<polygon points="{pts_(q)}" fill="{PAST[i % 2]}" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>')
    f.o.append(f'<polygon points="{pts_(inner)}" fill="{NAVY}" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>')
    f.text(cx, cy - 66, 'Cultural', 52, 700, '#fff', maxw=2 * r - 160)
    f.text(cx, cy + 12, 'CIDOC', 40, 400, '#fff'); f.text(cx, cy + 60, 'CRM', 40, 400, '#fff')
    f.text(cx, cy + 136, 'Heritage', 52, 700, '#fff', maxw=2 * r - 160)
    d = ap + 78
    def lab(deg, rot, lines):
        x, y = V(d, deg); n = len(lines)
        for i, t in enumerate(lines):
            f.text(0, 0, t, 52, 700, BLUE, maxw=700)
            f.o.pop()
            off = (i - (n - 1) / 2) * 64
            f.o.append(f'<text transform="translate({x:.1f},{y:.1f}) rotate({rot}) translate(0,{off + 18:.1f})" font-family="Fira Sans" font-size="52" font-weight="700" fill="{BLUE}" text-anchor="middle">{esc(t)}</text>')
    lab(90, 0, ['Agents']); lab(30, 60, ['Bibliography']); lab(330, -60, ['Space'])
    lab(270, 0, ['Application Domain', '(Biology)']); lab(210, 60, ['Time']); lab(150, -60, ['Provenance'])
    k = 2.655                                           # positions of the ontology names measured in the original (580 px hexagon width)
    for t, x, y in [('FOAF', 362, 165), ('CRMdig', 218, 226), ('PROV-O', 176, 296), ('dcterms', 493, 233), ('BIBO', 524, 286), ('OWL-TIME', 199, 392),
                    ('EDTF', 228, 460), ('GeoSPARQL', 524, 396), ('Pleiades', 508, 471), ('UBERON', 361, 485), ('GSSO', 301, 555), ('PATO', 427, 555)]:
        f.text(cx + (x - 362) * k, cy + (y - 343) * k + 15, t, 56, 700, '#1b2f55', maxw=330)
    f.done()

def fig2():
    """Fig. 2 re-arranged and redrawn: one frame per location of the Ogham stone CIIC 81 (present location in the museum, findspot at Garranes); per frame the
    evidence (photo, historical map, OpenStreetMap) and the coordinate statement of the stone in Wikidata and in the fuzzy-sl Wikibase as mini graphs.
    The statements are read from data/wd/Q130529871.json (+ labels_ciic81.json) and data/wb/Q74.json."""
    import base64, io
    from PIL import Image
    D = os.path.join(HERE, 'data/ogham')
    def load(n): return Image.open(os.path.join(D, n + '.png')).convert('RGB')
    f = Fig('fig2_ogham_ciic81', 2000)
    def frame(y0, y1): f.o.append(f'<rect x="20" y="{y0}" width="1660" height="{y1 - y0}" rx="16" fill="none" stroke="#d4d4d0" stroke-width="3"/>')
    def title(x, y, tag, text):
        f.o.append(f'<rect x="{x}" y="{y}" width="40" height="40" rx="6" fill="#000"/>'); f.text(x + 20, y + 30, tag, 28, 500, '#fff'); f.text(x + 56, y + 30, text, 28, 500, INK, 'start')
    def put(im, x, y, w, letter):
        h = round(im.height * w / im.width); b = io.BytesIO(); im.resize((w * 2, h * 2), Image.LANCZOS).save(b, 'PNG', optimize=True)
        f.o.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}"/>')
        f.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#b9b9b3" stroke-width="2"/>')
        f.o.append(f'<rect x="{x + 8}" y="{y + 8}" width="44" height="44" rx="7" fill="#000" stroke="#fff" stroke-width="3"/>'); f.text(x + 30, y + 41, letter, 28, 500, '#fff')
        return h
    FILL = {'item': (INST, INK, False), 'term': (TERM, '#fff', False), 'lit': ('#fff', INK, False), 'url': ('#fff', INK, True)}
    def stmt(x, y, w, vw, stone, prop, coord, rows):
        """stone --prop--> coordinate; qualifier rows hang off the coordinate: (chip, value, kind, highlighted, reference)"""
        f.box(x, y, 250, 54, INST, [stone], '#000', 2, 14, INK)
        y1 = y + 54 + 48; line = lambda *a, **k: None
        f.arrow(x + 125, y + 54, x + 125, y1); f.chip(x + 125, (y + 54 + y1) / 2, prop)
        f.box(x, y1, 420, 54, '#000', [coord], '#000', 2, 14, '#fff')
        bx, vx = x + 24, x + w - vw; yy = y1 + 54 + 26; ys = []
        for chip, val, kind, hl, ref in rows:
            vl = val if isinstance(val, list) else wrap(val, vw - 34); hb = 46 if len(vl) == 1 else 18 + 31 * len(vl); hb = max(hb, 68) if tw(chip, 24) + 28 > 340 else hb; cy = yy + hb / 2; ys.append(cy)
            fl, tc, dash = FILL[kind]
            da = ' stroke-dasharray="10 6"' if ref else ''
            f.o.append(f'<line x1="{bx}" y1="{cy:.1f}" x2="{vx}" y2="{cy:.1f}" stroke="#000" stroke-width="2.5"{da} marker-end="url(#a)"/>')
            if tw(chip, 24) + 28 > 340:                                   # long property label: two-line chip
                l1, l2 = chip.split(' or ', 1); l2 = 'or ' + l2; cw = max(tw(l1, 24), tw(l2, 24)) + 28; cxm = (bx + vx) / 2
                f.o.append(f'<rect x="{cxm - cw / 2:.1f}" y="{cy - 34:.1f}" width="{cw:.1f}" height="68" rx="26" fill="{AMB}" stroke="#000" stroke-width="1.5"/>')
                f.text(cxm, cy - 6, l1, 24); f.text(cxm, cy + 25, l2, 24)
            else: f.chip((bx + vx) / 2, cy, chip)
            f.box(vx, cy - hb / 2, vw, hb, fl, vl, '#000', 2, 22 if kind == 'term' else 8, tc, dash=dash)
            if hl: f.o.append(f'<rect x="{vx - 8}" y="{cy - hb / 2 - 8:.1f}" width="{vw + 16}" height="{hb + 16}" rx="12" fill="none" stroke="{RED}" stroke-width="5"/>')
            yy += max(hb + 8, 54)
        f.o.append(f'<line x1="{bx}" y1="{y1 + 54}" x2="{bx}" y2="{ys[-1]:.1f}" stroke="#000" stroke-width="2.5"/>')
        return yy
    # ---- data: Wikidata item Q130529871 (physical stone) and fuzzy-sl Wikibase item Q74; every row is read from the JSON copies
    WDQ, FSQ = 'Q130529871', 'Q74'
    WL = json.load(open(os.path.join(HERE, 'data/wd/labels_ciic81.json'), encoding='utf8'))
    wd = json.load(open(os.path.join(HERE, f'data/wd/{WDQ}.json'), encoding='utf8')); fs = wb_entity(FSQ)
    def dms(v, pos, neg):
        a_ = abs(v); d_ = int(a_); m_ = int((a_ - d_) * 60); s_ = ((a_ - d_) * 60 - m_) * 60
        return f"{d_}\u00b0{m_}'{s_:.2f}\"{pos if v >= 0 else neg}"
    def coord_text(lat, lon): return dms(lat, 'N', 'S') + ', ' + dms(lon, 'E', 'W')
    def fix(t):                                                   # visible correction of typos in the source data (reported to the data owner)
        return t.replace('servey', 'survey').replace('exhebition', 'exhibition')
    def urllines(u):
        assert u.startswith('https://'); h, r = u[8:].split('/', 1); return ['https://', h + '/', r]
    WD_HL, FS_HL = {'P276', 'P459'}, {'P5', 'P7', 'P23', 'P24'}
    def wd_rows(c):
        rows = []
        for p, ss in c['qualifiers'].items():
            for sn in ss:
                v = sn['datavalue']['value']; assert v['id'] in WL
                rows.append((WL[p], WL[v['id']], 'item', p in WD_HL, False))
        for r in c['references']:
            for p, ss in r['snaks'].items():
                for sn in ss:
                    v = sn['datavalue']['value']; assert isinstance(v, str)
                    rows.append((WL[p], urllines(v) if v.startswith('http') else v, 'url' if v.startswith('http') else 'lit', False, True))
        return rows
    def fs_rows(c):
        rows = []; assert not c.get('references')
        for p, ss in c['qualifiers'].items():
            lab = wb_label(p)
            for sn in ss:
                v = sn['datavalue']['value']
                if isinstance(v, dict) and 'id' in v: rows.append((lab, wb_label(v['id']), 'item' if p == 'P14' else 'term', p in FS_HL, False))
                else:
                    t = fix(v).replace('`', "'")
                    if len(t) > 120: k = t.index('the stone was found in') + len('the stone was found in'); t = t[:k] + ' [\u2026]'
                    rows.append((lab, t, 'lit', p in FS_HL, False))
        return rows
    WDc = {(round(c['mainsnak']['datavalue']['value']['latitude'], 4)): c for c in wd['claims']['P625']}
    FSc = {(round(c['mainsnak']['datavalue']['value']['latitude'], 4)): c for c in fs['claims']['P4']}
    K1, K2 = 51.8937, round(51.81655, 4); assert set(WDc) == set(FSc) == {K1, K2}
    def cv(c): v = c['mainsnak']['datavalue']['value']; return coord_text(v['latitude'], v['longitude'])
    assert [round(c['mainsnak']['datavalue']['value']['longitude'], 6) for c in (WDc[K1], FSc[K1])] == [-8.492443] * 2
    xw, ww, xf, wf = 40, 640, 760, 900
    def heads(y):
        for x, w, t in ((xw, ww, 'Wikidata'), (xf, wf, 'fuzzy-sl Wikibase')): f.text(x + 300, y, t, 28, 500, INK)
    # ---- frame 1: present location
    y0 = 10; title(44, y0 + 18, '1', 'Present location: exhibition, University College Cork'); heads(y0 + 90); yi = y0 + 106
    kx = 1000                                              # key in the title line
    f.o.append(f'<rect x="{kx}" y="{y0 + 20}" width="44" height="34" rx="8" fill="none" stroke="{RED}" stroke-width="5"/>')
    f.text(kx + 58, y0 + 46, 'location and reliability', 24, 400, INK, 'start')
    f.o.append(f'<line x1="{kx + 360}" y1="{y0 + 37}" x2="{kx + 410}" y2="{y0 + 37}" stroke="#000" stroke-width="2.5" stroke-dasharray="10 6" marker-end="url(#a)"/>')
    f.text(kx + 424, y0 + 46, 'reference', 24, 400, INK, 'start')
    ya = stmt(xw, yi, ww, 230, WDQ, WL['P625'], cv(WDc[K1]), wd_rows(WDc[K1]))
    yb_ = stmt(xf, yi, wf, 380, FSQ, wb_label('P4'), cv(FSc[K1]), fs_rows(FSc[K1]))
    hp = put(load('B'), xw, ya + 10, 400, 'A')
    yE = max(ya + 10 + hp, yb_) + 10; frame(y0, yE)
    # ---- frame 2: findspot
    y0 = yE + 20; title(44, y0 + 18, '2', 'Findspot: Garranes, Co. Cork'); heads(y0 + 90); yi = y0 + 106
    ya = stmt(xw, yi, ww, 230, WDQ, WL['P625'], cv(WDc[K2]), wd_rows(WDc[K2]))
    yb_ = stmt(xf, yi, wf, 380, FSQ, wb_label('P4'), cv(FSc[K2]), fs_rows(FSc[K2]))
    Dm = load('D'); free = max(yb_ - ya - 10, 200); wD = 400; hD = round(free); Dm = Dm.crop((0, 230, Dm.width, 230 + min(Dm.height - 230, round(Dm.width * hD / wD))))
    hp = put(Dm, xw, ya + 10, wD, 'B')
    yE = max(ya + 10 + hp, yb_) + 10; frame(y0, yE)
    f.h = int(yE + 20)
    f.done()

if __name__ == '__main__':
    want = sys.argv[1:] or ['fig4']
    if 'fig4' in want: fig4()
    if 'fig3' in want: fig3()
    if 'fig5' in want: fig5()
    if 'fig9' in want: fig9()
    if 'fig2' in want: fig2()
    if 'fig10' in want: fig10()
    if 'z3' in want: z3()
    if 'z2' in want: z2()
    if 'fig7' in want: fig7()
    if 'fig6' in want: fig6()
    try:                                                 # keep the gallery (docs/derse26_geographs/index.html) in step with out/
        import build_gallery
    except ImportError as e: print('gallery not rebuilt:', e)
