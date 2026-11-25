# brec_poster: figures for the DH 2027 poster abstract (BREC, CIDOC CRM, HDT, FDOx)

Builds `out/fig1_chain`, `out/fig2_layers`, and `out/fig3_model2` (SVG and PNG, Fira Sans). Everything the script reads is in this folder.

```
cd /d C:\git\figures-tmp-help\dh2027\brec_poster && pip install resvg_py pillow && python figures.py
```

## Figures

- `fig1_chain`: from photographs to the federated ecosystem. Capture, reconstruction, AI interpretation, FDOx package (with RO-Crate), ecosystem; below each step the statement type (measured, assumed, interpreted) with the CRM classes, and the layers (generic CIDOC CRM family and HDT, brick-specific BREC and MBO, FDOx tools).
- `fig2_layers`: the classes behind the statement types. Upper box of each pair: class of the CIDOC CRM family or HDT (blue outline); lower box: the BREC class that extends it. Class names are those of BREC 0.5.0.
- `fig3_model2`: Model 2 with its measured, assumed, and reconstructed statements as callouts, and the AI hypotheses with confidence, status, and Wikidata candidate as a SPARQL result. Data from `docs/brec.ttl` of brick-brec (instances `hyp_m2_a` to `hyp_m2_e`); the Maya and El Castillo hypotheses have no Wikidata match yet.

## Contents

- `photos/model1.jpg`, `photos/model2.jpg`: photographs of the two LEGO pyramids (Florian Thiery, Daria Stefan), cropped
- `renders/model*_reconstruction.png`: renderings of the reconstruction models (GLB of the FDOx), made with `render_models.py` (trimesh, numpy, pillow; needs the GLB files of the FDOx records)
- `fonts/`: Fira Sans 400 and 500 (SIL Open Font License); `fira.py`, `svgkit.py`: small SVG toolkit (overlap check for text, boxes, and arrows)
