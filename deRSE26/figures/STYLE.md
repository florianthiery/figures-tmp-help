# Graphic concept for the figures of "From Relations to Graphs" (deRSE26 / ECEASST)

One concept for every figure that is made under our own hand (Fig. 3, 4, 6, 7, 10, z2, z3 and later ones). Figures taken from
other projects keep their own look and are only marked in the caption. Everything below is implemented in `figs.py`; a new figure
uses these building blocks instead of inventing its own.

## Page and type
- Width 1700 px = 420 pt text width of the ECEASST class; height as needed. White background, no header, no footer, no title inside the image (the caption carries it).
- Fira Sans 400/500 only (`fonts/`). Minimum type 24 px (about 5.9 pt in print); `Fig.text` stops the run below that and on overflow.
- PNG goes into LaTeX (the SVG names Fira Sans without embedding it). Output of every run: `out/<name>.svg` and `.png`.
- Language: English, British spelling. No abbreviations that the paper does not introduce.

## Panels
- A panel title is a black rounded square (40 x 40 px, radius 6) with a white upper-case letter and a bold 28 px title next to it.
- Texts that refer to a panel use the same badge (never "panel A" as running text inside the image).
- Several panels: separated by a thin grey line (#d4d4d0); same structure in mirrored panels so that differences show.

## Colour roles (semantic, not decorative)
| Role | Fill | Text |
|---|---|---|
| Instance, item, node of the data | #e2e8f0 (pastel grey) | black |
| Class | #9a3412 (dark orange) | white |
| Vocabulary term, controlled value | #4c1d95 (dark purple) | white |
| Literal, plain value | white | black |
| External resource (URI) | white, dashed outline | black |
| Coordinate (WKT literal) | #1f1f1d | white |
| Property or edge label | #fbbf24 (amber chip) | black |
| Highlight (the thing the figure is about) | red #dc2626 outline, 4 px | |

Edge labels are always amber chips centred on the middle of the arrow, never beside it. Arrows black, 2.5 px, filled head. Class hierarchies: vertical edges with a hollow triangle at the parent (rdfs:subClassOf, no chip), several children or parents joined by a horizontal bus; chips only for real properties.
One bus line fans out to many values; chips sit on the branches.

## Maps
- Sea #dce9f1, land #f3f0e7, coast #b3b0a4, base map Natural Earth (public domain), plate carree scaled by cos(latitude) of the map centre.
- Large maps: dashed white graticule, degree labels outside the frame (10 or 5 degrees), black frame with ticks.
- Minimaps (below an instance node): same base map, graticule without labels, all points small, the item of the panel ringed in red. Zoom to the item where a region helps (Fig. 4: Eifel with rivers, borders, big cities as grey squares, one or two city names); at Europe scale (Fig. 7) only borders and major rivers, no city names.
- Orientation layers (`ne_eu_*.json`): lakes in sea colour, rivers #8fb4cf, borders grey dashed; only as much as stays quiet behind the points.
- Point colour follows the same roles: dark orange = archaeological site (class), white = other findspot, amber = fuzzy-sl Wikibase statement, purple star = special place (Phlegraean Fields).
- Callouts: white label with 8 px padding and a thin black leader line; never over the item they name.

## Data discipline
- Every value in a figure is read from the data (graph, Wikibase copy, CSV) by the script; assertions check that sources agree (e.g. AU3 in graph and Wikibase). Nothing is typed by hand except layout text.
- Data copies live in `data/` with their commit or date in the README; fetch scripts (`fetch_wd.py`, `prep_points.py`) document how they were made.
- Counts in captions come from the same script run as the figure.

## Caption and licence
- Caption in `captions.yaml`, British English, panels cited as (A), (B); colours explained if they carry meaning; the licence line names the authors and CC BY 4.0, third-party data and base map named.
- `replaces` names the figure of the submitted PDF, so the change list can point to it.

## Checklist before a figure is final
1. `python figs.py <name>` runs without overflow or type errors. 2. Looked at in full size and at 100 % print width. 3. Colours follow the roles above. 4. Caption, README row and tracker entry written. 5. Committed and pushed to `wikibase-static-help`.
