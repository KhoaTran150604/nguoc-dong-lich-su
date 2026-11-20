"""Gâu Nghệ uống cà phê sữa đá, hóng chuyện trên sân thượng nhà cao tầng nhìn xuống thành phố.
Lối vẽ sitcom: màu phẳng, viền đều nâu-đen, bóng phẳng mép cứng, xa thì nhạt màu/nhạt nét (không blur).
Chạy: python scripts/hoathinh/gau_nghe_avatar_cafe.py → build/thu-hoathinh/gau-nghe/avatar-cafe*.png/.jpg
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, ellipse_pts  # noqa: E402
from meo_nghe_cach_dieu import blob  # noqa: E402
from gau_nghe_van import Dog, OUT  # noqa: E402
from gau_nghe_avatar_tbm import poly, pline, W, H  # noqa: E402

rnd = np.random.RandomState(11)


def building(d, x, top, w, base, col, win, ol, lw, roof=None, rows=None):
    poly(d, [(x, top), (x + w, top), (x + w, base), (x, base)], col, ol=ol, w=lw)
    # cạnh tối bên phải (mặt bên)
    sw = max(6, w * 0.14)
    poly(d, [(x + w - sw, top), (x + w, top), (x + w, base), (x + w - sw, base)], win[1], ol=None)
    pline(d, [(x + w - sw, top), (x + w - sw, base)], ol, lw * 0.7)
    # cửa sổ lưới
    gx = 5 if w > 60 else 3
    cw = (w - sw - 12) / gx
    r = 0
    y = top + 12
    while y + 14 < base and (rows is None or r < rows):
        for i in range(gx):
            xx = x + 6 + i * cw
            lit = rnd.rand() < 0.15
            poly(d, [(xx + 2, y), (xx + cw - 3, y), (xx + cw - 3, y + 12), (xx + 2, y + 12)],
                 '#F6E7A8' if lit else win[0], ol=None)
        y += 22
        r += 1
    if roof == 'tank':      # bồn nước inox trên mái
        tx = x + w * 0.25
        poly(d, [(tx, top - 26), (tx + 30, top - 26), (tx + 30, top), (tx, top)], '#D9DEE2', ol=ol, w=lw)
        pline(d, [(tx, top - 14), (tx + 30, top - 14)], '#A9B1B8', lw * 0.8)
    elif roof == 'antenna':
        pline(d, [(x + w * 0.5, top), (x + w * 0.5, top - 46)], ol, lw)
        pline(d, [(x + w * 0.5 - 12, top - 30), (x + w * 0.5 + 12, top - 30)], ol, lw * 0.8)


def cloud(cv, cx, cy, k):
    """Mây bồng: hợp nhiều vòng tròn → MỘT viền liền, đáy phẳng, mảng bóng xanh nhạt ở dưới."""
    polys = [ellipse_pts(cx + dx * k, cy + dy * k, r * k, r * k, n=36)
             for dx, dy, r in ((-70, 0, 34), (-30, -24, 46), (18, -36, 56), (66, -18, 44), (100, 2, 30), (20, 6, 40))]
    polys.append([(cx - 100 * k, cy + 4 * k), (cx + 128 * k, cy + 4 * k), (cx + 128 * k, cy + 32 * k), (cx - 100 * k, cy + 32 * k)])
    blob(cv, polys, dict(b=hx('#FFFFFF'), s=hx('#DCEBF4')), lw=2.4, shd=12, hld=0)


def top_building(d, x, top, w, col, side, roof_col, ol, lw, tank=False, garden=False):
    """Nhà nhìn từ trên cao: mặt tiền có cửa sổ + mặt mái (sáng) + đồ trên mái."""
    poly(d, [(x, top + 12), (x + w, top + 12), (x + w, 820), (x, 820)], col, ol=ol, w=lw)
    poly(d, [(x + w - w * 0.16, top + 12), (x + w, top + 12), (x + w, 820), (x + w - w * 0.16, 820)], side, ol=None)
    pline(d, [(x + w - w * 0.16, top + 12), (x + w - w * 0.16, 820)], ol, lw * 0.7)
    poly(d, [(x + 6, top), (x + w + 6, top), (x + w, top + 12), (x, top + 12)], roof_col, ol=ol, w=lw)
    y = top + 24
    while y < 820:
        for i in range(max(2, int(w // 26))):
            xx = x + 7 + i * 24
            if xx + 14 > x + w * 0.84:
                break
            poly(d, [(xx, y), (xx + 14, y), (xx + 14, y + 12), (xx, y + 12)],
                 '#F6E7A8' if rnd.rand() < 0.12 else '#7F9DB3', ol=None)
        y += 24
    if tank:
        tx = x + w * 0.3
        poly(d, [(tx, top - 18), (tx + 24, top - 18), (tx + 24, top + 4), (tx, top + 4)], '#E1E6EA', ol=ol, w=lw)
        pline(d, [(tx, top - 8), (tx + 24, top - 8)], '#A9B1B8', lw * 0.8)
    if garden:
        for j in range(3):
            gx = x + 12 + j * 16
            poly(d, [(gx - 9, top + 2), (gx, top - 14), (gx + 9, top + 2)], '#7DB05A', ol='#4E6B34', w=lw * 0.8)


def scene(cv):
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 0, W * SS, H * SS], fill=hx('#9FD4EE') + (255,))
    for cx, cy, k in ((150, 120, 1.0), (600, 70, 0.8), (690, 230, 0.55)):
        cloud(cv, cx, cy, k)
    d = ImageDraw.Draw(cv)
    # đường chân trời: thành phố xa – xanh nhạt, nét nhạt, không cửa sổ
    x = -10
    while x < 820:
        w = rnd.randint(22, 46)
        t = rnd.randint(262, 318)
        poly(d, [(x, t), (x + w, t), (x + w, 360), (x, 360)], '#BCD6E6', ol='#97B5C9', w=1.6)
        x += w - 2
    # sông chạy ngang thành phố (gợi Sài Gòn/Hà Nội, không vẽ công trình có thật)
    poly(d, [(-20, 338), (820, 326), (820, 352), (-20, 366)], '#8EC3DA', ol='#6E9EB6', w=1.8)
    # lớp nhà nhìn từ trên: xa → gần (càng gần càng đậm, nét càng rõ)
    layers = [(350, 4, ['#D9E3EA', '#E6DCCF', '#DDE6D6'], '#9AAAB6', 1.6, 24, 40),
              (400, 3, ['#E9CFB3', '#D3E0C2', '#F0DCCF', '#CFDCE8', '#E8DFC3'], '#6E625A', 2.0, 40, 70),
              (470, 2, ['#E3B992', '#C9DBA9', '#EBCDBE', '#BFD3E3', '#E4D7AE', '#D9C3D9'], '#4E423C', 2.4, 60, 100)]
    for top0, var, cols, ol, lw, w0, w1 in layers:
        x = -30
        while x < 820:
            w = rnd.randint(w0, w1)
            c = cols[rnd.randint(len(cols))]
            top = top0 + rnd.randint(-var * 10, var * 10)
            top_building(d, x, top, w, c, '#00000000' and c, '#F3EEE2', ol, lw,
                         tank=rnd.rand() < 0.4, garden=rnd.rand() < 0.25)
            x += w + rnd.randint(0, 6)
    # sân thượng của mình: lan can sắt + sàn gạch
    poly(d, [(-20, 600), (820, 600), (820, 820), (-20, 820)], '#D8C4A4', ol=INK, w=3)
    for i in range(-2, 12):                     # mạch gạch phối cảnh
        x0 = i * 90
        pline(d, [(400 + (x0 - 400) * 0.7, 600), (400 + (x0 - 400) * 1.4, 820)], '#BCA886', 2.2)
    for yy in (632, 680, 744):
        pline(d, [(-20, yy), (820, yy)], '#BCA886', 2.2)
    poly(d, [(-20, 588), (820, 588), (820, 604), (-20, 604)], '#BDB3A2', ol=INK, w=2.6)        # gờ tường
    pline(d, [(-20, 534), (820, 534)], '#5E6E78', 4)                                           # tay vịn
    pline(d, [(-20, 562), (820, 562)], '#5E6E78', 3)
    for x in range(10, 820, 46):
        pline(d, [(x, 534), (x, 590)], '#5E6E78', 3)
    # ghế nhựa đỏ + phin cà phê bên trái, chậu cây bên phải
    poly(d, [(70, 660), (170, 660), (162, 676), (78, 676)], '#D9473A', ol=INK, w=2.6)
    poly(d, [(84, 676), (96, 676), (90, 740), (80, 740)], '#C23A30', ol=INK, w=2.4)
    poly(d, [(144, 676), (156, 676), (160, 740), (150, 740)], '#C23A30', ol=INK, w=2.4)
    poly(d, [(104, 640), (136, 640), (132, 660), (108, 660)], '#F2EEE6', ol=INK, w=2.2)        # ly
    poly(d, [(106, 622), (134, 622), (130, 640), (110, 640)], '#B8BDC2', ol=INK, w=2.2)        # phin
    poly(d, [(100, 618), (140, 618), (140, 624), (100, 624)], '#9AA0A6', ol=INK, w=2)
    poly(d, [(690, 640), (760, 640), (750, 700), (700, 700)], '#C46A45', ol=INK, w=2.6)
    for a in (-34, -16, 0, 18, 36):
        poly(d, [(725, 640), (725 + a, 580 + abs(a) * 0.5), (725 + a * 0.4 + 7, 636)], '#6FA14C', ol='#3F6B2C', w=2.2)
    poly(d, [(330, 728), (540, 728), (556, 746), (346, 748)], '#BCA886', ol=None)              # bóng nhân vật


def main():
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    scene(cv)
    st = dict(cup=True, mouth='smirk', lid=(0.38, 0.38), gaze=(-1, 1), brow=(6, 0), flat=True)
    Dog(cv, 440, 738, 0.95, st).draw()
    sq = cv.resize((W, H), Image.LANCZOS).convert('RGB')
    sq.save(os.path.join(OUT, 'avatar-cafe-khung.png'))
    R = W / 2 - 20
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).ellipse([(W / 2 - R) * SS, (H / 2 - R) * SS, (W / 2 + R) * SS, (H / 2 + R) * SS], fill=255)
    out = Image.new('RGBA', cv.size, hx('#F8EFDC') + (255,))
    out.paste(cv, (0, 0), m)
    ImageDraw.Draw(out).ellipse([(W / 2 - R) * SS, (H / 2 - R) * SS, (W / 2 + R) * SS, (H / 2 + R) * SS],
                                outline=INK + (255,), width=6 * SS)
    av = out.resize((W, H), Image.LANCZOS).convert('RGB')
    av.save(os.path.join(OUT, 'avatar-cafe.png'))
    both = Image.new('RGB', (W * 2 + 20, H), hx('#F2E6CC'))
    both.paste(av, (0, 0))
    both.paste(sq, (W + 20, 0))
    p = os.path.join(OUT, 'avatar-cafe.jpg')
    both.save(p, quality=92)
    print(p)


if __name__ == '__main__':
    main()
