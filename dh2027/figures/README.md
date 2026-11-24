# figures.py: figures for the DH 2027 short paper

Builds `out/fig*.svg` and `out/fig*.png` (Fira Sans, 1750 px wide). Fonts and the two photographs are included.

## Setup and run (Windows cmd, one line)

```
cd /d C:\git\wikibase-static-help\dh2027\figures && pip install resvg_py pillow && python figures.py
```

## Figures

- `fig1_clover`: the seven-leaf clover (light green community source, dark green research output, split leaf for both)
- `fig2_junctions`: backbone with the graph junction and the terminology junction, with photo and 3D-model preview of one stone
- `fig3_ogham_tei`: TEI/EpiDoc element, Linked Open Ogham class and CIDOC CRM / CRMtex class
- `fig4_benchmarks`: from the withdrawn OS Linked Data service to a community record
- `extra_commons_design`: Commons design with a depicts link (none exists yet, see `commons/results`), not used in the paper

## Contents

- `fonts/`: Fira Sans 400 and 500 (SIL Open Font License)
- `photos/govan2_commons.jpg`: photograph of the Govan hogback (Wikimedia Commons, Viking870, CC BY-SA 4.0; check before publishing)
- `photos/govan2_model.jpg`: preview of the Sketchfab 3D model of the same stone (Megan Kasten, CC BY 4.0; check before publishing)
