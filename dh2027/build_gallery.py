"""Builds docs/dh2027/index.html: the figures of the DH 2027 poster abstract (brec_poster) and of the short paper (figures), with captions and notes.
Self-contained (fonts and downsized figure copies sit next to the page), so it opens with a double click and runs on GitHub Pages (folder /docs).
  cd /d C:\\git\\figures-tmp-help\\dh2027 && pip install pillow && python build_gallery.py"""
import html, os, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, "..", "docs", "dh2027"))
E = html.escape
SECTIONS = [
    ("poster", "Poster abstract: BREC, CIDOC CRM, HDT, and FDOx", "brec_poster/out",
     "Abstract for the DH 2027 poster (Galway, 28 June to 3 July 2027), 500 to 750 words. Figures redrawn on 25 November 2026.", [
        ("fig1_chain", "Fig. 1", "From capture to the federated ecosystem",
         "Fig. 1. From capture to knowledge graph: measured, assumed, and AI-interpreted statements, packaged as FDOx.",
         ["Photographs: Florian Thiery (Model 1) and Daria Stefan (Model 2). Renderings of the reconstruction models: made from the GLB files of the FDOx records.",
          "FDOx column: RO-Crate with 3D model, photographs, RDF, metadata, and identifiers."]),
        ("fig2_layers", "Fig. 2", "Layers and statement types",
         "Fig. 2. CIDOC CRM and HDT classes with the BREC classes that extend them, by statement type.",
         ["Upper box of each pair: class of the CIDOC CRM family or of HDT (blue outline); lower box: the BREC class that extends it.",
          "Class names and properties are those of BREC 0.5.0 (docs/brec.ttl)."]),
        ("fig3_model2", "Fig. 3", "Model 2: statements and AI hypotheses",
         "Fig. 3. Model 2: statements about the object and AI hypotheses with confidence and status.",
         ["Hypotheses, confidence, and status are the values in docs/brec.ttl (instances hyp_m2_a to hyp_m2_e).",
          "The confirmed Maya hypothesis and El Castillo have no Wikidata match yet."])]),
    ("short", "Short paper: community sources and research outputs", "figures/out",
     "Figures of the DH 2027 short paper (descriptions as in the README of dh2027/figures).", [
        ("fig1_clover", "Fig. 1", "Seven-leaf clover", "The seven-leaf clover: light green community source, dark green research output, split leaf for both.", []),
        ("fig2_junctions", "Fig. 2", "Graph and terminology junctions", "Backbone with the graph junction and the terminology junction, with photograph and 3D-model preview of one stone.", []),
        ("fig3_osm_commons", "Fig. 3", "OpenStreetMap and Commons", "The two community leaves in practice: benchmark on Albert Bridge and the distribution map of 127 geotagged Commons files.", []),
        ("fig4_ogham_tei", "Fig. 4", "Ogham stones and the TEI crosswalk", "Two Ogham stones (FDOx 3D-model previews) and the crosswalk from the TEI/EpiDoc element to the Linked Open Ogham class and the CIDOC CRM / CRMtex class.", [])]),
]


def small(src, dst, width=2400):
    im = Image.open(src)
    if im.size[0] > width:
        im = im.resize((width, round(im.size[1] * width / im.size[0])), Image.LANCZOS)
    im.save(dst, optimize=True)


cards, rows = [], []
os.makedirs(os.path.join(SITE, "out"), exist_ok=True)
for key, title, folder, lead, figs in SECTIONS:
    cards.append(f'<h2 class="part" id="{key}">{E(title)}</h2><p class="sec">{E(lead)}</p>')
    for fid, num, ftitle, cap, notes in figs:
        src = os.path.join(HERE, folder, fid + ".png")
        name = f"{key}_{fid}.png"
        if os.path.exists(src):
            small(src, os.path.join(SITE, "out", name))
            img = f'<a href="out/{name}" class="zoom"><img loading="lazy" src="out/{name}" alt="{E(ftitle)}"></a>'
        else:
            img = f'<div class="empty">{E(ftitle)}<br><small>{E(folder)}/{E(fid)}.png missing</small></div>'
        ul = "<ul>" + "".join(f"<li>{E(n)}</li>" for n in notes) + "</ul>" if notes else ""
        cards.append(f'<section id="{key}-{fid}"><h3><span class="num">{E(num)}</span> {E(ftitle)}</h3><figure class="new">{img}<p class="cap">{E(cap)}</p></figure>{ul}</section>')
        rows.append(f'<tr><td><a href="#{key}-{fid}">{E(num)}</a></td><td>{E(ftitle)}</td><td>{"Poster abstract" if key == "poster" else "Short paper"}</td></tr>')
shutil.copytree(os.path.join(HERE, "brec_poster", "fonts"), os.path.join(SITE, "fonts"), dirs_exist_ok=True)
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures: DH 2027</title>
<style>
@font-face{{font-family:"Fira Sans";src:url("fonts/FiraSans-Regular.ttf");font-weight:400}}@font-face{{font-family:"Fira Sans";src:url("fonts/FiraSans-Medium.ttf");font-weight:500}}
:root{{--ink:#1f1f1d;--mut:#55544f;--bg:#f6f4ee;--card:#fff;--line:#d4d4d0;--acc:#9a3412}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.5 "Fira Sans",system-ui,sans-serif}}
header{{padding:28px 32px 8px;max-width:1500px;margin:0 auto}}h1{{font-weight:500;margin:0 0 4px;font-size:28px}}.meta{{color:var(--mut);font-size:15px}}
main{{max-width:1500px;margin:0 auto;padding:0 32px 60px}}table{{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:16px 0 8px}}
td{{padding:8px 12px;border-bottom:1px solid var(--line)}}tr:last-child td{{border-bottom:0}}a{{color:var(--acc)}}
h2.part{{font-weight:500;font-size:24px;margin:34px 0 0}}.sec{{color:var(--mut);margin:2px 0 14px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:0 0 26px}}h3{{font-weight:500;font-size:21px;margin:0 0 10px}}.num{{background:#000;color:#fff;border-radius:6px;padding:2px 10px;font-size:17px;margin-right:6px}}
figure{{margin:0;background:#fff;border:1px solid #c2410c;border-radius:10px;padding:10px}}figure img{{width:100%;height:auto;display:block;border-radius:4px}}
.cap{{font-size:15px;color:var(--mut);margin:8px 0 0}}.empty{{border:2px dashed var(--line);border-radius:8px;padding:60px 20px;text-align:center;color:var(--mut)}}ul{{margin:12px 0 0;color:var(--mut)}}
#lb{{position:fixed;inset:0;background:rgba(0,0,0,.88);display:none;align-items:center;justify-content:center;z-index:9;cursor:zoom-out;overflow:auto}}#lb img{{max-width:96vw;max-height:96vh;background:#fff}}
</style></head><body>
<header><h1>DH 2027: figures for the poster abstract and the short paper</h1><div class="meta">Working page, November 2026. Click an image to enlarge, Esc or click to close. Sources and scripts: dh2027/brec_poster and dh2027/figures.</div></header>
<main><table><tr><td><b>No.</b></td><td><b>Figure</b></td><td><b>Work</b></td></tr>{"".join(rows)}</table>
{"".join(cards)}</main>
<div id="lb"><img alt=""></div>
<script>const lb=document.getElementById('lb'),li=lb.querySelector('img');document.querySelectorAll('a.zoom').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();li.src=a.href;lb.style.display='flex'}}));lb.addEventListener('click',()=>lb.style.display='none');document.addEventListener('keydown',e=>{{if(e.key==='Escape')lb.style.display='none'}});</script>
</body></html>'''
open(os.path.join(SITE, "index.html"), "w", encoding="utf8").write(page)
print("wrote", os.path.join(SITE, "index.html"), len(page) // 1024, "KB")
