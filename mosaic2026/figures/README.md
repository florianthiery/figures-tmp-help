# figs.py: figures for the MOSAIC Winter School 2026 (Kiel, 4 Dec 2026)

Builds `out/<name>.svg` and `out/<name>.png` for the two decks (Part I and Part II). Same house style as `deRSE26/figures` (STYLE.md): Fira Sans, flat colours, no title or footer in the image, edge labels as amber chips centred on the arrow.

Differences for slides: canvas 2400 x 900 px, type 40 px and more, transparent background (use on white content slides), highlight in MOSAIC amethyst `#9454AC`. Values are read from `data/wd` (copies of the Wikidata items of CIIC 81, Q130529871, and of Q126503090); nothing is typed by hand.

## Run (Windows cmd, one line)

```
cd /d C:\git\figures-tmp-help\mosaic2026\figures && pip install resvg_py pillow && python figs.py g05 g04 g02 g06 g09 g08 g12 g15 g17 g18 g20 g19 g22
```

## Figures (numbers as in the plan, tab "Grafikplan")

| Name | Content | Used in |
|---|---|---|
| `g05_triple` | subject, predicate, object; class, plain value, value with language tag | Part I, step 4 |
| `g04_row_to_graph` | one table row becomes a graph | Part I, steps 3 to 4 |
| `g02_three_tables` | one stone, three identifiers, three column layouts | Part I, step 3 |
| `g06_ciic81_graph` | CIIC 81 as a graph with class, place, coordinate, external identifiers | Part I, step 4 |
| `g09_stone_in_crm` | stone, place and identifier with E22, E53, E42, P53, P48 | Part I, step 6 |
| `g08_vocabulary_stack` | languages, vocabularies, domain model | Part I, step 6 |
| `g12_sparql_pattern` | graph pattern and result table | Part I, step 8 |

| `g15_one_stone_six_ids` | the stone and the six repositories that hold it | Part II, step 2 |
| `g17_sample_measurement_model` | one EPICA Dome C methane observation: sample, measurement, chronology | Part II, step 3 |
| `g18_ci_competing_ages` | three competing ages of the Campanian Ignimbrite eruption, each with its time reference system | Part II, steps 3 and 4 |
| `g20_four_pillars` | identifiers, coordinates, vocabularies, crosswalks | Part II, step 4 |
| `g19_map_sisal_ci` | SISAL caves and CI findspots on one map | Part II, step 4 |
| `g22_demo_flow` | demo A (SPARQLing Unicorn, QGIS) and demo B (OER notebook) | Part II, step 5 |

Part II data in `data/geo` is built from the geo-lod repository with `python prep_geo.py <geoscience-fairification-lod dir> <ne_50m_land.geojson>` (needs rdflib). Natural Earth: public domain.

Licence of the drawings: CC BY 4.0, Florian Thiery. Wikidata statements: CC0.
