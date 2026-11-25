"""Slims the Natural Earth 10m layers (rivers, lakes, land borders, populated places; public domain) to Europe and the Mediterranean:
data/ne_eu_rivers.json, ne_eu_lakes.json, ne_eu_borders.json, ne_eu_places.json. Downloads the three files from nvkelso/natural-earth-vector if they are missing.
  cd /d C:\\git\\wikibase-static-help\\deRSE26\\figures && python prep_ne.py"""
import json, os, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, 'data')
BB = (-16, 28, 50, 60)
def load(n):
    p = os.path.join(D, f'{n}.geojson')
    if not os.path.exists(p): urllib.request.urlretrieve(f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/{n}.geojson', p)
    return json.load(open(p, encoding='utf8'))['features']
def lines(g): return g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']] if g['type'] == 'LineString' else []
def polys(g): return g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']] if g['type'] == 'Polygon' else []
def inb(c): return any(BB[0] <= x <= BB[2] and BB[1] <= y <= BB[3] for x, y in c)
r3 = lambda c: [[round(x, 3), round(y, 3)] for x, y in c]
rivers = [{'z': f['properties'].get('min_zoom') or 9, 'l': [r3(l) for l in lines(f['geometry']) if inb(l)]} for f in load('ne_10m_rivers_lake_centerlines')]
rivers = [r for r in rivers if r['l']]
lakes = [{'p': [[r3(ring) for ring in poly] for poly in polys(f['geometry']) if inb(poly[0])]} for f in load('ne_10m_lakes')]
lakes = [l for l in lakes if l['p']]
borders = [r3(l) for f in load('ne_10m_admin_0_boundary_lines_land') for l in lines(f['geometry']) if inb(l)]
places = [{'n': f['properties']['name'], 'p': f['properties'].get('pop_max') or 0, 'x': round(f['geometry']['coordinates'][0], 3), 'y': round(f['geometry']['coordinates'][1], 3)} for f in load('ne_10m_populated_places_simple') if BB[0] <= f['geometry']['coordinates'][0] <= BB[2] and BB[1] <= f['geometry']['coordinates'][1] <= BB[3]]
for n, o in (('places', places), ('rivers', rivers), ('lakes', lakes), ('borders', borders)): json.dump(o, open(os.path.join(D, f'ne_eu_{n}.json'), 'w', encoding='utf8'), separators=(',', ':'))
print(len(rivers), len(lakes), len(borders), len(places))
