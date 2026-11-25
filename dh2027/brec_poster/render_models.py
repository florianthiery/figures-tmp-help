import sys, numpy as np, trimesh
from PIL import Image
def render(path, out, az=35, el=28, R=1400):
    s = trimesh.load(path)
    V, F, C = [], [], []
    off = 0
    for g in s.geometry.values():
        col = np.array(g.visual.material.main_color[:3]) / 255.0
        V.append(g.vertices); F.append(g.faces + off); C.append(np.tile(col, (len(g.faces), 1))); off += len(g.vertices)
    V, F, C = np.vstack(V), np.vstack(F), np.vstack(C)
    a, e = np.radians(az), np.radians(el)
    Rz = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    M = Rz.T @ Rx.T
    P = V @ M
    N = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); N /= np.linalg.norm(N, axis=1)[:, None] + 1e-12
    Nr = N @ M
    light = np.array([-.4, .7, .6]); light /= np.linalg.norm(light)
    sh = np.clip(Nr @ light, 0, 1) * 0.55 + 0.45
    mn, mx = P[:, :2].min(0), P[:, :2].max(0); sc = (R - 40) / (mx - mn).max()
    X = (P[:, 0] - mn[0]) * sc + 20; Y = R - ((P[:, 1] - mn[1]) * sc + 20) - (R - 40 - (mx[1] - mn[1]) * sc) / 2
    Z = P[:, 2]
    img = np.zeros((R, R, 3)); zb = np.full((R, R), -1e9); fid = np.full((R, R), -1, int); alpha = np.zeros((R, R), bool)
    for i in np.where(Nr[:, 2] > 0)[0]:
        f = F[i]; x, y, z = X[f], Y[f], Z[f]
        x0, x1 = int(max(x.min(), 0)), int(min(x.max() + 1, R - 1)); y0, y1 = int(max(y.min(), 0)), int(min(y.max() + 1, R - 1))
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-9: continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
        l1 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        l2 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        l3 = 1 - l1 - l2
        ins = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        zz = l1 * z[0] + l2 * z[1] + l3 * z[2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]; ok = ins & (zz > sub)
        sub[ok] = zz[ok]; img[y0:y1 + 1, x0:x1 + 1][ok] = C[i] * sh[i]; fid[y0:y1 + 1, x0:x1 + 1][ok] = i; alpha[y0:y1 + 1, x0:x1 + 1] |= ok
    # edges: colour or depth discontinuities
    edge = np.zeros((R, R), bool)
    for dy, dx in ((0, 1), (1, 0)):
        a1, a2 = img[:R - dy, :R - dx], img[dy:, dx:]
        z1, z2 = zb[:R - dy, :R - dx], zb[dy:, dx:]
        dif = (np.abs(a1 - a2).sum(2) > 0.12) | (np.abs(z1 - z2) > 0.0025 * (Z.max() - Z.min()) * 4)
        both = alpha[:R - dy, :R - dx] & alpha[dy:, dx:]
        edge[:R - dy, :R - dx] |= dif & both
        edge[:R - dy, :R - dx] |= alpha[:R - dy, :R - dx] ^ alpha[dy:, dx:]
    img[edge] = img[edge] * 0.35
    rgba = np.dstack([img, alpha]); rgba = (np.clip(rgba, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(rgba).save(out)
for k in (1, 2):
    render(f'/home/claude/brick-brec-gh/docs/models/p{k}_reconstruction.glb', f'/home/claude/figwork/recon{k}.png')
