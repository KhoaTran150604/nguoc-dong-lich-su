"""Gâu Nghệ – avatar tư thế 2 (chỉ tay lém lỉnh) đứng trong MỘT KHUNG CẢNH THẬT, vẽ theo lối sitcom hoạt hình VN:
- nét viền đều, màu nâu-đen (INK), cả nhân vật lẫn nền đều có viền;
- màu phẳng, hơi ngả (không gradient, không làm mờ, không phát sáng); bóng = 1 mảng tối phẳng, mép cứng;
- xa → màu nhạt hơn, nét nhạt hơn (không blur); nền nhiều chi tiết nhỏ (bụi cỏ, gợn nước, ván gỗ).
Cảnh: bến gỗ bên sông, cọc gỗ nhô lên mặt nước (gợi Bạch Đằng), núi xa, lũy tre, thuyền buồm nhỏ.
Chạy: python scripts/hoathinh/gau_nghe_avatar_tbm.py → build/thu-hoathinh/gau-nghe/avatar-tbm-*.png/.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, cr  # noqa: E402
from gau_nghe_van import Dog, OUT  # noqa: E402

W = H = 800
rnd = np.random.RandomState(3)


def S(p):
    return [(x * SS, y * SS) for x, y in p]


def poly(d, pts, fill, ol=INK, w=3.0, smooth=False):
    if smooth:
        pts = cr(pts, n=6)
    d.polygon(S(pts), fill=hx(fill) + (255,))
    if ol is not None:
        d.line(S(pts + [pts[0]]), fill=(hx(ol) if isinstance(ol, str) else ol) + (255,), width=int(w * SS), joint='curve')


def pline(d, pts, col, w=2.5):
    d.line(S(pts), fill=(hx(col) if isinstance(col, str) else col) + (255,), width=int(w * SS), joint='curve')


def bumpy(x0, x1, ybase, amp, n, ph=0.0):
    """Đỉnh bụi tre/cây dạng vỏ sò (scallop) – kiểu bụi cây hoạt hình."""
    pts = []
    step = (x1 - x0) / n
    for i in range(n):
        xa = x0 + i * step
        h = amp * (0.7 + 0.5 * math.sin(i * 1.7 + ph))
        for t in np.linspace(0, 1, 7):
            pts.append((xa + t * step, ybase - h * math.sin(math.pi * t)))
    return pts


def scene(d, mode='ngay'):
    C = dict(sky='#EEE7C6', cloud='#FBF6E4', mtn='#C7D0A6', mtn2='#B3C18C', bush='#9DB46C', bush_d='#86A05A',
             water='#BFCDB4', water_d='#A9BB9E', bank='#C9B98A', wood='#A8714A', wood_d='#8A5A3A', wood_l='#BE875C')
    # trời phẳng
    d.rectangle([0, 0, W * SS, H * SS], fill=hx(C['sky']) + (255,))
    # mây phẳng có viền nhạt
    for cx, cy, k in ((150, 120, 1.0), (560, 80, 0.8), (700, 200, 0.6)):
        pts = []
        for i, (dx, r) in enumerate(((-60, 28), (-25, 40), (18, 46), (58, 32))):
            for t in np.linspace(math.pi, 2 * math.pi, 9):
                pts.append((cx + (dx + r * math.cos(t)) * k, cy + r * math.sin(t) * k))
        pts += [(cx + 90 * k, cy), (cx - 88 * k, cy)]
        poly(d, pts, C['cloud'], ol='#CFC7A4', w=2.2)
    # núi xa (nét nhạt)
    poly(d, [(-20, 400), (60, 300), (140, 330), (230, 250), (330, 320), (420, 280), (520, 330), (640, 240), (760, 300),
             (820, 290), (820, 420), (-20, 420)], C['mtn'], ol='#9EA984', w=2.2, smooth=False)
    poly(d, [(-20, 420), (90, 360), (200, 385), (300, 345), (420, 390), (560, 350), (700, 380), (820, 340), (820, 440),
             (-20, 440)], C['mtn2'], ol='#8C9A6A', w=2.4)
    # lũy tre / bụi cây bờ xa
    top = bumpy(-20, 820, 430, 34, 16, 0.3)
    poly(d, top + [(820, 470), (-20, 470)], C['bush'], ol='#5F6E3E', w=2.6)
    for i in range(14):           # nét lá trong bụi
        x = 20 + i * 57 + rnd.uniform(-10, 10)
        pline(d, [(x, 448), (x + 8, 436), (x + 16, 446)], '#6E8248', 2.2)
    for bx in (120, 470, 690):    # cây tre vươn cao
        pline(d, [(bx, 440), (bx + 10, 330), (bx + 30, 260)], '#6E7F45', 3.2)
        for j in range(6):
            yy = 420 - j * 28
            xx = bx + 4 + j * 4.5
            poly(d, [(xx, yy), (xx + 34, yy - 14), (xx + 6, yy + 4)], C['bush_d'], ol='#5F6E3E', w=2)
            poly(d, [(xx, yy), (xx - 30, yy - 10), (xx - 4, yy + 5)], C['bush_d'], ol='#5F6E3E', w=2)
    # dải bờ cát xa
    poly(d, [(-20, 468), (820, 462), (820, 480), (-20, 486)], C['bank'], ol='#8E7E56', w=2.2)
    # mặt sông phẳng + gợn nước bằng nét
    d.rectangle([0, 482 * SS, W * SS, H * SS], fill=hx(C['water']) + (255,))
    pline(d, [(-20, 484), (820, 478)], '#7E8E72', 2.4)
    for i in range(22):
        x = rnd.uniform(0, 800)
        y = rnd.uniform(505, 640)
        L = rnd.uniform(18, 46)
        pline(d, [(x, y), (x + L, y)], '#93A688', 2.2)
    # thuyền buồm nhỏ phía xa
    bx, by = 600, 520
    poly(d, [(bx - 46, by), (bx + 46, by), (bx + 34, by + 14), (bx - 34, by + 14)], '#7A5236', w=2.4)
    poly(d, [(bx - 2, by - 70), (bx + 34, by - 8), (bx - 2, by - 8)], '#E3D3A8', w=2.4)
    pline(d, [(bx - 2, by - 74), (bx - 2, by)], '#5A3A26', 3)
    # cọc gỗ nhô lên mặt nước (nhóm bên phải – chỗ Gâu Nghệ chỉ tay)
    for i, (x, y, h) in enumerate(((520, 600, 52), (560, 588, 46), (600, 604, 58), (648, 592, 48), (690, 606, 56),
                                   (736, 596, 44), (470, 612, 40))):
        poly(d, [(x - 8, y), (x - 6, y - h + 10), (x, y - h), (x + 6, y - h + 10), (x + 8, y)], C['wood'], w=2.6)
        poly(d, [(x + 1, y), (x + 1, y - h + 6), (x + 6, y - h + 10), (x + 8, y)], C['wood_d'], ol=None)
        pline(d, [(x - 8, y), (x - 6, y - h + 10), (x, y - h), (x + 6, y - h + 10), (x + 8, y)], INK, 2.6)
        pline(d, [(x - 16, y + 3), (x + 16, y + 3)], '#7E8E72', 2.2)     # gợn nước quanh chân cọc
    # bến gỗ tiền cảnh (phối cảnh)
    deck = [(-20, 640), (560, 640), (640, 820), (-20, 820)]
    poly(d, deck, C['wood'], w=3)
    for k in range(1, 7):           # khe ván chạy về điểm tụ
        x0 = -20 + k * 90
        pline(d, [(x0, 640), (x0 * 1.18 - 10, 820)], C['wood_d'], 2.6)
    for yy in (690, 752):           # nối ván
        pline(d, [(0, yy), (40, yy)], C['wood_d'], 2.2)
        pline(d, [(250, yy + 8), (300, yy + 8)], C['wood_d'], 2.2)
        pline(d, [(470, yy - 6), (520, yy - 6)], C['wood_d'], 2.2)
    poly(d, [(-20, 640), (560, 640), (566, 652), (-20, 652)], C['wood_l'], w=2.4)   # mép bến
    # cột lan can trái + thanh ngang
    poly(d, [(18, 470), (44, 470), (44, 700), (18, 700)], C['wood'], w=3)
    poly(d, [(34, 470), (44, 470), (44, 700), (34, 700)], C['wood_d'], ol=None)
    pline(d, [(18, 470), (44, 470), (44, 700), (18, 700), (18, 470)], INK, 3)
    poly(d, [(-20, 520), (40, 516), (40, 536), (-20, 540)], C['wood_l'], w=3)
    # bụi cỏ nhỏ ở mép bến
    for gx in (110, 520):
        for j in range(5):
            a = -1.2 + j * 0.6
            pline(d, [(gx, 652), (gx + 22 * math.sin(a), 652 - 26 * math.cos(a) - 6)], '#6E8248', 3)


def main():
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(cv)
    scene(d)
    # bóng nhân vật: mảng tối phẳng trên ván
    poly(d, [(220, 726), (440, 726), (456, 744), (236, 748)], '#8A5A3A', ol=None)
    st = dict(mouth='smirk', lid=(0.42, 0.34), gaze=(1, 0), arms=((18, 8), (80, 122)), flat=True)
    k = 1.25
    Dog(cv, 330, 735, k, st).draw()
    sq = cv.resize((W, H), Image.LANCZOS).convert('RGB')
    sq.save(os.path.join(OUT, 'avatar-tbm-khung.png'))
    # cắt tròn + viền mực
    R = W / 2 - 20
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).ellipse([(W / 2 - R) * SS, (H / 2 - R) * SS, (W / 2 + R) * SS, (H / 2 + R) * SS], fill=255)
    out = Image.new('RGBA', cv.size, hx('#F8EFDC') + (255,))
    out.paste(cv, (0, 0), m)
    ImageDraw.Draw(out).ellipse([(W / 2 - R) * SS, (H / 2 - R) * SS, (W / 2 + R) * SS, (H / 2 + R) * SS],
                                outline=INK + (255,), width=6 * SS)
    av = out.resize((W, H), Image.LANCZOS).convert('RGB')
    av.save(os.path.join(OUT, 'avatar-tbm.png'))
    both = Image.new('RGB', (W * 2 + 20, H), hx('#F2E6CC'))
    both.paste(av, (0, 0))
    both.paste(sq, (W + 20, 0))
    p = os.path.join(OUT, 'avatar-tbm.jpg')
    both.save(p, quality=92)
    print(p)


if __name__ == '__main__':
    main()
