"""arch_geolod_style.py: archaeological extension of the geo-lod figures (Part II, MOSAIC 2026).

Same pattern and look as 16-linked-graph, 04-measured-dated-interpreted and 03-stratigraphy-time of
Research-Squirrel-Engineers/GeoScience-FAIRification-LOD (1750 x 1000, Fira Sans). The geo-lod build module is imported from a local
clone; the example (trench, contexts, dates) is fictional.

Run (Windows cmd, one line):
  set GEOLOD=C:\\git\\GeoScience-FAIRification-LOD && cd /d C:\\git\\figures-tmp-help\\mosaic2026\\figures && python arch_geolod_style.py
Output: out/a1-context-linked-graph, a2-measured-dated-interpreted-arch, a3-harris-matrix (svg and png)
"""
import os, sys
from pathlib import Path
REPO = Path(os.environ.get('GEOLOD', '/home/claude/repos/GeoScience-FAIRification-LOD'))
sys.path.insert(0, str(REPO / 'visuals'))
import build as B
from build import Fig, chip, INST, CLS, TERM, OWL, MUTED
OUT = Path(__file__).resolve().parent / 'out'
LAYERS = [('#d9d2c3', '101', 'topsoil'), ('#cdbfa6', '102', 'plough soil'), ('#e6c9a8', '103', 'wall collapse'), ('#f0e0b8', '104', 'floor layer'), ('#b9b4aa', '107', 'natural')]

def section(f, x, y, w, h, labels=True):
    """Trench section: five contexts and a pit; returns the y of each band boundary."""
    bh = h / 5
    for i, (col, n, name) in enumerate(LAYERS):
        f.rect(x, y + i * bh, w, bh, col, '#000000', 0, 1)
        if labels: f.text(x + 14, y + i * bh + bh / 2, f'[{n}] {name}', 19, color='#1f1f1d', anchor='start')
    px, py = x + w * 0.52, y + 3 * bh
    f.raw(f'<path d="M{px - w * .22:.1f},{py:.1f} L{px - w * .13:.1f},{py + bh * 1.25:.1f} L{px + w * .13:.1f},{py + bh * 1.25:.1f} L{px + w * .22:.1f},{py:.1f} Z" fill="#8f7f66" stroke="#9454AC" stroke-width="3"/>')
    if labels: f.text(px, py + bh * .65, '[105]', 19, True, '#ffffff'); f.text(px, py + bh * .65 + 22, 'pit fill', 17, color='#ffffff')
    return bh

def a1():
    f = Fig('a1-context-linked-graph', 'Where the graph opens up: an excavation context as a node, linked to CRMarchaeo, its trench, DOIs, ORCID and its repository')
    f.box(650, 80, 450, 100, 'PeriodO', 'period of the context', TERM, 25, 19, dash=True)
    f.box(40, 200, 360, 110, 'CRMarchaeo', 'class of the node: A2', CLS, 25, 19)
    f.box(40, 740, 360, 110, 'Wikidata, Pleiades', 'the same place, if listed', TERM, 25, 19)
    f.box(1350, 200, 360, 110, 'Zenodo', 'DOI of the excavation record', TERM, 25, 19)
    f.box(1350, 390, 360, 110, 'ORCID', 'excavation director', TERM, 25, 19)
    f.box(1350, 580, 360, 110, 'Repository', 'finds and contexts as RDF', OWL, 25, 19)
    f.box(650, 700, 450, 100, 'GeoSPARQL geometry', 'outline of the trench', INST, 25, 19)
    section(f, 770, 300, 210, 200, labels=False)
    f.text(875, 530, 'Context [104]', 34, True); f.text(875, 568, 'one node, one persistent URI', 20, color=MUTED)
    # the trench: a pit in the ground, schematic
    f.rect(120, 520, 200, 70, '#b9b4aa', '#000000', 0, 1.6)
    f.raw('<path d="M150,520 L175,575 L265,575 L290,520 Z" fill="#ffffff" stroke="#000000" stroke-width="1.6"/>')
    f.text(220, 612, 'Trench 1', 30, True); f.text(220, 646, 'place of the context', 20, color=MUTED)
    for (x1, y1, x2, y2, t, cx, cy, d) in (
            (800, 340, 402, 270, 'rdf:type', 600, 305, False), (800, 450, 322, 540, 'P89 falls within', 580, 490, False),
            (220, 668, 220, 738, None, 0, 0, False), (950, 340, 1348, 270, 'owl:sameAs', 1160, 305, False),
            (960, 410, 1348, 445, 'dct:creator', 1160, 428, False), (950, 470, 1348, 620, 'prov:wasDerivedFrom', 1150, 545, False),
            (875, 590, 875, 698, 'geo:hasGeometry', 875, 644, False), (875, 262, 875, 182, 'references period', 875, 222, True)):
        f.line(x1, y1, x2, y2, dash=d)
        if t: chip(f, cx, cy, t)
    chip(f, 220, 703, 'owl:sameAs')
    f.save()

def a2():
    f = Fig('a2-measured-dated-interpreted-arch', 'One trench section, three kinds of statement: measured, dated, interpreted')
    x, y, w, h = 60, 90, 560, 760
    bh = section(f, x, y, w, h)
    f.text(x + w / 2, 50, 'Trench 1, section A', 24, True); f.text(x + w / 2, 72, 'fictional example', 18, color=MUTED)
    def badge(bx, by, n):
        f.raw(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="15" fill="#1f1f1d"/>'); f.text(bx, by + .5, n, 19, True, '#ffffff')
    cx = x + w * 0.52
    f.raw(f'<circle cx="{x + w * .86:.1f}" cy="{y + 3.5 * bh:.1f}" r="9" fill="#ffffff" stroke="#000000" stroke-width="2"/>')
    badge(x + w + 30, y + 3 * bh, '1'); badge(x + w * .86 + 32, y + 3.5 * bh, '2'); badge(x + w * .86 + 32, y + 3.5 * bh + 56, '3')
    f.line(x + w * .86, y + 3.5 * bh, x + w * .86 + 20, y + 3.5 * bh + 56, None, w=1.4)
    f.rect(x + w * .86 - 6, y + 3.5 * bh + 40, 12, 12, '#1f1f1d')
    cards = [(135, 'Interpreted', 'The pit was dug into the floor and filled later', 'ctx:106_cut', 'at the top of the floor', ('ctx:PitCut', 'local class'), 'A3', 'Stratigraphic Interface', 'CRMarchaeo'),
             (405, 'Dated', 'Charcoal from the floor, 14C, 1610 to 1520 cal BC', 'ctx:date_104', 'of context [104]', ('strat:AgeControlPoint', 'geo-lod class'), 'E13', 'Attribute Assignment', 'CIDOC CRM'),
             (675, 'Measured', 'One 14C measurement on one sample', 'ctx:c14_CH17', 'charcoal CH-17', ('ctx:C14Measurement', 'local class'), 'S4', 'Observation', 'CRMsci')]
    for yy, hd, sub, inst, isub, cl, code, nm, fam in cards:
        f.rect(820, yy - 30, 900, 230, '#f6f6f3', 'none', 10)
        f.text(845, yy + 6, hd, 28, True, anchor='start'); f.text(1000, yy + 7, sub, 20, color=MUTED, anchor='start', maxw=700)
        f.box(845, yy + 55, 310, 105, inst, isub, INST, 21, 19)
        f.box(1205, yy + 55, 265, 105, cl[0], cl[1], CLS, 21, 18)
        f.box(1520, yy + 55, 180, 105, code, nm, CLS, 25, 15.5)
        f.line(1155, yy + 107, 1203, yy + 107); chip(f, 1180, yy + 83, 'a', 15); f.line(1470, yy + 107, 1518, yy + 107, 't')
        f.text(1610, yy + 178, fam, 18, color=MUTED)
    for n, (yy, *_) in zip('123', cards): badge(1704, yy + 6, n)
    f.text(820, 965, 'Section schematic; all contexts, dates and the site are invented for the course', 19, color=MUTED, anchor='start')
    f.save()

def a3():
    f = Fig('a3-harris-matrix', 'The trench section on the left, the same contexts as a Harris matrix on the right')
    # left: what you see in the trench
    x, y, w, h = 60, 110, 700, 760
    f.text(x + w / 2, 55, 'Trench section', 28, True); f.text(x + w / 2, 85, 'fictional example', 19, color=MUTED)
    bh = section(f, x, y, w, h)
    px, py = x + w * 0.52, y + 3 * bh
    f.text(px + w * .27, py + bh * .55, '[106] cut', 21, True, '#9454AC', anchor='start')
    # right: the same contexts as a graph, later at the top
    mx, mw, bhh, gap, y0 = 1010, 320, 62, 64, 110
    f.text(mx + mw / 2, 55, 'Harris matrix', 28, True); f.text(mx + mw / 2, 85, 'later at the top, earlier below', 19, color=MUTED)
    seq = [('101', 'topsoil', '#d9d2c3'), ('102', 'plough soil', '#cdbfa6'), ('103', 'wall collapse', '#e6c9a8'),
           ('105', 'pit fill', '#8f7f66'), ('106', 'pit cut', '#ffffff'), ('104', 'floor layer', '#f0e0b8'), ('107', 'natural', '#b9b4aa')]
    rel = ['above', 'above', 'above', 'fills', 'cuts', 'above']
    for k, (n, nm, col) in enumerate(seq):
        yy = y0 + k * (bhh + gap)
        if n == '106': f.rect(mx, yy, mw, bhh, col, '#9454AC', 6, 3.2, dash=True)
        else: f.rect(mx, yy, mw, bhh, col, '#000000', 6, 1.2)
        f.text(mx + mw / 2, yy + bhh / 2, f'[{n}] {nm}', 24, True, '#ffffff' if n == '105' else '#1f1f1d', maxw=mw - 16)
        if k < len(rel):
            ya, yb = yy + bhh, yy + bhh + gap
            f.line(mx + mw / 2, ya, mx + mw / 2, yb - 2); chip(f, mx + mw / 2, (ya + yb) / 2, rel[k], 18)
    # right: how to read it
    cx, cw = 1380, 340
    f.rect(cx, 290, cw, 400, '#f6f6f3', 'none', 10)
    for t, yy, med in (('How to read it', 332, True), ('Box = one context', 392, False), ('Arrow = one relation', 436, False), ('Later above, earlier below', 480, False),
                       ('In CRMarchaeo', 556, True), ('Context = A2 Volume Unit', 604, False), ('Cut = A3 Interface', 648, False)):
        f.text(cx + 24, yy, t, 24 if med else 22, med, '#1f1f1d' if med else MUTED, anchor='start', maxw=cw - 40)
    f.save()

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for fn in (a1, a2, a3):
        orig = Fig.save
        def save(s, orig=orig):
            s.outdir = OUT; orig(s)
        Fig.save = save
        fn()
        Fig.save = orig
