"""figs.py: figures for the MOSAIC Winter School 2026 (Kiel, 4 Dec 2026), Part I and Part II.

House style of the figures-tmp-help repository (STYLE.md of deRSE26/figures): Fira Sans, flat colours, no title and no footer in the
image, edge labels as amber chips centred on the arrow. Differences for slides: canvas 2400 x 900 px, type 40 px and more, transparent
background, highlight in MOSAIC amethyst (#9454AC). Everything a graph states is read from data/; nothing of it is typed by hand.

Run (Windows cmd, one line):
  cd /d C:\\git\\figures-tmp-help\\mosaic2026\\figures && pip install resvg_py pillow && python figs.py g06
Output: out/<name>.svg and out/<name>.png
"""
import json, math, os, sys
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

if __name__ == '__main__':
    for n in (sys.argv[1:] or ['g06']): globals()[n]()
