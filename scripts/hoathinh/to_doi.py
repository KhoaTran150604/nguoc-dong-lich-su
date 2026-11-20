"""Tổ đội – Gâu Nghệ + nhân vật phụ, theo sổ tay mục 9 (M1–M14: cảnh nhiều nhân vật).

Nhân vật phụ dùng lại khung "mèo cách điệu" (meo_nghe_cach_dieu.Char) nhưng ĐỔI màu, tên, vai trò;
mỗi con một bóng dáng khác (M6). Tất cả vẽ lối sitcom: viền đậm, bóng cứng (flat).

Chạy:  python scripts/hoathinh/to_doi.py   →  build/thu-hoathinh/to-doi/to-doi-<n>.png + bang-to-doi.jpg
"""
import copy
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meo_nghe_cach_dieu as M  # noqa: E402
from ngo_quyen_can_canh import SS, INK, hx, ellipse_pts  # noqa: E402
from gau_nghe_avatar_tbm import poly, pline  # noqa: E402
from gau_nghe_van import Dog, ROOT  # noqa: E402
import gau_nghe_khung_thu as K  # noqa: E402
import sitcom_fx as F  # noqa: E402

W, H = 1600, 900
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'to-doi')

# ---- lối sitcom cho nhân vật phụ: viền đậm hơn, mảng bóng cứng rõ hơn (giống Dog flat)
_blob0 = M.blob


def _blob_flat(cv, polys, c, lw=3.0, shd=8, hld=5, inner=()):
    return _blob0(cv, polys, c, lw=lw * 1.45, shd=shd * 1.6, hld=0, inner=inner)


M.blob = _blob_flat

# ---- dàn nhân vật phụ (tên của kênh, không lấy của kênh khác)
_base = {c['ten']: c for c in M.CHARS}


def _mk(src, ten, fur, vai, **face):
    d = copy.deepcopy(_base[src])
    d['ten'], d['fur'], d['vai'] = ten, fur, vai
    d['face'].update(face)
    return d


CAST = {
    'mit':   _mk('Bánh Bao', 'Mít', '#E9A93A', 'tròn ủm, ham ăn, hay cười', eyes=('happy', 'happy')),
    'muop':  _mk('Cục Gạch', 'Mướp', '#8E8E98', 'mèo mướp xám, chán đời, khoanh tay', eyes=('line', 'line')),
    'sao':   _mk('Cao Kều', 'Sào', '#C98A4E', 'cao lêu nghêu, lém, hay cãi', eyes=('smug', 'cat')),
    'dau':   _mk('Chíp Bông', 'Đậu', '#F2D6A2', 'tí hon, mắt long lanh, hỏi nhiều', eyes=('bigdot', 'bigdot')),
}


def side(cv, key, x, gy, k, look=0.0, **face):
    """Vẽ nhân vật phụ. look = -1..1: quay mặt (mắt + miệng dịch) về phía người nói (M4)."""
    d = copy.deepcopy(CAST[key])
    d['face'].update(face)
    c = M.Char(cv, x, gy, k, d)
    f0 = c.face

    def face_turned():
        (hx_, hy), (Rx, Ry) = c.hc, c.R
        c.hc = (hx_ + look * 0.16 * Rx, hy)
        f0()
        c.hc = (hx_, hy)
    c.face = face_turned
    c.draw()
    return c


def back_head(cv, x, y, r, fur, ears='tri'):
    """M3/M8: đầu người nghe quay lưng ở tiền cảnh (bị mép khung cắt) – khối màu + tai + viền."""
    hd = ellipse_pts(x, y, r, r * 0.9, n=60)
    polys = [hd]
    for s in (-1, 1):
        ex = x + s * r * 0.62
        if ears == 'tri':
            polys.append([(ex - r * 0.28, y - r * 0.6), (ex + s * r * 0.08, y - r * 1.25), (ex + r * 0.28, y - r * 0.55)])
        else:
            polys.append(ellipse_pts(ex, y - r * 0.8, r * 0.3, r * 0.3, n=30))
    polys.append([(x - r * 1.5, y + r * 0.6), (x + r * 1.5, y + r * 0.6), (x + r * 1.9, y + r * 3), (x - r * 1.9, y + r * 3)])
    _blob0(cv, polys, M.C3(fur), lw=4.4, shd=26, hld=0)


# ------------------------------------------------------------------ khung 1: hàng ngang ở lan can bến sông (M1, M2, M4, M5, M6)
def frame_1():
    c = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 560), (0, 560)], '#D8E8EC', ol=None)
    K.cloud(c, 260, 110, 0.75)
    K.cloud(c, 1250, 80, 0.6)
    d = ImageDraw.Draw(c)
    F.layers_far(d, 300, n=3, base='#5E7A6C', sky='#D8E8EC', seed=4, bottom=470)
    poly(d, [(-20, 440), (W + 20, 430), (W + 20, 600), (-20, 610)], '#8EB7B8', w=2.2)
    for i in range(14):
        x = 40 + i * 120
        pline(d, [(x, 470 + (i % 3) * 30), (x + 56, 470 + (i % 3) * 30)], '#6E9A9C', 2)
    for x in (180, 1380):                                         # cọc gỗ dưới sông (gợi Bạch Đằng)
        for j in range(4):
            xx = x + j * 34
            poly(d, [(xx - 7, 560), (xx - 6, 470 - 10 * (j % 2)), (xx, 455 - 10 * (j % 2)), (xx + 6, 470 - 10 * (j % 2)), (xx + 7, 560)],
                 '#7A5236', w=2)
    poly(d, [(-20, 600), (W + 20, 590), (W + 20, 920), (-20, 920)], '#B08A60', w=2.6)      # sàn gỗ bến
    for y in (660, 740, 830):
        pline(d, [(-20, y), (W + 20, y - 6)], '#94704C', 2.2)
    for x in range(40, W, 150):
        pline(d, [(x, 600), (x - 30, 900)], '#94704C', 1.6)
    # lan can sau lưng nhân vật
    poly(d, [(-20, 548), (W + 20, 540), (W + 20, 566), (-20, 574)], '#C8632E', w=2.6)
    for x in range(30, W, 92):
        poly(d, [(x, 566), (x + 12, 566), (x + 12, 640), (x, 640)], '#E0DCD0', w=2)
    poly(d, [(-20, 636), (W + 20, 630), (W + 20, 648), (-20, 654)], '#C8632E', w=2.4)
    K.shade(c, [(-20, 648), (W + 20, 642), (W + 20, 700), (-20, 706)], 0.84)

    gy = 820
    # sau → trước (chồng lấn): Sào cao ở sau-trái, Mướp khoanh tay, Gâu Nghệ nói, Mít, Đậu tí hon trước
    side(c, 'sao', 470, gy - 14, 0.86, look=1, mouth='smirk')
    side(c, 'muop', 610, gy, 0.82, look=1, mouth='flat')
    Dog(c, 830, gy + 4, 1.0, dict(book=True, mouth='open', gaze=(0, 0.6), flat=True)).draw()
    side(c, 'mit', 1040, gy, 0.80, look=-1, mouth='D')
    side(c, 'dau', 1190, gy + 30, 0.62, look=-1, mouth='o')
    return c


# ------------------------------------------------------------------ khung 2: bàn trà đêm ấm, qua vai (M3, M8, M9)
def frame_2():
    c = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 640), (0, 640)], '#E2D0AC', ol=None)
    F.crack(d, 1340, 140, 80, seed=2)
    F.crack(d, 220, 380, 60, seed=5)
    poly(d, [(1180, 160), (1300, 160), (1300, 420), (1180, 420)], '#7A4E30', w=2.6)          # cửa sổ đêm
    poly(d, [(1192, 172), (1288, 172), (1288, 408), (1192, 408)], '#2E3E62', w=2)
    for xx in (1224, 1256):
        pline(d, [(xx, 172), (xx, 408)], '#7A4E30', 5)
    F.tet_calendar(d, 420, 120)
    F.lattice_door(d, 40, 110, 300, 640)
    poly(d, [(0, 640), (W, 640), (W, 920), (0, 920)], '#A8845C', w=2.6)
    for x in (560, 1080):
        K.stool(d, x, 880, '#C8382E', '#A82A22', 1.1)
    # nhân vật đứng SAU bàn → vẽ trước, mặt bàn vẽ sau che phần dưới (M9)
    side(c, 'mit', 600, 716, 0.62, look=1, mouth='D')
    Dog(c, 830, 724, 0.8, dict(cup=True, sip=False, mouth='smirk', gaze=(-0.4, 0), lid=(0.3, 0.3), flat=True)).draw()
    side(c, 'dau', 1020, 716, 0.5, look=-1, mouth='w')
    d = ImageDraw.Draw(c)
    poly(d, [(770, 700), (870, 700), (860, 900), (780, 900)], '#6E4630', w=2.4)
    poly(d, ellipse_pts(820, 694, 380, 74, n=60), '#8A5A3A', w=3)
    poly(d, ellipse_pts(820, 684, 360, 62, n=60), '#A06A42', ol=None)
    K.shade(c, ellipse_pts(820, 790, 400, 40, n=40), 0.8)
    d = ImageDraw.Draw(c)
    F.tea_set(d, 760, 700, 0.8)
    F.oil_lamp(d, 1010, 700)
    F._grade(c, (0.80, 0.70, 0.66), (12, 6, 4))                 # đêm ấm nhẹ: giữ màu nhân vật, không lộ mép quầng
    F.window_beam(c, [(960, 520), (1080, 520), (1180, 900), (900, 900)], 1.12)
    back_head(c, 1440, 760, 210, '#5E5A60')                     # Mướp quay lưng ở tiền cảnh (màu đã ám đêm)
    return c


# ------------------------------------------------------------------ khung 3: qua vai + đám đông ở chợ (M3, M5, M7)
def frame_3():
    c = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 520), (0, 520)], '#CFE4EE', ol=None)
    K.cloud(c, 1100, 90, 0.7)
    d = ImageDraw.Draw(c)
    F.layers_far(d, 360, n=2, base='#8A9AA6', sky='#CFE4EE', seed=11, bottom=520)
    for i, x in enumerate((60, 420, 820, 1180)):                   # dãy sạp chợ mái tôn
        poly(d, [(x, 300), (x + 330, 300), (x + 360, 360), (x - 30, 360)], ['#C8632E', '#3F8E7A', '#C8632E', '#3B5E8C'][i], w=2.4)
        poly(d, [(x, 360), (x + 330, 360), (x + 330, 520), (x, 520)], '#E6D8B8', w=2.2)
        for j in range(5):
            poly(d, ellipse_pts(x + 40 + j * 62, 470, 26, 16, n=20), ['#E9A93A', '#7FB25C', '#D9583A'][(i + j) % 3], w=1.6)
    poly(d, [(-20, 520), (W + 20, 520), (W + 20, 920), (-20, 920)], '#C9B48A', w=2.6)
    F.crowd(c, 40, 1560, 470, 600, n=46, col='#8A8498', seed=7)
    gy = 830
    side(c, 'muop', 760, gy, 0.8, look=1, mouth='flat')
    Dog(c, 960, gy, 1.05, dict(mouth='open', gaze=(-1, 0), arms=((60, 40), (18, 8)), flat=True)).draw()
    side(c, 'dau', 1130, gy + 20, 0.6, look=-1, mouth='o')
    back_head(c, 230, 700, 260, '#C98A4E')                          # Sào quay lưng, tiền cảnh trái
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    frames = [('M1/M2/M4 Hàng ngang ở bến, cao thấp khác nhau', frame_1()),
              ('M8/M9 Bàn trà đêm, người nghe quay lưng', frame_2()),
              ('M3 Chợ: lưng tiền cảnh – người nói – đám đông', frame_3())]
    font = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 24)
    PW, PH = 800, 450
    sheet = Image.new('RGB', (PW * 2, (PH + 40) * 2), hx('#F2E6CC'))
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(frames):
        im = im.resize((W, H), Image.LANCZOS).convert('RGB')
        im.save(os.path.join(OUT, 'to-doi-%d.png' % (i + 1)))
        x, y = (i % 2) * PW, (i // 2) * (PH + 40)
        sheet.paste(im.resize((PW, PH), Image.LANCZOS), (x, y + 40))
        dr.text((x + 10, y + 8), name, font=font, fill=hx('#14110F'))
    # ô thứ 4: bảng tên dàn nhân vật
    x, y = PW, PH + 40
    f2 = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf'), 22)
    dr.text((x + 20, y + 20), 'Dàn nhân vật (thử)', font=font, fill=hx('#B3261E'))
    rows = [('Gâu Nghệ', 'Border Collie – người kể sử')] + [(v['ten'], v['vai']) for v in CAST.values()]
    for j, (a, b) in enumerate(rows):
        dr.text((x + 20, y + 70 + j * 44), f'{a}: {b}', font=f2, fill=hx('#14110F'))
    p = os.path.join(OUT, 'bang-to-doi.jpg')
    sheet.save(p, quality=90)
    print(p)


if __name__ == '__main__':
    main()
