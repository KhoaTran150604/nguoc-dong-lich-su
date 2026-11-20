"""Gâu Nghệ – chó Border Collie cách điệu, 6 mẫu (toàn thân + avatar).

Dùng lại bộ vẽ khối liền (thân + tay + chân một viền) của meo_nghe_cach_dieu.py.
Dấu hiệu Border Collie giữ lại: tai gập đầu, sọc trắng giữa trán, mõm trắng, cổ bờm trắng,
ngực + bàn chân trắng, đuôi xù chóp trắng. Màu: đen-trắng (cổ điển), vàng nghệ-trắng (Red Border Collie),
ba màu (đen + chấm mày nâu).

Chạy:  python scripts/hoathinh/gau_nghe_mau.py
Ra:    build/thu-hoathinh/gau-nghe/gau-nghe-6-mau.jpg
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meo_nghe_cach_dieu as M  # noqa: E402
from meo_nghe_cach_dieu import Char, blob, ell, line, soft_ell, cr, ellipse_pts, hx, mix, SS, INK  # noqa: E402

ROOT = M.ROOT
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'gau-nghe')
WH = hx('#F8F4EC')
TAN = hx('#C98A4A')
FURS = {
    'den': dict(b=hx('#2F2D33'), s=hx('#1C1B1F'), l=hx('#504E57')),
    'nghe': dict(b=hx('#D2802F'), s=hx('#A65D1C'), l=hx('#EDA65C')),
}
M.CREAMY = WH   # tất trắng, chóp đuôi trắng


class Dog(Char):
    def __init__(self, cv, cx, gy, k, d):
        d.setdefault('fur', '#000000')
        super().__init__(cv, cx, gy, k, d)
        self.fur = FURS[d['mau']]

    def head_polys(self):
        d, k = self.d, self.k
        h = d['head']
        hcx, hcy = h.get('dx', 0), h['y']
        self.hc = self.P(hcx, hcy)
        self.R = (h['rx'] * k, h['ry'] * k)
        polys = [ellipse_pts(*self.hc, h['rx'] * k, h['ry'] * k, n=60)]
        self.ear_lines = []
        kinds = d['ears']
        for i, s in enumerate((-1, 1)):
            kind = kinds[i]
            sz = d.get('ear_sz', 1.0)
            if kind == 'drop':
                bx, by = hcx + s * h['rx'] * 0.78, hcy - h['ry'] * 0.55
                pts = [(bx - s * 12 * sz, by + 2), (bx + s * 26 * sz, by - 14 * sz), (bx + s * 50 * sz, by + 26 * sz),
                       (bx + s * 46 * sz, by + 88 * sz), (bx + s * 24 * sz, by + 94 * sz), (bx + s * 10 * sz, by + 40 * sz)]
                self.ear_lines.append(self.Ps([(bx + s * 14 * sz, by + 8 * sz), (bx + s * 26 * sz, by + 60 * sz)]))
            else:
                bx, by = hcx + s * h['rx'] * 0.6, hcy - h['ry'] * 0.74
                if kind == 'up':
                    pts = [(bx - s * 30 * sz, by + 18), (bx - s * 8 * sz, by - 40 * sz), (bx + s * 10 * sz, by - 64 * sz),
                           (bx + s * 26 * sz, by - 40 * sz), (bx + s * 32 * sz, by + 14)]
                else:   # flop: dựng rồi gập chóp ra ngoài
                    pts = [(bx - s * 30 * sz, by + 18), (bx - s * 14 * sz, by - 34 * sz), (bx + s * 8 * sz, by - 54 * sz),
                           (bx + s * 42 * sz, by - 42 * sz), (bx + s * 50 * sz, by - 20 * sz), (bx + s * 30 * sz, by - 22 * sz),
                           (bx + s * 30 * sz, by + 14)]
                    self.ear_lines.append(self.Ps([(bx - s * 2 * sz, by - 34 * sz), (bx + s * 28 * sz, by - 30 * sz)]))
            polys.append(cr(self.Ps(pts), n=5))
        return polys, []

    def head_inner(self, pinks):
        d, k = self.d, self.k
        (hx_, hy), (Rx, Ry) = self.hc, self.R
        inner = [('line', L, self.fur['s'], 3 * k) for L in self.ear_lines]
        bw = d.get('blaze', 1.0)
        blaze = cr([(hx_ - 0.06 * Rx * bw, hy - 0.98 * Ry), (hx_ + 0.06 * Rx * bw, hy - 0.98 * Ry), (hx_ + 0.11 * Rx * bw, hy - 0.25 * Ry),
                    (hx_ + 0.32 * Rx, hy + 0.12 * Ry), (hx_ - 0.32 * Rx, hy + 0.12 * Ry), (hx_ - 0.11 * Rx * bw, hy - 0.25 * Ry)], n=4)
        inner.append(('poly', blaze, WH))
        inner.append(('poly', ellipse_pts(hx_, hy + 0.44 * Ry, 0.48 * Rx, 0.38 * Ry, n=40), WH))
        if d.get('tan'):
            f = d['face']
            ex, ey = f.get('ex', 0.36) * Rx, hy + f.get('ey', -0.04) * Ry
            es = f.get('es', 1.0) * 0.15 * Rx
            for s in (-1, 1):
                inner.append(('poly', ellipse_pts(hx_ + s * ex * 1.02, ey - es * 1.75, es * 0.55, es * 0.38, n=20), TAN))
                inner.append(('poly', ellipse_pts(hx_ + s * 0.42 * Rx, hy + 0.28 * Ry, 0.12 * Rx, 0.09 * Ry, n=20), TAN))
        return inner

    def draw(self, merge_head=False):
        d, k = self.d, self.k
        soft_ell(self.cv, self.P(0, 2), d.get('shw', 90) * k, 11 * k, (60, 40, 20, 55))
        self.tail()
        bp = self.body_polys()
        hp, _ = self.head_polys()
        inner = []
        if d.get('belly'):
            bx, by, brx, bry = d['belly']
            inner.append(('poly', ellipse_pts(*self.P(bx, by), brx * k, bry * k, n=40), WH))
        if d.get('ruff'):
            bx, by, brx, bry = d['ruff']
            inner.append(('poly', ellipse_pts(*self.P(bx, by), brx * k, bry * k, n=40), WH))
        for p in self.hands:
            inner.append(('dot', p, d['arms']['w'] * 0.45 * k, WH))
        for p in self.feet:
            inner.append(('dot', p, d['legs']['w'] * 0.55 * k, WH))
        blob(self.cv, bp, self.fur, lw=3.0, shd=8, hld=5, inner=inner)
        blob(self.cv, hp, self.fur, lw=3.0, shd=8, hld=5, inner=self.head_inner([]))
        self.face()

    def face(self):
        d, k = self.d, self.k
        f = d['face']
        cv = self.cv
        (hx_, hy), (Rx, Ry) = self.hc, self.R
        f2 = dict(f, eyes=('-', '-'), wn=0, nose='none', muzzle=False)
        f2['ny'] = f.get('ny', 0.34)
        orig = d['face']
        d['face'] = f2
        super().face()
        d['face'] = orig
        ex, ey = f.get('ex', 0.36) * Rx, hy + f.get('ey', -0.04) * Ry
        es = f.get('es', 1.0) * 0.15 * Rx
        ink_w = max(2.6, 0.035 * Rx)
        for i, s in enumerate((-1, 1)):
            kind = f['eyes'][i]
            cx, cy = hx_ + s * ex, ey
            if kind == 'happy':
                line(cv, cr([(cx - es, cy + es * 0.3), (cx, cy - es * 0.6), (cx + es, cy + es * 0.3)], closed=False, n=8),
                     ink_w * 1.3, WH if d['mau'] == 'den' else INK)
                continue
            gx = f.get('gaze', 0.0)
            ell(cv, (cx, cy), es * 1.0, es * 1.12, fill=(255, 255, 255), ow=ink_w)
            ell(cv, (cx + gx * es * 0.3, cy + es * 0.08), es * 0.72, es * 0.78, fill=hx('#7A4A22'))
            ell(cv, (cx + gx * es * 0.3, cy + es * 0.08), es * 0.4, es * 0.44, fill=INK)
            ell(cv, (cx + gx * es * 0.3 - es * 0.28, cy - es * 0.26), es * 0.22, es * 0.22, fill=(255, 255, 255))
            lid = f.get('lid', [0, 0])[i] if isinstance(f.get('lid'), (list, tuple)) else f.get('lid', 0)
            if lid:
                top = cy - es * 1.12 + es * 2.24 * lid
                E = ellipse_pts(cx, cy, es * 1.0 + 2, es * 1.12 + 2, n=40)
                ImageDraw.Draw(cv).polygon([(x * SS, min(y, top) * SS) for x, y in E], fill=self.fur['s'] + (255,))
                line(cv, [(cx - es * 1.1, top + s * es * 0.08), (cx + es * 1.1, top - s * es * 0.08)], ink_w * 1.3)
        # mũi chó to
        ny = hy + f.get('ny', 0.34) * Ry - 0.03 * Rx
        nw = 0.13 * Rx
        P = cr([(hx_ - nw, ny - nw * 0.45), (hx_ + nw, ny - nw * 0.45), (hx_ + nw * 0.5, ny + nw * 0.45), (hx_, ny + nw * 0.6),
                (hx_ - nw * 0.5, ny + nw * 0.45)], n=5)
        ImageDraw.Draw(cv).polygon([(x * SS, y * SS) for x, y in P], fill=hx('#1A1517') + (255,))
        ell(cv, (hx_ - nw * 0.35, ny - nw * 0.15), nw * 0.22, nw * 0.13, fill=hx('#6A6468'))


# ------------------------------------------------------------------ khung người (dùng chung)
def tail_r(x, y, h, curl=1):
    return [(x, y), (x + 50, y - 10), (x + 82, y - h * 0.45), (x + 74 + 20 * curl, y - h * 0.85), (x + 46 + 30 * curl, y - h)]


DOGS = [
    dict(ten='Đen trắng · Lém', mo_ta='cổ điển, tai gập, liếc nhếch mép', mau='den', ears=('flop', 'flop'),
         body=('poly', [(0, -300), (58, -286), (72, -180), (66, -80), (40, -40), (0, -34)]),
         legs=dict(x=30, len=50, w=40), arms=dict(x=50, y=-236, len=74, w=30, L='down', R='point'),
         head=dict(y=-350, rx=104, ry=90), tail=dict(path=tail_r(44, -90, 150), w=34, tip=True),
         belly=(0, -150, 40, 70), ruff=(0, -266, 64, 34),
         face=dict(eyes=('d', 'd'), lid=(0.42, 0.34), gaze=0.6, mouth='smirk', brows=(0, 6))),
    dict(ten='Nghệ trắng · Vui', mo_ta='màu vàng nghệ, tròn, lè lưỡi', mau='nghe', ears=('flop', 'flop'),
         body=('super', -150, 112, 120, 2.2),
         legs=dict(x=48, len=40, w=44), arms=dict(x=92, y=-190, len=56, w=34, L='out', R='out'),
         head=dict(y=-318, rx=118, ry=98), tail=dict(path=tail_r(90, -110, 120), w=38, tip=True),
         belly=(0, -140, 70, 80), ruff=(0, -236, 90, 40),
         face=dict(eyes=('happy', 'happy'), mouth='tongue', mw=1.3, blush=True)),
    dict(ten='Đen trắng · Tai lệch', mo_ta='cao gầy, tai dựng tai gập, vẫy chào', mau='den', ears=('up', 'flop'),
         body=('poly', [(0, -320), (42, -312), (48, -240), (42, -170), (30, -130), (0, -126)]),
         legs=dict(x=20, len=134, w=28), arms=dict(x=30, y=-296, len=100, w=24, L='down', R='wave'),
         head=dict(y=-382, rx=86, ry=78), tail=dict(path=tail_r(30, -150, 170), w=28, tip=True),
         ruff=(0, -300, 48, 30), shw=70, ear_sz=0.85,
         face=dict(eyes=('d', 'd'), gaze=-0.5, mouth='w')),
    dict(ten='Nghệ trắng · Chibi', mo_ta='đầu to, tai cụp, mắt to', mau='nghe', ears=('drop', 'drop'),
         body=('poly', [(0, -170), (42, -160), (54, -110), (48, -60), (0, -50)]),
         legs=dict(x=24, len=56, w=30), arms=dict(x=36, y=-150, len=48, w=24, L='stub', R='wave'),
         head=dict(y=-290, rx=134, ry=116), tail=dict(path=tail_r(40, -80, 110), w=28, tip=True),
         ruff=(0, -158, 48, 26), shw=70, ear_sz=1.15,
         face=dict(eyes=('d', 'd'), es=1.35, mouth='w', blush=True, ey=0.0)),
    dict(ten='Ba màu · Thông thái', mo_ta='đen + chấm mày nâu, dáng quả lê, chỉ tay', mau='den', tan=True, ears=('flop', 'up'),
         body=('poly', [(0, -250), (40, -238), (62, -170), (98, -90), (90, -40), (0, -32)]),
         legs=dict(x=42, len=40, w=40), arms=dict(x=40, y=-212, len=82, w=26, L='down', R='point'),
         head=dict(y=-318, rx=96, ry=84), tail=dict(path=tail_r(80, -80, 150), w=32, tip=True),
         belly=(0, -110, 52, 60), ruff=(0, -228, 52, 30),
         face=dict(eyes=('d', 'd'), lid=(0.22, 0.22), gaze=0.2, mouth='smirk')),
    dict(ten='Nghệ trắng · Lém', mo_ta='thân dài, tai dựng, nhún vai', mau='nghe', ears=('up', 'up'),
         body=('poly', [(0, -330), (52, -322), (60, -250), (62, -120), (52, -50), (0, -40)]),
         legs=dict(x=30, len=50, w=36), arms=dict(x=50, y=-280, len=72, w=26, L='shrug', R='shrug'),
         head=dict(y=-386, rx=96, ry=82), tail=dict(path=tail_r(50, -80, 190), w=30, tip=True),
         belly=(0, -170, 42, 100), ruff=(0, -300, 62, 32), ear_sz=0.9,
         face=dict(eyes=('d', 'd'), lid=(0.46, 0.46), gaze=0.7, mouth='smirk', brows=(6, -2))),
]


def draw_card(d, CW, CH, avatar=False):
    cv = Image.new('RGBA', (CW * SS, CH * SS), hx('#F8EFDC') + (255,))
    if not avatar:
        Dog(cv, CW / 2 - 14, CH - 40, 0.82, d).draw()
        return cv.resize((CW, CH), Image.LANCZOS).convert('RGB')
    R, cx, cy = CW / 2 - 18, CW / 2, CH / 2
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    k = 0.68 * R / d['head']['rx']
    Dog(lay, cx - d['head'].get('dx', 0) * k, cy + 0.14 * R - d['head']['y'] * k, k, d).draw()
    dr = ImageDraw.Draw(cv)
    dr.ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=hx('#C9A24A') + (255,))
    for rr in (R * 0.85, R * 0.7, R * 0.55):
        dr.ellipse([(cx - rr) * SS, (cy - rr) * SS, (cx + rr) * SS, (cy + rr) * SS], outline=hx('#B08A38') + (255,), width=3 * SS)
    import numpy as np
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], fill=255)
    arr = np.asarray(lay).copy()
    arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
    cv.alpha_composite(Image.fromarray(arr, 'RGBA'))
    ImageDraw.Draw(cv).ellipse([(cx - R) * SS, (cy - R) * SS, (cx + R) * SS, (cy + R) * SS], outline=hx('#14110F') + (255,),
                               width=7 * SS)
    return cv.resize((CW, CH), Image.LANCZOS).convert('RGB')


def main():
    os.makedirs(OUT, exist_ok=True)
    CW, CH, AH, LAB, TOP = 340, 470, 300, 76, 96
    cols = 3
    rows = math.ceil(len(DOGS) / cols)
    W, H = cols * CW, TOP + rows * (CH + AH + LAB)
    img = Image.new('RGB', (W, H), hx('#F2E6CC'))
    dr = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf'), 46)
    f_n = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 24)
    f_d = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf'), 17)
    dr.text((28, 22), 'GÂU NGHỆ – Border Collie, 6 mẫu', font=f_t, fill=hx('#14110F'))
    for i, d in enumerate(DOGS):
        x0 = (i % cols) * CW
        y0 = TOP + (i // cols) * (CH + AH + LAB)
        img.paste(draw_card(d, CW - 16, CH), (x0 + 8, y0))
        img.paste(draw_card(d, CW - 16, AH, avatar=True), (x0 + 8, y0 + CH))
        dr.rectangle([x0 + 8, y0, x0 + CW - 9, y0 + CH + AH - 1], outline=hx('#C9A24A'), width=2)
        dr.text((x0 + CW / 2, y0 + CH + AH + 24), f'{i + 1} · {d["ten"]}', font=f_n, fill=hx('#B3261E'), anchor='mm')
        dr.text((x0 + CW / 2, y0 + CH + AH + 54), d['mo_ta'], font=f_d, fill=hx('#4A3E3A'), anchor='mm')
    p = os.path.join(OUT, 'gau-nghe-6-mau.jpg')
    img.save(p, quality=90)
    print(p)


if __name__ == '__main__':
    main()
