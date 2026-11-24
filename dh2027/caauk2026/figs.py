"""Glasgow talk figures (CAA-UK 2026): One target, four crosswalks.
Visuals style: Fira Sans, flat colours, 1750x1000 SVG -> PNG.
Setup (Windows cmd, one line):
  pip install resvg_py pillow fonttools && npm pack @fontsource/fira-sans && tar xzf fontsource-fira-sans-*.tgz
Fonts: convert package/files/fira-sans-latin-400-normal.woff and ...-500-normal.woff to TTF with fontTools,
save as fonts/FiraSans-400.ttf and fonts/FiraSans-500.ttf next to this script. Run: python figs.py  -> out/*.svg, out/*.png
No header/footer inside the figures (title and source live on the slide).
Figures: ecosystem_0..4 (4 = highlight crosswalk n), stone, benchmarks, osm_static, tei_layers, tei_gigha, tei_corpus.
"""
import resvg_py, math, os
from PIL import ImageFont
F4,F5='fonts/FiraSans-400.ttf','fonts/FiraSans-500.ttf'
W,H=1750,1000
INST,REAL,CLS,TERM,AMB='#e2e8f0','#166534','#9a3412','#4c1d95','#fbbf24'
RED,INK,MUT='#dc2626','#1f1f1d','#55544f'
def tw(s,size,w=400):
    return ImageFont.truetype(F5 if w==500 else F4,size,layout_engine=ImageFont.Layout.BASIC).getlength(s)
def esc(s): return s.replace('&','&amp;').replace('<','&lt;')
class Fig:
    def __init__(s): s.o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#f6f6f3"/>']
    def text(s,x,y,t,size=30,w=400,fill=INK,anchor='middle',maxw=None):
        if maxw and tw(t,size,w)>maxw: raise ValueError(f'overflow: {t} {tw(t,size,w):.0f}>{maxw}')
        s.o.append(f'<text x="{x}" y="{y}" font-family="Fira Sans" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{esc(t)}</text>')
    def box(s,x,y,w,h,fill,stroke='#000',sw=2,r=18,lines=(),tc=INK,size=32,sub=None,hl=False):
        s.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{RED if hl else stroke}" stroke-width="{7 if hl else sw}"/>')
        n=len(lines); gap=size*1.25; y0=y+h/2-(n-1)*gap/2+size*0.35-(14 if sub else 0)
        for i,l in enumerate(lines): s.text(x+w/2,y0+i*gap,l,size,500 if i==0 else 400,tc,maxw=w-30)
        if sub: s.text(x+w/2,y+h-22,sub,24,400,tc,maxw=w-30)
    def chip(s,cx,cy,t,size=24):
        w=tw(t,size)+28; s.o.append(f'<rect x="{cx-w/2}" y="{cy-20}" width="{w}" height="40" rx="20" fill="{AMB}" stroke="#000" stroke-width="1.5"/>'); s.text(cx,cy+8,t,size)
    def line(s,x1,y1,x2,y2,col=RED,dash=False,arrow=True):
        s.o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="4" {"stroke-dasharray=\"12 8\"" if dash else ""} {"marker-end=\"url(#a)\"" if arrow else ""}/>')
    def num(s,cx,cy,n):
        s.o.append(f'<circle cx="{cx}" cy="{cy}" r="22" fill="#fff" stroke="#000" stroke-width="2"/>'); s.text(cx,cy+9,str(n),26,500)
    def done(s,name,y0=0,y1=H):
        s.o[0]=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y1-y0}" viewBox="0 {y0} {W} {y1-y0}"><rect y="{y0}" width="{W}" height="{y1-y0}" fill="#f6f6f3"/>'
        s.o.insert(1,f'<defs><marker id="a" markerUnits="userSpaceOnUse" markerWidth="20" markerHeight="20" refX="18" refY="10" orient="auto"><path d="M0,0 L20,10 L0,20 z" fill="{RED}"/></marker></defs>')
        s.o.append('</svg>'); svg='\n'.join(s.o)
        open(f'out/{name}.svg','w').write(svg)
        open(f'out/{name}.png','wb').write(bytes(resvg_py.svg_to_bytes(svg_string=svg,font_files=[F4,F5],skip_system_fonts=True,zoom=1.0)))
os.makedirs('out',exist_ok=True)

# A: federated ecosystem, one target, four crosswalks; hl = highlighted crosswalk (0 = none)
SRC=[("TEI/EpiDoc to RDF","OG(H)AM editions, CRMtex","editorial project"),
     ("OpenStreetMap","osm2lod","open community"),
     ("Wikidata and Wikibase","FactGrid, fuzzy-sl, Kompakkt","community and project instances"),
     ("FAIR Digital Objects","FDOx metadata","project repositories")]
def eco(hl,name):
    f=Fig(); cx,cy=875,520
    pos=[(60,170),(1170,170),(60,640),(1170,640)]; bw,bh=520,190
    for i,(x,y) in enumerate(pos,1):
        ex=x+bw if x<800 else x
        f.line(ex,y+bh/2,cx-(150 if x<800 else -150),cy+(-25 if y<400 else 25),RED if hl in (0,i) else '#b8b6ae')
        mx=(ex+cx-(150 if x<800 else -150))/2; my=(y+bh/2+cy+(-25 if y<400 else 25))/2
        f.num(mx,my,i)
    f.box(cx-190,cy-110,380,220,CLS,lines=('CIDOC CRM','+ CRMtex, CRMsci'),tc='#fff',size=36,sub='shared target model')
    for i,((a,b,g),(x,y)) in enumerate(zip(SRC,pos),1):
        f.box(x,y,bw,bh,INST,lines=(f'{i}  {a}',b),size=34,sub=g,hl=(hl==i))
    f.done(name,130,870)
for h in range(5): eco(h,f'ecosystem_{h}')

# B: stone hub
f=Fig()
ids=[("Edition","TEI/EpiDoc, CIIC 81"),("Catalogue","CISP GARES/1"),("OpenStreetMap","node 11071361392"),("Wikidata","Q130529871"),
     ("FactGrid","Q1000294"),("fuzzy-sl","Q74"),("Semantic Kompakkt","Q1247")]
cx,cy=875,540
pts=[]
for i,(a_,b_) in enumerate(ids):
    ang=-math.pi/2+2*math.pi*i/len(ids); pts.append((cx+640*math.cos(ang),cy+300*math.sin(ang),a_,b_))
for x,y,a_,b_ in pts: f.line(cx,cy,x,y,'#7c7a72',True,False)
f.box(cx-165,cy-85,330,170,REAL,lines=('The stone','physical carrier'),tc='#fff',size=34)
for x,y,a_,b_ in pts: f.box(x-190,y-60,380,120,INST,lines=(a_,b_),size=30)
for x,y,a_,b_ in pts: f.chip(cx+(x-cx)*0.45,cy+(y-cy)*0.45-30,'same stone?',22)
f.done('stone',130,950)

# C: OS benchmarks governance chain
f=Fig()
steps=[("OS levelling net","unmaintained 40+ years",INST),("OS Linked Data","service withdrawn",INST),
       ("OpenStreetMap","record by A.-K. Distel",INST),("Re-runnable queries","Overpass, SPARQL, QGIS",CLS)]
bw,bh,gap=380,200,50; x0=(W-(4*bw+3*gap))/2
for i,(a,b,c) in enumerate(steps):
    x=x0+i*(bw+gap); y=350
    f.box(x,y,bw,bh,c,lines=(a,b),size=30,tc='#fff' if c==CLS else INK)
    if i<3: f.line(x+bw+4,y+bh/2,x+bw+gap-4,y+bh/2)
f.chip(x0+bw+gap/2,320,'lost',24); f.chip(x0+2*(bw+gap)+gap/2,320,'replaced',24)
f.done('benchmarks',280,570)

# D: OSM to static Wikibase (osm-benchmarks-static)
f=Fig()
bw,bh,gap=380,200,50; x0=(W-(4*bw+3*gap))/2; y=60
st=[("OSM element","node, way or relation","(c) OpenStreetMap contributors",INST),
    ("Overpass and OSM API","elements and history","23 nodes, 65 versions",INST),
    ("wikibase-static","CSV to static Wikibase","one QID per element",INST),
    ("Static site","pages, RDF and SPARQL","GitHub Pages",INST)]
for i,(a,b,c,col) in enumerate(st):
    x=x0+i*(bw+gap); f.box(x,y,bw,bh,col,lines=(a,b),size=30,sub=c)
    if i<3: f.line(x+bw+3,y+bh/2,x+bw+gap-3,y+bh/2)
x3=x0+2*(bw+gap)
f.line(x3+bw/2,y+bh+3,x3+bw/2,y+bh+90)
f.chip(x3+bw/2+120,y+bh+45,'anchored on',24)
f.box(x3,y+bh+95,bw,160,CLS,lines=('crm:E25','Human-Made Feature'),tc='#fff',size=30,sub='class Benchmark (Q100)')
f.done('osm_static',20,540)

# E: TEI/EpiDoc crosswalk, three layers (LinkedOpenOgham/tei--epidoc-crosswalk, out/README.md section 2)
f=Fig()
for x,t in ((45+230,'TEI/EpiDoc'),(645+230,'Linked Open Ogham'),(1245+230,'CIDOC CRM 7.1.3 / CRMtex')): f.text(x,40,t,28,500,MUT)
rows=[("<support>","the stone","ogham:OghamStone",("crm:E22 Human-Made Object",),"root node"),
      ("<idno>","CIIC, CISP, TM, SMR",None,("crm:E42 Identifier",),"P1_is_identified_by"),
      ("<div type=edition>","the inscription","ogham:Inscription",("crmtex:TX1 Written Text",),"P128_carries"),
      ("<rdg>","competing readings","ogham:Reading",("crmtex:TX7 Text Segment",),"ogham:identifiedAs"),
      ("<origPlace> + <geo>","findspot","ogham:Place",("crm:E53 Place",),"P53, geo:asWKT"),
      ("<name nymRef>","persons named","ogham:Person",("crm:E21 Person",),"P67_refers_to")]
bw,bh=460,110
for i,(a,b,c,d,e) in enumerate(rows):
    y=60+i*124
    f.box(45,y,bw,bh,INST,lines=(a,b),size=30)
    if c: f.box(645,y,bw,bh,TERM,lines=(c,),size=30,tc='#fff')
    else: f.box(645,y,bw,bh,'#ffffff',lines=('no domain class',),size=28,tc=MUT)
    f.box(1245,y,bw,bh,CLS,lines=d,size=28,tc='#fff',sub=e)
    f.line(45+bw+4,y+bh/2,645-4,y+bh/2); f.line(645+bw+4,y+bh/2,1245-4,y+bh/2)
f.done('tei_layers',0,820)

# F: one stone in CIDOC CRM (Gigha 1, CIIC 506; out/gigha1.crm.ttl)
f=Fig()
sx,sy=830,230
f.box(sx-170,80,340,300,REAL,lines=('Gigha 1','CIIC 506'),tc='#fff',size=36,sub='crm:E22 Human-Made Object')
L=[(90,'CIIC 506, CISP GIGHA/1','crm:E42 Identifier','P1_is_identified_by'),(230,'Granite','crm:E57 Material','P45_consists_of'),(370,'inscribed face','crm:E25 Human-Made Feature','P56_bears_feature')]
for y,a_,b_,p in L:
    f.box(40,y-55,360,110,INST,lines=(a_,),size=28,sub=b_); f.line(sx-174,y,404,y); f.chip((sx-170+400)/2,y-28,p,22)
f.box(1400,sy-55,330,110,INST,lines=('Gigha and Cara',),size=30,sub='crm:E53 Place + WKT'); f.line(sx+174,sy,1396,sy); f.chip((sx+170+1400)/2,sy-28,'P53_has_former_or_current_location',20)
f.box(sx-210,470,420,110,INST,lines=('[---]MAQ[---]COGIN[---]',),size=30,sub='crmtex:TX1 Written Text'); f.line(sx,384,sx,466); f.chip(sx+110,425,'P128_carries',22)
rd=['OG(H)AM (KF)','Rhys 1899','Rhys 1901','Macalister 1902','Macalister 1945']
for i,t in enumerate(rd):
    cx_=sx+(i-2)*310; f.box(cx_-140,690,280,100,INST,lines=(t,),size=28,sub='ogham:Reading'); f.line(sx+(i-2)*60,584,cx_,686)
f.chip(1560,590,'ogham:identifiedAs',22); f.chip(1560,640,'prov:wasAttributedTo',22)
f.done('tei_gigha',20,820)

# G: the corpus layer (og-h-am -> tei--epidoc-crosswalk -> RDF and maps)
f=Fig()
bw,bh,gap=500,200,70; x0=(W-(3*bw+2*gap))/2; y=60
st=[("og-h-am","EpiDoc editions of ogham stones","XML only, about 8 MB",INST),("tei--epidoc-crosswalk","Python, lxml, rdflib","re-run on every corpus commit",CLS),("RDF and maps","CIDOC CRM, CRMtex, GeoSPARQL","GitHub Pages",INST)]
for i,(a,b,c,col) in enumerate(st):
    x=x0+i*(bw+gap); f.box(x,y,bw,bh,col,lines=(a,b),size=30,sub=c,tc='#fff' if col==CLS else INK)
    if i<2: f.line(x+bw+3,y+bh/2,x+bw+gap-3,y+bh/2)
f.text(W/2,330,'The corpus commit is pinned in data/corpus-manifest.yaml and recorded as PROV-O in the graph',28,400,MUT,maxw=1600)
nums=[("506","stones"),("393","places"),("365","persons"),("119","kin relations"),("148","gazetteer links")]
nw,ngap=290,50; n0=(W-(5*nw+4*ngap))/2
for i,(a,b) in enumerate(nums): f.box(n0+i*(nw+ngap),380,nw,150,INST,lines=(a,b),size=38)
f.done('tei_corpus',20,560)
print('ok')