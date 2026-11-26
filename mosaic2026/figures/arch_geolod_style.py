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

import math
def section(f, x, y, w, h, labels=True):
    """Fictional trench section in the style of the WD1 core column: many contexts, dipping and lens-shaped. Returns key points."""
    sin = math.sin; N = 60
    X = lambda u: x + u * w; Y = lambda v: y + v * h
    B1 = lambda u: .07 + .03 * u + .014 * sin(7 * u); B2 = lambda u: .16 + .06 * u + .02 * sin(5 * u + 1)
    B3 = lambda u: B2(u) + .012 + .11 * u ** 1.5
    F = lambda u: .47 + .10 * u + .012 * sin(9 * u); FB = lambda u: F(u) + .085 + .035 * sin(4 * u)
    us = [k / N for k in range(N + 1)]
    def band(top, bot, fill, u0=0, u1=1, sw=1):
        uu = [u0 + (u1 - u0) * k / N for k in range(N + 1)]
        pts = [(X(u), Y(top(u))) for u in uu] + [(X(u), Y(bot(u))) for u in reversed(uu)]
        f.raw(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}" stroke="#000000" stroke-width="{sw}" stroke-linejoin="round"/>')
    f.rect(x, y, w, h, '#b9b4aa', '#000000', 0, 1)                       # 107 natural
    band(lambda u: 0, B1, '#d9d2c3'); band(B1, B2, '#cdbfa6'); band(B2, B3, '#d8c7ad')   # 101, 102, 116
    band(B3, F, '#e6c9a8'); band(F, FB, '#f0e0b8')                        # 103, 104
    for k in range(1, 5):   # bedding in the natural and tongues in the collapse (texture only)
        for fn, off, col in ((FB, .075 * k, '#8f8b82'), (B3, .05 * k, '#c9a987')):
            if fn is B3 and off > .22: continue
            pts = [(X(u), Y(fn(u) + off + .02 * sin(3 * u + k))) for u in us if (fn is FB or Y(fn(u) + off) < Y(F(u)) - 6)]
            if len(pts) > 2: f.raw(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{col}" stroke-width="1.1" opacity=".8"/>')
    u0, u1 = .05, .27
    band(lambda u: F(u) - .045 * sin(math.pi * (u - u0) / (u1 - u0)), F, '#a9a39b', u0, u1)   # 110 ash lens
    # flecks and stipple (texture only)
    for (u, v) in ((.06, .04), (.2, .05), (.45, .03), (.7, .06), (.9, .05), (.12, .13), (.55, .12), (.85, .14), (.3, .20), (.7, .21), (.1, .70), (.25, .78), (.8, .84), (.9, .72)):
        f.raw(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="2.2" fill="#6b6a63" opacity=".55"/>')
    # wall [108]: stones on the floor
    wx0, wx1 = .80, .93; wy0 = .31; wy1 = F(.865)
    f.rect(X(wx0), Y(wy0), (wx1 - wx0) * w, Y(wy1) - Y(wy0), '#8a8a84', '#000000', 0, 1.6)
    rows = 5; rh = (Y(wy1) - Y(wy0)) / rows
    for r in range(1, rows): f.line(X(wx0), Y(wy0) + r * rh, X(wx1), Y(wy0) + r * rh, None, w=1, color='#4a4a46')
    for r in range(rows):
        off = (r % 2) * .045 * w + .02 * w
        for k in range(2): f.line(X(wx0) + off + k * .06 * w, Y(wy0) + r * rh, X(wx0) + off + k * .06 * w, Y(wy0) + (r + 1) * rh, None, w=1, color='#4a4a46')
    # pit: cut [106] with two fills [115] below and [105] above
    FL, FR = F(.36), F(.64)
    xl = lambda v: .36 + (.44 - .36) * (v - FL) / (.88 - FL); xr = lambda v: .64 - (.64 - .57) * (v - FR) / (.86 - FR)
    vb = .70
    curve = [(xl(vb) + (xr(vb) - xl(vb)) * k / 30, vb + .035 * sin(math.pi * k / 30)) for k in range(31)]
    P = lambda pts: " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in pts)
    f.raw(f'<polygon points="{P([(.36, FL), (.64, FR)] + [curve[-1]] + curve[::-1][1:] )}" fill="#a89677" stroke="none"/>')
    f.raw(f'<polygon points="{P(curve + [(.57, .86), (.44, .88)])}" fill="#6f6455" stroke="none"/>')
    f.raw(f'<polygon points="{P([(.36, FL), (.64, FR), (.57, .86), (.44, .88)])}" fill="none" stroke="#9454AC" stroke-width="3.4" stroke-linejoin="round"/>')
    # charcoal sample in the floor [104]
    cu, cv = .80, F(.80) + .04
    for dx, dy in ((0, 0), (.015, .012), (-.012, .018), (.02, -.006)):
        f.raw(f'<circle cx="{X(cu + dx):.1f}" cy="{Y(cv + dy):.1f}" r="3" fill="#1f1f1d"/>')
    if labels:
        T = lambda u, v, t, c='#1f1f1d', sz=19, med=False, anc='start': f.text(X(u), Y(v), t, sz, med, c, anchor=anc)
        T(.02, .04, '[101] topsoil'); T(.02, .13, '[102] plough soil'); T(.56, (B2(.56) + B3(.56)) / 2, '[116] levelling', sz=16); T(.02, .33, '[103] wall collapse')
        T(.02, F(.02) + .04, '[104] floor'); T(.02, .86, '[107] natural')
        T(.16, F(.16) - .02, '[110] ash', sz=16, anc='middle')
        T(.865, wy0 + (wy1 - wy0) / 2 / h * h * 0 + .075, '[108]', '#ffffff', 17, True, 'middle'); T(.865, wy0 + .115, 'wall', '#ffffff', 16, False, 'middle')
        T(.50, .62, '[105]', '#ffffff', 19, True, 'middle'); T(.50, .79, '[115]', '#ffffff', 19, True, 'middle')
        T(.69, .80, '[106] cut', '#9454AC', 21, True)
    return {'cut_pt': (X(xr(.66)), Y(.66)), 'date_pt': (X(cu), Y(cv)), 'sample_pt': (X(.84), Y(F(.84) + .085)), 'X': X, 'Y': Y}

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
    k = section(f, x, y, w, h)
    f.text(x + w / 2, 50, 'Trench 1, section A', 24, True); f.text(x + w / 2, 72, 'fictional example', 18, color=MUTED)
    def badge(bx, by, n):
        f.raw(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="15" fill="#1f1f1d"/>'); f.text(bx, by + .5, n, 19, True, '#ffffff')
    (cx_, cy_), (dx_, dy_), (sx_, sy_) = k['cut_pt'], k['date_pt'], k['sample_pt']
    f.raw(f'<circle cx="{dx_:.1f}" cy="{dy_:.1f}" r="9" fill="#ffffff" stroke="#000000" stroke-width="2"/>')
    f.rect(sx_ - 6, sy_ - 6, 12, 12, '#1f1f1d')
    f.line(dx_, dy_, sx_, sy_, None, w=1.2)
    badge(cx_ + 62, cy_, '1'); f.line(cx_ + 47, cy_, cx_ + 6, cy_, None, w=1.2)
    badge(dx_ - 34, dy_ + 28, '2'); badge(sx_ + 34, sy_ + 14, '3')
    cards = [(135, 'Interpreted', 'The pit was dug into the floor and filled later', 'ctx:context_106', 'pit cut', 'A3 Stratigraphic Interface', 'CRMarchaeo'),
             (405, 'Dated', 'Charcoal from the floor, 14C, 1610 to 1520 cal BC', 'ctx:date_104', 'floor layer [104]', 'E13 Attribute Assignment', 'CIDOC CRM'),
             (675, 'Measured', 'One 14C measurement on one sample', 'ctx:c14_CH17', 'charcoal CH-17', 'S4 Observation', 'CRMsci')]
    for yy, hd, sub, inst, isub, cl, fam in cards:
        f.rect(820, yy - 30, 900, 230, '#f6f6f3', 'none', 10)
        f.text(845, yy + 6, hd, 28, True, anchor='start'); f.text(1000, yy + 7, sub, 20, color=MUTED, anchor='start', maxw=700)
        f.box(845, yy + 55, 330, 105, inst, isub, INST, 22, 19)
        f.box(1260, yy + 55, 440, 105, cl, fam, CLS, 25, 19)
        f.line(1175, yy + 107, 1258, yy + 107); chip(f, 1217, yy + 83, 'a', 15)
    for n, (yy, *_) in zip('123', cards): badge(1704, yy + 6, n)
    f.legend(965, [(INST, 'Instance'), (CLS, 'Class')], x=820)
    f.save()

def a3():
    f = Fig('a3-harris-matrix', 'The trench section on the left, the same contexts as a Harris matrix on the right', h=900)
    x, y, w, h = 60, 118, 580, 748
    f.text(x + w / 2, 42, 'Trench section', 30, True); f.text(x + w / 2, 78, 'fictional example', 21, color=MUTED)
    section(f, x, y, w, h)
    bw, bhh, gap, y0 = 230, 44, 44, 118
    L, C, R = 775, 1020, 1265
    f.text(C, 42, 'Harris matrix', 30, True); f.text(C, 78, 'later at the top, earlier below', 21, color=MUTED)
    nodes = {'101': (C, 0, 'topsoil', '#d9d2c3'), '102': (C, 1, 'plough soil', '#cdbfa6'), '116': (C, 2, 'levelling', '#d8c7ad'), '103': (C, 3, 'collapse', '#e6c9a8'),
             '105': (L, 4, 'upper fill', '#a89677'), '108': (C, 4, 'wall', '#8a8a84'), '110': (R, 4, 'ash lens', '#a9a39b'),
             '115': (L, 5, 'lower fill', '#6f6455'), '106': (L, 6, 'pit cut', '#ffffff'), '104': (C, 7, 'floor', '#f0e0b8'), '107': (C, 8, 'natural', '#b9b4aa')}
    top = lambda n: (nodes[n][0], y0 + nodes[n][1] * (bhh + gap)); bot = lambda n: (nodes[n][0], y0 + nodes[n][1] * (bhh + gap) + bhh)
    for n, (cx, r, nm, col) in nodes.items():
        yy = y0 + r * (bhh + gap)
        if n == '106': f.rect(cx - bw / 2, yy, bw, bhh, col, '#9454AC', 6, 3.2, dash=True)
        else: f.rect(cx - bw / 2, yy, bw, bhh, col, '#000000', 6, 1.2)
        f.text(cx, yy + bhh / 2, f'[{n}] {nm}', 21, True, '#ffffff' if n in ('115',) else '#1f1f1d', maxw=bw - 14)
    for a, b, t in (('101', '102', 'above'), ('102', '116', 'above'), ('116', '103', 'above'), ('103', '105', 'above'), ('103', '108', 'above'), ('103', '110', 'above'),
                    ('105', '115', 'above'), ('115', '106', 'fills'), ('106', '104', 'cuts'), ('108', '104', 'above'), ('110', '104', 'above'), ('104', '107', 'above')):
        (xa, ya), (xb, yb) = bot(a), top(b)
        f.line(xa, ya, xb, yb - 2); chip(f, (xa + xb) / 2, (ya + yb) / 2, t, 18)
    cx, cw = 1415, 310
    f.rect(cx, 300, cw, 390, '#f6f6f3', 'none', 10)
    for t, yy, med in (('How to read it', 342, True), ('Box = one context', 398, False), ('Arrow = one relation', 440, False), ('Later above, earlier below', 482, False),
                       ('In CRMarchaeo', 552, True), ('Context = A2 Volume Unit', 604, False), ('Cut = A3 Interface', 646, False)):
        f.text(cx + 20, yy, t, 25 if med else 21, med, '#1f1f1d' if med else MUTED, anchor='start', maxw=cw - 30)
    f.save()

def a4():
    f = Fig('a4-same-pattern', 'Core, cave and trench: the same CIDOC CRM pattern, once through the geo-lod extension and once through CRMarchaeo', h=810)
    for cx, hd, sub in ((190, 'geo-lod extension', 'drill core, cave, ice core'), (650, 'geo-lod classes', 'subclasses of the CRM'), (1175, 'CIDOC CRM family', 'the shared pattern'), (1585, 'Excavation', 'CRMarchaeo, fictional')):
        f.text(cx, 40, hd, 30, True, maxw=420); f.text(cx, 76, sub, 21, color=MUTED, maxw=420)
    rows = [('wd1:unit_HBT', '86.13–86.43 m, tephra layer', 'strat:StratigraphicUnit', 'subclass of A2', 'A2', 'Stratigraphic Volume Unit', 'CRMarchaeo', 'ctx:context_104', 'floor layer'),
            ('sisal:hiatus_0420893', 'at 19.325 mm', 'geolod:GrowthHiatus', 'geo-lod class', 'A3', 'Stratigraphic Interface', 'CRMarchaeo', 'ctx:context_106', 'pit cut'),
            ('sisal:datingpoint_012773', 'U/Th at 21.05 mm', 'strat:AgeControlPoint', 'geo-lod class', 'E13', 'Attribute Assignment', 'CIDOC CRM', 'ctx:date_104', 'floor layer, 14C'),
            ('sisal:obs_d18o_0420984', '−4.78 ‰ at 97.95 mm', 'SpeleothemObservation', 'geo-lod class', 'S4', 'Observation', 'CRMsci', 'ctx:c14_CH17', 'charcoal CH-17')]
    for k, (li, ls, gc, gs, code, nm, fam, ri, rs) in enumerate(rows):
        cy = 200 + k * 160; y = cy - 54
        f.box(20, y, 340, 108, li, ls, INST, 22, 20)
        f.box(480, y, 340, 108, gc, gs, CLS, 22, 20)
        f.box(1030, y, 290, 108, code, nm, CLS, 30, 20)
        f.box(1440, y, 290, 108, ri, rs, INST, 22, 20)
        f.text(1175, y + 108 + 18, fam, 20, color=MUTED)
        f.line(360, cy, 478, cy); chip(f, 419, cy, 'a', 18)
        f.line(820, cy, 1028, cy); chip(f, 924, cy, 'rdfs:subClassOf', 19)
        f.line(1440, cy, 1322, cy); chip(f, 1381, cy, 'a', 18)
    f.legend(785, [(INST, 'Instance'), (CLS, 'Class')], x=20)
    f.save()

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for fn in (a1, a2, a3, a4):
        orig = Fig.save
        def save(s, orig=orig):
            s.outdir = OUT; orig(s)
        Fig.save = save
        fn()
        Fig.save = orig
