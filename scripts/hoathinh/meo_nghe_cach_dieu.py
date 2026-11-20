"""Mèo Nghệ cách điệu – 10 nhân vật (không mặc đồ + avatar), mỗi con một khung người & gương mặt.

Không vẽ giống mèo thật: chỉ giữ tai, râu, đuôi làm dấu hiệu "mèo"; thân là khối đơn giản.
THÂN + TAY + CHÂN gộp thành MỘT khối (blob) → một đường viền liền, tay không thể lệch khỏi người.

Chạy:  python scripts/hoathinh/meo_nghe_cach_dieu.py
Ra:    build/thu-hoathinh/meo-nghe/cach-dieu-10.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, AWAY, _shift, paste, hx, mix, cr, taper, ellipse_pts, stroke  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'meo-nghe')
WHITE = (255, 255, 255)
PINK = hx('#F2A0A6')
CREAMY = hx('#FFF1DC')


def C3(h):
    c = hx(h)
    return dict(b=c, s=mix(c, (90, 30, 0), 0.22), l=mix(c, (255, 255, 255), 0.28))


# ------------------------------------------------------------------ khối gộp nhiều đa giác (một viền)
def blob(cv, polys, c, lw=3.0, shd=8, hld=5, inner=()):
    """Như shape() nhưng mặt nạ = HỢP của nhiều đa giác → viền mực liền một nét quanh cả khối."""
    S = SS
    allp = [(x * S, y * S) for P in polys for x, y in P]
    pad = int((lw * 1.6 + max(shd, hld)) * S) + 6
    x0, y0 = int(min(p[0] for p in allp)) - pad, int(min(p[1] for p in allp)) - pad
    x1, y1 = int(max(p[0] for p in allp)) + pad, int(max(p[1] for p in allp)) + pad
    w, h = x1 - x0, y1 - y0
    mi = Image.new('L', (w, h), 0)
    dm = ImageDraw.Draw(mi)
    for P in polys:
        dm.polygon([(x * S - x0, y * S - y0) for x, y in P], fill=255)
    m = np.asarray(mi) > 0
    out = np.zeros((h, w, 4), np.uint8)
    r = max(1, int(round(lw * S * 0.5)))
    d1 = np.asarray(mi.filter(ImageFilter.MaxFilter(2 * r + 1))) > 0
    r2 = max(1, int(round(lw * S * 0.55)))
    d2 = _shift(np.asarray(mi.filter(ImageFilter.MaxFilter(2 * r2 + 1))) > 0, AWAY[0] * r2, AWAY[1] * r2)
    out[(d1 | d2) & ~m] = INK + (255,)
    out[m] = c['b'] + (255,)
    if shd:
        s = m & ~_shift(m, -AWAY[0] * shd * S, -AWAY[1] * shd * S)
        out[s] = c['s'] + (255,)
    if hld:
        li = m & ~_shift(m, AWAY[0] * hld * S, AWAY[1] * hld * S)
        out[li] = c['l'] + (255,)
    if inner:
        tmp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        dr = ImageDraw.Draw(tmp)

        def T(p):
            return (p[0] * S - x0, p[1] * S - y0)
        for it in inner:
            k = it[0]
            if k == 'poly':
                dr.polygon([T(p) for p in it[1]], fill=tuple(it[2]) + (255,))
            elif k == 'line':
                dr.line([T(p) for p in it[1]], fill=tuple(it[2]) + (255,), width=max(1, int(it[3] * S)), joint='curve')
            elif k == 'taper':
                dr.polygon([T(p) for p in taper(it[1], it[2], it[3])], fill=tuple(it[4]) + (255,))
            elif k == 'dot':
                x, y = T(it[1])
                rr = it[2] * S
                dr.ellipse([x - rr, y - rr, x + rr, y + rr], fill=tuple(it[3]) + (255,))
        ta = np.asarray(tmp).copy()
        ta[..., 3] = (ta[..., 3] * m).astype(np.uint8)
        base = Image.fromarray(out, 'RGBA')
        base.alpha_composite(Image.fromarray(ta, 'RGBA'))
        out = np.asarray(base).copy()
    paste(cv, out, x0, y0)


def superell(cx, cy, rx, ry, n=4.0, N=60):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N
        c, s = math.cos(t), math.sin(t)
        pts.append((cx + rx * math.copysign(abs(c) ** (2 / n), c), cy + ry * math.copysign(abs(s) ** (2 / n), s)))
    return pts


def ell(cv, c, rx, ry, fill=None, ow=0.0, oc=INK):
    x, y = c
    ImageDraw.Draw(cv).ellipse([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS],
                               fill=None if fill is None else tuple(fill) + (255,),
                               outline=None if ow <= 0 else tuple(oc) + (255,), width=max(1, int(ow * SS)) if ow > 0 else 0)


def line(cv, pts, w, col=INK):
    d = ImageDraw.Draw(cv)
    P = [(x * SS, y * SS) for x, y in pts]
    d.line(P, fill=tuple(col) + (255,), width=max(1, int(w * SS)), joint='curve')
    r = w * SS / 2
    for x, y in (P[0], P[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(col) + (255,))


def soft_ell(cv, c, rx, ry, rgba):
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    x, y = c
    ImageDraw.Draw(lay).ellipse([(x - rx) * SS, (y - ry) * SS, (x + rx) * SS, (y + ry) * SS], fill=rgba)
    cv.alpha_composite(lay)


def tube(path, w0, w1):
    """Ống tay/chân đầu tròn: đa giác thon + hai nắp tròn."""
    P = cr(path, closed=False, n=8)
    return [taper(P, w0, w1), ellipse_pts(*P[0], w0 / 2, w0 / 2, n=20), ellipse_pts(*P[-1], w1 / 2, w1 / 2, n=20)]


# ------------------------------------------------------------------ tư thế tay
def arm_path(pose, s, sx, sy, L):
    P = {
        'down': [(0.22, 0.5), (0.3, 0.95)],
        'out': [(0.6, 0.18), (1.0, 0.32)],
        'wave': [(0.55, -0.08), (0.72, -0.75)],
        'up': [(0.32, -0.5), (0.44, -1.0)],
        'flex': [(0.62, -0.02), (0.6, -0.62)],
        'shrug': [(0.5, 0.32), (0.95, 0.06)],
        'point': [(0.6, -0.12), (1.05, -0.42)],
        'stub': [(0.35, 0.3), (0.5, 0.55)],
    }[pose]
    return [(s * (sx - 6), sy + 4)] + [(s * (sx + a * L), sy + b * L) for a, b in P]


# ------------------------------------------------------------------ nhân vật
class Char:
    def __init__(self, cv, cx, gy, k, d):
        self.cv, self.cx, self.gy, self.k, self.d = cv, cx, gy, k, d
        self.fur = C3(d['fur'])

    def P(self, x, y):
        return (self.cx + x * self.k, self.gy + y * self.k)

    def Ps(self, pts):
        return [self.P(*p) for p in pts]

    # ---------------- thân + tay + chân = 1 khối
    def body_polys(self):
        d, k = self.d, self.k
        b = d['body']
        if b[0] == 'super':
            _, cy, rx, ry, n = b
            body = [self.P(x, y) for x, y in superell(0, cy, rx, ry, n)]
        else:
            right = b[1]
            pts = right + [(-x, y) for x, y in right[1:-1]][::-1]
            body = cr(self.Ps(pts), n=8)
        polys = [body]
        lg = d['legs']
        for s in (-1, 1):
            top = (s * lg['x'], -lg['len'] - 6)
            foot = (s * (lg['x'] + lg.get('splay', 4)), -lg['w'] * 0.45)
            polys += tube(self.Ps([top, ((top[0] + foot[0]) / 2, -lg['len'] / 2), foot]), lg['w'] * k, lg['w'] * 0.92 * k)
            polys.append(ellipse_pts(*self.P(s * (lg['x'] + lg.get('splay', 4) + lg['w'] * 0.12), -lg['w'] * 0.42),
                                     lg['w'] * 0.62 * k, lg['w'] * 0.42 * k, n=24))
        am = d['arms']
        for s, pose in ((-1, am['L']), (1, am['R'])):
            path = arm_path(pose, s, am['x'], am['y'], am['len'])
            polys += tube(self.Ps(path), am['w'] * k, am['w'] * 0.86 * k)
            self.__dict__.setdefault('hands', []).append(self.P(*path[-1]))
            self.__dict__.setdefault('feet', [])
        for s in (-1, 1):
            self.feet.append(self.P(s * (lg['x'] + lg.get('splay', 4) + lg['w'] * 0.12), -lg['w'] * 0.42))
        return polys

    # ---------------- đầu + tai = 1 khối
    def head_polys(self):
        d, k = self.d, self.k
        h = d['head']
        hcx, hcy = h.get('dx', 0), h['y']
        self.hc = self.P(hcx, hcy)
        self.R = (h['rx'] * k, h['ry'] * k)
        if h.get('n', 2) != 2:
            head = [self.P(x, y) for x, y in superell(hcx, hcy, h['rx'], h['ry'], h['n'])]
        else:
            head = ellipse_pts(*self.hc, h['rx'] * k, h['ry'] * k, n=60)
        e = d['ears']
        polys, pinks = [head], []
        sz = e.get('size', 1.0)
        for s in (-1, 1):
            bx = hcx + s * h['rx'] * e.get('x', 0.62)
            by = hcy - h['ry'] * e.get('yb', 0.72)
            kind = e['kind']
            if kind == 'round':
                pts = [(bx - s * 30 * sz, by + 14), (bx - s * 22 * sz, by - 30 * sz), (bx + s * 4 * sz, by - 46 * sz),
                       (bx + s * 26 * sz, by - 30 * sz), (bx + s * 30 * sz, by + 10)]
                ip = [(bx - s * 14 * sz, by + 4), (bx - s * 8 * sz, by - 24 * sz), (bx + s * 6 * sz, by - 32 * sz),
                      (bx + s * 16 * sz, by - 18 * sz), (bx + s * 14 * sz, by + 4)]
                n = 6
            elif kind == 'long':
                pts = [(bx - s * 26 * sz, by + 16), (bx + s * 6 * sz, by - 80 * sz), (bx + s * 30 * sz, by + 10)]
                ip = [(bx - s * 12 * sz, by + 6), (bx + s * 6 * sz, by - 58 * sz), (bx + s * 16 * sz, by + 4)]
                n = 3
            elif kind == 'wide':
                pts = [(bx - s * 24 * sz, by + 20), (bx + s * 46 * sz, by - 34 * sz), (bx + s * 26 * sz, by + 22)]
                ip = [(bx - s * 8 * sz, by + 12), (bx + s * 32 * sz, by - 20 * sz), (bx + s * 16 * sz, by + 14)]
                n = 3
            elif kind == 'tiny':
                pts = [(bx - s * 18 * sz, by + 10), (bx + s * 2 * sz, by - 30 * sz), (bx + s * 20 * sz, by + 8)]
                ip = []
                n = 3
            else:   # tri
                pts = [(bx - s * 30 * sz, by + 16), (bx + s * 4 * sz, by - 54 * sz), (bx + s * 32 * sz, by + 12)]
                ip = [(bx - s * 16 * sz, by + 6), (bx + s * 4 * sz, by - 34 * sz), (bx + s * 18 * sz, by + 4)]
                n = 3
            polys.append(cr(self.Ps(pts), n=n) if n > 3 else self.Ps(pts))
            if ip:
                pinks.append(cr(self.Ps(ip), n=5))
        return polys, pinks

    def tail(self):
        d, k = self.d, self.k
        t = d['tail']
        P = cr(self.Ps(t['path']), closed=False, n=8)
        polys = [taper(P, t['w'] * k, t['w'] * 0.55 * k), ellipse_pts(*P[-1], t['w'] * 0.28 * k, t['w'] * 0.28 * k, n=16)]
        inner = []
        if d.get('stripes'):
            for i in range(8, len(P) - 4, 10):
                a, b = P[i - 1], P[i + 1]
                dx, dy = b[0] - a[0], b[1] - a[1]
                dd = math.hypot(dx, dy) or 1
                nx, ny = -dy / dd, dx / dd
                c = P[i]
                inner.append(('line', [(c[0] - nx * 40 * k, c[1] - ny * 40 * k), (c[0] + nx * 40 * k, c[1] + ny * 40 * k)],
                              self.fur['s'], 6 * k))
        if t.get('tip'):
            inner.append(('poly', ellipse_pts(*P[-1], t['w'] * 0.7 * k, t['w'] * 0.7 * k, n=20), CREAMY))
        blob(self.cv, polys, self.fur, lw=2.8, shd=5, hld=3, inner=inner)

    def draw(self, merge_head=False):
        d, k = self.d, self.k
        soft_ell(self.cv, self.P(0, 2), d.get('shw', 90) * k, 11 * k, (60, 40, 20, 55))
        self.tail()
        bp = self.body_polys()
        hp, pinks = self.head_polys()
        inner = []
        if d.get('belly'):
            bx, by, brx, bry = d['belly']
            inner.append(('poly', ellipse_pts(*self.P(bx, by), brx * k, bry * k, n=40), CREAMY))
        for p in self.hands + self.feet:
            if d.get('socks', True):
                inner.append(('dot', p, d['arms']['w'] * 0.42 * k if p in self.hands else d['legs']['w'] * 0.5 * k, CREAMY))
        if merge_head or d.get('merge'):
            blob(self.cv, bp + hp, self.fur, lw=3.0, shd=8, hld=5, inner=inner + self.head_inner(pinks))
        else:
            blob(self.cv, bp, self.fur, lw=3.0, shd=8, hld=5, inner=inner)
            blob(self.cv, hp, self.fur, lw=3.0, shd=8, hld=5, inner=self.head_inner(pinks))
        self.face()

    def head_inner(self, pinks):
        d, k = self.d, self.k
        (hx_, hy), (Rx, Ry) = self.hc, self.R
        f = d['face']
        inner = [('poly', p, PINK) for p in pinks]
        if d.get('stripes'):
            for i, dx in enumerate((-0.18, 0, 0.18)):
                inner.append(('taper', [(hx_ + dx * Rx, hy - Ry * 1.02), (hx_ + dx * Rx * 0.9, hy - Ry * 0.62)],
                              (9 if i != 1 else 11) * k, 2 * k, self.fur['s']))
            for s in (-1, 1):
                for j in (0, 1):
                    inner.append(('taper', [(hx_ + s * Rx * 1.04, hy + (j * 0.16 - 0.02) * Ry),
                                            (hx_ + s * Rx * 0.74, hy + (j * 0.16) * Ry)], 8 * k, 2 * k, self.fur['s']))
        if f.get('muzzle', True):
            my = hy + f.get('ny', 0.30) * Ry + 0.13 * Ry
            for s in (-1, 1):
                inner.append(('poly', ellipse_pts(hx_ + s * 0.15 * Rx, my, 0.22 * Rx, 0.16 * Ry, n=24), CREAMY))
        return inner

    # ---------------- mặt
    def face(self):
        d, k = self.d, self.k
        cv = self.cv
        f = d['face']
        (hx_, hy), (Rx, Ry) = self.hc, self.R
        ex, ey = f.get('ex', 0.36) * Rx, hy + f.get('ey', -0.04) * Ry
        es = f.get('es', 1.0) * 0.15 * Rx
        ink_w = max(2.6, 0.035 * Rx)
        for i, s in enumerate((-1, 1)):
            kind = f['eyes'][i]
            cx, cy = hx_ + s * ex, ey
            if kind == 'dot':
                ell(cv, (cx, cy), es * 0.55, es * 0.75, fill=INK)
                ell(cv, (cx - es * 0.18, cy - es * 0.3), es * 0.18, es * 0.18, fill=WHITE)
            elif kind == 'bigdot':
                ell(cv, (cx, cy), es * 0.95, es * 1.1, fill=INK)
                ell(cv, (cx - es * 0.32, cy - es * 0.4), es * 0.34, es * 0.34, fill=WHITE)
                ell(cv, (cx + es * 0.3, cy + es * 0.42), es * 0.14, es * 0.14, fill=WHITE)
            elif kind == 'line':
                line(cv, [(cx - es, cy), (cx + es, cy)], ink_w * 1.2)
            elif kind == 'happy':
                line(cv, cr([(cx - es, cy + es * 0.3), (cx, cy - es * 0.6), (cx + es, cy + es * 0.3)], closed=False, n=8),
                     ink_w * 1.3)
            elif kind == 'sleepy':
                line(cv, cr([(cx - es, cy - es * 0.1), (cx, cy + es * 0.45), (cx + es, cy - es * 0.1)], closed=False, n=8),
                     ink_w * 1.2)
            elif kind == 'wide':
                ell(cv, (cx, cy), es * 1.15, es * 1.3, fill=WHITE, ow=ink_w)
                ell(cv, (cx + s * es * 0.1, cy), es * 0.3, es * 0.3, fill=INK)
            elif kind in ('smug', 'cat'):
                ell(cv, (cx, cy), es * 1.05, es * 1.15, fill=hx(f.get('iris', '#B9CC3C')), ow=ink_w)
                gx = f.get('gaze', 0.3)
                ell(cv, (cx + gx * es * 0.4, cy), es * 0.34, es * 0.86, fill=INK)
                ell(cv, (cx + gx * es * 0.4 - es * 0.3, cy - es * 0.4), es * 0.25, es * 0.25, fill=WHITE)
                if kind == 'smug':
                    lid = cy - es * 1.15 + es * 2.3 * f.get('lid', 0.45)
                    E = ellipse_pts(cx, cy, es * 1.05 + 2, es * 1.15 + 2, n=40)
                    ImageDraw.Draw(cv).polygon([(x * SS, min(y, lid + s * 0.0) * SS) for x, y in E],
                                               fill=self.fur['s'] + (255,))
                    line(cv, [(cx - es * 1.15, lid + es * 0.06 * s), (cx + es * 1.15, lid - es * 0.06 * s)], ink_w * 1.3)
            elif kind == 'x':
                line(cv, [(cx - es * 0.7, cy - es * 0.7), (cx + es * 0.7, cy + es * 0.7)], ink_w * 1.2)
                line(cv, [(cx - es * 0.7, cy + es * 0.7), (cx + es * 0.7, cy - es * 0.7)], ink_w * 1.2)
        br = f.get('brows')
        if br:
            for s, a in zip((-1, 1), br):
                cx = hx_ + s * ex
                y = ey - es * 1.7
                stroke(cv, [(cx - s * es * 0.9, y + a * 0.5 * k * s * 0 + a * k * 0.5), (cx + s * es * 0.9, y - a * k * 0.5)],
                       f.get('bw', 7) * k, f.get('bw', 7) * k * 0.6, mix(self.fur['s'], (40, 15, 0), 0.5))
        ny = hy + f.get('ny', 0.30) * Ry
        ns = 0.07 * Rx
        if f.get('nose', 'tri') == 'tri':
            ImageDraw.Draw(cv).polygon([((hx_ - ns) * SS, (ny - ns * 0.5) * SS), ((hx_ + ns) * SS, (ny - ns * 0.5) * SS),
                                        (hx_ * SS, (ny + ns * 0.5) * SS)], fill=PINK + (255,), outline=INK + (255,),
                                       width=max(1, int(2 * SS)))
        else:
            ell(cv, (hx_, ny), ns * 0.6, ns * 0.45, fill=INK)
        my = ny + ns * 0.7
        mw = 0.12 * Rx * f.get('mw', 1.0)
        m = f['mouth']
        if m == 'w':
            line(cv, cr([(hx_ - mw, my + mw * 0.2), (hx_ - mw * 0.5, my + mw * 0.55), (hx_, my), (hx_ + mw * 0.5, my + mw * 0.55),
                         (hx_ + mw, my + mw * 0.2)], closed=False, n=6), ink_w)
        elif m == 'o':
            ell(cv, (hx_, my + mw * 0.5), mw * 0.38, mw * 0.5, fill=hx('#5C1A16'), ow=ink_w * 0.8)
        elif m == 'smirk':
            line(cv, cr([(hx_ - mw * 0.8, my + mw * 0.35), (hx_, my + mw * 0.3), (hx_ + mw * 0.9, my - mw * 0.1),
                         (hx_ + mw * 1.1, my - mw * 0.35)], closed=False, n=6), ink_w)
        elif m == 'flat':
            line(cv, [(hx_ - mw * 0.7, my + mw * 0.3), (hx_ + mw * 0.7, my + mw * 0.3)], ink_w)
        elif m in ('D', 'tooth', 'tongue'):
            pts = cr([(hx_ - mw * 1.2, my), (hx_ + mw * 1.2, my), (hx_ + mw * 0.7, my + mw * 1.1), (hx_, my + mw * 1.4),
                      (hx_ - mw * 0.7, my + mw * 1.1)], n=6)
            if m == 'tongue':
                line(cv, cr([(hx_ - mw, my + mw * 0.1), (hx_ - mw * 0.5, my + mw * 0.45), (hx_, my), (hx_ + mw * 0.5, my + mw * 0.45),
                             (hx_ + mw, my + mw * 0.1)], closed=False, n=6), ink_w)
                ImageDraw.Draw(cv).ellipse([(hx_ - mw * 0.45) * SS, (my + mw * 0.3) * SS, (hx_ + mw * 0.45) * SS,
                                            (my + mw * 1.3) * SS], fill=PINK + (255,), outline=INK + (255,),
                                           width=max(1, int(ink_w * 0.8 * SS)))
            else:
                ImageDraw.Draw(cv).polygon([(x * SS, y * SS) for x, y in pts], fill=hx('#5C1A16') + (255,),
                                           outline=INK + (255,))
                ell(cv, (hx_, my + mw * 1.05), mw * 0.55, mw * 0.28, fill=PINK)
                if m == 'tooth':
                    ImageDraw.Draw(cv).polygon([((hx_ + mw * 0.2) * SS, my * SS), ((hx_ + mw * 0.6) * SS, my * SS),
                                                ((hx_ + mw * 0.4) * SS, (my + mw * 0.45) * SS)], fill=WHITE + (255,))
        elif m == 'tri':
            ImageDraw.Draw(cv).polygon([((hx_ - mw * 0.4) * SS, (my + mw * 0.2) * SS), ((hx_ + mw * 0.4) * SS, (my + mw * 0.2) * SS),
                                        (hx_ * SS, (my + mw * 0.8) * SS)], fill=hx('#5C1A16') + (255,))
        wn, wl = f.get('wn', 3), f.get('wl', 0.55)
        for s in (-1, 1):
            for j in range(wn):
                a = (j - (wn - 1) / 2) * 0.16
                x0 = hx_ + s * 0.42 * Rx
                y0 = ny + 0.06 * Ry + a * 0.3 * Ry
                x2, y2 = x0 + s * wl * Rx, y0 + a * Ry * 0.9
                line(cv, cr([(x0, y0), ((x0 + x2) / 2, (y0 + y2) / 2 - (4 * k if f.get('wcurl') else 0)), (x2, y2)],
                            closed=False, n=6), max(1.6, 0.018 * Rx))
        if f.get('blush'):
            for s in (-1, 1):
                soft_ell(cv, (hx_ + s * ex * 1.25, ey + es * 1.6), es * 0.9, es * 0.5, PINK + (110,))
        if f.get('freckle'):
            for s in (-1, 1):
                for j, (ax, ay) in enumerate(((1.0, 1.4), (1.35, 1.5), (1.18, 1.85))):
                    ell(cv, (hx_ + s * ex * ax, ey + es * ay), 2.2 * k, 2.2 * k, fill=self.fur['s'])
        if f.get('sweat'):
            sx, sy = hx_ + Rx * 0.75, hy - Ry * 0.45
            ImageDraw.Draw(cv).polygon(
                [(x * SS, y * SS) for x, y in cr([(sx, sy - 16 * k), (sx + 9 * k, sy + 4 * k), (sx, sy + 12 * k), (sx - 9 * k, sy + 4 * k)],
                                                 n=5)], fill=hx('#9FD3F0') + (255,), outline=INK + (255,), width=int(2 * SS))
        if f.get('zzz'):
            fz = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), int(26 * k * SS))
            ImageDraw.Draw(cv).text(((hx_ + Rx * 0.9) * SS, (hy - Ry * 1.2) * SS), 'z', font=fz, fill=INK + (255,))
            fz2 = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), int(36 * k * SS))
            ImageDraw.Draw(cv).text(((hx_ + Rx * 1.05) * SS, (hy - Ry * 1.6) * SS), 'Z', font=fz2, fill=INK + (255,))


# ------------------------------------------------------------------ 10 nhân vật
def tail_r(x, y, h, curl=1):
    return [(x, y), (x + 50, y - 10), (x + 80, y - h * 0.45), (x + 70 + 20 * curl, y - h * 0.85), (x + 40 + 30 * curl, y - h)]


CHARS = [
    dict(ten='Hạt Đậu', mo_ta='thân hạt đậu dài, mắt chấm',
         fur='#F2A65A', body=('poly', [(0, -330), (60, -300), (72, -180), (66, -80), (40, -40), (0, -34)]),
         legs=dict(x=30, len=48, w=40), arms=dict(x=50, y=-230, len=70, w=30, L='down', R='wave'),
         head=dict(y=-370, rx=105, ry=92), ears=dict(kind='round', size=0.9),
         tail=dict(path=tail_r(40, -90, 150), w=20), belly=(0, -160, 44, 80),
         face=dict(eyes=('dot', 'dot'), mouth='w', wn=2, wl=0.5, blush=True)),
    dict(ten='Bánh Bao', mo_ta='tròn ủm, cười híp mắt',
         fur='#EE8A2E', body=('super', -150, 112, 120, 2.2), stripes=True,
         legs=dict(x=48, len=40, w=44), arms=dict(x=92, y=-190, len=55, w=34, L='out', R='out'),
         head=dict(y=-320, rx=120, ry=100), ears=dict(kind='tri', size=0.9),
         tail=dict(path=tail_r(90, -110, 120), w=26), belly=(0, -140, 72, 80),
         face=dict(eyes=('happy', 'happy'), mouth='D', blush=True, wl=0.5)),
    dict(ten='Quả Lê', mo_ta='vai hẹp đít to, mặt lém',
         fur='#E9822B', body=('poly', [(0, -250), (40, -238), (62, -170), (98, -90), (90, -40), (0, -32)]), stripes=True,
         legs=dict(x=42, len=36, w=40), arms=dict(x=40, y=-212, len=80, w=26, L='down', R='point'),
         head=dict(y=-320, rx=96, ry=84), ears=dict(kind='tri', size=1.0),
         tail=dict(path=tail_r(80, -80, 150), w=22),
         face=dict(eyes=('smug', 'smug'), mouth='smirk', brows=(0, 6), gaze=0.5, lid=0.48)),
    dict(ten='Cò Hương', mo_ta='chân tay dài ngoằng, hốt hoảng',
         fur='#F09445', body=('poly', [(0, -300), (42, -290), (50, -220), (46, -170), (28, -150), (0, -148)]),
         legs=dict(x=22, len=156, w=26, splay=8), arms=dict(x=32, y=-276, len=110, w=22, L='up', R='up'),
         head=dict(y=-370, rx=78, ry=70), ears=dict(kind='long', size=0.85),
         tail=dict(path=tail_r(30, -170, 160), w=16),
         face=dict(eyes=('wide', 'wide'), mouth='o', sweat=True, wn=2, wl=0.7, muzzle=False), shw=70),
    dict(ten='Cục Gạch', mo_ta='thân vuông, chán đời',
         fur='#DE7A28', body=('super', -150, 92, 118, 5), stripes=True,
         legs=dict(x=44, len=36, w=40), arms=dict(x=78, y=-210, len=70, w=30, L='down', R='down'),
         head=dict(y=-330, rx=118, ry=82, n=4.5), ears=dict(kind='tiny', size=1.1, x=0.7, yb=0.8),
         tail=dict(path=tail_r(80, -80, 110, 0), w=24),
         face=dict(eyes=('line', 'line'), mouth='flat', wn=3, wl=0.75, ey=-0.02, brows=(-4, -4))),
    dict(ten='Chíp Bông', mo_ta='đầu to thân tí, mắt long lanh',
         fur='#F7B26E', body=('poly', [(0, -170), (40, -160), (52, -110), (46, -60), (0, -50)]),
         legs=dict(x=24, len=56, w=30), arms=dict(x=36, y=-150, len=48, w=24, L='stub', R='wave'),
         head=dict(y=-290, rx=138, ry=120), ears=dict(kind='round', size=1.25),
         tail=dict(path=tail_r(40, -80, 110), w=18, tip=True), belly=(0, -100, 30, 40),
         face=dict(eyes=('bigdot', 'bigdot'), es=1.2, mouth='w', blush=True, wl=0.4, ey=0.02), shw=70),
    dict(ten='Lạp Xưởng', mo_ta='thân dài chân ngắn, lè lưỡi',
         fur='#D96C2A', body=('poly', [(0, -360), (52, -352), (60, -260), (62, -120), (52, -50), (0, -40)]), stripes=True,
         legs=dict(x=30, len=50, w=36), arms=dict(x=50, y=-300, len=72, w=26, L='shrug', R='shrug'),
         head=dict(y=-410, rx=96, ry=80), ears=dict(kind='wide', size=1.0),
         tail=dict(path=tail_r(50, -80, 200), w=20),
         face=dict(eyes=('bigdot', 'dot'), mouth='tongue', wn=2, wl=0.55, es=0.95)),
    dict(ten='Lực Sĩ', mo_ta='vai u thịt bắp, nhe nanh',
         fur='#E57F26', body=('poly', [(0, -290), (100, -278), (96, -220), (54, -140), (40, -96), (0, -90)]), stripes=True,
         legs=dict(x=26, len=100, w=28), arms=dict(x=88, y=-262, len=86, w=38, L='flex', R='flex'),
         head=dict(y=-345, rx=82, ry=72), ears=dict(kind='tri', size=0.8),
         tail=dict(path=tail_r(40, -120, 120), w=18),
         face=dict(eyes=('dot', 'dot'), es=0.9, brows=(10, 10), bw=9, mouth='tooth', mw=1.1)),
    dict(ten='Mochi', mo_ta='đầu liền thân, ngủ gật',
         fur='#F4B97C', body=('super', -150, 140, 140, 2.0), merge=True,
         legs=dict(x=56, len=26, w=40), arms=dict(x=118, y=-170, len=36, w=32, L='stub', R='stub'),
         head=dict(y=-190, rx=128, ry=110), ears=dict(kind='round', size=1.05, yb=0.9, x=0.6),
         tail=dict(path=tail_r(110, -80, 100), w=24),
         face=dict(eyes=('sleepy', 'sleepy'), mouth='w', zzz=True, blush=True, wn=2, wl=0.45, ey=-0.05, muzzle=False)),
    dict(ten='Cao Kều', mo_ta='gầy cao, liếc xéo, tàn nhang',
         fur='#EA8B3A', body=('poly', [(0, -320), (40, -312), (46, -240), (40, -170), (30, -130), (0, -126)]),
         legs=dict(x=20, len=134, w=28), arms=dict(x=30, y=-296, len=100, w=22, L='down', R='point'),
         head=dict(y=-380, rx=84, ry=76, dx=10), ears=dict(kind='long', size=0.75),
         tail=dict(path=tail_r(30, -150, 170), w=16, tip=True),
         face=dict(eyes=('smug', 'cat'), mouth='smirk', freckle=True, gaze=-0.6, lid=0.42, iris='#9CC93A', brows=(4, -4)),
         shw=70),
]


def draw_card(d, CW, CH, avatar=False):
    cv = Image.new('RGBA', (CW * SS, CH * SS), hx('#F8EFDC') + (255,))
    if not avatar:
        Char(cv, CW / 2 - 14, CH - 40, 0.82, d).draw()
        return cv.resize((CW, CH), Image.LANCZOS).convert('RGB')
    R, cx, cy = CW / 2 - 18, CW / 2, CH / 2
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    k = 0.70 * R / d['head']['rx']
    hy = d['head']['y']
    c = Char(lay, cx - d['head'].get('dx', 0) * k, cy + 0.16 * R - hy * k, k, d)
    c.draw()
    dr = ImageDraw.Draw(cv)
    dr.ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=hx('#14110F') + (255,))
    for rr in (R * 0.85, R * 0.7, R * 0.55):
        dr.ellipse([(cx - rr) * SS, (cy - rr) * SS, (cx + rr) * SS, (cy + rr) * SS], outline=hx('#3A2F1E') + (255,), width=3 * SS)
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=255)
    arr = np.asarray(lay).copy()
    arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
    cv.alpha_composite(Image.fromarray(arr, 'RGBA'))
    dr = ImageDraw.Draw(cv)
    dr.ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], outline=hx('#C9A24A') + (255,), width=7 * SS)
    return cv.resize((CW, CH), Image.LANCZOS).convert('RGB')


def main():
    os.makedirs(OUT, exist_ok=True)
    CW, CH, AH, LAB, TOP = 340, 470, 300, 76, 96
    cols = 5
    rows = math.ceil(len(CHARS) / cols)
    W, H = cols * CW, TOP + rows * (CH + AH + LAB)
    img = Image.new('RGB', (W, H), hx('#F2E6CC'))
    dr = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf'), 48)
    f_n = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26)
    f_d = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf'), 18)
    dr.text((30, 22), 'MÈO NGHỆ cách điệu – 10 nhân vật', font=f_t, fill=hx('#14110F'))
    only = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else range(len(CHARS))
    for i in only:
        d = CHARS[i]
        x0 = (i % cols) * CW
        y0 = TOP + (i // cols) * (CH + AH + LAB)
        img.paste(draw_card(d, CW - 16, CH), (x0 + 8, y0))
        img.paste(draw_card(d, CW - 16, AH, avatar=True), (x0 + 8, y0 + CH))
        dr.rectangle([x0 + 8, y0, x0 + CW - 9, y0 + CH + AH - 1], outline=hx('#C9A24A'), width=2)
        dr.text((x0 + CW / 2, y0 + CH + AH + 24), f'{i + 1} · {d["ten"]}', font=f_n, fill=hx('#B3261E'), anchor='mm')
        dr.text((x0 + CW / 2, y0 + CH + AH + 54), d['mo_ta'], font=f_d, fill=hx('#4A3E3A'), anchor='mm')
    p = os.path.join(OUT, 'cach-dieu-10.jpg')
    img.save(p, quality=90)
    print(p)


if __name__ == '__main__':
    main()
