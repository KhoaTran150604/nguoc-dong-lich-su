"""BỘ ĐỘNG TÁC cho hoạt hình Gâu Nghệ (60 khung/giây) – vẽ & chấm TRƯỚC khi ghép video.

Thư viện (dùng lại cho video):
  kf(t, keys)               nội suy khoá hình có tăng/giảm tốc: keys = [(t, giá_trị_số_hoặc_tuple), ...]
  Walker                    đi/chạy KHÔNG trượt chân: pha bước tính từ quãng đường; trả feet, nhún, lắc, vung tay
  racket_head(h)            toạ độ mặt vợt thật của một Human đã đặt dáng → cầu bay đúng từ mặt vợt
  arc(t, t0, t1, p0, p1, h) quỹ đạo cầu lông (bay nhanh, hãm dần, rơi dốc) + góc đầu cầu theo hướng bay
  phone_screen(...)         màn hình điện thoại cuộn bản tin + ngón cái vuốt
Demo: python scripts/hoathinh/dong_tac.py [--clip ten] [--khung]   → build/thu-hoathinh/dong-tac/
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cau_long_video as V  # noqa: E402  nền nhà thi đấu, lưới, cầu, máy quay
import meo_nghe_cach_dieu as M  # noqa: E402
from ngo_quyen_can_canh import SS, INK, hx  # noqa: E402
from nguoi2 import Human, CAST, prop  # noqa: E402
from gau_nghe_van import Dog, ROOT  # noqa: E402

FPS = 60
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'dong-tac')
FONT_B = V.FONT_B


# ================================================================== nội suy
def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def kf(t, keys, fn=ease):
    """keys: [(t, v), ...] v là số hoặc tuple. Giữa 2 khoá: ease (mặc định). Khoá có thể kèm hàm riêng: (t, v, fn)."""
    if t <= keys[0][0]:
        return keys[0][1]
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        if a[0] <= t <= b[0]:
            f = b[2] if len(b) > 2 else fn
            k = f((t - a[0]) / max(1e-6, b[0] - a[0]))
            if isinstance(a[1], tuple):
                return tuple(x + (y - x) * k for x, y in zip(a[1], b[1]))
            return a[1] + (b[1] - a[1]) * k
    return keys[-1][1]


def lin(x):
    return min(1.0, max(0.0, x))


def eout(x):
    x = lin(x)
    return 1 - (1 - x) ** 2.4


def ein(x):
    x = lin(x)
    return x ** 2.2


# ================================================================== đi / chạy
class Walker:
    """Vị trí x theo khoá hình; pha bước = quãng đường / (2*sải) * π → bàn chân đứng yên trên sàn khi chạm (không trượt)."""

    def __init__(self, keys, stride=24, lift=16, run=False, fat=False):
        self.keys, self.A, self.L, self.run, self.fat = keys, stride, lift, run, fat
        self.cache = {}

    def x(self, t):
        return kf(t, self.keys)

    def phase(self, t):
        n = int(t * FPS)
        if n in self.cache:
            return self.cache[n]
        d, px = 0.0, self.x(0)
        for i in range(1, n + 1):
            nx = self.x(i / FPS)
            d += abs(nx - px)
            px = nx
        self.cache[n] = d
        return d

    def pose(self, t, s, legx):
        """→ (x màn hình, st bổ sung). Đơn vị sải/nhấc là toạ độ cục bộ (trước khi nhân s)."""
        x = self.x(t)
        v = (self.x(t + 1 / FPS) - x) * FPS
        moving = min(1.0, abs(v) / (60 * s))           # 0 = đứng, 1 = đi đều
        dirn = 1 if v >= 0 else -1
        ph = self.phase(t) / s / (2 * self.A) * math.pi
        feet = {}
        for sd, off in ((-1, 0.0), (1, math.pi)):
            phi = ph + off
            ox = -dirn * self.A * 0.3 * math.cos(phi) * moving      # nhìn chính diện: bước dọc trục nhìn, lệch ngang ít
            lf = self.L * max(0.0, math.sin(phi)) * moving
            feet['L' if sd < 0 else 'R'] = (sd * (legx + 2) + ox, -18 - lf)
        st = dict(feet=feet, kdir=dirn)
        bob = (0.10 if not self.run else 0.22) * (math.cos(ph) ** 2) * moving
        st['crouch'] = bob
        st['lean'] = dirn * (3 if not self.run else 9) * moving + (7 * math.sin(ph) * moving if self.fat else 0)
        sw = math.sin(ph) * moving
        if self.run:     # tay co 90°, đánh mạnh
            st['arms'] = ((24 + 22 * sw, 100 + 20 * sw), (24 - 22 * sw, 100 - 20 * sw))
        else:
            st['arms'] = ((12 + 12 * sw, 18 + 14 * sw), (12 - 12 * sw, 18 - 14 * sw))
        return x, st, ph, moving


def dog_draw(cv, x, y, s, st, lean=0.0, sq=1.0):
    """Vẽ Gâu; lean (độ, dương = nghiêng phải) xoay quanh chân; sq = nén/dãn dọc quanh chân (giữ thể tích: ngang 1/sqrt)."""
    if not lean and abs(sq - 1) < 1e-3:
        d = Dog(cv, x, y, s, st)
        d.draw()
        return d
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    d = Dog(lay, x, y, s, st)
    d.draw()
    if abs(sq - 1) > 1e-3:
        sx, sy = 1 / math.sqrt(sq), sq
        X, Y = x * SS, y * SS
        lay = lay.transform(lay.size, Image.AFFINE, (1 / sx, 0, X - X / sx, 0, 1 / sy, Y - Y / sy), resample=Image.BICUBIC)
    if lean:
        lay = lay.rotate(-lean, center=(x * SS, y * SS), resample=Image.BICUBIC)
    cv.alpha_composite(lay)
    return d


def run_fx(cv, x, gy, t, ph, dirn=1):
    """Chạy kiểu hoạt hình: cụm bụi tròn phẳng tung sau gót + 4 vệt tốc độ ngang sau lưng."""
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(5):                       # bụi: sinh theo nhịp bước, bay lùi + nở + mờ dần
        age = ((t * 4 + i / 5) % 1)
        bx = x - dirn * (30 + 90 * age) - i * 6
        by = gy - 8 - 26 * age
        r = 10 + 20 * age
        a = int(200 * (1 - age))
        d.ellipse([(bx - r) * SS, (by - r) * SS, (bx + r) * SS, (by + r) * SS], fill=(236, 226, 206, a),
                  outline=(120, 105, 90, a), width=2 * SS)
    for k, yy in enumerate((-60, -100, -140, -175)):
        L = 70 + 30 * math.sin(t * 20 + k)
        x0 = x - dirn * (70 + 12 * k)
        d.line([(x0 * SS, (gy + yy) * SS), ((x0 - dirn * L) * SS, (gy + yy) * SS)], fill=(255, 255, 255, 170), width=4 * SS)
    cv.alpha_composite(lay)


def dog_gait(ph, moving, run=False):
    A, L = (34, 46) if run else (12, 32)
    f = []
    for off in (0.0, math.pi):
        f.append((A * math.cos(ph + off) * moving, L * max(0.0, math.sin(ph + off)) * moving))
    bob = (30 if run else 14) * abs(math.cos(ph)) * moving
    return tuple(f), bob


# ================================================================== vợt + cầu
def racket_head(h, side='R', L=120):
    """Tâm mặt vợt (màn hình) của Human h với st hiện tại."""
    sd = 1 if side == 'R' else -1
    hd = h.P(*h.arm(sd)[2])
    a = math.radians(h.st.get('prop_ang', {}).get(side, -30))
    return (hd[0] + math.sin(a) * L * h.s, hd[1] - math.cos(a) * L * h.s)


def arc(t, t0, t1, p0, p1, h, drag=1.7):
    """Cầu lông: ngang hãm dần (drag), độ cao parabol lệch về cuối → rơi dốc. Trả ((x,y), góc) – góc: đầu cầu theo hướng bay."""
    def at(tt):
        k = lin((tt - t0) / (t1 - t0))
        kx = 1 - (1 - k) ** drag
        y = p0[1] + (p1[1] - p0[1]) * k - h * 4 * kx * (1 - kx)
        return p0[0] + (p1[0] - p0[0]) * kx, y
    x, y = at(t)
    x2, y2 = at(t + 0.004)
    vx, vy = x2 - x, y2 - y
    ang = math.degrees(math.atan2(-vx, vy)) if (vx or vy) else 0
    return (x, y), ang


def trail(cv, pts, col=(255, 255, 255)):
    """Vệt bay phẳng: vài nét mảnh nhạt dần (không blur)."""
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(len(pts) - 1):
        a = int(150 * (i + 1) / len(pts))
        d.line([(pts[i][0] * SS, pts[i][1] * SS), (pts[i + 1][0] * SS, pts[i + 1][1] * SS)], fill=col + (a,),
               width=int((2 + 4 * i / len(pts)) * SS))
    cv.alpha_composite(lay)


class Rally:
    """Chuỗi cú đánh: list (t_hit, t_land, p_from, p_to, cao). p có thể là hàm() → lấy từ mặt vợt lúc đánh."""

    def __init__(self, shots):
        self.shots = shots

    def at(self, t):
        for t0, t1, p0, p1, hh in self.shots:
            if t0 <= t <= t1:
                p0_ = p0() if callable(p0) else p0
                p1_ = p1() if callable(p1) else p1
                return arc(t, t0, t1, p0_, p1_, hh)
        return None

    def draw(self, cv, t, k=1.0):
        r = self.at(t)
        if not r:
            return
        pts = [self.at(t - i * 0.016) for i in range(7, 0, -1)]
        pts = [p[0] for p in pts if p]
        if len(pts) > 2:
            trail(cv, pts + [r[0]])
        V.shuttle(cv, r[0][0], r[0][1], r[1], k)


# ================================================================== điện thoại
def phone_screen(cv, hand, s, t, scroll_v=60, thumb=True, img=None):
    """Bản tin cuộn trên màn hình điện thoại (prop 'phone' tâm bàn tay = hand)."""
    x, y = hand
    w, h = 24 * s, 44 * s
    x0, y0, x1, y1 = x - w + 5 * s, y - h, x + w - 5 * s, y + 4 * s
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=hx('#F4F4F4') + (255,))
    off = (t * scroll_v * s) % (30 * s)
    cols = ['#F7A8BA', '#9ED4EE', '#FFD34D', '#A6D99B']
    for i in range(-1, 4):
        cy = y0 + i * 30 * s - off + 4 * s
        c = cols[(i + int(t * scroll_v / 30)) % 4]
        d.rectangle([(x0 + 3 * s) * SS, cy * SS, (x1 - 3 * s) * SS, (cy + 17 * s) * SS], fill=hx(c) + (255,))
        d.rectangle([(x0 + 3 * s) * SS, (cy + 20 * s) * SS, (x1 - 12 * s) * SS, (cy + 24 * s) * SS], fill=hx('#B8B8C0') + (255,))
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=255)
    arr = np.asarray(lay).copy()
    arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
    cv.alpha_composite(Image.fromarray(arr, 'RGBA'))
    if thumb:      # ngón cái vuốt lên
        k = (t * 1.6) % 1
        ty = y1 - 8 * s - 26 * s * ease(k / 0.6) if k < 0.6 else y1 - 8 * s
        M.ell(cv, (x + 12 * s, ty), 7 * s, 9 * s, fill=hx(CAST['na']['skin']), ow=2.4 * s)


# ================================================================== khung chung
def label(im, text, sub=''):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_B, 30)
    d.rounded_rectangle([16, 14, 30 + d.textlength(text, font=f), 60], 8, fill=(20, 17, 15))
    d.text((24, 18), text, font=f, fill=(243, 210, 122))
    if sub:
        f2 = ImageFont.truetype(V.FONT, 20)
        d.rounded_rectangle([16, 64, 32 + d.textlength(sub, font=f2), 96], 6, fill=(244, 239, 228))
        d.text((24, 68), sub, font=f2, fill=(20, 17, 15))
    return im


def hum(cv, key, x, gy, s, st):
    h = Human(cv, x, gy, s * (1.13 if key == 'khang' else 1.0), CAST[key], st)
    return h


def blink(t, ph=0.0):
    return ((t + ph) % 3.1) < 0.1


# ================================================================== CLIP 1: đi bộ – 4 kiểu dáng đi
def c_walk(t):
    cv = V.BG['gym'].copy()
    # hàng sau: Na đi nảy (sải ngắn, nhấc cao) ← ; Thầy Ba đi chắp tay chậm →
    wn = W_NA
    x, st, ph, mv = wn.pose(t, 0.42, 17)
    st.update(mouth='smile', eyes='closed' if blink(t) else 'open', gaze=(-0.6, 0), crouch=st['crouch'] + 0.05 * abs(math.sin(ph)))
    hum(cv, 'na', x, 712, 0.44, st).draw()
    x, st, ph, mv = W_TH.pose(t, 0.42, 23)
    st.update(mouth='frown', eyes='open', gaze=(-1, 0), arm_to={'L': (-30, -170), 'R': (30, -170)})
    st.pop('arms')
    hum(cv, 'thay', x, 700, 0.44, st).draw()
    V.net(cv)
    # hàng trước: Khang sải dài tự tin →, Tùng lạch bạch ←, Gâu lon ton →
    x, st, ph, mv = W_TU.pose(t, 0.5, 30)
    st.update(mouth='open', mo=0.3, eyes='open', gaze=(-0.8, 0), sweat=True)
    if t > 3.7:     # dừng lại vẫy chào
        st.pop('arms', None)
        st['arm_to'] = {'R': (120, -330 + 25 * math.sin(t * 10))}
        st.update(mouth='D', eyes='happy')
    hum(cv, 'tung', x, 800, 0.47, st).draw()
    x, st, ph, mv = W_KH.pose(t, 0.5, 22)
    st.update(mouth='smirk', gaze=(0.8, 0), hold={'R': 'racket'}, prop_ang={'R': 60})
    hk = hum(cv, 'khang', x, 895, 0.5, st)
    hk.draw()
    x = W_GA.x(t)
    ph = W_GA.phase(t) / 40 * math.pi
    mv = min(1, abs(W_GA.x(t + 1 / 60) - x) * 60 / 30)
    feet, bob = dog_gait(ph, mv)
    dog_draw(cv, x, 878 - bob * 0.5, 0.48, dict(flat=True, feet=feet, mouth='tongue', gaze=(0.7, 0), eyes='open',
                                                 arms=((18 + 30 * math.sin(ph) * mv, 20), (18 - 30 * math.sin(ph) * mv, 20))),
             lean=(5 + 4 * math.sin(ph)) * mv)
    im = V.cam(cv, 1.3, kf(t, [(0, 640), (5, 960)]), 650)
    return label(im, 'ĐI BỘ', 'Khang sải dài · Tùng lạch bạch · Na nhún nhảy · Thầy chắp tay · Gâu lon ton')


W_KH = Walker([(0, 200), (0.4, 200), (4.2, 990), (5.2, 990)], stride=30, lift=26)
W_TU = Walker([(0, 1500), (0.3, 1500), (3.6, 1230), (5.2, 1230)], stride=22, lift=16, fat=True)
W_NA = Walker([(0, 1250), (0.5, 1250), (4.8, 520)], stride=20, lift=30)
W_TH = Walker([(0, 1350), (0.6, 1350), (5.0, 760)], stride=20, lift=18)
W_GA = Walker([(0, 30), (0.6, 30), (4.6, 780), (5.2, 780)])


# ================================================================== CLIP 2: đánh qua lại (đỡ cầu, di chuyển, đập)
# Tùng (trái, x≈480) – Khang (phải, x≈1180). Mốc đánh:
R_T = dict(serve=0.9, clear=2.6, drive=4.0, lift=5.3, smash=7.0, land=7.45)


def tung_rally(cv, t, draw=True):
    """Tùng: giao cầu thấp tay → lùi/chạy sang đỡ → đánh ngang → đứng nhìn cầu bay → bị đập hụt, ngã."""
    x = kf(t, [(0, 470), (1.4, 470), (2.6, 470), (3.1, 470), (3.75, 560), (4.6, 560), (5.4, 450), (6.6, 450)])
    st = dict(hold={'R': 'racket'}, gaze=(1, -0.3), mouth='smile', eyes='open')
    # tay vợt theo khoá: (t, (hx, hy), góc)
    hand = kf(t, [(0, (120, -170)), (0.6, (140, -150)), (0.9, (75, -210), ein), (0.93, (75, -210)), (1.15, (130, -380)),
                  (1.6, (100, -300)), (3.2, (100, -300)), (3.7, (-80, -250)), (4.0, (170, -300), ein), (4.03, (170, -300)),
                  (4.3, (110, -380)), (5.6, (110, -300)), (6.8, (110, -330))])
    ang = kf(t, [(0, 150.0), (0.6, 175.0), (0.9, -122.0, ein), (0.93, -122.0), (1.15, 20.0), (1.6, 30.0), (3.2, 30.0),
                 (3.7, -90.0), (4.0, 70.0, ein), (4.03, 70.0), (4.3, -10.0), (5.6, 30.0), (7.15, -20.0)])
    st['arm_to'] = {'R': hand, 'L': kf(t, [(0, (-20, -215)), (0.72, (-20, -215)), (1.0, (-90, -200))])}
    st['prop_ang'] = {'R': ang}
    # chân: bước sang phải đỡ cú drive (3.1–3.75), lùi về (4.6–5.4)
    w = Walker([(0, 470), (3.1, 470), (3.75, 560), (4.6, 560), (5.4, 450), (9, 450)], stride=16, lift=12, fat=True)
    _, wst, ph, mv = w.pose(t, 0.5, 30)
    st['feet'] = wst['feet']
    st['crouch'] = wst['crouch'] + kf(t, [(3.75, 0.0), (3.95, 0.35), (4.3, 0.0)])
    st['lean'] = wst['lean']
    if t > R_T['smash'] - 0.15:      # bị đập: giật mình, ngửa ra sau
        k = ease((t - R_T['smash'] + 0.15) / 0.4)
        st.update(eyes='wide', mouth='o', gaze=(0.3, 0.6), lean=-10 * k)
    if t > R_T['land']:              # ngã ngồi phịch xuống, nảy, tay chống sàn, vợt văng
        L0 = R_T['land']
        k = ease((t - L0) / 0.5)
        bounce = kf(t, [(L0 + 0.3, 0.0), (L0 + 0.38, -0.5), (L0 + 0.48, 0.0), (L0 + 0.54, -0.22), (L0 + 0.62, 0.0)])
        if k < 0.6:      # đang khuỵu xuống
            st['crouch'] = st['crouch'] + 1.0 * k / 0.6
            st['feet'] = {'L': (-40 - 30 * k, -18), 'R': (40 + 30 * k, -18)}
        else:            # ngồi bệt (dáng ngồi có sẵn) + nảy
            st.pop('feet', None)
            st['crouch'] = bounce
            st['sit'] = True
            st['sit_drop'] = 0.95
        st['lean'] = -4 - 6 * k
        st['tilt'] = 9 * math.sin((t - L0 - 0.6) * 14) * (1 if L0 + 0.6 < t < L0 + 1.5 else 0)
        st.pop('hold', None)
        if t > L0 + 1.5:
            st.update(gaze=(-1, 0.7), mouth='o', eyes='wide')
        st['arm_to'] = {'R': (90 + 40 * k, -200 + 70 * k), 'L': (-90 - 40 * k, -200 + 70 * k)}
        st['prop_ang'] = {}
        st.update(mouth='open', mo=0.6, eyes='wide' if (t - R_T['land']) % 1.2 > 0.1 else 'closed', sweat=True)
    h = hum(cv, 'tung', x, 840, 0.5, st)
    if draw:
        h.draw()
    return h


def khang_rally(cv, t, draw=True):
    """Khang: chờ → lùi đánh cầu cao → lao trái đỡ thấp (bước dài) → về giữa → nhún, bật nhảy, đập."""
    xs = [(0, 1180), (1.6, 1180), (2.2, 1260), (2.9, 1260), (3.6, 1180), (4.5, 1060), (4.9, 1060), (5.8, 1180), (6.2, 1200)]
    w = Walker(xs, stride=20, lift=16, run=False)
    x, wst, ph, mv = w.pose(t, 0.5, 22)
    st = dict(hold={'R': 'racket'}, gaze=(-1, -0.4), mouth='smirk', eyes='open', gear=True)
    st['feet'] = wst['feet']
    st['lean'] = wst['lean']
    cr_ = kf(t, [(0, 0.15), (2.3, 0.15), (2.45, 0.3), (2.7, 0.0), (4.5, 0.1), (4.8, 0.7), (5.2, 0.7), (5.6, 0.15),
                 (6.2, 0.15), (6.5, 0.85), (6.62, 0.0, ein)])
    st['crouch'] = wst['crouch'] + cr_ + (0.08 * (1 + math.sin(t * 12)) if t < 2.1 else 0)
    # đỡ thấp: chân trái bước dài sang trái (lunge)
    lunge = kf(t, [(4.5, 0.0), (4.75, 1.0), (5.25, 1.0), (5.6, 0.0)])
    if lunge > 0:
        st['feet'] = dict(st['feet'])
        lx, ly = st['feet']['L']
        st['feet']['L'] = (lx - 90 * lunge, ly)
        st['lean'] = -8 * lunge
    # nhảy đập
    jump = 0.0
    if 6.62 <= t <= 7.42:
        k = (t - 6.62) / 0.8
        jump = 260 * (4 * k * (1 - k)) ** 0.85
        st['feet'] = {'L': (-30, -60), 'R': (40, -34)}
        st['crouch'] = 0.25
        st['lean'] = -8 * math.sin(math.pi * k)
    hand = kf(t, [(0, (110, -380)), (2.2, (110, -400)), (2.45, (80, -450)), (2.6, (118, -462), ein), (2.63, (118, -462)),
                  (2.88, (-60, -230)), (3.4, (110, -380)), (4.6, (90, -300)), (4.95, (-40, -200)), (5.3, (-30, -320), eout),
                  (5.33, (-30, -320)), (5.9, (110, -380)), (6.45, (120, -470)), (6.8, (70, -450)), (7.0, (118, -466), ein),
                  (7.03, (118, -466)), (7.2, (-60, -220)), (7.6, (60, -300))])
    ang = kf(t, [(0, 20.0), (2.2, 10.0), (2.45, 200.0), (2.6, 18.0, ein), (2.63, 18.0), (2.88, -160.0), (3.4, 20.0),
                 (4.6, -20.0), (4.95, -150.0), (5.3, -40.0, eout), (5.33, -40.0), (5.9, 20.0), (6.45, 60.0), (6.8, 210.0),
                 (7.0, 14.0, ein), (7.03, 14.0), (7.2, -165.0), (7.6, -90.0)])
    st['arm_to'] = {'R': hand, 'L': kf(t, [(0, (-80, -300)), (6.3, (-80, -300)), (6.6, (-60, -500)), (6.95, (-90, -330))])}
    st['prop_ang'] = {'R': ang}
    if 6.5 < t < 7.0:
        st.update(eyes='angry', mouth='D')
    elif t >= 7.0:
        st.update(mouth='grin', eyes='open')
    h = hum(cv, 'khang', x, 860 - jump * 0.5 * 1.13, 0.5, st)
    if draw:
        h.draw()
    return h


def _rh(fn, t):
    tmp = Image.new('RGBA', (8, 8))
    return racket_head(fn(tmp, t, draw=False))


def rally_obj():
    T = R_T
    return Rally([
        (T['serve'], T['clear'], lambda: _rh(tung_rally, T['serve']), lambda: _rh(khang_rally, T['clear']), 190),
        (T['clear'], T['drive'], lambda: _rh(khang_rally, T['clear']), lambda: _rh(tung_rally, T['drive']), 210),
        (T['drive'], T['lift'], lambda: _rh(tung_rally, T['drive']), lambda: _rh(khang_rally, T['lift']), 40),
        (T['lift'], T['smash'], lambda: _rh(khang_rally, T['lift']), lambda: _rh(khang_rally, T['smash']), 200),
        (T['smash'], T['land'], lambda: _rh(khang_rally, T['smash']), (600, 846), -40),
    ])


RALLY = None


def tung_lhand(t):
    h = tung_rally(Image.new('RGBA', (8, 8)), t, draw=False)
    return h.P(*h.arm(-1)[2])


def c_rally(t):
    global RALLY
    if RALLY is None:
        RALLY = rally_obj()
    cv = V.BG['gym'].copy()
    if t > R_T['land']:              # vợt tuột tay, văng ra sau lưng theo cung rồi nằm ngang trên sàn
        L0 = R_T['land']
        q = min(1.0, (t - L0) / 0.5)
        p0 = _rh(tung_rally, L0 - 0.01)
        px = p0[0] + (390 - p0[0]) * q
        py = p0[1] + (858 - p0[1]) * q - 110 * 4 * q * (1 - q)
        if q >= 1:
            py -= 8 * abs(math.sin((t - L0 - 0.5) * 12)) * max(0, 1 - (t - L0 - 0.5) * 4)
        prop(cv, 'racket', (px - 60, py), 0.5, 90 + 360 * q, hand=False)
    tung_rally(cv, t)
    T_DROP = 0.72
    if t < T_DROP:                        # cầu cầm sẵn ở tay trái (đầu bần chúc xuống)
        lx, ly = tung_lhand(t)
        V.shuttle(cv, lx, ly + 14, 0, 1.0)
    elif t < R_T['serve']:                # thả rơi tự do tới mặt vợt
        lx, ly = tung_lhand(T_DROP)
        rx, ry = _rh(tung_rally, R_T['serve'])
        k = ((t - T_DROP) / (R_T['serve'] - T_DROP)) ** 2
        V.shuttle(cv, lx + (rx - lx) * k, ly + 14 + (ry - ly - 14) * k, 0, 1.0)
    V.net(cv)
    khang_rally(cv, t)
    RALLY.draw(cv, t, 1.0)
    if t > R_T['land']:              # cầu cắm sàn
        V.shuttle(cv, 600, 846 - 8 * max(0, 1 - (t - R_T['land']) * 4) * abs(math.sin((t - R_T['land']) * 14)), -40)
    if R_T['smash'] - 0.02 < t < R_T['smash'] + 0.12:      # "bốp" – vòng tác động phẳng
        r = racket_head(khang_rally(Image.new('RGBA', (8, 8)), R_T['smash'], draw=False))
        k = (t - R_T['smash'] + 0.02) / 0.14
        d = ImageDraw.Draw(cv)
        for i in range(8):
            a = i * math.pi / 4
            d.line([((r[0] + 40 * k * math.cos(a)) * SS, (r[1] + 40 * k * math.sin(a)) * SS),
                    ((r[0] + (60 + 30 * k) * math.cos(a)) * SS, (r[1] + (60 + 30 * k) * math.sin(a)) * SS)], fill=hx('#FFD34D') + (255,),
                   width=5 * SS)
    if 6.35 <= t < 7.25:          # cận Khang bật nhảy đập
        im = V.cam(cv, 2.0, 1150, kf(t, [(6.35, 600), (6.9, 520), (7.25, 560)]))
    elif 7.25 <= t:               # cận Tùng: cầu cắm sàn, ngã phịch
        im = V.cam(cv, 1.9, 520, 660)
    else:
        im = V.cam(cv, 1.15, kf(t, [(0, 820), (6.2, 840)]), 560)
    return label(im, 'ĐÁNH QUA LẠI', 'giao cầu · lùi đánh cao · lao đỡ thấp · bật nhảy đập')


# ================================================================== CLIP 3: Na lướt điện thoại đi tới, khoe Gâu
def c_phone(t):
    cv = V.BG['gym'].copy()
    w = W_NA2
    x, st, ph, mv = w.pose(t, 0.5, 17)
    show = kf(t, [(0, 0.0), (3.0, 0.0), (3.5, 1.0)])
    st.pop('arms')
    hand = kf(t, [(0, (30, -232)), (3.0, (30, -232)), (3.5, (150, -330))])
    st.update(hold={'R': 'phone'}, prop_k=1.5, arm_to={'R': hand, 'L': (20, -250)}, gaze=(0.2, 1) if show < 0.5 else (1, 0),
              tilt=6 * (1 - show),
              mouth='smile' if t < 2.4 else 'D', eyes='open' if t < 2.4 else 'happy', lean=st['lean'] - 4 * (1 - show))
    h = hum(cv, 'na', x, 860, 0.5, st)
    h.draw()
    phone_screen(cv, h.hands['R'], 0.75, t, thumb=t < 3.0)
    # Gâu đứng chờ, quay sang nhìn rồi nghiêng người ngó
    gx = 1000
    look = kf(t, [(0, 0.0), (3.2, 0.0), (3.7, 1.0)])
    hop = abs(math.sin((t - 3.7) * 9)) * 14 * (1 if 3.7 < t < 4.6 else 0)
    dog_draw(cv, gx, 868 - hop, 0.5, dict(flat=True, mouth='tongue' if look > 0.5 else 'smirk', eyes='happy' if look > 0.5 else 'open',
                                          gaze=(-1, 0.3 * look), arms=((18, 8), (18, 8)) if look < 0.5 else ((60, 60), (60, 60))),
             lean=-8 * look)
    im = V.cam(cv, 1.9, kf(t, [(0, 640), (3.0, 820), (3.5, 900)]), 680)
    return label(im, 'LƯỚT ĐIỆN THOẠI', 'đi chậm, cúi nhìn, ngón cái vuốt · dừng lại, quay khoe bạn')


W_NA2 = Walker([(0, 420), (0.3, 420), (3.0, 860), (5.0, 860)], stride=12, lift=10)


# ================================================================== CLIP 4: Tùng uống nước, Khang chờ sốt ruột
def c_drink(t):
    cv = V.BG['gym'].copy()
    # Khang đứng chờ, gõ chân, khoanh tay → chỉ đồng hồ
    tap = max(0, math.sin(t * 8)) * 38
    watch = kf(t, [(0, 0.0), (2.9, 0.0), (3.2, 1.0), (3.9, 1.0), (4.2, 0.0)])
    hk = hum(cv, 'khang', 1000, 860, 0.5, dict(gaze=(-1, 0) if watch < 0.5 else (-0.6, 0.8), mouth='flat', eyes='open', lid=0.5,
                                                 tilt=kf(t, [(1.4, 0.0), (1.8, 10.0), (2.6, 10.0), (2.9, 0.0)]),
                                                 hold={'R': 'racket'}, prop_ang={'R': -60},
                                                 arm_to={'L': kf(watch, [(0, (-10, -270)), (1, (-20, -330))], lin), 'R': (30, -275)},
                                                 feet={'L': (-24, -18), 'R': (24, -18 - tap)}))
    hk.draw()
    # Tùng: cầm chai lên (0.5–1.3) → ngửa cổ tu (1.3–3.3, nghiêng chai dần) → hạ (3.3–3.8) → quệt miệng (3.9–4.5) → "khà"
    # miệng chai (cách tâm tay 74) đặt ĐÚNG miệng Tùng (cục bộ ≈ (0, -297)); tu dần: tay nâng, đáy chai dốc lên
    hand = kf(t, [(0, (120, -170)), (0.5, (120, -170)), (1.0, (125, -290)), (1.35, (110, -330)), (3.3, (100, -360)),
                  (3.8, (120, -190))])
    ang = kf(t, [(0, 0.0), (0.5, 0.0), (1.0, -50.0), (1.35, -107.0), (3.3, -122.0), (3.8, 0.0)])
    lean = kf(t, [(0, 0.0), (1.1, 0.0), (1.6, -7.0), (3.3, -8.0), (3.8, 0.0)])
    glug = abs(math.sin(t * 7)) * 0.09 if 1.6 < t < 3.3 else 0
    lw = kf(t, [(0, (-80, -200)), (3.9, (-80, -200)), (4.2, (60, -300)), (4.5, (-60, -300)), (4.8, (-80, -200))])
    st = dict(hold={'R': 'bottle'}, prop_ang={'R': ang}, arm_to={'R': hand, 'L': lw}, lean=lean, crouch=glug + 0.05,
              tilt=kf(t, [(1.1, 0.0), (1.6, -17.0), (3.3, -19.0), (3.8, 0.0)]), elbow={'R': 'out'}, prop_k=1.56,
              eyes='closed' if 1.5 < t < 3.4 else ('happy' if t > 4.5 else 'open'), gaze=(0, -1) if t < 3.4 else (1, 0),
              mouth='o' if t < 3.4 else ('D' if t > 4.5 else 'smile'), sweat=True)
    hum(cv, 'tung', 640, 860, 0.5, st).draw()
    im = V.cam(cv, 1.7, 820, 650)
    return label(im, 'UỐNG NƯỚC', 'nhấc chai · ngửa cổ tu ực ực · hạ chai · quệt miệng · Khang chờ gõ chân')


# ================================================================== CLIP 5: Gâu thấy cầu → chạy → nhảy ngậm cầu
def c_catch(t):
    cv = V.BG['gym'].copy()
    T_RUN, T_JUMP, T_CATCH, T_LAND = 1.6, 2.7, 3.0, 3.35
    JH = 300

    def gx(tt):
        return kf(tt, [(0, 380), (T_RUN, 380), (T_JUMP, 980, lin), (T_LAND, 1120, eout), (T_LAND + 0.6, 1160)])

    def gy(tt):                                   # chân Gâu (màn hình): lấy đà – bay – tiếp đất nhún
        y = 868
        y += kf(tt, [(1.1, 0.0), (1.45, 14.0), (1.65, 0.0)]) + kf(tt, [(2.42, 0.0), (2.66, 40.0), (2.72, 0.0)])
        if T_JUMP <= tt <= T_LAND:
            k = (tt - T_JUMP) / (T_LAND - T_JUMP)
            y -= JH * 4 * k * (1 - k)
        y += kf(tt, [(T_LAND, 0.0), (T_LAND + 0.1, 18.0), (T_LAND + 0.35, 0.0)])
        return y
    w = Walker([(0, 380), (T_RUN, 380), (T_JUMP, 980, lin), (T_LAND, 1120, eout), (T_LAND + 0.6, 1160)], run=True)
    x = gx(t)
    ph = w.phase(t) / 0.5 / 70 * math.pi
    mv = min(1, abs(gx(t + 1 / 60) - x) * 60 / 40) if t < T_JUMP else 0
    feet, bob = dog_gait(ph, mv, run=True)
    if T_JUMP <= t <= T_LAND:
        feet = ((-26, 34), (-10, 30))             # bay: chân co, duỗi ra sau
    y = gy(t) - bob
    mouth_at = lambda tt: (gx(tt) + 9, gy(tt) - 111)
    (sx, sy), ang = arc(t, -0.2, T_CATCH, (1560, 620), mouth_at(T_CATCH), 330)
    see = kf(t, [(0, 0.0), (0.4, 0.0), (1.0, 1.0)])
    flying = T_JUMP <= t <= T_LAND
    st = dict(flat=True, eyes='open' if t < 0.5 else 'wide', big=1 + 0.25 * see, gaze=(1, -1) if t < T_JUMP else (1, -0.4),
              mouth='tongue' if T_RUN < t < T_JUMP else ('open' if t < T_CATCH else 'smirk'), mo=1.0, feet=feet,
              arms=((50 + 80 * math.sin(ph) * mv, 90), (50 - 80 * math.sin(ph) * mv, 90)) if not flying else ((150, 30), (150, 30)))
    lean = 22 * mv + (6 * math.sin(math.pi * (t - T_JUMP) / (T_LAND - T_JUMP)) if flying else 0)
    if mv > 0.3:
        run_fx(cv, x, gy(t), t, ph)
    # nén – dãn: lấy đà nén, bật lên dãn, trên không co lại, chạm đất nén rồi đàn hồi
    sq = kf(t, [(2.42, 1.0), (2.66, 0.84), (2.74, 1.18), (2.9, 1.04), (T_LAND - 0.05, 1.08), (T_LAND + 0.06, 0.8),
                (T_LAND + 0.2, 1.06), (T_LAND + 0.32, 1.0)])
    if T_RUN < t < T_JUMP:                         # chạy: nén/dãn theo nhịp bước
        sq = 1 + 0.08 * math.cos(2 * ph)
    if flying:
        lean = 18 * (1 - 2 * (t - T_JUMP) / (T_LAND - T_JUMP))   # chúi lên khi bật, chúi xuống khi rơi (cung bay)
    dog_draw(cv, x, y, 0.5, st, lean=lean, sq=sq)
    if t < T_CATCH:
        pts = [arc(t - i * 0.016, -0.2, T_CATCH, (1560, 620), mouth_at(T_CATCH), 330)[0] for i in range(7, 0, -1)]
        trail(cv, pts + [(sx, sy)])
        V.shuttle(cv, sx, sy, ang, 1.0)
    else:
        mx, my = x + 9, y - 111
        V.shuttle(cv, mx + 18, my + 2, 90, 1.0)     # ngậm ngang
    if 0.4 < t < 1.2:      # mắt sáng lên: tia lấp lánh phẳng
        V.sparkles(cv, [(x - 30, 868 - 150), (x + 40, 868 - 160)], t)
    cx = kf(t, [(0, 520), (T_RUN - 0.2, 520), (T_RUN + 0.3, 1.0)], lin)
    cx = 520 + (gx(t - 0.12) + 90 - 520) * ease(cx) if t > T_RUN - 0.2 else 520     # bám Gâu, trễ nhẹ
    cy = kf(t, [(0, 640), (2.5, 690), (2.85, 520), (3.1, 540), (T_LAND + 0.3, 700)])
    im = V.cam(cv, kf(t, [(0, 1.6), (1.4, 1.9), (T_RUN, 1.7), (4.6, 1.7)]), cx, cy)
    return label(im, 'GÂU CHẠY + NHẢY NGẬM CẦU', 'thấy cầu, mắt sáng · lấy đà · chạy · bật nhảy · ngậm gọn · tiếp đất')


# ================================================================== CLIP 6: chụp hình chung (nhiều người, chen vào khung)
def c_selfie(t):
    return label(selfie_raw(t).convert('RGBA'), 'CHỤP HÌNH CHUNG', 'Na giơ máy · Khang khoác vai · Tùng chạy chen · Gâu nhảy vào · tách!')


def selfie_raw(t):
    cv = V.BG['gym'].copy()
    # Na giơ máy (0–0.8). Khang từ trái trượt vào khoác vai (0.8–1.8). Tùng từ phải chạy vào chen (1.4–2.4), đẩy Khang lệch.
    # Gâu nhảy lên từ dưới (2.4–2.8). Bấm chụp 3.2 (chớp trắng) → ảnh đóng khung.
    na_x = 800
    kx = kf(t, [(0, 380), (0.8, 380), (1.8, 700), (2.35, 700), (2.55, 630)])
    w = Walker([(0, 380), (0.8, 380), (1.8, 700), (2.35, 700), (2.55, 630)], stride=20, lift=14)
    _, ws, _, _ = w.pose(t, 0.5, 22)
    sk = dict(feet=ws['feet'], lean=ws['lean'] + kf(t, [(1.8, 0.0), (2.2, 8.0), (2.35, 8.0), (2.55, -12.0), (2.9, -4.0)]), crouch=ws['crouch'],
              gaze=(0.5, 0.2) if t < 2.3 else (0.3, -0.2), mouth='smirk' if t < 3.0 else 'grin',
              arm_to={'R': kf(t, [(0, (90, -300)), (1.6, (90, -300)), (2.1, (128, -262)), (2.35, (128, -262)), (2.6, (100, -200))]),
                      'L': (-80, -300)})
    hum(cv, 'khang', kx, 870, 0.5, sk).draw()
    tx = kf(t, [(0, 1400), (1.4, 1400), (2.4, 990, eout)])
    wt = Walker([(0, 1400), (1.4, 1400), (2.4, 990, eout)], stride=16, lift=14, run=True, fat=True)
    _, wts, _, _ = wt.pose(t, 0.5, 30)
    stt = dict(feet=wts['feet'], lean=wts['lean'] + kf(t, [(2.3, 0.0), (2.6, -10.0)]), crouch=wts['crouch'],
               mouth='D' if t > 2.4 else 'open', mo=0.5, eyes='happy' if t > 2.6 else 'open', gaze=(-1, -0.2),
               arm_to={'L': kf(t, [(0, (-90, -200)), (2.3, (-90, -200)), (2.6, (-130, -380))]), 'R': (110, -200)})
    if t < 2.4:
        stt['arms'] = wts['arms']
        stt.pop('arm_to')
    hum(cv, 'tung', tx, 880, 0.5, stt).draw()
    up = kf(t, [(0, (120, -250)), (0.8, (130, -560), eout)])
    na = hum(cv, 'na', na_x, 860, 0.5, dict(hold={'R': 'phone'}, arm_to={'R': up, 'L': (-60, -330)}, gaze=(0.5, -1),
                                            mouth='D' if t > 0.6 else 'smile', eyes='happy' if t > 2.9 else 'open', lean=-3))
    na.draw()
    gj = kf(t, [(0, 200.0), (2.4, 200.0), (2.75, 0.0, eout), (2.85, 8.0), (2.95, 0.0)])
    Dog(cv, 900, 900 + gj, 0.46, dict(flat=True, mouth='tongue', eyes='happy' if t > 2.9 else 'open', gaze=(0, -1),
                                      hand_to={'R': (60, -230)})).draw()
    im = V.cam(cv, 1.5, 760, 610)
    if 3.2 <= t < 3.35:
        im = Image.blend(im.convert('RGB'), Image.new('RGB', im.size, (255, 255, 255)), 1 - (t - 3.2) / 0.15)
    if t >= 3.35:          # ảnh đóng băng thu nhỏ có viền trắng như ảnh vừa chụp
        if 'snap' not in SNAP:
            SNAP['snap'] = selfie_raw(3.19)
        k = ease((t - 3.35) / 0.6)
        ph_ = SNAP['snap'].convert('RGB')
        sz = (int(1280 * (1 - 0.35 * k)), int(720 * (1 - 0.35 * k)))
        bg = V.cam(V.BG['gym'].copy(), 1.5, 760, 610).convert('RGB')
        fr = Image.new('RGB', (sz[0] + 24, sz[1] + 24), (255, 255, 255))
        fr.paste(ph_.resize(sz), (12, 12))
        fr = fr.convert('RGBA').rotate(-4 * k, expand=True, resample=Image.BICUBIC)
        bg.paste(fr, ((1280 - fr.size[0]) // 2, (720 - fr.size[1]) // 2), fr)
        im = bg
    return im


SNAP = {}

CLIPS = [('di-bo', c_walk, 5.2), ('danh-qua-lai', c_rally, 8.6), ('luot-dien-thoai', c_phone, 5.0),
         ('uong-nuoc', c_drink, 5.2), ('gau-ngam-cau', c_catch, 4.6), ('chup-hinh', c_selfie, 4.6)]


def frame(i):
    t = i / FPS
    for name, fn, dur in CLIPS_RUN:
        if t < dur:
            return fn(t)
        t -= dur
    return CLIPS_RUN[-1][1](CLIPS_RUN[-1][2] - 0.01)


G = {}


def init(d, names):
    global CLIPS_RUN
    V.build()
    G['d'] = d
    CLIPS_RUN = [c for c in CLIPS if c[0] in names]


def job(i):
    frame(i).convert('RGB').save(os.path.join(G['d'], 'f%05d.jpg' % i), quality=92)


CLIPS_RUN = CLIPS


def main():
    os.makedirs(OUT, exist_ok=True)
    names = [c[0] for c in CLIPS]
    if '--clip' in sys.argv:
        names = sys.argv[sys.argv.index('--clip') + 1].split(',')
    if '--khung' in sys.argv:          # bảng khung hình: mỗi clip 8 khung đều nhau
        init(None, names)
        for name, fn, dur in CLIPS_RUN:
            ts = [dur * k / 8 for k in range(8)]
            sheet = Image.new('RGB', (4 * 480, 2 * 270))
            dr = ImageDraw.Draw(sheet)
            for k, tt in enumerate(ts):
                sheet.paste(fn(tt).convert('RGB').resize((480, 270)), ((k % 4) * 480, (k // 4) * 270))
                dr.text(((k % 4) * 480 + 6, (k // 4) * 270 + 250), '%.2fs' % tt, fill=(255, 255, 0))
            p = os.path.join(OUT, 'khung-%s.jpg' % name)
            sheet.save(p, quality=88)
            print(p)
        return
    fdir = tempfile.mkdtemp(prefix='dongtac-')
    sel = [c for c in CLIPS if c[0] in names]
    n = int(sum(c[2] for c in sel) * FPS)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init, initargs=(fdir, names)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n), chunksize=4)):
            if k % 240 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    out = os.path.join(OUT, 'dong-tac.mp4' if len(sel) > 1 else 'dong-tac-%s.mp4' % sel[0][0])
    subprocess.run([V.ffmpeg(), '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, 'f%05d.jpg'),
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', out], check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
