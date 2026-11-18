"""Cảnh thử ~11s phong cách hoạt hình sitcom tối giản (học phong cách, KHÔNG dùng nhân vật kênh khác):
Anh Văn (áo vàng, khăn vấn, bút lông, nốt ruồi) – Em Võ (áo đỏ, mũ trụ, sẹo má) đối thoại bên bờ sông.

Giọng: build/thu-hoathinh/song-tu/thoai.wav + thoai.json (tạo bằng thoai_song_tu.py).
Khẩu hình: theo biên độ giọng (env) của người đang nói. Cắt cảnh kiểu sitcom: toàn – cận Văn – cận Võ – toàn (triều rút).

Chạy:  python3 scripts/hoathinh/song_tu_doi_thoai.py [--khung 1 5 9 10.5]
"""
import argparse
import glob
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ngo_quyen_can_canh as cc  # noqa: E402
from ngo_quyen_can_canh import cr, hx, mix, clamp, ease, stroke, paste  # noqa: E402

ROOT = cc.ROOT
SS = cc.SS
W, H = 1920, 1080
FPS = 30
DIR = os.path.join(ROOT, 'build', 'thu-hoathinh', 'song-tu')
OUTL = 3.0                                     # viền mảnh, đều
INKC = hx('#2B2222')
cc.INK = INKC                                  # viền nâu than, mềm hơn đen


def S_(c, s=None, l=None):
    d = dict(b=hx(c))
    d['s'] = hx(s) if s else mix(hx(c), hx('#3A3040'), 0.22)
    if l:
        d['l'] = hx(l)
    return d


SKIN = S_('#F6D7B8', '#E2B48E')
PANTS = S_('#3A2E2A')
VAN = dict(tunic=S_('#E0B44A', '#B88A2A'), trim=S_('#F7ECD2'), belt=S_('#5A3A22'))
VO = dict(tunic=S_('#C9342A', '#962018'), trim=S_('#F3D27A'), belt=S_('#3A2418'))
BLUSH = hx('#F49A9A')

D = json.load(open(os.path.join(DIR, 'thoai.json')))
DUR = math.ceil((D['dur'] + 0.5) * 10) / 10
ENV = D['env']


def speaking(t):
    for ln in D['lines']:
        if ln['start'] - 0.05 <= t <= ln['end'] + 0.05:
            return ln['who']
    return None


def mouth_open(t):
    k = int(t * FPS)
    vals = [ENV[j] for j in (k - 1, k, k + 1) if 0 <= j < len(ENV)]
    return clamp((sum(vals) / max(1, len(vals)) - 0.06) * 1.6) if vals else 0.0


def shape(cv, pts, c, lw=OUTL, shd=7, hld=0, inner=()):
    cc.shape(cv, pts, c, lw, shd, hld, inner, light=False)


# ------------------------------------------------------------------ nhân vật
def draw_char(cv, who, x, y, s, f, t, st):
    """who: 'van'|'vo'; (x,y) chân; s tỉ lệ; f hướng mặt (+1 phải); st: trạng thái (dict)."""
    talk = mouth_open(t) if speaking(t) == who else 0.0
    bounce = st.get('bounce', 0.0)
    lean = st.get('lean', 0.0)
    breath = math.sin(t * 2.6 + (0 if who == 'van' else 1.7))
    sq = 1 + 0.015 * breath + 0.05 * bounce            # co giãn nhẹ
    by = -18 * bounce

    def P(px, py, head=False):
        if head:
            px += lean * 0.35 * (-py) / 250
        return (x + f * px * s / sq ** 0.3, y + (py * sq + by) * s)

    def PP(pts, head=False):
        return [P(a, b, head) for a, b in pts]
    pal = VAN if who == 'van' else VO
    # chân
    for dx in (-24, 24):
        shape(cv, PP(cr([(dx - 13, -58), (dx + 13, -58), (dx + 12, -6), (dx - 12, -6)], n=4)), PANTS, OUTL, 4)
        shape(cv, PP(cr([(dx - 16, -14), (dx + 20, -14), (dx + 22, 2), (dx - 16, 2)], n=4)), S_('#2A2220'), OUTL, 3)

    def arm(side, a1, a2, front):
        shx = 54 if side > 0 else -54
        sh = (shx, -150)
        ang1 = math.radians(a1)
        el = (sh[0] + side * 38 * math.sin(ang1), sh[1] + 38 * math.cos(ang1))
        ang2 = math.radians(a2)
        hd = (el[0] + side * 36 * math.sin(ang2), el[1] + 36 * math.cos(ang2))
        pts = [P(*sh), P(*el), P(*hd)]
        stroke(cv, pts, 30 * s, 26 * s, INKC)
        stroke(cv, pts, 24 * s, 20 * s, pal['tunic']['b'])
        shape(cv, PP(cr([(hd[0] - 13, hd[1] - 13), (hd[0] + 13, hd[1] - 13), (hd[0] + 14, hd[1] + 12),
                         (hd[0] - 13, hd[1] + 13)], n=5)), SKIN, OUTL, 4)
        return hd

    def arm_to(side, hd):
        """Tay vươn tới điểm hd (tính khuỷu bằng định lý cos, khuỷu chĩa ra ngoài – xuống)."""
        sh = (54 if side > 0 else -54, -150)
        dx, dy = hd[0] - sh[0], hd[1] - sh[1]
        d = min(math.hypot(dx, dy), 73.0)
        a = math.atan2(dy, dx)
        b = math.acos(clamp((38 ** 2 + d ** 2 - 36 ** 2) / (2 * 38 * d), -1, 1))
        a1 = a - b if side > 0 else a + b
        el = (sh[0] + 38 * math.cos(a1), sh[1] + 38 * math.sin(a1))
        pts = [P(*sh), P(*el), P(*hd)]
        stroke(cv, pts, 30 * s, 26 * s, INKC)
        stroke(cv, pts, 24 * s, 20 * s, pal['tunic']['b'])
        shape(cv, PP(cr([(hd[0] - 13, hd[1] - 13), (hd[0] + 13, hd[1] - 13), (hd[0] + 14, hd[1] + 12),
                         (hd[0] - 13, hd[1] + 13)], n=5)), SKIN, OUTL, 4)

    holding = who == 'van' and st.get('book', True)
    arms = st.get('arms', ((20, 10), (20, 10)))      # (vai, khuỷu) tay sau, tay trước – độ, 0 = buông
    if not holding:
        arm(-1, *arms[0], False)
    # thân
    body = cr([(-60, -168), (60, -168), (76, -40), (68, -24), (-68, -24), (-76, -40)], n=6)
    shape(cv, PP(body), pal['tunic'], OUTL, 10, 0,
          [('poly', PP([(-74, -40), (74, -40), (70, -24), (-70, -24)]), pal['trim']['b'] + (255,)),
           ('poly', PP([(-26, -168), (-10, -168), (22, -96), (8, -88)]), pal['trim']['b'] + (255,)),
           ('poly', PP([(26, -168), (10, -168), (-6, -132), (2, -122)]), pal['trim']['b'] + (255,)),
           ('poly', PP([(-76, -80), (76, -80), (76, -66), (-76, -66)]), pal['belt']['b'] + (255,))])
    if who == 'vo':   # bao kiếm bên hông
        shape(cv, PP([(56, -78), (66, -86), (104, -16), (94, -10)]), S_('#5A3A22'), OUTL, 3)
    if not holding:
        arm(1, *arms[1], True)

    # đầu
    hc = (0, -262)
    R = 98
    off = 14        # lệch mặt về hướng nhìn (3/4)
    gx = st.get('gaze', (0, 0))
    head = [(hc[0] + R * 1.04 * math.cos(a), hc[1] + R * 0.95 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48)]
    if who == 'vo':   # mũ: chóp + tua (vẽ sau đầu)
        shape(cv, PP([(-6, -360), (6, -360), (3, -392), (-3, -392)], True), S_('#8A6A2E'), OUTL, 2)
        for sgn in (-1, 1):
            wv = 4 * math.sin(t * 6 + sgn)
            shape(cv, PP(cr([(0, -388), (sgn * 30, -414 + wv), (sgn * 50, -400 + wv), (sgn * 26, -394)], n=5), True),
                  S_('#F3D27A'), OUTL * 0.8, 3)
    shape(cv, PP(head, True), SKIN, OUTL, 12, 0,
          [('dot', P(hc[0] + off - 60, hc[1] + 36, True), 17 * s, BLUSH + (150,)),
           ('dot', P(hc[0] + off + 60, hc[1] + 36, True), 17 * s, BLUSH + (150,))])
    # tóc / khăn / mũ
    if who == 'van':
        turban = cr([(-106, -276), (-100, -326), (-60, -364), (0, -376), (60, -364), (100, -326), (106, -276),
                     (60, -298), (0, -306), (-60, -298)], n=6)
        shape(cv, PP(turban, True), S_('#231B18', '#120C0A'), OUTL, 6, 0,
              [('taper', PP(cr([(-100, yy + 30), (0, yy), (100, yy + 30)], closed=False, n=6), True), 3 * s, 3 * s,
                hx('#4A3A34') + (255,)) for yy in (-350, -326, -302)])
        # bút lông gác tai
        side = -1
        stroke(cv, [P(side * 96, -270, True), P(side * 150, -330, True)], 8 * s, 6 * s, INKC)
        stroke(cv, [P(side * 96, -270, True), P(side * 146, -326, True)], 5 * s, 4 * s, hx('#8A4A2A'))
        stroke(cv, [P(side * 146, -326, True), P(side * 158, -340, True)], 6 * s, 1 * s, hx('#1A1210'))
    else:
        shape(cv, PP(cr([(-104, -272), (-96, -300), (96, -300), (104, -272), (60, -294), (0, -300), (-60, -294)], n=5),
                     True), S_('#231B18'), OUTL, 4)
        dome = cr([(-110, -290), (-98, -340), (-50, -372), (0, -380), (50, -372), (98, -340), (110, -290), (0, -298)],
                  n=6)
        shape(cv, PP(dome, True), S_('#8A6A2E', '#62491C'), OUTL, 8, 0,
              [('taper', PP(cr([(-108, -306), (0, -314), (108, -306)], closed=False, n=6), True), 7 * s, 7 * s,
                hx('#F3D27A') + (255,))])
        shape(cv, PP(cr([(off - 11, -350), (off + 11, -350), (off + 11, -330), (off - 11, -330)], n=4), True),
              S_('#C9342A'), OUTL * 0.8, 2)
    # mắt
    blink = st.get('blink', 0.0)
    big = st.get('bigeye', 0.0)
    for ex in (-34, 34):
        cx_, cy_ = hc[0] + off + ex + gx[0], hc[1] + 2 + gx[1]
        if blink > 0.6:
            stroke(cv, [P(cx_ - 10, cy_ + 2, True), P(cx_, cy_ + 5, True), P(cx_ + 10, cy_ + 2, True)], 4 * s, 4 * s, INKC)
        else:
            ry = (16 + 6 * big) * (1 - blink)
            rx = 9 + 4 * big
            ImageDraw.Draw(cv).ellipse([P(cx_ - rx, cy_ - ry, True)[0] * SS, P(0, cy_ - ry, True)[1] * SS,
                                        P(cx_ + rx, cy_ + ry, True)[0] * SS, P(0, cy_ + ry, True)[1] * SS]
                                       if f > 0 else
                                       [P(cx_ + rx, cy_ - ry, True)[0] * SS, P(0, cy_ - ry, True)[1] * SS,
                                        P(cx_ - rx, cy_ + ry, True)[0] * SS, P(0, cy_ + ry, True)[1] * SS],
                                       fill=hx('#1E1818'))
            hxp, hyp = P(cx_ + 3, cy_ - ry * 0.45, True)
            r = (4 + 2 * big) * s * SS
            ImageDraw.Draw(cv).ellipse([hxp * SS - r, hyp * SS - r, hxp * SS + r, hyp * SS + r], fill=(255, 255, 255, 255))
            if big > 0.5:
                hxp, hyp = P(cx_ - 4, cy_ + ry * 0.4, True)
                r = 2.4 * s * SS
                ImageDraw.Draw(cv).ellipse([hxp * SS - r, hyp * SS - r, hxp * SS + r, hyp * SS + r], fill=(255, 255, 255, 255))
    # lông mày
    if who == 'van':
        for ex in (-34, 34):
            stroke(cv, [P(off + ex - 13, -287, True), P(off + ex + 13, -287, True)], 6 * s, 6 * s, INKC)
        ImageDraw.Draw(cv).ellipse([(P(off - 52, -236, True)[0] - 3.4 * s) * SS, (P(0, -236, True)[1] - 3.4 * s) * SS,
                                    (P(off - 52, -236, True)[0] + 3.4 * s) * SS, (P(0, -236, True)[1] + 3.4 * s) * SS],
                                   fill=hx('#4A3028'))   # nốt ruồi
    else:
        up = st.get('brow', 0.0)
        for ex, sg in ((-34, 1), (34, -1)):
            stroke(cv, [P(off + ex - 14, -284 + sg * 5 - up * 6, True), P(off + ex + 14, -284 - sg * 5 - up * 6, True)],
                   7 * s, 5 * s, INKC)
        for d in ((-8, -8, 8, 8), (-8, 8, 8, -8)):   # sẹo
            cx_, cy_ = off + 62, -232
            stroke(cv, [P(cx_ + d[0], cy_ + d[1], True), P(cx_ + d[2], cy_ + d[3], True)], 3 * s, 3 * s, hx('#B0604A'))
    # miệng
    mx, my = hc[0] + off, hc[1] + 50
    smile = st.get('smile', 0.4)
    if talk < 0.12:
        pts = [P(mx - 14, my - 3 * smile, True), P(mx, my + 6 * smile, True), P(mx + 14, my - 3 * smile, True)]
        stroke(cv, pts, 4 * s, 4 * s, INKC, mid=4.6 * s)
    else:
        o = talk
        mo = cr([(mx - 15 - 3 * o, my - 4), (mx, my - 6 + 2 * o), (mx + 15 + 3 * o, my - 4), (mx + 10, my + 6 + 18 * o),
                 (mx, my + 9 + 22 * o), (mx - 10, my + 6 + 18 * o)], n=5)
        shape(cv, PP(mo, True), S_('#7A2A2A'), OUTL * 0.9, 0, 0,
              [('dot', P(mx, my + 8 + 20 * o, True), (9 + 6 * o) * s, hx('#E87A7A') + (255,))])
    # đạo cụ tay trước
    if holding:   # sách mở trước ngực, hai tay đỡ hai mép dưới (không chồng lên trang)
        bx, by_ = 14, -128
        for sgn in (-1, 1):
            pg = [(bx, by_ - 4), (bx + sgn * 54, by_ - 14), (bx + sgn * 54, by_ + 44), (bx, by_ + 52)]
            shape(cv, PP(pg), S_('#F7ECD2', '#D8C8A0'), OUTL, 4, 0,
                  [('line', PP([(bx + sgn * 12, by_ + yy), (bx + sgn * 44, by_ + yy - 6)]), hx('#B8A880') + (255,), 2 * s)
                   for yy in (8, 20, 32)])
        shape(cv, PP([(bx - 2, by_ - 6), (bx + 2, by_ - 6), (bx + 2, by_ + 53), (bx - 2, by_ + 53)]),
              S_('#8A6A3A'), OUTL * 0.6, 0)                              # gáy sách
        arm_to(-1, (bx - 50, by_ + 50))
        arm_to(1, (bx + 50, by_ + 46))


# ------------------------------------------------------------------ nền
BG = {}


def build_bg():
    im = Image.new('RGBA', (W * SS, H * SS))
    yy = np.arange(H * SS)[:, None] / SS
    k = np.clip(yy / 470, 0, 1)
    top, hor = np.array(hx('#7CC8EE'), np.float32), np.array(hx('#DDF2FA'), np.float32)
    sky = top + (hor - top) * k
    im = Image.fromarray(np.repeat(sky[:, None, :], W * SS, 1).astype(np.uint8)).convert('RGBA')
    rng = np.random.default_rng(5)
    for cx_, cy_, sc in ((260, 150, 1.0), (900, 110, 1.3), (1560, 190, 0.9), (1300, 70, 0.6)):
        blobs = [(cx_ + rng.uniform(-90, 90) * sc, cy_ + rng.uniform(-20, 20) * sc, rng.uniform(36, 62) * sc)
                 for _ in range(7)]
        lay = Image.new('L', im.size, 0)
        d = ImageDraw.Draw(lay)
        for bx, by_, r in blobs:
            d.ellipse([(bx - r) * SS, (by_ - r) * SS, (bx + r) * SS, (by_ + r * 0.8) * SS], fill=255)
        d.rectangle([(cx_ - 140 * sc) * SS, (cy_ + 20 * sc) * SS, (cx_ + 140 * sc) * SS, (cy_ + 80 * sc) * SS], fill=0)
        m = np.asarray(lay) > 0
        a = np.zeros(m.shape + (4,), np.uint8)
        sh = m & ~cc._shift(m, 0, -14 * SS)
        a[m] = (255, 255, 255, 255)
        a[sh] = hx('#CFE6F2') + (255,)
        im.alpha_composite(Image.fromarray(a, 'RGBA'))
    # núi xa
    for col, base, hh in ((hx('#A9D2D0'), 470, 120), (hx('#86BDB4'), 476, 80)):
        x = -40.0
        while x < W + 40:
            wd = rng.uniform(90, 200)
            ht = rng.uniform(0.5, 1.0) * hh
            pts = cr([(x, base), (x + wd * 0.15, base - ht * 0.8), (x + wd * 0.4, base - ht), (x + wd * 0.7, base - ht * 0.85),
                      (x + wd, base)], n=6)
            ImageDraw.Draw(im).polygon([(a * SS, b * SS) for a, b in pts], fill=col + (255,))
            x += wd * 0.7
    # sông
    ImageDraw.Draw(im).rectangle([0, 470 * SS, W * SS, 660 * SS], fill=hx('#56BFC6') + (255,))
    ImageDraw.Draw(im).rectangle([0, 470 * SS, W * SS, 478 * SS], fill=hx('#7FA86A') + (255,))
    for i in range(40):
        y = rng.uniform(486, 650)
        x = rng.uniform(0, W)
        ln = rng.uniform(20, 70)
        ImageDraw.Draw(im).line([((x - ln) * SS, y * SS), ((x + ln) * SS, y * SS)], fill=hx('#A6E2E4') + (255,),
                                width=int(3 * SS))
    # bờ gần + đường đất
    bank = cr([(-20, 640), (400, 628), (900, 650), (1400, 630), (1960, 646), (1960, 1100), (-20, 1100)], n=8)
    shape(im, bank, S_('#9ED36A', '#7FB84E'), OUTL, 14, 0,
          [('poly', cr([(600, 1100), (760, 760), (1080, 720), (1500, 1100)], n=8), hx('#EBDCA8') + (255,)),
           ('poly', cr([(700, 1100), (820, 800), (1000, 770), (1300, 1100)], n=8), hx('#F3E7BE') + (255,))])
    # bụi cây hai bên
    for cx_, cy_, sc in ((120, 700, 1.3), (380, 690, 1.0), (1620, 690, 1.1), (1860, 700, 1.4), (240, 760, 1.2)):
        blobs = [(cx_ + rng.uniform(-80, 80) * sc, cy_ + rng.uniform(-40, 10) * sc, rng.uniform(40, 62) * sc)
                 for _ in range(6)]
        for lw_ in (OUTL, 0):    # lượt 2 không viền → bụi liền khối, chỉ còn viền ngoài
            for bx, by_, r in sorted(blobs, key=lambda b: b[1]):
                shape(im, cc.ellipse_pts(bx, by_, r, r * 0.88, 30), S_('#5DB04A', '#3E8A36'), lw_, 12, 0,
                      [('dot', (bx - r * 0.3, by_ - r * 0.35), r * 0.22, hx('#86CF6A') + (255,))])
    # khóm tre bên trái
    for i, (bx, h_) in enumerate(((60, 560), (100, 600), (140, 520), (1800, 580), (1850, 520))):
        stroke(im, [(bx, 720), (bx + 10, 720 - h_)], 16, 10, INKC)
        stroke(im, [(bx, 720), (bx + 10, 720 - h_)], 11, 6, hx('#8CC05A'))
        for j in range(5):
            yj = 700 - j * h_ / 5
            stroke(im, [(bx - 7, yj), (bx + 9, yj)], 2.5, 2.5, hx('#5E8A3A'))
            sg = 1 if j % 2 else -1
            stroke(im, [(bx + 5, yj - 20), (bx + sg * 60, yj - 50), (bx + sg * 90, yj - 30)], 9, 1, hx('#6CB04A'), mid=12)
    BG['wide'] = im


def stakes(cv, t, sc=1.0, ox=0, oy=0):
    k = ease((t - 9.6) / 1.6)
    for i in range(16):
        x = 520 + i * 62 + (i % 3) * 9
        y = 560 + (i % 2) * 26
        h_ = (8 + 70 * k) * (0.8 + 0.2 * (i % 3))
        lean = (-10 + (i * 7) % 20)
        a = math.radians(lean)
        top = (x + math.sin(a) * h_, y - math.cos(a) * h_)
        pts = [(x - 7, y), (top[0] - 5, top[1] + 12), (top[0], top[1] - 4), (top[0] + 5, top[1] + 12), (x + 7, y)]
        cc.shape(cv, [(ox + px * sc, oy + py * sc) for px, py in pts], S_('#6B4A32', '#4A3020'), OUTL * 0.8, 3, 0,
                 light=False)
        ImageDraw.Draw(cv).ellipse([(ox + (x - 18) * sc) * SS, (oy + (y - 3) * sc) * SS, (ox + (x + 18) * sc) * SS,
                                    (oy + (y + 5) * sc) * SS], outline=hx('#D8F4F4') + (255,), width=int(2.4 * SS))


def bg_close(cx_, cy_, z):
    key = ('close', cx_, cy_, z)
    if key not in BG:
        im = BG['wide']
        w, h = W / z, H / z
        crop = im.resize((W, H), Image.LANCZOS, box=((cx_ - w / 2) * SS, (cy_ - h / 2) * SS, (cx_ + w / 2) * SS,
                                                     (cy_ + h / 2) * SS))
        crop = crop.filter(ImageFilter.GaussianBlur(5)).resize((W * SS, H * SS), Image.BICUBIC)
        BG[key] = crop
    return BG[key]


# ------------------------------------------------------------------ dàn cảnh
L = D['lines']
CUTS = [0.0, L[1]['start'] - 0.2, L[2]['start'] - 0.15, L[3]['start'] - 0.15, DUR]


def blink_at(t, who):
    for tb in ((1.8, 6.0, 9.2) if who == 'van' else (2.6, 5.2, 7.6, 10.6)):
        d = t - tb
        if 0 <= d < 0.16:
            return math.sin(d / 0.16 * math.pi)
    return 0.0


def state(who, t):
    st = dict(blink=blink_at(t, who), gaze=(4, 0))
    if who == 'vo':
        st['smile'] = 0.9
        if t < CUTS[1]:      # hỏi dồn, vung tay
            w = math.sin(t * 7)
            st['arms'] = ((150 + 20 * w, 40), (160 - 20 * w, 30))
            st['bounce'] = abs(math.sin(t * 6)) * 0.6
            st['brow'] = 0.6
        elif t < CUTS[2]:    # nghe, gật gù
            st['arms'] = ((25, 10), (40, 90))
            st['lean'] = 4 * math.sin(t * 2)
        elif t < CUTS[3]:    # "Rồi sao nữa anh?" mắt long lanh
            st['arms'] = ((60, 100), (60, 100))
            st['bigeye'] = 1.0
            st['lean'] = 10
            st['bounce'] = abs(math.sin(t * 9)) * 0.3
            st['brow'] = 1.0
        else:
            st['arms'] = ((25, 10), (30, 20))
            st['gaze'] = (0, -6)
    else:
        st['smile'] = 0.3
        st['arms'] = ((30, 20), (55, 110))
        if CUTS[1] <= t < CUTS[2] and t < L[1]['start'] + 1.6:   # "Sử chép rằng" – giơ ngón trỏ
            k = ease((t - CUTS[1]) / 0.3) * (1 - ease((t - L[1]['start'] - 1.3) / 0.3))
            st['arms'] = ((30, 20), (55 + 100 * k, 110 + 60 * k))
            st['book'] = k < 0.5
        if t >= CUTS[3]:
            st['gaze'] = (-6, -6)
    return st


def render(t):
    cv = None
    if t < CUTS[1] or t >= CUTS[3]:          # toàn cảnh
        cv = BG['wide'].copy()
        stakes(cv, t)
        draw_char(cv, 'vo', 760, 930, 1.25, 1, t, state('vo', t))
        draw_char(cv, 'van', 1170, 930, 1.25, -1, t, state('van', t))
    elif t < CUTS[2]:                         # cận Văn
        cv = bg_close(1160, 640, 1.9).copy()
        draw_char(cv, 'van', 1080, 1420, 2.7, -1, t, state('van', t))
        draw_char(cv, 'vo', -60, 1520, 3.2, 1, t, state('vo', t))      # vai Võ tiền cảnh
    else:                                     # cận Võ
        cv = bg_close(760, 640, 1.9).copy()
        draw_char(cv, 'vo', 840, 1420, 2.7, 1, t, state('vo', t))
        draw_char(cv, 'van', 1980, 1520, 3.2, -1, t, state('van', t))
    out = cv.convert('RGB').resize((W, H), Image.LANCZOS)
    return out


def init():
    build_bg()


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
    a = ap.parse_args()
    if a.khung:
        init()
        for t in a.khung:
            p = os.path.join(DIR, 'khung-%05.2f.jpg' % t)
            render(t).save(p, quality=93)
            print(p)
        return
    fdir = os.path.join(DIR, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for f in glob.glob(os.path.join(fdir, '*.jpg')):
        os.remove(f)
    n = int(DUR * FPS)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init_pool, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n))):
            if k % 60 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    silent = os.path.join(DIR, 'song-tu-cam.mp4')
    subprocess.run(['swift', os.path.join(ROOT, 'scripts', 'hoathinh', 'anh2mp4.swift'), fdir, str(FPS), silent], check=True)
    out = os.path.join(DIR, 'song-tu-doi-thoai.mp4')
    subprocess.run(['swift', os.path.join(ROOT, 'scripts', 'hoathinh', 'ghep_tieng.swift'), silent,
                    os.path.join(DIR, 'thoai.wav'), out], check=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
