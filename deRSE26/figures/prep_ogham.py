"""Cuts the panels of the submitted Fig. 2 (img/ogham-wikidata.jpg of the LaTeX project, 4334 x 2093 px) into single images in data/ogham/
and removes the round letter marks of the old figure. Usage: python prep_ogham.py path/to/ogham-wikidata.jpg   (needs pillow, opencv-python, numpy)"""
import os, sys, numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'data/ogham'); os.makedirs(OUT, exist_ok=True)
im = Image.open(sys.argv[1]).convert('RGB'); S = im.width / 1700
BOX = {'A_top': (0, 0, 520, 400), 'A_bot': (0, 400, 520, 821), 'B': (522, 0, 1032, 285), 'C': (1034, 0, 1700, 285), 'D': (522, 288, 830, 821), 'E': (828, 288, 1135, 821), 'F': (1135, 288, 1700, 821)}
CENTRE = {'A_top': (185, 257), 'B': (148.5, 579), 'C': (1493, 518), 'D': (157.5, 597), 'E': (149, 325), 'F': (297, 178)}   # centres of the round marks (radius 130 px)
for n, b in BOX.items():
    c = np.array(im.crop(tuple(round(v * S) for v in b)))[:, :, ::-1].copy()
    if n in CENTRE:
        cx, cy = CENTRE[n]; mask = np.zeros(c.shape[:2], np.uint8); cv2.circle(mask, (int(cx), int(cy)), 138, 255, -1)
        if n == 'B': c = cv2.inpaint(c, mask, 9, cv2.INPAINT_TELEA)          # photo: inpainting
        else:                                                                 # flat backgrounds: median colour of the ring around the mark
            ring = np.zeros(c.shape[:2], np.uint8); cv2.circle(ring, (int(cx), int(cy)), 160, 255, -1); cv2.circle(ring, (int(cx), int(cy)), 142, 0, -1)
            c[mask > 0] = np.median(c[ring > 0], axis=0)
    if c.shape[1] > 1200: c = cv2.resize(c, (1200, round(c.shape[0] * 1200 / c.shape[1])), interpolation=cv2.INTER_AREA)   # 2 x the display size is enough
    cv2.imwrite(os.path.join(OUT, n + '.png'), c, [cv2.IMWRITE_PNG_COMPRESSION, 9]); print(n, c.shape[1], c.shape[0])
