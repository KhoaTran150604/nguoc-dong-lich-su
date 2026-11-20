"""Mèo Nghệ – bộ vẽ mèo đi đứng như người (code tự vẽ) + bảng thử 5 giống × 5 phong cách.

Chạy:  python scripts/hoathinh/meo_nghe_mau.py [cam muop anh xiem cup]
Ra:    build/thu-hoathinh/meo-nghe/giong-<mã>.jpg  (mỗi giống 5 ảnh) + tong-hop.jpg
Phong cách: 1 không mặc đồ · 2 sticker (không đồ, phẳng, viền trắng) · 3 polo + quần jean
            · 4 sơ mi đóng thùng · 5 avatar cận mặt.
Tay: gốc tay luôn nằm TRONG thân + vá màu che nắp mực ở gốc → tay không bị tách khỏi người.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, BR, RED, CREAM, hx, mix, cr, taper, ellipse_pts, shape, stroke  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'meo-nghe')


def C3(h):
    c = hx(h)
    return dict(b=c, s=mix(c, (0, 0, 0), 0.28), l=mix(c, (255, 255, 255), 0.25))


ORG = dict(b=hx('#EE8A2E'), s=hx('#C2621C'), l=hx('#F9B266'))
WHT = dict(b=hx('#FBF3E6'), s=hx('#DCCBB4'), l=hx('#FFFFFF'))
PINK = dict(b=hx('#EF9AA0'), s=hx('#C9737A'))
WOOD = hx('#7A4E28')
DENIM = dict(b=hx('#4A6E9C'), s=hx('#34507A'), l=hx('#6A8DB8'))
SLACK = dict(b=hx('#3C3A40'), s=hx('#262429'), l=hx('#56535B'))

BREEDS = {
    'cam': dict(ten='Mèo cam ta', fur=ORG, stripe=hx('#C0561A'), white=('muzzle', 'chest', 'paws'),
                eye=hx('#B9CC3C'), ear='up', head='fluff', hw=1.0),
    'muop': dict(ten='Mèo mướp xám', fur=dict(b=hx('#9C9284'), s=hx('#6E665A'), l=hx('#C0B8A8')), stripe=hx('#48403A'),
                 heavy=True, white=('muzzle',), muzzle=hx('#E2DACB'), eye=hx('#D9A12E'), ear='up', head='fluff', hw=1.0),
    'anh': dict(ten='Mèo Anh lông ngắn', fur=dict(b=hx('#8E99A6'), s=hx('#68727D'), l=hx('#B1BAC4')), stripe=None,
                white=(), muzzle=hx('#AAB3BD'), eye=hx('#E58A26'), nose=hx('#8E7F86'), ear='small', head='round', hw=1.14),
    'xiem': dict(ten='Mèo Xiêm', fur=dict(b=hx('#EFE3CC'), s=hx('#CDBB9C'), l=hx('#FFF6E6')), stripe=None, white=(),
                 points=dict(b=hx('#5A4032'), s=hx('#3E2B20'), l=hx('#7A5A46')), eye=hx('#4DA3E0'), nose=hx('#3A2A22'),
                 ear='big', head='slim', hw=0.96),
    'cup': dict(ten='Mèo tai cụp', fur=dict(b=hx('#F0C48A'), s=hx('#CC9A5E'), l=hx('#FADBB0')), stripe=hx('#D4914A'),
                white=('muzzle', 'chest', 'paws'), eye=hx('#C88A2A'), ear='fold', head='round', hw=1.08),
}

# tư thế tay bên phải (x>0); bên trái lật x. Điểm đầu = gốc tay, nằm trong thân.
POSES = {
    'down': [(32, -198), (60, -160), (58, -122)],
    'hip': [(32, -198), (76, -160), (52, -124)],
    'wave': [(32, -198), (80, -226), (90, -278)],
    'chest': [(32, -198), (60, -160), (14, -152)],
    'hold': [(32, -198), (68, -168), (86, -180)],
    'phone': [(32, -198), (64, -160), (42, -206)],
    'thumb': [(32, -198), (64, -164), (38, -172)],
}


# ------------------------------------------------------------------ nét vẽ trực tiếp (toạ độ logic)
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


def poly(cv, pts, fill):
    ImageDraw.Draw(cv).polygon([(x * SS, y * SS) for x, y in pts], fill=tuple(fill) + (255,))


def soft(cv, fn):
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    cv.alpha_composite(lay)


def mirror(right):
    """Nửa phải (từ đỉnh xuống cằm) → đường kín cả đầu."""
    left = [(-x, y) for x, y in right[1:-1]][::-1]
    return right + left


# ------------------------------------------------------------------ nhân vật
class Cat:
    def __init__(self, cv, cx, gy, k, o):
        self.cv, self.cx, self.gy, self.k, self.o = cv, cx, gy, k, o
        self.flat = o.get('flat', False)
        br = BREEDS[o.get('giong', 'cam')]
        self.br = br
        self.fur = br['fur']
        self.pts = br.get('points')
        self.stripe = br.get('stripe')
        wh = br.get('white', ())
        self.pawc = WHT if 'paws' in wh else (self.pts or self.fur)
        self.muzzle = WHT['b'] if 'muzzle' in wh else (self.pts['b'] if self.pts else br.get('muzzle'))
        self.chest = WHT['b'] if 'chest' in wh else None
        self.hw = br.get('hw', 1.0)
        self.hs = o.get('hs', 1.0)
        self.hcy = -215 - 85 * self.hs

    # toạ độ
    def B(self, x, y):
        return (self.cx + x * self.k, self.gy + y * self.k)

    def Bs(self, pts):
        return [self.B(*p) for p in pts]

    def H(self, x, y):
        return (self.cx + x * self.hw * self.k * self.hs, self.gy + (self.hcy + (y + 300) * self.hs) * self.k)

    def Hs(self, pts):
        return [self.H(*p) for p in pts]

    @property
    def hk(self):
        return self.k * self.hs

    def sh(self, pts, c, **kw):
        if self.flat:
            kw['shade'] = False
            kw['light'] = False
        shape(self.cv, pts, c, **kw)

    # -------------------------------------------------- phần thân
    def shadow(self):
        cx, gy, k = self.cx, self.gy, self.k
        soft(self.cv, lambda d: d.ellipse([(cx - 95 * k) * SS, (gy - 10 * k) * SS, (cx + 95 * k) * SS,
                                           (gy + 12 * k) * SS], fill=(60, 40, 20, 55)))

    def tail(self):
        k = self.k
        path = [(46, -106), (100, -112), (138, -160), (146, -228), (122, -268)]
        P = cr(self.Bs(path), closed=False, n=8)
        col = self.pts or self.fur
        inner = []
        if self.stripe:
            for i in range(6, len(P) - 3, 9):
                a, b = P[i - 1], P[i + 1]
                dx, dy = b[0] - a[0], b[1] - a[1]
                d = math.hypot(dx, dy) or 1
                nx, ny = -dy / d, dx / d
                c = P[i]
                inner.append(('line', [(c[0] - nx * 30 * k, c[1] - ny * 30 * k), (c[0] + nx * 30 * k, c[1] + ny * 30 * k)],
                              self.stripe, 6 * k))
        self.sh(taper(P, 26 * k, 13 * k, 24 * k), col, lw=2.6, shd=5, hld=3, inner=inner)

    def legs(self):
        k, o = self.k, self.o
        pants = o.get('pants')
        legc = pants or self.fur
        for s in (-1, 1):
            stroke(self.cv, self.Bs([(s * 26, -108), (s * 27, -60), (s * 29, -24)]), 36 * k, 33 * k, legc['b'], ink=2.6)
            if pants is DENIM:
                line(self.cv, self.Bs([(s * 36, -96), (s * 38, -30)]), 1.6 * k, DENIM['l'])
            pc = (self.pts or self.fur) if (self.pts and not pants) else self.pawc
            if o.get('giay'):
                self.sh(cr(self.Bs([(s * 4, -26), (s * 52, -26), (s * 60, -6), (s * 4, -4)]), n=4),
                        C3(o['giay']), lw=2.6, shd=3, hld=2)
            else:
                self.sh(ellipse_pts(*self.B(s * 33, -13), 30 * k, 15 * k, n=30), pc, lw=2.6, shd=4, hld=2,
                        inner=[('line', [self.B(s * 33 - 6, -22), self.B(s * 33 - 6, -6)], pc['s'], 2.2 * k),
                               ('line', [self.B(s * 33 + 8, -22), self.B(s * 33 + 8, -6)], pc['s'], 2.2 * k)])
        if pants:
            # cạp quần + đũng
            pts = [(-60, -126), (60, -126), (62, -84), (8, -78), (0, -92), (-8, -78), (-62, -84)]
            inner = [('line', self.Bs([(0, -126), (0, -94)]), pants['s'], 2 * k)]
            if pants is DENIM:
                inner += [('line', cr(self.Bs([(-48, -120), (-34, -106), (-20, -118)]), closed=False, n=4), DENIM['l'], 1.8 * k),
                          ('line', cr(self.Bs([(48, -120), (34, -106), (20, -118)]), closed=False, n=4), DENIM['l'], 1.8 * k)]
            self.sh(pts and self.Bs(pts), pants, lw=2.6, shd=5, hld=3, inner=inner)

    def torso(self):
        k, o = self.k, self.o
        st = o.get('outfit', 'none')
        if st == 'polo':
            c = C3(o['col'])
            pts = [(-48, -222), (48, -222), (64, -176), (68, -118), (62, -98), (0, -94), (-62, -98), (-68, -118), (-64, -176)]
            inner = [('poly', self.Bs([(-6, -222), (6, -222), (6, -180), (-6, -180)]), c['s']),
                     ('dot', self.B(0, -206), 3 * k, WHT['b']), ('dot', self.B(0, -190), 3 * k, WHT['b']),
                     ('line', self.Bs([(-66, -104), (66, -104)]), c['s'], 2.4 * k),
                     ('poly', self.Bs([(30, -186), (46, -186), (46, -170), (30, -170)]), c['l'])]
            self.sh(cr(self.Bs(pts), n=8), c, lw=2.8, shd=7, hld=4, inner=inner)
            for s in (-1, 1):   # cổ áo bẻ
                self.sh(self.Bs([(s * 2, -224), (s * 40, -226), (s * 30, -202), (s * 6, -200)]), c, lw=2.4, shd=3, hld=2)
        elif st == 'somi':
            c = C3(o['col'])
            pts = [(-48, -222), (48, -222), (62, -176), (64, -130), (60, -118), (-60, -118), (-64, -130), (-62, -176)]
            inner = [('line', self.Bs([(0, -222), (0, -118)]), c['s'], 2.2 * k)]
            inner += [('dot', self.B(5, y), 2.6 * k, c['s']) for y in (-200, -176, -152, -130)]
            inner += [('line', self.Bs([(-30, -126), (-26, -146), (-34, -160)]), c['s'], 1.6 * k),
                      ('line', self.Bs([(30, -126), (26, -146), (34, -160)]), c['s'], 1.6 * k)]
            self.sh(cr(self.Bs(pts), n=8), c, lw=2.8, shd=7, hld=4, inner=inner)
            # thắt lưng (đóng thùng)
            self.sh(self.Bs([(-62, -124), (62, -124), (62, -110), (-62, -110)]), C3('#3A2618'), lw=2.2, shd=2, hld=1,
                    inner=[('polyo', self.Bs([(-9, -124), (9, -124), (9, -110), (-9, -110)]), BR['b'], BR['s'], 1.6 * k)])
            for s in (-1, 1):
                self.sh(self.Bs([(s * 2, -224), (s * 36, -228), (s * 28, -204), (s * 6, -204)]), c, lw=2.4, shd=3, hld=2)
            if o.get('cavat'):
                self.sh(cr(self.Bs([(-6, -210), (6, -210), (10, -150), (0, -138), (-10, -150)]), n=3), C3(o['cavat']),
                        lw=2.2, shd=3, hld=2)
        else:   # không mặc đồ
            pts = [(-46, -222), (46, -222), (58, -176), (64, -116), (54, -94), (0, -88), (-54, -94), (-64, -116), (-58, -176)]
            inner = []
            if self.chest is not None:
                inner.append(('poly', cr(self.Bs([(-26, -224), (26, -224), (30, -172), (0, -128), (-30, -172)]), n=6), self.chest))
            if self.stripe:
                for y in ((-166, -160), (-136, -130), (-110, -106)):
                    inner.append(('taper', self.Bs([(-62, y[0]), (-40, y[1])]), 7 * k, 2 * k, self.stripe))
                    inner.append(('taper', self.Bs([(62, y[0]), (40, y[1])]), 7 * k, 2 * k, self.stripe))
            self.sh(cr(self.Bs(pts), n=8), self.fur, lw=2.8, shd=7, hld=4, inner=inner)

    # -------------------------------------------------- đầu
    def head(self):
        o, hk, br = self.o, self.hk, self.br
        cv = self.cv
        earc = self.pts or self.fur
        ear = br.get('ear', 'up')
        for s in (-1, 1):
            if ear == 'fold':
                e = [(s * 82, -352), (s * 100, -370), (s * 98, -392), (s * 72, -398), (s * 38, -380)]
                self.sh(cr(self.Hs(e), n=6), earc, lw=2.8, shd=4, hld=3,
                        inner=[('line', cr(self.Hs([(s * 52, -384), (s * 78, -386), (s * 92, -374)]), closed=False, n=4),
                                earc['s'], 2.2 * hk)])
                continue
            if ear == 'small':
                e = [(s * 86, -340), (s * 96, -384), (s * 92, -404), (s * 74, -396), (s * 42, -378)]
                ie = [(s * 80, -352), (s * 86, -388), (s * 60, -380)]
            elif ear == 'big':
                e = [(s * 84, -330), (s * 112, -400), (s * 112, -438), (s * 88, -422), (s * 34, -370)]
                ie = [(s * 80, -346), (s * 100, -410), (s * 52, -374)]
            else:
                e = [(s * 90, -326), (s * 104, -392), (s * 100, -424), (s * 78, -410), (s * 36, -372)]
                ie = [(s * 82, -344), (s * 92, -398), (s * 86, -408), (s * 52, -374)]
            self.sh(cr(self.Hs(e), n=6), earc, lw=2.8, shd=5, hld=3)
            self.sh(cr(self.Hs(ie), n=6), PINK if not self.pts else dict(b=mix(PINK['b'], self.pts['b'], 0.6)), lw=0, shd=3,
                    light=False)
        hd = br.get('head', 'fluff')
        if hd == 'round':
            right = [(0, -392), (62, -386), (102, -356), (120, -312), (122, -272), (106, -238), (64, -214), (0, -208)]
        elif hd == 'slim':
            right = [(0, -386), (50, -380), (88, -350), (100, -308), (96, -270), (72, -234), (36, -214), (0, -210)]
        else:
            right = [(0, -388), (52, -382), (90, -352), (104, -310), (116, -276), (100, -270), (110, -248), (84, -230),
                     (44, -214), (0, -210)]
        inner = []
        if self.stripe:
            for x0, x1, w in ((-26, -20, 10), (0, 0, 11), (26, 20, 10)):
                inner.append(('taper', self.Hs([(x0, -392), (x1, -352)]), w * hk, 2 * hk, self.stripe))
            for s in (-1, 1):
                inner.append(('taper', self.Hs([(s * 124, -302), (s * 84, -298)]), 9 * hk, 2 * hk, self.stripe))
                inner.append(('taper', self.Hs([(s * 124, -282), (s * 88, -282)]), 8 * hk, 2 * hk, self.stripe))
                inner.append(('taper', self.Hs([(s * 70, -372), (s * 58, -350)]), 7 * hk, 2 * hk, self.stripe))
                if br.get('heavy'):
                    inner.append(('taper', self.Hs([(s * 50, -390), (s * 42, -358)]), 8 * hk, 2 * hk, self.stripe))
                    inner.append(('taper', self.Hs([(s * 124, -262), (s * 92, -264)]), 7 * hk, 2 * hk, self.stripe))
        if self.pts:   # mặt nạ Xiêm
            inner.append(('poly', ellipse_pts(*self.H(0, -262), 72 * hk * self.hw, 56 * hk, n=36), self.pts['b']))
            inner.append(('poly', ellipse_pts(*self.H(0, -318), 34 * hk * self.hw, 44 * hk, n=30), self.pts['b']))
        elif self.muzzle is not None:
            for s in (-1, 1):
                inner.append(('poly', ellipse_pts(*self.H(s * 25, -256), 36 * hk * self.hw, 26 * hk, n=30), self.muzzle))
            inner.append(('poly', ellipse_pts(*self.H(0, -232), 28 * hk * self.hw, 16 * hk, n=24), self.muzzle))
        self.sh(cr(self.Hs(mirror(right)), n=8), self.fur, lw=3.0, shd=9, hld=5, inner=inner)
        for s in (-1, 1):
            self.eye(s, o['eyes'][0 if s < 0 else 1])
        brc = self.pts['s'] if self.pts else mix(self.stripe or self.fur['s'], (40, 20, 10), 0.35)
        for s, ang in zip((-1, 1), o.get('brow', (0, 0))):
            y0 = -338 - ang * 0.5
            stroke(cv, self.Hs([(s * 58, y0 + ang * 0.6), (s * 40, y0 - 4), (s * 22, y0 - ang * 0.6 + 2)]),
                   4 * hk, 2.5 * hk, brc, mid=7 * hk)
        nose = br.get('nose', PINK['b'])
        self.sh(cr(self.Hs([(-10, -279), (10, -279), (0, -268)]), n=5), dict(b=nose, s=mix(nose, (0, 0, 0), 0.3)),
                lw=2.0, shd=2, light=False)
        self.mouth(o.get('mouth', 'w'))
        wc = (245, 240, 230) if self.pts else INK
        for s in (-1, 1):
            for dy, ey in ((-6, -290), (0, -266), (6, -242)):
                p0, p2 = self.H(s * 48, -262 + dy), self.H(s * 146, ey)
                p1 = self.H(s * 98, (-262 + dy + ey) / 2 - 6)
                line(cv, cr([p0, p1, p2], closed=False, n=6), 2.0 * hk, wc)

    def eye(self, s, e):
        cv, hk = self.cv, self.hk
        kind = e.get('k', 'open')
        sc = e.get('sc', 1.0)
        ex, ey = self.H(s * 40, -308)
        rx, ry = 20 * hk * sc, 23 * hk * sc
        if kind == 'happy':
            line(cv, cr([(ex - rx, ey + ry * 0.25), (ex, ey - ry * 0.55), (ex + rx, ey + ry * 0.25)], closed=False, n=8),
                 4.6 * hk)
            return
        ell(cv, (ex, ey), rx, ry, fill=self.br['eye'], ow=2.8 * hk)
        gx, gy = e.get('g', (0, 0))
        px, py = ex + gx * rx * 0.32, ey + gy * ry * 0.25
        ell(cv, (px, py), rx * 0.36, ry * 0.78, fill=INK)
        ell(cv, (px - rx * 0.30, py - ry * 0.38), rx * 0.26, rx * 0.26, fill=(255, 255, 255))
        ell(cv, (px + rx * 0.28, py + ry * 0.36), rx * 0.11, rx * 0.11, fill=(255, 255, 255))
        lid = e.get('lid', 0.0)
        if lid > 0:
            tilt = e.get('tilt', 0.0) * s
            top = ey - ry

            def ly(x):
                return top + 2 * ry * lid + tilt * (x - ex)
            E = ellipse_pts(ex, ey, rx + 1.6 * hk, ry + 1.6 * hk, n=48)
            poly(cv, [(x, min(y, ly(x))) for x, y in E], (self.pts or self.fur)['s'])
            xs = [x for x, y in E if y <= ly(x) + 0.5]
            if xs:
                a, b = min(xs) - 2 * hk, max(xs) + 2 * hk
                line(cv, [(a, ly(a)), (b, ly(b))], 4.0 * hk)

    def mouth(self, m):
        cv, hk = self.cv, self.hk
        mc = (245, 240, 230) if self.pts else INK
        top = [(0, -268), (0, -260)]
        if m == 'w':
            line(cv, self.Hs(top), 2.6 * hk, mc)
            line(cv, cr(self.Hs([(-20, -254), (-10, -248), (0, -260), (10, -248), (20, -254)]), closed=False, n=6), 2.8 * hk, mc)
        elif m == 'smirk':
            line(cv, self.Hs(top), 2.6 * hk, mc)
            line(cv, cr(self.Hs([(-16, -252), (-8, -250), (0, -260), (14, -252), (28, -262), (32, -268)]), closed=False, n=6),
                 3.0 * hk, mc)
        elif m in ('grin', 'teeth'):
            P = cr(self.Hs([(-30, -258), (-14, -252), (0, -258), (14, -252), (30, -258), (22, -236), (0, -226), (-22, -236)]), n=6)
            teeth = ([('poly', self.Hs([(-24, -258), (24, -258), (22, -250), (-22, -250)]), (255, 255, 255))] if m == 'teeth' else
                     [('poly', self.Hs([(-24, -258), (-16, -258), (-20, -246)]), (255, 255, 255)),
                      ('poly', self.Hs([(16, -258), (24, -258), (20, -246)]), (255, 255, 255))])
            self.sh(P, dict(b=hx('#5C1A16')), lw=2.6, shade=False, light=False,
                    inner=[('poly', ellipse_pts(*self.H(4, -230), 15 * hk, 9 * hk, n=20), PINK['b'])] + teeth)
            line(cv, self.Hs(top), 2.6 * hk, mc)

    # -------------------------------------------------- tay
    def arm(self, a):
        k = self.k
        s = a['side']
        pts = [(s * x, y) for x, y in POSES[a['pose']]]
        P = cr(self.Bs(pts), closed=False, n=6)
        fur = self.fur
        sl = a.get('sleeve')
        if sl is None:
            stroke(self.cv, P, 27 * k, 22 * k, fur['b'], ink=2.6)
            root = fur['b']
        elif a.get('short'):
            stroke(self.cv, P, 25 * k, 22 * k, fur['b'], ink=2.6)
            half = P[:len(P) // 2 - 1]
            stroke(self.cv, half, 33 * k, 31 * k, sl['b'], ink=2.6)
            root = sl['b']
        else:
            stroke(self.cv, P, 28 * k, 24 * k, sl['b'], ink=2.6)
            root = sl['b']
            hx_, hy = self.B(*pts[-1])
            d = P[-1][0] - P[-3][0], P[-1][1] - P[-3][1]
            L = math.hypot(*d) or 1
            ux, uy = d[0] / L, d[1] / L
            line(self.cv, [(hx_ - ux * 10 * k - uy * 13 * k, hy - uy * 10 * k + ux * 13 * k),
                           (hx_ - ux * 10 * k + uy * 13 * k, hy - uy * 10 * k - ux * 13 * k)], 2.2 * k, sl['s'])
        # vá gốc tay (che nắp mực) – gốc nằm trong thân
        ell(self.cv, self.B(*pts[0]), 12.5 * k, 12.5 * k, fill=root)
        hand = self.B(*pts[-1])
        if a.get('prop'):
            a['prop'](self, hand)
        paw = a.get('paw', 'paw')
        if paw == 'none':
            return
        hx_, hy = hand
        pc = self.pawc
        if paw == 'open':
            self.sh(cr([(hx_ - 15 * k, hy + 8 * k), (hx_ - 17 * k, hy - 10 * k), (hx_ - 8 * k, hy - 20 * k),
                        (hx_ + 6 * k, hy - 20 * k), (hx_ + 16 * k, hy - 8 * k), (hx_ + 14 * k, hy + 10 * k)], n=5), pc,
                    lw=2.4, shd=3, hld=2,
                    inner=[('line', [(hx_ + dx * k, hy - 20 * k), (hx_ + dx * k, hy - 10 * k)], pc['s'], 2 * k) for dx in (-6, 2)])
            return
        self.sh(ellipse_pts(hx_, hy, 15 * k, 14 * k, n=24), pc, lw=2.4, shd=3, hld=2)
        if paw == 'thumb':
            stroke(self.cv, [(hx_ - 4 * k, hy - 8 * k), (hx_ - 6 * k, hy - 28 * k)], 10 * k, 9 * k, pc['b'], ink=2.2)

    # -------------------------------------------------- vẽ cả con
    def draw(self, head_only=False):
        o = self.o
        if not head_only:
            self.shadow()
        self.tail()
        self.legs()
        self.torso()
        for a in o.get('arms', []):
            if not a.get('front'):
                self.arm(a)
        self.head()
        for a in o.get('arms', []):
            if a.get('front'):
                self.arm(a)


# ------------------------------------------------------------------ đạo cụ
def tra_da(c, at):
    k = c.k
    x, y = at
    glass = [(x - 15 * k, y - 44 * k), (x + 15 * k, y - 44 * k), (x + 12 * k, y + 14 * k), (x - 12 * k, y + 14 * k)]
    c.sh(glass, dict(b=hx('#C9822E'), s=hx('#A0601C'), l=hx('#E2A653')), lw=2.4, shd=3, hld=3,
         inner=[('poly', [(x - 15 * k, y - 44 * k), (x + 15 * k, y - 44 * k), (x + 14 * k, y - 34 * k), (x - 14 * k, y - 34 * k)],
                 hx('#F3E3C4')),
                ('polyo', [(x - 8 * k, y - 32 * k), (x + 2 * k, y - 32 * k), (x + 2 * k, y - 22 * k), (x - 8 * k, y - 22 * k)],
                 hx('#F6EEDF'), hx('#C8B89A'), 1.2 * k),
                ('polyo', [(x + 2 * k, y - 20 * k), (x + 11 * k, y - 20 * k), (x + 11 * k, y - 11 * k), (x + 2 * k, y - 11 * k)],
                 hx('#F6EEDF'), hx('#C8B89A'), 1.2 * k),
                ('line', [(x - 11 * k, y - 30 * k), (x - 9 * k, y + 8 * k)], hx('#F0C27A'), 2.6 * k)])
    line(c.cv, [(x + 4 * k, y - 40 * k), (x + 12 * k, y - 66 * k)], 3.2 * k, RED['b'])


def phone(c, at):
    k = c.k
    x, y = at
    c.sh([(x - 9 * k, y - 32 * k), (x + 9 * k, y - 32 * k), (x + 9 * k, y + 2 * k), (x - 9 * k, y + 2 * k)],
         dict(b=hx('#2A2E36'), l=hx('#5A6270')), lw=2.2, shd=2, hld=2,
         inner=[('poly', [(x - 6 * k, y - 28 * k), (x + 6 * k, y - 28 * k), (x + 6 * k, y - 2 * k), (x - 6 * k, y - 2 * k)],
                 hx('#7FB6E0'))])


def cuon_su(c, at):
    k = c.k
    x, y = at
    a, b = (x - 34 * k, y + 14 * k), (x + 30 * k, y - 30 * k)
    c.sh(taper([a, b], 22 * k, 22 * k), CREAM, lw=2.4, shd=4, hld=2)
    for p in (a, b):
        c.sh(ellipse_pts(*p, 9 * k, 13 * k, n=16, rot=-0.6), dict(b=hx('#8A5A34'), s=hx('#62391C')), lw=2.2, shd=2, light=False)


# ------------------------------------------------------------------ 5 phong cách
SMUG = dict(eyes=(dict(lid=0.42, tilt=-0.15, g=(1, 0)), dict(lid=0.30, tilt=0.1, g=(1, 0))), brow=(0, 14), mouth='smirk')
WINK = dict(eyes=(dict(k='happy'), dict(g=(-0.4, -0.2))), brow=(-6, 6), mouth='grin')
HAPPY = dict(eyes=(dict(k='happy'), dict(k='happy')), brow=(6, 6), mouth='teeth')
SLY = dict(eyes=(dict(lid=0.30, tilt=0.12, g=(-1, 0)), dict(lid=0.30, tilt=0.12, g=(-1, 0))), brow=(10, -10), mouth='w')

DOI_MAU = dict(cam=('#3E7CB1', '#F2EFE8'), muop=('#2F6B4F', '#E9EEF4'), anh=('#E2B93B', '#FFFFFF'),
               xiem=('#B3261E', '#DDE8F2'), cup=('#5C4B8A', '#F7F1E1'))

STYLES = [
    ('Không mặc đồ', 'dáng đứng lém, chống nạnh',
     lambda g: dict(giong=g, **SMUG, arms=[dict(side=-1, pose='down'), dict(side=1, pose='hip')])),
    ('Sticker', 'không đồ, nét phẳng, vẫy chào',
     lambda g: dict(giong=g, flat=True, **HAPPY, arms=[dict(side=-1, pose='hip'), dict(side=1, pose='wave', paw='open', front=True)])),
    ('Polo + quần jean', 'đời thường, cầm ly trà đá',
     lambda g: dict(giong=g, outfit='polo', col=DOI_MAU[g][0], pants=DENIM, giay='#F4F1EA', **WINK,
                    arms=[dict(side=-1, pose='down', sleeve=C3(DOI_MAU[g][0]), short=True),
                          dict(side=1, pose='hold', sleeve=C3(DOI_MAU[g][0]), short=True, prop=tra_da)])),
    ('Sơ mi đóng thùng', 'quần tây, thắt lưng, cầm cuộn sử',
     lambda g: dict(giong=g, outfit='somi', col=DOI_MAU[g][1], pants=SLACK, giay='#3A2618', cavat=DOI_MAU[g][0], **SLY,
                    arms=[dict(side=-1, pose='chest', sleeve=C3(DOI_MAU[g][1]), prop=cuon_su),
                          dict(side=1, pose='hip', sleeve=C3(DOI_MAU[g][1]))])),
    ('Avatar', 'cận mặt, dùng làm ảnh kênh',
     lambda g: dict(giong=g, **SMUG, arms=[])),
]


def card(g, idx, CW, CH):
    name, desc, fn = STYLES[idx]
    o = fn(g)
    bgc = hx('#F8EFDC')
    cv = Image.new('RGBA', (CW * SS, CH * SS), bgc + (255,))
    if name == 'Avatar':
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        k = 1.45
        Cat(lay, CW / 2, 330 + 300 * k + 30, k, o).draw(head_only=True)
        R, cx, cy = 210, CW / 2, 330
        d = ImageDraw.Draw(cv)
        d.ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=hx('#14110F') + (255,))
        for rr in (180, 150, 120):
            d.ellipse([(cx - rr) * SS, (cy - rr) * SS, (cx + rr) * SS, (cy + rr) * SS], outline=hx('#3A2F1E') + (255,),
                      width=3 * SS)
        m = Image.new('L', cv.size, 0)
        ImageDraw.Draw(m).ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=255)
        a = np.minimum(np.asarray(lay)[..., 3], np.asarray(m))
        arr = np.asarray(lay).copy()
        arr[..., 3] = a
        cv.alpha_composite(Image.fromarray(arr, 'RGBA'))
        d = ImageDraw.Draw(cv)
        d.ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], outline=hx('#C9A24A') + (255,), width=8 * SS)
    elif name == 'Sticker':
        cv = Image.new('RGBA', cv.size, hx('#FBE3CF') + (255,))
        d = ImageDraw.Draw(cv)
        for yy in range(30, CH, 46):
            for xx in range(30 + (yy // 46 % 2) * 23, CW, 46):
                d.ellipse([(xx - 3) * SS, (yy - 3) * SS, (xx + 3) * SS, (yy + 3) * SS], fill=hx('#F4CDB0') + (255,))
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        Cat(lay, CW / 2 - 8, 600, 1.0, o).draw(head_only=True)
        al = np.asarray(lay)[..., 3] > 0
        dist = ndimage.distance_transform_edt(~al)
        border = (dist <= 12 * SS)
        sh = np.zeros(al.shape + (4,), np.uint8)
        sh[..., :3] = (120, 80, 60)
        sh[..., 3] = (np.roll(np.roll(border, 8 * SS, 0), 6 * SS, 1) * 70).astype(np.uint8)
        cv.alpha_composite(Image.fromarray(sh, 'RGBA'))
        wb = np.zeros(al.shape + (4,), np.uint8)
        wb[..., :3] = 255
        wb[..., 3] = border.astype(np.uint8) * 255
        cv.alpha_composite(Image.fromarray(wb, 'RGBA'))
        cv.alpha_composite(lay)
    else:
        Cat(cv, CW / 2 - 8, 620, 1.05, o).draw()
    return cv.resize((CW, CH), Image.LANCZOS).convert('RGB')


def sheet(g):
    CW, CH, TOP, BOT = 480, 700, 100, 90
    W, H = CW * 5, TOP + CH + BOT
    img = Image.new('RGB', (W, H), hx('#F2E6CC'))
    dr = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf'), 50)
    f_n = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 28)
    f_d = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf'), 19)
    dr.text((36, 22), f'MÈO NGHỆ · {BREEDS[g]["ten"].upper()} – 5 phong cách', font=f_t, fill=hx('#14110F'))
    for i in range(5):
        c = card(g, i, CW - 24, CH)
        x0 = i * CW + 12
        img.paste(c, (x0, TOP))
        dr.rectangle([x0, TOP, x0 + CW - 25, TOP + CH - 1], outline=hx('#C9A24A'), width=2)
        name, desc, _ = STYLES[i]
        dr.text((i * CW + CW / 2, TOP + CH + 28), f'{i + 1} · {name}', font=f_n, fill=hx('#B3261E'), anchor='mm')
        dr.text((i * CW + CW / 2, TOP + CH + 62), desc, font=f_d, fill=hx('#4A3E3A'), anchor='mm')
    p = os.path.join(OUT, f'giong-{g}.jpg')
    img.save(p, quality=90)
    return p, img


def main():
    os.makedirs(OUT, exist_ok=True)
    keys = sys.argv[1:] or list(BREEDS)
    imgs = []
    for g in keys:
        p, im = sheet(g)
        imgs.append(im)
        print(p)
    if len(imgs) > 1:
        w = imgs[0].width
        tot = Image.new('RGB', (w, sum(i.height for i in imgs)), hx('#F2E6CC'))
        y = 0
        for im in imgs:
            tot.paste(im, (0, y))
            y += im.height
        tot.resize((w // 2, tot.height // 2), Image.LANCZOS).save(os.path.join(OUT, 'tong-hop.jpg'), quality=88)


if __name__ == '__main__':
    main()
