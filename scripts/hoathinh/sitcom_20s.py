"""Demo ~20s phong cách SITCOM TƯƠI SÁNG (chuẩn tham khảo: nhịp hài của kênh hoạt hình sitcom VN).
Chỉ học NGÔN NGỮ HÌNH (chibi tối giản, màu phẳng tươi, biểu cảm phóng đại, cắt cảnh sitcom, câu chốt hài).
Nhân vật là của kênh: Anh Văn (áo vàng, sách) – Em Võ (áo đỏ, mũ trụ). KHÔNG vẽ nhân vật kênh khác.

Lời: build/thu-hoathinh/sitcom-20s/loi.json → thoai_song_tu.py → thoai.wav + thoai.json
Dữ kiện sử (lời Anh Văn): kb/E2 F17 (cọc lớn, vót nhọn, bịt sắt ở cửa biển), F19 (triều rút, cọc lộ).
Phần Em Võ tự cắm cọc là tình huống hài của người dẫn, không phải sử.

Chạy:  python scripts/hoathinh/sitcom_20s.py --khung 1 5 9 14 18     (ảnh thử)
       python scripts/hoathinh/sitcom_20s.py                          (dựng video)
"""
import argparse
import glob
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ngo_quyen_can_canh as cc  # noqa: E402
import song_tu_doi_thoai as sd  # noqa: E402
import ben_song as bs  # noqa: E402
import anhsang  # noqa: E402  (scripts/video, ben_song đã thêm vào sys.path)
from ngo_quyen_can_canh import cr, hx, mix, clamp, ease, stroke  # noqa: E402

ROOT = cc.ROOT
SS = cc.SS
W, H = 1920, 1080
FPS = 30
DIR = os.path.join(ROOT, 'build', 'thu-hoathinh', 'sitcom-20s')
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')
FONTB = os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf')
INK = sd.INKC

# ---------------------------------------------------------------- phong cách: phẳng, tươi
S_ = sd.S_
sd.SKIN = S_('#FFE1C6', '#F3C7A2')
sd.VAN = dict(tunic=S_('#F6C445', '#E3A92E'), trim=S_('#FFF6E0'), belt=S_('#6A4426'))
sd.VO = dict(tunic=S_('#EE4B3B', '#D23426'), trim=S_('#FFD866'), belt=S_('#4A2A1A'))
sd.BLUSH = hx('#FF9E9E')
_shape0 = cc.shape


def flat_shape(cv, pts, c, lw=sd.OUTL, shd=7, hld=0, inner=()):
    _shape0(cv, pts, c, lw * 1.25, shd * 0.35, hld, inner, light=False)   # viền dày hơn, bóng rất nhẹ


sd.shape = flat_shape

# ---------------------------------------------------------------- giọng + dời câu cuối (chừa chỗ triều rút)
PAUSE = 2.7         # khoảng nghỉ trước câu cuối (nước rút)
TAIL = 3.6          # đuôi sau câu cuối (cọc trôi qua, nhạc buồn)
A = {}


def load_voice():
    D = json.load(open(os.path.join(DIR, 'thoai.json'), encoding='utf-8'))
    v, sr = sf.read(os.path.join(DIR, 'thoai.wav'), dtype='float32')
    L = D['lines']
    cut = int((L[4]['start'] - 0.1) * sr)
    v2 = np.concatenate([v[:cut], np.zeros(int(PAUSE * sr), np.float32), v[cut:]])
    for ln in L[4:]:
        ln['start'] = round(ln['start'] + PAUSE, 3)
        ln['end'] = round(ln['end'] + PAUSE, 3)
    dur = L[-1]['end'] + TAIL
    v2 = np.concatenate([v2, np.zeros(max(0, int(dur * sr) - v2.size), np.float32)])[:int(dur * sr)]
    hop = sr // FPS
    env = [float(np.sqrt(np.mean(v2[k:k + hop] ** 2))) for k in range(0, v2.size, hop)]
    mx = max(env) or 1
    D2 = dict(sr=sr, dur=dur, lines=L, env=[e / mx for e in env])
    sd.D, sd.ENV = D2, D2['env']
    A.update(D=D2, voice=v2, sr=sr)
    return D2


D = load_voice()
L = D['lines']
DUR = round(D['dur'], 2)
C1 = L[1]['start'] - 0.2          # cận Văn
C2 = L[2]['start'] - 0.15         # cận Võ
C3 = L[3]['start'] - 0.15         # cận Văn
C4 = L[3]['end'] + 0.3            # toàn cảnh: triều rút (cắt "bốp")
TIDE0, TIDE1 = C4 + 0.5, C4 + 2.4
DRIFT0 = L[4]['end'] + 0.2        # cọc của Võ trôi ngang
HIGH, LOW = 830, 610              # mép nước phía gần (y) lúc triều lên / rút

# ---------------------------------------------------------------- nền (bến sông chi tiết – ben_song.py)
BG = {}
VO_X, VAN_X, FOOT, SC = 830, 1090, 870, 0.85     # nhân vật NHỎ trong toàn cảnh, nền là chính


def build_layers():
    BG.update(bs.build())


def water(cv, edge, t):
    bs.water(cv, 452, t, edge)


def stake(cv, x, y, h_, ang=0.0, iron=False, s=1.0):
    """Cọc gỗ đơn giản: thân + mũi nhọn (+ bịt sắt)."""
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    px, py = math.cos(a), math.sin(a)
    w = 13 * s
    tip = (x + ux * h_, y + uy * h_)
    sh = (x + ux * (h_ - 34 * s), y + uy * (h_ - 34 * s))
    body = [(x - px * w, y - py * w), (sh[0] - px * w, sh[1] - py * w), tip, (sh[0] + px * w, sh[1] + py * w),
            (x + px * w, y + py * w)]
    inner = [('line', [(x + px * 4 * s + ux * k, y + py * 4 * s + uy * k) for k in (10 * s, h_ - 50 * s)],
              hx('#B07A4A') + (255,), 3 * s)]
    if iron:
        inner.append(('poly', [(sh[0] - px * w, sh[1] - py * w), tip, (sh[0] + px * w, sh[1] + py * w)],
                      hx('#7D8A96') + (255,)))
    cc.shape(cv, body, S_('#C8925A', '#A8744A'), sd.OUTL * 1.2, 4, 0, inner, light=False)


def floating_stake(cv, x, y, t, s=1.0):
    """Cọc của Võ nằm ngang trôi trên mặt nước, nhấp nhô."""
    bob = 4 * math.sin(t * 5)
    ang = 92 + 4 * math.sin(t * 3)
    stake(cv, x - 70 * s, y + bob, 140 * s, ang, s=s)
    for k in (-1, 1):
        ImageDraw.Draw(cv).arc([(x + k * 60 * s - 26 * s) * SS, (y + bob + 8 * s) * SS, (x + k * 60 * s + 26 * s) * SS,
                                (y + bob + 20 * s) * SS], 0, 180, fill=hx('#E6FAFF') + (255,), width=int(3 * SS))


def level_at(t):
    return HIGH + (LOW - HIGH) * ease((t - TIDE0) / (TIDE1 - TIDE0))


def contact_shadow(cv, x, y, s):
    lay = Image.new('L', cv.size, 0)
    ImageDraw.Draw(lay).ellipse([(x - 95 * s) * SS, (y - 14 * s) * SS, (x + 95 * s) * SS, (y + 14 * s) * SS], fill=120)
    lay = lay.filter(ImageFilter.GaussianBlur(6 * SS))
    cv.alpha_composite(Image.merge('RGBA', [Image.new('L', cv.size, 50), Image.new('L', cv.size, 40),
                                             Image.new('L', cv.size, 70), lay]))


def wide_bg(t, shadows=True):
    cv = BG['sky'].copy()
    cv.alpha_composite(BG['mud'])
    lv = level_at(t)
    if lv < HIGH - 5:   # chỗ Võ "cắm cọc": chỉ còn cái lỗ
        ImageDraw.Draw(cv).ellipse([640 * SS, 700 * SS, 700 * SS, 714 * SS], fill=hx('#8A6A44') + (255,))
    water(cv, lv, t)
    if t < TIDE0:       # gợn tròn ở chỗ Võ chỉ
        for r in (20, 38):
            rr = r + 8 * ((t * 1.5) % 1)
            ImageDraw.Draw(cv).ellipse([(670 - rr) * SS, (640 - rr * 0.25) * SS, (670 + rr) * SS, (640 + rr * 0.25) * SS],
                                       outline=hx('#E6FAFF') + (255,), width=int(3 * SS))
    bs.boat(cv, 1450, 492 + 2 * math.sin(t * 2), 0.9)
    cv.alpha_composite(BG['mid'])
    if t >= DRIFT0:     # cọc trôi ngang trên dòng nước còn lại
        x = -120 + (t - DRIFT0) * 230
        floating_stake(cv, x, lv - 40, t, 0.9)
    cv.alpha_composite(BG['fg'])
    if shadows:
        contact_shadow(cv, VO_X, FOOT, SC)
        contact_shadow(cv, VAN_X, FOOT, SC)
    return cv


def close_bg(cx_, cy_, z, t, drift=None):
    key = ('close', cx_, cy_, z)
    if key not in BG:
        im = wide_bg(0.0, shadows=False)
        w, h = W / z, H / z
        crop = im.resize((W, H), Image.LANCZOS, box=((cx_ - w / 2) * SS, (cy_ - h / 2) * SS, (cx_ + w / 2) * SS,
                                                     (cy_ + h / 2) * SS))
        BG[key] = crop.filter(ImageFilter.GaussianBlur(2.5)).resize((W * SS, H * SS), Image.BICUBIC)
    cv = BG[key].copy()
    if drift is not None:   # cọc trôi ngang hậu cảnh (mờ nhẹ) – gài trước câu chốt
        lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
        floating_stake(lay, drift, 300, t, 1.6)
        cv.alpha_composite(lay.filter(ImageFilter.GaussianBlur(3)))
    return cv


# ---------------------------------------------------------------- hiệu ứng biểu cảm sitcom
def head_xy(x, y, s, f):
    return x + f * 14 * s, y - 262 * s


def sweat(cv, x, y, s, f, t, t0):
    k = clamp((t - t0) / 0.25)
    if k <= 0:
        return
    hx_, hy_ = head_xy(x, y, s, f)
    dx, dy = hx_ + f * 92 * s, hy_ - 60 * s + 30 * s * ease(clamp((t - t0) / 1.2))
    r = 13 * s * ease(k)
    pts = [(dx, dy - r * 2.2), (dx + r, dy), (dx + r * 0.7, dy + r * 0.8), (dx, dy + r), (dx - r * 0.7, dy + r * 0.8),
           (dx - r, dy)]
    cc.shape(cv, cr(pts, n=5), S_('#9EDCFF', '#7CC8F2'), sd.OUTL, 3, 0, [('dot', (dx - r * 0.3, dy - r * 0.1), r * 0.25,
                                                                           (255, 255, 255, 255))], light=False)


def shock_lines(cv, x, y, s, f, t, t0, dur=0.9):
    if not (t0 <= t < t0 + dur):
        return
    hx_, hy_ = head_xy(x, y, s, f)
    k = ease(clamp((t - t0) / 0.15))
    for a in (-60, -90, -120, -30, -150):
        r0, r1 = 135 * s, (135 + 40 * k) * s
        ra = math.radians(a)
        stroke(cv, [(hx_ + r0 * math.cos(ra), hy_ - 20 * s + r0 * math.sin(ra)),
                    (hx_ + r1 * math.cos(ra), hy_ - 20 * s + r1 * math.sin(ra))], 7 * s, 3 * s, INK)


def qmarks(cv, x, y, s, f, t, t0):
    if t < t0:
        return
    hx_, hy_ = head_xy(x, y, s, f)
    fnt = ImageFont.truetype(FONTB, int(70 * s * SS))
    d = ImageDraw.Draw(cv)
    for i, (dx, dy) in enumerate(((-120, -150), (110, -175))):
        k = ease(clamp((t - t0 - i * 0.2) / 0.25))
        if k <= 0:
            continue
        bob = 6 * math.sin(t * 6 + i)
        d.text(((hx_ + dx * s) * SS, (hy_ + (dy + bob) * s) * SS), '?', font=fnt, fill=INK + (255,), anchor='mm',
               stroke_width=int(3 * SS), stroke_fill=(255, 255, 255, 255))


def sparkles(cv, x, y, s, f, t):
    hx_, hy_ = head_xy(x, y, s, f)
    for i, (dx, dy) in enumerate(((-150, -120), (150, -80), (120, -190))):
        ph = (t * 2 + i * 0.33) % 1
        r = 16 * s * math.sin(ph * math.pi)
        cx_, cy_ = hx_ + dx * s, hy_ + dy * s
        pts = [(cx_, cy_ - r), (cx_ + r * 0.25, cy_ - r * 0.25), (cx_ + r, cy_), (cx_ + r * 0.25, cy_ + r * 0.25),
               (cx_, cy_ + r), (cx_ - r * 0.25, cy_ + r * 0.25), (cx_ - r, cy_), (cx_ - r * 0.25, cy_ - r * 0.25)]
        if r > 2:
            ImageDraw.Draw(cv).polygon([(a * SS, b * SS) for a, b in pts], fill=hx('#FFE14A') + (255,))


# ---------------------------------------------------------------- thẻ chữ
CARDS = {}


def card_stake():
    if 'stake' in CARDS:
        return CARDS['stake']
    w, h = 470, 300
    im = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6 * SS, 6 * SS, (w - 6) * SS, (h - 6) * SS], radius=26 * SS, fill=hx('#FFF8E6') + (255,),
                        outline=INK + (255,), width=int(5 * SS))
    for i, x in enumerate((90, 150, 210)):
        stake(im, x, 250, 190 - i * 12, -6 + i * 6, iron=True, s=1.15)
    f1 = ImageFont.truetype(FONTB, 34 * SS)
    f2 = ImageFont.truetype(FONT, 28 * SS)
    d.text((262 * SS, 60 * SS), 'Sử chép', font=f1, fill=hx('#B3261E') + (255,), anchor='lm')
    for i, tx in enumerate(('Cọc lớn', 'Vót nhọn', 'Bịt sắt', 'Ở cửa biển')):
        d.text((262 * SS, (112 + i * 42) * SS), '• ' + tx, font=f2, fill=INK + (255,), anchor='lm')
    CARDS['stake'] = im
    return im


def card_text(text):
    if text in CARDS:
        return CARDS[text]
    f = ImageFont.truetype(FONTB, 52 * SS)
    tw = int(f.getlength(text) / SS) + 80
    im = Image.new('RGBA', (tw * SS, 100 * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4 * SS, 4 * SS, (tw - 4) * SS, 96 * SS], radius=20 * SS, fill=hx('#FFE14A') + (255,),
                        outline=INK + (255,), width=int(5 * SS))
    d.text((tw / 2 * SS, 52 * SS), text, font=f, fill=INK + (255,), anchor='mm')
    CARDS[text] = im
    return im


def pop(cv, im, cx_, cy_, t0, t1, t, rot=-3):
    if not (t0 <= t < t1):
        return
    k = clamp((t - t0) / 0.28)
    sc = (1.15 - 0.15 * ease(clamp((k - 0.6) / 0.4))) * ease(min(1, k / 0.6))
    out = 1 - ease(clamp((t - (t1 - 0.2)) / 0.2))
    sc *= out
    if sc < 0.02:
        return
    w, h = im.size
    r = im.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.BICUBIC).rotate(rot, expand=True, resample=Image.BICUBIC)
    cv.alpha_composite(r, (int(cx_ * SS - r.size[0] / 2), int(cy_ * SS - r.size[1] / 2)))


# ---------------------------------------------------------------- phụ đề
def line_at(t):
    for ln in L:
        if ln['start'] - 0.1 <= t <= ln['end'] + 0.25:
            return ln
    return None


FS = {}


def subtitle(im, t):
    ln = line_at(t)
    if not ln:
        return
    if 'f' not in FS:
        FS['f'] = ImageFont.truetype(FONT, 46)
        FS['n'] = ImageFont.truetype(FONTB, 30)
    f, fn = FS['f'], FS['n']
    words, rows, cur = ln['text'].split(), [], ''
    for w_ in words:
        if f.getlength(cur + ' ' + w_) > 1300 and cur:
            rows.append(cur)
            cur = w_
        else:
            cur = (cur + ' ' + w_).strip()
    rows.append(cur)
    d = ImageDraw.Draw(im)
    y0 = H - 70 - 58 * len(rows)
    name = 'ANH VĂN' if ln['who'] == 'van' else 'EM VÕ'
    col = hx('#E3A92E') if ln['who'] == 'van' else hx('#EE4B3B')
    nw = fn.getlength(name) + 32
    d.rounded_rectangle([W / 2 - nw / 2, y0 - 50, W / 2 + nw / 2, y0 - 8], radius=12, fill=col, outline=INK, width=3)
    d.text((W / 2, y0 - 29), name, font=fn, fill=(255, 255, 255), anchor='mm', stroke_width=2, stroke_fill=INK)
    for i, r in enumerate(rows):
        d.text((W / 2, y0 + 30 + i * 58), r, font=f, fill=(255, 255, 255), anchor='mm', stroke_width=5, stroke_fill=INK)


# ---------------------------------------------------------------- diễn xuất
def blink_at(t, who):
    for tb in ((1.6, 5.4, 9.8, 12.9) if who == 'van' else (2.4, 4.9, 7.7, 11.2)):
        d = t - tb
        if 0 <= d < 0.16:
            return math.sin(d / 0.16 * math.pi)
    return 0.0


def state(who, t):
    st = dict(blink=blink_at(t, who), gaze=(4, 0))
    if who == 'vo':
        st['smile'] = 1.0
        if t < C1:                                  # khoe, nhảy tưng tưng, hai tay giơ cao
            w = math.sin(t * 8)
            st['arms'] = ((155 + 18 * w, 30), (165 - 18 * w, 25))
            st['bounce'] = abs(math.sin(t * 7)) * 0.8
            st['brow'] = 0.8
        elif t < C2:
            st['arms'] = ((25, 10), (30, 20))
        elif t < C3:                                # "Thì em cũng cắm y chang nè!" – ưỡn ngực, chống nạnh
            st['arms'] = ((70, 150), (70, 150))
            st['lean'] = -8
            st['brow'] = 1.0
            st['bounce'] = abs(math.sin(t * 9)) * 0.25
        elif t < TIDE1 + 0.2:
            st['arms'] = ((25, 10), (30, 20))
            st['smile'] = 0.8
        else:                                       # sững sờ
            st['arms'] = ((40, 60), (40, 60))
            st['bigeye'] = 1.0
            st['smile'] = -0.6
            st['brow'] = 0.4
            st['gaze'] = (-10, 4) if t < DRIFT0 + 0.6 else (-14 + 18 * ease((t - DRIFT0 - 0.6) / 1.5), 4)
    else:
        st['smile'] = 0.2
        st['arms'] = ((30, 20), (55, 110))
        if C1 <= t < C2:
            k = ease((t - C1) / 0.3) * (1 - ease((t - L[1]['start'] - 1.3) / 0.3))
            st['arms'] = ((30, 20), (55 + 100 * k, 110 + 60 * k))
            st['book'] = k < 0.5
        if C3 <= t < C4:                            # nhắm mắt, giảng giải
            st['blink'] = 0.9
            st['smile'] = 0.5
        if t >= L[4]['end']:                        # thở dài
            st['blink'] = 0.9
            st['smile'] = -0.3
    return st


# ---------------------------------------------------------------- dựng khung
def blank():
    return Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))


def shoot(bg, ov, t, zoom=1.0, cx_=W / 2, cy_=H / 2, shake=0.0):
    """Máy quay (zoom/rung) cắt cùng khung cho nền + lớp nhân vật, rồi chiếu sáng (bóng đổ, viền nắng, tông chiều)."""
    w, h = W / zoom, H / zoom
    sx = shake * math.sin(t * 90) * 10
    sy = shake * math.cos(t * 77) * 8
    x0 = clamp(cx_ - w / 2 + sx, 0, W - w)
    y0 = clamp(cy_ - h / 2 + sy, 0, H - h)
    box = (x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS)
    b = bg.resize((W, H), Image.LANCZOS, box=box)
    o = ov.resize((W, H), Image.LANCZOS, box=box)
    return anhsang.ap_dung(b, o, bs.TONE, U=1.0)


def render(t):
    ov = blank()
    if t < C1 or t >= C4:                           # toàn cảnh
        bg = wide_bg(t)
        sd.draw_char(ov, 'vo', VO_X, FOOT, SC, 1, t, state('vo', t))
        sd.draw_char(ov, 'van', VAN_X, FOOT, SC, -1, t, state('van', t))
        if t >= C4:
            pop(ov, card_text('Chờ triều rút…'), 960, 200, TIDE0 - 0.2, TIDE1 + 0.3, t, rot=-2)
            shock_lines(ov, VO_X, FOOT, SC, 1, t, TIDE1 + 0.1)
            qmarks(ov, VO_X, FOOT, SC, 1, t, L[4]['start'] + 0.3)
            sweat(ov, VAN_X, FOOT, SC, -1, t, L[4]['end'] + 0.1)
            sweat(ov, VO_X, FOOT, SC, 1, t, DRIFT0 + 1.2)
        if t < C1:                                  # mở: đẩy nhẹ vào
            return shoot(bg, ov, t, 1.0 + 0.05 * ease(t / C1), 960, 600)
        if t < DRIFT0:                              # sững sờ: đẩy mạnh vào mặt Võ + rung
            z = 1.0 + 1.0 * ease((t - TIDE1 - 0.1) / 0.25)
            sh = 1.0 if TIDE1 + 0.1 <= t < TIDE1 + 0.45 else 0.0
            return shoot(bg, ov, t, z, VO_X + 10, FOOT - 200, sh)
        z = 2.0 - 1.0 * ease((t - DRIFT0) / 0.6)    # lùi ra cho thấy cọc trôi
        return shoot(bg, ov, t, z, 900, 640)
    if t < C2 or (C3 <= t < C4):                    # cận Văn
        bg = close_bg(1120, 700, 2.2, t)
        sd.draw_char(ov, 'van', 1080, 1300, 2.2, -1, t, state('van', t))
        sd.draw_char(ov, 'vo', -60, 1440, 2.7, 1, t, state('vo', t))
        if t < C2:
            pop(ov, card_stake(), 440, 330, L[1]['start'] + 1.0, C2 - 0.05, t, rot=-3)
        return shoot(bg, ov, t, 1.0 + 0.05 * ease((t - (C1 if t < C2 else C3)) / 3))
    bg = close_bg(800, 700, 2.2, t, drift=-300 + (t - C2) * 260)   # cận Võ – cọc trôi hậu cảnh
    sd.draw_char(ov, 'vo', 860, 1300, 2.2, 1, t, state('vo', t))
    sd.draw_char(ov, 'van', 1980, 1440, 2.7, -1, t, state('van', t))
    sparkles(ov, 860, 1300, 2.2, 1, t)
    return shoot(bg, ov, t, 1.0 + 0.04 * ease((t - C2) / 1.5))


def frame(t):
    im = render(t)
    subtitle(im, t)
    return im


# ---------------------------------------------------------------- âm thanh
def tone(fq, dur, sr, kind='sin', decay=4.0, vib=0.0):
    tt = np.arange(int(dur * sr)) / sr
    f = fq * (1 + vib * np.sin(2 * np.pi * 5.5 * tt))
    ph = 2 * np.pi * np.cumsum(f) / sr
    if kind == 'saw':
        w = sum(np.sin(k * ph) / k for k in range(1, 7))
    elif kind == 'pluck':
        w = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    else:
        w = np.sin(ph)
    return (w * np.exp(-tt * decay)).astype(np.float32)


def make_audio():
    sr = A['sr']
    n = int(DUR * sr)
    v = A['voice'][:n]
    out = np.zeros(n, np.float32)
    out[:v.size] += v
    rng = np.random.default_rng(9)

    def add(at, sig, g=1.0):
        s0 = int(at * sr)
        m = min(n - s0, sig.size)
        if m > 0 and s0 >= 0:
            out[s0:s0 + m] += sig[:m] * g

    # nhạc nền vui: ngũ cung trưởng C, 120 bpm, pluck + bass, dừng "phựt" khi Võ sững sờ
    stop = TIDE1 + 0.1
    beat = 0.5
    scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25]
    mel = [0, 2, 4, 2, 3, 2, 1, 0, 2, 4, 5, 4, 3, 1, 2, 0]
    bass = [130.81, 130.81, 196.0, 174.61]
    music = np.zeros(n, np.float32)
    for i in range(int(stop / beat)):
        at = i * beat
        if i % 2 == 0:
            s0 = int(at * sr)
            sig = tone(bass[(i // 4) % 4], 0.45, sr, 'sin', 6)
            m = min(n - s0, sig.size)
            music[s0:s0 + m] += sig[:m] * 0.22
        s0 = int(at * sr)
        sig = tone(scale[mel[i % len(mel)]] * 2, 0.35, sr, 'pluck', 9)
        m = min(n - s0, sig.size)
        music[s0:s0 + m] += sig[:m] * 0.09
    hop = sr // FPS
    envv = np.repeat(np.array(D['env'] + [0] * (int(DUR * FPS) + 2 - len(D['env'])), np.float32), hop)[:n]
    duck = 1 - 0.5 * np.clip(np.convolve(envv, np.ones(hop * 6) / (hop * 6), 'same') * 3, 0, 1)
    out += music * duck
    # tiếng động
    tw = np.arange(int(0.35 * sr)) / sr
    whoosh = np.convolve(rng.normal(0, 1, tw.size), np.ones(30) / 30, 'same').astype(np.float32) * \
        np.sin(np.pi * tw / 0.35) ** 2
    for at in (C1, C2, C3, C4):
        add(at - 0.12, whoosh, 0.18)
    for i in range(3):                                         # boing khi Võ nhảy
        tt = np.arange(int(0.3 * sr)) / sr
        add(0.15 + i * 0.45, np.sin(2 * np.pi * np.cumsum(220 + 160 * np.sin(tt * 40) * np.exp(-tt * 6)) / sr)
            .astype(np.float32) * np.exp(-tt * 8), 0.12)
    tt = np.arange(int(0.12 * sr)) / sr
    blip = (np.sin(2 * np.pi * (700 + 900 * tt / 0.12) * tt) * np.exp(-tt * 30)).astype(np.float32)
    add(L[1]['start'] + 1.0, blip, 0.15)                       # thẻ "Sử chép" bật
    add(TIDE0 - 0.2, blip, 0.15)                               # thẻ "Chờ triều rút"
    add(C2 + 0.2, tone(1568, 0.5, sr, 'sin', 6), 0.05)         # lấp lánh
    add(C2 + 0.35, tone(2093, 0.5, sr, 'sin', 6), 0.05)
    ts = np.arange(int(1.9 * sr)) / sr                         # còi trượt xuống: nước rút
    fq = 1100 * np.exp(-ts * 0.75)
    add(TIDE0, (np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.sin(np.pi * ts / 1.9)).astype(np.float32), 0.10)
    tr = np.arange(int(0.25 * sr)) / sr                        # "rẹt" dừng nhạc
    add(stop, (rng.normal(0, 1, tr.size) * np.exp(-tr * 18)).astype(np.float32), 0.25)
    add(stop + 0.02, tone(90, 0.4, sr, 'sin', 8), 0.4)         # "bụp" trầm khi zoom mặt
    add(DRIFT0 + 0.1, tone(180, 0.35, sr, 'sin', 10) * 1.0, 0.25)   # "tõm" cọc trôi
    for k, (fq_, d_) in enumerate(((392, 0.42), (370, 0.42), (349, 0.42), (330, 1.2))):   # kèn buồn wah-wah
        add(DRIFT0 + 0.9 + k * 0.45, tone(fq_ / 2, d_, sr, 'saw', 1.5, vib=0.02 if k == 3 else 0.0), 0.06)
    add(L[4]['end'] + 0.1, tone(2600, 0.25, sr, 'sin', 14), 0.06)   # "tinh" giọt mồ hôi
    out = out / max(1e-6, np.abs(out).max()) * 0.92
    p = os.path.join(DIR, 'tieng-tron.wav')
    sf.write(p, out, sr)
    return p


# ---------------------------------------------------------------- chạy
G = {}


def init():
    if 'sky' not in BG:
        build_layers()


def init_pool(d):
    init()
    G['dir'] = d


def job(i):
    frame(i / FPS).save(os.path.join(G['dir'], 'f%04d.jpg' % i), quality=92)
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
    a = ap.parse_args()
    init()
    if a.khung:
        for t in a.khung:
            p = os.path.join(DIR, 'khung-%05.2f.jpg' % t)
            frame(t).save(p, quality=92)
            print(p)
        return
    fdir = tempfile.mkdtemp(prefix='sitcom20s-')     # khung tạm ngoài Google Drive (khỏi đồng bộ hàng trăm ảnh)
    n = int(DUR * FPS)
    print('Thời lượng %.2fs, %d khung' % (DUR, n), flush=True)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init_pool, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n))):
            if k % 60 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    wav = make_audio()
    out = os.path.join(DIR, 'sitcom-20s-van-vo.mp4')
    subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, 'f%04d.jpg'),
                    '-i', wav, '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', out], check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
