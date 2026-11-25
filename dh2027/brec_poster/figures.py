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
    for k, (t, c, s) in enumerate([("Maya step pyramid", "0.70", "confirmed by the builder"), ("El Castillo", "0.35", "not confirmed")]):
        y = DT + 20 + k * 92
        svg.rect(X0[2] + 40, y, SW - 80, 78, PURPLE, name="h" + t)
        svg.text(XC[2], y + 20, t, 17, True, "#fff", "middle", maxw=SW - 100)
        svg.text(XC[2], y + 42, f"confidence {c} (AI estimate)", 14, False, "#fff", "middle", maxw=SW - 100)
        svg.text(XC[2], y + 62, s, 13, False, "#fff", "middle", maxw=SW - 100)
    svg.rect(X0[2] + 40, DT + 204, SW - 80, 50, WHITE, name="m1")
    svg.text(XC[2], DT + 222, "Model 1: still open", 15, True, INK, "middle", maxw=SW - 100)
    svg.text(XC[2], DT + 242, "status stays a conjecture", 13, False, MUTED, "middle", maxw=SW - 100)
    for j, t in enumerate(["Named agent: Claude Sonnet 5.5", "Evidence, Wikidata candidates,", "builder confirms or not"]):
        svg.text(XC[2], DT + 290 + j * 24, t, 15, False, INK, "middle", maxw=SW - 10)
    items = [("RO-Crate", "ro-crate-metadata.json describes every part"), ("3D model", "GLB, scan and reconstruction"),
             ("Photographs", "reference images"), ("RDF", "CRM, HDT, BREC statements"),
             ("Metadata", "MD.cff and CITATION.cff"), ("Identifiers", "Zenodo DOI, Sketchfab")]
    for k, (t, s) in enumerate(items):
        y = DT + 10 + k * 64
        svg.rect(X0[3] + 25, y, SW - 50, 54, ORANGE, stroke="#000", sw=(3.5 if k == 0 else 1.2), name="f" + t)
        svg.text(XC[3], y + 19, t, 16, True, "#fff", "middle", maxw=SW - 60)
        svg.text(XC[3], y + 39, s, 13, False, "#fff", "middle", maxw=SW - 60)
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
        svg.text(x0 + SW / 2, 44, head, 24, True, ON[fill], "middle", maxw=SW - 20)
        svg.text(x0 + SW / 2, 72, sub, 14, False, ON[fill], "middle", maxw=SW - 20)
        for r, (gen, brec) in enumerate(pairs):
            xb = x0 + (SW - BW) / 2
            yg = 120 + r * ROW
            yb = yg + BH + 58
            hdt = gen[1].startswith("HDT")
            for (t, s), y, kind in ((gen, yg, "gen"), (brec, yb, "brec")):
                st, sw = (HDT_BLUE, 4) if (kind == "gen" and hdt) else ("#000", 1.2)
                svg.rect(xb, y, BW, BH, fill, stroke=st, sw=sw, name=f"{c}{r}{kind}")
                svg.text(xb + BW / 2, y + 21, t, 16, True, ON[fill], "middle", maxw=BW - 16)
                svg.text(xb + BW / 2, y + 42, s, 13, False, ON[fill], "middle", maxw=BW - 16)
            a, b = (xb + BW / 2, yb - 3), (xb + BW / 2, yg + BH + 6)
            svg.arrow([a, b])
            svg.chip(a[0], (a[1] + b[1]) / 2, "subClassOf")
    svg.text(M, H - 52, "Upper box of each pair: class of the CIDOC CRM family or of HDT (blue outline). Lower box: the brick-specific class of BREC "
             "that extends it.", 15, False, MUTED, maxw=W - 2 * M)
    svg.legend([(GREY, "measured"), (AMBER, "assumed"), (PURPLE, "interpreted by AI"), (ORANGE, "packaged")], M, H - 28)
    save(svg, "fig2_layers")


# ---------------------------------------------------------------- Fig. 3: Model 2
def fig3():
    W, H = 2400, 900
    svg = Svg(W, H)
    P0, PY, PWD, PHT = 760, 100, 600, 732
    svg.text(375, 36, "Statements about Model 2", 25, True, INK, "middle", maxw=640)
    svg.text(375, 68, "measured, assumed, reconstructed", 15, False, MUTED, "middle", maxw=640)
    svg.text(P0 + PWD / 2, 36, "Photograph", 25, True, INK, "middle", maxw=PWD)
    svg.text(P0 + PWD / 2, 68, "Daria Stefan, Galaxy A71, 115 photos", 15, False, MUTED, "middle", maxw=PWD)
    svg.text(1920, 36, "Interpreted by Claude", 25, True, INK, "middle", maxw=860)
    svg.text(1920, 68, "result of a SPARQL query over the FDOx RDF", 15, False, MUTED, "middle", maxw=860)
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
        y = 110 + i * 130
        svg.block(55, y, 640, 110, [line], fill, head=head, size=17, pad=14)
        svg.arrow([(695, y + 55), (target[0] - 2, target[1])], head=False, dot=True, sw=1.3)

    rows = [("Mesoamerican (Maya) step pyramid with a temple on top", "0.70", "confirmed by the builder, 17 Nov 2026", "none yet"),
            ("El Castillo at Chichén Itzá (special case of the first)", "0.35", "not confirmed by the builder", "none yet"),
            ("Free design without a specific model", "0.15", "open", "none yet"),
            ("Angkor temple mountain with sanctuary", "0.10", "open", "Q788982"),
            ("Ziggurat with temple", "0.08", "open", "Q170153")]
    TX, TW_ = 1480, 880
    cx = [TX + 14, TX + 440, TX + 540, TX + 790]
    svg.rect(TX, 100, TW_, 56, PURPLE, name="thead")
    for x, t in zip(cx, ["Hypothesis", "Confidence", "Status", "Wikidata"]):
        svg.text(x, 128, t, 16, True, "#fff", "start", maxw=250)
    for i, (h, c, s, w) in enumerate(rows):
        y = 156 + i * 92
        svg.rect(TX, y, TW_, 92, WHITE, name=f"row{i}")
        for j, ln in enumerate(wrap(h, 15, 410, i == 0)):
            svg.text(cx[0], y + 34 + j * 20, ln, 15, i == 0, INK, "start", maxw=420)
        svg.text(cx[1] + 20, y + 34, c, 18, True, INK, "start", maxw=90)
        for j, ln in enumerate(wrap(s, 14, 240, i == 0)):
            svg.text(cx[2], y + 34 + j * 20, ln, 14, i == 0, INK, "start", maxw=250)
        svg.text(cx[3], y + 34, w, 14, False, MUTED if w == "none yet" else INK, "start", maxw=90)
    svg.block(TX, 156 + 5 * 92 + 24, TW_, 100, ["Model 1 has four hypotheses, all open; the best is a monument with a warrior statue on a column (0.55). "
                                             "Confidence is the AI's own estimate, not a measurement."], GREY, head="Model 1 and the limits", size=16, pad=12)
    a, b = (P0 + PWD + 8, 470), (TX - 8, 470)
    svg.arrow([a, b])
    svg.chip((a[0] + b[0]) / 2, 470, "interpreted")
    svg.legend([(GREY, "measured"), (AMBER, "assumed"), (ORANGE, "reconstructed"), (PURPLE, "interpreted by AI")], 55, H - 40)
    save(svg, "fig3_model2")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
