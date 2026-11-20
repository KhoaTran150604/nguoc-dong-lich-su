"""Gâu Nghệ #1 – Các kiểu người khi đi đánh cầu lông (~1:45).
Kịch bản: docs/videos/gau-nghe/01-cac-kieu-nguoi-cau-long.md · Giọng: build/thu-hoathinh/cau-long/thoai.wav/.json
(thoai_song_tu.py loi.json – giahuy/hamy/tiendat/quangminh/huuduc). Lối vẽ: sổ tay sitcom VN (mục 9: nhiều nhân vật).

Toàn bộ cảnh vẽ trên MỘT nhà thi đấu 1600x900 (SS=2) rồi máy quay cắt khung/zoom → cỡ cảnh khác nhau.
Chạy: python scripts/hoathinh/cau_long_video.py [--khung 3 10.5 ...]   → build/thu-hoathinh/cau-long/cau-long.mp4
"""
import argparse
import copy
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from multiprocessing import Pool

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ngo_quyen_can_canh import SS, INK, hx, ellipse_pts  # noqa: E402
from gau_nghe_avatar_tbm import poly, pline  # noqa: E402
from gau_nghe_van import Dog, ROOT  # noqa: E402
import gau_nghe_khung_thu as K  # noqa: E402
import sitcom_fx as F  # noqa: E402
import meo_nghe_cach_dieu as M  # noqa: E402
from nguoi import Human, CAST, prop, blob  # noqa: E402

DIR = os.path.join(ROOT, 'build', 'thu-hoathinh', 'cau-long')
FPS = 30
W, H = 1600, 900
OW, OH = 1280, 720
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')
FONT_B = os.path.join(ROOT, 'fonts', 'BeVietnamPro-ExtraBold.ttf')
if not os.path.exists(FONT_B):
    FONT_B = os.path.join(ROOT, 'fonts', 'BeVietnamPro-Bold.ttf') if os.path.exists(os.path.join(ROOT, 'fonts', 'BeVietnamPro-Bold.ttf')) else FONT
# nghỉ thêm TRƯỚC câu i (giây) – chỗ cho hành động không lời
PRE = {0: 1.4, 1: 0.4, 3: 1.5, 4: 0.4, 7: 0.4, 9: 0.2, 10: 0.4, 12: 2.0, 13: 0.4, 15: 0.3, 16: 0.4, 18: 2.2, 19: 2.4, 21: 0.6}
TAIL = 2.8
TITLES = {1: ('KIỂU 1', 'Trang bị hơn tuyển quốc gia'), 4: ('KIỂU 2', 'Đến để chụp hình'),
          7: ('KIỂU 3', 'Trọng tài kiêm luật sư'), 10: ('KIỂU 4', '"Đánh nhẹ thôi mà"'),
          13: ('KIỂU 5', 'Chuyên gia nghỉ giải lao'), 16: ('KIỂU 6', 'Bình luận viên'), 18: ('KIỂU 7', '... là Gâu Nghệ')}


# ------------------------------------------------------------------ giọng + mốc thời gian
def load_voice():
    d = json.load(open(os.path.join(DIR, 'thoai.json'), encoding='utf-8'))
    v, sr = sf.read(os.path.join(DIR, 'thoai.wav'), dtype='float32')
    parts, prev, shift = [], 0, 0.0
    for i, ln in enumerate(d['lines']):
        ps = PRE.get(i, 0.0)
        cut = max(prev, int((ln['start'] - 0.05) * sr))
        parts += [v[prev:cut], np.zeros(int(ps * sr), np.float32)]
        prev = cut
        shift += ps
        ln['start'] = round(ln['start'] + shift, 3)
        ln['end'] = round(ln['end'] + shift, 3)
        ln['who'] = ln['seg'].split('|')[1]
    parts.append(v[prev:])
    v2 = np.concatenate(parts)
    dur = d['lines'][-1]['end'] + TAIL
    v2 = np.concatenate([v2, np.zeros(max(0, int(dur * sr) - v2.size), np.float32)])[:int(dur * sr)]
    hop = sr // 30
    env = [float(np.sqrt(np.mean(v2[k:k + hop] ** 2))) for k in range(0, v2.size, hop)]
    mx = max(env) or 1
    return d['lines'], [e / mx for e in env], v2, sr, round(dur, 2)


L, ENV, VOICE, SR, DUR = load_voice()
T = [ln['start'] for ln in L]
E = [ln['end'] for ln in L]

SHOTS = [
    (0.0, 'cold'), (1.4, 'open'), (T[0] + 1.3, 'intro'),
    (T[1] - 0.25, 'title1'), (T[2] - 0.2, 'price'), (E[2] + 0.2, 'miss'),
    (T[4] - 0.25, 'title2'), (T[5] - 0.2, 'selfie'), (T[6] - 0.2, 'eat'),
    (T[7] - 0.25, 'title3'), (T[8] - 0.2, 'referee'), (T[9] - 0.15, 'floor'), (T[9] + (E[9] - T[9]) * 0.5, 'deadpan'),
    (T[10] - 0.25, 'title4'), (T[11] - 0.2, 'sweet'), (E[11] + 0.15, 'smashface'), (E[11] + 0.75, 'smash'), (E[11] + 1.5, 'ko'),
    (T[13] - 0.25, 'title5'), (T[14] - 0.2, 'rest'), (T[15] - 0.2, 'clock'),
    (T[16] - 0.25, 'title6'), (T[17] - 0.2, 'mic'), (E[17] + 0.2, 'flop'), (E[17] + 1.5, 'fly'),
    (T[18] - 0.25, 'chase'), (T[19] - 0.6, 'thay'), (T[20] - 0.15, 'gauclose'),
    (T[21] - 0.3, 'lineup'),
]


def shot_at(t):
    k = 0
    for i, (t0, _) in enumerate(SHOTS):
        if t >= t0:
            k = i
    t0 = SHOTS[k][0]
    t1 = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else DUR
    return SHOTS[k][1], t - t0, t1 - t0


def env_at(t):
    k = int(t * 30)
    return ENV[k] if 0 <= k < len(ENV) else 0.0


def mo_of(who, t):
    for ln in L:
        if ln['who'] == who and ln['start'] <= t <= ln['end']:
            return min(1.0, max(env_at(t), 0.6 * env_at(t - 1 / 30)) * 1.7)
    return 0.0


def talking(who, t):
    return any(ln['who'] == who and ln['start'] <= t <= ln['end'] for ln in L)


def blink(t, ph=0.0):
    return ((t + ph) % 3.3) < 0.11


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def pop(x):            # bật vào có nảy
    x = min(1.0, max(0.0, x))
    return 1 + 0.25 * math.sin(x * math.pi) * (1 - x) * 2 if x < 1 else 1.0


# ------------------------------------------------------------------ nhà thi đấu
NET_X = 860
CLOCK = (1480, 300)


def gym():
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(cv)
    poly(d, [(0, 0), (W, 0), (W, 440), (0, 440)], '#E9E0C9', ol=None)                      # tường trên
    for x in range(0, W + 1, 200):                                                          # cột tường
        poly(d, [(x - 14, 40), (x + 14, 40), (x + 14, 440), (x - 14, 440)], '#DCD1B6', w=2)
    poly(d, [(-10, -10), (W + 10, -10), (W + 10, 46), (-10, 46)], '#5E646E', w=2.4)          # dầm mái
    for x in range(0, W, 80):
        pline(d, [(x, 46), (x + 40, 0)], '#4A505A', 3)
    for i, x in enumerate((470, 720, 970, 1220)):                                           # cửa sổ cao
        poly(d, [(x, 80), (x + 170, 80), (x + 170, 220), (x, 220)], '#7A8A90', w=2.6)
        poly(d, [(x + 10, 90), (x + 160, 90), (x + 160, 210), (x + 10, 210)], '#BFE3EE', w=2)
        pline(d, [(x + 85, 90), (x + 85, 210)], '#7A8A90', 5)
        pline(d, [(x + 10, 150), (x + 160, 150)], '#7A8A90', 4)
        pline(d, [(x + 24, 104), (x + 50, 104)], '#FFFFFF', 3)
    poly(d, [(560, 258), (1190, 258), (1190, 322), (560, 322)], '#B3261E', w=2.6)          # băng rôn
    d.text((875 * SS, 291 * SS), 'NHÀ THI ĐẤU · THPT BẾN ĐÒ', font=ImageFont.truetype(FONT_B, 34 * SS),
           fill=hx('#F4EFE4'), anchor='mm')
    poly(d, [(1230, 340), (1350, 340), (1350, 420), (1230, 420)], '#F4EFE4', w=2.2)          # bảng nội quy
    d.text((1290 * SS, 356 * SS), 'NỘI QUY', font=ImageFont.truetype(FONT_B, 14 * SS), fill=hx('#B3261E'), anchor='mm')
    for y in (374, 388, 402):
        pline(d, [(1246, y), (1334, y)], '#9A9080', 2)
    F.crack(d, 330, 160, 70, seed=3)
    F.crack(d, 1560, 380, 50, seed=8)
    # đồng hồ treo tường (kiểu 5 quay nhanh – kim vẽ riêng)
    poly(d, ellipse_pts(*CLOCK, 40, 40, n=48), '#FFFFFF', w=4)
    for k in range(12):
        a = k * math.pi / 6
        pline(d, [(CLOCK[0] + 31 * math.sin(a), CLOCK[1] - 31 * math.cos(a)), (CLOCK[0] + 36 * math.sin(a), CLOCK[1] - 36 * math.cos(a))], INK, 2.4)
    # tường dưới xanh + sọc
    poly(d, [(0, 440), (W, 440), (W, 610), (0, 610)], '#4E8F6E', w=2.4)
    pline(d, [(0, 456), (W, 456)], '#F4EFE4', 5)
    for x in range(60, W, 240):
        F.crack(d, x + 90, 520, 40, seed=x)
    # khán đài nhựa bên trái (3 bậc)
    for k, (y, x1) in enumerate(((470, 470), (530, 440), (590, 410))):
        poly(d, [(-20, y), (x1, y), (x1, y + 60), (-20, y + 60)], '#8C949E', w=2.4)
        for x in range(10, x1 - 30, 62):
            poly(d, [(x, y - 26), (x + 44, y - 26), (x + 48, y + 4), (x - 4, y + 4)], ['#2F6FB5', '#3B7FC5'][k % 2], w=2)
    # cửa đôi bên phải
    poly(d, [(1430, 380), (1590, 380), (1590, 610), (1430, 610)], '#3F7A5E', w=2.6)
    pline(d, [(1510, 380), (1510, 610)], INK, 3)
    for x in (1495, 1525):
        pline(d, [(x, 490), (x, 520)], '#C9CDD2', 4)
    # sàn: lề gỗ + sân xanh + vạch (nhìn ngang sân, lưới ở giữa)
    poly(d, [(-20, 610), (W + 20, 610), (W + 20, 920), (-20, 920)], '#C89A64', w=2.6)
    for y in (630, 700, 800):
        pline(d, [(-20, y), (W + 20, y)], '#B5875A', 1.6)
    poly(d, [(110, 650), (1610, 650), (1640, 892), (60, 892)], '#3F8E6E', w=2.4)
    for a, b in (((120, 660), (1600, 660)), ((70, 884), (1630, 884)), ((120, 660), (70, 884)), ((96, 772), (1615, 772)),
                 ((NET_X - 210, 660), (NET_X - 222, 884)), ((NET_X + 210, 660), (NET_X + 222, 884)), ((1600, 660), (1630, 884))):
        pline(d, [a, b], '#F4F4F0', 4)
    F.window_beam(cv, [(500, 640), (680, 640), (760, 900), (560, 900)], 1.10)
    F.window_beam(cv, [(1010, 640), (1190, 640), (1290, 900), (1080, 900)], 1.10)
    K.shade(cv, [(-20, 610), (W + 20, 610), (W + 20, 628), (-20, 628)], 0.8)
    return cv


def net(cv):
    """Lưới (vẽ sau nhân vật đứng phía sau lưới)."""
    d = ImageDraw.Draw(cv)
    x0, x1 = NET_X - 4, NET_X + 4
    for (x, yb, ht) in ((x0, 660, 150), (x1, 884, 190)):
        poly(d, [(x - 6, yb - ht), (x + 6, yb - ht), (x + 6, yb), (x - 6, yb)], '#2A2D34', w=2)
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    top0, top1 = (x0, 660 - 150), (x1, 884 - 190)
    bot0, bot1 = (x0, 660 - 80), (x1, 884 - 100)
    dl.polygon([(p[0] * SS, p[1] * SS) for p in (top0, top1, bot1, bot0)], fill=(30, 30, 36, 90))
    for k in np.linspace(0, 1, 16):
        a = (top0[0] + (top1[0] - top0[0]) * k, top0[1] + (top1[1] - top0[1]) * k)
        b = (bot0[0] + (bot1[0] - bot0[0]) * k, bot0[1] + (bot1[1] - bot0[1]) * k)
        dl.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=(30, 30, 36, 200), width=2 * SS)
    cv.alpha_composite(lay)
    pline(ImageDraw.Draw(cv), [top0, top1], '#F4F4F0', 6)


def clock_hands(cv, ang):
    d = ImageDraw.Draw(cv)
    cx, cy = CLOCK
    pline(d, [(cx, cy), (cx + 20 * math.sin(ang / 12), cy - 20 * math.cos(ang / 12))], INK, 5)
    pline(d, [(cx, cy), (cx + 30 * math.sin(ang), cy - 30 * math.cos(ang))], '#B3261E', 3)


# ------------------------------------------------------------------ đạo cụ, hiệu ứng
def shuttle(cv, x, y, ang=0.0, k=1.0):
    """Quả cầu: đầu bần tròn + váy lông hình nón; ang = hướng bay (độ, 0 = đầu cầu chúc xuống)."""
    a = math.radians(ang)
    ux, uy = -math.sin(a), math.cos(a)               # hướng đầu bần
    px, py = -uy, ux
    tip = (x + ux * 10 * k, y + uy * 10 * k)
    skirt = [(x - ux * 4 * k + px * 9 * k, y - uy * 4 * k + py * 9 * k), (x - ux * 34 * k + px * 20 * k, y - uy * 34 * k + py * 20 * k),
             (x - ux * 34 * k - px * 20 * k, y - uy * 34 * k - py * 20 * k), (x - ux * 4 * k - px * 9 * k, y - uy * 4 * k - py * 9 * k)]
    blob(cv, [skirt], '#FBFBF6', lw=2.0)
    for s_ in (-0.5, 0, 0.5):
        M.line(cv, [(x - ux * 6 * k + px * 6 * s_ * k, y - uy * 6 * k + py * 6 * s_ * k),
                    (x - ux * 32 * k + px * 18 * s_ * k, y - uy * 32 * k + py * 18 * s_ * k)], 1.4 * k, hx('#B8B8B0'))
    M.ell(cv, tip, 9 * k, 9 * k, fill=hx('#F2E6CC'), ow=2.6 * k)


def stars(cv, x, y, r, t, n=3):
    d = ImageDraw.Draw(cv)
    for i in range(n):
        a = t * 5 + i * 2 * math.pi / n
        cx, cy = x + r * math.cos(a), y + r * 0.35 * math.sin(a)
        pts = []
        for k in range(10):
            rr = 13 if k % 2 == 0 else 5.5
            b = k * math.pi / 5 - math.pi / 2
            pts.append((cx + rr * math.cos(b), cy + rr * math.sin(b)))
        poly(d, pts, '#FFD34D', w=2.2)


def sparkles(cv, pts, t):
    d = ImageDraw.Draw(cv)
    for i, (x, y) in enumerate(pts):
        k = 0.6 + 0.4 * math.sin(t * 8 + i * 1.7)
        for a in (0, math.pi / 2):
            pline(d, [(x - 14 * k * math.cos(a), y - 14 * k * math.sin(a)), (x + 14 * k * math.cos(a), y + 14 * k * math.sin(a))], '#FFF3B0', 4)


def zzz(cv, x, y, t):
    f = ImageFont.truetype(FONT_B, 30 * SS)
    d = ImageDraw.Draw(cv)
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        d.text(((x + 30 * ph + i * 6) * SS, (y - 70 * ph) * SS), 'Z', font=f, fill=hx('#3B5E8C'), stroke_width=2 * SS,
               stroke_fill=hx('#F4EFE4'))


def speed_bg(cv, cx, cy, t, col1='#B3261E', col2='#E8553A'):
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 0, W * SS, H * SS], fill=hx(col1) + (255,))
    rnd = np.random.RandomState(int(t * 12))
    for k in range(34):
        a = k * 2 * math.pi / 34 + rnd.uniform(-0.05, 0.05)
        wd = rnd.uniform(0.02, 0.05)
        pts = [(cx + 160 * math.cos(a), cy + 160 * math.sin(a)), (cx + 2000 * math.cos(a - wd), cy + 2000 * math.sin(a - wd)),
               (cx + 2000 * math.cos(a + wd), cy + 2000 * math.sin(a + wd))]
        d.polygon([(px * SS, py * SS) for px, py in pts], fill=hx(col2) + (255,))


def fly(cv, x, y, t, k=1.0):
    d = ImageDraw.Draw(cv)
    w = (9 + 5 * math.sin(t * 60)) * k
    for s_ in (-1, 1):
        d.ellipse([(x + (s_ * 4 - 6) * k) * SS, (y - w - 4 * k) * SS, (x + (s_ * 4 + 6) * k) * SS, (y - 2 * k) * SS],
                  fill=(220, 230, 240, 255), outline=INK + (255,), width=int(2 * k * SS))
    d.ellipse([(x - 7 * k) * SS, (y - 5 * k) * SS, (x + 7 * k) * SS, (y + 5 * k) * SS], fill=INK + (255,))


def dog_hand(dog, side, a1, a2):
    return dog.P(*dog.arm_pts(side, a1, a2)[-1])


def rot_layer(draw_fn, cx, cy, ang):
    lay = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    draw_fn(lay)
    return lay.rotate(ang, center=(cx * SS, cy * SS), resample=Image.BICUBIC)


def gau(cv, x, y, s, t, **st):
    base = dict(flat=True, mouth='talk', mo=mo_of('gau', t), rest=st.pop('rest', 'smirk'))
    base.update({k: v for k, v in st.items() if v is not None})
    if base.get('mouth') == 'o':
        base['mouth'] = 'open'
    if blink(t, 0.3) and 'lid' not in base and base.get('eyes') not in ('happy',):
        base['lid'] = (1.0, 1.0)
    dg = Dog(cv, x, y, s, base)
    dg.draw()
    return dg


def hum(cv, key, x, y, s, t, **st):
    st.setdefault('mouth', 'talk' if talking(key, t) else st.get('rest', 'smile'))
    st.setdefault('mo', mo_of(key, t))
    st.pop('rest', None)
    if blink(t, hash(key) % 7 * 0.4) and st.get('eyes', 'open') == 'open' and not st.get('lid'):
        st['eyes'] = 'closed'
    hm = Human(cv, x, y, s * (1.13 if key == 'khang' else 1.0), CAST[key], st)
    hm.draw()
    return hm


# ------------------------------------------------------------------ máy quay + chữ
BG = {}


def build():
    if not BG:
        BG['gym'] = gym()


def cam(cv, z, cx, cy, shake=0.0, t=0.0):
    w, h = W / z, H / z
    cx += shake * math.sin(t * 91)
    cy += shake * math.cos(t * 77)
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return cv.crop((int(x0 * SS), int(y0 * SS), int((x0 + w) * SS), int((y0 + h) * SS))).resize((OW, OH), Image.LANCZOS)


def title_card(im, k, big, small):
    if k <= 0:
        return
    s = pop(k) * min(1, k * 1.6)
    lay = Image.new('RGBA', (900, 230), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([250, 8, 650, 92], 16, fill=hx('#B3261E') + (255,), outline=INK + (255,), width=6)
    d.text((450, 50), big, font=ImageFont.truetype(FONT_B, 52), fill=hx('#F4EFE4'), anchor='mm')
    fs = ImageFont.truetype(FONT_B, 46)
    tw = d.textlength(small, font=fs)
    d.rounded_rectangle([450 - tw / 2 - 34, 104, 450 + tw / 2 + 34, 200], 18, fill=hx('#F4EFE4') + (255,), outline=INK + (255,), width=6)
    d.text((450, 152), small, font=fs, fill=INK, anchor='mm')
    lay = lay.resize((max(1, int(900 * s)), max(1, int(230 * s))), Image.LANCZOS).rotate(-2, expand=True, resample=Image.BICUBIC)
    im.paste(lay, (int(OW / 2 - lay.width / 2), int(130 - lay.height / 2)), lay)


def tag(im, k, text, x, y, rot=4, col='#F4EFE4', fg='#14110F', size=42):
    if k <= 0:
        return
    s = pop(k) * min(1, k * 1.6)
    f = ImageFont.truetype(FONT_B, size)
    tw = ImageDraw.Draw(im).textlength(text, font=f)
    lay = Image.new('RGBA', (int(tw + 80), size + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([6, 6, tw + 74, size + 54], 14, fill=hx(col) + (255,), outline=INK + (255,), width=5)
    d.text(((tw + 80) / 2, (size + 60) / 2), text, font=f, fill=hx(fg), anchor='mm')
    lay = lay.resize((max(1, int(lay.width * s)), max(1, int(lay.height * s))), Image.LANCZOS).rotate(rot, expand=True, resample=Image.BICUBIC)
    im.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)


def letterbox(im, k=1.0):
    d = ImageDraw.Draw(im)
    h = int(90 * k)
    d.rectangle([0, 0, OW, h], fill=(10, 8, 8))
    d.rectangle([0, OH - h, OW, OH], fill=(10, 8, 8))


def flash(im, a):
    if a > 0:
        im.paste(Image.blend(im, Image.new(im.mode, im.size, (255, 255, 255) if im.mode == 'RGB' else (255, 255, 255, 255)), min(1, a)))


# ------------------------------------------------------------------ các cảnh
def s_open(t, lt, dur):
    cv = BG['gym'].copy()
    hum(cv, 'tung', 200, 590, 0.42, t, sit=True, arm_to={'R': (125, -270)}, hold={'R': 'bottle'}, prop_ang={'R': 0}, rest='smile')
    hum(cv, 'khang', 1090, 770, 0.45, t, arms=((14, 6), (70 + 50 * math.sin(t * 4), 150 + 30 * math.sin(t * 4))),
        hold={'R': 'racket'}, prop_ang={'R': 10 + 40 * math.sin(t * 4)}, rest='grin', gaze=(-1, 0))
    net(cv)
    up = 150 + 25 * math.sin(t * 3)
    hum(cv, 'na', 1330, 800, 0.46, t, arms=((up, 175), (up, 175)), eyes='happy', rest='smile')
    dg = gau(cv, 600, 860, 0.5, t, arms=((18, 8), (60, 150)), gaze=(0, 0), rest='smirk')
    prop(cv, 'racket', dog_hand(dg, 1, 60, 150), 0.55, 15)
    z = 1.0 + 0.25 * ease(lt / dur)
    return cam(cv, z, 800 - 160 * ease(lt / dur), 520 + 120 * ease(lt / dur))


TITLE_POSE = {
    1: ('khang', dict(arm_to={'R': (100, -440)}, hold={'R': 'racket', 'L': 'bag'}, prop_ang={'R': 5}, rest='grin', gaze=(0, 0))),
    2: ('na', dict(arm_to={'R': (40, -400)}, hold={'R': 'phone'}, rest='D', eyes='happy', lean=-6)),
    3: ('tung', dict(arm_to={'R': (128, -240)}, hold={'R': 'magnifier'}, prop_ang={'R': 40}, eyes='wide', rest='o')),
    4: ('khang', dict(arms=((14, 6), (40, 140)), hold={'R': 'racket'}, prop_ang={'R': -20}, rest='smile', eyes='happy')),
    5: ('tung', dict(arm_to={'R': (125, -270)}, hold={'R': 'bottle'}, prop_ang={'R': 0}, eyes='happy', rest='smile')),
    6: ('na', dict(arm_to={'R': (40, -215)}, hold={'R': 'bottle'}, prop_ang={'R': 180}, eyes='wide', rest='D')),
}


def s_title(n):
    def f(t, lt, dur):
        cv = BG['gym'].copy()
        key, st = TITLE_POSE[n]
        st = copy.deepcopy(st)
        bag = st['hold'].pop('L', None) if 'hold' in st else None
        st['hold'] = dict(st.get('hold', {}))
        y = 600 if st.get('sit') else 830
        x = 220 if st.get('sit') else 1150
        hm = hum(cv, key, x, y, 0.55, t, **st)
        if bag:
            bx, by = hm.hands['L']
            dq = ImageDraw.Draw(cv)
            pline(dq, [(bx - 50, by + 30), (bx - 10, by), (bx + 26, by + 30)], '#14110F', 5)     # quai túi
            blob(cv, [[(bx - 70, by + 28), (bx + 40, by + 28), (bx + 46, by + 98), (bx - 76, by + 98)]], '#C8382E')
            pline(ImageDraw.Draw(cv), [(bx - 60, by + 58), (bx + 30, by + 58)], '#F4EFE4', 3)
            M.ell(cv, (bx, by), 13 * 0.55, 13 * 0.55, fill=hx('#F6D2B4'), ow=3.2 * 0.55)
        cx = x
        im = cam(cv, 1.9 + 0.08 * ease(lt / dur), cx, (y - 200) if not st.get('sit') else y - 30)
        title_card(im, (lt - 0.1) / 0.3, *TITLES[[1, 4, 7, 10, 13, 16][n - 1]])
        return im
    return f


def s_price(t, lt, dur):
    k = min(2, int(lt / (dur / 3)))
    cv = Image.new('RGBA', (W * SS, H * SS), hx(['#F2C14E', '#7FC1D9', '#F29A8A'][k]) + (255,))
    d = ImageDraw.Draw(cv)
    for i in range(14):
        pline(d, [(-100 + i * 140, 0), (100 + i * 140, H)], ['#E5B23E', '#6EB0C8', '#E58A7A'][k], 30)
    if k == 0:
        prop(cv, 'racket', (700, 760), 4.2, 25)
        lab = '3.000.000đ'
    elif k == 1:
        blob(cv, [ellipse_pts(800, 560, 330, 150, n=60), [(520, 560), (700, 330), (980, 330), (1100, 560)]], '#F7F7F2')
        blob(cv, [[(480, 620), (1130, 620), (1130, 700), (480, 700)]], '#C8382E')
        M.line(cv, [(620, 520), (800, 470), (1000, 520)], 14, hx('#2F6FB5'))
        for k_ in range(4):                              # dây giày
            M.line(cv, [(700 + k_ * 30, 380 + k_ * 10), (760 + k_ * 30, 420 + k_ * 10)], 6, INK)
        M.line(cv, [(480, 660), (1130, 660)], 5, hx('#F4EFE4'))
        lab = '2.000.000đ'
    else:
        blob(cv, [[(330, 330), (1270, 330), (1300, 780), (300, 780)]], '#2F6FB5')
        for y in (430, 540, 650):
            M.line(cv, [(360, y), (1240, y)], 5, hx('#F4EFE4'))
        M.line(cv, [(560, 330), (800, 160), (1040, 330)], 22, INK)
        for zx in (420, 1180):
            M.line(cv, [(zx, 360), (zx + 10, 760)], 6, hx('#F2C14E'))
        lab = 'ĐỰNG ĐƯỢC TỦ LẠNH'
    im = cam(cv, 1.0 + 0.06 * ((lt % (dur / 3)) / (dur / 3)), 800, 450)
    tag(im, ((lt % (dur / 3)) - 0.1) / 0.2, lab, 980 if k < 2 else 640, 140, rot=-5, col='#B3261E', fg='#F4EFE4', size=64)
    return im


def s_miss(t, lt, dur):
    cv = BG['gym'].copy()
    hit = 0.85
    if lt < 0.5:
        arm = (80, 170)
        ang = 30
    elif lt < 0.75:
        p = (lt - 0.5) / 0.25
        arm = (80 + 80 * p, 170 - 20 * p)
        ang = 30 + 110 * p
    else:
        arm = (160, 150)
        ang = 140
    dizzy = lt > hit
    hm = hum(cv, 'khang', 560, 830, 0.55, t, arms=((14, 6), arm), hold={'R': 'racket'}, prop_ang={'R': ang},
             eyes='wide' if dizzy else 'open', rest='o' if dizzy else 'grin', gaze=(0, -1) if not dizzy else (0, 0))
    hx_, hy_ = 560, 830 - 410 * 0.55
    if lt < hit:
        p = lt / hit
        shuttle(cv, 580 - 20 * p, 120 + (hy_ - 140) * p * p, 0, 1.3)
    else:
        bounce = max(0, 1 - (lt - hit) * 3)
        shuttle(cv, 600 + 60 * (lt - hit), hy_ - 40 - 60 * bounce * abs(math.sin((lt - hit) * 8)), 60, 1.3)
        stars(cv, hx_, hy_ - 10, 60, lt)
    net(cv)
    im = cam(cv, 1.8, 640, 610, shake=8 * math.exp(-max(0, lt - hit) * 6) if dizzy else 0, t=t)
    return im


def s_selfie(t, lt, dur):
    cv = BG['gym'].copy()
    pose = int(lt / 0.55) % 3
    lean = (-8, 0, 8)[pose]
    hum(cv, 'na', 980, 810, 0.5, t, arm_to={'R': (30 + 10 * pose, -400)}, hold={'R': 'phone'}, lean=lean,
        eyes=('happy', 'open', 'happy')[pose], rest='D')
    dg = gau(cv, 1200, 830, 0.44, t, arms=((14, 6), (60, 60)), lid=(0.55, 0.55), gaze=(-1, 0), rest='smirk', mouth='smirk')
    prop(cv, 'racket', dog_hand(dg, 1, 60, 60), 0.5, 35)
    im = cam(cv, 2.0, 1080, 620)
    flash(im, 0.35 if (lt % 0.55) < 0.07 else 0)
    return im


def s_eat(t, lt, dur):
    cv = BG['gym'].copy()
    chew = 0.3 + 0.3 * abs(math.sin(t * 9))
    hum(cv, 'na', 250, 530, 0.46, t, sit=True, arm_to={'R': (88, -296)}, hold={'R': 'banhmi'}, mouth='talk', mo=chew,
        eyes='happy')
    im = cam(cv, 2.3, 300, 520)
    # khung "story" điện thoại (khung trong khung, N21)
    k = ease(lt / 0.3)
    if k > 0:
        ph = Image.new('RGBA', (300, 520), (0, 0, 0, 0))
        d = ImageDraw.Draw(ph)
        d.rounded_rectangle([4, 4, 296, 516], 36, fill=hx('#22252C') + (255,), outline=INK + (255,), width=6)
        d.rounded_rectangle([20, 40, 280, 480], 18, fill=hx('#F29AB0') + (255,))
        d.text((150, 120), 'Chăm tập', font=ImageFont.truetype(FONT_B, 40), fill=hx('#FFFFFF'), anchor='mm', stroke_width=3, stroke_fill=hx('#B3261E'))
        d.text((150, 175), 'thể thao!!', font=ImageFont.truetype(FONT_B, 40), fill=hx('#FFFFFF'), anchor='mm', stroke_width=3, stroke_fill=hx('#B3261E'))
        d.ellipse([105, 230, 195, 320], fill=hx('#F6D2B4'), outline=INK, width=4)
        d.ellipse([110, 342, 132, 364], fill=hx('#B3261E'))
        d.ellipse([128, 342, 150, 364], fill=hx('#B3261E'))
        d.polygon([(111, 357), (149, 357), (130, 382)], fill=hx('#B3261E'))
        d.text((175, 362), '3', font=ImageFont.truetype(FONT_B, 34), fill=hx('#B3261E'), anchor='mm')
        ph = ph.rotate(6, expand=True, resample=Image.BICUBIC)
        im.paste(ph, (int(OW - 400 + 360 * (1 - k)), 90), ph)
    tag(im, (lt - 0.15) / 0.25, 'ĐÁNH: 0 PHÚT', 330, 560, rot=-4)
    tag(im, (lt - dur * 0.5) / 0.25, 'CHỤP: 45 PHÚT', 360, 650, rot=3, col='#B3261E', fg='#F4EFE4')
    return im


def s_referee(t, lt, dur):
    cv = BG['gym'].copy()
    jump = -abs(math.sin(t * 7)) * 18
    hum(cv, 'tung', 720, 830 + jump, 0.55, t, arm_to={'R': (135, -150), 'L': (-128, -235)}, hold={'L': 'magnifier'},
        prop_ang={'L': -40}, eyes='wide', gaze=(1, 1), brow=-12, rest='D')
    im = cam(cv, 2.0, 760, 600, shake=7 if 0.6 <= lt < 0.85 else 0, t=t)
    tag(im, (lt - 0.6) / 0.2, 'RA RỒI!!', 960, 170, rot=6, col='#B3261E', fg='#F4EFE4', size=58)
    return im


def s_floor(t, lt, dur):
    cv = BG['gym'].copy()
    shuttle(cv, 1150, 722, 75, 1.0)
    d = ImageDraw.Draw(cv)
    for k in range(18):                                  # vòng tròn nét đứt
        a0, a1 = k * 2 * math.pi / 18, (k + 0.55) * 2 * math.pi / 18
        pts = [(1150 + 52 * math.cos(a), 718 + 30 * math.sin(a)) for a in np.linspace(a0, a1, 5)]
        pline(d, pts, '#B3261E', 4)
    im = cam(cv, 2.6, 1150, 760)
    tag(im, (lt - 0.2) / 0.2, 'GIỮA SÂN', 640, 120, rot=-3)
    return im


def s_deadpan(t, lt, dur):
    cv = BG['gym'].copy()
    dg = gau(cv, 640, 860, 0.5, t, lid=(0.7, 0.7), gaze=(-0.8, 0), arms=((14, 6), (60, 60)), rest='flat', brow=(-6, -6))
    prop(cv, 'racket', dog_hand(dg, 1, 60, 60), 0.55, 35)
    return cam(cv, 2.8, 640, 700)


def s_sweet(t, lt, dur):
    cv = BG['gym'].copy()
    hm = hum(cv, 'khang', 520, 830, 0.55, t, arms=((14, 6), (40, 140)), hold={'R': 'racket'}, prop_ang={'R': -20},
             eyes='happy', rest='smile')
    sparkles(cv, [(440, 560), (620, 580), (470, 470), (600, 480)], t)
    return cam(cv, 2.3, 540, 610)


def s_smashface(t, lt, dur):
    cv = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 255))
    speed_bg(cv, 800, 420, t)
    Human(cv, 800, 1320, 2.0, CAST['khang'], dict(eyes='angry', mouth='grin', brow=-18, arms=((14, 6), (14, 6)))).draw()
    m = Image.new('L', cv.size, 0)
    ImageDraw.Draw(m).ellipse([(800 - 92) * SS, (1320 - 784 - 104) * SS, (800 + 92) * SS, (1320 - 784 + 104) * SS], fill=110)
    ImageDraw.Draw(m).rectangle([0, (1320 - 784 + 6) * SS, W * SS, H * SS], fill=0)
    cv.paste(Image.new('RGBA', cv.size, (40, 10, 30, 255)), (0, 0), m)
    z = 1.35 - 0.3 * ease(lt / 0.12)
    im = cam(cv, z, 800, 420, shake=10, t=t)
    letterbox(im)
    return im


def s_smash(t, lt, dur):
    cv = BG['gym'].copy()
    hum(cv, 'khang', 560, 760, 0.55, t, arms=((14, 6), (150, 40)), hold={'R': 'racket'}, prop_ang={'R': 120}, eyes='angry', rest='grin')
    net(cv)
    hit = 0.3
    gx, gy = 1150, 730
    if lt < hit:
        p = lt / hit
        x, y = 620 + (gx - 620) * p, 500 + (gy - 260 - 500) * p
        d = ImageDraw.Draw(cv)
        for k in range(6):                               # vệt cầu
            pline(d, [(x - (40 + k * 40), y - (40 + k * 40) * 0.12 + k), (x - 20, y)], '#FFF3B0', 6 - k * 0.8)
        shuttle(cv, x, y, -78, 1.2)
        gau(cv, gx, gy, 0.5, t, mouth='o', eyes=None, big=1.3, gaze=(-1, 0), arms=((14, 6), (14, 6)))
    else:
        p = ease((lt - hit) / 0.35)

        def draw(lay):
            Dog(lay, gx, gy, 0.5, dict(flat=True, mouth='open', big=1.2, arms=((120, 160), (120, 160)))).draw()
            shuttle(lay, gx + 10, gy - 222, -12, 1.2)
        cv.alpha_composite(rot_layer(draw, gx, gy, -35 * p))
        stars(cv, gx + 80 * p, gy - 240, 70, lt)
    im = cam(cv, 1.5, 960, 600, shake=14 * math.exp(-max(0, lt - hit) * 5) if lt > hit else 0, t=t)
    flash(im, 0.8 if hit <= lt < hit + 0.06 else 0)
    letterbox(im, 1 - ease((lt - hit - 0.4) / 0.3))
    # "Vui ghê." khi đã nằm: vẫn giữ cảnh này (câu 12 nằm trong khung này)
    return im


def s_rest(t, lt, dur):
    cv = BG['gym'].copy()
    k = min(2, int(lt / (dur / 3)))
    if k == 0:
        hum(cv, 'tung', 230, 530, 0.5, t, sit=True, arm_to={'R': (125, -270)}, hold={'R': 'bottle'}, prop_ang={'R': 0}, eyes='closed')
    elif k == 1:
        hum(cv, 'tung', 230, 530, 0.5, t, sit=True, arm_to={'R': (128, -262)}, hold={'R': 'banhmi'}, eyes='happy')
    else:
        def draw(lay):
            Human(lay, 230, 530, 0.5, CAST['tung'], dict(eyes='closed', mouth='o', arms=((14, 6), (14, 6)))).draw()
        cv.alpha_composite(rot_layer(draw, 230, 500, 80))
        zzz(cv, 150, 380, t)
    im = cam(cv, 2.2, 260, 525)
    return im


def s_clock(t, lt, dur):
    cv = BG['gym'].copy()
    clock_hands(cv, lt * 40)
    net(cv)

    dg = gau(cv, 1080, 860, 0.5, t, arms=((14, 6), (60, 60)), lid=(0.6, 0.6), gaze=(-1, -0.3), rest='flat')
    prop(cv, 'racket', dog_hand(dg, 1, 60, 60), 0.55, 35)
    im = cam(cv, 1.35, 1100, 600)
    tag(im, (lt - 0.2) / 0.25, 'ĐÁNH: 2 QUẢ', 360, 220, rot=-4)
    tag(im, (lt - dur * 0.55) / 0.25, 'NGHỈ: 4 LẦN', 380, 320, rot=3, col='#B3261E', fg='#F4EFE4')
    return im


def s_mic(t, lt, dur):
    cv = BG['gym'].copy()
    hop = -abs(math.sin(t * 6)) * 12
    hum(cv, 'na', 1300, 820 + hop, 0.55, t, arm_to={'R': (58, -246)}, hold={'R': 'bottle'}, prop_ang={'R': 0},
        arms=((120, 160), (14, 6)), eyes='wide')
    im = cam(cv, 2.1, 1290, 600)
    tag(im, (lt - dur * 0.45) / 0.2, 'CÚ ĐÁNH THẾ KỶ!', 420, 160, rot=-6, col='#FFD34D', size=60)
    return im


def s_fly(t, lt, dur):
    cv = BG['gym'].copy()
    fx = 120 + 260 * (lt / dur)
    fy = 470 + 40 * math.sin(lt * 9) + 20 * math.sin(lt * 23)
    fly(cv, fx, fy, t, k=2.4)
    return cam(cv, 2.4, 250, 540)


def s_chase(t, lt, dur):
    cv = BG['gym'].copy()
    net(cv)
    t_drop = (E[18] - (T[18] - 0.25)) - 0.4          # thả vợt gần cuối câu 18
    sx0, sy0 = 420, 440
    if lt < t_drop:                                  # cầu bay lơ lửng trên cao, Gâu nhìn theo
        p = lt / max(0.1, t_drop)
        cx_, cy_ = sx0 + 380 * p, sy0 - 50 * math.sin(p * math.pi)
        dg = gau(cv, 640, 860, 0.5, t, arms=((14, 6), (60, 60)), gaze=(0.3, -1), big=1.0 + 0.3 * p, rest='o')
        prop(cv, 'racket', dog_hand(dg, 1, 60, 60), 0.55, 35)
        shuttle(cv, cx_, cy_, 100, 1.1)
    else:
        q = lt - t_drop
        prop(cv, 'racket', (700, 880), 0.55, 80)     # vợt rơi dưới sàn
        jt = 1.1                                     # thời gian chạy + nhảy
        p = min(1.0, q / jt)
        x = 640 + 520 * ease(p)
        y = 860 - 170 * math.sin(math.pi * min(1, p * 1.0))
        land = q > jt
        wag = math.sin(q * 25)
        if not land and q > 0.05:
            dd = ImageDraw.Draw(cv)
            for k_ in range(5):
                yy = y - 60 - k_ * 45
                pline(dd, [(x - 90 - 30 * k_, yy), (x - 220 - 40 * k_, yy)], '#F4EFE4', 6)
        if not land:
            cx_, cy_ = sx0 + 380 + 360 * min(1, q / jt), sy0 + (y - 220 - sy0) * min(1, q / jt)
            shuttle(cv, cx_, cy_, 120, 1.1)
        dg = gau(cv, x, y if not land else 860, 0.5, t, arms=((110, 150), (110, 150)) if not land else ((20, 10), (20, 10)),
                 eyes='happy' if land else None, big=1.2, rest='tongue' if land else 'o', mouth='tongue' if land else 'o',
                 lean=6 * wag if land else 0)
        if land or p > 0.5:
            shuttle(cv, x + 34, (y if not land else 860) - 0.5 * 225, 90, 1.0)
    im = cam(cv, 1.6, 860, 660)
    if lt < 1.8:
        title_card(im, (lt - 0.1) / 0.3, *TITLES[18])
    return im


def s_thay(t, lt, dur):
    cv = BG['gym'].copy()
    whistle = lt < 0.55
    st = dict(eyes='angry', gaze=(-1, 0))
    if whistle:
        st.update(arm_to={'R': (8, -330)}, hold={'R': 'whistle'}, mouth='o')
    else:
        st.update(arm_to={'R': (-110, -260)})
    hum(cv, 'thay', 1300, 830, 0.55, t, **st)
    gau(cv, 1080, 860, 0.44, t, mouth='o', big=1.25, arms=((14, 6), (14, 6)), gaze=(1, -0.5))
    shuttle(cv, 1110, 860 - 0.44 * 225, 90, 0.9)
    return cam(cv, 1.9, 1180, 640, shake=3 if whistle else 0, t=t)


def s_gauclose(t, lt, dur):
    cv = BG['gym'].copy()
    dg = gau(cv, 900, 860, 0.5, t, arms=((14, 6), (130, 165)), big=1.15, gaze=(1, -0.3), brow=(12, 0), rest='open')
    shuttle(cv, *dog_hand(dg, 1, 130, 165), 180, 1.0)
    return cam(cv, 2.7, 900, 720)


def s_lineup(t, lt, dur):
    cv = BG['gym'].copy()
    hum(cv, 'khang', 520, 820, 0.5, t, arms=((14, 6), (30, 60)), hold={'R': 'racket'}, prop_ang={'R': 30}, rest='grin', gaze=(0.6, 0))
    hum(cv, 'na', 690, 835, 0.47, t, arm_to={'R': (86, -336)}, hold={'R': 'phone'}, eyes='happy', rest='smile', gaze=(0.6, 0))
    hum(cv, 'tung', 1060, 840, 0.5, t, arm_to={'L': (-30, -200)}, hold={'L': 'banhmi'}, rest='smile', gaze=(-0.6, 0))
    hum(cv, 'thay', 1230, 825, 0.5, t, arms=((14, 6), (14, 6)), rest='flat', eyes='open', gaze=(-0.6, 0), lid=0.35)
    end = E[21]
    st = dict(arms=((14, 6), (120, 150 + 20 * math.sin(lt * 12))), gaze=(0, 0), rest='smile')
    if t > end - 0.3:
        st.update(mouth='tongue', eyes='happy', arms=((14, 6), (14, 6)))
    gau(cv, 870, 870, 0.52, t, **st)
    im = cam(cv, 1.7 + 0.08 * ease(lt / dur), 870, 700)
    if t > end + 0.2:
        title_card(im, (t - end - 0.2) / 0.3, 'BẠN LÀ', 'KIỂU NÀO?')
    return im


def s_cold(t, lt, dur):
    """Cold open: cận mặt Khang hóa ác (0.5s) → Gâu choáng cầu cắm trán."""
    if lt < 0.5:
        return s_smashface(t, lt, 0.5)
    im = s_ko(t, lt, dur)
    flash(im, 0.6 if lt < 0.57 else 0)
    return im


def s_intro(t, lt, dur):
    cv = BG['gym'].copy()
    hum(cv, 'khang', 1150, 800, 0.45, t, arms=((14, 6), (60, 150)), hold={'R': 'racket'}, prop_ang={'R': 20}, rest='grin')
    dg = gau(cv, 780, 860, 0.52, t, arms=((14, 6), (60, 60)), gaze=(0, 0.3), rest='smirk')
    prop(cv, 'racket', dog_hand(dg, 1, 60, 60), 0.57, 35)
    return cam(cv, 2.0 + 0.1 * ease(lt / dur), 840, 650)


def s_ko(t, lt, dur):
    """Gâu ngồi bệt choáng: mắt lim dim, cầu cắm trán, sao quay – giữ suốt 'Vui ghê'."""
    cv = BG['gym'].copy()
    gx, gy = 820, 860
    sway = 4 * math.sin(lt * 5)

    def draw(lay):
        Dog(lay, gx, gy, 0.52, dict(flat=True, mouth='talk', mo=mo_of('gau', t), rest='flat', lid=(0.8, 0.55),
                                    gaze=(0.3, -0.6), brow=(-10, 8), arms=((40, 30), (40, 30)))).draw()
        shuttle(lay, gx + 14, gy - 222, -12, 1.25)
    cv.alpha_composite(rot_layer(draw, gx, gy, sway))
    stars(cv, gx + 10, gy - 250, 95, lt, n=4)
    return cam(cv, 2.3, gx, gy - 170)


def s_flop(t, lt, dur):
    """Cú 'thế kỷ' thực tế: cầu bay lờ đờ, chạm lưới, rơi bịch."""
    cv = BG['gym'].copy()
    hum(cv, 'tung', 560, 840, 0.5, t, arms=((14, 6), (150, 60)), hold={'R': 'racket'}, prop_ang={'R': 140}, eyes='wide', rest='o')
    net(cv)
    p = min(1.0, lt / 0.8)
    if p < 1:
        x, y = 600 + 250 * p, 560 - 60 * math.sin(p * math.pi)
        ang = 120
    else:
        q = min(1.0, (lt - 0.8) / 0.3)
        x, y = 850, 560 + 300 * q * q
        ang = 0
    shuttle(cv, x, y, ang, 1.1)
    return cam(cv, 1.7, 720, 640)


SHOT_FN = dict(cold=s_cold, intro=s_intro, ko=s_ko, flop=s_flop, open=s_open, price=s_price, miss=s_miss, selfie=s_selfie, eat=s_eat, referee=s_referee, floor=s_floor,
               deadpan=s_deadpan, sweet=s_sweet, smashface=s_smashface, smash=s_smash, rest=s_rest, clock=s_clock,
               mic=s_mic, fly=s_fly, chase=s_chase, thay=s_thay, gauclose=s_gauclose, lineup=s_lineup,
               **{'title%d' % n: s_title(n) for n in range(1, 7)})


def render(t):
    build()
    name, lt, dur = shot_at(t)
    return SHOT_FN[name](t, lt, dur)


# ------------------------------------------------------------------ âm thanh
def tone(fq, dur, sr, kind='sin', decay=4.0):
    tt = np.arange(int(dur * sr)) / sr
    ph = 2 * np.pi * fq * tt
    w = np.sin(ph) if kind == 'sin' else np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    return (w * np.exp(-tt * decay)).astype(np.float32)


def noise(dur, sr, rng, decay=20.0, smooth=1):
    tt = np.arange(int(dur * sr)) / sr
    nz = rng.normal(0, 1, tt.size)
    if smooth > 1:
        nz = np.convolve(nz, np.ones(smooth) / smooth, 'same')
    return (nz * np.exp(-tt * decay)).astype(np.float32)


def mix(a, b):
    o = np.zeros(max(a.size, b.size), np.float32)
    o[:a.size] += a
    o[:b.size] += b
    return o


def make_audio():
    sr = SR
    n = int(DUR * sr)
    out = np.zeros(n, np.float32)
    out[:min(n, VOICE.size)] += VOICE[:n]
    rng = np.random.default_rng(5)

    def add(buf, at, sig, g=1.0):
        s0 = int(at * sr)
        m = min(n - s0, sig.size)
        if m > 0 and s0 >= 0:
            buf[s0:s0 + m] += sig[:m] * g

    # nhạc nền vui 128 bpm (ngũ cung), dừng "rẹt" ở cú đập (kiểu 4) và lúc Gâu lao theo cầu
    music = np.zeros(n, np.float32)
    beat = 60 / 128
    scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33]
    mel = [0, 2, 4, 2, 5, 4, 2, 4, 3, 1, 0, 1, 2, 4, 5, 6]
    bass = [130.81, 110.0, 98.0, 87.31]
    t_ch0 = T[18] - 0.25 + (E[18] - (T[18] - 0.25)) - 0.4
    quiet = [(0.0, 1.4), (E[11] + 0.15, T[12] - 0.2), (t_ch0 - 0.1, t_ch0 + 1.2)]
    for k in range(int(DUR / beat) + 1):
        at = k * beat
        if any(a <= at < b for a, b in quiet):
            continue
        if k % 2 == 0:
            add(music, at, tone(bass[(k // 8) % 4], 0.45, sr, 'sin', 5), 0.22)
        add(music, at, tone(scale[mel[k % 16]] * 2, 0.3, sr, 'pluck', 10), 0.07)
        add(music, at + beat / 2, noise(0.04, sr, rng, 90), 0.035)
    hop = sr // 30
    envv = np.repeat(np.array(ENV + [0] * (int(DUR * 30) + 2 - len(ENV)), np.float32), hop)[:n]
    duck = 1 - 0.6 * np.clip(np.convolve(envv, np.ones(hop * 6) / (hop * 6), 'same') * 3, 0, 1)
    out += music * duck
    # tiếng động
    tw = np.arange(int(0.25 * sr)) / sr
    whoosh = np.convolve(rng.normal(0, 1, tw.size), np.ones(30) / 30, 'same').astype(np.float32) * np.sin(np.pi * tw / 0.25) ** 2
    blip_t = np.arange(int(0.12 * sr)) / sr
    blip = (np.sin(2 * np.pi * (700 + 900 * blip_t / 0.12) * blip_t) * np.exp(-blip_t * 30)).astype(np.float32)
    for t0, name in SHOTS[1:]:
        if name.startswith('title') or name in ('chase', 'lineup'):
            add(out, t0 - 0.08, whoosh, 0.25)
            add(out, t0 + 0.1, blip, 0.2)
    bonk = mix(tone(220, 0.25, sr, 'sin', 14), noise(0.08, sr, rng, 40) * 0.5)
    t_miss = E[2] + 0.2
    add(out, t_miss + 0.6, whoosh, 0.2)                                   # vung hụt
    add(out, t_miss + 0.85, bonk, 0.5)                                    # cầu rơi trúng đầu
    for k in range(int((T[6] - T[5]) / 0.55) + 1):                       # tách tách chụp ảnh
        add(out, T[5] - 0.2 + k * 0.55, noise(0.05, sr, rng, 120), 0.25)
    for t0, name in SHOTS:
        if name in ('eat', 'clock'):
            add(out, t0 + 0.12, blip, 0.18)
            add(out, t0 + (SHOTS[SHOTS.index((t0, name)) + 1][0] - t0) * 0.5 + 0.1 if name == 'eat' else t0 + 0.2, blip, 0.18)
    t_sm = E[11] + 0.75
    add(out, E[11] + 0.15, tone(80, 0.6, sr, 'sin', 3), 0.4)            # "đùng" mặt Khang
    add(out, t_sm, noise(0.3, sr, rng, 10, 6), 0.4)                       # VÙUU
    add(out, t_sm + 0.3, mix(tone(110, 0.3, sr, 'sin', 12), noise(0.1, sr, rng, 30)), 0.42)   # bộp
    tt = np.arange(int(0.45 * sr)) / sr                                   # còi thầy
    whistle = (np.sin(2 * np.pi * 2900 * tt + 8 * np.sin(2 * np.pi * 38 * tt)) * np.minimum(1, tt * 40) * np.exp(-tt * 2)).astype(np.float32)
    add(out, T[19] - 0.6, whistle, 0.25)
    add(out, T[19] - 0.1, whistle[:int(0.25 * sr)], 0.2)
    fz = np.arange(int((T[18] - 0.25 - (E[17] + 1.5)) * sr)) / sr       # ruồi vo ve
    buzz = (np.sign(np.sin(2 * np.pi * 180 * fz + 3 * np.sin(2 * np.pi * 7 * fz))) * 0.5).astype(np.float32)
    add(out, E[17] + 1.5, np.convolve(buzz, np.ones(8) / 8, 'same').astype(np.float32), 0.15)
    add(out, 0.2, noise(0.3, sr, rng, 10, 6), 0.3)
    add(out, 0.5, mix(tone(110, 0.3, sr, 'sin', 12), noise(0.1, sr, rng, 30)), 0.42)
    add(out, E[17] + 1.0, tone(300, 0.12, sr, 'sin', 25), 0.25)          # cầu chạm lưới 'pụp'
    sq_t = np.arange(int(0.18 * sr)) / sr                                  # giày rít sàn
    squeak = (np.sin(2 * np.pi * (1800 + 600 * np.sin(sq_t * 40)) * sq_t) * np.sin(np.pi * sq_t / 0.18)).astype(np.float32)
    for at in (T[2] - 0.6, E[2] + 0.5, E[11] + 0.85, T[18] + 0.3):
        add(out, at, squeak, 0.08)
    t_ch = T[18] - 0.25 + (E[18] - (T[18] - 0.25)) - 0.4
    add(out, t_ch, tone(400, 0.15, sr, 'sin', 20), 0.2)                  # vợt rơi "cạch"
    for k in range(5):                                                    # chân chạy lạch bạch
        add(out, t_ch + 0.15 + k * 0.16, noise(0.04, sr, rng, 80, 3), 0.2)
    add(out, t_ch + 1.15, tone(1200, 0.3, sr, 'pluck', 8), 0.15)          # "phập" ngậm cầu
    for k, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        add(out, E[21] + 0.25 + k * 0.12, tone(f, 0.6, sr, 'pluck', 5), 0.12)
    out = np.tanh(out / max(1e-6, np.percentile(np.abs(out), 99.7)) * 0.9) * 0.88   # nâng độ to + chặn đỉnh mềm
    p = os.path.join(DIR, 'tieng-tron.wav')
    sf.write(p, out, sr)
    return p


# ------------------------------------------------------------------ chạy
G = {}


def init_pool(d):
    build()
    G['dir'] = d


def job(i):
    render(i / FPS).convert('RGB').save(os.path.join(G['dir'], 'f%05d.jpg' % i), quality=92)
    return i


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return 'ffmpeg'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--khung', type=float, nargs='*')
    ap.add_argument('--canh', action='store_true', help='1 khung giữa mỗi cảnh → bảng soát')
    a = ap.parse_args()
    if a.khung is not None or a.canh:
        ts = a.khung or []
        if a.canh:
            for i, (t0, _) in enumerate(SHOTS):
                t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
                ts.append(t0 + (t1 - t0) * 0.6)
        ims = [render(t).convert('RGB') for t in ts]
        cols = 4
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 480, rows * 270), (0, 0, 0))
        dr = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            x, y = (k % cols) * 480, (k // cols) * 270
            sheet.paste(im.resize((480, 270)), (x, y))
            dr.text((x + 6, y + 4), '%.1fs %s' % (ts[k], shot_at(ts[k])[0]), fill=(255, 255, 0))
        p = os.path.join(DIR, 'bang-khung.jpg')
        sheet.save(p, quality=88)
        print(p)
        return
    fdir = tempfile.mkdtemp(prefix='caulong-')
    n = int(DUR * FPS)
    print('Thời lượng %.2fs, %d khung' % (DUR, n), flush=True)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init_pool, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n), chunksize=4)):
            if k % 150 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    wav = make_audio()
    out = os.path.join(DIR, 'cau-long.mp4')
    subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, 'f%05d.jpg'),
                    '-i', wav, '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', out], check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
