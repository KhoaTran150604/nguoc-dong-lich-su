"""Cảnh thử hoạt họa 2D – trận trên sông Bạch Đằng (MINH HỌA), 10 giây.

Dựa trên dữ kiện kho kb/E2-bach-dang-938.md: F17 (cọc nhọn ở cửa sông), F18 (nước triều lên, thuyền nhẹ
ra khiêu chiến rồi giả thua), F19 (triều rút, cọc lộ), F20 (thuyền giặc vướng cọc, lật đắm).
Chi tiết đánh nhau (tên, giáo), hình dáng thuyền, trang phục: minh họa, không phải tái hiện chính xác.

Diễn biến: thuyền nhẹ của ta lao vào, bắn tên, đâm giáo rồi quay mũi rút chạy; thuyền lớn Nam Hán đuổi theo;
nước rút dần, đầu cọc lộ ra; thuyền lớn đâm cọc, chững lại, nghiêng. Ngô Quyền (bản code vẽ cận cảnh)
đứng mũi thuyền gần máy quay, hét lệnh.

Chạy:  python3 scripts/hoathinh/thuyen_bach_dang.py           (1080p)
       python3 scripts/hoathinh/thuyen_bach_dang.py --khung 3 7.6
"""
import argparse
import glob
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ngo_quyen_can_canh as cc  # noqa: E402
import thu_danh_nhau_v2 as v2  # noqa: E402

m = v2.m
from ngo_quyen_can_canh import cr, hx, mix, clamp, ease, shape, stroke, paste, INK  # noqa: E402

ROOT = cc.ROOT
SS = cc.SS
FPS, DUR = 30, 10.0
W, H = 1920, 1080
WW = 2300                      # bề rộng thế giới (máy quay lia)
HOR = 430                      # đường chân trời
T_HIT = 7.2                    # thuyền giặc đâm cọc

SKY0, SKY1 = hx('#4A1E3A'), hx('#FFB878')
HAZE = hx('#E9A06E')
WATER_FAR, WATER_NEAR = hx('#D98A62'), hx('#33202C')
HULL = dict(b=hx('#5C2C1E'), s=hx('#3A1810'), l=hx('#8A4A30'))
HULL2 = dict(b=hx('#6B4326'), s=hx('#44281A'), l=hx('#9A6A42'))
HOUSE = dict(b=hx('#7A3A26'), s=hx('#4E2216'), l=hx('#A65A3A'))
ROOF = dict(b=hx('#2E2830'), s=hx('#1C171C'), l=hx('#5A4A54'))
SAIL = dict(b=hx('#9A5038'), s=hx('#6A3022'), l=hx('#C27A56'))
WOOD = dict(b=hx('#4A2E22'), s=hx('#2E1A12'), l=hx('#8A5A3A'))


def water_col(y):
    k = clamp((y - HOR) / (H - HOR)) ** 0.7
    return mix(WATER_FAR, WATER_NEAR, k)


def tide(t):
    """0 = triều cao, 1 = triều rút hẳn."""
    return ease((t - 4.0) / 5.0)


# ------------------------------------------------------------------ nền tĩnh
BG = {}


def build_bg():
    w, h = WW * SS, H * SS
    yy = np.arange(h) / SS
    k = (np.clip(yy / HOR, 0, 1) ** 1.4)[:, None]
    rows = np.array(SKY0, np.float32) + (np.array(SKY1, np.float32) - np.array(SKY0, np.float32)) * k
    kw = (np.clip((yy - HOR) / (H - HOR), 0, 1) ** 0.7)[:, None]
    wat = np.array(WATER_FAR, np.float32) + (np.array(WATER_NEAR, np.float32) - np.array(WATER_FAR, np.float32)) * kw
    rows[yy >= HOR] = wat[yy >= HOR]
    sky = np.repeat(rows[:, None, :], w, axis=1)
    im = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8)).convert('RGBA')
    dr = ImageDraw.Draw(im)
    sx, sy, sr = 1080 * SS, 360 * SS, 58 * SS
    glow = Image.new('L', im.size, 0)
    ImageDraw.Draw(glow).ellipse([sx - sr * 4, sy - sr * 4, sx + sr * 4, sy + sr * 4], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(70 * SS))
    im.paste(Image.new('RGBA', im.size, hx('#FFD596') + (255,)), (0, 0), glow)
    dr.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=hx('#FFF0C6') + (255,))
    # núi đá vôi hai lớp
    rng = np.random.default_rng(11)
    for layer, (col, base, hmin, hmax) in enumerate(((mix(HAZE, hx('#7A3A5A'), 0.45), HOR + 4, 50, 130),
                                                     (mix(HAZE, hx('#4A2034'), 0.7), HOR + 6, 30, 90))):
        x = -60.0
        while x < WW + 60:
            wd = rng.uniform(60, 150)
            ht = rng.uniform(hmin, hmax)
            pts = [(x, base), (x + wd * 0.08, base - ht * 0.7), (x + wd * 0.25, base - ht), (x + wd * 0.6, base - ht * 0.95),
                   (x + wd * 0.85, base - ht * 0.55), (x + wd, base)]
            shape(im, cr(pts, n=6), dict(b=col, s=mix(col, hx('#2A1020'), 0.25), l=mix(col, hx('#FFC890'), 0.35)),
                  0, 6, 3)
            x += wd * rng.uniform(0.55, 0.9)
    # bờ xa
    shore = [(0, HOR + 8)] + [(x, HOR + 4 + 3 * math.sin(x / 90)) for x in range(0, WW + 40, 40)] + [(WW, HOR + 12),
                                                                                                    (WW, HOR + 20),
                                                                                                    (0, HOR + 20)]
    ImageDraw.Draw(im).polygon([(x * SS, y * SS) for x, y in shore], fill=hx('#4A2234') + (255,))
    BG['im'] = im


# ------------------------------------------------------------------ biến đổi
def tf(x, y, s, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)

    def T(px, py):
        return (x + s * (px * ca - py * sa), y + s * (px * sa + py * ca))
    return T


def paint_char(cv, ch, t):
    ops, meta = ch.parts(t)
    for op in ops:
        if op[0] == 'p':
            m.paint(cv, [(x * SS, y * SS) for x, y in op[1]], op[2], op[3] * SS, op[4] * SS, op[5] * SS, ink=ch.ink)
        elif op[0] == 'f':
            ImageDraw.Draw(cv).polygon([(x * SS, y * SS) for x, y in op[1]], fill=op[2])
        else:
            ImageDraw.Draw(cv).line([(x * SS, y * SS) for x, y in op[1]], fill=op[2], width=max(1, int(op[3] * SS)),
                                    joint='curve')
    return meta


class Crew(v2.Char2):
    """Lính trên thuyền: chèo (rower), đâm giáo (role left/right) hoặc đứng; nghiêng theo thuyền."""
    def __init__(self, *a, rower=False, **kw):
        super().__init__(*a, **kw)
        self.rower = rower
        self.tilt = 0.0

    def pose(self, t):
        P = super().pose(t)
        if self.rower:
            u = math.sin(t * 5.2 + self.phase * 6)
            P['armF'] = (70 + 25 * u, 60 + 30 * u)
            P['armN'] = (60 + 25 * u, 50 + 30 * u)
            P['w'] = 20 + 34 * u
            P['lam'] = 18 + 8 * u
        P['phi'] = P.get('phi', 0) + self.tilt * self.f
        return P


# ------------------------------------------------------------------ thuyền lớn Nam Hán
def ship_state(t):
    if t < T_HIT:
        x = 1720 - 210 * ease(t / T_HIT) - 20 * t / T_HIT
        return x, 0.0, 0.0
    k = 1 - math.exp(-(t - T_HIT) * 2.2)
    x = 1490 - 18 * k
    jolt = math.sin((t - T_HIT) * 26) * math.exp(-(t - T_HIT) * 5) * 2.5
    return x, -7.0 * k + jolt, 16 * k


def draw_ship(cv, t, x, y, s, tilt, sink, crew=(), far=False):
    bob = 3 * math.sin(t * 1.6 + x * 0.01)
    T = tf(x, y + bob + sink, s, tilt)

    def TT(pts):
        return [T(*p) for p in pts]
    lw = 2.6 if not far else 1.4
    # cột buồm + buồm vách tre
    shape(cv, TT([(-170, -30), (-158, -30), (-160, -470), (-168, -470)]), WOOD, lw, 3, 1)
    sail = [(-286, -430), (-170, -446), (-62, -452), (-56, -300), (-50, -150), (-180, -142), (-300, -132), (-292, -280)]
    bat = [('taper', TT([(-300, yy), (-50, yy - 8)]), 3, 3, INK + (255,)) for yy in range(-420, -140, 40)]
    bat += [('poly', TT([(-280, -430), (-180, -440), (-185, -150), (-290, -140)]), SAIL['l'] + (90,))]
    shape(cv, TT(sail), SAIL, lw, 10, 4, bat)
    flag_w = math.sin(t * 6) * 8
    shape(cv, TT([(-162, -470), (-80, -478 + flag_w), (-92, -455 + flag_w * 0.5), (-80, -432 + flag_w), (-162, -440)]),
          dict(b=hx('#2E3A6A'), s=hx('#1E2648')), lw * 0.8, 3, 0)
    # lâu thuyền 2 tầng
    shape(cv, TT([(-80, -40), (200, -40), (200, -150), (-80, -150)]), HOUSE, lw, 8, 3,
          [('poly', TT([(xx, -120), (xx + 26, -120), (xx + 26, -70), (xx, -70)]), hx('#1E1010') + (255,))
           for xx in range(-60, 190, 46)])
    shape(cv, TT([(-118, -146), (-96, -160), (220, -160), (244, -146), (250, -156), (226, -176), (-100, -178),
                  (-124, -156)]), ROOF, lw, 4, 2)
    shape(cv, TT([(-20, -186), (160, -186), (160, -260), (-20, -260)]), HOUSE, lw, 7, 3,
          [('poly', TT([(xx, -240), (xx + 22, -240), (xx + 22, -205), (xx, -205)]), hx('#1E1010') + (255,))
           for xx in range(0, 150, 40)])
    shape(cv, TT([(-52, -256), (-30, -270), (176, -270), (198, -256), (204, -266), (180, -286), (-34, -288),
                  (-58, -266)]), ROOF, lw, 4, 2)
    # lính trên boong
    metas = []
    for ch, lx in crew:
        fx, fy = T(lx, -36)
        ch.x, ch.y = fx, fy
        ch.tilt = tilt
        metas.append(paint_char(cv, ch, t))
    # thân thuyền + mạn + khiên
    hull = cr([(-360, -86), (-300, -40), (0, -34), (260, -50), (330, -120), (346, -70), (300, 16), (-300, 16)], n=6)
    planks = [('taper', TT(cr([(-330, yy - 20), (0, yy), (320, yy - 30)], closed=False)), 2.2, 2.2, HULL['s'] + (255,))
              for yy in (-14, 2)]
    planks += [('poly', TT(cr([(-340, -80), (-300, -44), (0, -38), (250, -54), (320, -110), (300, -96), (0, -56),
                               (-300, -60)])), HULL['l'] + (200,))]
    shape(cv, TT(hull), HULL, lw + 0.6, 12, 4, planks)
    if not far:
        for i, xx in enumerate(range(-270, 260, 44)):
            c = dict(b=hx('#C9A24A'), s=hx('#7A5620'), l=hx('#F0D080')) if i % 2 else \
                dict(b=hx('#6A2E24'), s=hx('#3E1610'), l=hx('#9A4A3A'))
            yy = -44 - (0 if xx < 200 else (xx - 200) * 0.6)
            shape(cv, TT(cr([(xx - 15, yy), (xx, yy - 14), (xx + 15, yy), (xx, yy + 16)], n=4)), c, 1.8, 3, 2)
        # mái chèo
        for i, xx in enumerate(range(-240, 260, 36)):
            u = math.sin(t * 3 + i * 0.5) * (0 if t > T_HIT else 1)
            stroke(cv, TT([(xx, -8), (xx - 30 + 18 * u, 70)]), 4 * s, 4 * s, WOOD['s'])
    # mũi thuyền: tượng đầu rồng giản lược
    shape(cv, TT(cr([(-360, -86), (-392, -112), (-384, -128), (-352, -116), (-340, -96)], n=4)), HULL, lw, 4, 2)
    return T, metas


# ------------------------------------------------------------------ thuyền nhẹ của ta
def draw_boat(cv, t, x, y, s, flip, crew=(), deg=0.0):
    bob = 2.5 * math.sin(t * 3.1 + x * 0.02)
    T = tf(x, y + bob, s, deg)
    f = flip

    def TT(pts):
        return [T(px * f, py) for px, py in pts]
    for ch, lx, *_ in crew:
        fx, fy = T(lx * f, -10)
        ch.x, ch.y = fx, fy
        ch.tilt = deg
        paint_char(cv, ch, t)
    hull = cr([(-180, -30), (-120, -14), (120, -14), (190, -40), (170, 0), (130, 14), (-130, 14), (-166, 0)], n=6)
    shape(cv, TT(hull), HULL2, 2.6, 8, 3,
          [('taper', TT([(-170, -8), (0, -4), (175, -14)]), 6, 6, hx('#9E2A24') + (255,)),
           ('taper', TT([(-172, -2), (0, 2), (172, -8)]), 2, 2, hx('#C9A24A') + (255,))])
    return T


def wake(cv, x, y, s, flip, speed, t):
    dr = ImageDraw.Draw(cv)
    for i in range(6):
        k = ((t * 1.6 + i / 6) % 1.0)
        bx = x - flip * (160 + 260 * k) * s
        sp = (10 + 50 * k) * s
        a = int(150 * (1 - k) * clamp(abs(speed) / 60))
        if a <= 0:
            continue
        for sg in (-1, 1):
            dr.line([((bx - flip * 30 * s) * SS, (y + 8 * s + sg * sp * 0.25) * SS), (bx * SS, (y + 8 * s + sg * sp * 0.35) * SS)],
                    fill=(255, 226, 190, a), width=max(1, int(2.4 * SS)))


def waterline(cv, x, y, half, s):
    """Dải nước + bọt trắng che phần đáy thuyền."""
    pts = [(x - half, y + 6 * s)]
    for i in range(21):
        u = i / 20
        pts.append((x - half + 2 * half * u, y + 6 * s + 3 * s * math.sin(u * 18)))
    pts += [(x + half, y + 40 * s), (x - half, y + 40 * s)]
    ImageDraw.Draw(cv).polygon([(px * SS, py * SS) for px, py in pts], fill=water_col(y + 20 * s) + (255,))
    stroke(cv, [(px, py) for px, py in pts[1:22]], 3 * s, 3 * s, (255, 236, 210, 200))


# ------------------------------------------------------------------ cọc, tên, nước bắn
STAKES = []


def make_stakes():
    rng = np.random.default_rng(4)
    for row, (y, n, sc) in enumerate(((560, 26, 0.55), (600, 22, 0.7), (660, 20, 0.9))):
        for i in range(n):
            x = 1050 + i * (820 / n) + rng.uniform(-14, 14) + row * 12
            STAKES.append((x, y + rng.uniform(-6, 6), sc * rng.uniform(0.85, 1.15), rng.uniform(-14, 14)))


def draw_stakes(cv, t, ymin, ymax):
    k = 0.04 + 0.96 * tide(t)
    for x, y, sc, lean in STAKES:
        if not (ymin <= y < ymax):
            continue
        hgt = 70 * sc * k
        if hgt < 2:
            continue
        a = math.radians(lean)
        top = (x + math.sin(a) * hgt, y - math.cos(a) * hgt)
        wdt = 7 * sc
        pts = [(x - wdt, y), (top[0] - wdt * 0.5, top[1] + 12 * sc), (top[0], top[1] - 6 * sc), (top[0] + wdt * 0.5,
                                                                                            top[1] + 12 * sc), (x + wdt, y)]
        shape(cv, pts, dict(b=hx('#3E2026'), s=hx('#24121A'), l=hx('#B07050')), 1.6, 3, 2,
              [('poly', [(top[0] - wdt * 0.5, top[1] + 12 * sc), (top[0], top[1] - 6 * sc), (top[0] + wdt * 0.5, top[1] + 12 * sc)],
                hx('#6A6470') + (255,))])     # bịt sắt
        ImageDraw.Draw(cv).ellipse([(x - 16 * sc) * SS, (y - 3 * sc) * SS, (x + 16 * sc) * SS, (y + 4 * sc) * SS],
                                   outline=(255, 214, 160, 170), width=max(1, int(1.6 * SS)))


ARROWS = []   # (t0, dur, x0, y0, x1, y1, arc)
SPLASH = []   # (t0, x, y, size)


def make_arrows():
    rng = np.random.default_rng(9)
    for i in range(16):          # ta bắn lên boong
        t0 = 2.0 + rng.uniform(0, 1.4)
        x0, y0 = rng.uniform(700, 1000), rng.uniform(660, 720)
        x1, y1 = rng.uniform(1420, 1700), rng.uniform(420, 560)
        ARROWS.append((t0, 0.75, x0, y0, x1, y1, rng.uniform(120, 200), 'viet'))
    for i in range(18):          # giặc bắn trả xuống nước
        t0 = 4.0 + rng.uniform(0, 2.2)
        x0, y0 = rng.uniform(1380, 1600), rng.uniform(450, 520)
        x1, y1 = rng.uniform(450, 1050), rng.uniform(690, 820)
        ARROWS.append((t0, 0.8, x0, y0, x1, y1, rng.uniform(100, 180), 'han'))
        SPLASH.append((t0 + 0.8, x1, y1, rng.uniform(0.6, 1.0)))


def arrow_pos(a, u):
    t0, d, x0, y0, x1, y1, arc, _ = a
    x = x0 + (x1 - x0) * u
    y = y0 + (y1 - y0) * u - arc * 4 * u * (1 - u)
    return x, y


def draw_arrows(cv, t):
    dr = ImageDraw.Draw(cv)
    for a in ARROWS:
        u = (t - a[0]) / a[1]
        if not 0 <= u <= 1:
            continue
        x, y = arrow_pos(a, u)
        px, py = arrow_pos(a, max(0, u - 0.04))
        d = math.hypot(x - px, y - py) or 1
        dx, dy = (x - px) / d, (y - py) / d
        L = 34
        dr.line([((x - dx * L) * SS, (y - dy * L) * SS), (x * SS, y * SS)], fill=hx('#2A1810') + (255,), width=int(2.4 * SS))
        dr.polygon([((x + dx * 7) * SS, (y + dy * 7) * SS), ((x - dy * 3) * SS, (y + dx * 3) * SS),
                    ((x + dy * 3) * SS, (y - dx * 3) * SS)], fill=hx('#B8B4AE') + (255,))
        # vệt mờ
        dr.line([((x - dx * 90) * SS, (y - dy * 90) * SS), ((x - dx * L) * SS, (y - dy * L) * SS)],
                fill=(255, 230, 190, 60), width=int(1.6 * SS))


def draw_splashes(cv, t):
    dr = ImageDraw.Draw(cv)
    for t0, x, y, sz in SPLASH:
        k = (t - t0) / 0.7
        if not 0 <= k <= 1:
            continue
        r = (8 + 30 * k) * sz
        dr.ellipse([(x - r * 1.6) * SS, (y - r * 0.35) * SS, (x + r * 1.6) * SS, (y + r * 0.35) * SS],
                   outline=(255, 236, 210, int(220 * (1 - k))), width=max(1, int(2 * SS)))
        for j in range(7):
            ang = math.pi * (0.15 + 0.7 * j / 6)
            v = 70 * sz
            px = x + math.cos(ang) * v * k * 0.6
            py = y - math.sin(ang) * v * k + 120 * k * k * sz
            rr = 3.2 * sz * (1 - k * 0.5)
            dr.ellipse([(px - rr) * SS, (py - rr) * SS, (px + rr) * SS, (py + rr) * SS], fill=(255, 240, 220, int(230 * (1 - k))))


# ------------------------------------------------------------------ Ngô Quyền (bản code vẽ cận cảnh)
NQ_BOX = (560, 0, 1460, 1000)      # vùng cắt trong khung cận cảnh (1x)
NQ = {}


def nq_pose(t):
    p = cc.Pose()
    br = math.sin(2 * math.pi * t / 3.0)
    sh = ease((t - 3.2) / 0.3) * (1 - ease((t - 4.9) / 0.35))
    sh = max(sh, ease((t - 7.4) / 0.3) * (1 - ease((t - 8.8) / 0.35)))
    p.breath, p.shout, p.t = br, sh, t
    p.tilt = 1.0 * math.sin(t * 1.1) - 5.0 * sh
    p.dy, p.dx = -3.0 * br - 6 * sh, 8 * sh
    b = 0.0
    for tb in (1.6, 6.2):
        d = t - tb
        if 0 <= d < 0.2:
            b = max(b, math.sin(d / 0.2 * math.pi))
    p.blink, p.gaze = b, 4.0
    return p


def nq_layer(t):
    if not NQ:
        cc.build_torso()
        NQ['ok'] = True
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    p = nq_pose(t)
    paste(lay, np.asarray(cc.TORSO['im']), 0, int(round(-3.0 * p.breath * SS)))
    cc.draw_head(lay, p)
    return lay.crop(tuple(v * SS for v in NQ_BOX))


# ------------------------------------------------------------------ dàn cảnh
CAST = {}


def make_cast():
    def viet(sc, role=None, rower=False, phase=0.0, f=1):
        c = Crew(0, 700, 'viet', f, weapon='spear', role=role, rower=rower, period=1.1, phase=phase)
        c.s = sc
        return c

    def han(sc, role=None, phase=0.0):
        c = Crew(0, 560, 'han', -1, weapon='sword', role=role, period=1.3, phase=phase)
        c.s = sc
        return c
    CAST['ship'] = [(han(0.42, None, 0.1), -300), (han(0.42, 'right', 0.3), -250), (han(0.42, None, 0.6), -200),
                    (han(0.42, 'right', 0.8), -130), (han(0.42, None, 0.2), 230), (han(0.42, 'right', 0.5), 280)]
    CAST['b1'] = [(viet(0.40, 'left', phase=0.1), 110), (viet(0.40, rower=True, phase=0.3), 20),
                  (viet(0.40, rower=True, phase=0.6), -60), (viet(0.40, rower=True, phase=0.9), -130)]
    CAST['b2'] = [(viet(0.34, 'left', phase=0.5), 110), (viet(0.34, rower=True, phase=0.2), 10),
                  (viet(0.34, rower=True, phase=0.7), -80)]
    CAST['b3'] = [(viet(0.30, rower=True, phase=0.4), 60), (viet(0.30, rower=True, phase=0.1), -30),
                  (viet(0.30, rower=True, phase=0.8), -110)]
    CAST['fg'] = [(viet(1.15, rower=True, phase=0.25), -190), (viet(1.15, rower=True, phase=0.75), -60)]


def boat_paths(t):
    """Thuyền nhẹ: lao vào (0–3.2s), đâm/bắn, rồi quay mũi rút chạy (giả thua) từ ~4.2s."""
    out = []
    # b1: áp sát mũi thuyền giặc rồi quay đầu
    if t < 4.2:
        x = 520 + 640 * ease(t / 3.6)
        flip, v = 1, 160
    else:
        k = ease((t - 4.2) / 4)
        x = 1160 - 700 * k
        flip, v = -1, -170
    out.append(('b1', x, 735, 1.0, flip, v))
    if t < 4.6:
        x = 380 + 560 * ease(t / 4.0)
        flip, v = 1, 140
    else:
        x = 940 - 620 * ease((t - 4.6) / 4)
        flip, v = -1, -150
    out.append(('b2', x, 690, 0.85, flip, v))
    x = 760 - 420 * ease(t / 9)
    out.append(('b3', x, 650, 0.72, -1, -50))
    return out


def render(t):
    cam = 260 * ease(t / DUR)
    z = 1.0 + 0.05 * ease(t / DUR)
    cv = BG['im'].copy()
    # lấp lánh mặt nước
    dr = ImageDraw.Draw(cv)
    rng = np.random.default_rng(int(t * 8))
    for i in range(40):
        yv = HOR + 14 + i * 5.5
        xc = 1080 + rng.uniform(-80, 80) * (1 + i / 12)
        ln = rng.uniform(16, 60) * (1 - i / 60)
        dr.line([((xc - ln) * SS, yv * SS), ((xc + ln) * SS, yv * SS)], fill=(255, 230, 176, 200), width=int(1.8 * SS))
    rng2 = np.random.default_rng(2)
    for i in range(160):
        y = rng2.uniform(HOR + 20, H + 40)
        x = (rng2.uniform(0, WW) + t * 18 * (1 + (y - HOR) / 300)) % WW
        ln = 8 + (y - HOR) * 0.08
        a = int(70 + 60 * math.sin(t * 2 + i))
        dr.line([((x - ln) * SS, y * SS), ((x + ln) * SS, y * SS)], fill=(255, 220, 180, a), width=max(1, int(1.4 * SS)))

    # thuyền xa
    draw_ship(cv, t, 420, 520, 0.38, 0, 0, far=True)
    waterline(cv, 420, 520, 140, 0.38)
    draw_stakes(cv, t, 0, 620)
    # thuyền lớn
    sx, tilt, sink = ship_state(t)
    draw_ship(cv, t, sx, 640, 0.95, tilt, sink, CAST['ship'])
    waterline(cv, sx, 640 + sink, 340, 0.95)
    if t >= T_HIT:   # đâm cọc: dăm gỗ + nước bắn
        k = (t - T_HIT) / 0.6
        if k < 1:
            bx, by = sx - 300, 640
            for j in range(10):
                ang = -math.pi * (0.1 + 0.8 * j / 9)
                rr = 90 * k
                px, py = bx + math.cos(ang) * rr, by + math.sin(ang) * rr + 120 * k * k
                ImageDraw.Draw(cv).line([(px * SS, py * SS), ((px + 8) * SS, (py - 4) * SS)], fill=hx('#5A3A26') + (255,),
                                        width=int(3 * SS))
        if (T_HIT, sx - 300, 650, 1.6) not in SPLASH:
            SPLASH.append((T_HIT, sx - 300, 650, 1.6))
    draw_stakes(cv, t, 620, 700)
    # thuyền nhẹ (xa → gần)
    paths = sorted(boat_paths(t), key=lambda b: b[2])
    for key, x, y, sc, flip, v in paths:
        wake(cv, x, y, sc, flip, v, t)
        draw_boat(cv, t, x, y, sc, flip, CAST[key], deg=-2.0 * flip * clamp(abs(v) / 150))
        waterline(cv, x, y, 190 * sc, sc)
    draw_stakes(cv, t, 700, 2000)
    draw_arrows(cv, t)
    draw_splashes(cv, t)

    # tiền cảnh: thuyền Ngô Quyền (theo máy quay)
    fgx = cam + 360 + 30 * math.sin(t * 0.6)
    fgy = 1010
    bob = 4 * math.sin(t * 2.3)
    sc_nq = 0.44
    nq = nq_layer(t)
    nq = nq.resize((int(nq.width * sc_nq / SS * SS), int(nq.height * sc_nq / SS * SS)) if False else
                   (int(nq.width * sc_nq), int(nq.height * sc_nq)), Image.LANCZOS)
    a = np.asarray(nq).astype(np.float32)
    a[..., :3] *= np.array([1.0, 0.92, 0.84])
    nq = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    for ch, lx in CAST['fg']:
        ch.x, ch.y, ch.tilt = fgx + lx, fgy - 20 + bob, 0
        paint_char(cv, ch, t)
    px = int((fgx + 150) * SS - nq.width / 2)
    py = int((fgy - 380 + bob) * SS)
    paste(cv, np.asarray(nq), px, py)
    T = tf(fgx, fgy + bob, 1.6, -1.0)
    hull = cr([(-260, -48), (-180, -26), (160, -26), (280, -70), (250, 0), (190, 24), (-190, 24), (-240, 0)], n=6)
    shape(cv, [T(*p) for p in hull], HULL2, 3.4, 12, 4,
          [('taper', [T(-250, -14), T(0, -8), T(262, -28)], 8, 8, hx('#9E2A24') + (255,)),
           ('taper', [T(-252, -4), T(0, 2), T(258, -16)], 3, 3, hx('#C9A24A') + (255,)),
           ('dot', T(232, -42), 7, hx('#F2E6CC') + (255,)), ('dot', T(234, -42), 3.4, INK + (255,))])   # mắt thuyền
    waterline(cv, fgx, fgy + bob, 420, 1.6)

    # máy quay + rung khi đâm cọc
    shx = shy = 0.0
    if 0 <= t - T_HIT < 0.6:
        k = math.exp(-(t - T_HIT) * 7) * 9
        shx, shy = k * math.sin((t - T_HIT) * 90), k * math.cos((t - T_HIT) * 70)
    cw, ch_ = W / z, H / z
    x0 = clamp(cam + (W - cw) / 2 + shx, 0, WW - cw)
    y0 = clamp((H - ch_) * 0.6 + shy, 0, H - ch_)
    out = cv.convert('RGB').resize((W, H), Image.LANCZOS, box=(x0 * SS, y0 * SS, (x0 + cw) * SS, (y0 + ch_) * SS))
    arr = np.asarray(out).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.32 * np.clip(((xx / W - 0.5) * 2) ** 2 * 0.7 + ((yy / H - 0.5) * 2) ** 2, 0, 1.3)
    arr = arr * vig[..., None]
    arr += np.random.default_rng(int(t * 1000)).normal(0, 2.6, arr.shape[:2])[..., None]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Medium.ttf'), 24)
    txt = 'Minh họa · thuyền, trang phục, diễn biến gần đúng'
    d.text((41, H - 59), txt, font=f, fill=(20, 10, 14))
    d.text((40, H - 60), txt, font=f, fill=hx('#F2E6CC'))
    return out


def init():
    build_bg()
    make_stakes()
    make_arrows()
    make_cast()


G = {}


def job(i):
    render(i / FPS).save(os.path.join(G['dir'], 'f%04d.jpg' % i), quality=93)
    return i


def init_pool(d):
    init()
    G['dir'] = d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--khung', type=float, nargs='*')
    ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'thu-hoathinh', 'thuyen'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.khung:
        init()
        for t in a.khung:
            pth = os.path.join(a.out, 'khung-%05.2f.jpg' % t)
            render(t).save(pth, quality=93)
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
    mp4 = os.path.join(a.out, 'thuyen-bach-dang.mp4')
    subprocess.run(['swift', os.path.join(ROOT, 'scripts', 'hoathinh', 'anh2mp4.swift'), fdir, str(FPS), mp4],
                   check=True)


if __name__ == '__main__':
    main()
