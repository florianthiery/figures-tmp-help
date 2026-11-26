"""figs.py: figures for the MOSAIC Winter School 2026 (Kiel, 4 Dec 2026), Part I and Part II.

House style of the figures-tmp-help repository (STYLE.md of deRSE26/figures): Fira Sans, flat colours, no title and no footer in the
image, edge labels as amber chips centred on the arrow. Differences for slides: canvas 2400 x 900 px, type 40 px and more, transparent
background, highlight in MOSAIC amethyst (#9454AC). Everything a graph states is read from data/; nothing of it is typed by hand.

Run (Windows cmd, one line):
  cd /d C:\\git\\figures-tmp-help\\mosaic2026\\figures && pip install resvg_py pillow && python figs.py g06
Output: out/<name>.svg and out/<name>.png
"""
import json, math, os, re, sys
import resvg_py
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F4, F5, F7 = (os.path.join(HERE, 'fonts/FiraSans-%d.ttf' % n) for n in (400, 500, 700))
W, H = 2400, 900
MIN_TYPE = 40
INST, CLS, TERM, AMB = '#e2e8f0', '#9a3412', '#4c1d95', '#fbbf24'
INK, HL = '#1f1f1d', '#9454AC'

_fonts = {}
def tw(s, size, w=400):
    k = (size, w)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype({500: F5, 700: F7}.get(w, F4), size, layout_engine=ImageFont.Layout.BASIC)
    return _fonts[k].getlength(s)
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')

class Fig:
    def __init__(s, name, h=H):
        s.name, s.h, s.o = name, h, []
    def text(s, x, y, t, size=MIN_TYPE, w=400, fill=INK, anchor='middle', maxw=None):
        if size < MIN_TYPE: raise ValueError(f'{s.name}: type {size} px < {MIN_TYPE}: {t}')
        if maxw and tw(t, size, w) > maxw: raise ValueError(f'{s.name}: overflow {tw(t, size, w):.0f}>{maxw}: {t}')
        s.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Fira Sans" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{esc(t)}</text>')
    def box(s, cx, cy, w, h, fill, lines, stroke='#000', sw=2.5, r=18, tc=INK, dash=False, size=MIN_TYPE):
        da = ' stroke-dasharray="12 8"' if dash else ''
        s.o.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
        n = len(lines); gap = size * 1.25; y0 = cy - (n - 1) * gap / 2 + size * 0.34
        for i, l in enumerate(lines): s.text(cx, y0 + i * gap, l, size, 500 if i == 0 and n > 1 else 400, tc, maxw=w - 28)
    def chip(s, cx, cy, t):
        w = tw(t, MIN_TYPE) + 36
        s.o.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - 29:.1f}" width="{w:.1f}" height="58" rx="29" fill="{AMB}" stroke="#000" stroke-width="2"/>')
        s.text(cx, cy + MIN_TYPE * 0.34, t)
    def edge(s, a, b, label):
        """Arrow from box a to box b (cx, cy, w, h), label as amber chip on the middle of the visible arrow."""
        p1, p2 = border(a, b), border(b, a)
        s.o.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#000" stroke-width="3" marker-end="url(#a)"/>')
        if label: s.chip((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, label)
    def line(s, x1, y1, x2, y2, dash=True):
        da = ' stroke-dasharray="12 8"' if dash else ''
        s.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000" stroke-width="3"{da}/>')
    def table(s, x, y, colw, rows, rowh=92, hdr='#e2e8f0'):
        """Plain table, first row is the header; x, y = top left. Returns (cx, cy, w, h) of the whole table."""
        for i, r in enumerate(rows):
            cx = x
            for w, t in zip(colw, r):
                s.o.append(f'<rect x="{cx:.1f}" y="{y + i * rowh:.1f}" width="{w}" height="{rowh}" fill="{hdr if i == 0 else "#fff"}" stroke="#000" stroke-width="2.5"/>')
                s.text(cx + w / 2, y + i * rowh + rowh / 2 + MIN_TYPE * 0.34, t, MIN_TYPE, 500 if i == 0 else 400, maxw=w - 24)
                cx += w
        return (x + sum(colw) / 2, y + len(rows) * rowh / 2, sum(colw), len(rows) * rowh)
    def done(s):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{s.h}" viewBox="0 0 {W} {s.h}">'
               '<defs><marker id="a" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="24" refX="22" refY="12" orient="auto">'
               '<path d="M0,0 L24,12 L0,24 z" fill="#000"/></marker></defs>' + '\n'.join(s.o) + '</svg>')
        os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
        open(os.path.join(HERE, f'out/{s.name}.svg'), 'w', encoding='utf8').write(svg)
        open(os.path.join(HERE, f'out/{s.name}.png'), 'wb').write(bytes(resvg_py.svg_to_bytes(svg_string=svg, font_files=[F4, F5, F7], skip_system_fonts=True, zoom=1.0)))
        print('wrote', s.name, f'{W}x{s.h}')

def border(a, b):
    """Point where the line from the centre of a to the centre of b leaves the rectangle of a."""
    (x, y, w, h), (x2, y2, _, _) = a, b
    dx, dy = x2 - x, y2 - y
    t = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
    return x + dx * t, y + dy * t

def wd_item(q): return json.load(open(os.path.join(HERE, f'data/wd/{q}.json'), encoding='utf8'))
LAB = json.load(open(os.path.join(HERE, 'data/wd/labels_ciic81.json'), encoding='utf8'))
def claim_ids(item, p): return [c['mainsnak']['datavalue']['value']['id'] for c in item['claims'].get(p, [])]
def claim_str(item, p): return [c['mainsnak']['datavalue']['value'] for c in item['claims'].get(p, [])]

def dms(v, pos, neg):
    return f"{abs(v):.3f}\u00b0{pos if v >= 0 else neg}"

def g06():
    """G06: the Ogham stone CIIC 81 as a graph (Part I, step 4). One node, its class, a place, a coordinate and three external identifiers."""
    q = 'Q130529871'; it = wd_item(q)
    cls = LAB['Q2016147']                                       # instance of: ogham stone
    assert 'Q2016147' in claim_ids(it, 'P31')
    loc = LAB[claim_ids(it, 'P276')[0]]                         # location
    find = LAB[claim_ids(it, 'P189')[0]].replace(' (Ogham Site)', '')   # location of discovery
    osm = claim_str(it, 'P11693')[0]; fg = claim_str(it, 'P8168')[0]
    lod = claim_str(it, 'P2888')[0].rsplit('/', 1)[-1]
    c = it['claims']['P625'][0]['mainsnak']['datavalue']['value']
    coord = dms(c['latitude'], 'N', 'S') + ' ' + dms(c['longitude'], 'E', 'W')
    f = Fig('g06_ciic81_graph')
    S = (1200, 450, 400, 130)
    s_ = (S[0], S[1], S[2], S[3])
    nodes = {
        'cls': (270, 130, 440, 96), 'find': (270, 450, 440, 96), 'xy': (270, 770, 480, 96),
        'loc': (2130, 130, 480, 96), 'osm': (2130, 330, 480, 130), 'lod': (2130, 570, 480, 130), 'fg': (2130, 770, 480, 130)}
    f.box(*nodes['cls'], CLS, [cls], tc='#fff')
    f.box(*nodes['find'], INST, [find])
    f.box(*nodes['xy'], '#1f1f1d', [coord], tc='#fff')
    f.box(*nodes['loc'], INST, [loc])
    f.box(*nodes['osm'], '#fff', ['OpenStreetMap', 'node ' + osm], dash=True)
    f.box(*nodes['lod'], '#fff', ['lod.ogham.link', lod], dash=True)
    f.box(*nodes['fg'], '#fff', ['FactGrid', fg], dash=True)
    f.box(*s_, INST, ['CIIC 81', q], stroke=HL, sw=8)
    for k, lab in [('cls', 'instance of'), ('find', 'location of discovery'), ('xy', 'coordinate location'), ('loc', 'location'),
                   ('osm', 'OSM node ID'), ('lod', 'exact match'), ('fg', 'FactGrid item ID')]:
        f.edge(s_, nodes[k], lab)
    f.done()

STONE = 'Q130529871'
def stone_label(item):
    return item['labels']['en']['value'].replace('Ogham Stone ', '').split(' / ')[0]

def g05():
    """G05: the triple (Part I, step 4). Three statements about one subject: object is a class, a plain value, a value with language tag."""
    it = wd_item(STONE)
    assert 'Q2016147' in claim_ids(it, 'P31')
    inv = claim_str(it, 'P217')[0]; lab = it['labels']['en']['value']
    f = Fig('g05_triple')
    for x, t in [(330, 'Subject'), (1150, 'Predicate'), (1960, 'Object')]: f.text(x, 80, t, MIN_TYPE, 500, fill='#55544f')
    rows = [(260, 'instance of', ('box', CLS, ['ogham stone'], '#fff', False)),
            (480, 'inventory number', ('box', '#fff', [inv], INK, False)),
            (700, 'label', ('box', '#fff', ['\u201c' + lab + '\u201d@en'], INK, False))]
    S = lambda y: (330, y, 440, 110)
    for y, pred, (_, fill, lines, tc, dash) in rows:
        o = (1960 if pred == 'label' else 1700 + (440 if pred == 'instance of' else 220) / 2, y, 840 if pred == 'label' else (440 if pred == 'instance of' else 220), 110)
        f.box(*S(y), INST, ['CIIC 81'])
        f.box(*o, fill, lines, tc=tc, dash=dash)
        f.edge(S(y), o, pred)
    f.done()

def g04():
    """G04: one table row becomes a graph (Part I, step 3 to 4)."""
    it = wd_item(STONE)
    cls = LAB['Q2016147']; find = LAB[claim_ids(it, 'P189')[0]].replace(' (Ogham Site)', '')
    f = Fig('g04_row_to_graph')
    t = f.table(40, 405, [240, 300, 240], [['Stone', 'Class', 'Place'], ['CIIC 81', cls, find]])
    f.edge((900, 450, 80, 10), (1100, 450, 80, 10), None)
    S = (1250, 450, 260, 110)
    c = (2030, 200, 440, 100); p = (2030, 700, 440, 100)
    f.box(*c, CLS, [cls], tc='#fff'); f.box(*p, INST, [find]); f.box(*S, INST, ['CIIC 81'])
    f.edge(S, c, 'instance of'); f.edge(S, p, 'location of discovery')
    f.done()

def g02():
    """G02: one stone, three tables (Part I, step 3): the same stone has three identifiers and three column layouts."""
    it = wd_item(STONE)
    smr = claim_str(it, 'P4057')[0]; find = LAB[claim_ids(it, 'P189')[0]].replace(' (Ogham Site)', '')
    f = Fig('g02_three_tables')
    specs = [(60, 'CIIC', [200, 330], [['No.', 'Place'], ['81', find]]),
             (880, 'CISP', [300, 330], [['Code', 'Site'], ['GARES/1', find]]),
             (1560, 'SMR', [400, 340], [['Record', 'Location'], [smr, find]])]
    cx = []
    for x, name, cw, rows in specs:
        f.text(x + sum(cw) / 2, 110, name, MIN_TYPE, 500)
        c = f.table(x, 160, cw, rows); cx.append(c)
    S = (1200, 720, 360, 110)
    for c in cx: f.line(S[0], S[1] - 55, c[0], c[1] + c[3] / 2)
    f.box(*S, INST, ['one stone'], stroke=HL, sw=8)
    f.done()

def g09():
    """G09: the stone in CIDOC CRM (Part I, step 6): instances with their CRM classes."""
    it = wd_item(STONE)
    name = stone_label(it); place = LAB[claim_ids(it, 'P276')[0]]
    f = Fig('g09_stone_in_crm')
    cl = {'stone': (1200, 130, 540, 96), 'place': (420, 130, 420, 96), 'id': (1980, 130, 460, 96)}
    inst = {'stone': (1200, 650, 460, 130), 'place': (420, 650, 460, 130), 'id': (1980, 650, 340, 110)}
    f.box(*cl['stone'], CLS, ['E22 Human-Made Object'], tc='#fff'); f.box(*cl['place'], CLS, ['E53 Place'], tc='#fff'); f.box(*cl['id'], CLS, ['E42 Identifier'], tc='#fff')
    f.box(*inst['place'], INST, [place])
    f.box(*inst['id'], INST, ['CIIC 81'])
    f.box(*inst['stone'], INST, [name], stroke=HL, sw=8)
    for k in cl: f.edge(inst[k], cl[k], 'type')
    f.edge(inst['stone'], inst['place'], 'P53 location'); f.edge(inst['stone'], inst['id'], 'P48 identifier')
    f.done()

def g08():
    """G08: vocabulary stack (Part I, step 6): general languages at the bottom, CIDOC CRM on top."""
    f = Fig('g08_vocabulary_stack')
    xs = [930, 1430, 1930]
    f.text(60, 170 + 14, 'Domain model', MIN_TYPE, 500, fill='#55544f', anchor='start')
    f.text(60, 450 + 14, 'Vocabularies', MIN_TYPE, 500, fill='#55544f', anchor='start')
    f.text(60, 730 + 14, 'Languages', MIN_TYPE, 500, fill='#55544f', anchor='start')
    f.box(1430, 170, 1480, 120, CLS, ['CIDOC CRM'], tc='#fff')
    for x, t in zip(xs, ['SKOS', 'PROV-O', 'GeoSPARQL']): f.box(x, 450, 480, 120, TERM, [t], tc='#fff')
    for x, t in zip(xs, ['RDF', 'RDFS', 'OWL']): f.box(x, 730, 480, 120, '#fff', [t])
    f.done()

def g12():
    """G12: a SPARQL query as a graph pattern and its result table (Part I, step 8). Rows are read from the Wikidata copies."""
    rows = []
    for q in (STONE, 'Q126503090'):
        it = wd_item(q); c = it['claims']['P625'][0]['mainsnak']['datavalue']['value']
        rows.append([stone_label(it), dms(c['latitude'], 'N', 'S') + ' ' + dms(c['longitude'], 'E', 'W')])
    f = Fig('g12_sparql_pattern')
    S = (290, 450, 260, 110); c = (1000, 200, 400, 100); xy = (1000, 700, 340, 100)
    f.box(*S, '#fff', ['?stone'], dash=True); f.box(*c, CLS, [LAB['Q2016147']], tc='#fff'); f.box(*xy, '#fff', ['?coord'], dash=True)
    f.edge(S, c, 'instance of'); f.edge(S, xy, 'coordinate location')
    f.edge((1250, 450, 60, 10), (1340, 450, 60, 10), None)
    f.table(1420, 360, [440, 480], [['?stone', '?coord']] + rows + [['\u2026', '\u2026']], rowh=92)
    f.done()


# ---------------------------------------------------------------- Part II
def wb_entity(i):
    d = json.load(open(os.path.join(HERE, f'data/wb/{i}.json'), encoding='utf8')); return list(d['entities'].values())[0] if 'entities' in d else d
def snak_text(sn):
    v = sn['datavalue']['value']
    return wb_entity(v['id'])['labels']['en']['value'] if isinstance(v, dict) and 'id' in v else str(v)

def geo(n): return json.load(open(os.path.join(HERE, f'data/geo/{n}.json'), encoding='utf8'))
def plain(s): return s.replace('₄', '4')            # Fira Sans subset has no subscript four

def g15():
    """G15: one stone, six identifiers (Part II, step 2). Hub with the repositories that hold the same stone."""
    it = wd_item(STONE)
    fdo = claim_str(it, 'P14097')[0].rsplit('-', 1)[0]      # the trailing hash is left out
    hub = (1200, 450, 420, 130)
    spec = [((450, 120), 'Wikidata item', ['Wikidata', STONE]), ((1200, 120), 'OSM node ID', ['OpenStreetMap', 'node ' + claim_str(it, 'P11693')[0]]),
            ((1950, 120), 'FactGrid item ID', ['FactGrid', claim_str(it, 'P8168')[0]]), ((450, 780), 'exact match', ['lod.ogham.link', claim_str(it, 'P2888')[0].rsplit('/', 1)[-1]]),
            ((1200, 780), 'SMR ID', ['SMR', claim_str(it, 'P4057')[0]]), ((1950, 780), 'FDO ID', ['FDOx', fdo])]
    f = Fig('g15_one_stone_six_ids')
    for (x, y), lab, lines in spec:
        n = (x, y, 640, 130); f.box(*n, '#fff', lines, dash=True); f.edge(hub, n, lab)
    f.box(*hub, INST, ['CIIC 81'], stroke=HL, sw=8)
    f.done()

def g17():
    """G17: sample, measurement, model (Part II, step 3). One EPICA Dome C methane observation, read from the geo-lod graph."""
    d = geo('epica_obs'); facts = geo('facts')
    assert ['http://w3id.org/geo-lod/IceCore', 'http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object'] in facts
    num = lambda s, k=2: (f'{float(s):.{k}f}'.rstrip('0') + '0').replace('.0', '.0') if '.' in f'{float(s):.{k}f}' and float(s) == int(float(s)) and k == 1 else f'{float(s):.{k}f}'.rstrip('0').rstrip('.')
    f = Fig('g17_sample_measurement_model')
    for x, t in [(300, 'Sample'), (1200, 'Measurement'), (2100, 'Model')]: f.text(x, 70, t, MIN_TYPE, 500, fill='#55544f')
    o = (1200, 450, 460, 130)
    core = (300, 250, 560, 130); prop = (300, 650, 560, 110)
    chron = (2100, 250, 560, 130); age = (2100, 650, 560, 110)
    val = (900, 800, 480, 100); dep = (1500, 800, 480, 100)
    f.box(*core, INST, [plain(d['core']), 'IceCore'])
    f.box(*prop, INST, [plain(d['prop'])])
    f.box(*chron, TERM, [d['chron_label'].split(',')[0], 'temporal reference system'], tc='#fff')
    f.box(*age, '#fff', [num(d['age'], 1) + ' ka BP'])
    f.box(*val, '#fff', [num(d['value']) + ' ' + d['unit'].lower()])
    f.box(*dep, '#fff', [num(d['depth']) + ' m'])
    f.box(*o, INST, ['Observation ' + d['obs'].rsplit('_', 1)[-1], 'IceCoreObservation'], stroke=HL, sw=8)
    for t, lab in [(core, 'feature of interest'), (prop, 'observed property'), (chron, 'age chronology'), (age, 'age'), (val, 'measured value'), (dep, 'at depth')]: f.edge(o, t, lab)
    f.done()

def g18():
    """G18: time and strata (Part II, step 3 and 4). Three competing ages of the Campanian Ignimbrite eruption on one axis, each with its own time reference system."""
    rows = geo('time')
    f = Fig('g18_ci_competing_ages')
    x0, x1, k0, k1 = 760, 2300, 40.15, 39.10
    X = lambda v: x0 + (k0 - v) / (k0 - k1) * (x1 - x0)
    ys = [150, 360, 570]
    for t in (40.1, 39.9, 39.7, 39.5, 39.3, 39.1):
        f.o.append(f'<line x1="{X(t):.1f}" y1="60" x2="{X(t):.1f}" y2="760" stroke="#d4d4d0" stroke-width="2" stroke-dasharray="6 8"/>')
        f.text(X(t), 815, f'{t:.1f}', MIN_TYPE, 400, '#55544f')
    f.line(x0, 760, x1, 760, dash=False)
    f.text(x1, 868, 'ka BP', MIN_TYPE, 500, '#55544f', 'end')
    for r, y in zip(rows, ys):
        who = re.search(r', ([^,]*)\((\d{4})\)$', r['label'])
        name = f'{who.group(1).strip()} ({who.group(2)})'
        f.text(60, y - 4, name, MIN_TYPE, 500, anchor='start', maxw=660)
        f.text(60, y + 46, r['trs'].rsplit('/', 1)[-1], MIN_TYPE, 400, '#55544f', 'start', maxw=660)
        a, b = X(r['begin']), X(r['end'])
        f.o.append(f'<rect x="{a:.1f}" y="{y - 45}" width="{b - a:.1f}" height="90" rx="18" fill="{INST}" stroke="{HL if r["adopted"] else "#000"}" stroke-width="{8 if r["adopted"] else 2.5}"/>')
        f.text(a, y + 92, f'{r["begin"]:.2f}', MIN_TYPE, 400, anchor='start'); f.text(b, y + 92, f'{r["end"]:.2f}', MIN_TYPE, 400, anchor='end')
        if r['adopted']: f.text(b + 30, y + 14, 'adopted', MIN_TYPE, 500, HL, 'start')
    f.done()

def g20():
    """G20: the four pillars of the bridge (Part II, step 4): identifiers, coordinates, vocabularies, crosswalks. Examples come from the stone, the SISAL cave Chauvet and the geo-lod ontologies."""
    it = wd_item(STONE); c = it['claims']['P625'][0]['mainsnak']['datavalue']['value']
    cave = next(x for x in geo('sisal') if x[2] == 'Chauvet cave'); facts = geo('facts')
    assert ['http://w3id.org/geo-lod/IceCore', 'http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object'] in facts
    pt = lambda lon, lat: f'POINT({lon:.2f} {lat:.2f})'
    pillars = [('Identifiers', [[STONE, 'CIIC 81'], ['Q191483', 'Chauvet cave']]),
               ('Coordinates', [[pt(c['longitude'], c['latitude']), 'CIIC 81'], [pt(cave[0], cave[1]), 'Chauvet cave']]),
               ('Vocabularies', [['CIDOC CRM', 'stones, places, events'], ['SOSA / SSN', 'samples, observations']]),
               ('Crosswalks', [['sosa:Observation', 'subClassOf crmsci:S4'], ['geolod:IceCore', 'subClassOf crm:E22']])]
    f = Fig('g20_four_pillars')
    f.o.append(f'<rect x="60" y="50" width="2280" height="110" rx="18" fill="{HL}" stroke="#000" stroke-width="2.5"/>')
    f.text(110, 118, 'Humanities', MIN_TYPE, 500, '#fff', 'start'); f.text(1200, 118, 'one knowledge graph', MIN_TYPE, 500, '#fff'); f.text(2290, 118, 'Geosciences', MIN_TYPE, 500, '#fff', 'end')
    for i, (title, items) in enumerate(pillars):
        cx = 330 + i * 580
        f.o.append(f'<rect x="{cx - 270}" y="160" width="540" height="700" fill="{INST}" stroke="#000" stroke-width="2.5"/>')
        f.text(cx, 245, f'{i + 1}  {title}', MIN_TYPE, 500)
        for j, lines in enumerate(items): f.box(cx, 450 + j * 220, 480, 150, '#fff', lines)
    f.done()

def g19():
    """G19: the SISAL caves and the Campanian Ignimbrite findspots on one map (Part II, step 4). Points only; archaeological sites carry an amethyst ring."""
    sl, ci, land_ = geo('sisal'), geo('ci'), geo('land')
    lon0, lon1, lat0, lat1, latc = -14, 48, 29, 55, 42
    mh = 860; kx = mh * math.cos(math.radians(latc)) / (lat1 - lat0); mw = (lon1 - lon0) * kx; ky = kx / math.cos(math.radians(latc))
    mx, my = 20, 20
    X = lambda lon: mx + (lon - lon0) * kx
    Y = lambda lat: my + (lat1 - lat) * ky
    inside = lambda p: lon0 <= p[0] <= lon1 and lat0 <= p[1] <= lat1
    f = Fig('g19_map_sisal_ci')
    f.o.append(f'<clipPath id="m"><rect x="{mx}" y="{my}" width="{mw:.1f}" height="{mh}"/></clipPath><rect x="{mx}" y="{my}" width="{mw:.1f}" height="{mh}" fill="#dce9f1"/><g clip-path="url(#m)">')
    for ring in land_: f.o.append('<path d="' + ' '.join(('M' if i == 0 else 'L') + f'{X(p[0]):.1f},{Y(p[1]):.1f}' for i, p in enumerate(ring)) + 'Z" fill="#f3f0e7" stroke="#b3b0a4" stroke-width="1.2"/>')
    S = [p for p in sl if inside(p)]
    for p in S:
        if p[3]: f.o.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="16" fill="none" stroke="{HL}" stroke-width="5"/>')
    for p in ci:
        if p[3]: f.o.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="20" fill="none" stroke="{HL}" stroke-width="5"/>')
    for p in S: f.o.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="8" fill="{CLS}" stroke="#fff" stroke-width="1.8"/>')
    for p in ci: f.o.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="11" fill="{TERM}" stroke="#fff" stroke-width="2.2"/>')
    f.o.append(f'</g><rect x="{mx}" y="{my}" width="{mw:.1f}" height="{mh}" fill="none" stroke="#000" stroke-width="2.5"/>')
    lx, ly = mx + mw + 70, 300
    f.o.append(f'<circle cx="{lx}" cy="{ly}" r="11" fill="{CLS}" stroke="#000" stroke-width="2"/>'); f.text(lx + 36, ly + 14, f'SISAL caves ({len(S)})', MIN_TYPE, 400, anchor='start')
    f.o.append(f'<circle cx="{lx}" cy="{ly + 90}" r="13" fill="{TERM}" stroke="#000" stroke-width="2"/>'); f.text(lx + 36, ly + 104, f'CI findspots ({len(ci)})', MIN_TYPE, 400, anchor='start')
    f.o.append(f'<circle cx="{lx}" cy="{ly + 180}" r="18" fill="none" stroke="{HL}" stroke-width="5"/>'); f.text(lx + 36, ly + 194, 'archaeological site', MIN_TYPE, 400, anchor='start')
    f.done()

def g22():
    """G22: the live demos (Part II, step 5). A: Wikidata or N4O KG, SPARQLing Unicorn, QGIS map. B: OER notebook running in the browser."""
    f = Fig('g22_demo_flow')
    f.text(60, 80, 'Demo A', MIN_TYPE, 500, '#55544f', 'start'); f.text(60, 530, 'Demo B', MIN_TYPE, 500, '#55544f', 'start')
    a = [(330, 280, 520, 130), (1200, 280, 520, 130), (2070, 280, 520, 130)]
    b = [(330, 730, 520, 130), (1200, 730, 520, 130), (2070, 730, 520, 130)]
    f.box(*a[0], '#fff', ['Wikidata', 'N4O KG'], dash=True); f.box(*a[1], INST, ['SPARQLing Unicorn', 'QGIS plugin'], stroke=HL, sw=8); f.box(*a[2], '#fff', ['Map in QGIS'])
    f.box(*b[0], INST, ['OER notebook', 'Quarto-live']); f.box(*b[1], '#fff', ['Python in the browser', 'Pyodide']); f.box(*b[2], '#fff', ['Table and map'])
    f.edge(a[0], a[1], 'SPARQL'); f.edge(a[1], a[2], 'layer'); f.edge(b[0], b[1], 'runs in'); f.edge(b[1], b[2], 'result')
    f.done()


# ---------------------------------------------------------------- Part I, rest
def star(f, cx, cy, r=24):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.45
        pts.append(f'{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}')
    f.o.append(f'<polygon points="{" ".join(pts)}" fill="{AMB}" stroke="#000" stroke-width="2" stroke-linejoin="round"/>')

def g03():
    """G03: the five stars of open data (Part I, step 5), each with a symbol."""
    f = Fig('g03_five_stars')
    spec = [('globe', 'On the web', 'open licence'), ('table', 'Structured', 'Excel, not a scan'), ('file', 'Open format', 'CSV, not Excel'), ('tag', 'URIs', 'RDF and SPARQL'), ('chain', 'Linked', 'to other data')]
    for i, (ic, a, b) in enumerate(spec):
        cx = 260 + i * 470; h = 380 + i * 100; top = 860 - h
        f.o.append(f'<rect x="{cx - 225}" y="{top}" width="450" height="{h}" rx="18" fill="{INST}" stroke="{HL if i >= 3 else "#000"}" stroke-width="{8 if i >= 3 else 2.5}"/>')
        for j in range(i + 1): star(f, cx + (j - i / 2) * 56, top + 50)
        icon(f, ic, cx, top + 150, z=1.0)
        f.text(cx, top + 255, a, MIN_TYPE, 500, maxw=420); f.text(cx, top + 305, b, MIN_TYPE, 400, maxw=420)
    f.done()

def g07():
    """G07: the Linked Open Data cloud (Part I, step 5), schematic: datasets as nodes, links to Wikidata as lines. Datasets of the project are solid, others dashed."""
    f = Fig('g07_lod_cloud')
    hub = (1200, 450, 360, 110)
    ext = [((500, 110), 'DBpedia'), ((1200, 110), 'GeoNames'), ((1900, 110), 'VIAF'), ((250, 450), 'Getty AAT'), ((2150, 450), 'Pleiades'), ((500, 790), 'FactGrid'), ((1900, 790), 'Europeana')]
    own = [((1200, 790), 'N4O KG')]
    for (x, y), t in ext + own:
        n = (x, y, 360, 100); a, b = border(hub, n), border(n, hub); f.line(a[0], a[1], b[0], b[1], dash=False)
    for (x, y), t in ext: f.box(x, y, 360, 100, '#fff', [t], dash=True)
    f.box(1200, 790, 360, 100, INST, ['N4O KG'], stroke=HL, sw=8)
    f.box(*hub, INST, ['Wikidata'])
    f.done()

def g10():
    """G10: the Federated Knowledge Graph Ecosystem, simplified from fig1_fkge (Part I, step 7): two workflows around one graph."""
    f = Fig('g10_fkge_simplified')
    po = (1200, 90, 460, 100)
    L = [(270, 330), (270, 530), (270, 730)]; R = [(2130, 330), (2130, 530), (2130, 730)]
    ln = ['Measurement', 'Analysis & Visualisation', 'Conclusion']; rn = ['Capture & Documentation', 'Analysis & Enrichment', 'Conclusion']
    f.text(270, 235, 'FDO-driven', MIN_TYPE, 500, fill='#55544f'); f.text(2130, 235, 'LOD-driven', MIN_TYPE, 500, fill='#55544f')
    Ln = [(x, y, 520, 100) for x, y in L]; Rn = [(x, y, 520, 100) for x, y in R]
    for n, t in zip(Ln, ln): f.box(*n, INST, [t])
    for n, t in zip(Rn, rn): f.box(*n, INST, [t])
    for i in (0, 1): f.edge(Ln[i], Ln[i + 1], None); f.edge(Rn[i], Rn[i + 1], None)
    fk = (1200, 540, 880, 640)
    f.o.append(f'<rect x="{fk[0] - fk[2] / 2}" y="{fk[1] - fk[3] / 2}" width="{fk[2]}" height="{fk[3]}" rx="30" fill="#fff" stroke="{HL}" stroke-width="8"/>')
    f.text(1200, 270, 'Federated Knowledge Graph', MIN_TYPE, 500)
    for i, t in enumerate(['LOD', 'Wikibase', 'FDO', 'GIS', 'OSM', 'LPG', 'HIN', 'EpiDoc']):
        f.box(1200 + (i % 4 - 1.5) * 205, 400 + (i // 4) * 130, 190, 90, INST, [t])
    f.box(1200, 700, 780, 100, '#fff', ['CIDOC CRM, ontologies, terminologies'], dash=True)
    f.box(*po, INST, ['Physical object'])
    f.edge(po, Ln[0], None); f.edge(po, Rn[0], None)
    f.edge(Ln[1], fk, 'FDOs'); f.edge(Rn[1], fk, 'LOD')
    f.done()

def g11():
    """G11: the N4O Knowledge Graph and its community hubs (Part I, step 7)."""
    f = Fig('g11_n4o_kg_hubs')
    kg = (1200, 450, 460, 130)
    hubs = [((450, 120), 'Roman Open Data', False), ((1200, 120), 'Ogham', False), ((1950, 120), 'fuzzy-sl', False),
            ((450, 780), 'Poseidon', False), ((1200, 780), 'BB-5KBC', False), ((1950, 780), 'Wikidata', True)]
    for (x, y), t, ext_ in hubs:
        n = (x, y, 520, 110); f.box(*n, '#fff' if ext_ else INST, [t], dash=ext_); f.edge(n, kg, 'exact match' if ext_ else 'RDF')
    f.box(*kg, INST, ['N4O KG'], stroke=HL, sw=8)
    f.done()

def g13():
    """G13: how sure is a place? Certainty levels of the 74 CI findspots in the geo-lod graph (Part I, step 9)."""
    from collections import Counter
    cnt = Counter(p[4] for p in geo('ci')); order = ['high', 'medium', 'low', 'dubious', 'representative']
    f = Fig('g13_findspot_certainty')
    s_ = (330, 450, 440, 130)
    for i, k in enumerate(order):
        n = (1950, 100 + i * 175, 560, 100); f.box(*n, TERM, [f'{k.capitalize()} ({cnt[k]})'], tc='#fff'); f.edge(s_, n, 'certainty level')
    f.box(*s_, INST, ['CI findspot', f'{sum(cnt.values())} in the graph'], stroke=HL, sw=8)
    f.done()

def g14():
    """G14: the Academic Meta Tool principle (Part I, step 9). A coordinate statement carries who said it, how, and how sure (fuzzy-sl Wikibase item Q70)."""
    e = wb_entity('Q70'); c = e['claims']['P4'][0]; v = c['mainsnak']['datavalue']['value']
    q = {p: snak_text(s[0]) for p, s in c['qualifiers'].items()}
    f = Fig('g14_amt_principle')
    s_ = (240, 450, 380, 110); xy = (1050, 450, 520, 110)
    f.box(*s_, INST, [e['labels']['en']['value']])
    f.box(*xy, '#1f1f1d', [dms(v['latitude'], 'N', 'S') + ' ' + dms(v['longitude'], 'E', 'W')], tc='#fff', stroke=HL, sw=8)
    f.edge(s_, xy, 'coordinate')
    for i, (p, fill) in enumerate([('P5', TERM), ('P7', TERM), ('P6', TERM), ('P14', INST)]):
        n = (1980, 130 + i * 213, 600, 100); f.box(*n, fill, [q[p]], tc='#fff' if fill == TERM else INK); f.edge(xy, n, {'P5': 'certainty level', 'P7': 'method used', 'P6': 'source type', 'P14': 'acting person'}[p])
    f.done()


def g16():
    """G16: measurement to CIDOC CRM (Part II, step 3 and 4): the crosswalk of the geo-lod measurement classes, asserted in the ontology files."""
    facts = geo('facts'); S = lambda a: [x[0] for x in facts if x[0].endswith(a)]
    rows = [('sosa:Observation', 'http://www.w3.org/ns/sosa/Observation', 'crmsci:S4_Observation'), ('sosa:Sample', 'http://www.w3.org/ns/sosa/Sample', 'crm:E18_Physical_Thing'),
            ('sosa:ObservableProperty', 'http://www.w3.org/ns/sosa/ObservableProperty', 'crmsci:S9_Property_Type'), ('geolod:IceCore', 'http://w3id.org/geo-lod/IceCore', 'crm:E22_Human-Made_Object')]
    for _, iri, _ in rows: assert any(x[0] == iri for x in facts), iri
    f = Fig('g16_measurement_to_crm')
    f.text(520, 70, 'Measurement vocabularies', MIN_TYPE, 500, fill='#55544f'); f.text(1900, 70, 'CIDOC CRM and CRMsci', MIN_TYPE, 500, fill='#55544f')
    for i, (a, _, b) in enumerate(rows):
        y = 200 + i * 200; l = (520, y, 700, 110); r = (1900, y, 760, 110)
        f.box(*l, CLS, [a], tc='#fff'); f.box(*r, CLS, [b], tc='#fff'); f.edge(l, r, 'subClassOf')
    f.done()

def g01():
    """G01: data islands (Part I, step 3, only on demand): the same stone sits in three sources that know nothing of each other."""
    it = wd_item(STONE)
    find = LAB[claim_ids(it, 'P189')[0]].replace(' (Ogham Site)', '')
    f = Fig('g01_data_islands')
    for cx, cy, name, key in [(420, 450, 'CIIC', 'No. 81'), (1200, 450, 'CISP', 'GARES/1'), (1980, 450, 'SMR', claim_str(it, 'P4057')[0])]:
        f.o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="330" ry="260" fill="{INST}" stroke="#000" stroke-width="2.5"/>')
        f.text(cx, cy - 60, name, MIN_TYPE, 500); f.text(cx, cy + 10, key, MIN_TYPE, 400, maxw=560); f.text(cx, cy + 80, find, MIN_TYPE, 400, maxw=560)
    f.done()

def g21():
    """G21: a crosswalk (Part II, step 4, only on demand): Wikidata properties mapped to CIDOC CRM properties, the same pairs as in G09."""
    f = Fig('g21_crosswalk')
    f.text(400, 90, 'Wikidata', MIN_TYPE, 500, fill='#55544f'); f.text(2000, 90, 'CIDOC CRM', MIN_TYPE, 500, fill='#55544f')
    for i, (a, b) in enumerate([('P31 instance of', 'P2 has type'), ('P276 location', 'P53 has former or current location'), ('P217 inventory number', 'P48 has preferred identifier')]):
        y = 250 + i * 240; l = (400, y, 620, 110); r = (2000, y, 760, 110)
        f.box(*l, TERM, [a], tc='#fff'); f.box(*r, TERM, [b], tc='#fff'); f.edge(l, r, 'maps to')
    f.done()


def g23():
    """G23: a relational database (Part I, step 3): two tables joined by a foreign key. Values are read from the Wikidata copy of CIIC 81."""
    it = wd_item(STONE); pid = claim_ids(it, 'P189')[0]; place = LAB[pid].replace(' (Ogham Site)', '')
    f = Fig('g23_relational_keys')
    f.text(520, 340, 'stone', MIN_TYPE, 500); f.text(1880, 340, 'place', MIN_TYPE, 500)
    t1 = f.table(100, 390, [440, 440], [['name', 'place_id'], ['CIIC 81', pid]], rowh=110)
    t2 = f.table(1440, 390, [440, 440], [['place_id', 'name'], [pid, place]], rowh=110)
    a = (100 + 440 + 220, 390 + 165, 440, 110); b = (1440 + 220, 390 + 165, 440, 110)
    f.edge(a, b, 'foreign key')
    f.done()

def g24():
    """G24: how an Ogham stone is read (Part I, step 2). The strokes are drawn from the transcription of CIIC 81 in Wikidata; restored letters are grey."""
    t = wd_item(STONE)['claims']['P1684'][0]['mainsnak']['datavalue']['value']['text']
    # aicme: (kind, count). B: right of the stem, H: left, M: across, A: notches
    code = {}
    for k, (kind, letters) in enumerate([('B', 'BLFSN'), ('H', 'HDTCQ'), ('M', 'MGZR'), ('A', 'AOUEI')]):
        for n, ch in enumerate(letters, 1): code[ch] = (kind, n)
    code['Z'] = ('M', 4)
    f = Fig('g24_ogham_reading')
    sy = 440; x = 90; sp = 18; gap = 26; wordgap = 60
    f.o.append(f'<line x1="40" y1="{sy}" x2="2360" y2="{sy}" stroke="#000" stroke-width="6"/>')
    restored = False
    for ch in t:
        if ch == '[': restored = True; continue
        if ch == ']': restored = False; continue
        if ch == ' ': x += wordgap; continue
        kind, n = code[ch]; col = '#a8a69c' if restored else '#000'
        for j in range(n):
            xs = x + j * sp
            if kind == 'B': f.o.append(f'<line x1="{xs}" y1="{sy}" x2="{xs}" y2="{sy + 85}" stroke="{col}" stroke-width="8" stroke-linecap="round"/>')
            elif kind == 'H': f.o.append(f'<line x1="{xs}" y1="{sy}" x2="{xs}" y2="{sy - 85}" stroke="{col}" stroke-width="8" stroke-linecap="round"/>')
            elif kind == 'M': f.o.append(f'<line x1="{xs - 18}" y1="{sy + 85}" x2="{xs + 18}" y2="{sy - 85}" stroke="{col}" stroke-width="8" stroke-linecap="round"/>')
            else: f.o.append(f'<line x1="{xs}" y1="{sy - 18}" x2="{xs}" y2="{sy + 18}" stroke="{col}" stroke-width="10" stroke-linecap="round"/>')
        w = (n - 1) * sp
        f.text(x + w / 2, sy + 190, ch, MIN_TYPE, 500, '#a8a69c' if restored else INK)
        x += w + gap + sp
    assert x < 2400, x
    f.text(40, 130, 'Strokes above the stem: H, D, T, C, Q', MIN_TYPE, 400, '#55544f', 'start'); f.text(40, 800, 'Strokes below the stem: B, L, F, S, N', MIN_TYPE, 400, '#55544f', 'start')
    f.text(2360, 800, 'Slanted: M, G, Z, R · Notches: A, O, U, E, I', MIN_TYPE, 400, '#55544f', 'end')
    f.text(2360, 130, 'grey: restored letters', MIN_TYPE, 400, '#55544f', 'end')
    f.done()

def g25():
    """G25: FAIR in four columns (Part I, step 10), each with an example from the stone."""
    cols = [('F', 'Findable', [['URI per thing', STONE], ['lod.ogham.link', claim_str(wd_item(STONE), 'P2888')[0].rsplit('/', 1)[-1]]]),
            ('A', 'Accessible', [['SPARQL', 'open protocol'], ['Wikidata', 'N4O KG']]),
            ('I', 'Interoperable', [['CIDOC CRM', 'shared model'], ['SKOS', 'GeoSPARQL']]),
            ('R', 'Reusable', [['Licence', 'CC0 in Wikidata'], ['Provenance', 'who said what']])]
    f = Fig('g25_fair_examples')
    for i, (l, name, items) in enumerate(cols):
        cx = 330 + i * 580
        f.o.append(f'<circle cx="{cx}" cy="130" r="80" fill="{INST}" stroke="{HL}" stroke-width="8"/>'); f.text(cx, 158, l, 80, 700)
        f.text(cx, 290, name, MIN_TYPE, 500)
        for j, lines in enumerate(items): f.box(cx, 450 + j * 200, 500, 140, '#fff', lines)
    f.done()


def panel(f, x, y, w, h):
    f.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#f6f3ec" stroke="#000" stroke-width="2.5"/>')

def g26():
    """G26: the triple in Turtle (Part I, step 4). The same three statements as in G05, written as Turtle; the semicolon repeats the subject."""
    it = wd_item(STONE); lab = it['labels']['en']['value']; inv = claim_str(it, 'P217')[0]
    f = Fig('g26_turtle_triples')
    panel(f, 60, 60, 2280, 780)
    for i, t in enumerate(['@prefix wd: <http://www.wikidata.org/entity/> .', '@prefix wdt: <http://www.wikidata.org/prop/direct/> .', '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .']):
        f.text(110, 150 + i * 62, t, MIN_TYPE, 400, '#55544f', 'start', maxw=2150)
    rows = [('wd:' + STONE, 'wdt:P31', 'wd:Q2016147 ;'), ('', 'wdt:P217', f'"{inv}" ;'), ('', 'rdfs:label', f'"{lab}"@en .')]
    for i, (s_, p_, o_) in enumerate(rows):
        y = 420 + i * 110
        if s_: f.o.append(f'<rect x="100" y="{y - 46}" width="{tw(s_, MIN_TYPE) + 30:.0f}" height="68" rx="12" fill="{INST}" stroke="#000" stroke-width="2"/>'); f.text(115, y, s_, MIN_TYPE, 500, anchor='start')
        f.o.append(f'<rect x="700" y="{y - 46}" width="{tw(p_, MIN_TYPE) + 30:.0f}" height="68" rx="12" fill="{AMB}" stroke="#000" stroke-width="2"/>'); f.text(715, y, p_, MIN_TYPE, 400, anchor='start')
        f.text(1050, y, o_, MIN_TYPE, 400, anchor='start', maxw=1250)
    f.text(110, 780, 'A semicolon repeats the subject, a full stop ends the sentence.', MIN_TYPE, 400, '#55544f', 'start')
    f.done()

def g29():
    """G29: the SPARQL query behind G12 (Part I, step 8)."""
    f = Fig('g29_sparql_query')
    panel(f, 60, 100, 2280, 700)
    lines = [(0, 'SELECT ?stone ?coord'), (0, 'WHERE {'), (1, '?stone wdt:P31 wd:Q2016147 ;'), (3, 'wdt:P625 ?coord .'), (0, '}'), (0, 'LIMIT 2')]
    for i, (ind, t) in enumerate(lines):
        x = 130 + ind * 50
        f.text(x, 230 + i * 100, t, MIN_TYPE, 500 if i in (0, 1, 4, 5) else 400, anchor='start')
    f.done()

def agenda(name, rows, cols_n):
    f = Fig(name)
    per = math.ceil(len(rows) / cols_n); step = 165 if per == 5 else 220
    y0 = 110 if per == 5 else 230
    for i, (t, m) in enumerate(rows):
        c, r = divmod(i, per); cx = 620 + c * 1160; cy = y0 + r * step
        f.box(cx, cy, 1120, 120, INST, [''], r=18)
        f.text(cx - 530, cy + 14, f'{i + 1}  {t}', MIN_TYPE, 500, anchor='start', maxw=870); f.text(cx + 530, cy + 14, f'{m} min', MIN_TYPE, 400, '#55544f', 'end')
    f.done()

def g27():
    """G27: agenda of Part I (60 minutes)."""
    agenda('g27_agenda_part1', [('Introduction', 4), ('Ogham in three minutes', 3), ('Tables and databases', 7), ('From graph to RDF', 10), ('Linked Data and the LOD cloud', 4),
        ('Vocabularies and CIDOC CRM', 7), ('N4O KG and community hubs', 7), ('SPARQL', 8), ('Vagueness and AMT', 5), ('FAIR and take-home', 5)], 2)

def g28():
    """G28: agenda of Part II (60 minutes)."""
    agenda('g28_agenda_part2', [('The bridge question', 4), ('Ogham and Linked Data', 13), ('geo-lod: ice, caves, tephra', 13), ('Building the bridge', 10), ('Live: Unicorn and OER', 15), ('Take-home', 5)], 2)

def g30():
    """G30: two communities, three shared keys (Part II, step 1)."""
    f = Fig('g30_two_communities')
    f.text(330, 70, 'Humanities ask', MIN_TYPE, 500, HL); f.text(2070, 70, 'Geosciences ask', MIN_TYPE, 500, HL); f.text(1200, 70, 'Both need', MIN_TYPE, 500, HL)
    left = ['Where was it found?', 'When was it made?', 'Which object is it?']; right = ['Where was it sampled?', 'How old is it?', 'Which sample is it?']
    keys = ['Place', 'Time', 'Identifier']
    for i in range(3):
        y = 230 + i * 240
        l, r, k = (330, y, 600, 130), (2070, y, 600, 130), (1200, y, 440, 130)
        f.box(*l, INST, [left[i]]); f.box(*r, INST, [right[i]]); f.box(*k, '#fff', [keys[i]], stroke=HL, sw=8)
        f.edge(l, k, ''); f.edge(r, k, '')
    f.done()

def g31():
    """G31: Ogham data from a database into the graph (Part II, step 2). Four stations of the pipeline."""
    f = Fig('g31_ogham_pipeline')
    st = [((250, 450, 400, 190), INST, ['CISP database', 'PostgreSQL'], False), ((850, 450, 400, 190), INST, ['RDF graph', 'CIDOC CRM'], False),
          ((1450, 450, 400, 190), INST, ['lod.ogham.link', 'Linked Data'], False), ((2050, 450, 400, 190), '#fff', ['Wikidata', 'FactGrid'], True)]
    for c, fill, lines, d in st: f.box(*c, fill, lines, dash=d)
    for (a, _, _, _), (b, _, _, _), lab in zip(st, st[1:], ['export', 'publish', 'link']): f.edge(a, b, lab)
    f.done()

def g32():
    """G32: geo-lod adds three geoscience datasets (Part II, step 3). Counts are read from data/geo; EPICA is the number of observations counted in the geo-lod graph."""
    EPICA_N = 4904
    sl, ci = geo('sisal'), geo('ci'); arch = sum(1 for p in sl if p[3])
    f = Fig('g32_geolod_datasets')
    hub = (1200, 150, 440, 120)
    cols = [(400, ['EPICA Dome C', 'ice core', f'{EPICA_N:,} observations']), (1200, ['SISAL', 'speleothems', f'{len(sl)} caves, {arch} archaeological']), (2000, ['Campanian Ignimbrite', 'tephra', f'{len(ci)} findspots'])]
    f.box(*hub, INST, ['geo-lod'], stroke=HL, sw=8)
    for x, lines in cols:
        n = (x, 600, 700, 260); f.box(*n, '#fff', lines); f.edge(hub, n, 'dataset')
    f.done()

def g33():
    """G33: time needs its own reference system (Part II, step 3). Every age points to the chronology it is measured in."""
    d = geo('epica_obs'); rows = geo('time')
    f = Fig('g33_time_reference')
    f.text(560, 50, 'Age', MIN_TYPE, 500, '#55544f'); f.text(1760, 50, 'Temporal reference system', MIN_TYPE, 500, '#55544f')
    items = [(f"{float(d['age']):.1f} ka BP", d['chron_label'].split(',')[0])] + [(f"{r['begin']:.2f}\u2013{r['end']:.2f} ka BP", r['trs'].rsplit('/', 1)[-1]) for r in rows]
    for i, (a, t) in enumerate(items):
        y = 190 + i * 210
        l, r = (560, y, 640, 120), (1760, y, 760, 120)
        f.box(*l, INST, [a]); f.box(*r, TERM, [t], tc='#fff'); f.edge(l, r, 'measured in')
    f.done()

def g34():
    """G34: place and time are the common keys (Part II, step 4). Stone, cave and findspot share the coordinate; cave and findspot also share the age."""
    it = wd_item(STONE); cave = next(x for x in geo('sisal') if x[2] == 'Chauvet cave'); fs = geo('ci')[0]
    f = Fig('g34_place_time_keys')
    ents = [(450, 170, ['CIIC 81', 'Ogham stone']), (450, 450, [cave[2], 'SISAL cave']), (450, 730, [fs[2], 'CI findspot'])]
    place, time_ = (1800, 200, 560, 150), (1800, 700, 560, 150)
    f.box(*place, '#fff', ['Place', 'coordinate'], stroke=HL, sw=8); f.box(*time_, '#fff', ['Time', 'age in ka BP'], stroke=HL, sw=8)
    boxes = [(x, y, 700, 130) for x, y, _ in ents]
    for b, (_, _, lines) in zip(boxes, ents): f.box(*b, INST, lines)
    for b in boxes: f.edge(b, place, '')
    for b in boxes[1:]: f.edge(b, time_, '')
    f.done()

def g35():
    """G35: a bridge does not merge the data (Part II, step 4). Two graphs keep their owner and model; the crosswalk sits between them."""
    f = Fig('g35_bridge_not_merge')
    L, M, R = (400, 450, 640, 330), (1200, 450, 560, 200), (2000, 450, 640, 330)
    f.box(*L, INST, ['Ogham graph', 'own owner', 'own model: CIDOC CRM']); f.box(*R, INST, ['geo-lod graph', 'own owner', 'own model: SOSA, CRMsci'])
    f.box(*M, '#fff', ['Crosswalk', 'maps classes'], stroke=HL, sw=8, dash=True)
    f.edge(M, L, ''); f.edge(M, R, '')
    f.done()

def icon(f, kind, cx, cy, col=HL, z=1.6):
    """Small line icons for slides (tag, globe, triple, chain); drawn as SVG, no font needed."""
    k = f'stroke="{col}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"'
    w, n = f'fill="#fff" {k}', f'fill="none" {k}'
    if kind == 'tag':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><path d="M-62,-38 L14,-38 L66,0 L14,38 L-62,38 Z" {w}/><circle cx="-34" cy="0" r="9" fill="{col}"/></g>')
    elif kind == 'globe':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><circle r="58" {w}/><ellipse rx="24" ry="58" {n}/><path d="M-58,0 H58 M-50,-30 H50 M-50,30 H50" {n}/></g>')
    elif kind == 'triple':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><path d="M-48,32 L48,32 M-48,32 L0,-40 M48,32 L0,-40" {n}/>'
                   f'<circle cx="-48" cy="32" r="17" {w}/><circle cx="48" cy="32" r="17" {w}/><circle cx="0" cy="-40" r="17" {w}/></g>')
    elif kind == 'table':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><path d="M-55,-40 H55 V40 H-55 Z" {w}/><path d="M-55,-13 H55 M-55,13 H55 M-18,-40 V40" {n}/></g>')
    elif kind == 'file':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><path d="M-38,-52 H14 L40,-26 V52 H-38 Z" {w}/><path d="M14,-52 V-26 H40 M-20,2 H22 M-20,24 H22" {n}/></g>')
    elif kind == 'within':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><circle r="58" {w}/><circle r="18" fill="{col}"/></g>')
    elif kind == 'overlap':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><circle cx="-24" r="40" {n}/><circle cx="24" r="40" {n}/></g>')
    elif kind == 'dist':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><path d="M-48,0 H48" {n} stroke-dasharray="10 12"/><circle cx="-56" r="14" fill="{col}"/><circle cx="56" r="14" fill="{col}"/></g>')
    elif kind == 'chain':
        f.o.append(f'<g transform="translate({cx},{cy}) scale({z})"><rect x="-70" y="-24" width="82" height="48" rx="24" {n}/><rect x="-12" y="-24" width="82" height="48" rx="24" {n}/></g>')

def g36():
    """G36: the four rules of Linked Data (Part I, step 5), each with a symbol."""
    f = Fig('g36_four_rules')
    rules = [('tag', '1  Names', 'URIs name things'), ('globe', '2  HTTP', 'anyone can look up'), ('triple', '3  Standards', 'RDF and SPARQL'), ('chain', '4  Links', 'to other URIs')]
    for i, (ic, a, b) in enumerate(rules):
        cx = 330 + i * 580
        f.o.append(f'<rect x="{cx - 260}" y="130" width="520" height="640" rx="18" fill="{INST}" stroke="{HL if i == 3 else "#000"}" stroke-width="{8 if i == 3 else 2.5}"/>')
        icon(f, ic, cx, 310)
        f.text(cx, 560, a, MIN_TYPE, 500, maxw=480); f.text(cx, 640, b, MIN_TYPE, 400, maxw=480)
    f.done()

def g37():
    """G37: three link types (Part II, step 2). The stone in lod.ogham.link and what each predicate says about the other end."""
    f = Fig('g37_link_types')
    hub = (500, 450, 560, 150)
    f.box(*hub, INST, ['lod.ogham.link', claim_str(wd_item(STONE), 'P2888')[0].rsplit('/', 1)[-1]], stroke=HL, sw=8)
    for y, lab, lines in [(150, 'owl:sameAs', ['Wikidata ' + STONE, 'the same thing']), (450, 'skos:exactMatch', ['FactGrid ' + claim_str(wd_item(STONE), 'P8168')[0], 'the same concept']), (750, 'rdfs:seeAlso', ['OpenStreetMap', 'a related page'])]:
        n = (1950, y, 700, 150); f.box(*n, '#fff', lines, dash=True); f.edge(hub, n, lab)
    f.done()

def g38():
    """G38: one URI, two representations (Part II, step 2)."""
    f = Fig('g38_dereferencing')
    uri = (450, 450, 560, 170); web = (1950, 200, 600, 150); ttl = (1950, 700, 600, 150)
    f.box(*uri, INST, ['URI', 'lod.ogham.link/' + claim_str(wd_item(STONE), 'P2888')[0].rsplit('/', 1)[-1]], stroke=HL, sw=8)
    f.box(*web, '#fff', ['Web page', 'for people']); f.box(*ttl, '#fff', ['Triples', 'for machines'])
    f.edge(uri, web, 'Accept: text/html'); f.edge(uri, ttl, 'Accept: text/turtle')
    f.done()

def g39():
    """G39: the vocabulary stack of the bridge (Part II, step 4). One layer per question."""
    f = Fig('g39_ontology_stack')
    rows = [('What is it?', 'CIDOC CRM', 'E22 Human-Made Object'), ('How was it measured?', 'SOSA / CRMsci', 'sosa:Observation'), ('Where is it?', 'GeoSPARQL', 'WKT point'),
            ('When is it?', 'OWL-Time', 'time:TRS reference system'), ('How sure are we?', 'SKOS', 'certainty levels'), ('Who said so?', 'PROV-O', 'agent and activity')]
    for i, (q, v, ex) in enumerate(rows):
        y = 100 + i * 140
        f.box(520, y, 900, 110, INST, [q + '  ' + v] if False else [v + ': ' + q]); f.box(1750, y, 1000, 110, '#fff', [ex], stroke=HL, sw=5)
        f.line(980, y, 1250, y, dash=False)
    f.done()

def g40():
    """G40: a SHACL shape for findspots (Part II, step 4)."""
    f = Fig('g40_shacl_shape')
    shape = (480, 450, 640, 200); n = len(geo('ci'))
    f.box(*shape, TERM, ['FindspotShape', f'checks {n} findspots'], tc='#fff')
    for y, lines in [(150, ['coordinate', 'exactly one']), (450, ['certainty level', 'exactly one']), (750, ['age', 'at least one'])]:
        c = (1900, y, 640, 150); f.box(*c, '#fff', lines); f.edge(shape, c, 'sh:property')
    f.done()

def g41():
    """G41: a GeoSPARQL distance between the stone and a cave (Part II, step 4). The distance is computed from the two points."""
    c = wd_item(STONE)['claims']['P625'][0]['mainsnak']['datavalue']['value']; cave = next(x for x in geo('sisal') if x[2] == 'Chauvet cave')
    la1, lo1, la2, lo2 = map(math.radians, (c['latitude'], c['longitude'], cave[1], cave[0]))
    d = 2 * 6371 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
    pt = lambda lon, lat: f'POINT({lon:.2f} {lat:.2f})'
    f = Fig('g41_geosparql_distance')
    a = (480, 300, 640, 170); b = (1920, 300, 640, 170)
    f.box(*a, INST, ['CIIC 81', pt(c['longitude'], c['latitude'])]); f.box(*b, INST, ['Chauvet cave', pt(cave[0], cave[1])])
    f.edge(a, b, 'geof:distance')
    f.box(1200, 700, 900, 170, '#fff', ['returns', f'about {round(d, -1):,.0f} km'], stroke=HL, sw=8)
    f.done()

def g42():
    """G42: one federated query reaches three graphs (Part II, step 4)."""
    f = Fig('g42_federated_query')
    q = (1200, 450, 560, 170); f.box(*q, INST, ['One query', 'with SERVICE blocks'], stroke=HL, sw=8)
    for x, y, t in [(420, 170, 'Wikidata'), (420, 730, 'N4O KG'), (2080, 450, 'geo-lod graph')]:
        n = (x, y, 440 if x > 1000 else 560, 130); f.box(*n, '#fff', [t], dash=True); f.edge(q, n, 'SERVICE')
    f.done()

def g43():
    """G43: a URI is a namespace plus a local name (Part I, step 5)."""
    f = Fig('g43_uri_anatomy')
    ns, ln = 'http://www.cidoc-crm.org/cidoc-crm/', 'E22_Human-Made_Object'
    f.text(850, 120, 'namespace', MIN_TYPE, 500, '#55544f'); f.text(1700, 120, 'local name', MIN_TYPE, 500, '#55544f')
    a = (850, 260, 1000, 130); b = (1700, 260, 700, 130)
    f.box(*a, INST, [ns], stroke=HL, sw=6); f.box(*b, INST, [ln])
    p = (850, 700, 400, 130); q = (1700, 700, 700, 130)
    f.box(*p, '#fff', ['crm:'], stroke=HL, sw=6); f.box(*q, '#fff', [ln])
    f.edge(a, p, 'prefix'); f.edge(b, q, '')
    f.done()

def g44():
    """G44: a little RDFS (Part I, step 6). Classes, subclasses, types and a property between classes."""
    f = Fig('g44_rdfs_mini')
    ice, e22, e53 = (280, 200, 460, 130), (1200, 200, 460, 130), (2120, 200, 460, 130)
    edc, cave = (280, 700, 460, 130), (2120, 700, 460, 130)
    f.box(*ice, CLS, ['geolod:IceCore'], tc='#fff'); f.box(*e22, CLS, ['crm:E22', 'Human-Made Object'], tc='#fff'); f.box(*e53, CLS, ['crm:E53 Place'], tc='#fff')
    f.box(*edc, INST, ['EPICA Dome C core']); f.box(*cave, INST, ['Chauvet cave'])
    f.edge(ice, e22, 'rdfs:subClassOf'); f.edge(e22, e53, 'P53 location'); f.edge(edc, ice, 'rdf:type'); f.edge(cave, e53, 'rdf:type')
    f.done()

def g45():
    """G45: a SKOS concept scheme (Part I, step 6). The certainty levels of the Campanian Ignimbrite findspots."""
    from collections import Counter
    cnt = Counter(p[4] for p in geo('ci')); order = ['high', 'medium', 'low', 'dubious', 'representative']
    f = Fig('g45_skos_scheme')
    sch = (1200, 150, 640, 130); f.box(*sch, TERM, ['Certainty levels', 'skos:ConceptScheme'], tc='#fff')
    for i, k in enumerate(order):
        n = (300 + i * 450, 700, 400, 150); f.box(*n, INST, [k.capitalize(), f'{cnt[k]} findspots']); f.edge(n, sch, '' if i != 2 else 'skos:inScheme')
    f.done()

def short(lab): return lab.replace(' (Ogham Site)', '')

def g46():
    """G46: a triple reads like a sentence (Part I, step 4). Sentence on top, the same statement as a graph below."""
    it = wd_item(STONE); place = short(LAB[claim_ids(it, 'P189')[0]])
    f = Fig('g46_triple_sentence')
    for x, t in [(330, 'Subject'), (1200, 'Predicate'), (2070, 'Object')]: f.text(x, 90, t, MIN_TYPE, 500, fill='#55544f')
    f.box(330, 220, 520, 130, INST, ['CIIC 81']); f.box(1200, 220, 520, 130, AMB, ['was found at']); f.box(2070, 220, 520, 130, INST, [place])
    f.text(1200, 440, 'the same statement as a graph', MIN_TYPE, 400, fill='#55544f')
    a, b = (330, 700, 520, 130), (2070, 700, 520, 130)
    f.box(*a, INST, ['CIIC 81'], stroke=HL, sw=8); f.box(*b, INST, [place], stroke=HL, sw=8)
    f.edge(a, b, 'location of discovery')
    f.line(330, 285, 330, 635); f.line(2070, 285, 2070, 635)
    f.done()

def g47():
    """G47: one predicate, many subjects (Part I, step 4). The edge has a URI and can be reused and queried."""
    f = Fig('g47_edge_meaning')
    rows = [(170, 'CIIC 81', short(LAB[claim_ids(wd_item(STONE), 'P189')[0]])), (420, 'Chauvet cave', 'Ardèche'), (670, 'EPICA Dome C core', 'Antarctica')]
    for y, s_, o in rows:
        a, b = (450, y, 640, 120), (1950, y, 640, 120)
        f.box(*a, INST, [s_]); f.box(*b, INST, [o]); f.edge(a, b, 'has location')
    f.text(1200, 860, 'crm:P53_has_former_or_current_location', MIN_TYPE, 500, fill=HL)
    f.done()

def g48():
    """G48: classes and instances (Part I, step 4). The model sits above the line, the data below."""
    it = wd_item(STONE); place = short(LAB[claim_ids(it, 'P189')[0]])
    f = Fig('g48_class_instance')
    f.line(40, 450, 2360, 450)
    f.text(40, 130, 'Classes', MIN_TYPE, 500, fill='#55544f', anchor='start'); f.text(40, 180, 'kinds of things', MIN_TYPE, 400, fill='#55544f', anchor='start')
    f.text(40, 630, 'Instances', MIN_TYPE, 500, fill='#55544f', anchor='start'); f.text(40, 680, 'the things themselves', MIN_TYPE, 400, fill='#55544f', anchor='start')
    c1, c2 = (900, 160, 600, 130), (1900, 160, 600, 130); i1, i2 = (900, 740, 600, 130), (1900, 740, 600, 130)
    f.box(*c1, CLS, ['E22 Human-Made Object'], tc='#fff'); f.box(*c2, CLS, ['E53 Place'], tc='#fff')
    f.box(*i1, INST, ['CIIC 81']); f.box(*i2, INST, [place])
    f.edge(c1, c2, 'P53 has location'); f.edge(i1, i2, 'P53 has location')
    f.edge(i1, c1, 'rdf:type'); f.edge(i2, c2, 'rdf:type')
    f.done()

def g49():
    """G49: CIDOC CRM puts an event in the centre (Part I, step 6). Unknown slots stay open and dashed."""
    it = wd_item(STONE); place = short(LAB[claim_ids(it, 'P189')[0]])
    f = Fig('g49_crm_event')
    hub = (1200, 450, 440, 170); f.box(*hub, INST, ['Carving of CIIC 81', 'E12 Production'], stroke=HL, sw=8)
    spec = [((300, 200), ['unknown carver', 'E39 Actor'], True, 'P14 carried out by'), ((300, 700), ['unknown date', 'E52 Time-Span'], True, 'P4 has time-span'),
            ((2100, 200), ['CIIC 81', 'E22 Human-Made Object'], False, 'P108 has produced'), ((2100, 700), [place, 'E53 Place'], False, 'P7 took place at')]
    for (x, y), lines, dash, lab in spec:
        n = (x, y, 540, 150); f.box(*n, '#fff' if dash else INST, lines, dash=dash); f.edge(hub, n, lab)
    f.done()

def g50():
    """G50: the life of one object as events (Part I, step 6)."""
    it = wd_item(STONE); place = short(LAB[claim_ids(it, 'P189')[0]])
    f = Fig('g50_crm_life')
    ev = [(400, ['Carving', 'E12 Production']), (1200, ['Discovery at ' + place, 'E7 Activity']), (2000, ['Transfer to UCC', 'E10 Transfer of Custody'])]
    boxes = [(x, 200, 640, 150) for x, _ in ev]
    for b, (_, l) in zip(boxes, ev): f.box(*b, INST, l)
    f.edge(boxes[0], boxes[1], 'then'); f.edge(boxes[1], boxes[2], 'then')
    obj = (1200, 730, 560, 140); f.box(*obj, INST, ['CIIC 81', 'E22 Human-Made Object'], stroke=HL, sw=8)
    for b, lab in zip(boxes, ['has produced', 'present at', 'custody of']): f.edge(b, obj, lab)
    f.done()

def g51():
    """G51: a Wikidata item is a page of statements (Part I, step 5). Values read from the Wikidata JSON."""
    it = wd_item(STONE); c = it['claims']['P625'][0]['mainsnak']['datavalue']['value']
    f = Fig('g51_wikidata_item')
    item = (400, 450, 600, 330); f.box(*item, INST, ['Item', STONE, stone_label(it)], stroke=HL, sw=8)
    rows = [['Property', 'Value'], ['P31 instance of', LAB['Q2016147']], ['P189 location of discovery', short(LAB[claim_ids(it, 'P189')[0]])],
            ['P625 coordinate location', dms(c['latitude'], 'N', 'S') + ' ' + dms(c['longitude'], 'E', 'W')], ['P2888 exact match', 'lod.ogham.link ' + claim_str(it, 'P2888')[0].rsplit('/', 1)[-1]]]
    f.table(800, 220, [680, 820], rows, rowh=92)
    f.done()

def g52():
    """G52: statement anatomy (Part I, step 5). One of the two coordinates of CIIC 81 with its qualifiers, reference and rank."""
    it = wd_item(STONE); st = it['claims']['P625'][0]; v = st['mainsnak']['datavalue']['value']
    assert st['rank'] == 'preferred'
    q = {p: LAB[s[0]['datavalue']['value']['id']] for p, s in st['qualifiers'].items() if p in ('P459', 'P276', 'P248')}
    ref = st['references'][0]['snaks']['P11693'][0]['datavalue']['value']
    f = Fig('g52_statement_anatomy')
    a, b = (350, 130, 500, 110), (1950, 130, 700, 110); f.box(*a, INST, ['CIIC 81']); f.box(*b, INST, [dms(v['latitude'], 'N', 'S') + ' ' + dms(v['longitude'], 'E', 'W')])
    f.edge(a, b, 'P625 coordinate location')
    f.text(650, 330, 'Qualifiers', MIN_TYPE, 500, fill='#55544f'); f.text(1760, 330, 'Reference', MIN_TYPE, 500, fill='#55544f')
    for i, (lab, p) in enumerate([('determination method', 'P459'), ('location', 'P276'), ('stated in', 'P248')]):
        f.box(650, 440 + i * 140, 1000, 110, '#fff', [f'{lab}: {q[p]}'], dash=True)
    f.box(1760, 480, 720, 150, '#fff', ['OSM node ID', ref], dash=True)
    f.text(1760, 650, 'Rank', MIN_TYPE, 500, fill='#55544f'); f.box(1760, 760, 720, 110, AMB, ['preferred'])
    f.done()

def g53():
    """G53: a statement as RDF (Part I, step 5). wdt: is the shortcut, p: ps: pq: prov: reach the statement node."""
    it = wd_item(STONE); st = it['claims']['P625'][0]; v = st['mainsnak']['datavalue']['value']
    meth = LAB[st['qualifiers']['P459'][0]['datavalue']['value']['id']]; ref = st['references'][0]['snaks']['P11693'][0]['datavalue']['value']
    f = Fig('g53_statement_rdf')
    s_, n = (270, 450, 440, 120), (1010, 450, 400, 120)
    val, qual, rf = (2030, 170, 640, 120), (2030, 450, 640, 120), (2030, 730, 640, 120)
    f.box(*s_, INST, ['wd:' + STONE], stroke=HL, sw=8); f.box(*n, '#fff', ['statement node'], dash=True)
    f.box(*val, INST, [f"Point({v['longitude']:.2f} {v['latitude']:.2f})"]); f.box(*qual, INST, [meth]); f.box(*rf, INST, ['OSM node ' + ref])
    f.edge(s_, val, 'wdt:P625'); f.edge(s_, n, 'p:P625'); f.edge(n, val, 'ps:P625'); f.edge(n, qual, 'pq:P459'); f.edge(n, rf, 'prov:wasDerivedFrom')
    f.done()

def g54():
    """G54: follow your nose (Part I, step 5). Each URI opened returns triples with the next URI in them."""
    it = wd_item(STONE); cty = claim_ids(it, 'P131')[0]; ctr = claim_ids(it, 'P17')[0]
    f = Fig('g54_follow_nose')
    xs = [330, 1200, 2070]; names = [('CIIC 81', STONE), (LAB[cty], cty), (LAB[ctr], ctr)]
    boxes = [(x, 320, 520, 150) for x in xs]
    for b, (n_, q) in zip(boxes, names): f.box(*b, INST, [n_, 'wd:' + q], stroke=HL if q == STONE else '#000', sw=8 if q == STONE else 2.5)
    f.edge(boxes[0], boxes[1], 'located in'); f.edge(boxes[1], boxes[2], 'country')
    for b in boxes:
        t = (b[0], 700, 520, 130); f.box(*t, '#fff', ['open the URI', 'get more triples'], dash=True); f.edge(b, t, '')
    f.done()

def g55():
    """G55: GeoSPARQL feature and geometry (Part II, step 4). A feature has a geometry, the geometry has a WKT literal."""
    c = wd_item(STONE)['claims']['P625'][0]['mainsnak']['datavalue']['value']
    f = Fig('g55_geosparql_feature')
    a, g, w = (300, 450, 440, 150), (1200, 450, 440, 150), (2120, 450, 500, 150)
    f.box(*a, INST, ['CIIC 81', 'geo:Feature'], stroke=HL, sw=8); f.box(*g, CLS, ['geo:Geometry'], tc='#fff')
    f.box(*w, '#fff', [f"POINT({c['longitude']:.2f} {c['latitude']:.2f})", 'geo:wktLiteral'])
    f.edge(a, g, 'geo:hasGeometry'); f.edge(g, w, 'geo:asWKT')
    f.done()

def g56():
    """G56: GeoSPARQL spatial functions (Part II, step 4), with one count computed from the geo-lod data."""
    ci, sl = geo('ci'), geo('sisal')
    def hv(a, b):
        la1, lo1, la2, lo2 = map(math.radians, (a[1], a[0], b[1], b[0]))
        return 2 * 6371 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
    n = sum(1 for p in ci if any(hv(p, q) <= 100 for q in sl))
    f = Fig('g56_geosparql_functions')
    for i, (ic, fn, what) in enumerate([('within', 'geof:sfWithin', 'inside a region'), ('overlap', 'geof:sfIntersects', 'overlaps a region'), ('dist', 'geof:distance', 'how far apart')]):
        cx = 400 + i * 800
        f.o.append(f'<rect x="{cx - 340}" y="60" width="680" height="480" rx="18" fill="{INST}" stroke="#000" stroke-width="2.5"/>')
        icon(f, ic, cx, 220, z=1.4); f.text(cx, 395, fn, MIN_TYPE, 500, maxw=640); f.text(cx, 465, what, MIN_TYPE, 400, maxw=640)
    f.box(1200, 740, 1900, 150, '#fff', [f'{n} of {len(ci)} Campanian Ignimbrite findspots lie within 100 km of a SISAL cave'], stroke=HL, sw=8)
    f.done()

if __name__ == '__main__':
    for n in (sys.argv[1:] or ['g06']): globals()[n]()
