"""Bộ hiệu ứng + đạo cụ theo sổ tay docs/plan/hoc-phong-cach-sitcom-vn.md mục 7 (N1–N14).
Mọi toạ độ là toạ độ khung 1600x900; canvas vẽ ở cỡ SS lần (RGBA).

Hiệu ứng toàn khung:  tint_night (N1)  dusk (N11)  rain (N11)  letterbox (N5)
Đạo cụ / nền:         crack, tile_floor (N3)  crowd (N6)  coconut, cau_tre (N7)  insert_stake (N8)
Đợt 3 (N15–N29): layers_far, snow_cap, snow_ground, sunset_sky, sun_rays, underwater, tint_warm_night, window_beam,
                     spotlight, tv_frame, smoke, symbol_card, black_eye, bamboo, bamboo_grove, bush_row, lattice_door,
                     tet_calendar, mai_bonsai, tea_set, wood_bench
Chạy demo: python scripts/hoathinh/sitcom_fx.py [--dot3] → build/thu-hoathinh/sitcom-fx/bang-hieu-ung[-3].jpg
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, ellipse_pts  # noqa: E402
from gau_nghe_avatar_tbm import poly, pline  # noqa: E402

W, H = 1600, 900


# ------------------------------------------------------------------ hiệu ứng toàn khung
def _grade(cv, mul, add):
    a = np.asarray(cv).astype(np.float32)
    a[..., :3] = a[..., :3] * np.array(mul, np.float32) + np.array(add, np.float32)
    cv.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def tint_night(cv, windows=None, moon=(1340, 120), stars=40, seed=1):
    """N1: ĐỔI bảng màu sang xanh dương (không chỉ làm tối); viền đen giữ nguyên.
    windows = màu (hex) của ô cửa sổ trong cảnh → ~35% ô được thắp vàng."""
    lit = None
    if windows:
        a = np.asarray(cv)[..., :3].astype(int)
        m = np.abs(a - np.array(hx(windows))).sum(-1) < 10
        m[int(560 * SS):] = False
        lab, n = ndimage.label(m)
        rnd = np.random.RandomState(seed)
        pick = np.where(rnd.rand(n + 1) < 0.35)[0]
        lit = np.isin(lab, pick[pick > 0])
    _grade(cv, (0.24, 0.32, 0.58), (6, 10, 34))
    if lit is not None:
        a = np.asarray(cv).copy()
        a[lit, :3] = hx('#F3D27A')
        cv.paste(Image.fromarray(a, 'RGBA'))
    d = ImageDraw.Draw(cv)
    rnd = np.random.RandomState(seed + 7)
    for _ in range(stars):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 260)
        r = rnd.uniform(1.2, 2.6)
        a = np.asarray(cv)[int(y * SS), int(x * SS)]
        if a[2] > a[0] + 30 and a[:3].sum() < 400:      # chỉ đặt sao lên trời
            d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=(240, 244, 255, 255))
    if moon:
        x, y = moon
        a = np.asarray(cv)[int(y * SS), int(x * SS)]
        if a[2] > a[0] + 30:
            d.ellipse([(x - 46) * SS, (y - 46) * SS, (x + 46) * SS, (y + 46) * SS], fill=(246, 246, 236, 255),
                      outline=INK + (255,), width=int(2.4 * SS))


def dusk(cv):
    """N11: hoàng hôn cam-tím."""
    _grade(cv, (0.92, 0.70, 0.74), (14, 0, 20))


def rain(cv, n=260, seed=2, ang=0.32):
    """N11: mưa = nét chéo trắng mảnh + cả khung ám xanh xám."""
    _grade(cv, (0.70, 0.78, 0.86), (10, 14, 22))
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rnd = np.random.RandomState(seed)
    for _ in range(n):
        x, y = rnd.uniform(-100, W), rnd.uniform(-60, H)
        L = rnd.uniform(24, 60)
        d.line([(x * SS, y * SS), ((x + L * ang) * SS, (y + L) * SS)], fill=(235, 242, 250, 150), width=int(1.6 * SS))
    cv.alpha_composite(lay)


def letterbox(cv, ratio=2.35):
    """N5: viền đen điện ảnh cho cảnh trận / cao trào."""
    h = (H - W / ratio) / 2
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 0, W * SS, h * SS], fill=(12, 10, 10, 255))
    d.rectangle([0, (H - h) * SS, W * SS, H * SS], fill=(12, 10, 10, 255))


# ------------------------------------------------------------------ đạo cụ / nền
def crack(d, x, y, L=70, seed=0, ang=1.2):
    """N3: vết nứt tường – nét đen mảnh gấp khúc + 1 nhánh."""
    rnd = np.random.RandomState(seed)
    pts = [(x, y)]
    for i in range(6):
        a = ang + rnd.uniform(-0.6, 0.6)
        x, y = x + L / 6 * math.cos(a), y + L / 6 * math.sin(a)
        pts.append((x, y))
    pline(d, pts, INK, 1.8)
    bx, by = pts[3]
    pline(d, [(bx, by), (bx + 14, by + 6), (bx + 22, by + 4)], INK, 1.6)


def tile_floor(d, y0, y1, vx, col='#7E8A8C', line='#5E6A6C', n=12, rows=(0.12, 0.3, 0.55)):
    """N3: sàn gạch ô vuông phối cảnh, điểm tụ (vx, y0 - 400)."""
    poly(d, [(-20, y0), (W + 20, y0), (W + 20, y1 + 20), (-20, y1 + 20)], col, w=2.6)
    vy = y0 - 420
    for k in range(-n, 2 * n):
        x1 = k * W / n
        t = (y0 - vy) / (y1 - vy)
        x0 = vx + (x1 - vx) * t
        pline(d, [(x0, y0), (x1, y1)], line, 1.8)
    for r in rows:
        y = y0 + (y1 - y0) * r
        pline(d, [(-20, y), (W + 20, y)], line, 1.8)


def crowd(cv, x0, x1, y0, y1, n=70, col='#6E6880', seed=3, front=()):
    """N6: đám đông = bóng người một màu (đầu tròn + vai), xa nhỏ gần to; vài người trước (front) màu riêng."""
    rnd = np.random.RandomState(seed)
    ppl = sorted([(rnd.uniform(y0, y1), rnd.uniform(x0, x1)) for _ in range(n)])
    d = ImageDraw.Draw(cv)
    for i, (y, x) in enumerate(ppl):
        k = 0.9 + 1.4 * (y - y0) / max(1, y1 - y0)
        c = col
        if i >= n - len(front):
            c = front[i - (n - len(front))]
        sh = [(x - 30 * k, y + 40 * k), (x - 24 * k, y + 6 * k), (x, y), (x + 24 * k, y + 6 * k), (x + 30 * k, y + 40 * k)]
        poly(d, sh, c, w=2.0 * k)
        d.ellipse([(x - 15 * k) * SS, (y - 30 * k) * SS, (x + 15 * k) * SS, (y + 2 * k) * SS], fill=hx(c) + (255,),
                  outline=INK + (255,), width=int(2.0 * k * SS))
        if rnd.rand() < 0.3:                 # nón lá
            poly(d, [(x - 24 * k, y - 18 * k), (x, y - 40 * k), (x + 24 * k, y - 18 * k)], '#D9C38A', w=1.8 * k)


def coconut(d, x, base, h=300, lean=40, seed=0):
    """N7: cây dừa – thân cong có đốt + tán lá xòe."""
    rnd = np.random.RandomState(seed)
    pts = [(x + lean * (t ** 2), base - h * t) for t in np.linspace(0, 1, 12)]
    left = [(px - 10 + 3 * t, py) for (px, py), t in zip(pts, np.linspace(0, 1, 12))]
    right = [(px + 10 - 3 * t, py) for (px, py), t in zip(pts, np.linspace(0, 1, 12))]
    poly(d, left + right[::-1], '#9A7A52', w=2.4)
    for px, py in pts[1:-1:2]:
        pline(d, [(px - 8, py), (px + 8, py - 3)], '#6E5434', 1.8)
    tx, ty = pts[-1]
    for a in np.linspace(-2.9, -0.25, 7):
        L = rnd.uniform(110, 150)
        ex, ey = tx + L * math.cos(a), ty + L * math.sin(a) + 70
        mx, my = tx + L * 0.5 * math.cos(a), ty + L * 0.5 * math.sin(a) - 10
        poly(d, [(tx, ty), (mx, my - 14), (ex, ey), (mx, my + 10)], '#6FA14C', ol='#3F6B2C', w=2.2)
    for j in range(3):
        d.ellipse([(tx - 14 + j * 10) * SS, (ty + 4) * SS, (tx - 2 + j * 10) * SS, (ty + 18) * SS],
                  fill=hx('#7E8A3A') + (255,), outline=INK + (255,), width=int(1.6 * SS))


def cau_tre(d, x0, x1, y, h=120):
    """N7: cầu khỉ – một cây tre ngang + tay vịn + chân chéo."""
    pline(d, [(x0, y), (x1, y)], '#B8A060', 9)
    pline(d, [(x0, y - 4), (x1, y - 4)], '#D6C07A', 3)
    pline(d, [(x0, y - h * 0.7), (x1, y - h * 0.7)], '#B8A060', 5)
    for k in np.linspace(x0 + 30, x1 - 30, 4):
        pline(d, [(k - 30, y + h), (k + 30, y - h * 0.75)], '#9A8550', 6)
        pline(d, [(k + 30, y + h), (k - 30, y - h * 0.75)], '#9A8550', 6)


def insert_stake(cv, bg='#C9B98A', oy=130):
    """N8: cỡ cảnh 'insert' – một cọc gỗ vót nhọn bịt sắt lấp đầy khung, nền phẳng."""
    ImageDraw.Draw(cv).rectangle([0, 0, W * SS, H * SS], fill=hx(bg) + (255,))
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for y in (260, 420, 600, 760):                                 # vân nền mờ
        pline(d, [(0, y), (W, y - 40)], '#B9A97C', 3)
    cx = 820
    body = [(cx - 120, 900), (cx - 104, 330), (cx + 104, 330), (cx + 120, 900)]
    poly(d, body, '#A8714A', w=5)
    poly(d, [(cx + 30, 900), (cx + 34, 330), (cx + 104, 330), (cx + 120, 900)], '#8A5A3A', ol=None)
    for yy in (430, 560, 700, 820):                                 # thớ gỗ
        pline(d, [(cx - 90, yy), (cx - 20, yy + 12), (cx + 40, yy - 4)], '#7A4E30', 3)
    poly(d, [(cx - 104, 330), (cx + 104, 330), (cx + 70, 230), (cx - 70, 230)], '#B07A50', w=5)   # phần vót
    poly(d, [(cx - 70, 230), (cx + 70, 230), (cx, 40)], '#6E747A', w=5)                           # mũi bịt sắt
    poly(d, [(cx, 40), (cx + 70, 230), (cx + 20, 230)], '#4E545A', ol=None)
    pline(d, [(cx - 70, 230), (cx, 40), (cx + 70, 230)], INK, 5)
    for yy in (250, 290):                                            # đai sắt
        poly(d, [(cx - 92, yy), (cx + 92, yy), (cx + 96, yy + 18), (cx - 96, yy + 18)], '#5E646A', w=4)
        for nx in (cx - 60, cx, cx + 60):
            d.ellipse([(nx - 5) * SS, (yy + 4) * SS, (nx + 5) * SS, (yy + 14) * SS], fill=hx('#C8CDD2') + (255,))
    d.ellipse([(cx - 26) * SS, 70 * SS, (cx - 14) * SS, 150 * SS], fill=(230, 236, 240, 200))       # loé sáng mũi sắt
    cv.alpha_composite(lay.transform(lay.size, Image.AFFINE, (1, 0, 0, 0, 1, -oy * SS)))


# ------------------------------------------------------------------ đợt 3 (sổ tay mục 8: N15–N29)
def _mix(c1, c2, t):
    a, b = hx(c1), hx(c2)
    return '#%02X%02X%02X' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _mask_mul(cv, mask, mul, add=(0, 0, 0)):
    """Nhân màu (mép cứng) chỉ trong mặt nạ bool."""
    a = np.asarray(cv).astype(np.float32)
    a[mask, :3] = a[mask, :3] * np.array(mul, np.float32) + np.array(add, np.float32)
    cv.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'))


def _poly_mask(cv, pts):
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    return np.asarray(m) > 0


def layers_far(d, y, n=4, base='#4E6A7C', sky='#DCE6E8', amp=90, step=46, seed=0, x0=-20, x1=W + 20, bottom=None):
    """N15: núi/đồi xa = n lớp phẳng, lớp xa nhạt & gần màu trời, viền mảnh (không sương mờ, không blur).
    Lớp xa nhất ở y, mỗi lớp gần hơn thấp xuống `step` px."""
    rnd = np.random.RandomState(seed)
    for i in range(n):
        t = (i + 1) / (n + 0.6)
        col = _mix(sky, base, t)
        yb = y + i * step
        ph = rnd.uniform(0, 6.3, 3)
        fr = rnd.uniform(0.6, 1.4, 3)
        xs = np.linspace(x0, x1, 60)
        a = amp * (1.1 - 0.18 * i)
        ridge = [(x, yb - a * (0.55 + 0.25 * math.sin(x / 210 * fr[0] + ph[0]) + 0.15 * math.sin(x / 90 * fr[1] + ph[1])
                                + 0.08 * math.sin(x / 41 * fr[2] + ph[2]))) for x in xs]
        bot = bottom if bottom is not None else yb + step + 40
        poly(d, ridge + [(x1, bot), (x0, bot)], col, ol=_mix(col, '#14110F', 0.35), w=1.6)


def snow_cap(d, top, th=16, seed=0):
    """N16: 'mũ tuyết' phủ lên mép trên của vật (top = các điểm mép trên, trái→phải); mép dưới gợn."""
    rnd = np.random.RandomState(seed)
    lower = [(x, y + th * rnd.uniform(0.6, 1.3)) for (x, y) in top[::-1]]
    up = [(x, y - th * 0.45) for x, y in top]
    poly(d, up + lower, '#F6F8FA', w=2.2)
    pline(d, [(x, y + th * 0.2) for x, y in top[1:-1]], '#C2CEDA', 2.2)


def snow_ground(d, y0, seed=0):
    """N16: nền tuyết trắng + vài mảng bóng xanh xám mép cứng."""
    poly(d, [(-20, y0), (W + 20, y0 - 10), (W + 20, H + 20), (-20, H + 20)], '#F4F6F8', w=2.4)
    rnd = np.random.RandomState(seed)
    for _ in range(5):
        cx, cy = rnd.uniform(80, W - 80), rnd.uniform(y0 + 40, H - 30)
        rw, rh = rnd.uniform(90, 220), rnd.uniform(14, 30)
        poly(d, ellipse_pts(cx, cy, rw, rh, n=30), '#D4DEE8', ol='#B8C6D4', w=1.6)


def sunset_sky(d, y1=520):
    """N17: trời hoàng hôn = 3 dải màu phẳng (cam → hồng → vàng nhạt), không gradient."""
    for (a, b, c) in ((0, 0.4, '#E9A07A'), (0.4, 0.75, '#F2B98A'), (0.75, 1.01, '#F6D6A0')):
        poly(d, [(-20, y1 * a), (W + 20, y1 * a), (W + 20, y1 * b + 1), (-20, y1 * b + 1)], c, ol=None)


def sun_rays(cv, x, y, n=9, r=70, col=(255, 236, 190), alpha=70, seed=0):
    """N17: mặt trời + tia chói mép cứng (tam giác mờ đều, không blur)."""
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rnd = np.random.RandomState(seed)
    for a in np.linspace(0, 2 * math.pi, n, endpoint=False) + rnd.uniform(0, 0.4):
        L, wd = rnd.uniform(900, 1400), rnd.uniform(0.05, 0.11)
        pts = [(x, y), (x + L * math.cos(a - wd), y + L * math.sin(a - wd)), (x + L * math.cos(a + wd), y + L * math.sin(a + wd))]
        d.polygon([(px * SS, py * SS) for px, py in pts], fill=col + (alpha,))
    d.ellipse([(x - r * 1.5) * SS, (y - r * 1.5) * SS, (x + r * 1.5) * SS, (y + r * 1.5) * SS], fill=col + (90,))
    cv.alpha_composite(lay)
    ImageDraw.Draw(cv).ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=(255, 248, 226, 255),
                               outline=INK + (255,), width=int(2.4 * SS))


def underwater(cv, n=40, seed=0):
    """N18: dưới nước = phủ cả khung xanh lục ngả lam + bong bóng tròn viền mảnh."""
    _grade(cv, (0.42, 0.74, 0.70), (6, 34, 40))
    d = ImageDraw.Draw(cv)
    rnd = np.random.RandomState(seed)
    for i in range(6):                                                  # vệt sáng mặt nước phía trên
        x = 120 + i * 260 + rnd.uniform(-40, 40)
        pline(d, [(x, 30 + rnd.uniform(0, 30)), (x + 90, 40 + rnd.uniform(0, 30))], '#CFF2EA', 3)
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(4, 16)
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=(190, 236, 228, 255),
                  outline=(40, 90, 90, 255), width=int(1.6 * SS))
        d.ellipse([(x - r * 0.5) * SS, (y - r * 0.6) * SS, (x - r * 0.1) * SS, (y - r * 0.2) * SS], fill=(250, 255, 255, 255))


def tint_warm_night(cv, lamp=(800, 380), r=360):
    """N19: đêm TRONG NHÀ ấm (nâu cam), quầng đèn 2 nấc mép cứng quanh đèn dầu/bàn thờ – không gradient."""
    _grade(cv, (0.46, 0.34, 0.27), (22, 10, 2))
    yy, xx = np.mgrid[0:cv.size[1], 0:cv.size[0]]
    dist = np.hypot(xx - lamp[0] * SS, yy - lamp[1] * SS)
    _mask_mul(cv, dist < 1.7 * r * SS, (1.22, 1.18, 1.08))
    _mask_mul(cv, dist < r * SS, (1.22, 1.16, 1.02), (6, 3, 0))


def window_beam(cv, pts, k=1.25):
    """N19: vệt sáng cửa sổ trên tường/sàn (hình bình hành sáng hơn, mép cứng)."""
    _mask_mul(cv, _poly_mask(cv, pts), (k, k * 0.98, k * 0.88))


def spotlight(cv, x, w0=90, w1=380, y0=0, y1=H, out=0.38):
    """N20: đèn rọi / giếng trời – nón sáng hình thang; ngoài nón tối hẳn."""
    m = _poly_mask(cv, [(x - w0, y0), (x + w0, y0), (x + w1, y1), (x - w1, y1)])
    _mask_mul(cv, ~m, (out, out, out * 1.15))
    _mask_mul(cv, m, (1.08, 1.06, 1.0), (8, 8, 6))


def tv_frame(cv, box, inner):
    """N21: khung trong khung – dán ảnh `inner` (PIL RGBA) vào màn hình TV/cửa sổ có viền."""
    x0, y0, x1, y1 = box
    im = inner.resize((int((x1 - x0) * SS), int((y1 - y0) * SS)), Image.LANCZOS)
    cv.alpha_composite(im, (int(x0 * SS), int(y0 * SS)))
    d = ImageDraw.Draw(cv)
    d.rectangle([(x0 - 14) * SS, (y0 - 14) * SS, (x1 + 14) * SS, (y1 + 14) * SS], outline=hx('#2A2A2E') + (255,), width=int(14 * SS))
    d.rectangle([(x0 - 21) * SS, (y0 - 21) * SS, (x1 + 21) * SS, (y1 + 21) * SS], outline=INK + (255,), width=int(2.6 * SS))
    pline(d, [(x0 + 20, y0 + 16), (x0 + 70, y0 + 16)], (255, 255, 255), 3)


def smoke(cv, x, y, r=60, n=7, col='#9C9CA4', seed=0, ol=True):
    """N27: khói/bụi = cụm tròn chồng nhau, xám phẳng, một viền liền ngoài, không blur."""
    rnd = np.random.RandomState(seed)
    cs = [(x + rnd.uniform(-1.2, 1.2) * r, y + rnd.uniform(-0.7, 0.5) * r, r * rnd.uniform(0.45, 0.85)) for _ in range(n)]
    d = ImageDraw.Draw(cv)
    if ol:
        w = 2.4
        for cx, cy, rr in cs:
            d.ellipse([(cx - rr - w) * SS, (cy - rr - w) * SS, (cx + rr + w) * SS, (cy + rr + w) * SS], fill=INK + (255,))
    for cx, cy, rr in cs:
        d.ellipse([(cx - rr) * SS, (cy - rr) * SS, (cx + rr) * SS, (cy + rr) * SS], fill=hx(col) + (255,))
    hl = _mix(col, '#FFFFFF', 0.35)
    for cx, cy, rr in cs[: n // 2]:
        d.ellipse([(cx - rr * 0.55) * SS, (cy - rr * 0.7) * SS, (cx + rr * 0.1) * SS, (cy - rr * 0.15) * SS], fill=hx(hl) + (255,))


def symbol_card(cv, bg='#22303C'):
    """N28: đồ họa biểu tượng chèn ngang – mặt trống đồng giản lược to giữa khung, nền trơn."""
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 0, W * SS, H * SS], fill=hx(bg) + (255,))
    cx, cy = W / 2, H / 2
    for k, c in ((300, '#C9A24A'), (240, '#B08A3A'), (180, '#C9A24A'), (110, '#B08A3A'), (60, '#F3D27A')):
        d.ellipse([(cx - k) * SS, (cy - k) * SS, (cx + k) * SS, (cy + k) * SS], fill=hx(c) + (255,),
                  outline=INK + (255,), width=int(3 * SS))
    for a in np.linspace(0, 2 * math.pi, 14, endpoint=False):           # tia sao giữa trống
        pts = [(cx + 60 * math.cos(a - 0.12), cy + 60 * math.sin(a - 0.12)), (cx + 108 * math.cos(a), cy + 108 * math.sin(a)),
               (cx + 60 * math.cos(a + 0.12), cy + 60 * math.sin(a + 0.12))]
        poly(d, pts, '#F3D27A', w=2)
    for a in np.linspace(0, 2 * math.pi, 6, endpoint=False):            # chim giản lược bay ngược chiều kim đồng hồ
        bx, by = cx + 210 * math.cos(a), cy + 210 * math.sin(a)
        t = a - math.pi / 2
        poly(d, [(bx + 26 * math.cos(t), by + 26 * math.sin(t)), (bx + 10 * math.cos(t + 2.2), by + 10 * math.sin(t + 2.2)),
                 (bx - 26 * math.cos(t), by - 26 * math.sin(t)), (bx + 10 * math.cos(t - 2.2), by + 10 * math.sin(t - 2.2))],
             '#14110F', ol='#14110F', w=1.5)


def black_eye(d, x, y, r=18):
    """N29: mắt bầm tím tròn – chi tiết hài giữ liên tục qua các cảnh."""
    d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=hx('#6A4C8C') + (255,),
              outline=INK + (255,), width=int(2 * SS))
    d.ellipse([(x - r * 0.45) * SS, (y - r * 0.45) * SS, (x + r * 0.45) * SS, (y + r * 0.45) * SS], fill=INK + (255,))


# ---- đạo cụ đợt 3
def bamboo(d, x, base, h=620, lean=0.0, wd=18, col='#8DB86A', dark='#5E8A44', seed=0):
    """N26: một cây tre – thân sọc đốt + bóng một bên + chùm lá viền ở ngọn."""
    rnd = np.random.RandomState(seed)
    tx, ty = x + lean * h, base - h
    pts = [(x + (tx - x) * t, base - h * t) for t in np.linspace(0, 1, 8)]
    L = [(px - wd / 2, py) for px, py in pts]
    R = [(px + wd / 2, py) for px, py in pts]
    poly(d, L + R[::-1], col, ol='#2E4A22', w=2.0)
    poly(d, [(px + wd * 0.15, py) for px, py in pts] + R[::-1], dark, ol=None)
    for t in np.arange(0.08, 1.0, 0.13):
        px, py = x + (tx - x) * t, base - h * t
        pline(d, [(px - wd / 2 - 2, py), (px + wd / 2 + 2, py - 2)], '#2E4A22', 2.4)
    for _ in range(4):                                                  # chùm lá
        lx, ly = tx + rnd.uniform(-60, 60), ty + rnd.uniform(-10, 90)
        for a in rnd.uniform(-2.8, -0.3, 4):
            Lf = rnd.uniform(50, 80)
            ca, sa = math.cos(a), math.sin(a)
            poly(d, [(lx, ly), (lx + Lf * 0.5 * ca - 6, ly + Lf * 0.5 * sa + 8), (lx + Lf * ca, ly + Lf * sa + 30),
                     (lx + Lf * 0.5 * ca + 6, ly + Lf * 0.5 * sa + 18)], '#7FB25C', ol='#2E4A22', w=1.6)


def bamboo_grove(d, x0, x1, base, n=9, seed=0):
    """N26: rừng tre 3 lớp: xa nhạt mảnh → gần đậm to."""
    rnd = np.random.RandomState(seed)
    for layer, (col, dark, wd, hk) in enumerate((('#B9D49A', '#9CBE7C', 10, 0.8), ('#9CC57A', '#76A256', 14, 0.95),
                                                ('#7FB25C', '#5A8A40', 22, 1.15))):
        for i in range(n // 3 + layer):
            bamboo(d, rnd.uniform(x0, x1), base + layer * 30, h=rnd.uniform(560, 720) * hk, lean=rnd.uniform(-0.08, 0.08),
                   wd=wd, col=col, dark=dark, seed=seed * 31 + layer * 7 + i)


def bush_row(d, x0, x1, y, amp=40, n=8, col='#7FB25C', seed=0):
    """Bụi cây tròn có viền ở chân cảnh (đi kèm rừng tre / nhà cổ)."""
    from gau_nghe_avatar_tbm import bumpy
    top = bumpy(x0, x1, y, amp, n, ph=seed)
    poly(d, top + [(x1, y + 80), (x0, y + 80)], col, ol='#2E4A22', w=2.2)


def lattice_door(d, x0, y0, x1, y1, wood='#7A4E30', paper='#EDE0C2', cols=4, rows=5):
    """N25: cửa bức bàn nhà cổ – khung gỗ, nửa trên song ô vuông dán giấy, nửa dưới ván kín."""
    poly(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], wood, w=3)
    ym = y0 + (y1 - y0) * 0.62
    ix0, ix1, iy0 = x0 + 14, x1 - 14, y0 + 14
    poly(d, [(ix0, iy0), (ix1, iy0), (ix1, ym - 8), (ix0, ym - 8)], paper, ol='#3E2A1E', w=2)
    for i in range(1, cols):
        x = ix0 + (ix1 - ix0) * i / cols
        pline(d, [(x, iy0), (x, ym - 8)], wood, 5)
    for j in range(1, rows):
        y = iy0 + (ym - 8 - iy0) * j / rows
        pline(d, [(ix0, y), (ix1, y)], wood, 5)
    poly(d, [(ix0, ym + 6), (ix1, ym + 6), (ix1, y1 - 14), (ix0, y1 - 14)], _mix(wood, '#000000', 0.18), ol='#3E2A1E', w=2)
    pline(d, [(ix0 + 16, ym + 30), (ix1 - 16, ym + 30)], '#5A3A24', 2)


def tet_calendar(d, x, y, k=1.0):
    """N24: lịch Tết treo tường – bìa đỏ, khối giấy trắng, số to."""
    pline(d, [(x - 30 * k, y), (x, y - 26 * k), (x + 30 * k, y)], '#14110F', 1.6)
    poly(d, [(x - 60 * k, y), (x + 60 * k, y), (x + 60 * k, y + 160 * k), (x - 60 * k, y + 160 * k)], '#B3261E', w=2.4)
    poly(d, [(x - 44 * k, y + 60 * k), (x + 44 * k, y + 60 * k), (x + 44 * k, y + 148 * k), (x - 44 * k, y + 148 * k)], '#FBF6EA', w=2)
    poly(d, ellipse_pts(x, y + 30 * k, 22 * k, 16 * k, n=24), '#F3D27A', w=1.6)
    for dy in (84, 100):
        pline(d, [(x - 18 * k, y + dy * k), (x + 18 * k, y + dy * k)], '#B3261E', 5 * k)
    pline(d, [(x - 22 * k, y + 124 * k), (x + 22 * k, y + 124 * k)], '#14110F', 2)


def mai_bonsai(d, x, base, k=1.0, seed=0):
    """N24: chậu mai Tết – chậu men xanh, cành gấp khúc, hoa vàng 5 cánh."""
    rnd = np.random.RandomState(seed)
    br = [(x, base - 70 * k), (x - 10 * k, base - 140 * k), (x + 26 * k, base - 200 * k), (x + 6 * k, base - 270 * k)]
    pline(d, br, '#14110F', 11 * k)
    pline(d, br, '#5A3E2E', 7 * k)
    tips = []
    for bx, by in br[1:]:
        for s in (-1, 1):
            ex, ey = bx + s * rnd.uniform(50, 90) * k, by - rnd.uniform(10, 50) * k
            mid = ((bx + ex) / 2, by - 20 * k)
            pline(d, [(bx, by), mid, (ex, ey)], '#14110F', 6 * k)
            pline(d, [(bx, by), mid, (ex, ey)], '#5A3E2E', 3.5 * k)
            tips += [(ex, ey), mid]
    for tx, ty in tips + [br[-1]]:
        for _ in range(3):
            fx, fy, r = tx + rnd.uniform(-16, 16) * k, ty + rnd.uniform(-14, 10) * k, 7 * k
            for a in np.linspace(0, 2 * math.pi, 5, endpoint=False):
                px, py = fx + r * math.cos(a), fy + r * math.sin(a)
                d.ellipse([(px - r * 0.7) * SS, (py - r * 0.7) * SS, (px + r * 0.7) * SS, (py + r * 0.7) * SS],
                          fill=hx('#F6C33A') + (255,), outline=INK + (255,), width=int(1.2 * SS))
            d.ellipse([(fx - 2.4) * SS, (fy - 2.4) * SS, (fx + 2.4) * SS, (fy + 2.4) * SS], fill=hx('#C8501E') + (255,))
    poly(d, [(x - 70 * k, base - 70 * k), (x + 70 * k, base - 70 * k), (x + 52 * k, base), (x - 52 * k, base)], '#3B5E8C', w=2.4)
    pline(d, [(x - 60 * k, base - 50 * k), (x + 60 * k, base - 50 * k)], '#F2E6CC', 3 * k)


def tea_set(d, x, y, k=1.0):
    """N24: khay + ấm trà + 3 chén (y = mặt bàn)."""
    poly(d, [(x - 110 * k, y - 10 * k), (x + 110 * k, y - 10 * k), (x + 96 * k, y), (x - 96 * k, y)], '#7A4E30', w=2.2)
    poly(d, [(x + 8 * k, y - 56 * k), (x + 46 * k, y - 76 * k), (x + 50 * k, y - 70 * k), (x + 12 * k, y - 46 * k)], '#E8E2D2', w=2)
    poly(d, ellipse_pts(x - 30 * k, y - 46 * k, 42 * k, 34 * k, n=30), '#E8E2D2', w=2.4)
    poly(d, ellipse_pts(x - 30 * k, y - 82 * k, 12 * k, 7 * k, n=16), '#3B5E8C', w=1.8)
    pline(d, [(x - 66 * k, y - 50 * k), (x + 6 * k, y - 50 * k)], '#3B5E8C', 3 * k)
    for cx in (40, 68, 96):
        poly(d, [(x + (cx - 12) * k, y - 30 * k), (x + (cx + 12) * k, y - 30 * k), (x + (cx + 8) * k, y - 12 * k),
                 (x + (cx - 8) * k, y - 12 * k)], '#E8E2D2', w=1.8)


def oil_lamp(d, x, y, k=1.0):
    """N19: đèn dầu (y = mặt bàn) – nguồn sáng cho cảnh đêm ấm."""
    poly(d, [(x - 22 * k, y), (x + 22 * k, y), (x + 14 * k, y - 16 * k), (x - 14 * k, y - 16 * k)], '#B08A3A', w=2)
    poly(d, ellipse_pts(x, y - 30 * k, 18 * k, 16 * k, n=24), '#C9A24A', w=2)
    poly(d, [(x - 12 * k, y - 44 * k), (x + 12 * k, y - 44 * k), (x + 16 * k, y - 96 * k), (x - 16 * k, y - 96 * k)],
         '#F6EEC8', w=2)
    poly(d, [(x, y - 52 * k), (x + 7 * k, y - 66 * k), (x, y - 84 * k), (x - 7 * k, y - 66 * k)], '#F7A23A', w=1.4)


def wood_bench(d, x0, x1, y, k=1.0):
    """N24: ghế băng / trường kỷ gỗ (y = chân ghế chạm sàn)."""
    for xx in (x0 + 14, x1 - 28):
        poly(d, [(xx, y - 150 * k), (xx + 14, y - 150 * k), (xx + 14, y), (xx, y)], '#6E4630', w=2.2)
    poly(d, [(x0 + 6, y - 150 * k), (x1 - 6, y - 150 * k), (x1 - 6, y - 128 * k), (x0 + 6, y - 128 * k)], '#8A5A3A', w=2.4)
    for xx in np.linspace(x0 + 60, x1 - 60, 4):
        pline(d, [(xx, y - 128 * k), (xx, y - 70 * k)], '#6E4630', 6 * k)
    poly(d, [(x0, y - 70 * k), (x1, y - 70 * k), (x1, y - 56 * k), (x0, y - 56 * k)], '#8A5A3A', w=2.4)


# ------------------------------------------------------------------ demo đợt 3
def demo3():
    from gau_nghe_van import Dog, ROOT
    import gau_nghe_khung_thu as K
    out = os.path.join(ROOT, 'build', 'thu-hoathinh', 'sitcom-fx')
    os.makedirs(out, exist_ok=True)
    new = lambda: Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    panels = []

    # 1. N15 núi xa nhiều lớp + sông
    c = new(); d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 620), (0, 620)], '#DCE6E8', ol=None)
    K.cloud(c, 300, 120, 0.8); K.cloud(c, 1200, 90, 0.6)
    d = ImageDraw.Draw(c)
    layers_far(d, 360, n=4, base='#3E5E70', sky='#DCE6E8', seed=2, bottom=620)
    poly(d, [(-20, 560), (W + 20, 540), (W + 20, 700), (-20, 720)], '#8EB7B8', w=2.4)
    for i in range(12):
        x = 80 + i * 130
        pline(d, [(x, 600 + (i % 3) * 22), (x + 60, 600 + (i % 3) * 22)], '#6E9A9C', 2)
    poly(d, [(-20, 700), (W + 20, 680), (W + 20, 920), (-20, 920)], '#D9C08A', w=2.6)
    Dog(c, 800, 860, 0.8, dict(mouth='smirk', gaze=(1, 0), flat=True, arms=((18, 8), (80, 122)))).draw()
    panels.append(('N15 Núi xa = nhiều lớp phẳng nhạt dần', c))

    # 2. N16 tuyết + bậc đá
    c = new(); d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 600), (0, 600)], '#BFD8EA', ol=None)
    layers_far(d, 330, n=3, base='#6E7C8A', sky='#BFD8EA', seed=5, bottom=560)
    snow_ground(d, 560, seed=3)
    for i, (x0, x1, y) in enumerate(((900, 1620, 560), (980, 1620, 640), (1060, 1620, 720))):
        poly(d, [(x0, y), (x1, y), (x1, y + 80), (x0 - 20, y + 80)], '#6E7480', w=2.6)
        pline(d, [(x0 + 20, y + 40), (x0 + 140, y + 44)], '#5A606C', 2)
        snow_cap(d, [(x, y + (4 if k % 2 else 0)) for k, x in enumerate(np.linspace(x0, x1, 10))], th=14, seed=i)
    Dog(c, 520, 840, 0.9, dict(mouth='open', gaze=(1, -0.3), flat=True, arms=((40, -20), (120, 40)))).draw()
    d = ImageDraw.Draw(c)
    poly(d, ellipse_pts(520, 846, 90, 12, n=30), '#C2CEDA', ol=None)
    panels.append(('N16 Tuyết: nền trắng, bóng xanh xám, mũ tuyết', c))

    # 3. N17 hoàng hôn + tia nắng
    c = new(); d = ImageDraw.Draw(c)
    sunset_sky(d, 560)
    sun_rays(c, 1180, 300, seed=4)
    K.cloud(c, 400, 150, 0.9)
    d = ImageDraw.Draw(c)
    _ = [poly(d, ellipse_pts(cx, cy, rw, 16, n=24), '#8E9AB4', ol='#5E6A84', w=1.6) for cx, cy, rw in ((300, 230, 120), (820, 180, 160))]
    layers_far(d, 470, n=3, base='#5A4A6A', sky='#F2B98A', seed=7, bottom=640)
    poly(d, [(-20, 620), (W + 20, 600), (W + 20, 920), (-20, 920)], '#A07850', w=2.6)
    K.shade(c, [(0, 600), (W, 580), (W, 900), (0, 900)], 0.82, (1.0, 0.9, 1.05))
    Dog(c, 700, 860, 1.0, dict(mouth='smirk', gaze=(1, -0.4), flat=True, arms=((18, 8), (80, 122)))).draw()
    panels.append(('N17 Hoàng hôn: trời dải phẳng + tia chói', c))

    # 4. N18 dưới nước: lòng sông có cọc
    c = new(); d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 900), (0, 900)], '#9CC8C0', ol=None)
    poly(d, [(-20, 700), (W + 20, 660), (W + 20, 920), (-20, 920)], '#A89060', w=2.6)
    for i, x in enumerate(range(200, 1500, 180)):
        poly(d, [(x - 18, 760), (x - 14, 340 + 30 * (i % 2)), (x, 300 + 30 * (i % 2)), (x + 14, 340 + 30 * (i % 2)), (x + 18, 760)],
             '#8A5A3A', w=2.6)
        pline(d, [(x - 12, 400), (x + 12, 404)], '#6E4630', 2)
    for x in (120, 760, 1420):
        pline(d, [(x, 700), (x + 20, 600), (x - 10, 520), (x + 14, 440)], '#4E7A3A', 6)
    underwater(c, seed=2)
    panels.append(('N18 Dưới nước: phủ xanh lục + bong bóng', c))

    # 5. N19 + N24 + N25 đêm ấm trong nhà Tết
    c = new(); d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 640), (0, 640)], '#E6D6B4', ol=None)
    for i, (x, y) in enumerate(((180, 120), (1450, 300))):
        crack(d, x, y, 70, seed=i)
    lattice_door(d, 80, 120, 360, 640)
    lattice_door(d, 1240, 120, 1520, 640)
    tet_calendar(d, 560, 140)
    poly(d, [(0, 640), (W, 640), (W, 920), (0, 920)], '#B08A60', w=2.6)
    for y in (700, 790):
        pline(d, [(0, y), (W, y)], '#9A7650', 2)
    wood_bench(d, 900, 1220, 760)
    tea_set(d, 1060, 690, 0.9)
    mai_bonsai(d, 700, 770, 1.0, seed=3)
    Dog(c, 470, 860, 0.85, dict(mouth='smirk', gaze=(1, 0), lid=(0.3, 0.3), flat=True, cup=True)).draw()
    oil_lamp(d, 1160, 690)
    tint_warm_night(c, lamp=(1160, 640), r=300)
    panels.append(('N19/N24/N25 Đêm ấm nhà Tết: mai, lịch, ấm trà, cửa bức bàn', c))

    # 6. N20 + N27 đèn rọi + khói
    c = new(); d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 640), (0, 640)], '#8A93A0', ol=None)
    for x in range(0, W, 200):
        pline(d, [(x, 0), (x, 640)], '#757E8C', 2)
    tile_floor(d, 640, 900, 800, col='#6E7480', line='#5A606C')
    Dog(c, 800, 830, 0.95, dict(mouth='open', gaze=(0, -0.5), flat=True, arms=((60, -60), (60, -60)))).draw()
    spotlight(c, 800, 80, 330, out=0.32)
    for i, x in enumerate((260, 1340)):
        smoke(c, x, 800, 80, n=8, seed=i, col='#6A6E78')
    panels.append(('N20/N27 Đèn rọi + khói tròn phẳng', c))

    # 7. N26 rừng tre + bụi cây
    c = new(); d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 780), (0, 780)], '#CFE6F0', ol=None)
    K.cloud(c, 1100, 110, 0.7)
    d = ImageDraw.Draw(c)
    layers_far(d, 420, n=2, base='#7A8C9A', sky='#CFE6F0', seed=9, bottom=780)
    bamboo_grove(d, -40, 1640, 760, n=12, seed=1)
    poly(d, [(-20, 740), (W + 20, 730), (W + 20, 920), (-20, 920)], '#A6C47A', w=2.4)
    bush_row(d, -40, 520, 790, n=5, seed=1)
    bush_row(d, 1080, 1640, 800, n=5, col='#8DBE64', seed=2)
    Dog(c, 800, 860, 0.9, dict(mouth='smirk', gaze=(-1, 0), flat=True, book=True)).draw()
    panels.append(('N26 Rừng tre 3 lớp + bụi tròn', c))

    # 8. N21 khung trong khung + N22 đạo cụ lệch thời + N28/N29
    c = new()
    inner = new(); symbol_card(inner)
    d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 660), (0, 660)], '#D8C8A4', ol=None)
    poly(d, [(0, 660), (W, 660), (W, 920), (0, 920)], '#9A7650', w=2.6)
    tv_frame(c, (900, 140, 1420, 430), inner)
    d = ImageDraw.Draw(c)
    poly(d, [(980, 470), (1340, 470), (1340, 660), (980, 660)], '#7A4E30', w=2.6)
    Dog(c, 520, 880, 1.0, dict(mouth='open', gaze=(1, -0.2), flat=True, cup=True, sip=False)).draw()
    panels.append(('N21/N28 Khung trong khung: TV chiếu biểu tượng', c))

    from PIL import ImageFont
    font = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26)
    PW, PH = 800, 450
    sheet = Image.new('RGB', (PW * 2, (PH + 44) * 4), hx('#F2E6CC'))
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(panels):
        im = im.resize((W, H), Image.LANCZOS).convert('RGB')
        im.save(os.path.join(out, 'fx3-%d.png' % (i + 1)))
        x, y = (i % 2) * PW, (i // 2) * (PH + 44)
        sheet.paste(im.resize((PW, PH), Image.LANCZOS), (x, y + 44))
        dr.text((x + 12, y + 8), name, font=font, fill=hx('#14110F'))
    p = os.path.join(out, 'bang-hieu-ung-3.jpg')
    sheet.save(p, quality=90)
    print(p)


# ------------------------------------------------------------------ demo
def demo():
    from gau_nghe_van import Dog, ROOT
    import gau_nghe_khung_thu as K
    out = os.path.join(ROOT, 'build', 'thu-hoathinh', 'sitcom-fx')
    os.makedirs(out, exist_ok=True)
    panels = []

    a = K.frame_a()
    tint_night(a, windows='#3E8F7A', moon=(1460, 110))
    panels.append(('N1 Đêm: đổi bảng màu xanh, thắp cửa sổ', a))

    a = K.frame_a()
    dusk(a)
    panels.append(('N11 Hoàng hôn', a))

    b = K.frame_b()
    rain(b)
    panels.append(('N11 Mưa', b))

    # trong nhà xám xanh: vết nứt, cột gỗ, cửa chớp, sàn gạch phối cảnh, vệt nắng
    c = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(c)
    poly(d, [(0, 0), (W, 0), (W, 620), (0, 620)], '#9FB3B0', ol=None)
    for i, (x, y) in enumerate(((220, 120), (900, 80), (1280, 300), (520, 420))):
        crack(d, x, y, 80, seed=i)
    poly(d, [(1080, 0), (1150, 0), (1150, 640), (1080, 640)], '#7A4E30', w=3)                    # cột gỗ
    pline(d, [(1100, 60), (1100, 600)], '#9A6A44', 3)
    for sx in (260, 400):                                                                         # cửa chớp
        poly(d, [(sx, 140), (sx + 130, 140), (sx + 130, 520), (sx, 520)], '#5A3E2E', w=3)
        for ly in range(160, 510, 26):
            pline(d, [(sx + 12, ly), (sx + 118, ly + 10)], '#3E2A1E', 3)
    tile_floor(d, 620, 900, 800)
    poly(d, [(1240, 380), (1400, 380), (1400, 620), (1240, 620)], '#4A3A30', w=3)                  # tủ
    K.shade(c, [(540, 620), (900, 620), (1080, 900), (620, 900)], 1.22, (1, 1, 0.9))              # vệt nắng
    K.shade(c, [(0, 0), (240, 0), (240, 620), (0, 620)], 0.8)
    Dog(c, 780, 860, 1.05, dict(mouth='smirk', gaze=(1, 0), lid=(0.3, 0.3), arms=((18, 8), (80, 122)), flat=True)).draw()
    panels.append(('N3/N4 Trong nhà: nứt tường, sàn phối cảnh, vệt nắng', c))

    # toàn cảnh bãi sông có đám đông + dừa + cầu tre + letterbox
    e = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(e)
    poly(d, [(0, 0), (W, 0), (W, 420), (0, 420)], '#E6D3A0', ol=None)
    poly(d, [(-20, 330), (W + 20, 300), (W + 20, 430), (-20, 450)], '#A9C46E', w=2.4)
    for i, x in enumerate((120, 380, 1240, 1480)):
        coconut(d, x, 440, 260 + 30 * (i % 2), lean=(-40 if i % 2 else 40), seed=i)
    poly(d, [(-20, 430), (W + 20, 410), (W + 20, 560), (-20, 580)], '#8EB7B8', w=2.4)              # sông
    for i in range(14):
        x = 60 + i * 110
        pline(d, [(x, 490 + (i % 3) * 18), (x + 50, 490 + (i % 3) * 18)], '#6E9A9C', 2.2)
    cau_tre(d, 560, 1020, 470, 90)
    poly(d, [(-20, 570), (W + 20, 550), (W + 20, 920), (-20, 920)], '#D9C08A', w=2.6)              # bãi
    crowd(e, 60, 1540, 600, 790, n=70, col='#6E6880', seed=4, front=('#B3261E', '#3B5E8C', '#7A5236'))
    letterbox(e)
    _grade(e, (1.0, 0.96, 0.86), (8, 4, 0))
    panels.append(('N5/N6/N7 Cảnh trận: đám đông, dừa, cầu tre, letterbox', e))

    f = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    insert_stake(f)
    letterbox(f)
    panels.append(('N8 Cận đạo cụ: cọc bịt sắt', f))

    from PIL import ImageFont
    font = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26)
    PW, PH = 800, 450
    sheet = Image.new('RGB', (PW * 2, (PH + 44) * 3), hx('#F2E6CC'))
    dr = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(panels):
        im = im.resize((W, H), Image.LANCZOS).convert('RGB')
        im.save(os.path.join(out, 'fx-%d.png' % (i + 1)))
        x, y = (i % 2) * PW, (i // 2) * (PH + 44)
        sheet.paste(im.resize((PW, PH), Image.LANCZOS), (x, y + 44))
        dr.text((x + 12, y + 8), name, font=font, fill=hx('#14110F'))
    p = os.path.join(out, 'bang-hieu-ung.jpg')
    sheet.save(p, quality=90)
    print(p)


if __name__ == '__main__':
    demo3() if '--dot3' in sys.argv else demo()
