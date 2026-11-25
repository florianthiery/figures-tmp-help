"""Builds data/showcase_points.csv (set, id, label, lon, lat) for the overview map z3.
Sources (paths given as arguments, all CC0 / CC BY 4.0):
  python prep_points.py <bb-5kbc-sites/data/fst_wgs84.csv> <geoscience-fairification-lod/SISAL/rdf/sisal_sites.ttl> <wb-fuzzysl-static/data/raw/entities>"""
import csv, glob, json, re, sys, os
bb, sisal, ents = sys.argv[1:4]
rows = []
for r in csv.DictReader(open(bb, encoding='utf-8-sig')):
    if r['wgs84_x'] and r['wgs84_y']: rows.append(('bb5kbc', r['fst_id'], r['fst_name'], float(r['wgs84_x']), float(r['wgs84_y'])))
t = open(sisal, encoding='utf8').read()
for i, m in enumerate(re.finditer(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)', t), 1): rows.append(('sisal', str(i), f'SISAL cave {i}', float(m.group(1)), float(m.group(2))))
seen = set()
for f in sorted(glob.glob(os.path.join(ents, 'Q*.json'))):
    d = json.load(open(f, encoding='utf8')); e = list(d['entities'].values())[0] if 'entities' in d else d
    for c in e.get('claims', {}).get('P4', []):
        v = c['mainsnak'].get('datavalue', {}).get('value')
        if v and (e['id'], v['latitude'], v['longitude']) not in seen:
            seen.add((e['id'], v['latitude'], v['longitude'])); rows.append(('fuzzysl', e['id'], e['labels']['en']['value'], v['longitude'], v['latitude']))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/showcase_points.csv'), 'w', newline='', encoding='utf8') as fh:
    w = csv.writer(fh); w.writerow(['set', 'id', 'label', 'lon', 'lat']); w.writerows(rows)
print({k: sum(1 for r in rows if r[0] == k) for k in ('bb5kbc', 'sisal', 'fuzzysl')})
