"""Nền BẾN SÔNG chi tiết (vẽ bằng code) cho cảnh sitcom Văn – Võ.

Chuẩn: nhân vật nhỏ + đơn giản, NỀN vẽ kỹ, nhiều đồ vật, có vết cũ, có ánh sáng và bóng đổ.
Lớp:  sky (trời, mây, núi xa, bờ xa)  →  mud (lòng sông)  →  [nước – vẽ theo khung]  →
      mid (cầu gỗ, cọc cầu)  →  [thuyền neo – theo khung]  →  fg (bờ, nhà tranh, chum, tre, chuối, lau sậy)
Đồ vật trong mid/fg được "nướng" bóng đổ + 3 tông một lần bằng scripts/video/anhsang.py (noi_khoi).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'video'))
import ngo_quyen_can_canh as cc  # noqa: E402
from ngo_quyen_can_canh import cr, hx, mix, stroke  # noqa: E402
import anhsang  # noqa: E402

# Tông màu dịu cho sitcom (người dùng: bản đầu sáng/rực quá). Thêm vào bảng preset, không sửa preset cũ.
anhsang.PRESETS['diu'] = dict(sun=(250, 214, 160), shadow=(58, 42, 70), light_dir=(-0.62, -0.78), sun_k=0.18,
                              dark_k=0.38, haze=(214, 200, 180), haze_k=0.28, split_lo=(46, 40, 80),
                              split_hi=(240, 206, 150), split_k=0.22, contrast=1.04, sat=0.74, vignette=0.45)
TONE = 'diu'

SS = cc.SS
W, H = 1920, 1080
LW = 3.4                     # viền
INK = hx('#2B2222')


def S_(c, s=None, l=None):
    d = dict(b=hx(c))
    d['s'] = hx(s) if s else mix(hx(c), hx('#3A3040'), 0.25)
    if l:
        d['l'] = hx(l)
    return d


def shp(cv, pts, c, lw=LW, shd=6, inner=()):
    cc.shape(cv, pts, c, lw, shd, 0, inner, light=False)


def line(cv, pts, col, w):
    ImageDraw.Draw(cv).line([(x * SS, y * SS) for x, y in pts], fill=hx(col) + (255,) if isinstance(col, str) else col,
                            width=max(1, int(w * SS)), joint='curve')


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ---------------------------------------------------------------- đồ vật
def plank(cv, x0, y0, x1, y1, rng, col='#B9844E'):
    """Tấm gỗ: thớ gỗ, mắt gỗ, đinh, vết nứt."""
    inner = []
    for k in range(3):
        yy = y0 + (y1 - y0) * (0.25 + 0.25 * k) + rng.uniform(-2, 2)
        pts = [(x0 + 4, yy)] + [(x0 + (x1 - x0) * u, yy + rng.uniform(-2, 2)) for u in (0.3, 0.6)] + [(x1 - 4, yy)]
        inner.append(('line', pts, hx('#8E5E34') + (255,), 1.6))
    if rng.random() < 0.6:
        kx = rng.uniform(x0 + 20, x1 - 20)
        ky = (y0 + y1) / 2
        inner.append(('dot', (kx, ky), 4.5, hx('#7A4C2A') + (255,)))
    if rng.random() < 0.4 and x1 - x0 > 30:
        cx_ = rng.uniform(x0 + 6, max(x0 + 7, x1 - 24))
        inner.append(('line', [(cx_, y0 + 2), (cx_ + 10, y0 + (y1 - y0) * 0.4), (cx_ + 6, y0 + (y1 - y0) * 0.7)],
                      hx('#6A4024') + (255,), 1.8))
    for nx in (x0 + 10, x1 - 10):
        inner.append(('dot', (nx, (y0 + y1) / 2), 2.6, hx('#4A4A52') + (255,)))
    shp(cv, rect(x0, y0, x1, y1), S_(col, '#9A6A3E'), LW * 0.8, 4, inner)


def post(cv, x, y0, y1, w=16, col='#8A5A34'):
    inner = [('line', [(x - w * 0.2, y0 + 8), (x - w * 0.15, y1 - 8)], hx('#6A4024') + (255,), 1.6),
             ('line', [(x - w / 2, y0 + 14), (x + w / 2, y0 + 18)], hx('#5A3A22') + (255,), 3)]
    shp(cv, rect(x - w / 2, y0, x + w / 2, y1), S_(col, '#6A4226'), LW * 0.8, 5, inner)


def jar(cv, x, y, s=1.0, col='#A0582E'):
    """Chum sành: thân phình, miệng, vân, vết sứt."""
    pts = cr([(x - 26 * s, y), (x - 44 * s, y - 40 * s), (x - 38 * s, y - 78 * s), (x - 22 * s, y - 92 * s),
              (x + 22 * s, y - 92 * s), (x + 38 * s, y - 78 * s), (x + 44 * s, y - 40 * s), (x + 26 * s, y)], n=6)
    inner = [('line', cr([(x - 42 * s, y - 52 * s), (x, y - 46 * s), (x + 42 * s, y - 52 * s)], closed=False, n=6),
              hx('#7A3E1E') + (255,), 2.4),
             ('line', cr([(x - 40 * s, y - 34 * s), (x, y - 28 * s), (x + 40 * s, y - 34 * s)], closed=False, n=6),
              hx('#7A3E1E') + (255,), 2.0),
             ('poly', [(x - 30 * s, y - 80 * s), (x - 24 * s, y - 84 * s), (x - 20 * s, y - 50 * s), (x - 26 * s, y - 48 * s)],
              hx('#C98250') + (255,))]
    shp(cv, pts, S_(col, '#7E3F1E'), LW, 8, inner)
    shp(cv, cr([(x - 26 * s, y - 92 * s), (x - 24 * s, y - 102 * s), (x + 24 * s, y - 102 * s), (x + 26 * s, y - 92 * s)],
               n=4), S_('#8A4824'), LW, 3)
    shp(cv, cc.ellipse_pts(x, y - 102 * s, 22 * s, 6 * s, 24), S_('#3A221A'), LW * 0.7, 0)


def basket(cv, x, y, s=1.0):
    """Rổ tre đan nghiêng."""
    pts = cc.ellipse_pts(x, y, 46 * s, 40 * s, 40)
    inner = []
    for k in range(-5, 6):
        inner.append(('line', [(x + k * 9 * s - 40 * s, y - 40 * s), (x + k * 9 * s + 40 * s, y + 40 * s)],
                      hx('#A8803E') + (255,), 1.6))
        inner.append(('line', [(x + k * 9 * s + 40 * s, y - 40 * s), (x + k * 9 * s - 40 * s, y + 40 * s)],
                      hx('#A8803E') + (255,), 1.6))
    shp(cv, pts, S_('#D8B068', '#B88E48'), LW, 6, inner)
    shp(cv, cc.ellipse_pts(x, y, 30 * s, 26 * s, 30), S_('#C49A54', '#A8803E'), 0, 0)


def rope_coil(cv, x, y, s=1.0):
    for k in range(4):
        r = (24 - k * 5) * s
        ImageDraw.Draw(cv).ellipse([(x - r) * SS, (y - r * 0.42) * SS, (x + r) * SS, (y + r * 0.42) * SS],
                                   outline=hx('#C9A464') + (255,), width=int(5 * s * SS))
        ImageDraw.Draw(cv).ellipse([(x - r - 2) * SS, (y - r * 0.42 - 2) * SS, (x + r + 2) * SS, (y + r * 0.42 + 2) * SS],
                                   outline=INK + (255,), width=int(1.4 * SS))


def leaf(cv, a, b, w, col, mid_col=None):
    """Lá thon từ a → b."""
    stroke(cv, [a, ((a[0] + b[0]) / 2 + (b[1] - a[1]) * 0.08, (a[1] + b[1]) / 2 - (b[0] - a[0]) * 0.08), b],
           w * 0.4, 0.5, INK, mid=w + 3)
    stroke(cv, [a, ((a[0] + b[0]) / 2 + (b[1] - a[1]) * 0.08, (a[1] + b[1]) / 2 - (b[0] - a[0]) * 0.08), b],
           w * 0.3, 0.3, hx(col), mid=w)
    if mid_col:
        stroke(cv, [a, b], 1.4, 0.4, hx(mid_col))


def bamboo(cv, x, y0, h_, rng, lean=0.0, w=15):
    top = (x + lean * h_, y0 - h_)
    stroke(cv, [(x, y0), top], w + 5, w * 0.6 + 4, INK)
    stroke(cv, [(x, y0), top], w, w * 0.6, hx('#9BC45A'))
    stroke(cv, [(x - w * 0.2, y0), (top[0] - w * 0.15, top[1])], w * 0.25, w * 0.15, hx('#C3E07E'))
    n = int(h_ / 70)
    for j in range(1, n):
        u = j / n
        px, py = x + (top[0] - x) * u, y0 + (top[1] - y0) * u
        ww = w * (1 - 0.4 * u)
        stroke(cv, [(px - ww / 2 - 2, py), (px + ww / 2 + 2, py)], 3, 3, hx('#5E8A34'))
        if j > n * 0.3:   # cành + chùm lá rủ xuống
            for sg in ((1, -1) if rng.random() < 0.5 else (1 if rng.random() < 0.5 else -1,)):
                ex, ey = px + sg * rng.uniform(40, 80), py - rng.uniform(5, 25)
                stroke(cv, [(px, py), (ex, ey)], 3.5, 1.8, hx('#6E9A3E'))
                for k in range(7):
                    ang = rng.uniform(0.25, 1.25)
                    ln = rng.uniform(40, 62)
                    leaf(cv, (ex, ey), (ex + sg * math.cos(ang) * ln, ey + math.sin(ang) * ln * 0.75),
                         rng.uniform(11, 15), rng.choice(['#6FB34A', '#86C85A', '#5DA040', '#9AD266']), '#4E8A30')


def banana(cv, x, y, rng):
    stroke(cv, [(x, y), (x + 6, y - 260)], 40, 30, INK)
    stroke(cv, [(x, y), (x + 6, y - 260)], 34, 24, hx('#9BB65A'))
    for k in range(5):
        yy = y - 40 - k * 45
        line(cv, [(x - 12, yy), (x + 16, yy - 6)], '#7A9446', 2)
    for ang, ln, tear in ((-150, 230, 2), (-115, 250, 3), (-70, 240, 2), (-30, 220, 3), (-95, 170, 0)):
        a = math.radians(ang)
        a0 = (x + 6, y - 250)
        b = (a0[0] + math.cos(a) * ln, a0[1] + math.sin(a) * ln * 0.55 + 40)
        mid = ((a0[0] + b[0]) / 2, (a0[1] + b[1]) / 2 - 30)
        pts = cr([a0, (mid[0] - 30 * math.sin(a), mid[1] - 34), b, (mid[0] + 30 * math.sin(a), mid[1] + 30)], n=8)
        inner = [('line', cr([a0, mid, b], closed=False, n=8), hx('#C6E08A') + (255,), 3)]
        for t_ in range(tear):   # vết rách lá
            u = 0.35 + 0.2 * t_
            p = (a0[0] + (b[0] - a0[0]) * u, a0[1] + (b[1] - a0[1]) * u)
            inner.append(('line', [p, (p[0] + 20, p[1] + 34)], hx('#4E8A30') + (255,), 2.2))
        shp(cv, pts, S_(rng.choice(['#5FAE45', '#6CBA4E']), '#4A8E36'), LW, 8, inner)


def reeds(cv, x0, x1, y, rng, n=30):
    for i in range(n):
        x = rng.uniform(x0, x1)
        h_ = rng.uniform(50, 120)
        lean = rng.uniform(-0.3, 0.3)
        stroke(cv, [(x, y), (x + lean * h_ * 0.5, y - h_ * 0.6), (x + lean * h_, y - h_)], 4.5, 0.8, INK)
        stroke(cv, [(x, y), (x + lean * h_ * 0.5, y - h_ * 0.6), (x + lean * h_, y - h_)], 3, 0.5,
               hx(rng.choice(['#8DB850', '#A3C862', '#7AA844'])))
        if rng.random() < 0.3:   # bông lau
            tx, ty = x + lean * h_, y - h_
            stroke(cv, [(tx, ty), (tx + lean * 20, ty - 26)], 7, 2, hx('#E8DCC0'))


def tufts(cv, x0, x1, y0, y1, rng, n=60):
    for i in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        for k in (-1, 0, 1):
            stroke(cv, [(x, y), (x + k * 6, y - rng.uniform(10, 18))], 3, 0.5, hx('#5FA43E'))


def pebbles(cv, x0, x1, y0, y1, rng, n=24):
    for i in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(4, 10)
        shp(cv, cc.ellipse_pts(x, y, r, r * 0.6, 14), S_(rng.choice(['#C8BBA2', '#B5A88E', '#D6CAB2'])), 1.6, 2)


def hut(cv, rng):
    """Nhà tranh sàn bên trái: cột, sàn, vách tre đan, cửa, rèm, mái tranh, đèn lồng, lưới, thang."""
    for x in (40, 180, 320, 400):
        post(cv, x, 520, 800, 20)
    stroke(cv, [(40, 600), (180, 660)], 7, 7, INK)        # giằng chéo
    stroke(cv, [(40, 600), (180, 660)], 4, 4, hx('#7A4C2A'))
    for i, x in enumerate(range(-20, 440, 46)):        # sàn
        plank(cv, x, 520, x + 46, 548, rng, '#B07A46')
    # vách tre đan
    wall = rect(-10, 300, 400, 522)
    inner = []
    for x in range(-10, 400, 16):
        inner.append(('line', [(x, 300), (x + 2, 522)], hx('#B89656') + (255,), 2))
    for y in range(312, 522, 22):
        inner.append(('line', [(-10, y), (400, y + 2)], hx('#C9A866') + (255,), 1.4))
    for y in (340, 470):
        inner.append(('poly', rect(-10, y, 400, y + 9), hx('#8E6A34') + (255,)))
    inner.append(('poly', [(250, 330), (300, 335), (296, 380), (262, 370)], hx('#C7A462') + (255,)))   # miếng vá
    inner.append(('line', [(258, 334), (292, 372)], hx('#8E6A34') + (255,), 1.6))
    shp(cv, wall, S_('#DDBE7E', '#C4A262'), LW, 10, inner)
    # cửa + rèm
    shp(cv, rect(130, 360, 240, 522), S_('#3A2A24', '#2A1E1A'), LW, 0,
        [('poly', rect(130, 360, 240, 380), hx('#523A30') + (255,))])
    curtain = [(132, 380), (184, 380), (180, 420), (172, 470), (176, 500), (160, 506), (146, 498), (132, 504)]
    shp(cv, curtain, S_('#B3362A', '#8E2620'), LW * 0.8, 5,
        [('line', [(146, 384), (144, 496)], hx('#8E2620') + (255,), 2), ('line', [(162, 384), (158, 500)], hx('#8E2620') + (255,), 2)])
    stroke(cv, [(126, 380), (246, 380)], 6, 6, INK)        # sào treo rèm
    stroke(cv, [(126, 380), (246, 380)], 3, 3, hx('#8A6430'))
    # cửa sổ có chấn song
    shp(cv, rect(290, 400, 370, 460), S_('#3A2A24'), LW, 0,
        [('poly', rect(292 + k * 20, 400, 298 + k * 20, 460), hx('#B89656') + (255,)) for k in range(4)])
    # lưới đánh cá phơi trên vách
    for i in range(10):
        line(cv, [(20 + i * 10, 330), (60 + i * 10, 500)], (60, 70, 80, 200), 1.4)
        line(cv, [(130 - i * 10, 330), (30 - i * 10 + 60, 500)], (60, 70, 80, 200), 1.4)
    line(cv, [(14, 330), (140, 330)], '#5A3A22', 4)
    # mái tranh
    roof = cr([(-60, 330), (40, 250), (210, 160), (380, 250), (480, 330), (440, 344), (210, 300), (-30, 344)], n=6)
    inner = []
    for k in range(140):
        u = rng.uniform(0, 1)
        x = -50 + u * 520
        ytop = 160 + abs(x - 210) * 0.55 + 10
        ybot = 330 + rng.uniform(-6, 8)
        if ytop > ybot - 20:
            continue
        y = rng.uniform(ytop, ybot - 20)
        inner.append(('line', [(x, y), (x + (x - 210) * 0.04, y + rng.uniform(18, 36))],
                      (hx('#A0783A') if rng.random() < 0.6 else hx('#E2C27A')) + (255,), 1.8))
    for k in range(-60, 480, 14):   # mép tranh lởm chởm
        inner.append(('line', [(k, 334), (k + 4, 346)], hx('#8A6430') + (255,), 2.4))
    shp(cv, roof, S_('#CDA65E', '#A88440'), LW, 12, inner)
    stroke(cv, [(40, 250), (210, 160), (380, 250)], 9, 9, INK)
    stroke(cv, [(40, 250), (210, 160), (380, 250)], 5, 5, hx('#8A6430'))
    # đèn lồng đỏ treo hiên
    line(cv, [(452, 336), (452, 372)], '#3A2A24', 2)
    shp(cv, cr([(434, 380), (452, 370), (470, 380), (472, 404), (452, 414), (432, 404)], n=5), S_('#E0402E', '#B02A20'), LW, 5,
        [('line', [(452, 372), (452, 412)], hx('#B02A20') + (255,), 1.6), ('poly', rect(444, 370, 460, 375), hx('#F3D27A') + (255,))])
    stroke(cv, [(452, 414), (452, 436)], 3, 1, hx('#F3D27A'))
    # thang
    for x in (300, 346):
        stroke(cv, [(x, 548), (x + 30, 790)], 9, 9, INK)
        stroke(cv, [(x, 548), (x + 30, 790)], 5, 5, hx('#9A6A3A'))
    for k in range(1, 6):
        y = 548 + k * 40
        u = (y - 548) / 242
        stroke(cv, [(300 + 30 * u, y), (346 + 30 * u, y)], 7, 7, INK)
        stroke(cv, [(300 + 30 * u, y), (346 + 30 * u, y)], 4, 4, hx('#9A6A3A'))


def dock(cv, rng):
    """Cầu gỗ chìa ra sông (bên phải) + cọc cầu."""
    for x in (1290, 1400, 1510, 1620):
        post(cv, x, 700, 830, 18, '#7A4C2A')
    for i, x in enumerate(range(1260, 1700, 40)):
        plank(cv, x, 690, x + 40, 712, rng, rng.choice(['#B9844E', '#AE7A46', '#C08C56']))
    shp(cv, rect(1258, 712, 1702, 724), S_('#6A4226'), LW * 0.8, 0)
    # cột buộc thuyền + dây
    post(cv, 1680, 640, 700, 16, '#7A4C2A')
    rope_coil(cv, 1600, 684, 0.8)


def boat(cv, x, y, s=1.0):
    """Thuyền nan nhỏ neo cạnh cầu (y = mặt nước)."""
    hull = cr([(x - 120 * s, y - 34 * s), (x - 80 * s, y - 20 * s), (x + 80 * s, y - 20 * s), (x + 130 * s, y - 40 * s),
               (x + 96 * s, y + 6 * s), (x - 90 * s, y + 6 * s)], n=6)
    inner = [('line', [(x - 100 * s, y - 14 * s), (x + 110 * s, y - 16 * s)], hx('#5A3A22') + (255,), 2.4)]
    inner += [('line', [(x + k * 30 * s, y - 20 * s), (x + k * 30 * s + 4 * s, y + 4 * s)], hx('#6A4630') + (255,), 1.6)
              for k in range(-3, 4)]
    shp(cv, hull, S_('#8A5A34', '#6A4226'), LW, 6, inner)
    shp(cv, cr([(x - 40 * s, y - 20 * s), (x - 30 * s, y - 62 * s), (x + 30 * s, y - 62 * s), (x + 40 * s, y - 20 * s)], n=5),
        S_('#C9A064', '#A8803E'), LW, 5,
        [('line', [(x - 30 * s + k * 12 * s, y - 60 * s), (x - 34 * s + k * 14 * s, y - 22 * s)], hx('#A8803E') + (255,), 1.6)
         for k in range(6)])        # mui thuyền


# ---------------------------------------------------------------- dựng các lớp
L = {}


def _bake(ground, props):
    """Nướng bóng + 3 tông cho đồ vật trên nền đất. Giữ trong suốt ngoài vùng có hình."""
    lit = anhsang.noi_khoi(ground, props, TONE, U=SS, manh=0.9)
    a = np.maximum(np.asarray(ground)[..., 3], np.asarray(props)[..., 3])
    arr = np.asarray(lit).copy()
    arr[..., 3] = a
    return Image.fromarray(arr, 'RGBA')


def build():
    rng = np.random.default_rng(11)
    yy = np.arange(H * SS)[:, None] / SS
    k = np.clip(yy / 450, 0, 1)
    top, hor = np.array(hx('#7FAFCB'), np.float32), np.array(hx('#E8D9BC'), np.float32)
    sky = Image.fromarray(np.repeat((top + (hor - top) * k ** 1.3)[:, None, :], W * SS, 1).astype(np.uint8)).convert('RGBA')
    # quầng nắng
    glow = Image.new('L', sky.size, 0)
    ImageDraw.Draw(glow).ellipse([60 * SS, -160 * SS, 760 * SS, 420 * SS], fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(80 * SS))
    sky.alpha_composite(Image.merge('RGBA', [Image.new('L', sky.size, 255), Image.new('L', sky.size, 236),
                                              Image.new('L', sky.size, 190), glow]))
    for cx_, cy_, sc in ((300, 120, 0.9), (900, 80, 1.3), (1450, 150, 0.9), (1760, 70, 0.6)):
        for lw_ in (LW, 0):
            for bx, by_, r in ((cx_ - 70 * sc, cy_ + 10 * sc, 40 * sc), (cx_ - 20 * sc, cy_ - 16 * sc, 52 * sc),
                               (cx_ + 40 * sc, cy_ - 6 * sc, 48 * sc), (cx_ + 92 * sc, cy_ + 12 * sc, 36 * sc)):
                cc.shape(sky, cc.ellipse_pts(bx, by_, r, r * 0.82, 32), S_('#FFFFFF', '#F2E2D0'), lw_, 9, 0, light=False)
    # chim xa
    for bx, by_ in ((620, 200), (650, 215), (1180, 140)):
        stroke(sky, [(bx - 10, by_ - 4), (bx, by_), (bx + 10, by_ - 4)], 2.4, 2.4, hx('#4A4048'))
    # núi đá vôi xa (3 lớp, càng xa càng nhạt)
    for col, base, hh, step in ((hx('#AEC4C4'), 452, 230, 170), (hx('#8AAEA6'), 454, 150, 130), (hx('#6A9480'), 456, 80, 90)):
        x = -80.0
        while x < W + 80:
            wd = rng.uniform(step * 0.8, step * 1.6)
            ht = rng.uniform(0.5, 1.0) * hh
            pts = cr([(x, base), (x + wd * 0.18, base - ht * 0.9), (x + wd * 0.38, base - ht), (x + wd * 0.62, base - ht * 0.94),
                      (x + wd * 0.82, base - ht * 0.6), (x + wd, base)], n=7)
            ImageDraw.Draw(sky).polygon([(a * SS, b * SS) for a, b in pts], fill=col + (255,))
            # sườn khuất nắng
            sh = [(x + wd * 0.38, base - ht), (x + wd * 0.62, base - ht * 0.94), (x + wd * 0.82, base - ht * 0.6), (x + wd, base),
                  (x + wd * 0.5, base)]
            ImageDraw.Draw(sky).polygon([(a * SS, b * SS) for a, b in sh], fill=mix(col, hx('#3A4A6A'), 0.14) + (255,))
            x += wd * 0.6
    # bờ xa: dải cây + nhà nhỏ
    ImageDraw.Draw(sky).rectangle([0, 438 * SS, W * SS, 456 * SS], fill=hx('#5E9E5A') + (255,))
    for i in range(60):
        x = rng.uniform(0, W)
        r = rng.uniform(8, 18)
        ImageDraw.Draw(sky).ellipse([(x - r) * SS, (440 - r * 1.4) * SS, (x + r) * SS, 446 * SS], fill=hx('#4E8C4E') + (255,))
    for x in (1040, 1090):
        ImageDraw.Draw(sky).polygon([(x * SS, 432 * SS), ((x + 18) * SS, 418 * SS), ((x + 36) * SS, 432 * SS)], fill=hx('#9A7A4A') + (255,))
        ImageDraw.Draw(sky).rectangle([(x + 6) * SS, 432 * SS, (x + 30) * SS, 444 * SS], fill=hx('#C9A870') + (255,))
    L['sky'] = sky
    # lòng sông
    mud = Image.new('RGBA', sky.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(mud)
    d.rectangle([0, 455 * SS, W * SS, 830 * SS], fill=hx('#C3A273') + (255,))
    for i in range(110):
        x, y = rng.uniform(0, W), rng.uniform(560, 820)
        r = rng.uniform(5, 20)
        d.ellipse([(x - r) * SS, (y - r * 0.32) * SS, (x + r) * SS, (y + r * 0.32) * SS], fill=hx(rng.choice(['#B08D60', '#D0B080'])) + (255,))
    for i in range(14):   # vỏ ốc, đá
        x, y = rng.uniform(450, 1250), rng.uniform(640, 800)
        cc.shape(mud, cc.ellipse_pts(x, y, 7, 4, 12), S_('#E8DCC4'), 1.4, 0, 0, light=False)
    L['mud'] = mud
    # cầu gỗ
    mid = Image.new('RGBA', sky.size, (0, 0, 0, 0))
    dock(mid, rng)
    L['mid'] = _bake(Image.new('RGBA', sky.size, (0, 0, 0, 0)), mid)
    # bờ gần
    ground = Image.new('RGBA', sky.size, (0, 0, 0, 0))
    bank = cr([(-20, 780), (420, 766), (980, 786), (1460, 762), (1960, 778), (1960, 1100), (-20, 1100)], n=8)
    shp(ground, bank, S_('#88AE5E', '#75994E'), LW, 10,
        [('poly', cr([(520, 1100), (720, 880), (1180, 860), (1480, 1100)], n=8), hx('#D6C094') + (255,)),
         ('poly', cr([(640, 1100), (800, 900), (1100, 890), (1340, 1100)], n=8), hx('#DFCDA2') + (255,))])
    for x0 in range(-20, 1960, 26):   # mép bờ đất lộ
        y = 780 - 14 * math.sin(x0 / 160) + 4
        stroke(ground, [(x0, y), (x0 + 14, y + 16)], 3, 1, hx('#6E9E44'))
    tufts(ground, 0, 520, 820, 1060, rng, 50)
    tufts(ground, 1480, 1920, 820, 1060, rng, 50)
    pebbles(ground, 700, 1260, 900, 1060, rng, 26)
    for i in range(14):   # hoa dại
        x, y = rng.uniform(40, 520) if i % 2 else rng.uniform(1460, 1880), rng.uniform(860, 1040)
        for k in range(5):
            a = k * 2 * math.pi / 5
            r = 5
            ImageDraw.Draw(ground).ellipse([(x + math.cos(a) * 6 - r) * SS, (y + math.sin(a) * 6 - r) * SS,
                                            (x + math.cos(a) * 6 + r) * SS, (y + math.sin(a) * 6 + r) * SS],
                                           fill=hx(rng.choice(['#FFF4F0', '#FFD6E0', '#FFE68A'])) + (255,))
        ImageDraw.Draw(ground).ellipse([(x - 3) * SS, (y - 3) * SS, (x + 3) * SS, (y + 3) * SS], fill=hx('#F2A23A') + (255,))
    props = Image.new('RGBA', sky.size, (0, 0, 0, 0))
    reeds(props, 440, 1240, 790, rng, 34)
    hut(props, rng)
    jar(props, 80, 860, 1.1)
    jar(props, 180, 878, 0.85, '#8E4E2A')
    basket(props, 470, 840, 0.9)
    rope_coil(props, 560, 900, 1.0)
    for x, h_, ln in ((1700, 760, -0.05), (1760, 820, 0.02), (1830, 700, 0.06), (1890, 780, -0.02)):
        bamboo(props, x, 860, h_, rng, ln, 17)
    banana(props, 1560, 900, rng)
    reeds(props, 1460, 1700, 800, rng, 18)
    jar(props, 1460, 930, 0.9, '#9A5A30')
    L['fg'] = _bake(ground, props)
    return L


def water(cv, level, t, bottom=830):
    """Nước từ y=level (bờ xa) tới y=bottom (mép nước phía gần; triều rút → bottom nhỏ lại, lộ bùn phía gần)."""
    d = ImageDraw.Draw(cv)
    yy0 = int(level * SS)
    h_ = int(bottom * SS) - yy0
    if h_ > 0:
        g = np.linspace(0, 1, h_)[:, None]
        c0, c1 = np.array(hx('#5BA8B4'), np.float32), np.array(hx('#3A7488'), np.float32)
        col = (c0 + (c1 - c0) * g ** 0.8)
        arr = np.repeat(col[:, None, :], W * SS, 1).astype(np.uint8)
        a = np.full(arr.shape[:2] + (1,), 255, np.uint8)
        cv.alpha_composite(Image.fromarray(np.concatenate([arr, a], 2), 'RGBA'), (0, yy0))
    d.rectangle([0, level * SS, W * SS, (level + 6) * SS], fill=hx('#A8D2D6') + (255,))
    rng = np.random.default_rng(3)
    for i in range(46):
        y = rng.uniform(level + 16, 815)
        if y > bottom - 10:
            continue
        x = (rng.uniform(0, W) + t * 26 * (0.5 + (i % 3) * 0.3)) % (W + 200) - 100
        ln = rng.uniform(18, 56)
        d.line([((x - ln) * SS, y * SS), ((x + ln) * SS, y * SS)], fill=hx('#8CC0C8') + (255,), width=int(2.6 * SS))
    # vệt nắng lấp lánh (phía nguồn sáng – trái)
    for i in range(18):
        x = 200 + rng.uniform(0, 500)
        y = rng.uniform(level + 10, min(level + 140, 810))
        if y > bottom - 10:
            continue
        ln = rng.uniform(8, 26) * (0.6 + 0.4 * math.sin(t * 4 + i))
        d.line([((x - ln) * SS, y * SS), ((x + ln) * SS, y * SS)], fill=(255, 250, 220, 255), width=int(3 * SS))
    if bottom < 820:   # mép nước ướt + bọt
        d.rectangle([0, (bottom - 2) * SS, W * SS, (bottom + 10) * SS], fill=hx('#9A7A50') + (255,))
        d.line([(0, bottom * SS), (W * SS, bottom * SS)], fill=hx('#D8EEEE') + (255,), width=int(3 * SS))
