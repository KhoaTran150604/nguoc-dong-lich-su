"""Nhân vật NGƯỜI cho thế giới Gâu Nghệ (lối sitcom: màu phẳng, viền đậm, 1 mảng bóng cứng).

Gâu Nghệ là con vật duy nhất; mọi nhân vật khác là người (cao hơn Gâu → tương phản kích thước, sổ tay M5).
Cách vẽ: chân (quần) → tay da (sau thân) → thân+tay áo (MỘT khối liền viền) → cổ/đầu → tóc → mặt → đạo cụ.

    Human(cv, x, gy, s, CAST['khang'], st).draw()
st: arms=((a1,a2),(a1,a2)) | arm_to={'L':(x,y),'R':(x,y)} (toạ độ cục bộ) | mouth: smile/talk/D/o/flat/frown/grin
    mo (0..1 độ mở khi talk) | eyes: open/happy/closed/wide/line/angry | gaze (dx,dy) | brow (deg) | sit | walk (pha)
    hold={'R': 'racket'|'phone'|'bottle'|'magnifier'|'banhmi'} | lean (độ)
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, cr, taper, ellipse_pts, mix  # noqa: E402
import meo_nghe_cach_dieu as M  # noqa: E402

_blob0 = M.blob


def blob(cv, polys, col, lw=3.0):
    """Khối một viền, lối sitcom (viền ×1.45, bóng cứng, không highlight)."""
    c = M.C3(col) if isinstance(col, str) else col
    _blob0(cv, polys, c, lw=lw * 1.45, shd=12, hld=0)


def tube(P, w0, w1):
    P = cr(P, closed=False, n=8)
    return [taper(P, w0, w1), ellipse_pts(*P[0], w0 / 2, w0 / 2, n=20), ellipse_pts(*P[-1], w1 / 2, w1 / 2, n=20)]


SKIN = '#F6D2B4'
CAST = {
    'khang': dict(ten='Khang', h='tall', skin=SKIN, shirt='#2F6FB5', pants='#22252C', shoe='#F4F4F4', hair='#1E1B1A',
                  style='quiff', vai='đẹp trai, kiêu, đánh hay'),
    'tung':  dict(ten='Tùng', h='fat', skin='#EFC39C', shirt='#F2C14E', pants='#5E6A7C', shoe='#C8382E', hair='#2A2420',
                  style='buzz', vai='mập, ham ăn, lắm mồm'),
    'na':    dict(ten='Na', h='girl', skin=SKIN, shirt='#E8768C', pants='#F2F0EA', shoe='#FFFFFF', hair='#3A2A22',
                  style='pony', band='#FFD34D', vai='lanh chanh, thích sống ảo'),
    'thay':  dict(ten='Thầy Ba', h='coach', skin='#E8B890', shirt='#7E8A96', pants='#2E3A5C', shoe='#2A2A2A', hair='#9A968E',
                  style='cap', capc='#C8382E', vai='thầy thể dục khó tính'),
}
BUILD = {   # hip_y, sh_y, sh_w, waist_w, hip_w, leg_x, leg_w, head (cy, rx, ry), upper, fore
    'tall':  dict(hip=-190, sh=-338, shw=50, waist=38, hipw=42, legx=20, legw=30, head=(-392, 46, 52), up=62, fo=60),
    'fat':   dict(hip=-130, sh=-262, shw=58, waist=80, hipw=66, legx=28, legw=40, head=(-312, 52, 50), up=52, fo=50),
    'girl':  dict(hip=-160, sh=-282, shw=40, waist=30, hipw=38, legx=16, legw=24, head=(-332, 44, 48), up=52, fo=50),
    'coach': dict(hip=-170, sh=-318, shw=52, waist=50, hipw=46, legx=20, legw=32, head=(-372, 46, 52), up=60, fo=58),
}


class Human:
    def __init__(self, cv, x, gy, s, d, st=None):
        self.cv, self.x, self.gy, self.s, self.d = cv, x, gy, s, d
        self.st = st or {}
        self.b = dict(BUILD[d['h']])
        if self.st.get('sit'):          # ngồi: hạ cả thân xuống bằng chiều dài đùi
            self.drop = -self.b['hip'] * 0.45
        else:
            self.drop = 0.0
        self.hands = {}

    def P(self, x, y):
        a = math.radians(self.st.get('lean', 0))
        y = y + self.drop if y < -10 or not self.st.get('sit') else y
        if a:                            # nghiêng thân quanh chân
            x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        return (self.x + x * self.s, self.gy + y * self.s)

    def Ps(self, pts):
        return [self.P(*p) for p in pts]

    # ---------------- tay
    def arm(self, side):
        b, st = self.b, self.st
        sh = (side * b['shw'] * 0.92, b['sh'] + 14)
        key = 'R' if side > 0 else 'L'
        if key in st.get('arm_to', {}):
            hd = st['arm_to'][key]
            dx, dy = hd[0] - sh[0], hd[1] - sh[1]
            dd = min(math.hypot(dx, dy), (b['up'] + b['fo']) * 0.999)
            a = math.atan2(dy, dx)
            cb = (b['up'] ** 2 + dd ** 2 - b['fo'] ** 2) / (2 * b['up'] * dd)
            bb = math.acos(max(-1, min(1, cb)))
            a1 = a - bb if side > 0 else a + bb
            el = (sh[0] + b['up'] * math.cos(a1), sh[1] + b['up'] * math.sin(a1))
            hd = (sh[0] + dd * math.cos(a), sh[1] + dd * math.sin(a))
            return sh, el, hd
        arms = st.get('arms', ((14, 6), (14, 6)))
        a1, a2 = arms[0] if side < 0 else arms[1]
        g1, g2 = math.radians(a1), math.radians(a2)
        el = (sh[0] + side * b['up'] * math.sin(g1), sh[1] + b['up'] * math.cos(g1))
        hd = (el[0] + side * b['fo'] * math.sin(g2), el[1] + b['fo'] * math.cos(g2))
        return sh, el, hd

    # ---------------- vẽ
    def draw(self):
        d, b, st, s, cv = self.d, self.b, self.st, self.s, self.cv
        # bóng chân
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        fx, fy = self.x, self.gy
        ImageDraw.Draw(lay).ellipse([(fx - 62 * s) * SS, (fy - 9 * s) * SS, (fx + 62 * s) * SS, (fy + 9 * s) * SS],
                                    fill=(30, 25, 40, 70))
        cv.alpha_composite(lay)
        # chân
        legs = []
        ph = st.get('walk')
        for sd in (-1, 1):
            hip = (sd * b['legx'], b['hip'])
            if st.get('sit'):
                knee = (sd * (b['legx'] + 6), b['hip'] + 10 - self.drop * 0)
                foot = (sd * (b['legx'] + 10), -6 - self.drop)
                pts = [self.P(*hip), self.P(*knee)]
                pts.append((self.x + foot[0] * s, self.gy - 6 * s))
            else:
                sw = 0 if ph is None else 26 * math.sin(ph + (0 if sd < 0 else math.pi))
                lift = 0 if ph is None else max(0, 14 * math.sin(ph + (0 if sd < 0 else math.pi)))
                pts = self.Ps([hip, (sd * b['legx'] + sw * 0.5, b['hip'] * 0.5), (sd * (b['legx'] + 4) + sw, -8 - lift)])
            legs.append(pts)
        lw_ = b['legw'] * s
        polys = []
        for pts in legs:
            polys += tube(pts, lw_, lw_ * 0.85)
        polys.append(self.Ps([(-b['hipw'], b['hip'] - 30), (b['hipw'], b['hip'] - 30), (b['hipw'], b['hip'] + 12),
                              (-b['hipw'], b['hip'] + 12)]))
        if d['h'] in ('girl', 'tall', 'fat'):          # quần đùi: da chân dưới gối
            skin_l = []
            for pts in legs:
                skin_l += tube(pts[1:], lw_ * 0.8, lw_ * 0.75)
            blob(cv, skin_l, d['skin'])
            sh_polys = []
            for pts in legs:
                mid = ((pts[0][0] + pts[1][0]) / 2 * 0 + pts[1][0], pts[1][1])
                sh_polys += tube([pts[0], mid], lw_ * 1.15, lw_ * 1.15)
            sh_polys.append(polys[-1])
            blob(cv, sh_polys, d['pants'])
        else:
            blob(cv, polys, d['pants'])
        for pts in legs:                                   # giày
            fx_, fy_ = pts[-1]
            blob(cv, [ellipse_pts(fx_ + 6 * s * np.sign(fx_ - self.x + 1e-6), fy_ + 4 * s, 24 * s, 12 * s, n=24)], d['shoe'])
        # tay (da) – vẽ trước thân để tay áo che chỗ nối
        arms = {}
        skin_p = []
        for sd in (-1, 1):
            sh, el, hd = self.arm(sd)
            arms[sd] = (sh, el, hd)
            skin_p += tube(self.Ps([((sh[0] + el[0]) / 2, (sh[1] + el[1]) / 2), el, hd]), 20 * s, 17 * s)
            skin_p.append(ellipse_pts(*self.P(*hd), 13 * s, 13 * s, n=24))
            self.hands['R' if sd > 0 else 'L'] = self.P(*hd)
        blob(cv, skin_p, d['skin'])
        # thân + tay áo: MỘT khối
        if d['h'] == 'fat':
            right = [(0, b['sh'] - 6), (b['shw'], b['sh'] + 6), (b['waist'] + 6, b['hip'] - 70), (b['waist'], b['hip'] - 6), (0, b['hip'] + 4)]
        elif d['h'] == 'girl':
            right = [(0, b['sh'] - 4), (b['shw'], b['sh'] + 4), (b['waist'], b['hip'] - 50), (b['hipw'] + 4, b['hip'] + 4), (0, b['hip'] + 8)]
        else:
            right = [(0, b['sh'] - 6), (b['shw'], b['sh'] + 4), (b['waist'] + 4, b['hip'] - 40), (b['waist'], b['hip'] + 6), (0, b['hip'] + 8)]
        body = cr(self.Ps(right + [(-x, y) for x, y in right[1:-1]][::-1]), n=8)
        polys = [body]
        for sd in (-1, 1):
            sh, el, hd = arms[sd]
            cut = (sh[0] + (el[0] - sh[0]) * 0.62, sh[1] + (el[1] - sh[1]) * 0.62)
            polys += tube(self.Ps([(sh[0] - sd * 6, sh[1] - 6), sh, cut]), 34 * s, 28 * s)
        blob(cv, polys, d['shirt'])
        dr = ImageDraw.Draw(cv)
        if d['h'] == 'coach':                              # cổ áo polo + dây còi
            M.line(cv, [self.P(-14, b['sh'] - 2), self.P(0, b['sh'] + 18), self.P(14, b['sh'] - 2)], 3 * s)
            M.line(cv, [self.P(-16, b['sh']), self.P(-4, b['sh'] + 70), self.P(10, b['sh'])], 2 * s, hx('#C8382E'))
            M.ell(cv, self.P(-4, b['sh'] + 78), 9 * s, 7 * s, fill=hx('#C9CDD2'), ow=2.4 * s)
        if d['ten'] == 'Khang':                            # số áo
            M.line(cv, [self.P(-30, b['sh'] + 40), self.P(30, b['sh'] + 40)], 4 * s, hx('#F4F4F4'))
        # cổ + đầu + tai
        hcy, rx, ry = b['head']
        neck = [self.P(-12, b['sh'] + 8), self.P(12, b['sh'] + 8), self.P(12, hcy + ry * 0.6), self.P(-12, hcy + ry * 0.6)]
        head = ellipse_pts(*self.P(0, hcy), rx * s, ry * s, n=60)
        ears = [ellipse_pts(*self.P(sd * rx * 0.98, hcy + 6), 9 * s, 13 * s, n=20) for sd in (-1, 1)]
        if d['style'] == 'pony':                            # đuôi ngựa sau đầu
            tail = tube(self.Ps([(rx * 0.6, hcy - ry * 0.5), (rx * 1.3, hcy - ry * 0.2), (rx * 1.15, hcy + ry * 0.8)]), 30 * s, 16 * s)
            blob(cv, tail, d['hair'])
        blob(cv, [neck, head] + ears, d['skin'])
        self.hair(hcy, rx, ry)
        self.face(hcy, rx, ry)
        self.props()

    def hair(self, hcy, rx, ry):
        d, s = self.d, self.s
        P = self.P
        st = d['style']
        if st == 'quiff':
            pts = [(-rx * 1.02, hcy + 4), (-rx * 0.95, hcy - ry * 0.6), (-rx * 0.4, hcy - ry * 1.08), (rx * 0.3, hcy - ry * 1.3),
                   (rx * 0.95, hcy - ry * 1.05), (rx * 1.04, hcy - ry * 0.2), (rx * 0.9, hcy - 2), (rx * 0.75, hcy - ry * 0.45),
                   (0, hcy - ry * 0.55), (-rx * 0.7, hcy - ry * 0.4), (-rx * 0.86, hcy + 2)]
            blob(self.cv, [cr(self.Ps(pts), n=6)], d['hair'])
        elif st == 'buzz':
            pts = [(-rx * 1.0, hcy - ry * 0.1), (-rx * 0.8, hcy - ry * 0.85), (0, hcy - ry * 1.04), (rx * 0.8, hcy - ry * 0.85),
                   (rx * 1.0, hcy - ry * 0.1), (rx * 0.82, hcy - ry * 0.5), (0, hcy - ry * 0.7), (-rx * 0.82, hcy - ry * 0.5)]
            blob(self.cv, [cr(self.Ps(pts), n=6)], d['hair'])
        elif st == 'pony':
            pts = [(-rx * 1.06, hcy + ry * 0.5), (-rx * 1.0, hcy - ry * 0.6), (-rx * 0.3, hcy - ry * 1.08), (rx * 0.5, hcy - ry * 1.0),
                   (rx * 1.05, hcy - ry * 0.4), (rx * 1.04, hcy + ry * 0.3), (rx * 0.8, hcy - ry * 0.3), (rx * 0.2, hcy - ry * 0.42),
                   (-rx * 0.4, hcy - ry * 0.36), (-rx * 0.8, hcy - ry * 0.2)]
            blob(self.cv, [cr(self.Ps(pts), n=6)], d['hair'])
            M.line(self.cv, [P(-rx * 0.98, hcy - ry * 0.45), P(0, hcy - ry * 0.78), P(rx * 0.98, hcy - ry * 0.45)], 7 * s, hx(d['band']))
        elif st == 'cap':
            for sd in (-1, 1):
                blob(self.cv, [ellipse_pts(*P(sd * rx * 0.9, hcy - 2), 10 * s, 18 * s, n=20)], d['hair'])
            cap = [(-rx * 1.04, hcy - ry * 0.3), (-rx * 0.9, hcy - ry * 0.9), (0, hcy - ry * 1.12), (rx * 0.9, hcy - ry * 0.9),
                   (rx * 1.04, hcy - ry * 0.3)]
            brim = [(-rx * 1.0, hcy - ry * 0.36), (rx * 1.5, hcy - ry * 0.36), (rx * 1.45, hcy - ry * 0.2), (-rx * 1.0, hcy - ry * 0.2)]
            blob(self.cv, [cr(self.Ps(cap), n=6), self.Ps(brim)], d['capc'])

    def face(self, hcy, rx, ry):
        st, s, cv, d = self.st, self.s, self.cv, self.d
        P = self.P
        gx, gy = st.get('gaze', (0, 0))
        eyes = st.get('eyes', 'open')
        ey = hcy + ry * 0.08
        for sd in (-1, 1):
            cx, cy = P(sd * rx * 0.36, ey)
            if eyes == 'happy':
                M.line(cv, [(cx - 9 * s, cy + 3 * s), (cx, cy - 6 * s), (cx + 9 * s, cy + 3 * s)], 3.4 * s)
            elif eyes in ('closed', 'line'):
                M.line(cv, [(cx - 9 * s, cy), (cx + 9 * s, cy)], 3.4 * s)
            else:
                big = 1.35 if eyes == 'wide' else 1.0
                M.ell(cv, (cx, cy), 10 * s * big, 13 * s * big, fill=(255, 255, 255), ow=2.6 * s)
                pr = (4.6 if eyes != 'wide' else 3.6) * s
                M.ell(cv, (cx + gx * 4 * s, cy + gy * 5 * s), pr, pr * 1.15, fill=INK)
                lid = st.get('lid', 0)
                if lid:
                    y0 = cy - 13 * s * big
                    ImageDraw.Draw(cv).rectangle([(cx - 12 * s) * SS, (y0 - 2 * s) * SS, (cx + 12 * s) * SS,
                                                  (y0 + 26 * s * big * lid) * SS], fill=hx(d['skin']) + (255,))
                    M.line(cv, [(cx - 11 * s, y0 + 26 * s * big * lid), (cx + 11 * s, y0 + 26 * s * big * lid)], 3 * s)
            # lông mày
            br = st.get('brow', 0)
            if eyes == 'angry':
                br = 22
            a = math.radians(br) * sd
            bx, by = P(sd * rx * 0.38, ey - 24 - (4 if eyes == 'wide' else 0))
            M.line(cv, [(bx - 11 * s * math.cos(a), by + 11 * s * math.sin(a) * -1 * -1 - 11 * s * math.sin(a) * 2 * 0),
                        (bx + 11 * s * math.cos(a), by - 11 * s * math.sin(a) * -1)], 4 * s, hx(d['hair']) if d['style'] != 'cap' else INK)
        # má hồng (Na)
        if d['style'] == 'pony':
            for sd in (-1, 1):
                lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
                cx, cy = P(sd * rx * 0.6, ey + 18)
                ImageDraw.Draw(lay).ellipse([(cx - 10 * s) * SS, (cy - 6 * s) * SS, (cx + 10 * s) * SS, (cy + 6 * s) * SS],
                                            fill=(240, 120, 130, 140))
                cv.alpha_composite(lay)
        # mũi
        nx, ny = P(gx * 3, ey + 16)
        M.line(cv, [(nx - 2 * s, ny - 6 * s), (nx - 4 * s, ny + 3 * s), (nx + 3 * s, ny + 4 * s)], 2.6 * s)
        if d['style'] == 'cap':                            # ria mép
            mx, my = P(gx * 3, ey + 27)
            blob(cv, [ellipse_pts(mx - 9 * s, my, 11 * s, 5 * s, n=16), ellipse_pts(mx + 9 * s, my, 11 * s, 5 * s, n=16)], '#9A968E')
        # miệng
        mx, my = P(gx * 3, ey + 36)
        m = st.get('mouth', 'smile')
        mo = st.get('mo', 0.0)
        if m == 'talk':
            m = 'flat' if mo < 0.12 else 'open'
        if m == 'smile':
            M.line(cv, [(mx - 12 * s, my - 3 * s), (mx, my + 4 * s), (mx + 12 * s, my - 3 * s)], 3.2 * s)
        elif m == 'grin':
            M.line(cv, [(mx - 16 * s, my - 6 * s), (mx - 4 * s, my + 3 * s), (mx + 14 * s, my - 8 * s)], 3.4 * s)
        elif m == 'flat':
            M.line(cv, [(mx - 9 * s, my), (mx + 9 * s, my)], 3.2 * s)
        elif m == 'frown':
            M.line(cv, [(mx - 11 * s, my + 4 * s), (mx, my - 3 * s), (mx + 11 * s, my + 4 * s)], 3.2 * s)
        elif m == 'o':
            M.ell(cv, (mx, my + 2 * s), 6 * s, 8 * s, fill=hx('#7A2A2A'), ow=2.6 * s)
        else:                                              # open / D
            h = (6 + 14 * (mo if st.get('mouth') == 'talk' else 1.0)) * s
            w = (16 if m == 'D' else 12) * s
            poly = [(mx - w, my - 4 * s)] + [(mx + w * math.cos(t), my - 4 * s + h * math.sin(t)) for t in np.linspace(0, math.pi, 14)][::-1]
            poly = [(mx - w, my - 4 * s), (mx + w, my - 4 * s)] + [(mx + w * math.cos(t), my - 4 * s + h * math.sin(t))
                                                                  for t in np.linspace(0, math.pi, 14)]
            ImageDraw.Draw(cv).polygon([(x * SS, y * SS) for x, y in poly], fill=hx('#7A2A2A') + (255,))
            if h > 10 * s:
                ImageDraw.Draw(cv).ellipse([(mx - w * 0.5) * SS, (my + h * 0.35) * SS, (mx + w * 0.5) * SS,
                                            (my - 4 * s + h * 0.98) * SS], fill=hx('#E2707A') + (255,))
            M.line(cv, poly + [poly[0]], 2.8 * s)

    def props(self):
        hold = self.st.get('hold', {})
        for k, what in hold.items():
            if k in self.hands:
                prop(self.cv, what, self.hands[k], self.s, self.st.get('prop_ang', {}).get(k, -30))


def prop(cv, what, at, s, ang=-30):
    """Đạo cụ cầm tay, `at` = tâm bàn tay (toạ độ khung), ang = góc cán (độ, 0 = thẳng lên)."""
    x, y = at
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    if what == 'racket':
        L = 70 * s
        hx_, hy_ = x + ux * L, y + uy * L
        M.line(cv, [(x - ux * 14 * s, y - uy * 14 * s), (hx_, hy_)], 6 * s, hx('#3A3A44'))
        cx, cy = x + ux * (L + 44 * s), y + uy * (L + 44 * s)
        e = [(cx + 30 * s * math.cos(t) * math.cos(a) - 46 * s * math.sin(t) * math.sin(a),
              cy + 30 * s * math.cos(t) * math.sin(a) + 46 * s * math.sin(t) * math.cos(a)) for t in np.linspace(0, 2 * math.pi, 48)]
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        dr.polygon([(px * SS, py * SS) for px, py in e], fill=(255, 255, 255, 80))
        vx, vy = math.cos(a), math.sin(a)              # trục ngang của mặt vợt
        for k in np.linspace(-1, 1, 9):                 # dây dọc + ngang, cắt theo mặt vợt
            for (ax, ay), (bx_, by_), L2 in (((vx, vy), (-vy, vx), 50), ((-vy, vx), (vx, vy), 34)):
                ox, oy = cx + bx_ * k * (34 if L2 == 50 else 50) * s, cy + by_ * k * (34 if L2 == 50 else 50) * s
                dr.line([((ox - ax * L2 * s) * SS, (oy - ay * L2 * s) * SS), ((ox + ax * L2 * s) * SS, (oy + ay * L2 * s) * SS)],
                        fill=(110, 110, 120, 255), width=max(1, int(1.3 * s * SS)))
        m = Image.new('L', cv.size, 0)
        ImageDraw.Draw(m).polygon([(px * SS, py * SS) for px, py in e], fill=255)
        arr = np.asarray(lay).copy()
        arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
        lay = Image.fromarray(arr, 'RGBA')
        cv.alpha_composite(lay)
        M.line(cv, e + [e[0]], 6 * s, hx('#C8382E'))
        M.ell(cv, (x, y), 13 * s, 13 * s, fill=hx(SKIN), ow=3.2 * s)
    elif what == 'phone':
        w, h = 22 * s, 40 * s
        pts = [(x - w, y - h - 8 * s), (x + w, y - h - 8 * s), (x + w, y + 8 * s), (x - w, y + 8 * s)]
        blob(cv, [pts], '#2A2A30')
        M.ell(cv, (x, y), 12 * s, 12 * s, fill=hx(SKIN), ow=3 * s)
    elif what == 'bottle':
        pts = [(x - 12 * s, y - 64 * s), (x + 12 * s, y - 64 * s), (x + 14 * s, y + 20 * s), (x - 14 * s, y + 20 * s)]
        blob(cv, [pts], '#9ED3E6')
        blob(cv, [[(x - 7 * s, y - 78 * s), (x + 7 * s, y - 78 * s), (x + 7 * s, y - 62 * s), (x - 7 * s, y - 62 * s)]], '#3B5E8C')
        M.ell(cv, (x, y), 12 * s, 12 * s, fill=hx(SKIN), ow=3 * s)
    elif what == 'magnifier':
        M.line(cv, [(x, y), (x + ux * 42 * s, y + uy * 42 * s)], 12 * s, INK)
        cx, cy = x + ux * 70 * s, y + uy * 70 * s
        M.ell(cv, (cx, cy), 32 * s, 32 * s, fill=hx('#D8EEF4'), ow=7 * s)
        M.line(cv, [(cx - 14 * s, cy - 10 * s), (cx - 4 * s, cy - 20 * s)], 4 * s, hx('#FFFFFF'))
        M.ell(cv, (x, y), 12 * s, 12 * s, fill=hx(SKIN), ow=3 * s)
    elif what == 'banhmi':
        e = ellipse_pts(x, y - 10 * s, 52 * s, 16 * s, n=30)
        blob(cv, [[(px, py + (py - y) * 0.0) for px, py in e]], '#E0A85A')
        for k in (-24, 0, 24):
            M.line(cv, [(x + (k - 8) * s, y - 18 * s), (x + (k + 8) * s, y - 14 * s)], 2.6 * s, hx('#B07A3A'))
        M.ell(cv, (x, y), 12 * s, 12 * s, fill=hx(SKIN), ow=3 * s)
    elif what == 'whistle':
        M.ell(cv, (x, y - 6 * s), 14 * s, 9 * s, fill=hx('#C9CDD2'), ow=3 * s)
        M.ell(cv, (x, y), 12 * s, 12 * s, fill=hx(SKIN), ow=3 * s)


def demo():
    from gau_nghe_van import Dog, ROOT
    out = os.path.join(ROOT, 'build', 'thu-hoathinh', 'cau-long')
    os.makedirs(out, exist_ok=True)
    W, H = 1600, 900
    cv = Image.new('RGBA', (W * SS, H * SS), hx('#EFE6D2') + (255,))
    gy = 800
    Human(cv, 230, gy, 1.0, CAST['khang'], dict(arms=((14, 6), (60, 160)), hold={'R': 'racket'}, prop_ang={'R': 20},
                                                 mouth='grin', gaze=(1, 0))).draw()
    Human(cv, 520, gy, 1.0, CAST['na'], dict(arm_to={'R': (40, -330)}, hold={'R': 'phone'}, mouth='D', eyes='happy')).draw()
    Dog(cv, 800, gy, 0.82, dict(mouth='smirk', flat=True, arms=((18, 8), (80, 122)))).draw()
    Human(cv, 1060, gy, 1.0, CAST['tung'], dict(arm_to={'L': (-40, -200)}, hold={'L': 'banhmi'}, mouth='open', gaze=(-1, 0))).draw()
    Human(cv, 1380, gy, 1.0, CAST['thay'], dict(arms=((14, 6), (130, 175)), mouth='frown', eyes='angry', gaze=(-1, 0))).draw()
    im = cv.resize((W, H), Image.LANCZOS).convert('RGB')
    p = os.path.join(out, 'dan-nhan-vat.png')
    im.save(p)
    print(p)


if __name__ == '__main__':
    demo()
