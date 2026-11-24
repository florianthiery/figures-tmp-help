"""Draw the visible incisions of the two marks in red onto the photographs (for Figure 4).
Coordinates are pixel positions in the source photographs (hand-traced); output: photos/*_trace.jpg.
Run: python trace_marks.py"""
from PIL import Image, ImageDraw
RED=(220,38,38)
JOBS={
 # source, crop box (x0,y0,x1,y1) or None, offset-free polylines in source pixel coordinates, line width, output
 'photos/butterfly_50219.jpg': dict(crop=(250,350,1130,1010), lw=7, out='photos/masons_mark_trace.jpg', lines=[
    [(365,620),(362,940)],                    # left vertical
    [(580,540),(608,910)],                    # centre vertical
    [(838,600),(810,890)],                    # right vertical
    [(420,545),(610,750),(810,925)],          # diagonal, upper left to lower right
    [(850,550),(610,745),(512,870)]]),        # diagonal, upper right to lower left
 'photos/albert_bridge_benchmark.jpg': dict(crop=(100,40,400,265), lw=4, out='photos/albert_bridge_benchmark_trace.jpg', lines=[
    [(205,97),(250,110),(294,120)],           # horizontal bar (top of the broad arrow)
    [(250,116),(220,166),(202,176)],          # left leg with its foot
    [(254,124),(285,190)],                    # right leg
    [(250,118),(246,208)]]),                  # vertical stem
}
for src,j in JOBS.items():
    im=Image.open(src).convert('RGB'); ov=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(ov)
    for pl in j['lines']: d.line(pl,fill=RED+(215,),width=j['lw'],joint='curve')
    im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB')
    if j['crop']: im=im.crop(j['crop'])
    im.save(j['out'],quality=90)
