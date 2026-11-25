"""Builds docs/derse26_geographs/index.html (repository root): all figures of the paper, old next to new, with captions and notes.
The page is self-contained (fonts, old and new images are copied next to it), so it opens with a double click and runs on GitHub Pages (folder /docs).
Reads figures.yaml and captions.yaml; images come from gallery/old/ (downsized copies of the submitted figures) and out/ (new figures).
  cd /d C:\\git\\wikibase-static-help\\deRSE26\\figures && pip install pyyaml && python build_gallery.py"""
import html, os, shutil, yaml
HERE = os.path.dirname(os.path.abspath(__file__))
F = yaml.safe_load(open(os.path.join(HERE, 'figures.yaml'), encoding='utf8'))
C = yaml.safe_load(open(os.path.join(HERE, 'captions.yaml'), encoding='utf8'))
E = html.escape
STATUS = {'done': ('new figure ready', '#166534'), 'todo': ('to do', '#9a3412'), 'keep': ('keep as submitted', '#55544f'), 'waiting': ('waiting for data', '#b45309')}
def img(path, alt, cls=''):
    if not os.path.exists(os.path.join(HERE, path)): return f'<div class="empty">{E(alt)}<br><small>{E(path)} missing</small></div>'
    return f'<a href="{path}" class="zoom {cls}"><img loading="lazy" src="{path}" alt="{E(alt)}"></a>'
def chip(s): t, c = STATUS[s]; return f'<span class="chip" style="background:{c}">{t}</span>'
def notes(ns): return '<ul>' + ''.join(f'<li>{E(n)}</li>' for n in ns) + '</ul>' if ns else ''
cards = []
for fg in F['figures']:
    new = fg.get('new'); nc = C.get(new, {}).get('caption', '') if new else ''
    left = f'<figure><figcaption>Submitted</figcaption>{img("gallery/old/" + os.path.splitext(fg["old"])[0] + ".jpg", fg["title"])}<p class="cap">{E(fg["caption_old"])}</p></figure>'
    right = (f'<figure class="new"><figcaption>New</figcaption>{img("out/" + new + ".png", fg["title"])}<p class="cap">{E(" ".join(nc.split()))}</p></figure>' if new else
             '<figure class="new none"><figcaption>New</figcaption><div class="empty">no new version yet</div></figure>')
    cards.append(f'<section id="fig{fg["n"]}"><h2><span class="num">Fig. {fg["n"]}</span> {E(fg["title"])} {chip(fg["status"])}</h2><p class="sec">{E(fg["section"])}</p><div class="pair">{left}{right}</div>{notes(fg.get("notes"))}</section>')
for ad in F['additions']:
    nc = C.get(ad['new'], {}).get('caption', '')
    cards.append(f'<section id="{ad["id"]}"><h2><span class="num">New {ad["id"].upper()}</span> {E(ad["title"])} {chip(ad["status"])}</h2><p class="sec">{E(ad["section"])}</p><div class="pair single"><figure class="new">{img("out/" + ad["new"] + ".png", ad["title"])}<p class="cap">{E(" ".join(nc.split()))}</p></figure></div>{notes(ad.get("notes"))}</section>')
for u in F.get('unused', []):
    cards.append(f'<section id="unused"><h2><span class="num">Not used</span> {E(u["title"])}</h2><div class="pair single"><figure>{img("gallery/old/" + os.path.splitext(u["old"])[0] + ".jpg", u["title"])}</figure></div>{notes(u.get("notes"))}</section>')
rows = ''.join(f'<tr><td><a href="#fig{g["n"]}">Fig. {g["n"]}</a></td><td>{E(g["title"])}</td><td>{E(g["section"])}</td><td>{chip(g["status"])}</td></tr>' for g in F['figures'])
rows += ''.join(f'<tr><td><a href="#{a["id"]}">{a["id"].upper()}</a></td><td>{E(a["title"])}</td><td>{E(a["section"])}</td><td>{chip(a["status"])}</td></tr>' for a in F['additions'])
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures: From Relations to Graphs</title>
<style>
@font-face{{font-family:"Fira Sans";src:url("fonts/FiraSans-400.ttf");font-weight:400}}@font-face{{font-family:"Fira Sans";src:url("fonts/FiraSans-500.ttf");font-weight:500}}
:root{{--ink:#1f1f1d;--mut:#55544f;--bg:#f6f4ee;--card:#fff;--line:#d4d4d0;--acc:#9a3412}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.5 "Fira Sans",system-ui,sans-serif}}
header{{padding:28px 32px 8px;max-width:1500px;margin:0 auto}}h1{{font-weight:500;margin:0 0 4px;font-size:28px}}.meta{{color:var(--mut);font-size:15px}}
main{{max-width:1500px;margin:0 auto;padding:0 32px 60px}}table{{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:16px 0 28px}}
td{{padding:8px 12px;border-bottom:1px solid var(--line);vertical-align:middle}}tr:last-child td{{border-bottom:0}}a{{color:var(--acc)}}
section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:0 0 26px}}h2{{font-weight:500;font-size:22px;margin:0}}.num{{background:#000;color:#fff;border-radius:6px;padding:2px 10px;font-size:18px;margin-right:6px}}
.sec{{color:var(--mut);margin:2px 0 14px}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.pair.single{{grid-template-columns:1fr}}figure{{margin:0;background:#fbfaf6;border:1px solid var(--line);border-radius:10px;padding:10px}}
figure.new{{border-color:#c2410c;background:#fff}}figcaption{{font-weight:500;color:var(--mut);margin-bottom:6px}}figure img{{width:100%;height:auto;display:block;border-radius:4px}}
.cap{{font-size:14px;color:var(--mut);margin:8px 0 0}}.empty{{border:2px dashed var(--line);border-radius:8px;padding:60px 20px;text-align:center;color:var(--mut)}}
.chip{{color:#fff;border-radius:12px;padding:1px 10px;font-size:14px;margin-left:8px;vertical-align:middle}}ul{{margin:12px 0 0;color:var(--mut)}}
#lb{{position:fixed;inset:0;background:rgba(0,0,0,.88);display:none;align-items:center;justify-content:center;z-index:9;cursor:zoom-out;overflow:auto}}#lb img{{max-width:96vw;max-height:96vh;background:#fff}}
@media(max-width:900px){{.pair{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>From Relations to Graphs: figures, submitted and new</h1><div class="meta">deRSE26 / ECEASST, revision of November 2026. Click an image to enlarge, Esc or click to close.</div></header>
<main><table><tr><td><b>No.</b></td><td><b>Figure</b></td><td><b>Section</b></td><td><b>Status</b></td></tr>{rows}</table>
{''.join(cards)}</main>
<div id="lb"><img alt=""></div>
<script>const lb=document.getElementById('lb'),li=lb.querySelector('img');document.querySelectorAll('a.zoom').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();li.src=a.href;lb.style.display='flex'}}));lb.addEventListener('click',()=>lb.style.display='none');document.addEventListener('keydown',e=>{{if(e.key==='Escape')lb.style.display='none'}});</script>
</body></html>'''
SITE = os.path.abspath(os.path.join(HERE, '..', '..', 'docs', 'derse26_geographs'))
os.makedirs(SITE, exist_ok=True)
shutil.copytree(os.path.join(HERE, 'fonts'), os.path.join(SITE, 'fonts'), dirs_exist_ok=True)
shutil.copytree(os.path.join(HERE, 'gallery', 'old'), os.path.join(SITE, 'gallery', 'old'), dirs_exist_ok=True)
os.makedirs(os.path.join(SITE, 'out'), exist_ok=True)
for fn in os.listdir(os.path.join(HERE, 'out')):
    if fn.endswith('.png'): shutil.copy2(os.path.join(HERE, 'out', fn), os.path.join(SITE, 'out', fn))
open(os.path.join(SITE, 'index.html'), 'w', encoding='utf8').write(page)
open(os.path.join(SITE, '..', '.nojekyll'), 'w').close()
n_new = sum(1 for g in F['figures'] if g.get('new')) + len(F['additions'])
n_all = len(F['figures']) + len(F['additions'])
start = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figures: help pages</title>
<style>
@font-face{{font-family:"Fira Sans";src:url("derse26_geographs/fonts/FiraSans-400.ttf");font-weight:400}}@font-face{{font-family:"Fira Sans";src:url("derse26_geographs/fonts/FiraSans-500.ttf");font-weight:500}}
:root{{--ink:#1f1f1d;--mut:#55544f;--bg:#f6f4ee;--card:#fff;--line:#d4d4d0;--acc:#9a3412}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.5 "Fira Sans",system-ui,sans-serif}}
main{{max-width:900px;margin:0 auto;padding:48px 24px 60px}}h1{{font-weight:500;font-size:30px;margin:0 0 6px}}p.lead{{color:var(--mut);margin:0 0 28px}}
a.card{{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;color:inherit;text-decoration:none}}a.card:hover{{border-color:var(--acc)}}
a.card img{{width:100%;display:block;border-bottom:1px solid var(--line)}}.body{{padding:16px 20px 18px}}h2{{font-weight:500;font-size:22px;margin:0 0 4px}}.meta{{color:var(--mut);font-size:15px}}.go{{color:var(--acc);font-weight:500;margin-top:8px;display:inline-block}}
</style></head><body><main>
<h1>Figures: help pages</h1><p class="lead">Working pages for figures that are made and checked in the open.</p>
<a class="card" href="derse26_geographs/"><img src="derse26_geographs/out/fig4_ci_findspots.png" alt="Fig. 4, Campanian Ignimbrite findspots"><div class="body"><h2>From Relations to Graphs: (Geo-)Spatial data in the Cultural Heritage Domain</h2>
<div class="meta">deRSE26 / ECEASST, revision of November 2026. {n_new} of {n_all} figures redrawn or new, each next to the submitted version, with caption and notes.</div><span class="go">Open the gallery &rarr;</span></div></a>
</main></body></html>'''
open(os.path.join(SITE, '..', 'index.html'), 'w', encoding='utf8').write(start)
print('wrote', os.path.join(SITE, 'index.html'), len(page) // 1024, 'KB')
