"""Small SVG toolkit for the schematic figures (Fira Sans, English, amber chips centred on arrows, overlap report).

Colours follow the house scheme: instance #e2e8f0, real object #166534, class #9a3412, term #4c1d95, property/value #fbbf24.
Every text can be given a maximum width; a text that is wider raises, so nothing overflows silently.
"""
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fira import chip_w, tw  # noqa: E402

GREY, GREEN, ORANGE, PURPLE, AMBER, WHITE = "#e2e8f0", "#166534", "#9a3412", "#4c1d95", "#fbbf24", "#ffffff"
INK, MUTED = "#1f1f1d", "#55544f"
ON = {GREY: INK, AMBER: "#000000", WHITE: INK, GREEN: "#fff", ORANGE: "#fff", PURPLE: "#fff"}   # text colour on a fill


def wrap(text, size, maxw, med=False):
    """Greedy wrap by measured width."""
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if tw(t, size, med) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.o, self.boxes, self.chips, self.lines = w, h, [], [], [], []
        self.o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Fira Sans">')
        self.o.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')
        self.o.append('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#111"/></marker>'
                      '<marker id="d" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6"><circle cx="5" cy="5" r="4" fill="#111"/></marker></defs>')

    def rect(self, x, y, w, h, fill=WHITE, stroke="#000", sw=1.2, rx=6, dash=None, check=True, name=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')
        if check:
            self.boxes.append((name or f"box@{x:.0f},{y:.0f}", (x, y, w, h)))

    def text(self, x, y, t, size=13, med=False, fill=INK, anchor="start", maxw=None):
        if maxw is not None and tw(t, size, med) > maxw:
            raise ValueError(f"text too wide ({tw(t, size, med):.0f}>{maxw:.0f}): {t}")
        wt = ' font-weight="500"' if med else ""
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="central" font-size="{size}"{wt} fill="{fill}">{escape(t)}</text>')

    def block(self, x, y, w, h, lines, fill, head=None, size=13, pad=10):
        """A statement box: optional bold head line, wrapped body lines; height is given, content must fit."""
        self.rect(x, y, w, h, fill, name=(head or lines[0])[:30])
        col = ON[fill]
        yy = y + pad + size * 0.55
        if head:
            for ln in wrap(head, size, w - 2 * pad, True):
                self.text(x + pad, yy, ln, size, True, col, maxw=w - 2 * pad)
                yy += size * 1.3
        for ln in lines:
            for l2 in wrap(ln, size - 1, w - 2 * pad):
                self.text(x + pad, yy, l2, size - 1, False, col, maxw=w - 2 * pad)
                yy += (size - 1) * 1.3
        if yy - (size - 1) * 0.65 > y + h:
            raise ValueError(f"statement does not fit its box: {head or lines[0]}")

    def height_of(self, w, lines, head=None, size=13, pad=10):
        n = sum(len(wrap(l, size, w - 2 * pad, True)) for l in ([head] if head else []))
        m = sum(len(wrap(l, size - 1, w - 2 * pad)) for l in lines)
        return round(2 * pad + n * size * 1.3 + m * (size - 1) * 1.3 + 2)

    def arrow(self, pts, head=True, dot=False, color="#111", sw=1.6, dash=None, ends=()):
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        mk = (' marker-end="url(#a)"' if head else "") + (' marker-end="url(#d)"' if dot else "")
        self.o.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{ds}{mk}/>')
        self.lines.append((pts, ends))

    def chip(self, cx, cy, t, size=12):
        w = chip_w(t, size)
        self.o.append(f'<rect x="{cx - w / 2:.1f}" y="{cy - 11:.1f}" width="{w}" height="22" rx="11" fill="{AMBER}" stroke="#000" stroke-width="1.2"/>'
                      f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="central" font-size="{size}" fill="#000">{escape(t)}</text>')
        self.chips.append((t, (cx - w / 2, cy - 11, w, 22)))

    def legend(self, items, x, y, size=13):
        for col, t in items:
            self.o.append(f'<rect x="{x}" y="{y}" width="26" height="16" fill="{col}" stroke="#000"/>')
            self.text(x + 34, y + 8.5, t, size)
            x += 60 + tw(t, size)

    def report(self):
        """Overlaps between statement boxes and chips, and chips on boxes (lines may end in boxes, they are not checked here)."""
        bad = []
        def hit(a, b, m=2):
            return a[0] < b[0] + b[2] + m and b[0] < a[0] + a[2] + m and a[1] < b[1] + b[3] + m and b[1] < a[1] + a[3] + m
        for i, (n1, r1) in enumerate(self.boxes):
            for n2, r2 in self.boxes[i + 1:]:
                if hit(r1, r2, 0) and not (r1[0] <= r2[0] and r1[1] <= r2[1] and r1[0] + r1[2] >= r2[0] + r2[2] and r1[1] + r1[3] >= r2[1] + r2[3]) \
                        and not (r2[0] <= r1[0] and r2[1] <= r1[1] and r2[0] + r2[2] >= r1[0] + r1[2] and r2[1] + r2[3] >= r1[1] + r1[3]):
                    bad.append(("box-box", n1, n2))
        def seg_x(p1, p2, p3, p4):
            def o(a, b, c): return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            return o(p1, p2, p3) * o(p1, p2, p4) < 0 and o(p3, p4, p1) * o(p3, p4, p2) < 0
        segs = [(i, a, b) for i, (pts, _) in enumerate(self.lines) for a, b in zip(pts, pts[1:])]
        for k, (i, a, b) in enumerate(segs):
            for j, c, d in segs[k + 1:]:
                if i != j and seg_x(a, b, c, d):
                    bad.append(("line-line", f"line{i}", f"line{j}"))
        for i, (pts, ends) in enumerate(self.lines):
            for a, b in zip(pts, pts[1:]):
                for n, rb in self.boxes:
                    if n in ends:
                        continue
                    for t in range(1, 40):
                        q = (a[0] + (b[0] - a[0]) * t / 40, a[1] + (b[1] - a[1]) * t / 40)
                        if rb[0] < q[0] < rb[0] + rb[2] and rb[1] < q[1] < rb[1] + rb[3]:
                            bad.append(("line-box", f"line{i}", n))
                            break
        for t, r in self.chips:
            for n, rb in self.boxes:
                if hit(r, rb):
                    bad.append(("chip-box", t, n))
        for i, (t1, r1) in enumerate(self.chips):
            for t2, r2 in self.chips[i + 1:]:
                if hit(r1, r2):
                    bad.append(("chip-chip", t1, t2))
        return bad

    def save(self, path):
        self.o.append("</svg>")
        Path(path).write_text("\n".join(self.o), encoding="utf-8", newline="\n")
        print("crossings/overlaps:", sorted(set(map(str, self.report()))))
