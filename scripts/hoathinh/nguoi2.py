"""Nhân vật NGƯỜI bản 2 – vẽ kỹ ngang Gâu Nghệ (19/11/2026, theo góp ý "người xấu, mất tay").

Khác bản 1 (nguoi.py):
- Tỉ lệ chibi gần Gâu: đầu to (~1/3 chiều cao), mắt có tròng + chấm sáng như Gâu, lông mày nét thon.
- Tay vẽ SAU thân, ĐÈ LÊN thân, có tay áo + bàn tay có ngón cái → không bao giờ "lọt" vào thân / mất tay.
- Quần áo có chi tiết: cổ áo, viền tay áo, hình in, sọc quần, tất, giày có đế + dây.
- Tóc là khối riêng có lọn sáng/tối; mỗi người một dáng (Khang tóc vuốt cao, Tùng đầu đinh, Na đuôi ngựa + mái, Thầy nón).

API giữ như bản 1:  Human(cv, x, gy, s, CAST[key], st).draw();  prop(cv, what, at, s, ang)
st: arms=((a1,a2),(a1,a2)) | arm_to={'L':(x,y),'R':(x,y)} | mouth smile/talk/D/open/o/flat/frown/grin/smirk | mo
    eyes open/happy/closed/wide/angry/line/sleepy | gaze (dx,dy) | brow (độ) | lid (0..1) | sit | walk (pha) | lean (độ)
    hold={'R': racket|phone|bottle|magnifier|banhmi|whistle|mic} | prop_ang {'R': độ} | blush | sweat
Chạy thử:  python scripts/hoathinh/nguoi2.py  → build/thu-hoathinh/cau-long/nhan-vat-v2.png
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, cr, taper, ellipse_pts, stroke  # noqa: E402
import meo_nghe_cach_dieu as M  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def C(col, sh=0.80, li=1.10):
    if isinstance(col, dict):
        return col
    r, g, b = hx(col)
    return dict(b=(r, g, b), s=tuple(int(v * sh) for v in (r, g, b)), l=tuple(min(255, int(v * li)) for v in (r, g, b)))


def blob(cv, polys, col, lw=3.4, shd=10, inner=()):
    """Khối một viền lối sitcom: viền đậm, 1 mảng bóng cứng, không highlight mềm."""
    M.blob(cv, polys, C(col), lw=lw * 1.45, shd=shd, hld=0, inner=inner)


def tube(P, w0, w1, n=8):
    P = cr(P, closed=False, n=n)
    return [taper(P, w0, w1), ellipse_pts(*P[0], w0 / 2, w0 / 2, n=20), ellipse_pts(*P[-1], w1 / 2, w1 / 2, n=20)]


def dark(col, k=0.72):
    r, g, b = hx(col) if isinstance(col, str) else col
    return (int(r * k), int(g * k), int(b * k))


SKIN = '#F7D3B5'
CAST = {
    'khang': dict(ten='Khang', h='tall', skin=SKIN, shirt='#3A6EA8', trim='#F4F4F4', pants='#23262E', stripe='#F4F4F4',
                  sock='#FFFFFF', shoe='#F4F4F4', sole='#C8382E', hair='#24201F', style='quiff', print='so',
                  band='#C8382E', iris='#3A2A20', lid0=0.42, vai='cao, đẹp trai, tóc vuốt, kiêu, đánh hay'),
    'tung':  dict(ten='Tùng', h='fat', skin='#F0C49E', shirt='#EBBE55', trim='#D49A34', pants='#6A7486', stripe=None,
                  sock='#FFFFFF', shoe='#C8382E', sole='#F4F4F4', hair='#2A2420', style='buzz', print='banh',
                  iris='#3A2A20', vai='mập, ham ăn, lười chạy, lắm mồm'),
    'na':    dict(ten='Na', h='girl', skin=SKIN, shirt='#E88AA0', trim='#FFFFFF', pants='#5B7DB8', stripe=None,
                  sock='#FFFFFF', shoe='#F7A8BA', sole='#FFFFFF', hair='#3B2A22', style='pony', print='sao',
                  band='#FFD34D', iris='#4A2E22', vai='lanh chanh, thích sống ảo'),
    'thay':  dict(ten='Thầy Ba', h='coach', skin='#E9B98F', shirt='#8A96A3', trim='#5E6A78', pants='#2E3A5C', stripe='#F4F4F4',
                  sock='#2E3A5C', shoe='#2A2A2E', sole='#F4F4F4', hair='#9C978E', style='cap', capc='#C8382E',
                  print='coi', iris='#2A2220', vai='thầy thể dục khó tính'),
}
# toạ độ cục bộ (đơn vị trước khi nhân s), y âm = lên, 0 = mặt sàn
HEAD_K = 1.18
BUILD = {
    'tall':  dict(head=(-440, 62, 68), sh=-350, shw=60, chest=56, waist=44, hip=-210, hipw=48, legx=22, legw=30,
                  up=66, fo=62, neck=14),
    'fat':   dict(head=(-352, 78, 74), sh=-262, shw=62, chest=74, waist=92, hip=-118, hipw=70, legx=30, legw=50,
                  up=56, fo=52, neck=16),
    'girl':  dict(head=(-366, 70, 74), sh=-284, shw=42, chest=40, waist=34, hip=-168, hipw=44, legx=17, legw=25,
                  up=56, fo=52, neck=12),
    'coach': dict(head=(-404, 68, 74), sh=-314, shw=56, chest=60, waist=72, hip=-178, hipw=54, legx=23, legw=34,
                  up=62, fo=58, neck=15),
}


class Human:
    def __init__(self, cv, x, gy, s, d, st=None):
        self.cv, self.x, self.gy, self.s, self.d = cv, x, gy, s, d
        self.st = st or {}
        self.b = dict(BUILD[d['h']])
        hy, hrx, hry = self.b['head']
        f = HEAD_K
        self.b['head'] = (hy - hry * (f - 1) * 0.8, hrx * f, hry * f)
        self.drop = -self.b['hip'] * self.st.get('sit_drop', 0.52) if self.st.get('sit') else 0.0
        self.hands = {}

    # ---------------- toạ độ
    def P(self, x, y, body=True):
        if body and self.st.get('sit'):
            y = y + self.drop
        if body and self.st.get('crouch'):      # nhún: hạ thân, gối khuỵu
            y = y + self.st['crouch'] * 34
        a = math.radians(self.st.get('lean', 0))
        if a and body:
            x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        return (self.x + x * self.s, self.gy + y * self.s)

    def Ps(self, pts, body=True):
        return [self.P(x, y, body) for x, y in pts]

    # ---------------- tay
    def arm(self, side):
        b, st = self.b, self.st
        sh = (side * (b['shw'] + 7), b['sh'] + 20)
        key = 'R' if side > 0 else 'L'
        if key in st.get('arm_to', {}):
            hd = st['arm_to'][key]
            dx, dy = hd[0] - sh[0], hd[1] - sh[1]
            dd = max(1.0, min(math.hypot(dx, dy), (b['up'] + b['fo']) * 0.995))
            a = math.atan2(dy, dx)
            cb = (b['up'] ** 2 + dd ** 2 - b['fo'] ** 2) / (2 * b['up'] * dd)
            bb = math.acos(max(-1, min(1, cb)))
            # khuỷu luôn bẻ RA NGOÀI thân (tránh tay lọt vào người)
            cands = [(sh[0] + b['up'] * math.cos(a + k * bb), sh[1] + b['up'] * math.sin(a + k * bb)) for k in (-1, 1)]
            if st.get('elbow', {}).get(key) == 'out':     # khuỷu chĩa ra ngoài/lên (tu nước, gãi đầu)
                el = max(cands, key=lambda e: side * e[0] - 0.3 * e[1])
            elif hd[1] < sh[1] + 10:          # tay giơ lên/ngang: khuỷu THẤP (không gãy, không bẻ ngược)
                el = max(cands, key=lambda e: e[1] + 0.3 * side * e[0])
            else:                           # tay ở dưới vai: khuỷu RA NGOÀI
                el = max(cands, key=lambda e: side * e[0])
            hd = (sh[0] + dd * math.cos(a), sh[1] + dd * math.sin(a))
            return sh, el, hd
        a1, a2 = st.get('arms', ((14, 6), (14, 6)))[0 if side < 0 else 1]
        g1, g2 = math.radians(a1), math.radians(a2)
        el = (sh[0] + side * b['up'] * math.sin(g1), sh[1] + b['up'] * math.cos(g1))
        hd = (el[0] + side * b['fo'] * math.sin(g2), el[1] + b['fo'] * math.cos(g2))
        # tay buông: đẩy ra ngoài mép thân cho khỏi chìm vào bụng (Tùng)
        edge = b['waist'] if d_is_fat(self.d) else b['shw']
        if side * hd[0] < edge + 16 and hd[1] > b['sh'] + 40:
            push = edge + 16 - side * hd[0]
            el = (el[0] + side * push * 0.6, el[1])
            hd = (hd[0] + side * push, hd[1])
        return sh, el, hd

    # ---------------- vẽ
    def draw(self):
        d, b, st, s, cv = self.d, self.b, self.st, self.s, self.cv
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))     # bóng sàn
        ImageDraw.Draw(lay).ellipse([(self.x - 70 * s) * SS, (self.gy - 10 * s) * SS, (self.x + 70 * s) * SS,
                                     (self.gy + 10 * s) * SS], fill=(30, 25, 40, 70))
        cv.alpha_composite(lay)
        hcy, rx, ry = b['head']
        if d['style'] == 'pony':
            self.ponytail(hcy, rx, ry)
        self.legs()
        self.neck(hcy, rx, ry)
        front = []
        for sd in (-1, 1):
            sh, el, hd = self.arm(sd)
            if sd * hd[0] >= b['chest'] * 0.8 and sd * el[0] >= b['chest'] * 0.8:
                self.draw_arm(sd)            # tay ngoài thân: vẽ TRƯỚC thân → thân đè lên, tay mọc từ mép vai
            else:
                front.append(sd)
        self.torso()
        tilt = st.get('tilt', 0)        # nghiêng/ngửa đầu (độ, dương = ngược kim đồng hồ) quanh cổ
        if tilt:
            real, self.cv = self.cv, Image.new('RGBA', self.cv.size, (0, 0, 0, 0))
        self.head(hcy, rx, ry)
        self.hair(hcy, rx, ry)
        self.face(hcy, rx, ry)
        if tilt:
            px, py = self.P(0, b['sh'] - 6)
            lay = self.cv.rotate(tilt, center=(px * SS, py * SS), resample=Image.BICUBIC)
            self.cv = real
            real.alpha_composite(lay)
            cv = real
        for sd in front:
            self.draw_arm(sd)
        self.props()
        if st.get('sweat'):
            for k, (ox, oy) in enumerate(((rx * 0.92, hcy - ry * 0.35), (-rx * 0.95, hcy - ry * 0.05))):
                x, y = self.P(ox, oy)
                pts = [(x, y - 14 * s), (x + 8 * s, y + 2 * s), (x, y + 9 * s), (x - 8 * s, y + 2 * s)]
                blob(cv, [cr(pts, n=5)], '#9ED3E6', lw=2.0, shd=0)

    def legs(self):
        d, b, st, s, cv = self.d, self.b, self.st, self.s, self.cv
        ph = st.get('walk')
        L = []
        for sd in (-1, 1):
            hip = self.P(sd * b['legx'], b['hip'])
            if st.get('sit'):
                knee = self.P(sd * (b['legx'] + 10), b['hip'] + 24)
                ank = (self.x + sd * (b['legx'] + 8) * s, self.gy - 16 * s)
            else:
                sw = 0 if ph is None else 22 * math.sin(ph + (0 if sd < 0 else math.pi))
                lift = 0 if ph is None else max(0, 16 * math.sin(ph + (0 if sd < 0 else math.pi)))
                knee = self.P(sd * (b['legx'] + 18 * st.get('crouch', 0)) + sw * 0.5, b['hip'] * 0.48)
                ank = self.P(sd * (b['legx'] + 2) + sw, -18 - lift, body=False)
                fk = 'R' if sd > 0 else 'L'
                if fk in st.get('feet', {}):        # bàn chân đặt tự do (bước, lao, nhảy) → gối theo IK
                    ank = self.P(*st['feet'][fk], body=False)
                    seg_ = (-18 - b['hip']) * 0.52
                    dx, dy = ank[0] - hip[0], ank[1] - hip[1]
                    dd = max(1.0, min(math.hypot(dx, dy), 2 * seg_ * self.s * 0.999))
                    a = math.atan2(dy, dx)
                    bb = math.acos(max(-1, min(1, dd / (2 * seg_ * self.s))))
                    ank = (hip[0] + dd * math.cos(a), hip[1] + dd * math.sin(a))
                    mid = ((hip[0] + ank[0]) / 2, (hip[1] + ank[1]) / 2)
                    bend = math.sqrt(max(0.0, (seg_ * self.s) ** 2 - (dd / 2) ** 2))
                    wide = abs(ank[0] - hip[0]) > seg_ * self.s * 0.6       # dạng chân (lao đỡ cầu / đứng tấn)
                    if wide:     # gối bẻ ra ngoài theo IK thật
                        cands = [(hip[0] + seg_ * self.s * math.cos(a + k * bb), hip[1] + seg_ * self.s * math.sin(a + k * bb))
                                 for k in (-1, 1)]
                        knee = max(cands, key=lambda e: sd * e[0])
                    else:        # nhìn chính diện: gối co VỀ PHÍA TRƯỚC → chỉ thấy chân ngắn lại, gối lệch nhẹ
                        kd = st.get('kdir', 0)
                        knee = (mid[0] + 0.22 * bend * (kd if kd else sd * 0.4), mid[1] - 0.12 * bend)
            L.append((sd, hip, knee, ank))
        lw_ = b['legw'] * s
        long_pants = d['h'] == 'coach'
        # da chân (đùi → cổ chân)
        if not long_pants:
            skin = []
            for sd, hip, knee, ank in L:
                skin += tube([hip, knee, ank], lw_ * 0.86, lw_ * 0.74)
            blob(cv, skin, d['skin'], shd=6)
        # quần: đùi (quần đùi) hoặc dài
        pol = []
        inner = []
        for sd, hip, knee, ank in L:
            if long_pants:
                pol += tube([hip, knee, ank], lw_ * 1.1, lw_ * 0.95)
                if d.get('stripe'):
                    inner.append(('line', cr([(p[0] + sd * lw_ * 0.42, p[1]) for p in (hip, knee, ank)], closed=False, n=6),
                                  hx(d['stripe']), 3.4 * s))
            else:
                mid = (hip[0] + (knee[0] - hip[0]) * 0.75, hip[1] + (knee[1] - hip[1]) * 0.75)
                pol += tube([hip, mid], lw_ * 1.32, lw_ * 1.38, n=4)
                if d.get('stripe'):
                    inner.append(('line', [(hip[0] + sd * lw_ * 0.55, hip[1]), (mid[0] + sd * lw_ * 0.6, mid[1])],
                                  hx(d['stripe']), 3.6 * s))
                inner.append(('line', [(mid[0] - lw_ * 0.66, mid[1] - 5 * s), (mid[0] + lw_ * 0.66, mid[1] - 5 * s)],
                              dark(d['pants'], 0.8), 2.4 * s))
        top = b['hip'] - (34 if not st.get('sit') else 20)
        tw = min(b['hipw'], b['waist'] - 4)
        pol.append(self.Ps([(-tw, top), (tw, top), (b['hipw'] + 2, b['hip'] + 10), (-b['hipw'] - 2, b['hip'] + 10)]))
        if d['h'] == 'tall':     # cạp quần viền trắng (tách áo xanh / quần đen)
            inner.append(('line', self.Ps([(-b['hipw'], b['hip'] - 6), (b['hipw'], b['hip'] - 6)]), hx('#F4F4F4'), 4 * s))
        blob(cv, pol, d['pants'], shd=8, inner=inner)
        # tất + giày
        for sd, hip, knee, ank in L:
            ax, ay = ank
            if not long_pants:
                blob(cv, [ellipse_pts(ax, ay - 4 * s, lw_ * 0.44, 9 * s, n=20)], d['sock'], shd=0, lw=2.2)
            self.shoe(ax + sd * 6 * s, ay + 12 * s, sd)

    def shoe(self, x, y, sd):
        d, s, cv = self.d, self.s, self.cv
        up = [(x - sd * 22 * s, y + 6 * s), (x - sd * 20 * s, y - 12 * s), (x - sd * 2 * s, y - 16 * s), (x + sd * 18 * s, y - 8 * s),
              (x + sd * 30 * s, y + 2 * s), (x + sd * 28 * s, y + 9 * s), (x - sd * 18 * s, y + 10 * s)]
        P = cr(up, n=5)
        inner = [('poly', [(x - sd * 26 * s, y + 3 * s), (x + sd * 34 * s, y + 3 * s), (x + sd * 34 * s, y + 14 * s),
                           (x - sd * 26 * s, y + 14 * s)], hx(d['sole']))]
        for k in range(3):
            lx = x - sd * (2 - k * 7) * s
            inner.append(('line', [(lx - 5 * s, y - 12 * s + k * 3 * s), (lx + 5 * s, y - 9 * s + k * 3 * s)], dark(d['shoe'], 0.55), 2.2 * s))
        blob(cv, [P], d['shoe'], shd=5, lw=2.6, inner=inner)

    def torso(self):
        d, b, st, s, cv = self.d, self.b, self.st, self.s, self.cv
        h = d['h']
        if h == 'fat':
            right = [(0, b['sh'] - 8), (b['shw'] * 0.7, b['sh'] - 4), (b['shw'], b['sh'] + 14), (b['chest'] + 6, b['sh'] + 60),
                     (b['waist'], b['hip'] - 50), (b['waist'] - 10, b['hip'] - 4), (0, b['hip'] + 6)]
        elif h == 'girl':
            right = [(0, b['sh'] - 6), (b['shw'] * 0.7, b['sh'] - 3), (b['shw'], b['sh'] + 12), (b['chest'], b['sh'] + 50),
                     (b['waist'], b['hip'] - 40), (b['hipw'] + 2, b['hip'] - 2), (0, b['hip'] + 4)]
        else:
            right = [(0, b['sh'] - 8), (b['shw'] * 0.7, b['sh'] - 4), (b['shw'], b['sh'] + 14), (b['chest'], b['sh'] + 64),
                     (b['waist'], b['hip'] - 40), (b['waist'] + 2, b['hip'] - 2), (0, b['hip'] + 6)]
        body = cr(self.Ps(right + [(-x, y) for x, y in right[1:-1]][::-1]), n=8)
        inner = []
        ny = b['sh'] - 6
        nw = b['neck'] + 8
        # cổ áo: chữ U (áo thun) / chữ V (Khang) / cổ bẻ (thầy)
        if d['style'] == 'quiff':
            inner.append(('poly', self.Ps([(-nw, ny - 4), (nw, ny - 4), (0, ny + 30)]), hx(d['skin'])))
            inner.append(('line', self.Ps([(-nw - 4, ny - 4), (0, ny + 34), (nw + 4, ny - 4)]), hx(d['trim']), 5 * s))
            inner.append(('poly', self.Ps([(b['chest'] - 4, b['sh'] + 40), (b['waist'] + 4, b['sh'] + 40), (b['waist'] + 2, b['hip'] - 4),
                                           (b['waist'] - 12, b['hip'] - 4)]), hx(d['trim'])))
            inner.append(('poly', self.Ps([(-b['chest'] + 4, b['sh'] + 40), (-b['waist'] - 4, b['sh'] + 40), (-b['waist'] - 2, b['hip'] - 4),
                                           (-b['waist'] + 12, b['hip'] - 4)]), hx(d['trim'])))
        elif d['style'] == 'cap':
            inner.append(('poly', self.Ps([(-nw, ny - 4), (nw, ny - 4), (0, ny + 22)]), hx(d['skin'])))
            for sd in (-1, 1):
                inner.append(('poly', self.Ps([(sd * 2, ny + 22), (sd * (nw + 4), ny - 8), (sd * (nw + 26), ny + 4), (sd * 10, ny + 30)]),
                              hx(d['trim'])))
            for k in range(2):
                inner.append(('dot', self.P(0, ny + 34 + k * 16), 3 * s, hx('#F4F4F4')))
        else:
            E = [(nw * math.cos(t), ny - 4 + 18 * math.sin(t)) for t in np.linspace(0, math.pi, 12)]
            inner.append(('poly', self.Ps([(-nw, ny - 6), (nw, ny - 6)] + E), hx(d['skin'])))
            inner.append(('line', self.Ps(E[::-1]), hx(d['trim']), 4.5 * s))
        # gấu áo
        inner.append(('line', self.Ps([(-b['waist'] - 6, b['hip'] - 12), (b['waist'] + 6, b['hip'] - 12)]), dark(d['shirt'], 0.82), 2.6 * s))
        # hình in trên áo
        px, py = self.P(0, b['sh'] + (70 if d['h'] != 'fat' else 74))
        if d['print'] == 'so':
            inner.append(('text', (px, py), '7', 46 * s, hx('#F4F4F4')))
        elif d['print'] == 'banh':
            inner.append(('dot', (px, py), 20 * s, hx('#F4F1EA')))
            inner.append(('dot', (px, py + 3 * s), 13 * s, hx('#E0A02E')))
            inner.append(('line', [(px - 8 * s, py - 6 * s), (px, py - 12 * s), (px + 8 * s, py - 6 * s)], hx('#F4F1EA'), 3 * s))
        elif d['print'] == 'sao':
            pts = []
            for k in range(10):
                rr = (18 if k % 2 == 0 else 8) * s
                a = k * math.pi / 5 - math.pi / 2
                pts.append((px + rr * math.cos(a), py + rr * math.sin(a)))
            inner.append(('poly', pts, hx('#FFFFFF')))
        txt = [it for it in inner if it[0] == 'text']
        inner = [it for it in inner if it[0] != 'text']
        blob(cv, [body], d['shirt'], shd=12, inner=inner)
        for _, (x, y), t, sz, col in txt:
            f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), max(8, int(sz * SS)))
            ImageDraw.Draw(cv).text((x * SS, y * SS), t, font=f, fill=col + (255,), anchor='mm',
                                    stroke_width=int(2 * self.s * SS), stroke_fill=INK + (255,))
        if d['print'] == 'coi':     # dây còi (+ còi nếu không cầm)
            x0, y0 = self.P(-nw + 2, ny + 2)
            x1, y1 = self.P(nw - 2, ny + 2)
            wx, wy = self.P(-6, ny + 84)
            if 'whistle' in self.st.get('hold', {}).values():
                hk = [k for k, v in self.st['hold'].items() if v == 'whistle'][0]
                hx_, hy_ = self.P(*self.arm(1 if hk == 'R' else -1)[2])
                M.line(cv, cr([(x1, y1), ((x1 + hx_) / 2, max(y1, hy_) + 26 * s), (hx_, hy_)], closed=False, n=6), 2.4 * s,
                       hx('#C8382E'))
            else:
                M.line(cv, [(x0, y0), (wx - 4 * s, wy - 8 * s)], 2.4 * s, hx('#C8382E'))
                M.line(cv, [(x1, y1), (wx + 4 * s, wy - 8 * s)], 2.4 * s, hx('#C8382E'))
            if 'whistle' not in self.st.get('hold', {}).values():
                blob(cv, [ellipse_pts(wx, wy, 12 * s, 8 * s, n=20), [(wx + 6 * s, wy - 4 * s), (wx + 20 * s, wy - 6 * s),
                                                                     (wx + 20 * s, wy + 2 * s), (wx + 6 * s, wy + 4 * s)]],
                     '#C9CDD2', lw=2.0, shd=3)

    def head(self, hcy, rx, ry):
        d, s, cv = self.d, self.s, self.cv
        b = self.b
        if d['h'] == 'fat':      # mặt bầu, má phúng
            head = cr(self.Ps([(0, hcy - ry), (rx * 0.82, hcy - ry * 0.8), (rx * 1.02, hcy - ry * 0.05), (rx * 0.95, hcy + ry * 0.55),
                               (rx * 0.55, hcy + ry * 0.95), (0, hcy + ry * 1.02), (-rx * 0.55, hcy + ry * 0.95), (-rx * 0.95, hcy + ry * 0.55),
                               (-rx * 1.02, hcy - ry * 0.05), (-rx * 0.82, hcy - ry * 0.8)]), n=8)
        elif d['h'] == 'tall':   # cằm thon hơn
            head = cr(self.Ps([(0, hcy - ry), (rx * 0.85, hcy - ry * 0.78), (rx, hcy - ry * 0.05), (rx * 0.82, hcy + ry * 0.58),
                               (rx * 0.32, hcy + ry * 0.98), (0, hcy + ry * 1.08), (-rx * 0.32, hcy + ry * 0.98), (-rx * 0.82, hcy + ry * 0.58),
                               (-rx, hcy - ry * 0.05), (-rx * 0.85, hcy - ry * 0.78)]), n=8)
        else:
            head = ellipse_pts(*self.P(0, hcy), rx * s, ry * s, n=64)
        ears = [ellipse_pts(*self.P(sd * rx * 0.97, hcy + ry * 0.12), 11 * s, 16 * s, n=24) for sd in (-1, 1)]
        inner = []
        for sd in (-1, 1):
            ex, ey = self.P(sd * rx * 0.99, hcy + ry * 0.12)
            inner.append(('line', cr([(ex - sd * 2 * s, ey - 8 * s), (ex + sd * 4 * s, ey - 2 * s), (ex - sd * 1 * s, ey + 7 * s)],
                                     closed=False, n=5), dark(d['skin'], 0.78), 2.4 * s))
        # bóng cổ dưới cằm
        blob(cv, [head] + ears, d['skin'], shd=9, inner=inner)

    def neck(self, hcy, rx, ry):
        d, b = self.d, self.b
        nk = self.Ps([(-b['neck'], b['sh'] + 24), (b['neck'], b['sh'] + 24), (b['neck'], hcy + ry * 0.7), (-b['neck'], hcy + ry * 0.7)])
        sh = [(b['neck'] * math.cos(t), hcy + ry * 0.92 + 12 * math.sin(t)) for t in np.linspace(0, math.pi, 10)]
        blob(self.cv, [nk], d['skin'], shd=0, inner=[('poly', self.Ps([(-b['neck'], hcy + ry * 0.8), (b['neck'], hcy + ry * 0.8)] + sh),
                                                       dark(d['skin'], 0.82))])

    def ponytail(self, hcy, rx, ry):
        d, s = self.d, self.s
        sw = 8 * math.sin(self.st.get('t', 0) * 6) if self.st.get('t') else 0
        tail = tube(self.Ps([(rx * 0.55, hcy - ry * 0.85), (rx * 1.25, hcy - ry * 0.7), (rx * 1.45 + sw, hcy - ry * 0.05),
                             (rx * 1.2 + sw * 1.4, hcy + ry * 0.75)]), 40 * s, 12 * s)
        blob(self.cv, tail, d['hair'], shd=8,
             inner=[('line', cr(self.Ps([(rx * 1.0, hcy - ry * 0.7), (rx * 1.3, hcy - ry * 0.1), (rx * 1.18 + sw, hcy + ry * 0.5)]),
                                closed=False, n=6), dark(d['hair'], 0.6), 3 * s)])

    def hair(self, hcy, rx, ry):
        d, s, cv = self.d, self.s, self.cv
        st = d['style']
        hl = tuple(min(255, int(c * 1.9) + 20) for c in hx(d['hair']))
        if st == 'quiff':       # tóc vuốt dựng cao, mái hất lệch phải
            pts = [(-rx * 1.04, hcy + ry * 0.1), (-rx * 1.06, hcy - ry * 0.55), (-rx * 0.7, hcy - ry * 1.05), (-rx * 0.2, hcy - ry * 1.3),
                   (rx * 0.25, hcy - ry * 1.62), (rx * 0.62, hcy - ry * 1.42), (rx * 0.95, hcy - ry * 1.5), (rx * 1.02, hcy - ry * 1.06),
                   (rx * 1.08, hcy - ry * 0.4), (rx * 1.0, hcy + ry * 0.06), (rx * 0.86, hcy - ry * 0.42), (rx * 0.3, hcy - ry * 0.6),
                   (-rx * 0.3, hcy - ry * 0.5), (-rx * 0.8, hcy - ry * 0.3), (-rx * 0.9, hcy + ry * 0.12)]
            inner = [('line', cr(self.Ps([(-rx * 0.5, hcy - ry * 0.9), (rx * 0.1, hcy - ry * 1.3), (rx * 0.55, hcy - ry * 1.3)]),
                                 closed=False, n=6), hl, 4 * s),
                     ('line', cr(self.Ps([(-rx * 0.2, hcy - ry * 0.7), (rx * 0.4, hcy - ry * 1.05), (rx * 0.85, hcy - ry * 1.2)]),
                                 closed=False, n=6), hl, 3 * s)]
            blob(cv, [cr(self.Ps(pts), n=6)], d['hair'], shd=8, inner=inner)
            if self.st.get('gear'):    # băng đô thể thao
                M.line(cv, [self.P(-rx * 1.0, hcy - ry * 0.32), self.P(0, hcy - ry * 0.5), self.P(rx * 1.0, hcy - ry * 0.32)],
                       12 * s, hx(d['band']))
        elif st == 'buzz':      # đầu đinh tròn + chỏm xoáy
            pts = [(-rx * 1.03, hcy + ry * 0.05), (-rx * 0.92, hcy - ry * 0.7), (-rx * 0.4, hcy - ry * 1.06), (rx * 0.2, hcy - ry * 1.1),
                   (rx * 0.32, hcy - ry * 1.24), (rx * 0.46, hcy - ry * 1.08), (rx * 0.92, hcy - ry * 0.7), (rx * 1.03, hcy + ry * 0.05),
                   (rx * 0.9, hcy - ry * 0.38), (rx * 0.4, hcy - ry * 0.52), (-rx * 0.1, hcy - ry * 0.46), (-rx * 0.6, hcy - ry * 0.52),
                   (-rx * 0.9, hcy - ry * 0.38)]
            inner = [('dot', self.P(x_, y_), 1.8 * s, hl) for x_, y_ in
                     ((-rx * 0.5, hcy - ry * 0.8), (-rx * 0.1, hcy - ry * 0.9), (rx * 0.35, hcy - ry * 0.85), (rx * 0.65, hcy - ry * 0.65),
                      (-rx * 0.75, hcy - ry * 0.5), (rx * 0.05, hcy - ry * 0.7))]
            blob(cv, [cr(self.Ps(pts), n=6)], d['hair'], shd=6, inner=inner)
        elif st == 'pony':      # tóc mái + buộc cao, băng đô vàng
            pts = [(-rx * 1.06, hcy + ry * 0.55), (-rx * 1.08, hcy - ry * 0.4), (-rx * 0.75, hcy - ry * 0.95), (0, hcy - ry * 1.12),
                   (rx * 0.75, hcy - ry * 0.95), (rx * 1.08, hcy - ry * 0.4), (rx * 1.06, hcy + ry * 0.45), (rx * 0.9, hcy + ry * 0.0),
                   (rx * 0.82, hcy - ry * 0.28), (rx * 0.5, hcy - ry * 0.2), (rx * 0.3, hcy - ry * 0.38), (rx * 0.05, hcy - ry * 0.18),
                   (-rx * 0.2, hcy - ry * 0.4), (-rx * 0.5, hcy - ry * 0.22), (-rx * 0.82, hcy - ry * 0.3), (-rx * 0.9, hcy + ry * 0.05)]
            inner = [('line', cr(self.Ps([(-rx * 0.6, hcy - ry * 0.85), (0, hcy - ry * 0.98), (rx * 0.5, hcy - ry * 0.9)]),
                                 closed=False, n=6), hl, 4 * s)]
            blob(cv, [cr(self.Ps(pts), n=6)], d['hair'], shd=8, inner=inner)
            M.line(cv, [self.P(-rx * 0.98, hcy - ry * 0.58), self.P(0, hcy - ry * 0.84), self.P(rx * 0.98, hcy - ry * 0.58)],
                   9 * s, hx(d['band']))
            sx, sy = self.P(rx * 0.62, hcy - ry * 0.9)    # dây buộc tóc
            blob(cv, [ellipse_pts(sx, sy, 13 * s, 11 * s, n=20)], d['band'], lw=2.2, shd=3)
        elif st == 'cap':       # tóc mai bạc + nón lưỡi trai
            for sd in (-1, 1):
                blob(cv, [cr(self.Ps([(sd * rx * 0.8, hcy - ry * 0.35), (sd * rx * 1.04, hcy - ry * 0.2), (sd * rx * 1.02, hcy + ry * 0.25),
                                      (sd * rx * 0.86, hcy + ry * 0.12)]), n=4)], d['hair'], shd=4)
            cap = [(-rx * 1.06, hcy - ry * 0.32), (-rx * 0.95, hcy - ry * 0.9), (0, hcy - ry * 1.16), (rx * 0.95, hcy - ry * 0.9),
                   (rx * 1.06, hcy - ry * 0.32)]
            brim = [(-rx * 0.9, hcy - ry * 0.42), (rx * 0.2, hcy - ry * 0.48), (rx * 1.25, hcy - ry * 0.34), (rx * 1.28, hcy - ry * 0.16),
                    (rx * 0.2, hcy - ry * 0.28), (-rx * 0.9, hcy - ry * 0.26)]
            inner = [('line', cr(self.Ps([(0, hcy - ry * 1.12), (0, hcy - ry * 0.45)]), closed=False, n=3), dark(d['capc'], 0.7), 2.4 * s),
                     ('dot', self.P(-rx * 0.45, hcy - ry * 0.72), 11 * s, hx('#F4F4F4')),
                     ('dot', self.P(-rx * 0.45, hcy - ry * 0.72), 6 * s, hx(d['capc']))]
            blob(cv, [cr(self.Ps(cap), n=6), cr(self.Ps(brim), n=4)], d['capc'], shd=8, inner=inner)

    def face(self, hcy, rx, ry):
        st, s, cv, d = self.st, self.s, self.cv, self.d
        gx, gy = st.get('gaze', (0, 0))
        fx = gx * rx * 0.10                            # mặt xoay nhẹ theo hướng nhìn
        e = rx / 70.0
        FS = dict(quiff=dict(k=1.02, hw=0.8, brow=-12, bw=9.5), pony=dict(k=1.15, hw=1.0, brow=0, bw=6),
                  buzz=dict(k=0.7, hw=1.0, brow=-4, bw=7, ey=0.2, sep=0.3), cap=dict(k=0.8, hw=0.85, brow=20, bw=12))[d['style']]
        eyes = st.get('eyes', 'open')
        ey = hcy + ry * FS.get('ey', 0.10)
        if 'lid' not in st and eyes == 'open' and d.get('lid0'):
            st = dict(st, lid=d['lid0'])     # Khang: mí cụp nửa -> vẻ kiêu
        if st.get('blush', d['h'] in ('girl', 'fat')):
            for sd in (-1, 1):
                lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
                cx, cy = self.P(fx + sd * rx * 0.58, ey + ry * 0.32)
                ImageDraw.Draw(lay).ellipse([(cx - 13 * s * e) * SS, (cy - 7 * s * e) * SS, (cx + 13 * s * e) * SS, (cy + 7 * s * e) * SS],
                                            fill=(240, 120, 130, 120))
                cv.alpha_composite(lay)
        lid = st.get('lid', 0)
        if eyes == 'sleepy':
            eyes, lid = 'open', 0.55
        for i, sd in enumerate((-1, 1)):
            cx, cy = self.P(fx + sd * rx * FS.get('sep', 0.37), ey)
            k = (1.25 if eyes == 'wide' else 1.0) * e * FS['k']
            if eyes == 'happy':
                M.line(cv, cr([(cx - 11 * k * s, cy + 4 * s), (cx, cy - 8 * s), (cx + 11 * k * s, cy + 4 * s)], closed=False, n=6), 4 * s)
            elif eyes == 'closed':
                M.line(cv, cr([(cx - 11 * k * s, cy - 2 * s), (cx, cy + 5 * s), (cx + 11 * k * s, cy - 2 * s)], closed=False, n=6), 4 * s)
            elif eyes == 'line':
                M.line(cv, [(cx - 11 * k * s, cy), (cx + 11 * k * s, cy)], 4 * s)
            else:
                ew, eh = 12 * k * s, 15 * k * s * FS['hw']
                M.ell(cv, (cx, cy), ew, eh, fill=(255, 255, 255), ow=2.6 * s)
                ir = (0.62 if eyes != 'wide' else 0.42)
                px, py = cx + gx * ew * 0.38, cy + gy * eh * 0.3 + 1 * s
                M.ell(cv, (px, py), ew * ir * 1.05, eh * ir * 1.05, fill=hx(d['iris']))
                M.ell(cv, (px, py), ew * ir * 0.6, eh * ir * 0.6, fill=hx('#120E0E'))
                M.ell(cv, (px - ew * 0.22, py - eh * 0.26), 3.2 * s * e, 3.2 * s * e, fill=(255, 255, 255))
                if eyes == 'angry' or lid:
                    lv = lid if lid else 0.35
                    top = cy - eh + 2 * eh * lv
                    if eyes == 'angry':       # mí xéo vào trong
                        P = [(cx - ew - 2 * s, cy - eh - 4 * s), (cx + ew + 2 * s, cy - eh - 4 * s)]
                        inner_y, outer_y = (top + 5 * s, top - 4 * s)
                        a, b_ = (outer_y, inner_y) if sd < 0 else (inner_y, outer_y)
                        P += [(cx + ew + 2 * s, b_), (cx - ew - 2 * s, a)]
                    else:
                        P = [(cx - ew - 2 * s, cy - eh - 4 * s), (cx + ew + 2 * s, cy - eh - 4 * s), (cx + ew + 2 * s, top),
                             (cx - ew - 2 * s, top)]
                    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
                    m = Image.new('L', cv.size, 0)
                    ImageDraw.Draw(m).ellipse([(cx - ew - 1.4 * s) * SS, (cy - eh - 1.4 * s) * SS, (cx + ew + 1.4 * s) * SS,
                                               (cy + eh + 1.4 * s) * SS], fill=255)
                    ImageDraw.Draw(lay).polygon([(x * SS, y * SS) for x, y in P], fill=hx(d['skin']) + (255,))
                    arr = np.asarray(lay).copy()
                    arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
                    cv.alpha_composite(Image.fromarray(arr, 'RGBA'))
                    M.line(cv, [P[3], P[2]], 3.6 * s)
                if d['style'] == 'pony':                  # mi cong
                    ox = cx + sd * ew * 0.9
                    M.line(cv, [(ox, cy - eh * 0.55), (ox + sd * 7 * s, cy - eh * 0.85)], 3 * s)
            # lông mày
            br = st.get('brow', FS['brow'])
            if isinstance(br, (tuple, list)):
                br = br[i]
            if eyes == 'angry':
                br = 24
            if eyes == 'wide':
                br = -10
            a = math.radians(br)
            bx, by = self.P(fx + sd * rx * FS.get('sep', 0.37), ey - ry * 0.30 - (5 if eyes == 'wide' else 0))
            # đầu trong (gần mũi) hạ xuống khi br > 0
            ix, iy = bx - sd * 13 * s * e, by + 13 * s * e * math.sin(a)
            ox, oy = bx + sd * 13 * s * e, by - 13 * s * e * math.sin(a)
            col = hx(d['hair']) if d['style'] != 'cap' else hx('#6E6A64')
            stroke(cv, [(ix, iy), (bx, by - 2 * s), (ox, oy)], FS['bw'] * s * e, 4.5 * s * e, col)
        # mũi
        nx, ny = self.P(fx * 1.3, ey + ry * 0.28)
        M.line(cv, cr([(nx - 6 * s, ny + 1 * s), (nx, ny + 5 * s), (nx + 6 * s, ny + 1 * s)], closed=False, n=5), 3 * s,
               dark(d['skin'], 0.55))
        if d['style'] == 'cap':                            # nếp nhăn trán
            for k in (0, 1):
                wx, wy = self.P(fx, hcy - ry * (0.32 + 0.1 * k))
                M.line(cv, cr([(wx - 18 * s, wy + 2 * s), (wx, wy - 1 * s), (wx + 18 * s, wy + 2 * s)], closed=False, n=5), 2.2 * s,
                       dark(d['skin'], 0.7))
        if d['style'] == 'cap':                            # ria mép
            mx, my = self.P(fx * 1.3, ey + ry * 0.44)
            blob(cv, [cr([(mx - 26 * s, my + 4 * s), (mx - 14 * s, my - 6 * s), (mx, my - 3 * s), (mx + 14 * s, my - 6 * s),
                          (mx + 26 * s, my + 4 * s), (mx, my + 4 * s)], n=5)], '#8E8A82', lw=2.2, shd=3)
        if d['style'] == 'buzz':                           # cằm 2 ngấn
            cx, cy = self.P(fx, hcy + ry * 0.86)
            M.line(cv, cr([(cx - 22 * s, cy - 3 * s), (cx, cy + 4 * s), (cx + 22 * s, cy - 3 * s)], closed=False, n=5), 2.4 * s,
                   dark(d['skin'], 0.72))
        if d['style'] == 'cap' and eyes not in ('happy', 'closed', 'line'):   # bọng mắt
            for sd in (-1, 1):
                cx, cy = self.P(fx + sd * rx * 0.37, ey + 16 * s)
                M.line(cv, cr([(cx - 9 * s, cy), (cx, cy + 3 * s), (cx + 9 * s, cy)], closed=False, n=5), 2 * s, dark(d['skin'], 0.7))
        self.mouth(*self.P(fx * 1.3, ey + ry * 0.55), e)

    def mouth(self, mx, my, e):
        st, s, cv = self.st, self.s, self.cv
        m = st.get('mouth', 'smirk' if self.d['style'] == 'quiff' else 'smile')
        mo = st.get('mo', 0.0)
        if m == 'talk':
            m = st.get('rest', 'flat') if mo < 0.12 else 'open'
            if m == 'talk':
                m = 'flat'
        w = 13 * s * e
        if m == 'smile':
            M.line(cv, cr([(mx - w, my - 4 * s), (mx - w * 0.4, my + 4 * s), (mx + w * 0.4, my + 4 * s), (mx + w, my - 4 * s)],
                          closed=False, n=6), 3.4 * s)
        elif m in ('grin', 'smirk'):
            M.line(cv, cr([(mx - w * 1.1, my - 1 * s), (mx - w * 0.2, my + 4 * s), (mx + w * 0.8, my - 2 * s), (mx + w * 1.25, my - 9 * s)],
                          closed=False, n=6), 3.4 * s)
        elif m == 'flat':
            M.line(cv, [(mx - w * 0.75, my), (mx + w * 0.75, my)], 3.4 * s)
        elif m == 'frown':
            M.line(cv, cr([(mx - w, my + 5 * s), (mx, my - 3 * s), (mx + w, my + 5 * s)], closed=False, n=6), 3.4 * s)
        elif m == 'o':
            M.ell(cv, (mx, my + 2 * s), 7 * s * e, 9 * s * e, fill=hx('#6E2226'), ow=2.6 * s)
        else:                                              # open (talk) / D (cười lớn)
            k = mo if st.get('mouth') == 'talk' else 1.0
            h = (7 + 15 * k) * s * e
            ww = (w * 1.25) if m == 'D' else w * (0.8 + 0.2 * k)
            top = my - 4 * s
            poly = [(mx - ww, top), (mx + ww, top)] + [(mx + ww * math.cos(t), top + h * math.sin(t)) for t in np.linspace(0, math.pi, 16)]
            inner = []
            if m == 'D' or h > 13 * s:
                inner.append(('poly', [(mx - ww, top), (mx + ww, top), (mx + ww * 0.9, top + 5 * s), (mx - ww * 0.9, top + 5 * s)],
                              hx('#FFFFFF')))
                inner.append(('dot', (mx, top + h * 0.85), ww * 0.5, hx('#E8707C')))
            M.blob(cv, [poly], C('#6E2226'), lw=2.6, shd=0, hld=0, inner=inner)

    def draw_arm(self, sd):
        d, b, s, cv = self.d, self.b, self.s, self.cv
        sh, el, hd = self.arm(sd)
        key = 'R' if sd > 0 else 'L'
        H = self.P(*hd)
        self.hands[key] = H
        # cẳng tay + bàn tay (da)
        mid = (sh[0] + (el[0] - sh[0]) * 0.45, sh[1] + (el[1] - sh[1]) * 0.45)
        arm_w = (31 if d['h'] == 'fat' else 19) * s
        polys = tube(self.Ps([mid, el, hd]), arm_w, arm_w * 0.86)
        # bàn tay: nắm tròn + ngón cái (hướng vào trong)
        ang = math.atan2(hd[1] - el[1], hd[0] - el[0])
        hr = (16.5 if d['h'] == 'fat' else 13.5) * s
        polys.append(ellipse_pts(*H, hr, hr, n=24))
        tx, ty = H[0] + (-sd) * 9 * s * abs(math.sin(ang)) + math.cos(ang) * 4 * s, H[1] - 10 * s * abs(math.cos(ang)) + 2 * s
        polys.append(ellipse_pts(tx, ty, 6.5 * s, 7 * s, n=16))
        inner = []
        if d['ten'] == 'Khang' and key == 'R':            # băng cổ tay đỏ
            wx, wy = self.P(el[0] + (hd[0] - el[0]) * 0.78, el[1] + (hd[1] - el[1]) * 0.78)
            inner.append(('taper', [(wx - math.cos(ang) * 6 * s, wy - math.sin(ang) * 6 * s), (wx + math.cos(ang) * 6 * s, wy + math.sin(ang) * 6 * s)],
                          arm_w * 1.3, arm_w * 1.3, hx(d['band'])))
        if d['h'] == 'coach':                              # áo khoác dài tay? không – thầy mặc polo ngắn tay
            pass
        blob(cv, polys, d['skin'], shd=6, lw=3.2, inner=inner)
        # tay áo (đè lên vai, nối liền thân)
        cut = (sh[0] + (el[0] - sh[0]) * 0.58, sh[1] + (el[1] - sh[1]) * 0.58)
        sl = tube(self.Ps([(sh[0], sh[1] - 4), sh, cut]), (40 if d['h'] == 'fat' else 27) * s, (38 if d['h'] == 'fat' else 26) * s, n=5)
        cx, cy = self.P(*cut)
        a2 = math.atan2(el[1] - sh[1], el[0] - sh[0]) + math.pi / 2
        hw = (19 if d['h'] == 'fat' else 13) * s
        inner = [('line', [(cx - math.cos(a2) * hw, cy - math.sin(a2) * hw), (cx + math.cos(a2) * hw, cy + math.sin(a2) * hw)],
                  hx(d['trim']), 4 * s)]
        blob(cv, sl, d['shirt'], shd=7, lw=3.2, inner=inner)

    def props(self):
        for k, what in self.st.get('hold', {}).items():
            if k in self.hands:
                prop(self.cv, what, self.hands[k], self.s * self.st.get('prop_k', 1.0), self.st.get('prop_ang', {}).get(k, -30),
                     skin=self.d['skin'])


def d_is_fat(d):
    return d['h'] == 'fat'


def fist(cv, x, y, s, skin):
    blob(cv, [ellipse_pts(x, y, 13.5 * s, 13.5 * s, n=24)], skin, lw=2.6, shd=4,
         inner=[('line', [(x - 8 * s, y - 4 * s), (x + 8 * s, y - 4 * s)], dark(skin, 0.72), 2 * s),
                ('line', [(x - 8 * s, y + 3 * s), (x + 8 * s, y + 3 * s)], dark(skin, 0.72), 2 * s)])


def prop(cv, what, at, s, ang=-30, skin=SKIN, lens=None, hand=True):
    """Đạo cụ cầm tay; at = tâm bàn tay; ang = góc cán (độ, 0 = thẳng lên). Bàn tay nắm vẽ đè lên cán."""
    x, y = at
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    vx, vy = math.cos(a), math.sin(a)
    if what == 'racket':
        L = 74 * s
        M.line(cv, [(x - ux * 16 * s, y - uy * 16 * s), (x + ux * L, y + uy * L)], 9 * s, INK)
        M.line(cv, [(x - ux * 14 * s, y - uy * 14 * s), (x + ux * L, y + uy * L)], 5 * s, hx('#3A3A44'))
        M.line(cv, [(x - ux * 16 * s, y - uy * 16 * s), (x + ux * 10 * s, y + uy * 10 * s)], 11 * s, hx('#F4F4F4'))   # cán quấn
        cx, cy = x + ux * (L + 46 * s), y + uy * (L + 46 * s)
        e = [(cx + 32 * s * math.cos(t) * vx - 48 * s * math.sin(t) * ux, cy + 32 * s * math.cos(t) * vy - 48 * s * math.sin(t) * uy)
             for t in np.linspace(0, 2 * math.pi, 56)]
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        dr.polygon([(px * SS, py * SS) for px, py in e], fill=(250, 250, 250, 70))
        for k in np.linspace(-1, 1, 9):
            for (ax, ay), (bx_, by_), L1, L2 in (((ux, uy), (vx, vy), 34, 52), ((vx, vy), (ux, uy), 52, 34)):
                ox, oy = cx + bx_ * k * L1 * s, cy + by_ * k * L1 * s
                dr.line([((ox - ax * L2 * s) * SS, (oy - ay * L2 * s) * SS), ((ox + ax * L2 * s) * SS, (oy + ay * L2 * s) * SS)],
                        fill=(90, 90, 100, 255), width=max(1, int(1.4 * s * SS)))
        m = Image.new('L', cv.size, 0)
        ImageDraw.Draw(m).polygon([(px * SS, py * SS) for px, py in e], fill=255)
        arr = np.asarray(lay).copy()
        arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
        cv.alpha_composite(Image.fromarray(arr, 'RGBA'))
        M.line(cv, e + [e[0]], 9.5 * s, INK)
        M.line(cv, e + [e[0]], 6 * s, hx('#D83A2E'))
        if hand:
            fist(cv, x, y, s, skin)
    elif what == 'phone':
        w, h = 24 * s, 44 * s
        pts = [(x - w, y - h - 6 * s), (x + w, y - h - 6 * s), (x + w, y + 10 * s), (x - w, y + 10 * s)]
        blob(cv, [pts], '#2A2A30', lw=2.6, shd=0,
             inner=[('poly', [(x - w + 5 * s, y - h), (x + w - 5 * s, y - h), (x + w - 5 * s, y + 4 * s), (x - w + 5 * s, y + 4 * s)],
                     hx('#8FD0E8')),
                    ('dot', (x, y - h - 1 * s), 2.4 * s, hx('#555560'))])
        fist(cv, x, y + 4 * s, s, skin)
    elif what in ('bottle', 'mic'):
        if ang == -30:
            ang = 0
            a = 0.0
            ux, uy, vx, vy = 0.0, -1.0, 1.0, 0.0

        def T(lx, ly):     # toạ độ cục bộ của chai (ly âm = phía nắp) → khung
            return (x + vx * lx * s - ux * ly * s, y + vy * lx * s - uy * ly * s)
        blob(cv, [cr([T(-13, -60), T(13, -60), T(15, 24), T(-15, 24)], n=3)], '#A8DCEC', lw=2.8, shd=4,
             inner=[('poly', [T(-16, -34), T(16, -34), T(16, -14), T(-16, -14)], hx('#2F6FB5')),
                    ('line', [T(-7, -52), T(-7, -40)], hx('#FFFFFF'), 3 * s)])
        blob(cv, [[T(-8, -74), T(8, -74), T(8, -58), T(-8, -58)]], '#3B5E8C', lw=2.4, shd=0)
        fist(cv, x, y, s, skin)
    elif what == 'magnifier':
        M.line(cv, [(x - ux * 10 * s, y - uy * 10 * s), (x + ux * 44 * s, y + uy * 44 * s)], 14 * s, INK)
        M.line(cv, [(x - ux * 8 * s, y - uy * 8 * s), (x + ux * 42 * s, y + uy * 42 * s)], 8 * s, hx('#7A4E30'))
        cx, cy = x + ux * 76 * s, y + uy * 76 * s
        blob(cv, [ellipse_pts(cx, cy, 38 * s, 38 * s, n=48)], '#3A3A42', lw=3.0, shd=0,      # vành đen dày
             inner=[('dot', (cx, cy), 33 * s, hx('#B8BEC6')),                                 # viền kim loại
                    ('dot', (cx, cy), 27 * s, hx('#9ED4EE')),                                 # mặt kính xanh
                    ('dot', (cx + 6 * s, cy + 6 * s), 18 * s, hx('#B9E2F4')),
                    ('line', [(cx - 18 * s, cy - 2 * s), (cx - 4 * s, cy - 18 * s)], hx('#FFFFFF'), 5 * s),
                    ('line', [(cx - 16 * s, cy + 8 * s), (cx - 13 * s, cy + 5 * s)], hx('#FFFFFF'), 4 * s)])
        if lens:
            lens(cx, cy, 27 * s)
        fist(cv, x, y, s, skin)
    elif what == 'banhmi':
        e = cr([(x - 56 * s, y - 6 * s), (x - 30 * s, y - 24 * s), (x + 30 * s, y - 24 * s), (x + 58 * s, y - 8 * s), (x + 40 * s, y + 6 * s),
                (x - 40 * s, y + 6 * s)], n=5)
        inner = [('poly', [(x - 40 * s, y + 2 * s), (x + 40 * s, y + 2 * s), (x + 36 * s, y + 9 * s), (x - 36 * s, y + 9 * s)],
                  hx('#5FA84A'))]
        for k in (-28, -6, 16, 38):
            inner.append(('line', [(x + (k - 9) * s, y - 14 * s), (x + (k + 7) * s, y - 20 * s)], hx('#B57A36'), 3 * s))
        blob(cv, [e], '#E8B266', lw=2.6, shd=5, inner=inner)
        fist(cv, x, y, s, skin)
    elif what == 'whistle':
        blob(cv, [ellipse_pts(x + 6 * s, y - 8 * s, 15 * s, 10 * s, n=20), [(x - 2 * s, y - 14 * s), (x - 22 * s, y - 16 * s),
                                                                            (x - 22 * s, y - 6 * s), (x - 2 * s, y - 4 * s)]],
             '#C9CDD2', lw=2.4, shd=3)
        fist(cv, x, y + 2 * s, s, skin)


# ------------------------------------------------------------------ bảng thử
def demo():
    from gau_nghe_van import Dog
    out = os.path.join(ROOT, 'build', 'thu-hoathinh', 'cau-long')
    os.makedirs(out, exist_ok=True)
    W, H = 1800, 1500
    cv = Image.new('RGBA', (W * SS, H * SS), hx('#EFE6D2') + (255,))
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 470 * SS, W * SS, 500 * SS], fill=hx('#5AA36A') + (255,))
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26 * SS)
    # hàng 1: toàn thân đứng chuẩn + Gâu để so cỡ
    gy = 480
    row = [('khang', 230), ('na', 560), (None, 860), ('tung', 1160), ('thay', 1500)]
    for key, x in row:
        if key is None:
            Dog(cv, x, gy, 0.82, dict(flat=True, mouth='tongue', arms=((18, 8), (18, 8)))).draw()
            name = 'Gâu Nghệ'
        else:
            Human(cv, x, gy, 0.82, CAST[key], dict(mouth='smile', gaze=(0, 0))).draw()
            name = CAST[key]['ten']
        d.text((x * SS, (gy + 30) * SS), name, font=f, fill=INK + (255,), anchor='mt')
    # hàng 2: biểu cảm (cận mặt)
    ex = [('khang', dict(mouth='grin', eyes='open', gaze=(1, 0))), ('khang', dict(mouth='D', eyes='angry')),
          ('na', dict(mouth='D', eyes='happy')), ('na', dict(mouth='o', eyes='wide')),
          ('tung', dict(mouth='open', mo=0.7, eyes='wide', sweat=True)), ('tung', dict(mouth='smile', eyes='sleepy')),
          ('thay', dict(mouth='frown', eyes='angry')), ('thay', dict(mouth='flat', eyes='open', gaze=(-1, 0)))]
    for i, (key, st) in enumerate(ex):
        b = BUILD[CAST[key]['h']]
        tmp = Image.new('RGBA', (400 * SS, 900 * SS), hx('#E4D8BE') + (255,))
        Human(tmp, 200, 230 - b['head'][0] * 1.3, 1.3, CAST[key], st).draw()
        crop = tmp.crop((50 * SS, 60 * SS, 350 * SS, 400 * SS)).resize((210 * SS, 238 * SS), Image.LANCZOS)
        cv.paste(crop, ((10 + i * 222) * SS, 640 * SS))
    # hàng 3: tư thế + đạo cụ
    gy = 1440
    d.rectangle([0, (gy - 6) * SS, W * SS, H * SS], fill=hx('#5AA36A') + (255,))
    poses = [('khang', 200, dict(arm_to={'R': (110, -470)}, hold={'R': 'racket'}, prop_ang={'R': 10}, mouth='grin', gear=True,
                                 eyes='open', gaze=(0.5, -1))),
             ('na', 520, dict(arm_to={'R': (96, -420), 'L': (-46, -200)}, hold={'R': 'phone'}, mouth='D', eyes='happy', lean=-5)),
             ('tung', 860, dict(arm_to={'R': (44, -300)}, hold={'R': 'bottle'}, prop_ang={'R': -70}, gaze=(0, -1), mouth='o', eyes='closed',
                                sweat=True)),
             ('tung', 1150, dict(arm_to={'L': (-110, -230), 'R': (130, -150)}, hold={'L': 'magnifier'}, prop_ang={'L': -35},
                                 mouth='open', mo=0.8, eyes='wide', gaze=(-1, 0.5))),
             ('thay', 1500, dict(arm_to={'R': (54, -345), 'L': (-80, -200)}, hold={'R': 'whistle'}, mouth='o', eyes='angry'))]
    for key, x, st in poses:
        Human(cv, x, gy, 0.82, CAST[key], st).draw()
    p = os.path.join(out, 'nhan-vat-v2.png')
    cv.convert('RGB').resize((W, H), Image.LANCZOS).save(p)
    print(p)


if __name__ == '__main__':
    demo()
