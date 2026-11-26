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
    """G03: the five stars of open data (Part I, step 5)."""
    f = Fig('g03_five_stars')
    spec = [('On the web', 'open licence'), ('Structured', 'Excel, not a scan'), ('Open format', 'CSV, not Excel'), ('URIs', 'RDF and SPARQL'), ('Linked', 'to other data')]
    for i, (a, b) in enumerate(spec):
        cx = 260 + i * 470; h = 240 + i * 120; top = 860 - h
        f.o.append(f'<rect x="{cx - 225}" y="{top}" width="450" height="{h}" rx="18" fill="{INST}" stroke="{HL if i >= 3 else "#000"}" stroke-width="{8 if i >= 3 else 2.5}"/>')
        for j in range(i + 1): star(f, cx + (j - i / 2) * 56, top + 55)
        f.text(cx, top + 135, a, MIN_TYPE, 500, maxw=420); f.text(cx, top + 185, b, MIN_TYPE, 400, maxw=420)
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

if __name__ == '__main__':
    for n in (sys.argv[1:] or ['g06']): globals()[n]()
