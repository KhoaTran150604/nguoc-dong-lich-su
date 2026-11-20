"""Gâu Nghệ – Border Collie đen trắng, tai lệch, vẽ theo ĐÚNG KHUNG NGƯỜI của Anh Văn
(đầu tròn R≈98 tâm y=-262, thân hình thang -172→-24, vai ±54,-150, cánh tay 38+36, chân ngắn -64→0).

Thân + tay + chân = MỘT khối liền viền (blob) → tay không bao giờ lệch khỏi người.
Chạy:  python scripts/hoathinh/gau_nghe_van.py
Ra:    build/thu-hoathinh/gau-nghe/gau-nghe-khung-van.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, mix, cr, taper, ellipse_pts, shape, stroke  # noqa: E402
from meo_nghe_cach_dieu import blob, ell, line  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'gau-nghe')

BLK = dict(b=hx('#2C2B31'), s=hx('#1A191D'), l=hx('#45444C'))
BLK_F = dict(b=hx('#3B3A42'), s=hx('#25242B'), l=hx('#4A4952'))
WH = hx('#F7F3EA')
WHD = dict(b=WH, s=hx('#D9D2C4'))
PINK = hx('#EF8A96')


def fluff_ring(cx, cy, rx, ry, n=72, tuft=(), amp=0.08):
    """Elip có túm lông ở các góc (độ) cho trong tuft=[(a0,a1),...]."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        deg = math.degrees(a) % 360
        r = 1.0
        for a0, a1 in tuft:
            if a0 <= deg <= a1:
                r = 1.0 + (amp if i % 2 == 0 else -amp * 0.2)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return pts


def soft_blob(cv, polys, c, cast=0.0, **kw):
    """blob() + đổ bóng mềm nhiều tầng (sáng trên-trái), viền sáng, và bóng đổ của khối lên cái nằm dưới (cast)."""
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    blob(lay, polys, c, **kw)
    a = np.asarray(lay).astype(np.float32)
    al = a[..., 3] / 255.0
    mi = Image.fromarray((al * 255).astype(np.uint8), 'L')
    W = cv.size[0]
    u = W / 1600.0        # đơn vị theo cỡ canvas

    def sh(img, dx, dy):
        return img.transform(img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy))

    def blur(img, r):
        return np.asarray(img.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0
    # vùng khuất sáng (dưới-phải) mềm, 2 tầng
    d1 = blur(Image.fromarray(np.clip((al - np.asarray(sh(mi, -0.6 * 34 * u, -0.8 * 34 * u)) / 255.0) * 255, 0, 255).astype(np.uint8)), 14 * u)
    d2 = blur(Image.fromarray(np.clip((al - np.asarray(sh(mi, -0.6 * 12 * u, -0.8 * 12 * u)) / 255.0) * 255, 0, 255).astype(np.uint8)), 4 * u)
    li = blur(Image.fromarray(np.clip((al - np.asarray(sh(mi, 0.6 * 10 * u, 0.8 * 10 * u)) / 255.0) * 255, 0, 255).astype(np.uint8)), 3 * u)
    rgb = a[..., :3]
    k = 1 - 0.30 * d1 - 0.25 * d2
    rgb = rgb * k[..., None]
    rgb = rgb + (np.array([255, 236, 200]) - rgb) * (0.22 * li)[..., None]
    a[..., :3] = np.clip(rgb, 0, 255)
    if cast:     # bóng đổ xuống phần đã vẽ bên dưới (vd. đầu đổ lên thân)
        base = np.asarray(cv).astype(np.float32)
        sd = blur(sh(mi, 0.6 * cast * u, 0.8 * cast * u * 1.6), 10 * u) * (base[..., 3] / 255.0) * (1 - al)
        base[..., :3] *= (1 - 0.45 * sd)[..., None]
        cv.paste(Image.fromarray(base.astype(np.uint8), 'RGBA'))
    cv.alpha_composite(Image.fromarray(a.astype(np.uint8), 'RGBA'))


class Dog:
    """Border Collie theo khung Anh Văn. st: arms ((a1,a2),(a1,a2)) | book | eyes | mouth | gaze | lid."""

    def __init__(self, cv, x, y, s, st):
        self.cv, self.x, self.y, self.s, self.st = cv, x, y, s, st

    def _blob(self, cv, polys, c, cast=0.0, **kw):
        if self.st.get('flat'):    # lối sitcom: màu phẳng, 1 mảng bóng cứng rõ hơn
            if c is BLK:
                c = BLK_F
            kw['shd'] = kw.get('shd', 8) * 1.6 * max(1.0, self.s * 0.6)
            kw['lw'] = kw.get('lw', 3.0) * 1.45     # nét viền đậm hơn như phim
            lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
            blob(lay, polys, c, **kw)
            al = np.asarray(lay)[..., 3] > 0
            if cast >= 16 and getattr(self, '_body', None) is not None:   # đầu đổ bóng cứng lên thân
                d = int(cast * self.s * SS * 1.1)
                sh = np.zeros_like(al)
                sh[d:] = al[:-d]
                m = sh & self._body & ~al
                arr = np.asarray(cv).copy()
                arr[m, :3] = (arr[m, :3] * 0.72).astype(np.uint8)
                cv.paste(Image.fromarray(arr, 'RGBA'))
            elif cast == 6:
                self._body = al
            cv.alpha_composite(lay)
            return
        if self.st.get('soft'):
            soft_blob(cv, polys, c, cast=cast * self.s * 2, **kw)
        else:
            blob(cv, polys, c, **kw)

    def P(self, px, py):
        return (self.x + px * self.s, self.y + py * self.s)

    def Ps(self, pts):
        return [self.P(*p) for p in pts]

    def tube(self, pts, w0, w1):
        P = cr(self.Ps(pts), closed=False, n=8)
        return [taper(P, w0 * self.s, w1 * self.s), ellipse_pts(*P[0], w0 * self.s / 2, w0 * self.s / 2, n=20),
                ellipse_pts(*P[-1], w1 * self.s / 2, w1 * self.s / 2, n=20)]

    # tay theo góc (giống Anh Văn: a1 vai, a2 khuỷu; 0 = buông, 90 = dang ngang, 180 = giơ thẳng)
    def arm_pts(self, side, a1, a2):
        sh = (side * 54, -150)
        g1, g2 = math.radians(a1), math.radians(a2)
        el = (sh[0] + side * 38 * math.sin(g1), sh[1] + 38 * math.cos(g1))
        hd = (el[0] + side * 36 * math.sin(g2), el[1] + 36 * math.cos(g2))
        return [(side * 40, -152), sh, el, hd]

    def arm_to(self, side, hd):
        sh = (side * 54, -150)
        dx, dy = hd[0] - sh[0], hd[1] - sh[1]
        d = min(math.hypot(dx, dy), 73.0)
        a = math.atan2(dy, dx)
        b = math.acos(max(-1, min(1, (38 ** 2 + d ** 2 - 36 ** 2) / (2 * 38 * d))))
        a1 = a - b if side > 0 else a + b
        el = (sh[0] + 38 * math.cos(a1), sh[1] + 38 * math.sin(a1))
        return [(side * 40, -152), sh, el, hd]

    def draw(self):
        st, s, cv = self.st, self.s, self.cv
        # bóng chân
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        x, y = self.P(0, 2)
        ImageDraw.Draw(lay).ellipse([(x - 84 * s) * SS, (y - 9 * s) * SS, (x + 84 * s) * SS, (y + 10 * s) * SS],
                                    fill=(60, 40, 20, 60))
        cv.alpha_composite(lay)
        # đuôi xù (sau thân): rủ xuống rồi vểnh chóp
        path = [(46, -60), (92, -52), (124, -30), (150, -40), (166, -72)]
        Pp = cr(self.Ps(path), closed=False, n=10)
        poly = taper(Pp, 34 * s, 18 * s, 40 * s)
        self._blob(cv, [poly, ellipse_pts(*Pp[-1], 9 * s, 9 * s, n=16)], BLK, lw=3.0, shd=6, hld=0,
             inner=[('poly', ellipse_pts(*Pp[-1], 26 * s, 24 * s, n=24), WH)])
        # thân + tay + chân = 1 khối
        polys = [cr(self.Ps([(-58, -172), (58, -172), (74, -44), (64, -22), (-64, -22), (-74, -44)]), n=6)]
        feet, hands = [], []
        fo = st.get('feet', ((0, 0), (0, 0)))      # (lệch ngang, nhấc) mỗi chân – đi/chạy/nhảy
        for i, dx in enumerate((-24, 24)):
            ox, lf = fo[i]
            polys += self.tube([(dx, -60), (dx + ox * 0.5, -34 - lf * 0.6), (dx + ox, -10 - lf)], 30, 28)
            fp = self.P(dx + ox + (3 if dx > 0 else -3), -8 - lf)
            polys.append(ellipse_pts(*fp, 21 * s, 12 * s, n=24))
            feet.append(fp)
        if st.get('cup'):      # tay trái chống lên lan can, tay phải cầm ly cà phê
            arms = [self.arm_pts(-1, 22, 10), self.arm_to(1, (50, -118))]
        elif st.get('book'):
            bx, by = 14, -128
            arms = [self.arm_to(-1, (bx - 50, by + 50)), self.arm_to(1, (bx + 50, by + 46))]
        else:
            (l1, l2), (r1, r2) = st.get('arms', ((18, 8), (18, 8)))
            arms = [self.arm_pts(-1, l1, l2), self.arm_pts(1, r1, r2)]
            ht = st.get('hand_to', {})
            if 'L' in ht:
                arms[0] = self.arm_to(-1, ht['L'])
            if 'R' in ht:
                arms[1] = self.arm_to(1, ht['R'])
        for a in arms:
            polys += self.tube(a, 26, 22)
            hands.append(self.P(*a[-1]))
        self.hands = hands
        inner = []
        # bờm ngực trắng xù (răng cưa) + bụng
        ruff = [(-50, -172), (-36, -150), (-44, -136), (-26, -120), (-30, -100), (-12, -88), (0, -70), (12, -88), (30, -100),
                (26, -120), (44, -136), (36, -150), (50, -172)]
        inner.append(('poly', self.Ps(ruff), WH))
        if st.get('flat'):
            inner.append(('poly', self.Ps([(-50, -172), (50, -172), (38, -154), (0, -146), (-38, -154)]), hx('#D6CDBE')))
        for f in feet:
            inner.append(('poly', ellipse_pts(*f, 22 * s, 13 * s, n=24), WH))
        for i, dx in enumerate((-24, 24)):   # cổ chân trắng
            ox, lf = fo[i]
            inner.append(('poly', self.Ps([(dx + ox - 16, -22 - lf), (dx + ox + 16, -22 - lf), (dx + ox + 16, -4 - lf),
                                           (dx + ox - 16, -4 - lf)]), WH))
        for h in hands:
            inner.append(('dot', h, 12 * s, WH))
        self._blob(cv, polys, BLK, cast=6, lw=3.0, shd=10, hld=0, inner=inner)
        if st.get('book'):
            self.book()
            for h in hands:      # bàn tay đè lên mép sách
                shape(cv, ellipse_pts(*h, 12.5 * s, 12 * s, n=20), WHD, lw=2.6, shd=3, light=False)
        if st.get('cup'):
            self.cup(hands[1])
        self.head()
        if st.get('cup'):     # ống hút tới miệng (vẽ sau đầu)
            hx_, hy_ = hands[1]
            mx, my = self.P(st.get('off', 8) + 14, -220)
            if not st.get('sip', True):      # không hút: ống hút dựng đứng trong ly
                mx, my = hx_ - 10 * s, hy_ - 78 * s
            stroke(cv, [(hx_ - 20 * s, hy_ - 40 * s), (mx, my)], 7 * s, 7 * s, INK)
            stroke(cv, [(hx_ - 20 * s, hy_ - 40 * s), (mx, my)], 4 * s, 4 * s, hx('#2F7D4A'))

    def cup(self, h):
        """Ly cà phê sữa đá (ly nhựa trong, đá viên) – tay ôm phía trước."""
        s, cv = self.s, self.cv
        x, y = h[0] - 16 * s, h[1]
        top, bot = y - 40 * s, y + 18 * s
        body = [(x - 20 * s, top), (x + 20 * s, top), (x + 15 * s, bot), (x - 15 * s, bot)]
        shape(cv, body, dict(b=hx('#E8DCC8'), s=hx('#CBBCA2')), lw=2.6, shd=3, light=False,
              inner=[('poly', [(x - 18 * s, top + 14 * s), (x + 18 * s, top + 14 * s), (x + 15 * s, bot), (x - 15 * s, bot)],
                      hx('#A86A3E')),
                     ('poly', [(x - 16 * s, top + 34 * s), (x + 16 * s, top + 34 * s), (x + 15 * s, bot), (x - 15 * s, bot)],
                      hx('#7A4526')),
                     ('poly', [(x - 12 * s, top + 4 * s), (x - 2 * s, top + 4 * s), (x - 2 * s, top + 14 * s), (x - 12 * s, top + 14 * s)],
                      hx('#F4F0E6')),
                     ('poly', [(x + 2 * s, top + 8 * s), (x + 12 * s, top + 8 * s), (x + 12 * s, top + 18 * s), (x + 2 * s, top + 18 * s)],
                      hx('#F4F0E6')),
                     ('line', [(x - 13 * s, top + 22 * s), (x - 13 * s, bot - 6 * s)], hx('#FFFFFF'), 2.5 * s)])
        shape(cv, ellipse_pts(x + 18 * s, y - 4 * s, 12 * s, 13 * s, n=20), WHD, lw=2.6, shd=3, light=False)   # bàn tay ôm cạnh ly

    def book(self):
        s, cv = self.s, self.cv
        bx, by = 14, -128
        for sgn in (-1, 1):
            pg = [(bx, by - 4), (bx + sgn * 54, by - 14), (bx + sgn * 54, by + 44), (bx, by + 52)]
            shape(cv, self.Ps(pg), dict(b=hx('#F7ECD2'), s=hx('#D8C8A0')), lw=3, shd=4, light=False,
                  inner=[('line', self.Ps([(bx + sgn * 12, by + yy), (bx + sgn * 44, by + yy - 6)]), hx('#B8A880'), 2 * s)
                         for yy in (8, 20, 32)])
        shape(cv, self.Ps([(bx - 2, by - 6), (bx + 2, by - 6), (bx + 2, by + 53), (bx - 2, by + 53)]),
              dict(b=hx('#8A6A3A')), lw=1.8, shade=False, light=False)

    def head(self):
        st, s, cv = self.st, self.s, self.cv
        hc = (0, -262)
        off = st.get('off', 8)
        cx, cy = self.P(*hc)
        # đầu + má xù + tai lệch = 1 khối
        head = fluff_ring(cx, cy, 104 * s, 94 * s)   # mặt tròn trơn (bỏ túm lông răng cưa)
        ears, inner = [], []
        UP = [(92, -318), (84, -372), (70, -404), (50, -380), (34, -344)]            # tai dựng (bên phải)
        FLOP = [(34, -344), (52, -384), (74, -400), (106, -386), (114, -362), (92, -364), (90, -318)]   # tai gập chóp
        for side, kind in zip((-1, 1), st.get('ears', ('up', 'flop'))):
            pts = UP if kind == 'up' else FLOP
            ears.append(cr(self.Ps([(side * x, y) for x, y in pts]), n=5))
            if kind == 'up':
                inner.append(('poly', cr(self.Ps([(side * 78, -330), (side * 70, -380), (side * 56, -350)]), n=4), hx('#5A4048')))
            else:
                inner.append(('line', self.Ps([(side * 56, -372), (side * 88, -372)]), BLK['s'], 3 * s))
        mask = st.get('mask', 'blaze')
        if mask == 'wide':      # mặt nạ trắng rộng (mắt nằm trên nền trắng)
            inner.append(('poly', cr(self.Ps([(off - 8, -358), (off + 8, -358), (off + 22, -318), (off + 62, -296), (off + 76, -250),
                                              (off + 58, -196), (off - 58, -196), (off - 76, -250), (off - 62, -296),
                                              (off - 22, -318)]), n=5), WH))
        elif mask == 'split':   # nửa mặt trắng
            inner.append(('poly', self.Ps([(off + 2, -380), (off + 2, -140), (-140, -140), (-140, -300), (-70, -360)]), WH))
        elif mask == 'patch':   # mặt trắng, chỏm đen + đốm đen quanh một mắt
            inner.append(('poly', ellipse_pts(*self.P(0, -262), 120 * s, 110 * s, n=50), WH))
            inner.append(('poly', ellipse_pts(*self.P(0, -362), 112 * s, 52 * s, n=40), BLK['b']))
            inner.append(('poly', ellipse_pts(*self.P(off + 38, -276), 32 * s, 27 * s, n=30, rot=-0.3), BLK['b']))
            inner.append(('poly', cr(self.Ps([(off - 6, -330), (off + 6, -330), (off + 3, -306), (off - 3, -306)]), n=3), WH))
        if mask != 'patch':     # sọc trắng giữa trán
            inner.append(('poly', cr(self.Ps([(off - 5, -356), (off + 6, -356), (off + 10, -290), (off + 26, -252), (off - 22, -252),
                                              (off - 8, -290)]), n=4), WH))
        inner.append(('poly', ellipse_pts(*self.P(off, -224), 56 * s, 40 * s, n=40), WH))
        inner.append(('poly', ellipse_pts(*self.P(off, -186), 40 * s, 22 * s, n=30), WH))
        if st.get('tuft'):     # chỏm lông xoăn nhô trên đỉnh (thuộc khối đầu)
            ears.append(cr(self.Ps([(-26, -350), (-30, -384), (-10, -404), (-4, -380), (12, -410), (20, -384), (30, -352)]), n=4))
        self._blob(cv, [head] + ears, BLK, cast=16, lw=3.0, shd=12, hld=0, inner=inner)
        self.on_white = mask in ('wide', 'patch')
        # mắt (tròng trắng nhỏ để nổi trên lông đen, tròng nâu)
        gx, gy = st.get('gaze', (0, 0))
        kinds = st.get('eyes', 'open')
        if isinstance(kinds, str):
            kinds = (kinds, kinds)
        big = st.get('big', 1.0)
        if st.get('blush'):
            for ex in (-62, 62):
                lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
                bx, by = self.P(off + ex, -236)
                ImageDraw.Draw(lay).ellipse([(bx - 17 * s) * SS, (by - 11 * s) * SS, (bx + 17 * s) * SS, (by + 11 * s) * SS],
                                            fill=hx('#F49A9A') + (150,))
                cv.alpha_composite(lay)
        for i, ex in enumerate((-36, 36)):
            kind = kinds[i]
            ex_, ey_ = self.P(off + ex, -270)
            if kind == 'happy':
                col = INK if (self.on_white and not (st.get('mask') == 'patch' and i == 1)) else WH
                line(cv, cr([(ex_ - 13 * s, ey_ + 4 * s), (ex_, ey_ - 9 * s), (ex_ + 13 * s, ey_ + 4 * s)], closed=False, n=8),
                     4.5 * s, col)
                continue
            if kind == 'dot':     # mắt chấm kiểu Anh Văn
                ell(cv, (ex_, ey_), 9 * s * big, 15 * s * big, fill=hx('#1E1818'))
                ell(cv, (ex_ + 3 * s, ey_ - 7 * s * big), 4 * s * big, 4 * s * big, fill=(255, 255, 255))
                if big > 1.1:
                    ell(cv, (ex_ - 4 * s, ey_ + 6 * s * big), 2.4 * s, 2.4 * s, fill=(255, 255, 255))
                continue
            ell(cv, (ex_, ey_), 14 * s * big, 16 * s * big, fill=(255, 255, 255), ow=2.6 * s)
            px, py = ex_ + gx * 4 * s, ey_ + 1 * s + gy * 3 * s
            ell(cv, (px, py), 10 * s * big, 12 * s * big, fill=hx('#6A3E1E'))
            ell(cv, (px, py), 6 * s * big, 7.5 * s * big, fill=hx('#141012'))
            ell(cv, (px - 3.5 * s, py - 4.5 * s * big), 3.4 * s * big, 3.4 * s * big, fill=(255, 255, 255))
            if big > 1.1:
                ell(cv, (px + 3.5 * s, py + 5 * s), 1.8 * s, 1.8 * s, fill=(255, 255, 255))
            lid = st.get('lid', (0, 0))[i]
            if lid:
                top = ey_ - 16 * s + 32 * s * lid
                E = ellipse_pts(ex_, ey_, 15.5 * s, 17.5 * s, n=40)
                ImageDraw.Draw(cv).polygon([(x * SS, min(y, top) * SS) for x, y in E], fill=BLK['s'] + (255,))
                line(cv, [(ex_ - 16 * s, top), (ex_ + 16 * s, top)], 4 * s)
        # lông mày xám nhạt
        for i, ex in enumerate((-36, 36)):
            up = st.get('brow', (0, 0))[i]
            stroke(cv, self.Ps([(off + ex - 12, -296 - up), (off + ex + 12, -296 + (up if i == 0 else -up) * 0)]), 6 * s, 5 * s,
                   hx('#2B2222') if self.on_white else hx('#6E6C76'))
        # mũi
        nx, ny = self.P(off, -238)
        P = cr([(nx - 17 * s, ny - 7 * s), (nx + 17 * s, ny - 7 * s), (nx + 9 * s, ny + 7 * s), (nx, ny + 10 * s),
                (nx - 9 * s, ny + 7 * s)], n=5)
        ImageDraw.Draw(cv).polygon([(a * SS, b * SS) for a, b in P], fill=hx('#151214') + (255,))
        ell(cv, (nx - 6 * s, ny - 3 * s), 4.5 * s, 2.6 * s, fill=hx('#6A6468'))
        line(cv, [(nx, ny + 9 * s), (nx, ny + 16 * s)], 3 * s)
        # miệng
        m = st.get('mouth', 'smile')
        mx, my = nx, ny + 16 * s
        ko = 1.0
        if m == 'talk':          # khẩu hình theo biên độ giọng: mo 0..1
            ko = float(st.get('mo', 0))
            m = 'open' if ko >= 0.12 else st.get('rest', 'smile')
            ko = 0.35 + 0.75 * min(1.0, ko)
        if m == 'tongue':   # há miệng lè lưỡi như ảnh thật
            mo = cr([(mx - 26 * s, my - 2 * s), (mx, my + 2 * s), (mx + 26 * s, my - 2 * s), (mx + 16 * s, my + 16 * s),
                     (mx, my + 20 * s), (mx - 16 * s, my + 16 * s)], n=5)
            shape(cv, mo, dict(b=hx('#5C1A1E')), lw=2.6, shade=False, light=False)
            tg = cr([(mx - 13 * s, my + 6 * s), (mx + 13 * s, my + 6 * s), (mx + 14 * s, my + 30 * s), (mx, my + 38 * s),
                     (mx - 14 * s, my + 30 * s)], n=5)
            shape(cv, tg, dict(b=PINK, s=hx('#C9606E')), lw=2.4, shd=3, light=False,
                  inner=[('line', [(mx, my + 10 * s), (mx, my + 28 * s)], hx('#C9606E'), 2 * s)])
        elif m == 'smirk':
            line(cv, cr([(mx - 20 * s, my + 2 * s), (mx - 6 * s, my + 6 * s), (mx + 14 * s, my + 1 * s), (mx + 24 * s, my - 6 * s)],
                        closed=False, n=6), 3.4 * s)
        elif m == 'flat':        # tỉnh bơ: gạch ngang
            line(cv, [(mx - 16 * s, my + 4 * s), (mx + 16 * s, my + 4 * s)], 3.4 * s)
        elif m == 'open':
            hw = (0.75 + 0.25 * ko) * s
            mo = cr([(mx - 18 * hw, my), (mx + 18 * hw, my), (mx + 10 * hw, my + 18 * s * ko), (mx - 10 * hw, my + 18 * s * ko)], n=5)
            shape(cv, mo, dict(b=hx('#5C1A1E')), lw=2.6, shade=False, light=False,
                  inner=[('dot', (mx, my + 16 * s * ko), 8 * s * ko, PINK)])
        else:
            line(cv, cr([(mx - 20 * s, my - 1 * s), (mx - 10 * s, my + 7 * s), (mx, my + 1 * s), (mx + 10 * s, my + 7 * s),
                         (mx + 20 * s, my - 1 * s)], closed=False, n=6), 3.2 * s)
        if st.get('but') and not st.get('khan'):   # chỉ bút lông gác tai (không nón)
            stroke(cv, self.Ps([(-96, -300), (-150, -352)]), 8 * s, 6 * s, INK)
            stroke(cv, self.Ps([(-96, -300), (-146, -348)]), 5 * s, 4 * s, hx('#8A4A2A'))
            stroke(cv, self.Ps([(-146, -348), (-158, -362)]), 6 * s, 1 * s, hx('#1A1210'))
        if st.get('khan'):   # khăn đóng + bút lông gác tai như Anh Văn
            turban = cr(self.Ps([(-108, -304), (-100, -344), (-60, -372), (0, -382), (60, -372), (100, -344), (108, -304),
                                 (60, -324), (0, -332), (-60, -324)]), n=6)
            shape(cv, turban, dict(b=hx('#B8892E'), s=hx('#8A6420')), lw=3, shd=6, light=False,
                  inner=[('line', cr(self.Ps([(-100, yy + 30), (0, yy), (100, yy + 30)]), closed=False, n=6), hx('#E0B44A'), 3 * s)
                         for yy in (-364, -344, -324)])
            stroke(cv, self.Ps([(-100, -280), (-152, -336)]), 8 * s, 6 * s, INK)
            stroke(cv, self.Ps([(-100, -280), (-148, -332)]), 5 * s, 4 * s, hx('#8A4A2A'))
            stroke(cv, self.Ps([(-148, -332), (-160, -346)]), 6 * s, 1 * s, hx('#1A1210'))


IDEAS = [
    ('Mặt nạ trắng', 'mắt chấm + má hồng như Anh Văn',
     dict(mask='wide', eyes='dot', blush=True, mouth='smile', arms=((18, 8), (112, 162)))),
    ('Nửa mặt trắng', 'nửa trắng nửa đen, tai lệch',
     dict(mask='split', mouth='tongue', gaze=(1, 0), arms=((18, 8), (18, 8)))),
    ('Đốm một mắt', 'mặt trắng, đốm đen quanh mắt, 2 tai gập',
     dict(mask='patch', ears=('flop', 'flop'), eyes=('dot', 'happy'), mouth='tongue', arms=((18, 8), (80, 122)))),
    ('Chỏm lông', '2 tai dựng, chỏm xoăn, mắt to long lanh',
     dict(ears=('up', 'up'), tuft=True, big=1.3, mouth='open', arms=((112, 162), (112, 162)))),
    ('Ông đồ', 'khăn đóng + bút lông, cầm sách',
     dict(khan=True, book=True, mouth='smirk', lid=(0.3, 0.3), gaze=(0, 1))),
]


POSES = [
    ('Lè lưỡi', 'như ảnh thật – vui, thân thiện', dict(mouth='tongue', arms=((18, 8), (18, 8)))),
    ('Kể sử', 'cầm sách như Anh Văn', dict(book=True, mouth='open', gaze=(0, 1))),
    ('Vẫy chào', 'mở đầu / kết video', dict(eyes='happy', mouth='tongue', arms=((18, 8), (112, 162)))),
    ('Lém lỉnh', 'liếc mắt, nhếch mép, chỉ tay', dict(mouth='smirk', lid=(0.42, 0.34), gaze=(1, 0), arms=((18, 8), (80, 122)))),
]


def meadow(size, cx, cy, R, mode='ngay'):
    """Nền đồng cỏ (đơn vị đã nhân SS): trời, mây, đồi xa, cỏ gần, cừu nhỏ, hoa."""
    W, H = size
    rnd = np.random.RandomState(7)
    P = {'ngay': dict(sky=('#9FD3EE', '#E4F3F8'), far='#9CC78A', mid='#7DB566', near='#5E9E4C', sun='#FFF3C4'),
         'chieu': dict(sky=('#F2B98A', '#FBE6C8'), far='#B9B87E', mid='#93A863', near='#6F8F4A', sun='#FFE1A0')}[mode]
    lay = Image.new('RGBA', size, (0, 0, 0, 0))
    a = np.zeros((H, W, 4), np.uint8)
    t = np.linspace(0, 1, H)[:, None]
    c0, c1 = np.array(hx(P['sky'][0])), np.array(hx(P['sky'][1]))
    a[..., :3] = (c0 * (1 - t) + c1 * t)[:, None, :].repeat(W, 1).reshape(H, W, 3) if False else (c0[None, None] * (1 - t[..., None]) + c1[None, None] * t[..., None]).astype(np.uint8).repeat(W, 1)
    a[..., 3] = 255
    lay = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(lay)
    S = lambda v: v * SS
    # mặt trời
    sx, sy = cx + 0.45 * R, cy - 0.55 * R
    for rr, al in ((0.30, 60), (0.22, 110), (0.14, 255)):
        d.ellipse([S(sx - rr * R), S(sy - rr * R), S(sx + rr * R), S(sy + rr * R)], fill=hx(P['sun']) + (al,))
    # mây
    for mx, my, k in ((-0.55, -0.62, 1.0), (0.05, -0.78, 0.7), (0.62, -0.25, 0.6)):
        for dx, dy, r in ((0, 0, .09), (.08, -.04, .11), (.17, 0, .08), (.08, .03, .09)):
            x, y, rr = cx + (mx + dx * k) * R, cy + (my + dy * k) * R, r * k * R
            d.ellipse([S(x - rr * 1.3), S(y - rr), S(x + rr * 1.3), S(y + rr)], fill=(255, 255, 255, 235))
    # đồi
    def hill(base, amp, ph, col):
        xs = np.linspace(cx - R - 10, cx + R + 10, 60)
        ys = cy + base * R - amp * R * np.sin(xs / R * 2.2 + ph)
        pts = [(S(x), S(y)) for x, y in zip(xs, ys)] + [(S(cx + R + 10), S(cy + R + 10)), (S(cx - R - 10), S(cy + R + 10))]
        d.polygon(pts, fill=hx(col) + (255,))
        return xs, ys
    hill(0.05, 0.08, 0.4, P['far'])
    xs, ys = hill(0.22, 0.06, 2.0, P['mid'])
    # cừu nhỏ trên đồi giữa
    for fx in (-0.86, 0.84):
        x = cx + fx * R
        y = float(np.interp(x, xs, ys)) - 0.02 * R
        w = 0.075 * R
        ol = hx('#3A3530') + (255,)
        for lx in (-0.5, 0.45):   # chân
            d.line([(S(x + lx * w), S(y)), (S(x + lx * w), S(y + w * .8))], fill=hx('#2E2A26') + (255,), width=3 * SS)
        for dx, dy, r in ((-.55, 0, .5), (0, -.25, .6), (.5, 0, .5), (0, .15, .55), (-.2, -.1, .5), (.25, -.15, .5)):
            d.ellipse([S(x + dx * w - r * w), S(y + dy * w - r * w), S(x + dx * w + r * w), S(y + dy * w + r * w)], fill=(250, 248, 240, 255))
        hd = x + (-w * .95 if fx > 0 else w * .95)
        d.ellipse([S(hd - w * .32), S(y - w * .55), S(hd + w * .32), S(y + w * .2)], fill=hx('#2E2A26') + (255,))
    hill(0.48, 0.05, 4.1, P['near'])
    # cỏ + hoa
    for _ in range(140):
        x = cx + rnd.uniform(-1, 1) * R
        y = cy + rnd.uniform(0.5, 1.0) * R
        h = rnd.uniform(0.03, 0.06) * R
        d.line([(S(x), S(y)), (S(x + rnd.uniform(-.3, .3) * h), S(y - h))], fill=hx('#4A8A3C') + (255,), width=2 * SS)
    for _ in range(26):
        x = cx + rnd.uniform(-1, 1) * R
        y = cy + rnd.uniform(0.5, 0.95) * R
        r = 0.012 * R
        col = ['#FFFFFF', '#F6D45A', '#F2A6B8'][rnd.randint(3)]
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=hx(col) + (255,))
    return lay


def card(st, CW, CH, avatar=False, compare=False, bg=None):
    cv = Image.new('RGBA', (CW * SS, CH * SS), hx('#F8EFDC') + (255,))
    if avatar:
        R, cx, cy = CW / 2 - 20, CW / 2, CH / 2
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        if st.get('full'):    # toàn thân nhỏ, thấy tay chân làm động tác
            k = st.get('zoom', 0.47) * R / 104
            Dog(lay, cx - 0.06 * R, cy + 0.93 * R, k, st).draw()
        else:
            k = 0.66 * R / 104
            Dog(lay, cx, cy + 0.12 * R + 262 * k, k, st).draw()
        d = ImageDraw.Draw(cv)
        m = Image.new('L', cv.size, 0)
        ImageDraw.Draw(m).ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=255)
        if bg:
            bl = meadow(cv.size, cx, cy, R, bg)
            if st.get('soft'):     # nền mờ nhẹ + tối viền để nhân vật nổi
                bl = bl.filter(ImageFilter.GaussianBlur(2.2 * SS))
                ba0 = np.asarray(bl).astype(np.float32)
                yy, xx = np.mgrid[0:cv.size[1], 0:cv.size[0]]
                rr = np.hypot(xx - cx * SS, yy - cy * SS) / (R * SS)
                ba0[..., :3] *= (1 - 0.35 * np.clip(rr - 0.55, 0, 1) ** 1.5)[..., None]
                bl = Image.fromarray(ba0.astype(np.uint8), 'RGBA')
            ba = np.asarray(bl).copy()
            ba[..., 3] = np.minimum(ba[..., 3], np.asarray(m))
            cv.alpha_composite(Image.fromarray(ba, 'RGBA'))
        else:
            d.ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=hx('#C9A24A') + (255,))
            for rr in (R * 0.85, R * 0.7, R * 0.55):
                d.ellipse([(cx - rr) * SS, (cy - rr) * SS, (cx + rr) * SS, (cy + rr) * SS], outline=hx('#B08A38') + (255,), width=3 * SS)
        arr = np.asarray(lay).copy()
        arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
        cv.alpha_composite(Image.fromarray(arr, 'RGBA'))
        ImageDraw.Draw(cv).ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], outline=hx('#14110F') + (255,),
                                   width=7 * SS)
    else:
        Dog(cv, CW / 2 - 10, CH - 36, 1.0, st).draw()
    return cv.resize((CW, CH), Image.LANCZOS).convert('RGB')


def main_y_tuong():
    CW, CH, AH, LAB, TOP = 360, 520, 300, 74, 96
    W, H = len(IDEAS) * CW, TOP + CH + AH + LAB
    img = Image.new('RGB', (W, H), hx('#F2E6CC'))
    dr = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf'), 46)
    f_n = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26)
    f_d = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf'), 17)
    dr.text((28, 22), 'GÂU NGHỆ – 5 ý tưởng mới (khung Anh Văn)', font=f_t, fill=hx('#14110F'))
    for i, (name, desc, st) in enumerate(IDEAS):
        x0 = i * CW
        img.paste(card(st, CW - 16, CH), (x0 + 8, TOP))
        av = dict(st, book=False)
        img.paste(card(av, CW - 16, AH, avatar=True), (x0 + 8, TOP + CH))
        dr.rectangle([x0 + 8, TOP, x0 + CW - 9, TOP + CH + AH - 1], outline=hx('#C9A24A'), width=2)
        dr.text((x0 + CW / 2, TOP + CH + AH + 24), f'{i + 1} · {name}', font=f_n, fill=hx('#B3261E'), anchor='mm')
        dr.text((x0 + CW / 2, TOP + CH + AH + 54), desc, font=f_d, fill=hx('#4A3E3A'), anchor='mm')
    p = os.path.join(OUT, 'gau-nghe-5-y-tuong.jpg')
    img.save(p, quality=92)
    print(p)


def main_so5():
    CW, CH, AH, LAB, TOP = 360, 520, 300, 74, 96
    items = [('Ông đồ – bỏ nón, giữ bút', 'bút lông gác tai, cầm sách',
              dict(but=True, book=True, mouth='smirk', lid=(0.3, 0.3), gaze=(0, 1))),
             ('Ông đồ – bỏ nón và bút', 'chỉ cầm sách',
              dict(book=True, mouth='smirk', lid=(0.3, 0.3), gaze=(0, 1)))]
    W, H = len(items) * CW, TOP + CH + AH + LAB
    img = Image.new('RGB', (W, H), hx('#F2E6CC'))
    dr = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf'), 40)
    f_n = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 22)
    f_d = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf'), 17)
    dr.text((24, 26), 'GÂU NGHỆ – số 5 bỏ nón', font=f_t, fill=hx('#14110F'))
    for i, (name, desc, st) in enumerate(items):
        x0 = i * CW
        img.paste(card(st, CW - 16, CH), (x0 + 8, TOP))
        img.paste(card(dict(st, book=False), CW - 16, AH, avatar=True), (x0 + 8, TOP + CH))
        dr.rectangle([x0 + 8, TOP, x0 + CW - 9, TOP + CH + AH - 1], outline=hx('#C9A24A'), width=2)
        dr.text((x0 + CW / 2, TOP + CH + AH + 24), f'{chr(65 + i)} · {name}', font=f_n, fill=hx('#B3261E'), anchor='mm')
        dr.text((x0 + CW / 2, TOP + CH + AH + 54), desc, font=f_d, fill=hx('#4A3E3A'), anchor='mm')
    p = os.path.join(OUT, 'gau-nghe-so5-bo-non.jpg')
    img.save(p, quality=92)
    print(p)


def main():
    os.makedirs(OUT, exist_ok=True)
    CW, CH, LAB, TOP = 360, 520, 74, 96
    n = len(POSES) + 1
    W, H = n * CW, TOP + CH + LAB
    img = Image.new('RGB', (W, H), hx('#F2E6CC'))
    dr = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf'), 46)
    f_n = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26)
    f_d = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf'), 18)
    dr.text((28, 22), 'GÂU NGHỆ – Border Collie đen trắng, tai lệch (khung Anh Văn)', font=f_t, fill=hx('#14110F'))
    items = [(a, b, c, False) for a, b, c in POSES] + [('Avatar', 'ảnh đại diện kênh', dict(mouth='tongue'), True)]
    for i, (name, desc, st, av) in enumerate(items):
        x0 = i * CW
        img.paste(card(st, CW - 16, CH, avatar=av), (x0 + 8, TOP))
        dr.rectangle([x0 + 8, TOP, x0 + CW - 9, TOP + CH - 1], outline=hx('#C9A24A'), width=2)
        dr.text((x0 + CW / 2, TOP + CH + 24), f'{i + 1} · {name}', font=f_n, fill=hx('#B3261E'), anchor='mm')
        dr.text((x0 + CW / 2, TOP + CH + 54), desc, font=f_d, fill=hx('#4A3E3A'), anchor='mm')
    p = os.path.join(OUT, 'gau-nghe-khung-van.jpg')
    img.save(p, quality=92)
    print(p)


if __name__ == '__main__':
    if 'so5' in sys.argv:
        main_so5()
    elif 'y-tuong' in sys.argv:
        main_y_tuong()
    else:
        main()
