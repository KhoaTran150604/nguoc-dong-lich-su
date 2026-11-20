"""Cảnh THỬ phong cách hoạt họa 2D kiểu "rối cắt giấy" (cut-out) – 10 giây.

Chiều trên bãi sông Bạch Đằng (minh họa, không phải tái hiện chính xác):
lính Việt (áo đỏ sơn mài, khăn vàng, khiên mây) đánh lính Nam Hán (áo chàm, mũ sắt)
trên bãi bùn; xa xa thuyền mắc cọc lúc nước rút.

Kỹ thuật: mỗi bộ phận là một đa giác tô 3 tông (nền / bóng / viền sáng ngược nắng),
viền mực, bóng đổ xuống đất, camera lia + zoom, lớp nền thị sai, nhân vật cử động
"on twos" (15 tư thế/giây) cho cảm giác hoạt hình, vệt chém, tia lửa, bụi.

Chạy:  python3 scripts/hoathinh/thu_danh_nhau.py --nhap        (540p nháp)
       python3 scripts/hoathinh/thu_danh_nhau.py               (1080p)
       thêm --khung 5.5  để xuất 1 khung hình
"""
import argparse
import glob
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FPS, DUR = 30, 10.0
POSE_FPS = 15
CAM_MAX = 420

LIGHT = np.array([0.74, -0.67])
LIGHT /= np.linalg.norm(LIGHT)


def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


SUN = hx('#FFD596')
DUSK = hx('#3A1830')
INK = hx('#2A141A')
HAZE = hx('#E9A06E')


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


# ------------------------------------------------------------------ vẽ tô 3 tông
def _poly_mask(pts, w, h):
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
    return np.asarray(im) > 0


def _shift(m, dx, dy):
    return np.roll(np.roll(m, int(round(dy)), 0), int(round(dx)), 1)


def _erode(m, r):
    if r < 1:
        return m
    out = m.copy()
    d = max(1, int(round(r * 0.7)))
    for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r), (d, d), (-d, d), (d, -d), (-d, -d)):
        out &= _shift(m, dx, dy)
    return out


def paint_mask(cv, x0, y0, m, base, sh=0, rw=0, ow=0, shade_c=None, rim_c=None, ink=INK):
    """Tô mặt nạ m (bool) tại (x0,y0): nền + bóng (phía khuất nắng) + viền sáng + viền mực."""
    h, w = m.shape
    if not m.any():
        return
    box = (x0, y0, x0 + w, y0 + h)
    four = cv.mode == 'RGBA'

    def col(c):
        return tuple(c) + (255,) if four else tuple(c)

    cv.paste(col(base), box, Image.fromarray((m * 255).astype(np.uint8)))
    if sh > 0:
        s = m & ~_shift(m, LIGHT[0] * sh, LIGHT[1] * sh)
        cv.paste(col(shade_c or mix(base, DUSK, 0.42)), box, Image.fromarray((s * 255).astype(np.uint8)))
    if rw > 0:
        r = m & ~_shift(m, -LIGHT[0] * rw, -LIGHT[1] * rw)
        cv.paste(col(rim_c or mix(base, SUN, 0.62)), box, Image.fromarray((r * 255).astype(np.uint8)))
    if ow > 0:
        o = m & ~_erode(m, ow)
        cv.paste(col(ink), box, Image.fromarray((o * 255).astype(np.uint8)))


def paint(cv, pts, base, sh=0, rw=0, ow=0, **kw):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = int(max(sh, rw, ow)) + 3
    x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
    x1, y1 = int(max(xs)) + pad + 1, int(max(ys)) + pad + 1
    if x1 < 0 or y1 < 0 or x0 > cv.width or y0 > cv.height:
        return
    m = _poly_mask([(x - x0, y - y0) for x, y in pts], x1 - x0, y1 - y0)
    paint_mask(cv, x0, y0, m, base, sh, rw, ow, **kw)


# ------------------------------------------------------------------ hình cơ bản
def circ(cx, cy, rx, ry=None, n=26, a0=0.0, a1=2 * math.pi):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-6 else 1))]


def capsule(a, b, ra, rb, n=7):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    pts = []
    for i in range(n + 1):
        t = ang + math.pi / 2 + math.pi * i / n
        pts.append((a[0] + ra * math.cos(t), a[1] + ra * math.sin(t)))
    for i in range(n + 1):
        t = ang - math.pi / 2 + math.pi * i / n
        pts.append((b[0] + rb * math.cos(t), b[1] + rb * math.sin(t)))
    return pts


def add(p, q, k=1.0):
    return (p[0] + q[0] * k, p[1] + q[1] * k)


def dirv(deg):  # 0 = thẳng xuống, 90 = về phía trước, 180 = thẳng lên
    r = math.radians(deg)
    return (math.sin(r), math.cos(r))


# ------------------------------------------------------------------ nhân vật
VIET = dict(tunic='#A3302A', pants='#E6D3AA', belt='#C9A24A', skin='#E2AC7E', hair='#2B1B18',
            band='#D9A440', shield='#C99A55', sline='#7A4E28', blade='#E6E0D0', shaft='#6B4326')
HAN = dict(tunic='#33416A', pants='#4E4140', belt='#7A2E28', skin='#DDA77C', vest='#7A7680',
           helmet='#57545E', shield='#6A2E24', sline='#C9A24A', blade='#D8D6D2', shaft='#5A3A26')

GUARD = dict(leg=(22, 6, -24, -10), lam=6, tilt=0, armN=(55, 88), armF=(30, 100), w=135,
             dx=0, phi=0, shout=0)
ATK = [(0.0, {}), (0.30, dict(armF=(165, 205), w=235, lam=-6, dx=-6, leg=(18, 4, -28, -14), shout=1)),
       (0.40, dict(armF=(88, 70), w=92, lam=20, dx=16, leg=(34, 10, -30, -16), shout=1)),
       (0.58, dict(armF=(70, 52), w=70, lam=16, dx=16, leg=(34, 10, -30, -16), shout=1)), (1.0, {})]
DEF = [(0.0, {}), (0.28, dict(armN=(100, 150), lam=2)),
       (0.42, dict(armN=(100, 152), lam=-10, dx=-12, tilt=-8, leg=(26, 8, -20, -6))),
       (0.62, dict(armN=(80, 120), lam=0, dx=-8)), (1.0, {})]
SPEAR_GUARD = dict(armN=(62, 84), armF=(38, 88), w=96)


def full(d, base=GUARD):
    o = dict(base)
    o.update(d)
    return o


def lerp_val(a, b, t):
    if isinstance(a, tuple):
        return tuple(x + (y - x) * t for x, y in zip(a, b))
    return a + (b - a) * t


def keyed(u, keys, base=GUARD):
    for (u0, d0), (u1, d1) in zip(keys, keys[1:]):
        if u0 <= u <= u1:
            a, b = full(d0, base), full(d1, base)
            t = ease((u - u0) / (u1 - u0))
            return {k: lerp_val(a[k], b[k], t) for k in a}
    return full({}, base)


class Char:
    def __init__(self, x, y, team, f, weapon='sword', role=None, period=1.5, phase=0.0, partner=None):
        self.x, self.y, self.team, self.f = x, y, team, f
        self.weapon, self.role, self.period, self.phase = weapon, role, period, phase
        self.s = 0.5 + (y - 600) / 480 * 1.1
        haze = clamp((900 - y) / 300) * 0.5
        pal = VIET if team == 'viet' else HAN
        self.c = {k: mix(hx(v), HAZE, haze) for k, v in pal.items()}
        self.ink = mix(INK, HAZE, haze * 0.6)
        self.path = None   # cho lính chạy: (t0, x0, t1, x1)
        self.fall_t = None

    # ---- tư thế theo thời gian
    def pose(self, t):
        base = full(SPEAR_GUARD) if self.weapon == 'spear' else dict(GUARD)
        P = dict(base)
        X = self.x
        if self.role in ('left', 'right'):
            n = math.floor(t / self.period + self.phase)
            u = (t / self.period + self.phase) - n
            attacking = (n % 2 == 0) == (self.role == 'left')
            P = keyed(u, ATK if attacking else DEF, base)
            P['_atk'] = attacking
            P['_u'] = u
        elif self.role == 'runner':
            t0, x0, t1, x1 = self.path
            if t < t0:
                X = x0
            elif t < t1:
                X = x0 + (x1 - x0) * (t - t0) / (t1 - t0)
                v = (t - t0) / 0.42
                s1 = math.sin(2 * math.pi * v)
                c1 = math.cos(2 * math.pi * v)
                tn, tf = 36 * s1, -36 * s1
                P = full(dict(leg=(tn, tn - 55 * max(0, c1) - 5, tf, tf - 55 * max(0, -c1) - 5),
                              lam=20, armN=(64, 82), armF=(40, 86), w=94, shout=1), base)
            else:
                X = x1
                k = clamp((t - t1) / 0.18)
                k2 = clamp((t - t1 - 0.5) / 0.5)
                thr = full(dict(armN=(88, 94), armF=(80, 92), w=93, lam=28, dx=34,
                                leg=(42, 12, -40, -22), shout=1), base)
                P = {kk: lerp_val(lerp_val(base[kk], thr[kk], ease(k)), base[kk], ease(k2) * 0.6) for kk in base}
        elif self.role == 'victim':
            P = dict(base)
            if t > self.fall_t - 0.35:
                P = full(dict(armN=(100, 150), lam=0), base)
            if t >= self.fall_t:
                k = clamp((t - self.fall_t) / 0.42)
                kk = 1 - (1 - k) ** 3
                bounce = math.sin(clamp((t - self.fall_t - 0.42) / 0.25) * math.pi) * 6
                P = full(dict(armN=(135, 175), armF=(150, 195), w=250, lam=-14, tilt=-20,
                              leg=(30, 30, 10, 20), shout=1), base)
                P['phi'] = -84 * kk + bounce
                P['dx'] = -30 * kk
        else:  # đứng thủ, thở nhẹ
            P['lam'] = 6 + 2 * math.sin(t * 3 + self.phase * 6)
        P['X'] = X
        return P

    # ---- dựng các bộ phận (toạ độ cục bộ, mặt hướng phải, y hướng xuống, gốc ở chân)
    def parts(self, t):
        P = self.pose(t)
        c, team = self.c, self.team
        tn, sn, tf, sf = P['leg']
        L1, L2 = 52, 50
        dn = L1 * math.cos(math.radians(tn)) + L2 * math.cos(math.radians(sn))
        df = L1 * math.cos(math.radians(tf)) + L2 * math.cos(math.radians(sf))
        hip = (P['dx'], -max(dn, df))

        def leg(a, b):
            k = add(hip, dirv(a), L1)
            return k, add(k, dirv(b), L2)

        kN, aN = leg(tn, sn)
        kF, aF = leg(tf, sf)
        lam = math.radians(P['lam'])
        up = (math.sin(lam), -math.cos(lam))
        fw = (math.cos(lam), math.sin(lam))

        def T(a, b):  # toạ độ theo thân: a dọc 'phía trước', b dọc 'lên'
            return (hip[0] + a * fw[0] + b * up[0], hip[1] + a * fw[1] + b * up[1])

        neck = T(0, 78)
        tl = lam + math.radians(P['tilt'])
        head = (neck[0] + 30 * math.sin(tl), neck[1] - 30 * math.cos(tl))
        shN, shF = T(3, 70), T(-5, 70)
        eN = add(shN, dirv(P['armN'][0]), 40)
        hN = add(eN, dirv(P['armN'][1]), 38)
        eF = add(shF, dirv(P['armF'][0]), 40)
        hF = add(eF, dirv(P['armF'][1]), 38)
        wd = dirv(P['w'])
        wp = (wd[1], -wd[0])
        ops = []  # (pts, màu, sh, rw, ow)  hoặc ('flat', pts, màu)
        fl = t * 9 + self.phase * 7
        STEEL = c['blade']

        def body(pts, col, sh=7, rw=3.2, ow=2.6):
            ops.append(('p', pts, col, sh, rw, ow))

        def flat(pts, col):
            ops.append(('f', pts, col))

        # vũ khí + tay xa
        if self.weapon == 'spear':
            a, b = add(hF, wd, -70), add(hF, wd, 150)
            body(capsule(a, b, 3.2, 3.2, 3), c['shaft'], 3, 1.6, 2)
            tip = add(b, wd, 30)
            body([add(b, wp, 6), tip, add(b, wp, -6), add(b, wd, -6)], STEEL, 3, 2.2, 2)
            tipP, midP = tip, add(hF, wd, 90)
        else:
            curve = 9 if team == 'viet' else 0
            blade = []
            for i in range(9):
                u = i / 8
                p = add(add(hF, wd, 12 + 66 * u), wp, -curve * u * u + 0)
                blade.append(add(p, wp, 4.2 * (1 - 0.6 * u)))
            for i in range(8, -1, -1):
                u = i / 8
                p = add(add(hF, wd, 12 + 66 * u), wp, -curve * u * u)
                blade.append(add(p, wp, -3.4 * (1 - 0.5 * u)))
            blade.insert(9, add(add(hF, wd, 84), wp, -curve - 1))
            body(blade, STEEL, 3, 2.4, 2)
            body(capsule(add(hF, wp, 9), add(hF, wp, -9), 3, 3, 3), c['belt'], 2, 1.4, 1.8)
            tipP, midP = add(add(hF, wd, 80), wp, -curve), add(hF, wd, 34)
        body(capsule(shF, eF, 9.5, 8), c['tunic'])
        body(capsule(eF, hF, 8, 7), c['tunic'])
        body(circ(hF[0], hF[1], 7.5, n=12), c['skin'], 3, 2, 2)
        # chân
        for k, a_, back in ((kF, aF, True), (kN, aN, False)):
            col = mix(c['pants'], DUSK, 0.18) if back else c['pants']
            body(capsule(hip, k, 11, 9.5), col)
            body(capsule(k, a_, 9.5, 8), col)
            body(capsule(a_, add(a_, (1, 0.12), 15), 7, 6, 4), c['hair'] if team == 'viet' else hx('#2E2224'), 3, 2, 2.4)
        # áo
        wv = math.sin(fl) * 4
        robe = [T(-15, 74), T(12, 74), T(17, 50), T(15, 18), T(27 + wv, -40), T(0, -45 - wv * 0.5),
                T(-31 - wv, -37), T(-17, 18), T(-19, 50)]
        body(robe, c['tunic'], 8, 3.4, 2.8)
        if team == 'han':
            body([T(-17, 70), T(15, 68), T(16, 22), T(-18, 22)], c['vest'], 6, 3, 2.4)
            for b in (60, 50, 40, 30):
                ops.append(('l', [T(-15, b), T(14, b)], mix(c['vest'], DUSK, 0.5), 1.6))
        body([T(-18, 24), T(16, 24), T(16, 14), T(-18, 14)], c['belt'], 3, 2, 2.2)
        # đầu
        hxp, hyp = head
        if team == 'viet':
            tail = [(hxp - 22, hyp - 6), (hxp - 50, hyp + 2 + math.sin(fl) * 5),
                    (hxp - 46, hyp + 9 + math.sin(fl + 1) * 5), (hxp - 20, hyp + 2)]
            body(tail, c['band'], 3, 2, 2)
        body(circ(hxp, hyp, 25), c['skin'], 7, 3, 2.6)
        if team == 'viet':
            body(circ(hxp - 2, hyp - 3, 26.5, 26, 14, math.pi * 0.98, math.pi * 2.02), c['hair'], 4, 2.6, 2.4)
            body(circ(hxp - 18, hyp - 22, 9, n=12), c['hair'], 3, 2, 2.2)
            body([(hxp - 27, hyp - 12), (hxp + 24, hyp - 14), (hxp + 25, hyp - 6), (hxp - 26, hyp - 3)],
                 c['band'], 3, 2, 2.2)
        else:
            body(circ(hxp - 1, hyp - 4, 28, 27, 16, math.pi * 0.95, math.pi * 2.05), c['helmet'], 5, 3, 2.6)
            body([(hxp - 26, hyp - 4), (hxp - 32, hyp + 20), (hxp - 10, hyp + 18), (hxp - 8, hyp - 4)],
                 c['helmet'], 4, 2, 2.4)
            body([(hxp - 4, hyp - 30), (hxp, hyp - 46), (hxp + 4, hyp - 30)], c['belt'], 2, 2, 2)
            body([(hxp - 30, hyp - 4), (hxp + 30, hyp - 6), (hxp + 30, hyp - 1), (hxp - 30, hyp + 1)],
                 mix(c['helmet'], DUSK, 0.2), 2, 1.6, 2)
        # mặt
        flat(circ(hxp + 11, hyp + 1, 2.8, 3.6, 10), INK)
        ops.append(('l', [(hxp + 4, hyp - 8), (hxp + 17, hyp - 4)], INK, 3.4))
        if P['shout'] > 0.5:
            flat(circ(hxp + 15, hyp + 12, 5, 6.5, 12), hx('#5A1A1E'))
        else:
            ops.append(('l', [(hxp + 11, hyp + 13), (hxp + 19, hyp + 12)], INK, 2))
        flat(circ(hxp - 4, hyp + 3, 3.4, 4.8, 10), mix(c['skin'], DUSK, 0.3))
        # tay gần + khiên
        body(capsule(shN, eN, 9.5, 8), c['tunic'])
        body(capsule(eN, hN, 8, 7), c['tunic'])
        body(circ(hN[0], hN[1], 7.5, n=12), c['skin'], 3, 2, 2)
        shieldP = hN
        if self.weapon != 'spear':
            sc = add(hN, (2, 0))
            if team == 'viet':
                body(circ(sc[0], sc[1], 24, 34), c['shield'], 7, 3.4, 2.8)
                for r in (0.7, 0.42):
                    ops.append(('l', circ(sc[0], sc[1], 24 * r, 34 * r) + [circ(sc[0], sc[1], 24 * r, 34 * r)[0]],
                                c['sline'], 1.8))
                body(circ(sc[0], sc[1], 5, 6, 10), c['sline'], 2, 1.6, 1.8)
            else:
                body([(sc[0] - 17, sc[1] - 36), (sc[0] + 17, sc[1] - 33), (sc[0] + 17, sc[1] + 33),
                      (sc[0] - 17, sc[1] + 36)], c['shield'], 7, 3.4, 2.8)
                body(circ(sc[0], sc[1], 7, n=12), c['sline'], 2, 2, 1.8)
            shieldP = sc

        # xoay (ngã) + lật hướng + đặt vào cảnh
        phi = math.radians(P['phi'])
        lift = 16 * abs(math.sin(phi))
        f, s, X, Y = self.f, self.s, P['X'], self.y

        def tr(p):
            x, y = p
            x2 = x * math.cos(phi) - y * math.sin(phi)
            y2 = x * math.sin(phi) + y * math.cos(phi) - lift
            return (X + f * x2 * s, Y + y2 * s)

        out = []
        for op in ops:
            if op[0] == 'p':
                out.append(('p', [tr(q) for q in op[1]], op[2], op[3] * s, op[4] * s, op[5] * s))
            elif op[0] == 'f':
                out.append(('f', [tr(q) for q in op[1]], op[2]))
            else:
                out.append(('l', [tr(q) for q in op[1]], op[2], op[3] * s))
        meta = dict(tip=tr(tipP), mid=tr(midP), shield=tr(shieldP), feet=(X + f * P['dx'] * s, Y), P=P)
        return out, meta


# ------------------------------------------------------------------ dàn cảnh
def make_cast():
    cast = []

    def pair(xl, xr, y, period, phase):
        a = Char(xl, y, 'viet', 1, role='left', period=period, phase=phase)
        b = Char(xr, y, 'han', -1, role='right', period=period, phase=phase)
        cast.extend([a, b])
        return a, b

    A = pair(600, 800, 1000, 1.5, 0.05)
    pair(1170, 1320, 830, 1.35, 0.45)
    pair(380, 465, 690, 1.25, 0.7)
    pair(900, 982, 662, 1.6, 0.2)
    pair(1480, 1572, 705, 1.45, 0.85)
    pair(2060, 2148, 672, 1.3, 0.35)
    pair(1960, 2080, 780, 1.55, 0.6)
    run = Char(1240, 935, 'viet', 1, weapon='spear', role='runner', phase=0.3)
    run.path = (2.3, 1180, 5.25, 1590)
    vic = Char(1760, 930, 'han', -1, role='victim', phase=0.1)
    vic.fall_t = 5.5
    cast += [run, vic]
    return cast, A


CAST, PAIR_A = make_cast()


def hit_events():
    ev = []
    a, b = PAIR_A
    t = 0.0
    while t < DUR:
        n = math.floor(t / a.period + a.phase)
        th = (n + 0.40 - a.phase) * a.period
        if 0 <= th < DUR and (not ev or abs(ev[-1][0] - th) > 0.1):
            ev.append((th, 7.0, 'A'))
        t += a.period
    ev.append((5.5, 12.0, 'V'))
    return ev


HITS = hit_events()


def cam(t):
    k = ease(t / DUR)
    return CAM_MAX * (0.5 * k + 0.5 * (t / DUR)), 1.03 + 0.06 * k


# ------------------------------------------------------------------ nền (dựng 1 lần)
def rng(seed):
    return np.random.default_rng(seed)


def build_layers(K):
    W, H = int(1920 * K), int(1080 * K)
    L = {}

    def layer(p):
        return Image.new('RGBA', (int((1920 + CAM_MAX * p + 80) * K), H), (0, 0, 0, 0))

    # trời
    p = 0.04
    wl = int((1920 + CAM_MAX * p + 80) * K)
    ys = np.arange(H) / K
    stops = [(0, '#2B1A3A'), (200, '#6A3050'), (360, '#C25A52'), (470, '#F4A060'), (1080, '#F6B070')]
    cols = np.zeros((H, 3))
    for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
        m = (ys >= y0) & (ys <= y1)
        tt = ((ys[m] - y0) / (y1 - y0))[:, None]
        cols[m] = np.array(hx(c0)) * (1 - tt) + np.array(hx(c1)) * tt
    sky = np.repeat(cols[:, None, :], wl, 1)
    yy, xx = np.mgrid[0:H, 0:wl] / K
    d = np.hypot(xx - 1350, yy - 410)
    glow = np.clip(1 - d / 520, 0, 1) ** 2.2
    sky = sky + (np.array(SUN) - sky) * glow[..., None] * 0.75
    sky = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8), 'RGB')
    ImageDraw.Draw(sky).ellipse([(1350 - 58) * K, (410 - 58) * K, (1350 + 58) * K, (410 + 58) * K], fill=hx('#FFF0C6'))
    L['sky'] = (sky, p)

    # mây
    p = 0.1
    im = layer(p)
    r = rng(3)
    for cx, cy, wd, sc in ((260, 150, 520, 1.0), (980, 95, 640, 1.1), (1700, 175, 560, 0.9),
                           (620, 300, 380, 0.7), (1450, 285, 300, 0.6), (2050, 90, 420, 0.9)):
        x0, y0 = int((cx - wd / 2 - 70) * K), int((cy - 120 * sc) * K)
        w_, h_ = int((wd + 140) * K), int(200 * sc * K)
        m = Image.new('L', (w_, h_), 0)
        dr = ImageDraw.Draw(m)
        n = 9
        for i in range(n):
            u = i / (n - 1)
            bx = 70 + u * wd
            rr = (34 + 46 * math.sin(math.pi * u) + r.uniform(-8, 12)) * sc
            by = 120 * sc - rr * 0.55
            dr.ellipse([(bx - rr) * K, (by - rr) * K, (bx + rr) * K, (by + rr) * K], fill=255)
        dr.rectangle([70 * K, 120 * sc * K - 2, (70 + wd) * K, 120 * sc * K + 14 * K], fill=0)
        dr.ellipse([60 * K, (120 * sc - 26) * K, (80 + wd) * K, (120 * sc + 2) * K], fill=255)
        base = mix(hx('#A84E66'), hx('#F09A70'), clamp(1 - abs(cx - 1350) / 900) * 0.5)
        paint_mask(im, x0, y0, np.asarray(m) > 0, base, 16 * K, 6 * K, 2.2 * K,
                   rim_c=hx('#FFC890'), ink=mix(base, DUSK, 0.5))
    L['cloud'] = (im, p)

    # núi đá vôi
    def karst(im, cx, base, w, h, col, seed, rimw, ow):
        r = rng(seed)
        pts = []
        n = 22
        for i in range(n + 1):
            th = math.pi * i / n
            c_ = math.cos(th)
            x = cx + (w / 2) * np.sign(c_) * abs(c_) ** 0.55 + r.uniform(-3, 3)
            y = base - h * abs(math.sin(th)) ** 0.3 + r.uniform(-4, 4)
            pts.append((x * K, y * K))
        pts = [(pts[0][0], (base + 30) * K)] + pts + [(pts[-1][0], (base + 30) * K)]
        paint(im, pts, col, 18 * K, rimw * K, ow * K, rim_c=hx('#FFC08A'), ink=mix(col, DUSK, 0.45))

    for p, col, base, items in (
            (0.18, hx('#B06070'), 478, [(120, 120, 150), (330, 90, 210), (700, 160, 140), (1040, 110, 120),
                                        (1260, 140, 175), (1640, 100, 230), (1900, 150, 160), (2120, 120, 190)]),
            (0.32, hx('#7E3E52'), 485, [(30, 150, 250), (450, 130, 190), (820, 110, 150), (1580, 140, 210),
                                        (1830, 100, 160), (2180, 170, 270)])):
        im = layer(p)
        for i, (cx, w, h) in enumerate(items):
            karst(im, cx, base, w, h, col, 10 + i + int(p * 100), 4, 2)
        L['m%.2f' % p] = (im, p)

    # sông + cọc + thuyền
    p = 0.6
    im = layer(p)
    dr = ImageDraw.Draw(im)
    for yv in range(470, 600):
        tt = (yv - 470) / 130
        dr.line([(0, yv * K), (im.width, yv * K)], fill=mix(hx('#F2A462'), hx('#B8604A'), tt) + (255,),
                width=int(K) + 1)
    shore = [(0, 482 * K)] + [(x * K, (480 + 5 * math.sin(x / 70)) * K) for x in range(0, 2400, 40)] + \
            [(im.width, 470 * K), (im.width, 460 * K), (0, 460 * K)]
    dr.polygon(shore, fill=hx('#5E2E40') + (255,))
    r = rng(7)
    for i in range(70):
        sx = 760 + i * 22 + r.uniform(-8, 8)
        sy = 535 + r.uniform(-30, 45)
        hgt = r.uniform(26, 52) * (0.7 + (sy - 500) / 200)
        lean = r.uniform(10, 26)
        top = (sx + lean * 0.6, sy - hgt)
        pts = [((sx - 3) * K, sy * K), ((sx + 3) * K, sy * K), ((top[0] + 2) * K, (top[1] + 4) * K),
               (top[0] * K, (top[1] - 4) * K), ((top[0] - 2) * K, (top[1] + 4) * K)]
        paint(im, pts, hx('#3E2026'), 3 * K, 1.6 * K, 1.2 * K, rim_c=hx('#FFB070'))
        dr.ellipse([(sx - 9) * K, (sy - 2) * K, (sx + 9) * K, (sy + 3) * K], outline=hx('#FFD39A') + (200,),
                   width=max(1, int(K)))

    def junk(cx, cy, sc, tilt, sail=True):
        a = math.radians(tilt)

        def R(x, y):
            return ((cx + (x * math.cos(a) - y * math.sin(a)) * sc) * K,
                    (cy + (x * math.sin(a) + y * math.cos(a)) * sc) * K)
        hull = [R(-120, -40), R(-90, -18), R(80, -18), R(125, -48), R(110, -10), R(70, 18), R(-80, 18), R(-112, -6)]
        if sail:
            sl = [R(-30, -40), R(-50, -190), R(30, -205), R(40, -40)]
            paint(im, sl, hx('#8E3328'), 10 * K * sc, 4 * K * sc, 2.4 * K * sc, rim_c=hx('#FF9C6A'))
            for k in range(1, 6):
                yk = -40 - k * 30
                ImageDraw.Draw(im).line([R(-32 - k * 3.5, yk), R(38 - k * 1.5, yk - k * 2.5)],
                                        fill=hx('#4E1A1C') + (255,), width=max(1, int(2 * K * sc)))
        else:
            paint(im, [R(-6, -20), R(4, -20), R(14, -120), R(4, -118)], hx('#3E2026'), 3 * K, 2 * K, 1.5 * K)
        paint(im, hull, hx('#4E2A26'), 14 * K * sc, 4 * K * sc, 2.6 * K * sc, rim_c=hx('#FFA870'))
        paint(im, [R(-70, -18), R(-66, -50), R(-20, -52), R(-18, -18)], hx('#6E3A2C'), 8 * K * sc, 3 * K * sc,
              2.2 * K * sc, rim_c=hx('#FFB070'))
    junk(1180, 545, 0.55, -9)
    junk(1560, 528, 0.45, 12, sail=False)
    junk(1880, 552, 0.6, 7)
    junk(2200, 530, 0.4, -5)
    L['river'] = (im, p)

    # bãi bùn
    p = 1.0
    im = layer(p)
    dr = ImageDraw.Draw(im)
    edge = [(x * K, (592 + 9 * math.sin(x / 95) + 4 * math.sin(x / 31)) * K) for x in range(-20, 2500, 20)]
    for yv in range(580, 1080, 2):
        tt = (yv - 580) / 500
        dr.line([(0, yv * K), (im.width, yv * K)], fill=mix(hx('#D08650'), hx('#9A5034'), tt ** 0.8) + (255,),
                width=int(2 * K) + 1)
    # xoá phần trên mép bờ
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).polygon(edge + [(im.width, im.height), (0, im.height)], fill=255)
    im.putalpha(m)
    dr = ImageDraw.Draw(im)
    dr.line(edge, fill=hx('#FFC88A') + (255,), width=int(3 * K))
    r = rng(11)
    for i in range(55):  # mảng bùn ướt, vũng nước
        cx, cy = r.uniform(0, 2400), r.uniform(620, 1060)
        sc = 0.5 + (cy - 600) / 480 * 1.1
        w, h = r.uniform(60, 180) * sc, r.uniform(10, 26) * sc
        if r.random() < 0.3:
            paint(im, circ(cx * K, cy * K, w * K, h * K, 20), hx('#F2AA6A'), 0, 3 * K, 1.6 * K,
                  rim_c=hx('#FFE0A8'), ink=hx('#7A3A2A'))
        else:
            paint(im, circ(cx * K, cy * K, w * K, h * K, 20), mix(hx('#9A5034'), DUSK, 0.15), 0, 0, 0)
    for i in range(240):  # sỏi
        cx, cy = r.uniform(0, 2400), r.uniform(605, 1075)
        sc = 0.5 + (cy - 600) / 480 * 1.1
        rr = r.uniform(2, 6) * sc
        paint(im, circ(cx * K, cy * K, rr * 1.4 * K, rr * K, 8), hx('#B06A44'), 2 * K * sc, 1.2 * K * sc,
              0.8 * K * sc, rim_c=hx('#FFC890'))
    for i in range(16):  # giáo gãy, tên cắm
        cx, cy = r.uniform(80, 2350), r.uniform(640, 1060)
        sc = 0.5 + (cy - 600) / 480 * 1.1
        if r.random() < 0.5:
            a = r.uniform(-0.3, 0.3)
            ln = r.uniform(60, 110) * sc
            p1 = (cx * K, cy * K)
            p2 = ((cx + math.cos(a) * ln) * K, (cy + math.sin(a) * ln * 0.3) * K)
            paint(im, capsule(p1, p2, 2.6 * sc * K, 2.6 * sc * K, 3), hx('#5A3A26'), 2 * K, 1.5 * K, 1.4 * K * sc)
        else:
            a = math.radians(r.uniform(-35, -10))
            ln = 34 * sc
            p1 = (cx * K, cy * K)
            p2 = ((cx - math.cos(a) * ln) * K, (cy + math.sin(a) * ln) * K)
            paint(im, capsule(p1, p2, 1.6 * sc * K, 1.6 * sc * K, 3), hx('#5A3A26'), 1, 1, 1.0 * K * sc)
            paint(im, circ(p2[0], p2[1], 4 * sc * K, 3 * sc * K, 8), hx('#E8D6B0'), 1, 1, 0.8 * K * sc)
    L['ground'] = (im, p)
    return L


# ------------------------------------------------------------------ một khung hình
G = {}


def init(K, OW, OH):
    G['K'], G['OW'], G['OH'] = K, OW, OH
    G['L'] = build_layers(K)
    yy, xx = np.mgrid[0:OH, 0:OW]
    nx, ny = (xx / OW - 0.5) * 2, (yy / OH - 0.5) * 2
    G['vig'] = (1 - 0.32 * np.clip((nx ** 2 * 0.8 + ny ** 2) ** 1.2, 0, 1.4))[..., None]
    d = np.hypot(xx / OW - 0.72, yy / OH - 0.36)
    G['glow'] = (np.clip(1 - d / 0.75, 0, 1) ** 2.5)[..., None]
    fp = os.path.join(ROOT, 'fonts', 'BeVietnamPro-Medium.ttf')
    G['font'] = ImageFont.truetype(fp, max(12, int(OH * 0.022)))


def shake(t):
    dx = dy = 0.0
    for th, amp, _ in HITS:
        if 0 <= t - th < 0.4:
            k = math.exp(-(t - th) * 11) * amp
            dx += k * math.sin((t - th) * 95)
            dy += k * math.cos((t - th) * 77)
    return dx, dy


def render(t):
    K = G['K']
    W, H = int(1920 * K), int(1080 * K)
    cx_, zoom = cam(t)
    tq = math.floor(t * POSE_FPS + 1e-6) / POSE_FPS
    cv = Image.new('RGB', (W, H))
    for name in ('sky', 'cloud', 'm0.18', 'm0.32', 'river', 'ground'):
        im, p = G['L'][name]
        ox = int(cx_ * p * K)
        crop = im.crop((ox, 0, ox + W, H))
        if name == 'sky':
            cv.paste(crop, (0, 0))
        else:
            cv.paste(crop, (0, 0), crop)
        if name == 'river':  # lấp lánh mặt nước
            dr = ImageDraw.Draw(cv)
            sxr = 1350 - cx_ * 0.6 + cx_ * 0.04
            r = rng(int(t * 6))
            for i in range(26):
                yv = 488 + i * 4.2
                xc = sxr + r.uniform(-60, 60) * (1 + i / 14)
                ln = r.uniform(14, 50) * (1 - i / 40)
                dr.line([((xc - ln) * K, yv * K), ((xc + ln) * K, yv * K)], fill=hx('#FFE6B0'),
                        width=max(1, int(1.6 * K)))
            # khói thuyền
            for j in range(7):
                age = (t * 0.35 + j / 7) % 1.0
                sx = (1560 - cx_ * 0.6 + 8 + age * 70) * K
                sy = (470 - age * 210) * K
                rr = (14 + age * 40) * K
                col = mix(hx('#7A4A5A'), hx('#C88A80'), age)
                paint(cv, circ(sx, sy, rr, rr * 0.85, 16), col, rr * 0.4, rr * 0.18, 1.6 * K, rim_c=hx('#FFC08A'),
                      ink=mix(col, DUSK, 0.4))

    # nhân vật: dựng, bóng đổ, vẽ theo chiều sâu
    built = []
    for ch in CAST:
        ops, meta = ch.parts(tq)
        built.append((ch, ops, meta))
    shadow = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(shadow)
    for ch, ops, meta in built:
        fx, fy = meta['feet']
        for op in ops:
            if op[0] != 'p':
                continue
            pts = []
            for x, y in op[1]:
                xr, yr = x - fx, y - fy
                pts.append(((fx + xr + yr * 0.62 - cx_) * K, (fy - yr * 0.2) * K))
            sd.polygon(pts, fill=150)
        sd.ellipse([(fx - 30 * ch.s - cx_) * K, (fy - 6 * ch.s) * K, (fx + 30 * ch.s - cx_) * K,
                    (fy + 7 * ch.s) * K], fill=200)
    sh_col = Image.new('RGB', (W, H), hx('#5A2234'))
    blend = Image.blend(cv, sh_col, 0.55)
    cv.paste(blend, (0, 0), shadow)

    fx_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fdr = ImageDraw.Draw(fx_layer)
    for ch, ops, meta in sorted(built, key=lambda b: b[0].y):
        for op in ops:
            if op[0] == 'p':
                pts = [((x - cx_) * K, y * K) for x, y in op[1]]
                paint(cv, pts, op[2], op[3] * K, op[4] * K, op[5] * K, ink=ch.ink)
            elif op[0] == 'f':
                ImageDraw.Draw(cv).polygon([((x - cx_) * K, y * K) for x, y in op[1]], fill=op[2])
            else:
                ImageDraw.Draw(cv).line([((x - cx_) * K, y * K) for x, y in op[1]], fill=op[2],
                                        width=max(1, int(op[3] * K)), joint='curve')
        P = meta['P']
        # vệt chém
        if P.get('_atk') and 0.33 <= P.get('_u', 0) <= 0.62:
            tips, mids = [], []
            for j in range(0, 4):
                _, m2 = ch.parts(tq - j / POSE_FPS * 0.5)
                tips.append(m2['tip'])
                mids.append(m2['mid'])
            poly = [((x - cx_) * K, y * K) for x, y in tips + mids[::-1]]
            fade = 1 - clamp((P['_u'] - 0.45) / 0.17)
            fdr.polygon(poly, fill=(255, 238, 200, int(170 * fade)))
    # tia lửa khi chém trúng khiên, bụi khi ngã
    for th, amp, who in HITS:
        dt = t - th
        if who == 'A' and 0 <= dt < 0.22:
            a, b = PAIR_A
            n = math.floor(th / a.period + a.phase + 1e-6)
            defender = b if n % 2 == 0 else a
            _, m2 = defender.parts(th)
            sx, sy = m2['shield']
            sx = (sx - cx_) * K
            sy *= K
            k = dt / 0.22
            R = (40 + 60 * k) * K * defender.s / 1.5
            star = []
            for i in range(16):
                ang = i * math.pi / 8 + 0.3
                rr = R if i % 2 == 0 else R * 0.32
                star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
            fdr.polygon(star, fill=(255, 246, 210, int(255 * (1 - k))), outline=(255, 150, 60, int(255 * (1 - k))))
            for i in range(7):
                ang = i * 0.9 + th
                d0, d1 = R * (0.6 + k), R * (0.9 + 1.6 * k)
                fdr.line([(sx + d0 * math.cos(ang), sy + d0 * math.sin(ang)),
                          (sx + d1 * math.cos(ang), sy + d1 * math.sin(ang))],
                         fill=(255, 210, 120, int(255 * (1 - k))), width=max(1, int(3 * K)))
        if who == 'V' and 0 <= dt < 0.25:
            vic = CAST[-1]
            _, m2 = vic.parts(th)
            sx, sy = m2['shield']
            sx = (sx - cx_) * K
            sy *= K
            k = dt / 0.25
            R = (60 + 90 * k) * K
            star = []
            for i in range(18):
                ang = i * math.pi / 9
                rr = R if i % 2 == 0 else R * 0.3
                star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
            fdr.polygon(star, fill=(255, 246, 210, int(230 * (1 - k))))
    # bụi: lính chạy + người ngã chạm đất
    puffs = []
    run, vic = CAST[-2], CAST[-1]
    t0, x0, t1, x1 = run.path
    for k in range(12):
        ts = t0 + k * 0.21
        if ts < t1 and 0 <= t - ts < 0.6:
            xs = x0 + (x1 - x0) * (ts - t0) / (t1 - t0) - 20
            puffs.append((xs, run.y, t - ts, 0.6, 26 * run.s))
    for k in range(6):
        if 0 <= t - (vic.fall_t + 0.4) < 0.9:
            puffs.append((vic.x + 30 + (k - 2.5) * 40 * vic.s, vic.y - 4, t - vic.fall_t - 0.4, 0.9, 30 * vic.s))
    for (px, py, age, life, rr) in puffs:
        k = age / life
        R = rr * (0.6 + 1.2 * k)
        dxp = (k * 20) * (1 if px > vic.x else -1)
        fdr.ellipse([((px + dxp - R - cx_) * K), (py - R * 1.3 - k * 20) * K, (px + dxp + R - cx_) * K,
                     (py + R * 0.2 - k * 20) * K], fill=(236, 184, 130, int(170 * (1 - k))))
    # tàn lửa / bụi bay trong nắng
    r = rng(5)
    for i in range(46):
        x0_, y0_, sp = r.uniform(0, 1920), r.uniform(300, 1080), r.uniform(10, 30)
        x = (x0_ + t * sp * 1.4 + 20 * math.sin(t + i)) % 1960
        y = (y0_ - t * sp) % 1000 + 80
        rr = r.uniform(1.2, 3.2) * K
        a = int(160 + 90 * math.sin(t * 5 + i))
        fdr.ellipse([x * K - rr, y * K - rr, x * K + rr, y * K + rr], fill=(255, 220, 160, max(0, min(255, a))))
    cvA = cv.convert('RGBA')
    cvA.alpha_composite(fx_layer)
    cv = cvA.convert('RGB')

    # cỏ lau tiền cảnh (thị sai 1.35, lay nhẹ)
    for bx_, side in ((60, 1), (2230, -1)):
        r = rng(int(bx_))
        for i in range(16):
            x = bx_ + r.uniform(-90, 90) - cx_ * 1.35
            ln = r.uniform(170, 330)
            sway = math.sin(t * 1.6 + i) * 10
            ang = math.radians(r.uniform(-22, 22) * side)
            pts_l, pts_r = [], []
            for j in range(9):
                u = j / 8
                px = x + math.sin(ang) * ln * u + sway * u * u
                py = 1100 - math.cos(ang) * ln * u
                wdt = 7 * (1 - u) + 0.6
                pts_l.append(((px - wdt) * K, py * K))
                pts_r.append(((px + wdt) * K, py * K))
            paint(cv, pts_l + pts_r[::-1], hx('#3C1E26'), 3 * K, 2.2 * K, 1.4 * K, rim_c=hx('#F59A60'))

    # camera: zoom + rung
    sx_, sy_ = shake(t)
    cw, chh = W / zoom, H / zoom
    cxc = W / 2 + sx_ * K
    cyc = H * 0.56 + sy_ * K
    x0 = clamp(cxc - cw / 2, 0, W - cw)
    y0 = clamp(cyc - chh / 2, 0, H - chh)
    out = cv.resize((G['OW'], G['OH']), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + chh))

    a = np.asarray(out).astype(np.float32)
    a = a + (np.array(hx('#FFC890')) - a) * G['glow'] * 0.28
    a = a * G['vig']
    a = a * 0.96 + np.array(DUSK) * 0.04
    a += np.random.default_rng(int(t * 1000)).normal(0, 3.2, a.shape[:2])[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    txt = 'Thử phong cách hoạt họa · minh họa'
    pad = int(G['OH'] * 0.03)
    d.text((pad + 1, G['OH'] - pad * 2 + 1), txt, font=G['font'], fill=(20, 10, 14))
    d.text((pad, G['OH'] - pad * 2), txt, font=G['font'], fill=hx('#F2E6CC'))
    return out


def job(i):
    out = render(i / FPS)
    out.save(os.path.join(G['dir'], 'f%04d.jpg' % i), quality=94)
    return i


def init_pool(K, OW, OH, d):
    init(K, OW, OH)
    G['dir'] = d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nhap', action='store_true', help='nháp 960x540')
    ap.add_argument('--khung', type=float, nargs='*', help='chỉ xuất các khung ở giây này')
    ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'thu-hoathinh'))
    a = ap.parse_args()
    OW, OH = (960, 540) if a.nhap else (1920, 1080)
    K = OH / 1080 * (1.0 if a.nhap else 2.0)
    os.makedirs(a.out, exist_ok=True)
    tag = 'nhap' if a.nhap else '1080p'
    if a.khung:
        init(K, OW, OH)
        for t in a.khung:
            p = os.path.join(a.out, 'khung-%s-%05.2f.jpg' % (tag, t))
            render(t).save(p, quality=92)
            print(p)
        return
    fdir = os.path.join(a.out, 'frames-' + tag)
    os.makedirs(fdir, exist_ok=True)
    for f in glob.glob(os.path.join(fdir, '*.jpg')):
        os.remove(f)
    n = int(DUR * FPS)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init_pool, initargs=(K, OW, OH, fdir)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n))):
            if k % 30 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    mp4 = os.path.join(a.out, 'thu-danh-nhau-%s.mp4' % tag)
    subprocess.run(['swift', os.path.join(ROOT, 'scripts', 'hoathinh', 'anh2mp4.swift'), fdir, str(FPS), mp4],
                   check=True)


if __name__ == '__main__':
    main()
