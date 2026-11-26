"""prep_geo.py: builds data/geo/*.json for the Part II figures (G17, G18, G19, G20) from the geo-lod repository.

  python prep_geo.py <geoscience-fairification-lod dir> <ne_50m_land.geojson>

Reads RDF only (rdflib); writes sisal.json, ci.json, time.json, epica_obs.json, facts.json and land.json (Natural Earth, public domain, clipped to the map extent).
"""
import json, os, re, sys
from rdflib import Graph, Namespace, RDF, RDFS, URIRef
G, LAND = sys.argv[1:3]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/geo'); os.makedirs(OUT, exist_ok=True)
GL, GEO, TIME, SOSA = Namespace('http://w3id.org/geo-lod/'), Namespace('http://www.opengis.net/ont/geosparql#'), Namespace('http://www.w3.org/2006/time#'), Namespace('http://www.w3.org/ns/sosa/')
CRM, CRMSCI = Namespace('http://www.cidoc-crm.org/cidoc-crm/'), Namespace('http://www.ics.forth.gr/isl/CRMsci/')
def g_(*p):
    g = Graph()
    for x in p: g.parse(os.path.join(G, x), format='turtle')
    return g
def wkt(g, geom):
    m = re.search(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)', str(g.value(geom, GEO.asWKT))); return float(m.group(1)), float(m.group(2))
dump = lambda n, o: json.dump(o, open(os.path.join(OUT, n), 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))

# SISAL caves (all 365; archaeological cave sites flagged)
s = g_('SISAL/rdf/sisal_sites.ttl', 'SISAL/rdf/sisal_site_annotations.ttl', 'SISAL/rdf/sisal_ontology.ttl')
arch = set(s.subjects(RDF.type, GL.ArchaeologicalCaveSite))
caves = [(wkt(s, s.value(c, GEO.hasGeometry)), str(s.value(c, RDFS.label)), c in arch) for c in s.subjects(RDF.type, GL.Cave)]
sisal = [[round(x[0][0], 3), round(x[0][1], 3), x[1], x[2]] for x in sorted(caves, key=lambda t: t[1])]
dump('sisal.json', sisal)

# CI findspots (74; archaeological ones flagged)
c = g_('CI/rdf/ci_findspots.ttl')
ca = set(c.subjects(RDF.type, GL.CIArchaeologicalSite))
ci = []
for x in c.subjects(RDF.type, GL.CIFindspot):
    lon, lat = wkt(c, c.value(x, GEO.hasGeometry)); ci.append([round(lon, 4), round(lat, 4), str(c.value(x, RDFS.label)), x in ca, str(c.value(x, GL.hasCertaintyLevel)).rsplit('/', 1)[-1]])
dump('ci.json', sorted(ci, key=lambda t: t[2]))

# competing ages of the CI eruption
tr = g_('ontology/trs.ttl')
rows = []
for a in c.subjects(RDF.type, CRM.E13_Attribute_Assignment):
    k = str(a).rsplit('_', 1)[-1]
    if 'ci_eruption_dating' not in str(a): continue
    pos = {}
    for kind in ('begin', 'end'):
        p = URIRef(f'http://w3id.org/geo-lod/ci_eruption_{kind}_pos_{k}')
        if (p, None, None) in c:
            pos[kind] = float(c.value(p, TIME.numericPosition)); pos['trs'] = str(c.value(p, TIME.hasTRS)); pos['trs_label'] = str(tr.value(URIRef(pos['trs']), RDFS.label))
    adopted = any('Adopted' in str(o) or 'Adopted as the age' in str(o) for o in c.objects(a, URIRef('http://www.w3.org/2004/02/skos/core#note')))
    rows.append(dict(id=k, label=str(c.value(a, RDFS.label)), adopted=adopted, **pos))
dump('time.json', sorted(rows, key=lambda r: -r['begin']))

# one EPICA observation (first CH4 record) with its sample, property and chronology
e = g_('EPICA/rdf/epica_dome_c.ttl', 'EPICA/rdf/epica_ontology.ttl')
o = sorted((x for x in e.subjects(RDF.type, GL.IceCoreObservation) if 'ch4' in str(x)), key=str)[0]
core = e.value(o, SOSA.hasFeatureOfInterest); prop = e.value(o, SOSA.observedProperty); chron = e.value(o, GL.ageChronology)
lit = lambda p: str(e.value(o, p))
dump('epica_obs.json', dict(obs=str(o).rsplit('/', 1)[-1], obs_label=str(e.value(o, RDFS.label)), core=str(e.value(core, RDFS.label)), prop=str(e.value(prop, RDFS.label)),
     value=lit(GL.measuredValue), unit=str(e.value(o, URIRef('http://qudt.org/schema/qudt/unit'))).rsplit('/', 1)[-1], depth=lit(GL.atDepth_m), age=lit(GL.ageKaBP),
     chron=str(chron).rsplit('/', 1)[-1], chron_label=str(tr.value(chron, RDFS.label)), n_obs=sum(1 for _ in e.subjects(RDF.type, GL.IceCoreObservation))))

# ontology facts the figures rely on (asserted here, so a change in geo-lod stops the build)
on = g_('EPICA/rdf/epica_ontology.ttl', 'SISAL/rdf/sisal_ontology.ttl', 'ontology/crm_bridging.ttl', 'ontology/geo_lod_core.ttl')
SC = RDFS.subClassOf
facts = [(GL.IceCore, CRM['E22_Human-Made_Object']), (SOSA.Observation, CRMSCI.S4_Observation), (SOSA.Sample, CRM.E18_Physical_Thing), (GL.Cave, GL.SamplingLocation), (GL.Borehole, GL.SamplingLocation)]
for a, b in facts: assert (a, SC, b) in on, (a, b)
dump('facts.json', [[str(a), str(b)] for a, b in facts])

# land, clipped to the extent of G19
X0, X1, Y0, Y1 = -16, 50, 26, 58
land = []
for f in json.load(open(LAND, encoding='utf8'))['features']:
    polys = [f['geometry']['coordinates']] if f['geometry']['type'] == 'Polygon' else f['geometry']['coordinates']
    for p in polys:
        r = p[0]
        if max(q[0] for q in r) < X0 or min(q[0] for q in r) > X1 or max(q[1] for q in r) < Y0 or min(q[1] for q in r) > Y1: continue
        land.append([[round(q[0], 2), round(q[1], 2)] for q in r])
dump('land.json', land)
print(len(sisal), 'caves', sum(1 for x in sisal if x[3]), 'archaeological;', len(ci), 'CI findspots', sum(1 for x in ci if x[3]), 'archaeological;', len(rows), 'ages;', len(land), 'land rings')
