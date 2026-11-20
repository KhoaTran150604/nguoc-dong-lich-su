"""Gâu Nghệ – 3 khung hình thử 16:9 theo sổ tay docs/plan/hoc-phong-cach-sitcom-vn.md
A toàn cảnh: vỉa hè quán cà phê trong hẻm (nhân vật nhỏ, nền chi tiết, mảng bóng mái hiên)
B trung cảnh: đứng sau quầy, liếc hóng chuyện, khung nghiêng (dutch angle)
C cận mặt: giật mình, nhìn qua vai người khác (tiền cảnh)
Chạy: python scripts/hoathinh/gau_nghe_khung_thu.py → build/thu-hoathinh/gau-nghe/khung-thu-*.png + khung-thu.jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, ellipse_pts  # noqa: E402
from meo_nghe_cach_dieu import blob  # noqa: E402
from gau_nghe_van import Dog, OUT, ROOT  # noqa: E402
from gau_nghe_avatar_tbm import poly, pline  # noqa: E402

W, H = 1600, 900
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')


def new():
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    return cv, ImageDraw.Draw(cv)


def shade(cv, pts, k=0.78, tint=(1.0, 0.97, 1.05)):
    """Mảng bóng phẳng mép cứng (nhân màu – multiply) lên mọi thứ đã vẽ."""
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    m = np.asarray(m) > 0
    a = np.asarray(cv).astype(np.float32)
    a[m, 0] *= k * tint[0]
    a[m, 1] *= k * tint[1]
    a[m, 2] *= min(1.0, k * tint[2])
    cv.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def stains(d, x0, y0, x1, y1, col, n, rnd, big=40):
    """Vết loang tường: mảng màu đậm hơn một chút, không viền."""
    for _ in range(n):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(big * 0.4, big)
        pts = []
        for i in range(14):
            t = 2 * math.pi * i / 14
            rr = r * rnd.uniform(0.6, 1.1)
            pts.append((cx + rr * math.cos(t) * 1.4, cy + rr * math.sin(t) * 0.7))
        d.polygon([(x * SS, y * SS) for x, y in pts], fill=hx(col) + (255,))


def cloud(cv, cx, cy, k):
    polys = [ellipse_pts(cx + dx * k, cy + dy * k, r * k, r * k, n=36)
             for dx, dy, r in ((-70, 0, 34), (-30, -24, 46), (18, -36, 56), (66, -18, 44), (100, 2, 30), (20, 6, 40))]
    polys.append([(cx - 100 * k, cy + 4 * k), (cx + 128 * k, cy + 4 * k), (cx + 128 * k, cy + 32 * k), (cx - 100 * k, cy + 32 * k)])
    blob(cv, polys, dict(b=hx('#FFFFFF'), s=hx('#D6EAF4')), lw=2.4, shd=12, hld=0)


def ton(d, x0, y0, x1, y1, a='#3FAE8A', b='#2E9474'):
    """Hàng rào tôn sóng xanh ngọc."""
    poly(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], a, w=2.6)
    x = x0 + 6
    while x < x1 - 6:
        d.rectangle([x * SS, y0 * SS, (x + 9) * SS, y1 * SS], fill=hx(b) + (255,))
        x += 22
    pline(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], INK, 2.6)


def stool(d, x, y, col, dark, k=1.0):
    """Ghế nhựa thấp (kiểu quán cóc)."""
    poly(d, [(x - 34 * k, y - 50 * k), (x + 34 * k, y - 50 * k), (x + 30 * k, y - 40 * k), (x - 30 * k, y - 40 * k)], col, w=2.4)
    poly(d, [(x - 30 * k, y - 40 * k), (x + 30 * k, y - 40 * k), (x + 36 * k, y), (x + 24 * k, y), (x, y - 26 * k),
             (x - 24 * k, y), (x - 36 * k, y)], dark, w=2.4)


def pole_wires(d, x, top, base):
    poly(d, [(x - 9, top), (x + 9, top), (x + 12, base), (x - 12, base)], '#A9A49A', w=2.6)
    poly(d, [(x - 60, top + 30), (x + 60, top + 30), (x + 60, top + 40), (x - 60, top + 40)], '#8E897F', w=2.2)
    for i, (dx, sag) in enumerate(((-56, 40), (-20, 55), (20, 48), (56, 62))):
        for side in (-1, 1):
            x2 = x + side * 900
            pts = []
            for t in np.linspace(0, 1, 30):
                pts.append((x + dx + (x2 - x - dx) * t, top + 32 + sag * math.sin(math.pi * t) * 1.6 + 30 * t))
            pline(d, pts, '#2A2422', 2.0)
    for j in range(3):                      # cuộn dây rối
        cy = top + 70 + j * 10
        d.ellipse([(x - 30 + j * 8) * SS, cy * SS, (x + 20 + j * 8) * SS, (cy + 18) * SS], outline=hx('#2A2422') + (255,),
                  width=int(2 * SS))


# ------------------------------------------------------------------ A. toàn cảnh
def frame_a(dogfn=None):
    rnd = np.random.RandomState(5)
    cv, d = new()
    d.rectangle([0, 0, W * SS, 420 * SS], fill=hx('#9CD6F0') + (255,))
    cloud(cv, 260, 110, 1.2)
    cloud(cv, 1180, 70, 0.9)
    d = ImageDraw.Draw(cv)
    # dãy nhà ống phía sau
    cols = [('#F1D9A8', '#D9BE8A'), ('#E8B9A0', '#CF9E86'), ('#CFE0C4', '#B3C7A6'), ('#F4E3C3', '#DCC8A2'), ('#BFD6E4', '#A2BCCB')]
    x = -20
    i = 0
    while x < W + 20:
        w = [230, 200, 260, 210, 240][i % 5]
        top = [140, 190, 110, 170, 150][i % 5]
        c, cd = cols[i % 5]
        poly(d, [(x, top), (x + w, top), (x + w, 560), (x, 560)], c, w=3)
        stains(d, x + 10, top + 20, x + w - 10, 540, cd, 5, rnd, 34)
        pline(d, [(x, top), (x + w, top), (x + w, 560), (x, 560), (x, top)], INK, 3)
        # mái tôn nhỏ + cửa sổ chớp xanh + ban công
        poly(d, [(x - 6, top - 14), (x + w + 6, top - 14), (x + w, top), (x, top)], '#C9583E', w=2.6)
        for fy in (top + 40, top + 150):
            if fy + 80 > 470:
                continue
            for wx in (x + 30, x + w - 100):
                poly(d, [(wx, fy), (wx + 70, fy), (wx + 70, fy + 80), (wx, fy + 80)], '#3E8F7A', w=2.6)
                pline(d, [(wx + 35, fy), (wx + 35, fy + 80)], INK, 2.2)
                for ly in range(int(fy + 12), int(fy + 76), 12):
                    pline(d, [(wx + 6, ly), (wx + 30, ly)], '#2E6F5E', 2)
                    pline(d, [(wx + 40, ly), (wx + 64, ly)], '#2E6F5E', 2)
            pline(d, [(x + 16, fy + 90), (x + w - 16, fy + 90)], INK, 3)      # lan can ban công
            for bx in range(int(x + 20), int(x + w - 16), 16):
                pline(d, [(bx, fy + 90), (bx, fy + 116)], '#5A4A40', 2)
        # tầng trệt: cửa cuốn / biển hiệu
        poly(d, [(x + 20, 460), (x + w - 20, 460), (x + w - 20, 560), (x + 20, 560)], '#B9B4AA', w=2.6)
        for ly in range(468, 556, 10):
            pline(d, [(x + 22, ly), (x + w - 22, ly)], '#9C978E', 1.6)
        if i % 2 == 0:
            poly(d, [(x + 30, 410), (x + w - 30, 410), (x + w - 30, 450), (x + 30, 450)], '#D9473A', w=2.6)
        x += w
        i += 1
    # biển quán cà phê (chữ do mình viết)
    poly(d, [(560, 380), (900, 380), (900, 440), (560, 440)], '#F6D35B', w=3)
    f = ImageFont.truetype(FONT, 34 * SS)
    d.text((730 * SS, 410 * SS), 'CÀ PHÊ GÂU', font=f, fill=INK + (255,), anchor='mm')
    # cột điện + dây
    pole_wires(d, 1230, 60, 640)
    # vỉa hè gạch
    poly(d, [(-20, 560), (W + 20, 560), (W + 20, 920), (-20, 920)], '#E3C69A', w=3)
    for k in range(-6, 22):
        x0 = k * 110
        pline(d, [(800 + (x0 - 800) * 0.8, 560), (800 + (x0 - 800) * 1.6, 920)], '#C9A878', 2)
    for yy in (600, 660, 750, 870):
        pline(d, [(-20, yy), (W + 20, yy)], '#C9A878', 2)
    stains(d, 0, 600, W, 880, '#D8B98C', 14, rnd, 30)
    # hàng rào tôn bên phải + chậu mai
    ton(d, 1330, 300, 1620, 600)
    poly(d, [(1380, 600), (1450, 600), (1440, 560), (1390, 560)], '#B5523A', w=2.4)
    for j in range(9):
        a = -1.1 + j * 0.28
        pline(d, [(1415, 560), (1415 + 70 * math.sin(a), 560 - 90 * math.cos(a))], '#6B4A2E', 3)
        d.ellipse([(1415 + 70 * math.sin(a) - 9) * SS, (560 - 90 * math.cos(a) - 9) * SS,
                   (1415 + 70 * math.sin(a) + 9) * SS, (560 - 90 * math.cos(a) + 9) * SS], fill=hx('#F2C230') + (255,),
                  outline=INK + (255,), width=int(1.6 * SS))
    # bàn + ghế quán cóc
    stool(d, 520, 760, '#3B7DD8', '#2E64B0')
    stool(d, 980, 790, '#D9473A', '#B23A2E')
    poly(d, [(640, 700), (860, 700), (850, 716), (650, 716)], '#C8CDD2', w=2.6)     # bàn inox thấp
    pline(d, [(660, 716), (650, 780)], INK, 4)
    pline(d, [(840, 716), (850, 780)], INK, 4)
    poly(d, [(700, 672), (724, 672), (722, 700), (702, 700)], '#7A4526', w=2.2)       # ly cà phê trên bàn
    # bóng mái hiên phủ chéo vỉa hè (mảng tối cứng)
    shade(cv, [(-20, 560), (1330, 560), (1180, 700), (-20, 700)], 0.8)
    for x0, x1 in ((120, 200), (800, 860)):     # vệt nắng lọt qua khe
        shade(cv, [(x0, 560), (x1, 560), (x1 - 60, 700), (x0 - 60, 700)], 1.18, (1, 1, 0.95))
    # Gâu Nghệ nhỏ, cầm ly, liếc sang bàn bên
    d = ImageDraw.Draw(cv)
    d.ellipse([(1010) * SS, 812 * SS, 1180 * SS, 836 * SS], fill=hx('#B99A6E') + (255,))
    if dogfn is None:
        Dog(cv, 1090, 828, 0.62, dict(cup=True, mouth='smirk', lid=(0.38, 0.38), gaze=(-1, 0), flat=True)).draw()
    else:
        dogfn(cv)
    return cv


# ------------------------------------------------------------------ B. trung cảnh, khung nghiêng
B_PAD = 200
BW, BH = W + 2 * B_PAD, H + 2 * B_PAD


def b_back():
    rnd = np.random.RandomState(8)
    cv = Image.new('RGBA', (BW * SS, BH * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(cv)
    # tường vàng kem có vết loang + mảng vữa bong
    poly(d, [(0, 0), (BW, 0), (BW, BH), (0, BH)], '#EBCB8B', ol=None)
    stains(d, 0, 0, BW, 760, '#DDB878', 22, rnd, 60)
    for x, y in ((260, 260), (1500, 180)):
        poly(d, [(x, y), (x + 90, y + 10), (x + 70, y + 60), (x + 10, y + 50)], '#C9B79A', w=2.4)
    # bảng menu bảng đen + lịch treo
    poly(d, [(980, 290), (1440, 290), (1440, 640), (980, 640)], '#2F4A3E', w=4)
    pline(d, [(980, 290), (1440, 290), (1440, 640), (980, 640), (980, 290)], '#7A5A3A', 10)
    f = ImageFont.truetype(FONT, 44 * SS)
    f2 = ImageFont.truetype(FONT, 30 * SS)
    d.text((1210 * SS, 350 * SS), 'MENU', font=f, fill=hx('#F3EEDC') + (255,), anchor='mm')
    for j, t in enumerate(('Đen đá ........ 15k', 'Sữa đá ....... 18k', 'Bạc xỉu ...... 20k', 'Trà đá ......... 5k')):
        d.text((1020 * SS, (410 + j * 52) * SS), t, font=f2, fill=hx('#E9E4D0') + (255,))
    poly(d, [(520, 190), (700, 190), (700, 420), (520, 420)], '#F4EFE4', w=3)          # lịch
    poly(d, [(520, 190), (700, 190), (700, 240), (520, 240)], '#D9473A', w=3)
    f3 = ImageFont.truetype(FONT, 110 * SS)
    d.text((610 * SS, 335 * SS), '18', font=f3, fill=INK + (255,), anchor='mm')
    pline(d, [(610, 150), (610, 190)], INK, 3)
    # cửa sổ: nắng chiếu mảng sáng xiên lên tường
    shade(cv, [(140, 120), (420, 120), (520, 700), (240, 700)], 1.12, (1, 1, 0.93))
    return cv


def b_front(cv):
    d = ImageDraw.Draw(cv)
    # quầy gỗ tiền cảnh che nửa người
    poly(d, [(-20, 860), (BW + 20, 860), (BW + 20, BH + 20), (-20, BH + 20)], '#A8714A', w=4)
    poly(d, [(-20, 840), (BW + 20, 840), (BW + 20, 878), (-20, 878)], '#C48A5A', w=4)
    for yy in (930, 1010, 1090):
        pline(d, [(-20, yy), (BW + 20, yy + 6)], '#8A5A3A', 3)
    poly(d, [(1180, 760), (1240, 760), (1236, 840), (1184, 840)], '#E9E4DA', w=3)        # ly nước trên quầy
    poly(d, [(320, 790), (420, 790), (410, 840), (330, 840)], '#C46A45', w=3)             # chậu cây nhỏ
    for a in (-30, -10, 10, 30):
        poly(d, [(370, 790), (370 + a, 720 + abs(a)), (370 + a * 0.4 + 8, 786)], '#6FA14C', ol='#3F6B2C', w=2.4)
    shade(cv, [(-20, 878), (BW + 20, 878), (BW + 20, 920), (-20, 920)], 0.75)              # bóng dưới mép quầy
    return cv


def b_rotate(cv, ang=6):
    """Nghiêng khung (dutch angle), cắt về 1600x900."""
    cv = cv.rotate(ang, resample=Image.BICUBIC, center=(BW * SS / 2, BH * SS / 2))
    return cv.crop((B_PAD * SS, B_PAD * SS, (B_PAD + W) * SS, (B_PAD + H) * SS))


def frame_b():
    cv = b_back()
    # Gâu Nghệ sau quầy, liếc sang trái hóng chuyện
    Dog(cv, 860, 1000, 1.75, dict(cup=True, mouth='smirk', lid=(0.45, 0.45), gaze=(-1, 0), brow=(8, 0), flat=True)).draw()
    b_front(cv)
    return b_rotate(cv)


# ------------------------------------------------------------------ C. cận mặt, nhìn qua vai
def c_back():
    rnd = np.random.RandomState(9)
    cv, d = new()
    poly(d, [(0, 0), (W, 0), (W, H), (0, H)], '#EBCB8B', ol=None)
    stains(d, 0, 0, W, H, '#DDB878', 14, rnd, 80)
    ton(d, 1150, -20, 1620, 760)
    shade(cv, [(-20, 620), (W + 20, 560), (W + 20, H + 20), (-20, H + 20)], 0.86)
    return cv


def c_shock(cv, dy=0.0):
    d = ImageDraw.Draw(cv)
    # giọt mồ hôi + vạch giật mình
    poly(d, [(1170, 330 + dy), (1196, 390 + dy), (1182, 412 + dy), (1156, 404 + dy), (1150, 380 + dy)], '#BFE6F7', w=3, smooth=True)
    for a in (-0.5, -0.15, 0.2):
        x, y = 1200, 330
        pline(d, [(x + 40 * math.cos(a), y + 40 * math.sin(a) - 40), (x + 90 * math.cos(a), y + 90 * math.sin(a) - 60)], INK, 5)


def c_front(cv):
    # tiền cảnh: vai + gáy người ngồi bàn bên (mảng tối phẳng, có viền)
    blob(cv, [[(-80, 700), (560, 740), (640, 960), (-80, 960)], ellipse_pts(250, 760, 340, 120, n=50)],
         dict(b=hx('#9A3A3A'), s=hx('#7A2C2E')), lw=4.4, shd=18, hld=0)                 # vai áo đỏ
    blob(cv, [ellipse_pts(240, 560, 230, 250, n=60)], dict(b=hx('#3A3238'), s=hx('#2A2328')), lw=4.4, shd=22, hld=0,
         inner=[('line', [(150, 380), (210, 470)], hx('#55494F'), 4), ('line', [(260, 360), (290, 460)], hx('#55494F'), 4)])
    return cv


def frame_c():
    cv = c_back()
    Dog(cv, 860, 1250, 2.45, dict(mouth='open', big=1.25, gaze=(-1, 0), brow=(14, 0), flat=True)).draw()
    c_shock(cv)
    return c_front(cv)


def main():
    outs = []
    for name, fn in (('A-toan-canh', frame_a), ('B-trung-canh', frame_b), ('C-can-mat', frame_c)):
        im = fn().resize((W, H), Image.LANCZOS).convert('RGB')
        p = os.path.join(OUT, f'khung-thu-{name}.png')
        im.save(p)
        outs.append(im)
        print(p)
    sheet = Image.new('RGB', (W, H * 3 + 40), hx('#F2E6CC'))
    for i, im in enumerate(outs):
        sheet.paste(im, (0, i * (H + 20)))
    sheet.resize((W // 2, (H * 3 + 40) // 2), Image.LANCZOS).save(os.path.join(OUT, 'khung-thu.jpg'), quality=90)


if __name__ == '__main__':
    main()
