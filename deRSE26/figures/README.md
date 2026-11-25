# figs.py: figures for the revision of "From Relations to Graphs" (deRSE26 / ECEASST)

Builds `out/<name>.svg` and `out/<name>.png` (Fira Sans, 1700 px wide = 420 pt text width of the ECEASST class, type 24 px and more = 5.9 pt and more).
Same style as `dh2027/figures/figures.py`: white background, no header or footer in the figure, edge labels as amber chips (#fbbf24) centred on the arrow.
Use the PNG in LaTeX: the SVG names Fira Sans without embedding it. A text that does not fit its box stops the run.

## Run (Windows cmd, one line)

```
cd /d C:\git\wikibase-static-help\deRSE26\figures && pip install resvg_py pillow rdflib pyyaml && python fetch_wd.py && python figs.py fig4 fig7 z2 z3
```

## Figures (numbers as in the submitted PDF)

| Name | Replaces | Content | Data |
|---|---|---|---|
| `fig4_ci_findspots` | Fig. 4 (screenshot collage) | (A) the 74 CI findspots, archaeological site or not, with distance rings around the Phlegraean Fields; (B) the coordinate statement of Auel Maar AU3 (Q70) with its qualifiers | `data/ci_findspots.ttl`, `data/wb/*.json` (static copy of n4o-rse/wb-fuzzysl-static, commit d22dc4e), `data/ne_50m_land.geojson` |

| `fig3_fuzzysl_datamodel` | Fig. 3 (old data-model picture) | Geolocation metadata (GLM) and coordinate metadata (CM) of a fuzzy-sl entity: properties, qualifiers, references, value classes | `data/wb/*.json` (properties P1 to P33, classes Q2 to Q125, witness item Q70) |

| `fig5_bb5kbc_spatial` | Fig. 5 (bb5kbc ontology) | (A) spatial classes and properties of the BB-5KBC ontology; (B) one findspot on a map of the 540 findspots and as an instance | `data/bb5kbc-bundle.ttl` (Research-Squirrel-Engineers/bb-5kbc-public, commit c2e989b, 2026-09-15); base map Natural Earth |
| `fig9_arno_modules` | Fig. 9 (ArNO modules) | hexagon with the CIDOC CRM core and six concept domains, redrawn 1:1 with the twelve ontology names, Fira Sans Bold (fonts/FiraSans-700.ttf, subset) | `gallery/old/ARNO.jpg` (original by Mattis thor Straten et al., CC BY 4.0) |
| `fig10_arno_spatial` | Fig. 10 (ArNO class tree and HIN schema) | (A) spatial part of the ArNO class hierarchy; (B) spatial node types of the Poseidon network schema with properties | `data/ArNO.ttl` (archaeonatural-cloud/archaeonatural-ontology, commit 5b1ad40, 2025-08-28); structure of the Poseidon data after archaeonatural-cloud/poseidon2lod `py/Poseidon2LOD.py` |

Planned: Fig. 7, Fig. 6, and the additions Z2 (one findspot in RDF, LPG and HIN) and Z3 (map of the showcases). Captions: `captions.yaml`.

## Data

- `data/ci_findspots.ttl`: copy of `CI/rdf/ci_findspots.ttl` of Research-Squirrel-Engineers/GeoScience-FAIRification-LOD, commit eec8fe5 (24 Nov 2026), CC BY 4.0. Everything that the graph states is read from it.
- `data/ne_50m_land.geojson`: Natural Earth 1:50m land, public domain.
- `fonts/`: Fira Sans 400 and 500 (SIL Open Font License).

## Notes on the data

- The graph writes one literature reference as `Fitzsimmons et al.,, 2013` (double comma); the figure normalises it to `Fitzsimmons et al. 2013`.
- The rings are drawn on an equirectangular map true at 44° N and are approximate; the star is the schematic position of the Phlegraean Fields (14.14° E, 40.83° N, wd:Q755123).

| `z2_one_stone_five_models` | new (Section 3 or 4) | Ogham stone Coumeenole North as Wikidata, fuzzy-sl Wikibase, RDF/GeoSPARQL, LPG, HIN | `data/wb/Q131.json` etc., `data/wd/` (built by `fetch_wd.py`, needs internet) |
| `z3_showcase_map` | new (Section 5) | map of the showcase datasets (fuzzy-sl Wikibase vs. bespoke RDF pipeline) | `data/showcase_points.csv` (built by `prep_points.py` from bb-5kbc-sites, geoscience-fairification-lod/SISAL and wb-fuzzysl-static), `data/ne_50m_land.geojson` |
| `fig7_ci_instances` | Fig. 7 | Toplitsa Cave and Franchthi Cave (ci:cisite_44, _45) as instances, read from the graph | `data/ci_findspots.ttl` |
| `fig6_place_taxonomy` | Fig. 6 (slice) | place classes with their CRM, CRMarchaeo, GeoSPARQL anchors; every arrow is checked against the ontology files | `ontology/*.ttl`, `SISAL/rdf/sisal_ontology.ttl`, `EPICA/rdf/epica_ontology.ttl` of GeoScience-FAIRification-LOD (clone path in `GEOLOD_DIR`, default Linux path in `figs.py`) |

Base-map layers: `prep_ne.py` slims the Natural Earth 10 m layers (rivers, lakes, land borders, populated places) to Europe: `data/ne_eu_*.json` (public domain).

Gallery: `docs/derse26_geographs/index.html` in the repository root (GitHub Pages: folder `/docs`). `python build_gallery.py` (needs `pip install pyyaml`) rebuilds it from `figures.yaml` and `captions.yaml`, and every run of `figs.py` does so as well; fonts, old images (`gallery/old/`, downsized copies of the submitted figures) and `out/*.png` are copied next to the page, so it opens with a double click. No time stamp inside, so identical inputs give an identical file.
