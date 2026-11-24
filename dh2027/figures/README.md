# figures.py: figures for the DH 2027 short paper

Builds `out/fig*.svg` and `out/fig*.png` (Fira Sans, 1750 px wide). Fonts and the two photographs are included.

## Photographs and map crop (run once on your own computer)

```
cd /d C:\git\wikibase-static-help\dh2027\figures && python fetch_assets.py --contact you@example.org --commons "File:Your masons mark.jpg=masons_mark.jpg"
```

Downloads the Albert Bridge benchmark photograph from Commons, stitches an OSM crop (9 tiles) around the node and the chosen masons' mark photograph into `photos/`; author and licence go to `photos/credits.md`. Without these files, Fig. 4 and Fig. 5 show dashed slots.

## Setup and run (Windows cmd, one line)

```
cd /d C:\git\wikibase-static-help\dh2027\figures && pip install resvg_py pillow && python figures.py
```

## Figures

- `fig1_clover`: the seven-leaf clover (light green community source, dark green research output, split leaf for both)
- `fig2_junctions`: backbone with the graph junction and the terminology junction, with photo and 3D-model preview of one stone
- `fig3_ogham_tei`: two Ogham stones (FDOx 3D-model previews) and the crosswalk TEI/EpiDoc element, Linked Open Ogham class, CIDOC CRM / CRMtex class
- `fig4_benchmarks`: the benchmark on Albert Bridge: photograph, OSM node (map crop), static Wikibase item (needs `photos/albert_bridge_*`, see below)
- `fig5_stonecutter_marks`: distribution map of the 127 geotagged Commons files (Natural Earth land, `data/`) with an inset for Britain and Ireland; slot for one exemplar photograph (`photos/masons_mark.jpg`)
- `extra_commons_design`: Commons design with a depicts link (none exists yet, see `commons/results`), not used in the paper

## Contents

- `fonts/`: Fira Sans 400 and 500 (SIL Open Font License)
- `photos/govan2_commons.jpg`: photograph of the Govan hogback (Wikimedia Commons, Viking870, CC BY-SA 4.0; check before publishing)
- `photos/govan2_model.jpg`: preview of the Sketchfab 3D model of the same stone (Megan Kasten, CC BY 4.0; check before publishing)
