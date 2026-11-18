"""THỬ MỨC TRẦN của "code tự vẽ": Ngô Quyền cận cảnh nửa người (chân dung MINH HỌA), 8 giây.

Kỹ thuật: đường cong Catmull-Rom (không còn đa giác gãy), vẽ siêu mẫu 2x rồi thu nhỏ (mịn),
bóng nhiều tầng (bóng tự động theo hướng sáng + mảng bóng vẽ tay), viền mực dày mỏng
(dày phía khuất sáng), nét thon hai đầu (lông mày, ria, lông mũ), giáp vảy từng miếng có đinh,
nền trống đồng xoay chậm, bụi vàng, hạt giấy.
Chuyển động: thở, chùm lông đỏ bay, chớp mắt, cau mày – hét lệnh – trở lại, máy quay đẩy vào.

Chạy:  python3 scripts/hoathinh/ngo_quyen_can_canh.py            (1080p)
       python3 scripts/hoathinh/ngo_quyen_can_canh.py --khung 2 5.2
"""
import argparse
import glob
import math
import os
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FPS, DUR = 30, 8.0
SS = 2                          # siêu mẫu
W, H = 1920, 1080
AWAY = np.array([0.6, 0.8])     # hướng khuất sáng (sáng chính từ trên-trái)


def hx(h, a=None):
    h = h.lstrip('#')
    c = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return c if a is None else c + (a,)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


INK = hx('#1A1110')
BR = dict(b=hx('#B98F3E'), s=hx('#7A5620'), d=hx('#5A3D14'), l=hx('#E2C070'), h=hx('#FFF1C0'))
RED = dict(b=hx('#9E2A24'), s=hx('#681713'), d=hx('#4A0E0C'), l=hx('#C4473A'))
SKIN = dict(b=hx('#E3AE82'), s=hx('#BF835C'), d=hx('#9A6243'), l=hx('#F6D0A8'), r=hx('#D88F70'))
HAIR = dict(b=hx('#1E1513'), l=hx('#4A3A34'))
CREAM = dict(b=hx('#F2E6CC'), s=hx('#C9B48C'))
PLUME = [hx('#7A1410'), hx('#9A1D16'), hx('#B3261E'), hx('#CF3A2A'), hx('#E8573E')]


# ------------------------------------------------------------------ hình học
def cr(pts, closed=True, n=10):
    """Catmull-Rom qua các điểm điều khiển."""
    P = list(pts)
    k = len(P)
    out = []
    idx = range(k) if closed else range(k - 1)
    for i in idx:
        p0 = P[(i - 1) % k] if (closed or i > 0) else P[0]
        p1, p2 = P[i], P[(i + 1) % k]
        p3 = P[(i + 2) % k] if (closed or i + 2 < k) else P[-1]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    if not closed:
        out.append(P[-1])
    return out


def taper(pts, w0, w1, mid=None):
    """Đa giác của một nét thon (độ rộng w0 → [mid] → w1) theo polyline pts."""
    n = len(pts)
    L, R = [], []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        u = i / max(1, n - 1)
        if mid is None:
            w = w0 + (w1 - w0) * u
        else:
            w = (w0 + (mid - w0) * (u / 0.5)) if u < 0.5 else (mid + (w1 - mid) * ((u - 0.5) / 0.5))
        L.append((p[0] + nx * w / 2, p[1] + ny * w / 2))
        R.append((p[0] - nx * w / 2, p[1] - ny * w / 2))
    return L + R[::-1]


def ellipse_pts(cx, cy, rx, ry, n=40, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + rx * math.cos(2 * math.pi * i / n) * c - ry * math.sin(2 * math.pi * i / n) * s,
             cy + rx * math.cos(2 * math.pi * i / n) * s + ry * math.sin(2 * math.pi * i / n) * c) for i in range(n)]


def _shift(m, dx, dy):
    return np.roll(np.roll(m, int(round(dy)), 0), int(round(dx)), 1)


# ------------------------------------------------------------------ vẽ
def paste(cv, arr, x0, y0):
    im = Image.fromarray(arr, 'RGBA')
    sx, sy = max(0, -x0), max(0, -y0)
    if sx >= im.width or sy >= im.height:
        return
    if sx or sy:
        im = im.crop((sx, sy, im.width, im.height))
    x0, y0 = x0 + sx, y0 + sy
    if x0 >= cv.width or y0 >= cv.height or im.width <= 0 or im.height <= 0:
        return
    im = im.crop((0, 0, min(im.width, cv.width - x0), min(im.height, cv.height - y0)))
    cv.alpha_composite(im, (x0, y0))


def shape(cv, pts, c, lw=3.0, shd=8, hld=5, inner=(), shade=True, light=True, alpha=255):
    """Tô một mảng: nền + mảng sáng/tối tự động + chi tiết bên trong (bị cắt theo mảng) + viền mực ngoài."""
    S = SS
    P = [(x * S, y * S) for x, y in pts]
    pad = int((lw * 1.6 + max(shd, hld)) * S) + 6
    x0, y0 = int(min(p[0] for p in P)) - pad, int(min(p[1] for p in P)) - pad
    x1, y1 = int(max(p[0] for p in P)) + pad, int(max(p[1] for p in P)) + pad
    w, h = x1 - x0, y1 - y0
    if w <= 2 or h <= 2:
        return
    mi = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mi).polygon([(x - x0, y - y0) for x, y in P], fill=255)
    m = np.asarray(mi) > 0
    out = np.zeros((h, w, 4), np.uint8)
    if lw > 0:
        r = max(1, int(round(lw * S * 0.5)))
        d1 = np.asarray(mi.filter(ImageFilter.MaxFilter(2 * r + 1))) > 0
        r2 = max(1, int(round(lw * S * 0.55)))
        d2 = _shift(np.asarray(mi.filter(ImageFilter.MaxFilter(2 * r2 + 1))) > 0, AWAY[0] * r2, AWAY[1] * r2)
        out[(d1 | d2) & ~m] = INK + (255,)
    out[m] = c['b'] + (255,)
    if shade and 's' in c:
        s = m & ~_shift(m, -AWAY[0] * shd * S, -AWAY[1] * shd * S)
        out[s] = c['s'] + (255,)
    if light and 'l' in c:
        li = m & ~_shift(m, AWAY[0] * hld * S, AWAY[1] * hld * S)
        out[li] = c['l'] + (255,)
    if inner:
        tmp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        dr0 = ImageDraw.Draw(tmp)

        def cv_(p):
            return (p[0] * S - x0, p[1] * S - y0)
        for it in inner:
            k = it[0]
            col = it[3] if k == 'dot' else (it[4] if k == 'taper' else it[2])
            if len(col) == 4 and col[3] < 255:
                lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
                dr = ImageDraw.Draw(lay)
            else:
                lay, dr = None, dr0
            if k == 'poly':
                dr.polygon([cv_(p) for p in it[1]], fill=it[2])
            elif k == 'polyo':   # đa giác có viền
                dr.polygon([cv_(p) for p in it[1]], fill=it[2], outline=it[3], width=max(1, int(it[4] * S)))
            elif k == 'line':
                dr.line([cv_(p) for p in it[1]], fill=it[2], width=max(1, int(it[3] * S)), joint='curve')
            elif k == 'taper':
                dr.polygon([cv_(p) for p in taper(it[1], it[2], it[3], it[5] if len(it) > 5 else None)], fill=it[4])
            elif k == 'dot':
                x, y = cv_(it[1])
                r = it[2] * S
                dr.ellipse([x - r, y - r, x + r, y + r], fill=it[3])
            if lay is not None:
                tmp.alpha_composite(lay)
        ta = np.asarray(tmp).copy()
        ta[..., 3] = (ta[..., 3] * m).astype(np.uint8)
        base = Image.fromarray(out, 'RGBA')
        base.alpha_composite(Image.fromarray(ta, 'RGBA'))
        out = np.asarray(base).copy()
    if alpha < 255:
        out[..., 3] = (out[..., 3].astype(np.float32) * alpha / 255).astype(np.uint8)
    paste(cv, out, x0, y0)


def stroke(cv, pts, w0, w1, col, ink=0.0, mid=None):
    """Nét thon vẽ thẳng lên canvas (ink>0: thêm viền mực)."""
    dr = ImageDraw.Draw(cv)
    if ink > 0:
        poly = taper(pts, w0 + ink * 2, w1 + ink * 2, None if mid is None else mid + ink * 2)
        dr.polygon([(x * SS, y * SS) for x, y in poly], fill=INK + (255,))
        # chụp kín hai đầu
        for p, w in ((pts[0], w0), (pts[-1], w1)):
            r = (w / 2 + ink) * SS
            dr.ellipse([p[0] * SS - r, p[1] * SS - r, p[0] * SS + r, p[1] * SS + r], fill=INK + (255,))
    poly = taper(pts, w0, w1, mid)
    dr.polygon([(x * SS, y * SS) for x, y in poly], fill=tuple(col) + (255,) if len(col) == 3 else col)


def scales_grid(x0, x1, y0, y1, cw, rh, c, skew=0.0, rivet=True):
    """Chi tiết giáp vảy: từng miếng bo góc có sáng/tối + đinh tán."""
    items = []
    row = 0
    y = y0
    while y < y1:
        off = (cw / 2) if row % 2 else 0
        x = x0 - cw + off
        while x < x1 + cw:
            xs = x + skew * (y - y0)
            p = [(xs + 2, y + 3), (xs + cw - 2, y + 3), (xs + cw - 2, y + rh - 6), (xs + cw / 2, y + rh),
                 (xs + 2, y + rh - 6)]
            items.append(('polyo', p, c['b'] + (255,), INK + (255,), 1.6))
            items.append(('poly', [(xs + 4, y + 5), (xs + cw * 0.45, y + 5), (xs + cw * 0.45, y + rh * 0.62),
                                   (xs + 4, y + rh * 0.55)], c['l'] + (255,)))
            items.append(('poly', [(xs + cw - 4, y + rh * 0.4), (xs + cw - 3, y + rh - 7), (xs + cw / 2, y + rh - 1.5),
                                   (xs + cw * 0.62, y + rh * 0.7)], c['s'] + (255,)))
            if rivet:
                items.append(('dot', (xs + cw * 0.5, y + 9), 2.2, c['d'] + (255,)))
                items.append(('dot', (xs + cw * 0.5 - 0.6, y + 8.4), 0.9, c['h'] + (255,)))
            x += cw
        y += rh * 0.78
        row += 1
    return items


# ------------------------------------------------------------------ nhân vật
HC0 = (1010.0, 372.0)      # tâm đầu (khung 1080p)
HEAD_S = 1.2


class Pose:
    pass


def pose_at(t):
    p = Pose()
    br = math.sin(2 * math.pi * t / 3.4)
    p.breath = br
    # hét lệnh 4.4–6.4s
    sh = ease((t - 4.35) / 0.3) * (1 - ease((t - 6.05) / 0.4))
    p.shout = sh
    p.tilt = 1.2 * math.sin(t * 0.9) - 5.0 * sh + (math.sin(t * 38) * 0.8 * sh if 4.7 < t < 5.9 else 0)
    p.dy = -3.0 * br - 6 * sh
    p.dx = 8 * sh
    # chớp mắt
    b = 0.0
    for tb in (1.25, 3.55, 7.05):
        d = t - tb
        if 0 <= d < 0.2:
            b = max(b, math.sin(d / 0.2 * math.pi))
    p.blink = b
    p.gaze = 3.0 + 2.0 * sh
    p.t = t
    return p


def head_tf(p):
    a = math.radians(p.tilt)
    piv = (0.0, 120.0)
    ca, sa = math.cos(a) * HEAD_S, math.sin(a) * HEAD_S
    ox, oy = HC0[0] + p.dx, HC0[1] + p.dy

    def T(x, y):
        x2, y2 = x - piv[0], y - piv[1]
        return (ox + piv[0] + x2 * ca - y2 * sa, oy + piv[1] + x2 * sa + y2 * ca)
    return T


def draw_plume(cv, p, T):
    t = p.t
    root = (-6.0, -186.0)
    strands = []
    for i in range(9):
        k = i / 8
        ln = 1.0 + 0.25 * math.sin(i * 2.1)
        ctrl = [(0, 0), (-12 - 10 * k, -38 - 10 * k), (-60 - 30 * k, -66 - 6 * k), (-120 - 40 * k, -54 + 14 * k),
                (-170 - 30 * k, -10 + 40 * k), (-196 - 20 * k, 50 + 70 * k)]
        pts = []
        for j, (x, y) in enumerate(ctrl):
            u = j / (len(ctrl) - 1)
            sw = (10 + 22 * u) * math.sin(t * 2.4 - u * 3.2 + i * 0.7) * u
            sw2 = 6 * u * math.sin(t * 3.7 + i)
            pts.append((root[0] + x * ln + sw2, root[1] + y * ln + sw))
        strands.append((cr(pts, closed=False, n=8), i))
    # viền mực toàn chùm
    for pts, i in strands:
        stroke(cv, [T(*q) for q in pts], 22 - i * 0.6, 3, INK, 0, mid=30)
    for pts, i in strands:
        stroke(cv, [T(*q) for q in pts], 17 - i * 0.6, 1.2, PLUME[i % 3], 0, mid=24)
    for pts, i in strands:
        if i % 2 == 0:
            q = [T(x + 3, y - 3) for x, y in pts[2:-6]]
            stroke(cv, q, 3, 1, PLUME[3 + (i // 2) % 2], 0, mid=6)


def draw_head(cv, p):
    T = head_tf(p)

    def TT(pts):
        return [T(x, y) for x, y in pts]

    # --- che gáy (vảy) phía sau + cổ
    guard = cr([(-70, -60), (-104, -30), (-118, 40), (-112, 120), (-92, 168), (-40, 178), (-30, 120), (-58, 60),
                (-64, 0)])
    rows = []
    for k, yy in enumerate(range(-30, 176, 17)):
        rows.append(('taper', TT([(-122, yy), (-80, yy + 4), (-34, yy + 6)]), 2.4, 1.4, INK + (255,)))
        for xx in range(-118, -40, 14):
            rows.append(('line', TT([(xx + (k % 2) * 7, yy + 2), (xx + (k % 2) * 7, yy + 15)]), BR['s'] + (255,), 1.6))
            rows.append(('dot', T(xx + 4 + (k % 2) * 7, yy + 8), 1.6, BR['d'] + (255,)))
    shape(cv, TT(guard), BR, 3.2, 10, 4, rows)
    neck = cr([(-44, 86), (46, 90), (54, 160), (-54, 164)])
    shape(cv, TT(neck), dict(b=SKIN['s'], s=SKIN['d'], l=SKIN['b']), 3.0, 8, 3,
          [('poly', TT([(-44, 92), (48, 96), (50, 124), (-46, 120)]), SKIN['d'] + (170,))])

    # --- mặt (3/4 nhìn sang phải)
    sh = p.shout
    jaw = 16 * sh
    face = cr([(x, y + (jaw * (y - 50) / 68 if y > 50 else 0)) for x, y in
               [(-6, -122), (52, -104), (86, -58), (95, -4), (90, 38), (74, 78), (46, 106), (20, 118), (-12, 110),
                (-50, 84), (-76, 40), (-86, -8), (-80, -62), (-48, -106)]])
    inner = [
        # mảng tối phía xa + dưới gò má + hốc mắt
        ('poly', TT(cr([(-86, -8), (-66, -12), (-56, 40), (-34, 86), (-12, 110), (-50, 84), (-76, 40)])), SKIN['s'] + (200,)),
        ('poly', TT(cr([(-36, -26), (6, -30), (8, -4), (-30, -2)])), SKIN['s'] + (120,)),
        ('poly', TT(cr([(24, -28), (80, -34), (84, -6), (26, -4)])), SKIN['s'] + (90,)),
        # má hồng
        ('dot', T(70, 34), 14, SKIN['r'] + (34,)),
        ('dot', T(-22, 40), 12, SKIN['r'] + (28,)),
        # mũi: mảng tối bên trái sống mũi + chóp mũi
        ('poly', TT(cr([(32, -4), (40, 30), (46, 50), (38, 52), (30, 30)])), SKIN['s'] + (150,)),
        ('poly', TT(cr([(46, 46), (66, 44), (70, 54), (52, 60)])), SKIN['s'] + (200,)),
        ('dot', T(62, 34), 4, SKIN['l'] + (255,)),
        # cằm sáng
        ('poly', TT(cr([(20, 96), (50, 96), (40, 112), (18, 116)])), SKIN['l'] + (120,)),
    ]
    shape(cv, TT(face), SKIN, 3.2, 9, 5, inner)

    # mũi, nét
    stroke(cv, TT(cr([(36, -6), (52, 30), (66, 44), (60, 54), (48, 56)], closed=False, n=6)), 1.2, 2.6, INK, mid=3.2)
    stroke(cv, TT(cr([(38, 52), (44, 58), (52, 56)], closed=False, n=5)), 1.4, 2.0, INK)

    # --- mắt
    def eye(cx, cy, w, h, slant, near):
        hh = h * (1 + 0.18 * sh) * (1 - p.blink)
        lc, rc = (cx - w / 2, cy + slant), (cx + w / 2, cy - slant * 0.4)
        if p.blink < 0.82:
            top = [(cx - w * 0.22, cy - hh * 0.95), (cx + w * 0.18, cy - hh * 1.05)]
            bot = [(cx + w * 0.2, cy + hh * 0.75), (cx - w * 0.22, cy + hh * 0.7)]
            outline = cr([lc] + top + [rc] + bot, n=8)
            ix, iy = cx + p.gaze * (1 if near else 0.8), cy + 0.5
            ir = h * 0.62
            shape(cv, TT(outline), dict(b=hx('#F4EBDD'), s=hx('#CBBBA6')), 0, 3, 0,
                  [('dot', T(ix, iy), ir, hx('#3A2418', 255)),
                   ('dot', T(ix, iy), ir * 0.62, hx('#5A3826', 255)),
                   ('dot', T(ix, iy), ir * 0.38, hx('#140C08', 255)),
                   ('dot', T(ix - ir * 0.35, iy - ir * 0.35), ir * 0.22, (255, 250, 236, 255)),
                   ('poly', TT([(lc[0], lc[1] - hh * 2), (rc[0], rc[1] - hh * 2), (rc[0], rc[1] - hh * 0.25),
                                (lc[0], lc[1] - hh * 0.2)]), hx('#2A1A14', 70))], shade=True, light=False)
            # mí trên dày, mí dưới mảnh
            stroke(cv, TT(cr([(lc[0] - 2, lc[1] + 1)] + top + [(rc[0] + 5, rc[1] - 2)], closed=False, n=6)),
                   1.6, 2.2, INK, mid=4.6)
            stroke(cv, TT(cr([(rc[0] - w * 0.12, rc[1] + hh * 0.5)] + bot[:1] + [(cx - w * 0.1, cy + hh * 0.78)],
                             closed=False, n=5)), 0.6, 1.0, INK + (180,), mid=1.6)
            # nếp mí
            stroke(cv, TT(cr([(cx - w * 0.3, cy - h * 1.6), (cx + w * 0.1, cy - h * 1.85), (cx + w * 0.42, cy - h * 1.4)],
                             closed=False, n=5)), 0.6, 0.6, SKIN['d'], mid=1.6)
        else:
            stroke(cv, TT(cr([lc, (cx, cy + h * 0.35), rc], closed=False, n=6)), 1.6, 2.0, INK, mid=4.0)

    eye(48, -6, 38, 9, 3, True)
    eye(-20, -8, 31, 8.5, 2, False)

    # --- lông mày (cau, đầu trong thấp)
    dn = 7 * sh
    stroke(cv, TT(cr([(24, -24 + dn), (44, -34 + dn * 0.4), (70, -38), (86, -30)], closed=False, n=6)), 7, 2, HAIR['b'],
           ink=0.8, mid=8.5)
    stroke(cv, TT(cr([(4, -24 + dn), (-16, -34 + dn * 0.4), (-38, -38), (-52, -30)], closed=False, n=6)), 6.5, 2,
           HAIR['b'], ink=0.8, mid=7.5)
    if sh > 0.2:   # nếp nhăn giữa trán khi hét
        a = int(200 * sh)
        stroke(cv, TT([(12, -44), (14, -30)]), 1.2, 0.6, SKIN['d'] + (a,))
        stroke(cv, TT([(20, -46), (22, -32)]), 1.2, 0.6, SKIN['d'] + (a,))

    # --- miệng
    if sh < 0.15:
        stroke(cv, TT(cr([(20, 74), (40, 72), (64, 77)], closed=False, n=6)), 1.0, 1.4, INK, mid=3.0)
        stroke(cv, TT(cr([(30, 86), (42, 87), (52, 85)], closed=False, n=4)), 1.0, 1.0, SKIN['s'], mid=2.4)
    else:
        o = sh * (1 + 0.1 * math.sin(p.t * 30))
        mouth = cr([(18, 70), (42, 66 - 2 * o), (66, 74), (58, 74 + 18 * o), (40, 78 + 22 * o), (24, 74 + 15 * o)])
        shape(cv, TT(mouth), dict(b=hx('#3A0E10')), 2.6, 0, 0,
              [('poly', TT([(16, 64), (70, 64), (66, 72 + 5 * o), (18, 72 + 5 * o)]), hx('#EFE6D2', 255)),
               ('poly', TT(cr([(28, 78 + 16 * o), (42, 74 + 14 * o), (56, 77 + 13 * o), (44, 82 + 21 * o)])),
                hx('#9A3A38', 255))])

    # --- ria + râu dê
    stroke(cv, TT(cr([(44, 62), (58, 63), (72, 70), (80, 84)], closed=False, n=6)), 5, 1.2, HAIR['b'], ink=0.6, mid=6)
    stroke(cv, TT(cr([(36, 62), (20, 64), (4, 72), (-6, 86)], closed=False, n=6)), 5, 1.2, HAIR['b'], ink=0.6, mid=5.5)
    goatee = cr([(24, 92 + jaw), (50, 90 + jaw), (48, 112 + jaw), (40, 150 + jaw), (34, 118 + jaw)])
    shape(cv, TT(goatee), HAIR, 2.2, 0, 3,
          [('line', TT([(36, 98 + jaw), (39, 138 + jaw)]), HAIR['l'] + (255,), 1.2),
           ('line', TT([(44, 98 + jaw), (42, 130 + jaw)]), HAIR['l'] + (200,), 1.0)])

    # --- mũ đồng
    draw_plume(cv, p, T)
    dome = cr([(-104, -66), (-98, -118), (-66, -160), (-12, -180), (46, -168), (92, -128), (108, -72), (60, -82),
               (0, -84), (-60, -78)])
    ribs = []
    for xx, bend in ((-58, -14), (-8, -4), (46, 10)):
        ribs.append(('taper', TT(cr([(xx * 0.3 - 4, -176), (xx * 0.75 + bend * 0.3, -140), (xx, -84)], closed=False, n=6)),
                     3.0, 4.0, INK + (255,)))
        ribs.append(('taper', TT(cr([(xx * 0.3 - 1, -174), (xx * 0.75 + bend * 0.3 + 3, -140), (xx + 4, -86)],
                                    closed=False, n=6)), 1.2, 2.0, BR['h'] + (200,)))
    ribs += [('poly', TT(cr([(-90, -110), (-60, -150), (-30, -160), (-56, -120), (-80, -86)])), BR['l'] + (200,)),
             ('dot', T(-50, -146), 7, BR['h'] + (220,)),
             ('poly', TT(cr([(70, -140), (100, -96), (104, -76), (80, -84)])), BR['s'] + (255,))]
    shape(cv, TT(dome), BR, 3.4, 10, 5, ribs)
    # vành mũ
    brim = cr([(-108, -74), (-40, -86), (30, -90), (112, -78), (114, -52), (30, -60), (-40, -58), (-110, -46)])
    rv = [('dot', T(xx, -70 + abs(xx) * 0.04), 2.6, BR['d'] + (255,)) for xx in range(-96, 110, 18)]
    rv += [('dot', T(xx - 0.8, -71 + abs(xx) * 0.04), 1.0, BR['h'] + (255,)) for xx in range(-96, 110, 18)]
    rv += [('taper', TT([(-104, -80), (0, -88), (106, -80)]), 1.8, 1.8, BR['h'] + (180,))]
    shape(cv, TT(brim), BR, 3.0, 6, 3, rv)
    # núm + ống cắm lông
    knob = cr([(-18, -178), (-14, -196), (2, -200), (8, -184)])
    shape(cv, TT(knob), BR, 2.6, 4, 2)
    # che má phía gần (mảnh nhỏ)
    flap = cr([(98, -54), (114, -50), (116, 10), (104, 30), (96, -10)])
    rows2 = [('taper', TT([(94, yy), (118, yy + 2)]), 1.8, 1.4, INK + (255,)) for yy in range(-40, 30, 13)]
    shape(cv, TT(flap), BR, 2.8, 5, 2, rows2)


TORSO = {}


def build_torso():
    """Thân (tĩnh) – dựng 1 lần, mỗi khung chỉ dời theo nhịp thở."""
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    NB = (HC0[0] - 6, HC0[1] + 166)          # gốc cổ
    nx, ny = NB

    def A(pts):
        return [(nx + x, ny + y) for x, y in pts]

    # vai xa (trái) – giáp vai sau thân
    for k in range(3):
        yo = k * 38
        band = cr([(-300 + k * 6, 30 + yo), (-240, -6 + yo), (-160, 0 + yo), (-150, 50 + yo), (-230, 52 + yo),
                   (-296 + k * 6, 80 + yo)])
        shape(cv, A(band), BR, 3.2, 8, 3,
              [('taper', A([(-290 + k * 6, 46 + yo), (-160, 26 + yo)]), 2.0, 2.0, INK + (255,))] +
              [('line', A([(xx, 2 + yo + (xx + 300) * 0.1), (xx, 40 + yo)]), BR['s'] + (255,), 1.6)
               for xx in range(-280, -160, 16)])
    # áo đỏ thân + tay áo
    tunic = cr([(-250, 60), (-150, 6), (-60, -6), (60, -8), (170, 4), (262, 54), (300, 190), (320, 560), (-300, 560),
                (-284, 190)])
    folds = [('taper', A(cr([(-230, 120), (-210, 300), (-220, 520)], closed=False)), 3, 8, RED['s'] + (255,)),
             ('taper', A(cr([(250, 120), (276, 300), (270, 520)], closed=False)), 3, 10, RED['s'] + (255,)),
             ('taper', A(cr([(230, 150), (250, 300)], closed=False)), 2, 4, RED['l'] + (200,))]
    shape(cv, A(tunic), RED, 3.6, 14, 6, folds)
    # cổ áo chéo màu kem (trái đè phải)
    col_back = cr([(-70, -4), (-30, -16), (30, -18), (78, -6), (40, 30), (-40, 30)])
    shape(cv, A(col_back), CREAM, 2.8, 6, 0)
    lapel = cr([(-74, -2), (-50, -10), (24, 112), (8, 130)])
    shape(cv, A(lapel), CREAM, 2.8, 6, 3)
    lapel2 = cr([(80, -6), (58, -12), (6, 90), (14, 116)])
    shape(cv, A(lapel2), CREAM, 2.8, 6, 3)
    # dây đeo giáp qua vai
    for x0_ in (-120, 110):
        strap = cr([(x0_ - 18, -2), (x0_ + 18, 0), (x0_ + 24 * (1 if x0_ > 0 else -1) * 0.2 + 16, 130),
                    (x0_ - 16, 130)])
        shape(cv, A(strap), dict(b=hx('#5A3A22'), s=hx('#3A2414'), l=hx('#7E5634')), 2.8, 5, 2,
              [('dot', A([(x0_, 40)])[0], 4, BR['b'] + (255,)), ('dot', A([(x0_ - 1, 39)])[0], 1.6, BR['h'] + (255,))])
    # giáp ngực vảy
    plate = cr([(-172, 96), (-60, 82), (60, 80), (176, 92), (196, 330), (204, 560), (-206, 560), (-194, 330)])
    sc = scales_grid(nx - 210, nx + 210, ny + 84, ny + 560, 30, 40, BR, skew=0.03)
    # mảng tối phía phải + sáng phía trái cho cả tấm
    sc += [('poly', A(cr([(120, 90), (190, 100), (210, 560), (130, 560)])), BR['d'] + (95,)),
           ('poly', A(cr([(-180, 100), (-110, 92), (-120, 560), (-200, 560)])), BR['h'] + (40,))]
    shape(cv, A(plate), BR, 3.6, 10, 5, sc)
    # viền trên tấm giáp
    rim = cr([(-178, 86), (0, 70), (182, 82), (182, 104), (0, 92), (-178, 108)])
    shape(cv, A(rim), BR, 2.8, 4, 3, [('dot', A([(xx, 90 - abs(xx) * -0.05)])[0], 2.6, BR['d'] + (255,))
                                      for xx in range(-160, 170, 26)])
    # vai gần (phải) – 3 lớp giáp vai
    for k in range(3):
        yo = k * 40
        band = cr([(140 - k * 4, 4 + yo), (230, -14 + yo), (306 + k * 4, 30 + yo), (318 + k * 6, 84 + yo),
                   (236, 62 + yo), (150, 54 + yo)])
        it = [('taper', A([(150, 32 + yo), (236, 22 + yo), (312, 56 + yo)]), 2.0, 2.4, INK + (255,))]
        it += [('line', A([(xx, -2 + yo + (xx - 150) * -0.02), (xx + 4, 54 + yo)]), BR['s'] + (255,), 1.6)
               for xx in range(160, 316, 16)]
        it += [('dot', A([(xx + 6, 10 + yo)])[0], 2.0, BR['d'] + (255,)) for xx in range(160, 316, 16)]
        it += [('poly', A(cr([(160, 6 + yo), (230, -6 + yo), (250, 10 + yo), (180, 22 + yo)])), BR['h'] + (110,))]
        shape(cv, A(band), BR, 3.2, 9, 4, it)
    TORSO['im'] = cv


# ------------------------------------------------------------------ nền
BG = {}


def build_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((xx - 1000) / W, (yy - 380) / H)
    k = np.clip(1 - d / 0.9, 0, 1) ** 1.6
    c0, c1 = np.array(hx('#0D0809'), np.float32), np.array(hx('#4A1C1C'), np.float32)
    bg = c0 + (c1 - c0) * k[..., None]
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    noise = np.asarray(Image.fromarray(noise).resize((W, H), Image.BICUBIC))
    bg += noise[..., None] * 4
    BG['base'] = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert('RGBA')
    # trống đồng (vẽ 1 lần, xoay mỗi khung)
    R = 420
    dr_im = Image.new('RGBA', (2 * R * SS, 2 * R * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(dr_im)
    C = R * SS
    gold = hx('#C9A24A')
    for r, wdt in ((410, 3), (396, 1.5), (330, 2), (318, 1.2), (250, 2), (238, 1.2), (150, 2), (140, 1.2)):
        rr = r * SS
        dr.ellipse([C - rr, C - rr, C + rr, C + rr], outline=gold + (90,), width=int(wdt * SS))
    for i in range(14):   # ngôi sao 14 cánh
        a = 2 * math.pi * i / 14
        a2, a3 = a + math.pi / 14, a - math.pi / 14
        dr.polygon([(C + 130 * SS * math.cos(a), C + 130 * SS * math.sin(a)),
                    (C + 34 * SS * math.cos(a2), C + 34 * SS * math.sin(a2)),
                    (C + 34 * SS * math.cos(a3), C + 34 * SS * math.sin(a3))], fill=gold + (80,))
    for i in range(36):   # vòng răng cưa
        a = 2 * math.pi * i / 36
        pts = [(C + r * SS * math.cos(a + o), C + r * SS * math.sin(a + o)) for r, o in
               ((244, -0.06), (300, 0.0), (244, 0.06))]
        dr.line(pts, fill=gold + (70,), width=int(1.6 * SS))
    for i in range(12):   # chim Lạc giản lược bay ngược chiều kim đồng hồ
        a = 2 * math.pi * i / 12
        cx, cy = C + 364 * SS * math.cos(a), C + 364 * SS * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        nx_, ny_ = math.cos(a), math.sin(a)
        L = 26 * SS
        dr.polygon([(cx - tx * L, cy - ty * L), (cx + tx * L * 0.6 + nx_ * 12 * SS, cy + ty * L * 0.6 + ny_ * 12 * SS),
                    (cx + tx * L * 0.2, cy + ty * L * 0.2), (cx + tx * L * 0.6 - nx_ * 12 * SS,
                                                             cy + ty * L * 0.6 - ny_ * 12 * SS)], fill=gold + (85,))
    BG['drum'] = dr_im


def render(t):
    p = pose_at(t)
    cv = Image.new('RGBA', (W * SS, H * SS))
    cv.paste(BG['base'].resize((W * SS, H * SS)), (0, 0))
    drum = BG['drum'].rotate(t * 4.0, resample=Image.BICUBIC)
    dc = (int((HC0[0] - 30) * SS - drum.width / 2), int((HC0[1] - 10) * SS - drum.height / 2))
    paste(cv, np.asarray(drum), dc[0], dc[1])
    # bóng tối mềm sau người
    sh = Image.new('L', (W * SS, H * SS), 0)
    ImageDraw.Draw(sh).ellipse([(HC0[0] - 380) * SS, (HC0[1] - 120) * SS, (HC0[0] + 420) * SS, (H + 300) * SS], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(60 * SS))
    dark = Image.new('RGBA', cv.size, hx('#080405') + (255,))
    cv.paste(dark, (0, 0), sh)
    # thân
    oy = int(round(-3.0 * p.breath * SS))
    paste(cv, np.asarray(TORSO['im']), 0, oy)
    # đầu
    draw_head(cv, p)
    # bụi vàng
    dr = ImageDraw.Draw(cv)
    rng = np.random.default_rng(3)
    for i in range(70):
        x0, y0, sp = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(6, 22)
        x = (x0 + 12 * math.sin(t * 0.7 + i)) % W
        y = (y0 - t * sp) % H
        r = rng.uniform(1.0, 2.6) * SS
        a = int(120 + 100 * math.sin(t * 3 + i))
        dr.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=(255, 214, 140, max(0, a)))
    # máy quay đẩy vào
    z = 1.0 + 0.07 * ease(t / DUR)
    cw, ch = W * SS / z, H * SS / z
    cx, cy = (HC0[0] + 20 * ease(t / DUR)) * SS, (HC0[1] + 160) * SS
    x0 = clamp(cx - cw / 2, 0, W * SS - cw)
    y0 = clamp(cy - ch / 2, 0, H * SS - ch)
    out = cv.convert('RGB').resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    a = np.asarray(out).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.38 * np.clip(((xx / W - 0.5) * 2) ** 2 * 0.7 + ((yy / H - 0.45) * 2) ** 2, 0, 1.3)
    a = a * vig[..., None]
    a += np.random.default_rng(int(t * 1000)).normal(0, 2.6, a.shape[:2])[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Medium.ttf'), 24)
    d.text((40, H - 60), 'Ngô Quyền · chân dung minh họa (code tự vẽ)', font=f, fill=hx('#F2E6CC'))
    return out


def init():
    build_bg()
    build_torso()


G = {}


def job(i):
    render(i / FPS).save(os.path.join(G['dir'], 'f%04d.jpg' % i), quality=94)
    return i


def init_pool(d):
    init()
    G['dir'] = d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--khung', type=float, nargs='*')
    ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'thu-hoathinh', 'can-canh'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.khung:
        init()
        for t in a.khung:
            pth = os.path.join(a.out, 'khung-%05.2f.jpg' % t)
            render(t).save(pth, quality=94)
            print(pth)
        return
    fdir = os.path.join(a.out, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for f in glob.glob(os.path.join(fdir, '*.jpg')):
        os.remove(f)
    n = int(DUR * FPS)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init_pool, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n))):
            if k % 30 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    mp4 = os.path.join(a.out, 'ngo-quyen-can-canh.mp4')
    subprocess.run(['swift', os.path.join(ROOT, 'scripts', 'hoathinh', 'anh2mp4.swift'), fdir, str(FPS), mp4],
                   check=True)


if __name__ == '__main__':
    main()
