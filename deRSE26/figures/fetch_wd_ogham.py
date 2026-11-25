"""Fetches the Wikidata items behind Fig. 2 (Ogham stone CIIC 81): the concept item Q69385424 and the physical-object item Q130529871,
plus the English labels of every item and property they refer to (incl. qualifiers and references), into data/wd/. Needs internet; run it once.
  cd /d C:\\git\\wikibase-static-help\\deRSE26\\figures && git pull && python fetch_wd_ogham.py && git add -A && git commit -m "data: Wikidata CIIC 81" && git push"""
import json, os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'data/wd'); os.makedirs(OUT, exist_ok=True)
QIDS = ['Q69385424', 'Q130529871']
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'deRSE26-figures/1.0 (florianthiery)'})))
ids = set(); ents = {}
for q in QIDS:
    e = get(f'https://www.wikidata.org/wiki/Special:EntityData/{q}.json')['entities'][q]; ents[q] = e
    json.dump(e, open(os.path.join(OUT, f'{q}.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    ids.add(q)
    def snaks(c): return [c['mainsnak']] + [s for qs in c.get('qualifiers', {}).values() for s in qs] + [s for r in c.get('references', []) for ss in r['snaks'].values() for s in ss]
    for p, cl in e['claims'].items():
        ids.add(p)
        for c in cl:
            for sn in snaks(c):
                ids.add(sn['property']); v = sn.get('datavalue', {}).get('value')
                if isinstance(v, dict) and 'id' in v: ids.add(v['id'])
                if isinstance(v, dict) and 'unit' in v and 'entity/' in v['unit']: ids.add(v['unit'].rsplit('/', 1)[1])
labels = {}; ids = sorted(ids)
for i in range(0, len(ids), 50):
    r = get('https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&languages=en&format=json&ids=' + urllib.parse.quote('|'.join(ids[i:i + 50])))
    for k, v in r['entities'].items(): labels[k] = v.get('labels', {}).get('en', {}).get('value', k)
p = os.path.join(OUT, 'labels_ciic81.json'); json.dump(labels, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('ok', [(q, ents[q]['labels'].get('en', {}).get('value')) for q in QIDS], len(labels), 'labels')
