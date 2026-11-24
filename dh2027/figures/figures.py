"""DH 2027 short paper figures (Seven Leaves, One Stem). Same style as the CAA-UK 2026 figs.py.
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
CMN,RES,MIX='#a7d9a5','#166534','url(#mix)'   # community source (light green) / research output (dark green) / both

import base64
_cid=[0]
def photo(f,path,cx,top,w,h):
    """embedded photograph, cover-fitted into a rounded frame (w x h), top-centre anchored at cx,top"""
    from PIL import Image
    iw,ih=Image.open(path).size; k=max(w/iw,h/ih); dw,dh=iw*k,ih*k
    b=base64.b64encode(open(path,'rb').read()).decode(); _cid[0]+=1; x=cx-w/2
    f.o.append(f'<clipPath id="c{_cid[0]}"><rect x="{x}" y="{top}" width="{w}" height="{h}" rx="14"/></clipPath>'
               f'<image href="data:image/{"png" if path.lower().endswith(".png") else "jpeg"};base64,{b}" x="{cx-dw/2}" y="{top+(h-dh)/2}" width="{dw}" height="{dh}" clip-path="url(#c{_cid[0]})"/>'
               f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="14" fill="none" stroke="#000" stroke-width="2"/>')

def edge(cx,cy,w,h,tx,ty,pad=6):
    """point on the rectangle (centre cx,cy) towards target tx,ty"""
    dx,dy=tx-cx,ty-cy
    if dx==0 and dy==0: return cx,cy
    k=min((w/2+pad)/abs(dx) if dx else 1e9,(h/2+pad)/abs(dy) if dy else 1e9)
    return cx+dx*k,cy+dy*k
def link(f,a,b,label=None,dash=False,col=RED,at=0.5,size=22):
    """arrow between two boxes a,b = (cx,cy,w,h); amber chip centred on the middle of the arrow"""
    x1,y1=edge(*a,b[0],b[1]); x2,y2=edge(*b,a[0],a[1])
    f.line(x1,y1,x2,y2,col,dash)
    if label: f.chip(x1+(x2-x1)*at,y1+(y2-y1)*at,label,size)
def node(f,cx,cy,w,h,fill,lines,sub=None,size=30,tc=None):
    f.box(cx-w/2,cy-h/2,w,h,fill,lines=lines,size=size,sub=sub,tc=tc or ('#fff' if fill in (CLS,TERM,REAL) else INK))
    return (cx,cy,w,h)

# Figure 1: the clover. Seven numbered heart-shaped leaves (numbers as in Table 1) around the stem, labels outside.
def heart(W,H):
    return (f"M0,0 C{-W*.15:.1f},{-H*.15:.1f} {-W*.55:.1f},{-H*.45:.1f} {-W*.5:.1f},{-H*.7:.1f} "
            f"C{-W*.45:.1f},{-H*.95:.1f} {-W*.1:.1f},{-H*1.0:.1f} 0,{-H*.78:.1f} "
            f"C{W*.1:.1f},{-H*1.0:.1f} {W*.45:.1f},{-H*.95:.1f} {W*.5:.1f},{-H*.7:.1f} "
            f"C{W*.55:.1f},{-H*.45:.1f} {W*.15:.1f},{-H*.15:.1f} 0,0 Z")
f=Fig(); cx,cy=875,470; R0,LH,LW=45,270,215
STEM='#14532d'
leaves=[(CMN,'OpenStreetMap','Ogham, Holy Wells, SISAL','via Overpass'),
        (CMN,'Wikidata','Ogham, Govan, Round Towers','Wikibase JSON'),
        (CMN,'Wikimedia Commons','stonecutter marks, 526 files','file metadata'),
        (RES,'TEI/EpiDoc','Ogham editions','EpiDoc XML'),
        (MIX,'FDOx','3D models, LEGO, software','Zenodo DCAT'),
        (MIX,'Chublets','open-archaeo software','CSV'),
        (RES,'MaCHeCO','CRM anchors, N4O KG','CRM link')]
f.o.append(f'<defs><linearGradient id="mix" x1="0" x2="1" y1="0" y2="0"><stop offset="0.5" stop-color="{CMN}"/><stop offset="0.5" stop-color="{RES}"/></linearGradient></defs>')
f.o.append(f'<path d="M{cx},{cy} C{cx-25},{cy+190} {cx+25},{cy+310} {cx},{cy+400}" fill="none" stroke="{STEM}" stroke-width="16" stroke-linecap="round"/>')
for i,(g,a_,b_,c_) in enumerate(leaves):
    ang=-math.pi/2+2*math.pi*i/7; deg=math.degrees(ang)+90; ca,sa=math.cos(ang),math.sin(ang)
    px,py=cx+R0*ca,cy+R0*sa
    f.o.append(f'<path d="{heart(LW,LH)}" transform="translate({px:.1f},{py:.1f}) rotate({deg:.1f})" fill="{g}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
    d=R0+LH*0.58
    if g==MIX: f.o.append(f'<circle cx="{cx+d*ca:.1f}" cy="{cy+d*sa:.1f}" r="34" fill="#fff" stroke="#000" stroke-width="2"/>')
    f.text(cx+d*ca,cy+d*sa+14,str(i+1),44,500,'#fff' if g==RES else INK)
    rl=R0+LH+28; lx,ly=cx+rl*ca,cy+rl*sa
    anc='start' if ca>0.2 else 'end' if ca<-0.2 else 'middle'
    if anc=='middle': ly-=70
    elif sa<-0.3: ly-=30
    elif sa>0.3: ly-=6
    else: ly-=12
    f.text(lx,ly,a_,32,500,INK,anchor=anc)
    f.text(lx,ly+34,b_,25,400,INK,anchor=anc)
    f.text(lx,ly+64,c_,22,400,MUT,anchor=anc)
f.o.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="{CLS}" stroke="#000" stroke-width="3"/>')
node(f,cx,cy+445,400,90,CLS,('wikibase-static','the stem'),size=26)
for k,(fl,t) in enumerate([(CMN,'community source'),(RES,'research output'),(MIX,'community and research')]):
    f.o.append(f'<rect x="40" y="{44+k*56}" width="64" height="40" rx="10" fill="{fl}" stroke="#000" stroke-width="2"/>')
    f.text(120,{0:72,1:128,2:184}[k],t,26,400,INK,anchor='start')
f.done('fig1_clover',0,H)

# Figure 2: the backbone, two junctions (photo and 3D-model preview of the same stone, Govan hogback)
f=Fig()
def lane(x,y,w,h,label):
    f.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="#ebebe5"/>'); f.text(x+26,y+40,label,26,500,MUT,anchor='start')
lane(20,20,520,445,'DCAT: metadata layer'); lane(580,20,1150,730,'CIDOC CRM: entity layer')
photo(f,'photos/govan2_model.jpg',150,75,210,158); photo(f,'photos/govan2_commons.jpg',410,75,210,158)
f.text(150,257,'3D model: M. Kasten',20,400,MUT); f.text(150,281,'CC BY 4.0, Sketchfab',20,400,MUT)
f.text(410,257,'photo: Viking870',20,400,MUT); f.text(410,281,'CC BY-SA 4.0, Commons',20,400,MUT)
rec=node(f,280,368,440,150,CMN,('Photo, model or edition','contributor, version, licence'),sub='dcat:Dataset',size=28)
stone=node(f,960,368,400,150,REAL,('The stone','what the record is about'),sub='crm:E22 Human-Made Object',size=30)
osm=node(f,1585,215,270,110,CMN,('OpenStreetMap node',),sub='authority record',size=24)
wd=node(f,1585,470,270,110,CMN,('Wikidata item',),sub='authority record',size=26)
term=node(f,960,660,400,130,TERM,('Concept in Wikidata',),sub='for example Ogham stone',size=30)
cls=node(f,1585,660,270,130,CLS,('CIDOC CRM class',),sub='crm:E22',size=26)
link(f,rec,stone,'graph junction',size=20); link(f,stone,osm,'terminology junction',size=20); link(f,stone,wd,'terminology junction',size=20)
link(f,term,cls,'terminology junction',size=20); link(f,stone,term,'instance of',dash=True,size=20)
f.chip(280,520,'graph junction',22); f.text(280,568,'a metadata record points to',22,400,INK); f.text(280,596,'the entity it describes',22,400,INK)
f.chip(280,650,'terminology junction',22); f.text(280,698,'the same individual (owl:sameAs) or',22,400,INK); f.text(280,726,'concept (skos:exactMatch) elsewhere',22,400,INK)
f.done('fig2_junctions',0,770)

# Extra (not in the paper): Commons design, photograph of a masons' mark
f=Fig()
phot=node(f,290,180,440,150,CMN,('Commons file','M-ID, structured data'),sub='crm:E36 Visual Item',size=30)
stone=node(f,900,180,360,150,REAL,('Stone','Glasgow Cathedral'),sub='crm:E22',size=30)
mark=node(f,1470,180,400,150,REAL,("Masons' mark",),sub='crm:E25 Human-Made Feature',size=32)
who=node(f,290,540,440,160,CMN,('Photographer','licence, date'),sub='dct:creator, dct:license',size=30)
typ=node(f,1470,540,420,160,TERM,('Mark type','Wikidata item'),sub='from the literature',size=30)
link(f,phot,stone,'P62 depicts')
link(f,stone,mark,'P56 bears')
link(f,phot,who,'DCAT record')
link(f,mark,typ,'P2 has type')
link(f,phot,typ,'P180 depicts',dash=True,at=0.5)
f.done('extra_commons_design',60,670)

# Figure 3: Ogham from TEI/EpiDoc: two Ogham stones (FDOx 3D-model previews), the crosswalk to Linked Open Ogham and CIDOC CRM
f=Fig()
photo(f,'photos/ogham_model1.jpg',105,130,170,470)
photo(f,'photos/ogham_model2.jpg',295,130,170,470)
rows=[(('<support>','the stone'),('ogham:OghamStone',),('crm:E22 Human-Made Object','root node')),
      (('<idno>','CIIC, CISP, TM, SMR'),None,('crm:E42 Identifier','P1_is_identified_by')),
      (('<div type=edition>','the inscription'),('ogham:Inscription',),('crmtex:TX1 Written Text','P128_carries')),
      (('<rdg>','competing readings'),('ogham:Reading',),('crmtex:TX7 Text Segment','ogham:identifiedAs')),
      (('<origPlace> + <geo>','findspot'),('ogham:Place',),('crm:E53 Place','P53, geo:asWKT')),
      (('<name nymRef>','persons named'),('ogham:Person',),('crm:E21 Person','P67_refers_to'))]
for i,(a_,b_,c_) in enumerate(rows):
    y=110+i*130
    A=node(f,700,y,380,104,RES,a_,size=28)
    B=node(f,1130,y,300,104,TERM,b_,size=28) if b_ else node(f,1130,y,300,104,'#fff',('no domain class',),size=28,tc=MUT)
    C=node(f,1535,y,410,104,CLS,c_[:1],sub=c_[1],size=28)
    link(f,A,B); link(f,B,C)
f.text(700,40,'TEI/EpiDoc',28,400,MUT); f.text(1130,40,'Linked Open Ogham',28,400,MUT); f.text(1535,40,'CIDOC CRM / CRMtex',28,400,MUT)
f.line(395,372,505,372); f.chip(450,372,'edited',22)
f.done('fig3_ogham_tei',0,110+5*130+80)

# Figure 4: the two community leaves in practice. Top: OSM, benchmark on Albert Bridge. Bottom: Commons, stonecutter marks.
import os, json, csv
def slot(path,cx,top,w,h,label):
    if os.path.exists(path): photo(f,path,cx,top,w,h)
    else:
        f.o.append(f'<rect x="{cx-w/2}" y="{top}" width="{w}" height="{h}" rx="14" fill="#fff" stroke="#000" stroke-width="2" stroke-dasharray="10 8"/>')
        f.text(cx,top+h/2,label,18,400,MUT,maxw=w-20)
def geomap(f,x0,y0,w,h,bbox,pts_groups,land,clus=0.4,rs=6.5,r0=9,goff=(0,0)):
    lo0,la0,lo1,la1=bbox; kx=w/(lo1-lo0); ky=h/(la1-la0)
    mx=lambda lon:x0+(lon-lo0)*kx; my=lambda lat:y0+h-(lat-la0)*ky
    cid=f'm{x0}_{y0}'
    f.o.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14"/></clipPath>')
    f.o.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="#dbe7ee"/><g clip-path="url(#{cid})">')
    for poly in land:
        for ring in poly:
            xs=[p[0] for p in ring]; ys=[p[1] for p in ring]
            if max(xs)<lo0 or min(xs)>lo1 or max(ys)<la0 or min(ys)>la1: continue
            d='M'+' L'.join(f'{mx(p[0]):.1f},{my(p[1]):.1f}' for p in ring)+'Z'
            f.o.append(f'<path d="{d}" fill="#f1efe8" stroke="#9ca3af" stroke-width="1" stroke-linejoin="round"/>')
    for gi,(col,pts) in enumerate(pts_groups):
        dx=goff[gi]; cl=[]
        for lon,lat in pts:   # greedy merge of points closer than clus degrees
            for c in cl:
                if abs(c[0]/c[2]-lon)<clus and abs(c[1]/c[2]-lat)<clus: c[0]+=lon; c[1]+=lat; c[2]+=1; break
            else: cl.append([lon,lat,1])
        for sx,sy,n in cl:
            lon,lat=sx/n,sy/n
            if not (lo0<=lon<=lo1 and la0<=lat<=la1): continue
            r=r0+math.sqrt(n)*rs
            f.o.append(f'<circle cx="{mx(lon)+dx:.1f}" cy="{my(lat):.1f}" r="{r:.1f}" fill="{col}" fill-opacity="0.85" stroke="#000" stroke-width="2"/>')
            if n>1: f.text(mx(lon)+dx,my(lat)+9,str(n),26 if r>26 else 20,500,'#fff' if col==REAL else INK)
    f.o.append('</g>'+f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="none" stroke="#000" stroke-width="2"/>')
    return mx,my
rows_=list(csv.DictReader(open('../commons/results/files.csv',encoding='utf-8-sig')))
land=[]
for ft in json.load(open('data/ne_50m_land.geojson'))['features']:
    g=ft['geometry']; land+=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
ak=[(float(r['lon']),float(r['lat'])) for r in rows_ if r['lat'] and r['author'].startswith('A.-K')]
ot=[(float(r['lon']),float(r['lat'])) for r in rows_ if r['lat'] and not r['author'].startswith('A.-K')]
f=Fig()
PX,PW,PH=240,280,210          # photo column
MX=800                         # source-record column
IX,IW=1420,400                 # item column
MW2=300
nid=open('photos/osm_node_id.txt').read().strip() if os.path.exists('photos/osm_node_id.txt') else ''
def row(top,title,ph,mid,item_lines,l1,l2,dash2=False):
    f.text(100,top-26,title,26,500,MUT,anchor='start')
    photo(f,ph,PX,top,PW,PH); cy=top+PH/2
    if mid[0]=='slot': slot(mid[1],MX,top,MW2,PH,mid[1])
    else: node(f,MX,cy,MW2,PH,CMN,mid[1],sub=mid[2],size=28)
    node(f,IX,cy,IW,PH,REAL,item_lines,sub='crm:E25 Human-Made Feature',size=28)
    f.line(PX+PW/2+4,cy,MX-MW2/2-6,cy); f.chip((PX+PW/2+MX-MW2/2)/2,cy,l1,22)
    f.line(MX+MW2/2+4,cy,IX-IW/2-6,cy,RED,dash2); f.chip((MX+MW2/2+IX-IW/2)/2,cy,l2,22)
row(70,'OpenStreetMap: benchmark on Albert Bridge, Glasgow','photos/albert_bridge_benchmark_trace.jpg',('slot','photos/albert_bridge_osm.png'),('Benchmark on Albert Bridge','Q107'),'mapped as','harvested as')
f.text(MX,70+PH+32,('OSM node '+nid) if nid else 'OSM node',24,400,MUT)
row(370,'Wikimedia Commons: stonecutter mark, Glasgow Cathedral','photos/masons_mark_trace.jpg',('node',('Commons file','CC BY-SA 4.0'),'crm:E36 Visual Item'),("Mason's mark type M035",'Q142278610'),'uploaded as','P180 depicts',dash2=True)
f.text(IX,370+PH+32,'type after Wallace (2020)',24,400,MUT)
f.done('fig4_osm_commons',0,650)
print('ok')
