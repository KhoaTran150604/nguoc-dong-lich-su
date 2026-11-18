"""Video thử ~1 phút kết hợp 3 phong cách đã chọn (18/11/2026):
  Đoạn A – S2 "minh họa sách sử" (nền giấy, thẻ chữ bật ra)       : bối cảnh 938
  Đoạn B – S3 "người tối giản trên bản đồ" (đoàn thuyền tiến vào, cọc hiện ra)
  Đoạn C – S1 "sitcom bờ sông" (thuyền nhẹ giả thua, triều rút, thuyền giặc mắc cọc)
Lời thoại: build/thu-hoathinh/mot-phut/loi.json → thoai.wav/thoai.json (thoai_song_tu.py), chỉ dữ kiện ✅ kho E2 (F9–F11, F14, F17–F20).
Nhạc nền + tiếng động: tự tổng hợp bằng numpy (không dùng nhạc ngoài).

Chạy:  python3 scripts/hoathinh/video_mot_phut.py [--khung 3 20 40]
"""
import argparse
import glob
import json
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ngo_quyen_can_canh as cc  # noqa: E402
import song_tu_doi_thoai as st  # noqa: E402
import mau_phong_cach as mp  # noqa: E402
import thuyen_bach_dang as tb  # noqa: E402
from ngo_quyen_can_canh import cr, hx, mix, clamp, ease, stroke  # noqa: E402

ROOT, SS, W, H, FPS = cc.ROOT, cc.SS, 1920, 1080, 30
DIR = os.path.join(ROOT, 'build', 'thu-hoathinh', 'mot-phut')
D = json.load(open(os.path.join(DIR, 'thoai.json')))
L = D['lines']
ENV = D['env']
DUR = round(D['dur'] + 1.2, 2)
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')
FONTB = os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf')
XF = 0.35                                     # thời gian chuyển cảnh (mờ chéo)

# st.* đọc env/lines của bản 11s → trỏ sang bản 1 phút
st.D, st.ENV = D, ENV


def first(seg):
    return next(l for l in L if l.get('seg') == seg)


B0 = first('B')['start'] - 0.25
C0 = first('C')['start'] - 0.25


def line_at(t):
    for i, l in enumerate(L):
        if l['start'] - 0.05 <= t <= l['end'] + 0.25:
            return i, l
    return None, None


def talk_amt(t, who):
    return st.mouth_open(t) if st.speaking(t) == who else 0.0


# ------------------------------------------------------------------ tiện ích chung
def subtitle(im, t):
    i, l = line_at(t)
    if l is None:
        return
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 40)
    txt = l['text']
    words, rows, cur = txt.split(), [], ''
    for w in words:
        if d.textlength(cur + ' ' + w, font=f) > 1300 and cur:
            rows.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    rows.append(cur)
    y = H - 70 - 52 * len(rows)
    who = 'VÕ' if l['who'] == 'vo' else 'VĂN'
    col = hx('#FFB4A8') if l['who'] == 'vo' else hx('#FFE08A')
    for k, r in enumerate(rows):
        tw = d.textlength(r, font=f)
        x = (W - tw) / 2
        for dx in (-3, 0, 3):
            for dy in (-3, 0, 3):
                d.text((x + dx, y + dy), r, font=f, fill=(30, 22, 20))
        d.text((x, y), r, font=f, fill=(255, 255, 255))
        y += 52
    fs = ImageFont.truetype(FONT, 28)
    tw = d.textlength(rows[0], font=f)
    d.text(((W - tw) / 2 - 2, H - 70 - 52 * len(rows) - 38), who, font=fs, fill=col, stroke_width=3,
           stroke_fill=(30, 22, 20))


def card(text, size=46, rot=-3, fill='#FFF7E2', ink='#2B2222', sub=None):
    f = ImageFont.truetype(FONTB, size)
    fs = ImageFont.truetype(FONT, int(size * 0.55))
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    w = int(max(tmp.textlength(text, font=f), tmp.textlength(sub or '', font=fs)) + 70)
    h = int(size * 1.6 + (size * 0.8 if sub else 0) + 20)
    im = Image.new('RGBA', (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([14, 16, w + 14, h + 16], 18, fill=(0, 0, 0, 60))
    d.rounded_rectangle([6, 6, w + 6, h + 6], 18, fill=hx(fill) + (255,), outline=hx(ink) + (255,), width=4)
    d.text((40, 18), text, font=f, fill=hx(ink))
    if sub:
        d.text((40, 18 + size * 1.25), sub, font=fs, fill=hx('#7A5A3A'))
    d.ellipse([w / 2 - 6, 0, w / 2 + 14, 20], fill=hx('#B3261E'), outline=hx(ink), width=3)   # đinh ghim
    return im.rotate(rot, resample=Image.BICUBIC, expand=True)


def pop(cv, im, cx, cy, t0, t):
    """Thẻ bật ra (phóng to vượt rồi về), cv là canvas SS."""
    if t < t0:
        return
    u = clamp((t - t0) / 0.35)
    k = 1 + 0.18 * math.sin(u * math.pi) if u < 1 else 1.0
    k *= ease(min(1, u * 2.2))
    if k <= 0.02:
        return
    im2 = im.resize((max(1, int(im.width * k * SS)), max(1, int(im.height * k * SS))), Image.LANCZOS)
    cv.alpha_composite(im2, (int(cx * SS - im2.width / 2), int(cy * SS - im2.height / 2)))


def blink(t, who):
    ph = 0.0 if who == 'van' else 1.3
    d = (t + ph) % 3.7
    return math.sin(d / 0.16 * math.pi) if d < 0.16 else 0.0


# ------------------------------------------------------------------ ĐOẠN A: sách sử
CARDS = {}


def seg_a(t):
    cv = mp.canvas('#F4EEDF')
    d = ImageDraw.Draw(cv)
    d.rectangle([0, 860 * SS, W * SS, H * SS], fill=hx('#E2D6BA') + (255,))
    for x in range(0, W + 200, 140):
        d.line([(x * SS, 860 * SS), ((x - 60) * SS, H * SS)], fill=hx('#D4C6A6') + (255,), width=int(2 * SS))
    cc.shape(cv, [(1380, 700), (1800, 700), (1860, 860), (1320, 860)], st.S_('#8A5A3A', '#6A4228'), 2.2, 6, 0,
             light=False)
    cc.shape(cv, [(1420, 690), (1760, 680), (1800, 760), (1390, 770)], st.S_('#EAD9A8', '#CDB880'), 2.2, 4, 0,
             light=False)
    pop(cv, CARDS['nam'], 250, 150, 0.2, t)
    l1, l2, l3 = L[1], L[2], L[3]
    pop(cv, CARDS['nq'], 1250, 200, l1['start'] + 0.9, t)
    pop(cv, CARDS['kct'], 1600, 380, l1['start'] + 3.2, t)
    pop(cv, CARDS['nh'], 1250, 520, l2['start'] + 1.6, t)
    if t > l2['start'] + 1.9:      # mũi tên Kiều Công Tiễn → Nam Hán (nét đứt)
        k = clamp((t - l2['start'] - 1.9) / 0.5)
        a, b = (1560, 440), (1380, 500)
        n = 8
        for j in range(int(n * k)):
            u0, u1 = j / n, (j + 0.55) / n
            stroke(cv, [(a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0),
                        (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1)], 6, 6, hx('#B3261E'))
    old = mp.with_globals(OUTL=2.2, BLUSH=hx('#F6C8B0'), INKC=hx('#1A1414'))
    vo_talk = st.speaking(t) == 'vo'
    st.draw_char(cv, 'vo', 520, 900, 1.45, 1, t, dict(
        blink=blink(t, 'vo'), gaze=(4, 0), smile=0.9, brow=0.6 if vo_talk else 0.2,
        arms=((150 + 15 * math.sin(t * 7), 40), (40, 90)) if vo_talk else ((25, 10), (40, 90)),
        bounce=abs(math.sin(t * 6)) * 0.4 if vo_talk else 0.0))
    st.draw_char(cv, 'van', 900, 900, 1.45, -1, t, dict(blink=blink(t, 'van'), gaze=(-4, 0), smile=0.4))
    mp.restore(*old)
    return cv


# ------------------------------------------------------------------ ĐOẠN B: bản đồ
MAP = {}


def simple_char(cv, x, y, s, col, hat, f=1, talk=0.0, bounce=0.0, eyes=(0, 0)):
    ink = hx('#111111')
    y = y - 22 * bounce * s
    cc.INK = ink

    def C(pts):
        return [(x + f * a * s, y + b * s) for a, b in pts]
    cc.shape(cv, C([(-34, -120), (34, -120), (38, 0), (-38, 0)]), st.S_(col), 5, 0, 0, light=False)
    cc.shape(cv, C(cc.ellipse_pts(0, -170, 52, 50, 40)), st.S_('#FBE3C8'), 5, 0, 0, light=False)
    for ex in (-16, 18):
        cc.shape(cv, C(cc.ellipse_pts(ex + eyes[0], -176 + eyes[1], 7, 9, 16)), dict(b=ink), 0, 0, 0, light=False)
    if talk > 0.1:
        cc.shape(cv, C(cc.ellipse_pts(4, -146, 9 + 4 * talk, 5 + 9 * talk, 16)), dict(b=hx('#5A1A1A')), 3, 0, 0,
                 light=False)
    else:
        stroke(cv, C([(-12, -146), (2, -140), (16, -146)]), 4 * s, 4 * s, ink)
    if hat == 'turban':
        cc.shape(cv, C(cr([(-54, -184), (-46, -218), (0, -230), (46, -218), (54, -184), (0, -196)], n=6)),
                 st.S_('#231B18'), 5, 0, 0, light=False)
        stroke(cv, C([(-48, -196), (-86, -236)]), 7 * s, 5 * s, hx('#8A4A2A'))
    else:
        cc.shape(cv, C(cr([(-56, -186), (-48, -222), (0, -236), (48, -222), (56, -186), (0, -194)], n=6)),
                 st.S_('#8A6A2E'), 5, 0, 0, light=False)
        cc.shape(cv, C([(-4, -236), (4, -236), (2, -256), (-2, -256)]), st.S_('#B3261E'), 3, 0, 0, light=False)
    cc.INK = hx('#2B2222')


def boat_icon(cv, x, y, s, col='#33416A'):
    cc.INK = hx('#111111')
    cc.shape(cv, [(x - 46 * s, y - 10 * s), (x + 46 * s, y - 10 * s), (x + 34 * s, y + 10 * s), (x - 36 * s, y + 10 * s)],
             st.S_('#4A2E22'), 3.5, 0, 0, light=False)
    cc.shape(cv, [(x - 4 * s, y - 12 * s), (x + 2 * s, y - 12 * s), (x + 2 * s, y - 62 * s), (x - 4 * s, y - 62 * s)],
             st.S_('#4A2E22'), 2.5, 0, 0, light=False)
    cc.shape(cv, [(x - 34 * s, y - 58 * s), (x - 2 * s, y - 60 * s), (x - 4 * s, y - 18 * s), (x - 30 * s, y - 20 * s)],
             st.S_(col), 3, 0, 0, light=False)
    cc.INK = hx('#2B2222')


def seg_b(t):
    cv = MAP['bg'].copy()
    mouth = MAP['mouth']
    l4, l5, l6 = L[4], L[5], L[6]
    # đoàn thuyền tiến vào cửa sông
    k = ease((t - l4['start'] - 0.8) / 5.0)
    for i in range(6):
        sx, sy = 1880 + (i % 3) * 60, 600 + (i // 3) * 80 + (i % 3) * 20
        ex, ey = mouth[0] + 190 + (i % 3) * 56, mouth[1] + 50 + (i // 3) * 44
        x, y = sx + (ex - sx) * k, sy + (ey - sy) * k + 3 * math.sin(t * 3 + i)
        if k > 0:
            for j in range(10):     # vệt nước
                u = j / 10
                xx = x + (sx - ex) * 0.06 * (1 + u * 3) * (1 if k < 1 else 0)
                if k < 1:
                    stroke(cv, [(xx + 40 + j * 9, y + 10), (xx + 52 + j * 9, y + 10)], 3, 3, hx('#D8EEF6'))
        boat_icon(cv, x, y, 0.9)
    if t > l4['start'] + 0.6:       # mũi tên nét đứt đường tiến quân
        kk = clamp((t - l4['start'] - 0.6) / 1.2)
        a, b = (1840, 560), (mouth[0] + 80, mouth[1] - 10)
        n = 14
        for j in range(int(n * kk)):
            u0, u1 = j / n, (j + 0.5) / n
            stroke(cv, [(a[0] + (b[0] - a[0]) * u0, a[1] + (b[1] - a[1]) * u0 - 60 * math.sin(u0 * math.pi)),
                        (a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1 - 60 * math.sin(u1 * math.pi))],
                   7, 7, hx('#33416A'))
    # cọc hiện ra ở cửa biển
    if t > l6['start'] + 0.6:
        for i in range(9):
            u = clamp((t - l6['start'] - 0.6 - i * 0.12) / 0.25)
            if u <= 0:
                continue
            x, y = mouth[0] - 10 + i * 18, mouth[1] + 20 + (i % 2) * 10
            hh = 30 * ease(u)
            cc.INK = hx('#111111')
            cc.shape(cv, [(x - 5, y), (x - 2, y - hh), (x, y - hh - 8), (x + 2, y - hh), (x + 5, y)], st.S_('#3A2418'),
                     2.4, 0, 0, light=False)
            cc.INK = hx('#2B2222')
        pop(cv, CARDS['coc'], mouth[0] + 40, mouth[1] - 120, l6['start'] + 2.2, t)
    pop(cv, CARDS['ht'], 1500, 330, l4['start'] + 1.5, t)
    simple_char(cv, 470, 1010, 1.6, '#E0B44A', 'turban', 1, talk_amt(t, 'van'), eyes=(4, -2))
    vo_talk = st.speaking(t) == 'vo'
    simple_char(cv, 690, 1010, 1.6, '#C9342A', 'helmet', 1, talk_amt(t, 'vo'),
                bounce=abs(math.sin(t * 7)) * 0.5 if vo_talk else 0.0, eyes=(5, -2))
    return cv


# ------------------------------------------------------------------ ĐOẠN C: bờ sông sitcom
def stakes_k(t):
    return clamp(ease((t - L[9]['start'] - 0.3) / 2.0))


def river_props(cv, t):
    l7, l9 = L[7], L[9]
    # thuyền lớn giặc trên sông: đuổi theo sang trái, rồi mắc cọc nghiêng
    hit = l9['start'] + 2.2
    if t < hit:
        sx = 1860 - 400 * ease((t - l7['start']) / (hit - l7['start']))
        tilt, sink = 0.0, 0.0
    else:
        q = 1 - math.exp(-(t - hit) * 2.0)
        sx = 1460 - 10 * q
        tilt, sink = -8 * q, 8 * q
    tb.draw_ship(cv, t, sx, 588, 0.3, tilt, sink, far=True)
    tb.waterline(cv, sx, 588 + sink, 110, 0.3)
    # thuyền nhẹ ta: lao ra rồi quay đầu chạy (giả thua)
    if t < l7['start'] + 2.4:
        bx, fl = 700 + 380 * ease((t - l7['start'] + 0.3) / 2.4), 1
    else:
        bx, fl = 1080 - 600 * ease((t - l7['start'] - 2.4) / 4.0), -1
    tb.draw_boat(cv, t, bx, 610, 0.32, fl)
    tb.waterline(cv, bx, 610, 70, 0.32)
    # cọc nhô lên khi triều rút (dùng stakes của S1 với tham số k)
    k = stakes_k(t)
    st.stakes(cv, 9.6 + k * 1.6)
    if t >= hit and t - hit < 0.6:   # nước bắn
        tb.SPLASH[:] = [(hit, sx - 110, 600, 0.9)]
        tb.draw_splashes(cv, t)


def seg_c(t):
    l8, l10 = L[8], L[10]
    who = st.speaking(t)
    close_vo = (l8['start'] - 0.1 <= t <= l8['end'] + 0.2) or (t >= l10['start'] - 0.1)
    vo_st = dict(blink=blink(t, 'vo'), gaze=(4, 0), smile=0.9)
    van_st = dict(blink=blink(t, 'van'), gaze=(-4, 0), smile=0.35)
    if close_vo:
        vo_st.update(arms=((60, 100), (60, 100)), bigeye=1.0, lean=10, brow=1.0,
                     bounce=abs(math.sin(t * 9)) * 0.3)
        if t >= l10['start'] - 0.1:
            vo_st.update(arms=((160, 30), (160, 30)), bigeye=0.6, bounce=abs(math.sin(t * 8)) * 0.6)
        cv = st.bg_close(760, 640, 1.9).copy()
        st.draw_char(cv, 'vo', 840, 1420, 2.7, 1, t, vo_st)
        st.draw_char(cv, 'van', 1980, 1520, 3.2, -1, t, van_st)
        return cv
    cv = st.BG['wide'].copy()
    river_props(cv, t)
    if who == 'van':
        van_st['gaze'] = (-8, -6)
    st.draw_char(cv, 'vo', 760, 930, 1.25, 1, t, vo_st)
    st.draw_char(cv, 'van', 1170, 930, 1.25, -1, t, van_st)
    return cv


# ------------------------------------------------------------------ ghép
def seg_of(t):
    return 'A' if t < B0 else ('B' if t < C0 else 'C')


def raw(t, seg):
    return {'A': seg_a, 'B': seg_b, 'C': seg_c}[seg](t)


def render(t):
    seg = seg_of(t)
    im = raw(t, seg).convert('RGB').resize((W, H), Image.LANCZOS)
    for b, prev in ((B0, 'A'), (C0, 'B')):
        if b <= t < b + XF:            # mờ chéo từ đoạn trước
            im0 = raw(b - 0.01, prev).convert('RGB').resize((W, H), Image.LANCZOS)
            im = Image.blend(im0, im, ease((t - b) / XF))
    subtitle(im, t)
    return im


def init():
    st.build_bg()
    MAP['bg'] = mp.canvas('#7EB6D6')
    P = mp.map_bg(MAP['bg'])
    MAP['mouth'] = P(106.75, 20.9)
    MAP['mouth'] = (MAP['mouth'][0] / SS, MAP['mouth'][1] / SS)
    CARDS['nam'] = card('NĂM 938', 64, -4)
    CARDS['nq'] = card('Ngô Quyền', 50, -3, sub='từ Ái Châu kéo quân ra')
    CARDS['kct'] = card('Kiều Công Tiễn', 46, 3, sub='giết Dương Đình Nghệ (937)')
    CARDS['nh'] = card('→ cầu cứu Nam Hán', 44, -2)
    CARDS['ht'] = card('Hoằng Tháo', 44, 2, sub='đem chiến thuyền vào Bạch Đằng')
    CARDS['coc'] = card('Cọc nhọn bịt sắt', 40, -3)


# ------------------------------------------------------------------ âm thanh
def make_audio():
    import soundfile as sf
    v, sr = sf.read(os.path.join(DIR, 'thoai.wav'), dtype='float32')
    n = int(DUR * sr)
    out = np.zeros(n, np.float32)
    out[:v.size] += v
    t = np.arange(n) / sr
    # nhạc nền: hợp âm ngũ cung D (D–F–G–A–C) dạng pad + gảy nhẹ, đổi màu theo đoạn
    notes = [146.83, 174.61, 196.0, 220.0, 261.63, 293.66]
    pad = np.zeros(n, np.float32)
    for k, fq in enumerate((146.83, 220.0, 293.66)):
        pad += 0.5 * np.sin(2 * np.pi * fq * t + k) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + k))
    pad *= 0.018
    pl = np.zeros(n, np.float32)
    rng = np.random.default_rng(3)
    beat = 0.75
    for i in range(int(DUR / beat)):
        if rng.random() < 0.55:
            fq = notes[rng.integers(len(notes))] * (2 if rng.random() < 0.4 else 1)
            s0 = int(i * beat * sr)
            m = min(n - s0, int(1.2 * sr))
            tt = np.arange(m) / sr
            env = np.exp(-tt * 4.0)
            pl[s0:s0 + m] += (np.sin(2 * np.pi * fq * tt) + 0.3 * np.sin(4 * np.pi * fq * tt)) * env * 0.05
    music = pad + pl
    # giảm nhạc khi có tiếng nói (ducking)
    hop = sr // 30
    envv = np.repeat(np.array(ENV + [0] * (int(DUR * 30) + 2 - len(ENV)), np.float32), hop)[:n]
    duck = 1 - 0.55 * np.clip(np.convolve(envv, np.ones(hop * 6) / (hop * 6), 'same') * 3, 0, 1)
    out += music * duck
    # tiếng động: "bụp" khi thẻ bật, "vút" khi chuyển đoạn, "rắc + ùm" khi thuyền mắc cọc
    def add(at, sig):
        s0 = int(at * sr)
        m = min(n - s0, sig.size)
        if m > 0:
            out[s0:s0 + m] += sig[:m]
    tt = np.arange(int(0.12 * sr)) / sr
    blip = np.sin(2 * np.pi * (700 + 900 * tt / 0.12) * tt) * np.exp(-tt * 30) * 0.12
    for at in (0.2, L[1]['start'] + 0.9, L[1]['start'] + 3.2, L[2]['start'] + 1.6, L[4]['start'] + 1.5,
               L[6]['start'] + 2.2):
        add(at, blip)
    tw = np.arange(int(0.5 * sr)) / sr
    noise = rng.normal(0, 1, tw.size).astype(np.float32)
    whoosh = np.convolve(noise, np.ones(40) / 40, 'same') * np.sin(np.pi * tw / 0.5) ** 2 * 0.25
    for at in (B0 - 0.2, C0 - 0.2):
        add(at, whoosh)
    hit = L[9]['start'] + 2.2
    tc = np.arange(int(0.9 * sr)) / sr
    crack = rng.normal(0, 1, tc.size).astype(np.float32) * np.exp(-tc * 12) * 0.35
    splash = np.convolve(rng.normal(0, 1, tc.size), np.ones(25) / 25, 'same').astype(np.float32) * \
        np.exp(-tc * 3) * 0.5
    add(hit, crack + splash)
    for i in range(6):   # cọc trồi trên bản đồ
        add(L[6]['start'] + 0.6 + i * 0.12, blip * 0.5)
    out = out / max(1e-6, np.abs(out).max()) * 0.92
    p = os.path.join(DIR, 'tieng-tron.wav')
    sf.write(p, out, sr)
    return p


G = {}


def job(i):
    render(i / FPS).save(os.path.join(G['dir'], 'f%05d.jpg' % i), quality=92)
    return i


def init_pool(d):
    init()
    G['dir'] = d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--khung', type=float, nargs='*')
    a = ap.parse_args()
    if a.khung:
        init()
        for t in a.khung:
            p = os.path.join(DIR, 'khung-%05.2f.jpg' % t)
            render(t).save(p, quality=92)
            print(p, seg_of(t))
        return
    wav = make_audio()
    fdir = os.path.join(DIR, 'frames')
    os.makedirs(fdir, exist_ok=True)
    for f in glob.glob(os.path.join(fdir, '*.jpg')):
        os.remove(f)
    n = int(DUR * FPS)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init_pool, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n), chunksize=4)):
            if k % 150 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    silent = os.path.join(DIR, 'mot-phut-cam.mp4')
    subprocess.run(['swift', os.path.join(ROOT, 'scripts', 'hoathinh', 'anh2mp4.swift'), fdir, str(FPS), silent],
                   check=True)
    out = os.path.join(DIR, 'song-tu-bach-dang-1-phut.mp4')
    subprocess.run(['swift', os.path.join(ROOT, 'scripts', 'hoathinh', 'ghep_tieng.swift'), silent, wav, out],
                   check=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
