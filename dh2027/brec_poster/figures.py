"""Figures for the DH 2027 poster abstract on BREC, CIDOC CRM, HDT, and FDOx.

Builds out/fig1_chain, out/fig2_layers, out/fig3_model2 (.svg and .png, Fira Sans). Photographs are in photos/, renderings of the
reconstruction models (made with render_models.py from the GLB files of the FDOx) in renders/. Class names and hypothesis data
are copied from the BREC ontology (docs/brec.ttl of Research-Squirrel-Engineers/brick-brec, release 0.5.0).
usage: python figures.py
"""
import base64
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from PIL import Image  # noqa: E402
from fira import tw, chip_w  # noqa: E402
from svgkit import GREY, ORANGE, PURPLE, AMBER, WHITE, INK, MUTED, ON, Svg, wrap  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
HDT_BLUE = "#1d4ed8"


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def image(svg, path, x, y, w, h):
    fmt = "png" if str(path).endswith(".png") else "jpeg"
    svg.o.append(f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" preserveAspectRatio="xMidYMid meet" '
                 f'href="data:image/{fmt};base64,{b64(path)}"/>')


def photo(svg, path, x, y, w, h):
    image(svg, path, x, y, w, h)
    svg.rect(x, y, w, h, "none", stroke="#9a9a94", sw=1, rx=0, check=False)


def fit(path, x, y, w, h):
    r = Image.open(path).size
    r = r[0] / r[1]
    ww, hh = (w, w / r) if r > w / h else (h * r, h)
    return x + (w - ww) / 2, y + (h - hh) / 2, ww, hh


def save(svg, name):
    svg.save(OUT / f"{name}.svg")
    import resvg_py  # type: ignore
    fonts = [str(HERE / "fonts" / n) for n in ("FiraSans-Regular.ttf", "FiraSans-Medium.ttf")]
    (OUT / f"{name}.png").write_bytes(bytes(resvg_py.svg_to_bytes(svg_path=str(OUT / f"{name}.svg"), background="#ffffff",
                                                               skip_system_fonts=True, font_files=fonts, zoom=2.0)))


# ---------------------------------------------------------------- Fig. 1: the chain
def fig1():
    W, H, SW, GAP, M = 2400, 800, 370, 110, 55
    svg = Svg(W, H)
    X0 = [M + i * (SW + GAP) for i in range(5)]
    XC = [x + SW / 2 for x in X0]
    heads = [("1 Capture", "Photographs and SfM scan"), ("2 Reconstruction", "Idealised bricks, assumptions logged"),
             ("3 Interpretation", "What does it represent?"), ("4 FDOx package", "One citable object per model"),
             ("5 Ecosystem", "Federated knowledge graphs")]
    for x, (t, s) in zip(XC, heads):
        svg.text(x, 36, t, 27, True, INK, "middle", maxw=SW + 60)
        svg.text(x, 70, s, 15, False, MUTED, "middle", maxw=SW + 60)
    DT, DB = 100, 500
    for x in X0:
        svg.rect(x, DT, SW, DB - DT, "#fbfbf9", stroke="#d8d6ce", check=False)
    PW, PH = 172, 210
    for k, sub in enumerate(["Galaxy S26, 69 photos", "Galaxy A71, 115 photos"]):
        x = X0[0] + 12 + k * (PW + 4)
        photo(svg, HERE / "photos" / f"model{k + 1}.jpg", x, DT + 18, PW, PH)
        svg.text(x + PW / 2, DT + 18 + PH + 22, f"Model {k + 1}", 16, True, INK, "middle", maxw=PW)
        svg.text(x + PW / 2, DT + 18 + PH + 44, sub, 13, False, MUTED, "middle", maxw=PW + 6)
    for j, t in enumerate(["Self-built LEGO® pyramids by", "Florian Thiery and Daria Stefan;", "SfM with the KIRI Engine"]):
        svg.text(XC[0], DT + 330 + j * 22, t, 15, False, INK, "middle", maxw=SW - 10)
    for k in (1, 2):
        p = HERE / "renders" / f"model{k}_reconstruction.png"
        image(svg, p, *fit(p, X0[1] + 12 + (k - 1) * (PW + 4), DT + 18, PW, PH))
        x = X0[1] + 12 + (k - 1) * (PW + 4)
        svg.text(x + PW / 2, DT + 18 + PH + 22, f"Model {k}", 16, True, INK, "middle", maxw=PW)
        svg.text(x + PW / 2, DT + 18 + PH + 44, "white and grey bricks" if k == 1 else "151 bricks", 13, False, MUTED, "middle", maxw=PW + 6)
    for j, t in enumerate(["Scripts rebuild each pyramid", "from bricks; every assumption", "is documented"]):
        svg.text(XC[1], DT + 330 + j * 22, t, 15, False, INK, "middle", maxw=SW - 10)
    svg.text(XC[2], DT + 24, "Hypotheses for Model 2", 17, True, INK, "middle", maxw=SW - 40)
    for k, (t, c, st) in enumerate([("Maya step pyramid", "0.70", "confirmed by the builder"), ("El Castillo", "0.35", "not confirmed")]):
        y = DT + 46 + k * 88
        svg.rect(X0[2] + 40, y, SW - 80, 78, PURPLE, name="h" + t)
        for j, (tt, sz, md) in enumerate([(t, 17, True), (f"confidence {c} (AI estimate)", 14, False), (st, 13, False)]):
            svg.text(XC[2], y + 17 + j * 22, tt, sz, md, "#fff", "middle", maxw=SW - 100)
    svg.rect(X0[2] + 40, DT + 226, SW - 80, 56, WHITE, name="m1")
    svg.text(XC[2], DT + 243, "Model 1: four hypotheses, all open", 15, True, INK, "middle", maxw=SW - 90)
    svg.text(XC[2], DT + 265, "status stays a conjecture", 13, False, MUTED, "middle", maxw=SW - 100)
    for j, t in enumerate(["Named agent: Claude Sonnet 5.5", "Evidence, Wikidata candidates,", "builder confirms or not"]):
        svg.text(XC[2], DT + 316 + j * 24, t, 15, False, INK, "middle", maxw=SW - 10)
    items = [("RO-Crate", "ro-crate-metadata.json describes every part"), ("3D model", "GLB, scan and reconstruction"),
             ("Photographs", "reference images"), ("RDF", "CRM, HDT, BREC statements"),
             ("Metadata", "MD.cff and CITATION.cff"), ("Identifiers", "Zenodo DOI, Sketchfab")]
    for k, (t, s) in enumerate(items):
        y = DT + 10 + k * 64
        svg.rect(X0[3] + 25, y, SW - 50, 54, ORANGE, stroke="#000", sw=(3.5 if k == 0 else 1.2), name="f" + t)
        svg.text(XC[3], y + 18, t, 16, True, "#fff", "middle", maxw=SW - 60)
        svg.text(XC[3], y + 38, s, 13, False, "#fff", "middle", maxw=SW - 60)
    items = [("Wikidata", "places, brick types, candidates"), ("SquirrelBase", "FDOx harvested as RDF"),
             ("Other graphs", "federated SPARQL"), ("Anyone", "re-uses, cites, disagrees")]
    for k, (t, s) in enumerate(items):
        y = DT + 22 + k * 92
        svg.rect(X0[4] + 25, y, SW - 50, 76, WHITE, name="e" + t)
        svg.text(XC[4], y + 26, t, 17, True, INK, "middle", maxw=SW - 60)
        svg.text(XC[4], y + 50, s, 13, False, MUTED, "middle", maxw=SW - 60)
    for i, chip in enumerate(["reconstructed", "interpreted", "packaged", "federated"]):
        a, b = (X0[i] + SW + 6, 300), (X0[i + 1] - 6, 300)
        svg.arrow([a, b])
        svg.chip((a[0] + b[0]) / 2, 300, chip)
    ST = DB + 24
    for i, (fill, head, line) in enumerate([
            (GREY, "Measured", "HC6 Imagery, D2 Digitization Process, HC7 3D Model (SfM scan), E16 Measurement"),
            (AMBER, "Assumed", "I2 Belief (for example seven levels), D7 Digital Machine Event, E39 Actor (the AI agent)"),
            (PURPLE, "Interpreted by AI", "I5 Inference Making and I2 Belief, with evidence, confidence 0 to 1, and a status"),
            (ORANGE, "Packaged", "brec:FDOx as dcat:Dataset in an RO-Crate, linked to the HC3 Heritage Digital Twin"),
            (WHITE, "Queried", "Statements stay separate in SPARQL: what was measured, assumed, or interpreted")]):
        svg.block(X0[i], ST, SW, 104, [line], fill, head=head, size=16, pad=12)
    LY = ST + 104 + 22

    def bar(i0, i1, y, text, fill):
        x, w = X0[i0], X0[i1] + SW - X0[i0]
        svg.rect(x, y, w, 40, fill, name=text[:20])
        svg.text(x + w / 2, y + 21, text, 16, True, INK, "middle", maxw=w - 20)
    bar(0, 4, LY, "Generic layer: CIDOC CRM, CRMdig, CRMinf, and the Heritage Digital Twin ontology (HDT)", WHITE)
    bar(0, 2, LY + 50, "Brick-specific layer: BREC (23 classes, 16 properties) and MBO (parts and colours)", GREY)
    bar(3, 4, LY + 50, "FDOx: RO-Crate, fdo-3d-packager, and fdo-squirrel", GREY)
    svg.legend([(GREY, "measured / extension"), (AMBER, "assumed"), (PURPLE, "interpreted by AI"), (ORANGE, "FDOx package"),
                (WHITE, "ecosystem or generic layer")], 55, H - 40)
    save(svg, "fig1_chain")


def icon(svg, k, x, y, n):
    """Small picture in a column head: photograph, reconstruction render, thought bubble, package."""
    o = svg.o
    if k in (0, 1):
        p = (HERE / "photos" / "model2.jpg" if k == 0 else HERE / "renders" / "model2_reconstruction.png")
        fx, fy, fw, fh = fit(p, x, y, n, n)
        image(svg, p, fx, fy, fw, fh)
        o.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" fill="none" stroke="#000" stroke-width="1"/>')
    elif k == 2:
        o.append(f'<ellipse cx="{x + n * .5}" cy="{y + n * .4}" rx="{n * .46}" ry="{n * .34}" fill="#fff" stroke="#000" stroke-width="1.4"/>'
                 f'<circle cx="{x + n * .2}" cy="{y + n * .82}" r="{n * .07}" fill="#fff" stroke="#000" stroke-width="1.2"/>'
                 f'<circle cx="{x + n * .08}" cy="{y + n * .94}" r="{n * .04}" fill="#fff" stroke="#000" stroke-width="1.2"/>'
                 f'<text x="{x + n * .5}" y="{y + n * .42}" text-anchor="middle" dominant-baseline="central" font-size="{n * .5}" font-weight="500" fill="#000">?</text>')
    else:
        cx, cy, a = x + n / 2, y + n * .5, n * .44
        top = f"{cx},{cy - a} {cx + a * .87},{cy - a * .5} {cx},{cy} {cx - a * .87},{cy - a * .5}"
        left = f"{cx - a * .87},{cy - a * .5} {cx},{cy} {cx},{cy + a} {cx - a * .87},{cy + a * .5}"
        right = f"{cx + a * .87},{cy - a * .5} {cx},{cy} {cx},{cy + a} {cx + a * .87},{cy + a * .5}"
        for pts, f in ((top, "#fff"), (left, "#e5e5e0"), (right, "#c9c9c2")):
            o.append(f'<polygon points="{pts}" fill="{f}" stroke="#000" stroke-width="1.3" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- Fig. 2: layers and statement types
def fig2():
    cols = [("Measured", "what capture and SfM produced", GREY, [
                (("D2 Digitization Process", "CRMdig"), ("ScanDigitization", "brec: imageCount, captureDevice")),
                (("E16 Measurement", "CIDOC CRM"), ("AlignmentAndMeasurement", "brec: grid, brick height")),
                (("HC7 3D Model", "HDT and D1 Digital Object"), ("RawScan", "brec: SfM scan"))]),
            ("Assumed", "each reconstruction decision", AMBER, [
                (("D7 Digital Machine Event", "CRMdig"), ("ProceduralReconstruction", "brec: usesAssumption, usesScript")),
                (("I2 Belief", "CRMinf"), ("Assumption", "brec: confidence, confidenceBasis")),
                (("HC7 3D Model", "HDT and D1 Digital Object"), ("ReconstructionModel", "brec: GLB, knownDeviation"))]),
            ("Interpreted by AI", "what the object is proposed to be", PURPLE, [
                (("I5 Inference Making", "CRMinf"), ("Identification", "brec: also E17 Type Assignment")),
                (("I2 Belief", "CRMinf"), ("IdentityHypothesis", "brec: confidence, verificationStatus")),
                (("I4 Proposition Set", "CRMinf"), ("Evidence", "brec: supports, weakens"))]),
            ("Packaged", "the citable object", ORANGE, [
                (("D1 Digital Object", "CRMdig and dcat:Dataset"), ("FDOx", "brec: Zenodo record")),
                (("HC3 Heritage Digital Twin", "HDT"), ("BrickModelTwin", "brec: hdt:has_digital_twin")),
                (("HC16 Tangible Asset", "HDT and E22 Human-Made Object"), ("BrickModel", "brec: builtBy"))])]
    SW, GAP, M, BW, BH = 440, 50, 55, 380, 58
    W = M * 2 + 4 * SW + 3 * GAP
    ROW, PAIR = 218, 3
    H = 130 + PAIR * ROW + 90
    svg = Svg(W, H)
    for c, (head, sub, fill, pairs) in enumerate(cols):
        x0 = M + c * (SW + GAP)
        svg.rect(x0, 20, SW, 72, fill, name="head" + head)
        icon(svg, c, x0 + 16, 28, 56)
        svg.text(x0 + SW / 2 + 36, 45, head, 24, True, ON[fill], "middle", maxw=SW - 100)
        svg.text(x0 + SW / 2 + 36, 70, sub, 14, False, ON[fill], "middle", maxw=SW - 100)
        for r, (gen, brec) in enumerate(pairs):
            xb = x0 + (SW - BW) / 2
            yg = 120 + r * ROW
            yb = yg + BH + 58
            hdt = gen[1].startswith("HDT")
            for (t, s), y, kind in ((gen, yg, "gen"), (brec, yb, "brec")):
                svg.rect(xb, y, BW, BH, fill, name=f"{c}{r}{kind}")
                svg.text(xb + BW / 2, y + 20, t, 16, True, ON[fill], "middle", maxw=BW - 16)
                svg.text(xb + BW / 2, y + 40, s, 13, False, ON[fill], "middle", maxw=BW - 16)
            a, b = (xb + BW / 2, yb - 3), (xb + BW / 2, yg + BH + 3)
            svg.arrow([a, b], marker="g")
            svg.chip(a[0], (a[1] + b[1]) / 2, "subClassOf")
    svg.text(M, H - 40, "Upper box of each pair: class of the CIDOC CRM family or of the Heritage Digital Twin ontology (HDT). Lower box: the BREC class "
             "that extends it. Arrow with a hollow head: the lower class is a subclass of the upper one.", 15, False, MUTED, maxw=W - 2 * M)
    save(svg, "fig2_layers")


# ---------------------------------------------------------------- Fig. 3: Model 2
def fig3():
    W, H = 2400, 940
    svg = Svg(W, H)
    P0, PY, PWD, PHT = 740, 110, 600, 732
    LW = 620
    svg.text(55 + LW / 2, 34, "Statements about Model 2", 30, True, INK, "middle", maxw=LW)
    svg.text(55 + LW / 2, 70, "measured, assumed, reconstructed", 19, False, MUTED, "middle", maxw=LW)
    svg.text(P0 + PWD / 2, 34, "Photograph", 30, True, INK, "middle", maxw=PWD)
    svg.text(P0 + PWD / 2, 70, "Daria Stefan, Galaxy A71, 115 photos", 19, False, MUTED, "middle", maxw=PWD)
    TX, TW_ = 1500, 860
    svg.text(TX + TW_ / 2, 34, "Interpreted by Claude", 30, True, INK, "middle", maxw=TW_)
    svg.text(TX + TW_ / 2, 70, "result of a SPARQL query over the FDOx RDF", 19, False, MUTED, "middle", maxw=TW_)
    photo(svg, HERE / "photos" / "model2.jpg", P0, PY, PWD, PHT)

    def pt(ox, oy):   # original photograph (810 x 1080) to the figure
        return P0 + (ox - 12) * PWD / 787, PY + (oy - 120) * PWD / 787
    callouts = [
        (ORANGE, "Reconstructed: temple", "Four courses: grey 4 x 4, four white 1 x 1 pillars (hollow), grey lintel", pt(410, 500)),
        (AMBER, "Assumed: hidden bricks", "Inner distribution of the bricks is estimated, not read from the scan", pt(410, 700)),
        (AMBER, "Assumed: seven levels", "According to the photo and the builder; the scan suggests eight levels", pt(190, 740)),
        (GREY, "Measured: scan distorted", "Compressed along one axis (about factor 0.72); ground rises towards the pyramid", pt(300, 900)),
        (GREY, "Measured: capture", "115 photographs, Samsung Galaxy A71, KIRI Engine (structure from motion)", (P0, PY + PHT - 50)),
    ]
    for i, (fill, head, line, target) in enumerate(callouts):
        y = 110 + i * 146
        svg.block(55, y, LW, 128, [line], fill, head=head, size=23, pad=16)
        svg.arrow([(55 + LW, y + 64), (target[0] - 2, target[1])], head=False, dot=True, sw=1.3)

    rows = [("Mesoamerican (Maya) step pyramid with a temple on top", "0.70", "confirmed by the builder, 17 Nov 2026", "none yet"),
            ("El Castillo at Chichén Itzá (special case of the first)", "0.35", "not confirmed by the builder", "none yet"),
            ("Free design without a specific model", "0.15", "open", "none yet"),
            ("Angkor temple mountain with sanctuary", "0.10", "open", "Q788982"),
            ("Ziggurat with temple", "0.08", "open", "Q170153")]
    cx = [TX + 18, TX + 440, TX + 545, TX + 770]
    HH, RH = 60, 104

    def mtext(x, cy, lines, size, med, fill=INK, anchor="start", maxw=None):
        lh = size * 1.25
        for j, ln in enumerate(lines):
            svg.text(x, cy + (j - (len(lines) - 1) / 2) * lh, ln, size, med, fill, anchor, maxw=maxw)
    svg.rect(TX, 110, TW_, HH, PURPLE, name="thead")
    for x, t in zip([cx[0], cx[1] - 24, cx[2], cx[3]], ["Hypothesis", "Confidence", "Status", "Wikidata"]):
        svg.text(x, 110 + HH / 2, t, 19, True, "#fff", "start", maxw=250)
    for i, (h, c, st, w) in enumerate(rows):
        y = 110 + HH + i * RH
        cy = y + RH / 2
        svg.rect(TX, y, TW_, RH, WHITE, name=f"row{i}")
        mtext(cx[0], cy, wrap(h, 20, 390, i == 0), 20, i == 0, maxw=400)
        mtext(cx[1] + 24, cy, [c], 23, True, maxw=90)
        mtext(cx[2], cy, wrap(st, 18, 210, i == 0), 18, i == 0, maxw=215)
        mtext(cx[3], cy, [w], 18, False, MUTED if w == "none yet" else INK, maxw=90)
    my = 110 + HH + 5 * RH + 24
    svg.block(TX, my, TW_, 842 - my, ["Model 1 has four hypotheses, all open; the best is a monument with a warrior statue on a column (0.55). "
                                      "Confidence is the AI's own estimate, not a measurement."], GREY, head="Model 1 and the limits", size=22, pad=16)
    a, b = (P0 + PWD + 8, 470), (TX - 8, 470)
    svg.arrow([a, b])
    svg.chip((a[0] + b[0]) / 2, 470, "interpreted", 16)
    svg.legend([(GREY, "measured"), (AMBER, "assumed"), (ORANGE, "reconstructed"), (PURPLE, "interpreted by AI")], 55, H - 44, 17)
    save(svg, "fig3_model2")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
