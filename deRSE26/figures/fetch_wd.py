"""Fetches the Wikidata item that the fuzzy-sl Wikibase lists as spatialCloseMatch of the Ogham stone Coumeenole North
(wd:Q126503090) plus the labels of everything it refers to, into data/wd/. Needs internet; run it once.
  cd /d C:\\git\\wikibase-static-help\\deRSE26\\figures && python fetch_wd.py && python figs.py z2"""
import json, os, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'data/wd'); os.makedirs(OUT, exist_ok=True)
QID = 'Q126503090'
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'deRSE26-figures/1.0 (florianthiery)'})))
d = get(f'https://www.wikidata.org/wiki/Special:EntityData/{QID}.json'); e = d['entities'][QID]
ids = set()
for p, cl in e['claims'].items():
    ids.add(p)
    for c in cl:
        for sn in [c['mainsnak']] + [s for qs in c.get('qualifiers', {}).values() for s in qs]:
            ids.add(sn['property']); v = sn.get('datavalue', {}).get('value')
            if isinstance(v, dict) and 'id' in v: ids.add(v['id'])
labels = {}
ids = sorted(ids)
for i in range(0, len(ids), 50):
    r = get('https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&languages=en&format=json&ids=' + urllib.parse.quote('|'.join(ids[i:i + 50])))
    for k, v in r['entities'].items(): labels[k] = v.get('labels', {}).get('en', {}).get('value', k)
json.dump(e, open(os.path.join(OUT, f'{QID}.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
json.dump(labels, open(os.path.join(OUT, 'labels.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('ok', QID, e['labels'].get('en', {}).get('value'), len(labels), 'labels')
