# figs.py: figures for the revision of "From Relations to Graphs" (deRSE26 / ECEASST)

Builds `out/<name>.svg` and `out/<name>.png` (Fira Sans, 1700 px wide = 420 pt text width of the ECEASST class, type 24 px and more = 5.9 pt and more).
Same style as `dh2027/figures/figures.py`: white background, no header or footer in the figure, edge labels as amber chips (#fbbf24) centred on the arrow.
Use the PNG in LaTeX: the SVG names Fira Sans without embedding it. A text that does not fit its box stops the run.

## Run (Windows cmd, one line)

```
cd /d C:\git\wikibase-static-help\deRSE26\figures && pip install resvg_py pillow rdflib && python figs.py fig4 z2 z3
```

## Figures (numbers as in the submitted PDF)

| Name | Replaces | Content | Data |
|---|---|---|---|
| `fig4_ci_findspots` | Fig. 4 (screenshot collage) | (A) the 74 CI findspots, archaeological site or not, with distance rings around the Phlegraean Fields; (B) the coordinate statement of Auel Maar AU3 (Q70) with its qualifiers | `data/ci_findspots.ttl`, `data/wb/*.json` (static copy of n4o-rse/wb-fuzzysl-static, commit d22dc4e), `data/ne_50m_land.geojson` |

Planned: Fig. 7, Fig. 6, Fig. 3, Fig. 10, and the additions Z2 (one findspot in RDF, LPG and HIN) and Z3 (map of the showcases). Captions: `captions.yaml`.

## Data

- `data/ci_findspots.ttl`: copy of `CI/rdf/ci_findspots.ttl` of Research-Squirrel-Engineers/GeoScience-FAIRification-LOD, commit eec8fe5 (24 Nov 2026), CC BY 4.0. Everything that the graph states is read from it.
- `data/ne_50m_land.geojson`: Natural Earth 1:50m land, public domain.
- `fonts/`: Fira Sans 400 and 500 (SIL Open Font License).

## Notes on the data

- The graph writes one literature reference as `Fitzsimmons et al.,, 2013` (double comma); the figure normalises it to `Fitzsimmons et al. 2013`.
- The rings are drawn on an equirectangular map true at 44° N and are approximate; the star is the schematic position of the Phlegraean Fields (14.14° E, 40.83° N, wd:Q755123).

| `z2_one_findspot_three_paradigms` | new (Sections 3 and 4) | Auel Maar AU3 as RDF/GeoSPARQL, LPG and HIN | `data/ci_findspots.ttl`, `data/wb/Q84.json` |
| `z3_showcase_map` | new (Section 5) | map of the showcase datasets (fuzzy-sl Wikibase vs. bespoke RDF pipeline) | `data/showcase_points.csv` (built by `prep_points.py` from bb-5kbc-sites, geoscience-fairification-lod/SISAL and wb-fuzzysl-static), `data/ne_50m_land.geojson` |
