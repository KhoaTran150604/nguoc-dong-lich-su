"""Gâu Nghệ #1 – Các kiểu người khi đi đánh cầu lông – BẢN 3 (60 khung/giây, nhân vật luôn chuyển động).
Kịch bản: docs/videos/gau-nghe/01-cac-kieu-nguoi-cau-long-v3.md · Động tác: dong_tac.py (đã chấm đạt 80).
Giọng: build/thu-hoathinh/cau-long-v2/thoai.* (A) + build/thu-hoathinh/cau-long-v3/them/thoai.* (B).
Chạy: python scripts/hoathinh/cau_long_v3.py [--khung t ...] [--canh]  → build/thu-hoathinh/cau-long-v3/cau-long-v3.mp4
"""
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
import cau_long_video as V  # noqa: E402
import dong_tac as D  # noqa: E402
from dong_tac import kf, ease, lin, eout, ein, Walker, arc, trail, racket_head, phone_screen, dog_draw, dog_gait, run_fx  # noqa
from nguoi2 import Human, CAST, prop, blob  # noqa: E402
from ngo_quyen_can_canh import SS, INK, hx  # noqa: E402
from gau_nghe_van import ROOT  # noqa: E402

FPS = 60
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'cau-long-v3')
OW, OH = 1280, 720
FONT_B = V.FONT_B
PAW = '#F4F4F4'


# ================================================================== giọng
def load(d):
    j = json.load(open(os.path.join(d, 'thoai.json'), encoding='utf-8'))
    w, sr = sf.read(os.path.join(d, 'thoai.wav'), dtype='float32')
    return j, w, sr


SRC = {}


def voices():
    if not SRC:
        SRC['A'] = load(os.path.join(ROOT, 'build', 'thu-hoathinh', 'cau-long-v2'))
        SRC['B'] = load(os.path.join(OUT, 'them'))
    return SRC


# ================================================================== tiện ích vẽ
def blink(t, ph=0.0):
    return ((t + ph) % 3.4) < 0.1


LINES = []      # (t0, t1, who, src, idx) tuyệt đối – điền khi dựng dòng thời gian


def talk(who, t):
    for t0, t1, w, src, i in LINES:
        if w == who and t0 <= t <= t1:
            j = voices()[src][0]
            ln = j['lines'][i]
            k = int((ln['start'] + t - t0) * 30)
            env = j['env']
            e = env[k] if 0 <= k < len(env) else 0
            e2 = env[k - 1] if 0 < k - 1 < len(env) else 0
            return min(1.0, max(e, 0.6 * e2) * 1.7)
    return None


def H(cv, key, x, gy, t, s=0.5, draw=True, **st):
    """Người: tự chớp mắt + khẩu hình khi đang nói."""
    mo = talk(key, t)
    if mo is not None:
        st['rest'] = st.get('mouth', 'flat') if st.get('mouth') not in ('talk', None) else 'flat'
        st['mouth'], st['mo'] = 'talk', mo
    if blink(t, (hash(key) % 7) * 0.45) and st.get('eyes', 'open') == 'open' and not st.get('lid'):
        st['eyes'] = 'closed'
    h = Human(cv, x, gy, s * (1.13 if key == 'khang' else 1.0), CAST[key], st)
    if draw:
        h.draw()
    return h


def G(cv, x, gy, t, s=0.5, lean=0.0, sq=1.0, racket=None, **st):
    """Gâu: khẩu hình theo giọng, chớp mắt; racket = góc vợt cầm tay phải (None = không cầm)."""
    base = dict(flat=True, mouth='smirk', eyes='open')
    base.update(st)
    if racket is not None and 'R' not in base.get('hand_to', {}):
        base['hand_to'] = dict(base.get('hand_to', {}), R=(104, -138))
    mo = talk('gau', t)
    if mo is not None:
        base['rest'] = base.get('mouth', 'smirk') if base.get('mouth') != 'talk' else 'smirk'
        base['mouth'], base['mo'] = 'talk', mo
    if blink(t, 0.3) and 'lid' not in base and base.get('eyes') == 'open':
        base['lid'] = (1.0, 1.0)
    d = dog_draw(cv, x, gy, s, base, lean=lean, sq=sq)
    if racket is not None and getattr(d, 'hands', None):
        if not lean:
            prop(cv, 'racket', d.hands[1], s, racket, skin=PAW)
    return d


def facepalm(cv, d, k):
    """Tay Gâu che mặt (vẽ đè sau đầu). k 0→1."""
    if k <= 0:
        return
    from ngo_quyen_can_canh import ellipse_pts
    sh = d.P(54, -150)
    hd = d.P(54 + (6 - 54) * k, -150 + (-238 + 150) * k)
    s = d.s
    mx, my = (sh[0] + hd[0]) / 2, (sh[1] + hd[1]) / 2
    L = math.hypot(hd[0] - sh[0], hd[1] - sh[1])
    ang = math.atan2(hd[1] - sh[1], hd[0] - sh[0])
    arm = [(mx + math.cos(ang) * (L / 2 + 6 * s) * math.cos(q) - math.sin(ang) * 14 * s * math.sin(q),
            my + math.sin(ang) * (L / 2 + 6 * s) * math.cos(q) + math.cos(ang) * 14 * s * math.sin(q))
           for q in [i * 2 * math.pi / 32 for i in range(32)]]
    blob(cv, [arm, ellipse_pts(*hd, 24 * s, 20 * s, n=24)], '#23232A', lw=3.0,
         inner=[('poly', ellipse_pts(*hd, 21 * s, 17 * s, n=24), hx('#F4F4F4'))])


def cam(cv, z, cx, cy):
    return V.cam(cv, z, cx, cy)


def card(im, k, big, small):
    V.title_card(im, k, big, small)


def tag(im, k, text, x, y, rot=4, col='#F4EFE4', size=34):
    V.tag(im, k, text, x, y, rot=rot, col=col, size=size)


def flash(im, a):
    if a > 0:
        im = Image.blend(im.convert('RGB'), Image.new('RGB', im.size, (255, 255, 255)), min(1.0, a))
    return im


def clock_overlay(im, hhmm, count=None):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_B, 44)
    d.rounded_rectangle([OW - 230, 18, OW - 20, 86], 14, fill=(20, 17, 15), outline=(243, 210, 122), width=4)
    d.text((OW - 125, 52), hhmm, font=f, fill=(243, 210, 122), anchor='mm')
    if count:
        f2 = ImageFont.truetype(FONT_B, 34)
        tw = d.textlength(count, font=f2)
        d.rounded_rectangle([OW - 40 - tw, 96, OW - 20, 146], 12, fill=(179, 38, 30), outline=INK, width=4)
        d.text((OW - 30 - tw / 2, 121), count, font=f2, fill=(244, 239, 228), anchor='mm')


def hhmm(m):
    m = int(m)
    return '%02d:%02d' % (m // 60, m % 60)


def bubble(cv, x, y, kind, k=1.0):
    """Bong bóng tám dóc có biểu tượng (vẽ phẳng)."""
    if k <= 0:
        return
    r = 46 * min(1, k * 1.5)
    d = ImageDraw.Draw(cv)
    d.ellipse([(x - r) * SS, (y - r * 0.8) * SS, (x + r) * SS, (y + r * 0.8) * SS], fill=hx('#FFFFFF') + (255,), outline=INK + (255,),
              width=4 * SS)
    d.polygon([((x - 10) * SS, (y + r * 0.7) * SS), ((x + 6) * SS, (y + r * 0.7) * SS), ((x - 18) * SS, (y + r * 1.15) * SS)],
              fill=hx('#FFFFFF') + (255,))
    q = r / 46
    if kind == 'tra':        # ly trà sữa
        d.polygon([((x - 16 * q) * SS, (y - 18 * q) * SS), ((x + 16 * q) * SS, (y - 18 * q) * SS), ((x + 11 * q) * SS, (y + 22 * q) * SS),
                   ((x - 11 * q) * SS, (y + 22 * q) * SS)], fill=hx('#C89B6D') + (255,), outline=INK + (255,), width=3 * SS)
        for bx in (-6, 0, 6):
            d.ellipse([(x + bx * q - 3 * q) * SS, (y + 12 * q) * SS, (x + bx * q + 3 * q) * SS, (y + 18 * q) * SS], fill=INK + (255,))
        d.line([((x + 4 * q) * SS, (y - 18 * q) * SS), ((x + 12 * q) * SS, (y - 34 * q) * SS)], fill=INK + (255,), width=4 * SS)
    elif kind == 'u':        # tin nhắn "ừ"
        d.rounded_rectangle([(x - 26 * q) * SS, (y - 16 * q) * SS, (x + 26 * q) * SS, (y + 16 * q) * SS], 8 * SS, fill=hx('#9ED4EE') + (255,),
                            outline=INK + (255,), width=3 * SS)
        d.text((x * SS, y * SS), 'ừ', font=ImageFont.truetype(FONT_B, int(26 * q * SS)), fill=INK + (255,), anchor='mm')
    elif kind == 'tim':      # tim vỡ
        pts = [(x, y + 20 * q), (x - 24 * q, y - 2 * q), (x - 22 * q, y - 18 * q), (x - 10 * q, y - 22 * q), (x, y - 12 * q),
               (x + 10 * q, y - 22 * q), (x + 22 * q, y - 18 * q), (x + 24 * q, y - 2 * q)]
        d.polygon([(px * SS, py * SS) for px, py in pts], fill=hx('#E8505B') + (255,), outline=INK + (255,))
        d.line([(x * SS, (y - 12 * q) * SS), ((x - 5 * q) * SS, (y - 2 * q) * SS), ((x + 4 * q) * SS, (y + 6 * q) * SS), (x * SS, (y + 18 * q) * SS)],
               fill=INK + (255,), width=4 * SS)
    elif kind == '!':
        d.text((x * SS, y * SS), '!!', font=ImageFont.truetype(FONT_B, int(40 * q * SS)), fill=hx('#B3261E') + (255,), anchor='mm')


def bag(cv, x, y, s, open_k=0.0):
    """Túi vợt 6 ngăn to (nằm sàn), open_k: khoá kéo mở lộ 3 cây vợt."""
    w, h = 150 * s, 66 * s
    d = ImageDraw.Draw(cv)
    if open_k > 0:            # 3 cây vợt lòi ra
        for k, (dx, a) in enumerate(((-40, -18), (0, 0), (40, 18))):
            prop(cv, 'racket', (x + dx * s, y - h * 0.5 - 4 * s), s * 0.9, a * open_k, hand=False)
    blob(cv, [[(x - w, y - h), (x + w, y - h), (x + w + 10 * s, y), (x - w - 10 * s, y)]], '#2A2D34', lw=3.0)
    for k in range(3):
        xx = x - w + (k + 0.5) * 2 * w / 3
        d.line([(xx * SS, (y - h + 8 * s) * SS), (xx * SS, (y - 6 * s) * SS)], fill=hx('#C8382E') + (255,), width=int(4 * s * SS))
    d.line([((x - w) * SS, (y - h + 4 * s) * SS), ((x - w + 2 * w * (1 - open_k * 0.9)) * SS, (y - h + 4 * s) * SS)],
           fill=hx('#E8E8E8') + (255,), width=int(5 * s * SS))


# ================================================================== CẢNH 0: mở đầu (8s)
def s0(t):
    cv = V.BG['gym'].copy()
    # nền sau: Khang xoay vợt khởi động; Tùng vươn vai rồi ngồi phịch
    sw = math.sin(t * 5)
    H(cv, 'khang', 1010, 720, t, s=0.42, hold={'R': 'racket'}, gear=True, prop_ang={'R': 75 + 35 * sw},
      arm_to={'R': (135 + 20 * sw, -300 - 30 * math.cos(t * 5)), 'L': (-70, -300)}, mouth='smirk')
    up = kf(t, [(0, 0.0), (1.0, 1.0), (2.6, 1.0), (3.2, 0.0)])
    sit = t > 3.6
    H(cv, 'tung', 1180, 730, t, s=0.42, arm_to={'L': (-60 - 40 * up, -260 - 280 * up), 'R': (60 + 40 * up, -260 - 280 * up)},
      eyes='closed' if up > 0.5 else 'open', mouth='o' if up > 0.5 else 'smile', sit=sit, sit_drop=0.9, gaze=(-1, 0))
    V.net(cv)
    # Gâu đi vào, vác vợt trên vai, dừng giữa sân, quay ra máy
    w = Walker([(0, 60), (0.2, 60), (3.6, 600), (8, 600)])
    x = w.x(t)
    ph = w.phase(t) / 40 * math.pi
    mv = min(1, abs(w.x(t + 1 / 60) - x) * 60 / 30)
    feet, bob = dog_gait(ph, mv)
    look = kf(t, [(3.6, 0.0), (4.0, 1.0)])
    G(cv, x, 868 - bob * 0.5, t, feet=feet, gaze=(1 - look, 0),
      arms=((18 + 26 * math.sin(ph) * mv, 20), (18, 8)), mouth='smirk', racket=25)
    z = kf(t, [(0, 1.3), (3.8, 1.3), (5.0, 1.55)])
    cx = kf(t, [(0, 600), (3.6, 760), (5.0, 720)])
    im = cam(cv, z, cx, kf(t, [(0, 600), (5.0, 640)]))
    return im


# ================================================================== CẢNH 1: trang bị (18s)
def s1(t):
    cv = V.BG['gym'].copy()
    BAGX = 980
    if t < 8.4:
        # Khang sải bước vào, túi xách tay trái → đặt xuống → mở khoá
        wk = Walker([(0, 1560), (0.2, 1560), (3.6, 1120), (8.4, 1120)], stride=30, lift=26)
        x, st, ph, mv = wk.pose(t, 0.5, 22)
        put = kf(t, [(3.7, 0.0), (4.2, 1.0)])
        st.update(mouth='smirk', gaze=(-1, 0) if t < 4.6 else (-0.5, 0.6), gear=True, eyes='open', lid=0.45)
        st.pop('arms')
        slap = kf(t, [(6.6, 0.0), (6.85, 1.0), (7.3, 1.0), (7.6, 0.0)])
        st['arm_to'] = {'L': kf(put, [(0, (-90, -190)), (1, (-120, -100))], lin) if slap == 0 else
                        kf(slap, [(0, (-120, -150)), (1, (-150, -330))], lin), 'R': (60, -250)}
        if slap > 0:
            st['eyes'] = 'angry'
        if put < 0.99:
            pass
        H(cv, 'khang', x, 880, t, **st)
        hk = Human(cv, x, 880, 0.565, CAST['khang'], dict(st))
        lh = hk.P(*hk.arm(-1)[2])
        if put < 1:
            bag(cv, lh[0], lh[1] + 40 * put + 30, 0.5)
        else:
            bag(cv, BAGX, 900, 0.5, open_k=kf(t, [(4.4, 0.0), (5.0, 1.0)]))
        # Tùng lại gần sờ vợt → bị gạt tay, rụt lại
        wt = Walker([(0, 300), (4.8, 300), (6.2, 800), (8.4, 800)], stride=22, lift=16, fat=True)
        tx, tst, _, _ = wt.pose(t, 0.5, 30)
        reach = kf(t, [(6.2, 0.0), (6.6, 1.0), (6.9, 1.0), (7.1, 0.0)])
        tst.pop('arms')
        tst.update(gaze=(1, 0.6), mouth='o' if reach > 0.5 else 'smile', eyes='wide' if t > 6.85 else 'open',
                   arm_to={'R': kf(reach, [(0, (100, -200)), (1, (150, -120))], lin), 'L': (-90, -200)},
                   lean=tst['lean'] + 6 * reach - kf(t, [(6.9, 0.0), (7.2, 6.0), (7.8, 0.0)]))
        H(cv, 'tung', tx, 900, t, **tst)
        im = cam(cv, kf(t, [(0, 1.9), (3.6, 1.9), (4.4, 1.6)]), kf(t, [(0, 1500), (3.6, 1100), (4.4, 1000)]),
                 kf(t, [(0, 760), (3.6, 740), (4.4, 700)]))
        card(im, kf(t, [(0.2, 0.0), (0.7, 1.0)], lin) * (1 if t < 3.2 else max(0, 1 - (t - 3.2) * 3)), 'KIỂU 1', 'Trang bị hơn tuyển quốc gia')
        tag(im, kf(t, [(4.6, 0.0), (5.0, 1.0)], lin), 'VỢT: 3 TRIỆU', 300, 230, rot=-5)
        tag(im, kf(t, [(5.4, 0.0), (5.8, 1.0)], lin), 'GIÀY: 2 TRIỆU', 960, 540, rot=4)
        tag(im, kf(t, [(6.2, 0.0), (6.6, 1.0)], lin), 'TÚI: VỪA CÁI TỦ LẠNH', 640, 170, rot=-3)
        return im
    # ---- vào trận: Tùng giao cầu bổng "ngon ăn" → Khang lùi, nhún, bật nhảy, vung… HỤT
    lt = t - 8.4
    T_SERVE, T_SW, T_PICH = 2.6, 4.45, 4.95
    wt = Walker([(0, 800), (0.2, 800), (1.6, 470), (9, 470)], stride=22, lift=16, fat=True)
    tx, tst, _, _ = wt.pose(lt, 0.5, 30)
    tst.pop('arms')
    hand = kf(lt, [(0, (120, -200)), (2.2, (140, -150)), (T_SERVE, (75, -210), ein), (T_SERVE + 0.25, (130, -380))])
    ang = kf(lt, [(0, 150.0), (2.2, 175.0), (T_SERVE, -122.0, ein), (T_SERVE + 0.25, 20.0)])
    tst.update(hold={'R': 'racket'}, prop_ang={'R': ang}, arm_to={'R': hand, 'L': kf(lt, [(1.6, (-20, -215)), (2.35, (-20, -215)),
                                                                                         (2.6, (-90, -200))])},
               gaze=(1, -0.3), mouth='D' if lt > T_SERVE else 'smile', eyes='happy' if lt > T_PICH + 0.3 else 'open')
    ht = H(cv, 'tung', tx, 840, lt + 8.4, **tst)
    if 1.6 < lt < 2.35:
        lx, ly = ht.P(*ht.arm(-1)[2])
        V.shuttle(cv, lx, ly + 14, 0, 1.0)
    elif 2.35 <= lt < T_SERVE:
        lx, ly = Human(cv, tx, 840, 0.5, CAST['tung'], dict(tst, arm_to={'R': hand, 'L': (-20, -215)})).P(-20, -215)
        k = ((lt - 2.35) / 0.25) ** 2
        rx, ry = racket_head(Human(cv, tx, 840, 0.5, CAST['tung'], dict(tst, arm_to={'R': (75, -210)}, prop_ang={'R': -122})))
        V.shuttle(cv, lx + (rx - lx) * k, ly + 14 + (ry - ly - 14) * k, 0, 1.0)
    V.net(cv)
    # Khang: chờ → lùi 2 bước → nhún → bật nhảy → vung (sớm) → hụt → đáp → đơ → từ từ quay đầu
    wk = Walker([(0, 1120), (0.2, 1120), (1.6, 1180), (3.0, 1180), (3.4, 1250), (9, 1250)], stride=24, lift=20)
    kx, kst, _, _ = wk.pose(lt, 0.5, 22)
    kst.pop('arms')
    J0, J1 = 3.85, 4.75
    cr_ = kf(lt, [(3.45, 0.1), (3.85, 0.85), (3.9, 0.0, ein)]) + (0.08 * (1 + math.sin(lt * 12)) if lt < 3.3 else 0)
    jump = 0
    if J0 <= lt <= J1:
        k = (lt - J0) / (J1 - J0)
        jump = 240 * (4 * k * (1 - k)) ** 0.85
        kst['feet'] = {'L': (-30, -60), 'R': (40, -34)}
    if J1 < lt < J1 + 0.25:
        cr_ = 0.6 * (1 - ease((lt - J1) / 0.25))
    kst['crouch'] = kst['crouch'] + cr_
    hk_ = kf(lt, [(0, (110, -380)), (3.5, (120, -470)), (4.2, (70, -450)), (T_SW, (118, -466), ein), (T_SW + 0.2, (-60, -220))])
    ak_ = kf(lt, [(0, 20.0), (3.5, 60.0), (4.2, 210.0), (T_SW, 14.0, ein), (T_SW + 0.2, -165.0)])
    turn = kf(lt, [(5.6, 0.0), (6.6, 1.0)])
    kst.update(hold={'R': 'racket'}, prop_ang={'R': ak_}, gear=True, arm_to={'R': hk_, 'L': (-60, -500) if J0 - 0.4 < lt < J1 else (-80, -300)},
               gaze=(-1, -0.6) if lt < T_SW else (turn, 0.4 * turn), eyes='angry' if J0 - 0.4 < lt < T_SW else ('wide' if lt > T_SW else 'open'),
               mouth='D' if J0 - 0.4 < lt < T_SW else ('o' if lt > T_SW else 'smirk'), tilt=-10 * turn, sweat=lt > 6.6)
    # cầu: bổng cao, lơ lửng, rơi SAU lưng Khang (vung sớm nên hụt)
    p0 = racket_head(Human(cv, tx, 840, 0.5, CAST['tung'], dict(tst, arm_to={'R': (75, -210)}, prop_ang={'R': -122})))
    land = (1330, 846)
    if T_SERVE <= lt < T_PICH:
        (sx, sy), sa = arc(lt, T_SERVE, T_PICH, p0, land, 470, drag=1.4)
        if sx > kx:
            V.shuttle(cv, sx, sy, sa, 1.0)
        H(cv, 'khang', kx, 880 - jump * 0.565, lt + 8.4, **kst)
        if sx <= kx:
            pts = [arc(lt - i * 0.016, T_SERVE, T_PICH, p0, land, 470, drag=1.4)[0] for i in range(7, 0, -1)]
            trail(cv, pts + [(sx, sy)])
            V.shuttle(cv, sx, sy, sa, 1.0)
    else:
        if lt >= T_PICH:
            q = lt - T_PICH
            V.shuttle(cv, land[0], land[1] - 18 * max(0, 1 - q * 3) * abs(math.sin(q * 12)), -60, 1.0)
        H(cv, 'khang', kx, 880 - jump * 0.565, lt + 8.4, **kst)
    if lt < 7.0:
        z = kf(lt, [(0, 1.15), (2.6, 1.15), (3.6, 1.35), (5.4, 1.35), (6.6, 2.3)])
        cx = kf(lt, [(0, 820), (2.6, 820), (3.6, 1100), (5.4, 1150), (6.6, 1240)])
        cy = kf(lt, [(0, 560), (2.6, 520), (3.6, 520), (5.4, 600), (6.6, 650)])
        return cam(cv, z, cx, cy)
    # cắt sang Gâu bên lưới: thở dài → từ từ che mặt
    cv2 = V.BG['gym'].copy()
    g = lt - 7.0
    k = ease((g - 0.6) / 0.9)
    dg = G(cv2, 720, 880 + 5 * math.sin(min(1, g / 0.6) * math.pi), lt + 8.4, s=0.55, mouth='flat',
           lid=(kf(g, [(0, 0.3), (0.6, 0.75)]),) * 2, gaze=(0.5, 0), brow=(-8, -8), arms=((14, 6), (14, 6)))
    facepalm(cv2, dg, k)
    return cam(cv2, 2.5, 730, 700)


S1_DUR = 8.4 + 9.6


# ================================================================== CẢNH 2: chụp hình (26s)
SNAP = {}


def group_photo(t, tired=False, with_thay=False):
    """Khung chụp chung (dùng cho ảnh đóng băng + ảnh trong story)."""
    cv = V.BG['gym'].copy()
    st_k = dict(arm_to={'R': (128, -262), 'L': (-80, -300)}, gaze=(0.3, -0.2), mouth='flat' if tired else 'grin', eyes='line' if tired else 'open',
                lean=6)
    H(cv, 'khang', 700, 870, 99, **st_k)
    H(cv, 'tung', 990, 880, 99, arm_to={'L': (-130, -380), 'R': (110, -200)}, mouth='flat' if tired else 'D',
      eyes='line' if tired else 'happy', lean=-8, gaze=(-1, -0.2))
    if with_thay:
        H(cv, 'thay', 560, 860, 99, mouth='frown', eyes='angry', arm_to={'L': (-80, -200), 'R': (80, -200)}, gaze=(1, 0))
    H(cv, 'na', 800, 860, 99, hold={'R': 'phone'}, arm_to={'R': (130, -560), 'L': (-60, -330)}, gaze=(0.5, -1), mouth='D', eyes='happy',
      lean=-3)
    G(cv, 900, 900, 99, s=0.46, mouth='flat' if tired else 'tongue', eyes='line' if tired else 'happy', gaze=(0, -1),
      hand_to={'R': (60, -230)})
    return cam(cv, 1.5, 760, 610)


def s2(t):
    if t < 6.0:          # Na vừa đi vừa lướt điện thoại; Gâu vẫy gọi; Na khựng lại, giơ máy
        cv = V.BG['gym'].copy()
        w = Walker([(0, 200), (0.3, 200), (4.0, 760), (9, 760)], stride=14, lift=12)
        x, st, ph, mv = w.pose(t, 0.5, 17)
        st.pop('arms')
        up = kf(t, [(4.6, 0.0), (5.4, 1.0)])
        st.update(hold={'R': 'phone'}, prop_k=1.4 - 0.4 * up,
                  arm_to={'R': kf(up, [(0, (30, -232)), (1, (130, -540))], lin), 'L': (20, -250) if up < 0.5 else (-60, -320)},
                  gaze=(0.2, 1) if t < 4.2 else (1, 0) if t < 4.7 else (0.5, -1), tilt=6 * (1 - up) if t < 4.2 else 0,
                  mouth='smile' if t < 4.2 else 'D', eyes='open')
        h = H(cv, 'na', x, 860, t, **st)
        if up < 0.3:
            phone_screen(cv, h.hands['R'], 0.7, t, thumb=True)
        wave = math.sin(t * 9) if 1.8 < t < 3.8 else 0
        G(cv, 1060, 880, t, s=0.5, gaze=(-1, 0), hand_to={'L': (-112 - 18 * wave, -236 - 30 * abs(wave))} if 1.8 < t < 3.8 else {},
          mouth='smirk' if talk('gau', t) is None else 'talk', racket=None)
        im = cam(cv, kf(t, [(0, 1.7), (4.0, 1.5)]), kf(t, [(0, 420), (4.0, 860)]), 650)
        card(im, kf(t, [(0.1, 0.0), (0.6, 1.0)], lin) * (1 if t < 2.0 else max(0, 1 - (t - 2.0) * 3)), 'KIỂU 2', 'Đến để chụp hình')
        return im
    if t < 15.0:         # chụp chung 2 lần (lần 2 ai cũng mệt)
        lt = t - 6.0
        if lt < 4.8:
            im = D.selfie_raw(min(lt, 3.19)) if lt < 3.2 else None
            if im is None:
                if 'p1' not in SNAP:
                    SNAP['p1'] = D.selfie_raw(3.19).convert('RGB')
                if lt < 3.35:
                    return flash(SNAP['p1'], 1 - (lt - 3.2) / 0.15)
                k = ease((lt - 3.35) / 0.6)
                return polaroid(SNAP['p1'], k)
            return im
        # mọi người tản ra… Na: "thêm tấm nữa!" → cả nhóm chạy ùa lại, mặt mệt → tách tách
        lt2 = lt - 4.8
        cv = V.BG['gym'].copy()
        back = kf(lt2, [(0, 0.0), (1.0, 1.0), (1.6, 1.0), (2.4, 0.0)])
        wk = Walker([(0, 700), (1.0, 420), (1.6, 420), (2.4, 700), (9, 700)], stride=24, lift=20)
        kx, kst, _, _ = wk.pose(lt2, 0.5, 22)
        kst.update(mouth='flat', eyes='line' if lt2 > 2.4 else 'open', gaze=(0.3, 0))
        kst.pop('arms')
        if lt2 > 2.4:
            kst['arm_to'] = {'R': (128, -262), 'L': (-80, -300)}
        H(cv, 'khang', kx, 870, t, **kst)
        wt = Walker([(0, 990), (1.0, 1300), (1.6, 1300), (2.4, 990), (9, 990)], stride=20, lift=14, run=True, fat=True)
        tx, tst, _, _ = wt.pose(lt2, 0.5, 30)
        tst.update(mouth='flat' if lt2 > 2.4 else 'open', mo=0.3, eyes='line' if lt2 > 2.4 else 'open', gaze=(-1, 0), sweat=True)
        H(cv, 'tung', tx, 880, t, **tst)
        H(cv, 'na', 800, 860, t, hold={'R': 'phone'}, arm_to={'R': (130, -560) if lt2 > 1.8 else (120, -300), 'L': (-60, -330)},
          gaze=(0.5, -1) if lt2 > 1.8 else (1, 0), mouth='D', eyes='happy' if lt2 > 2.4 else 'open')
        gy_ = 900 + kf(lt2, [(0, 0.0), (0.8, 200.0), (2.0, 200.0), (2.4, 0.0, eout)])
        G(cv, 900, gy_, t, s=0.46, mouth='flat', eyes='line' if lt2 > 2.4 else 'open', gaze=(0, -1), hand_to={'R': (60, -230)})
        im = cam(cv, 1.5, 760, 610)
        if 2.8 <= lt2 < 2.95:
            im = flash(im, 1 - (lt2 - 2.8) / 0.15)
        if 3.4 <= lt2 < 3.55:
            im = flash(im, 1 - (lt2 - 3.4) / 0.15)
        return im
    if t < 16.6:         # thẻ "20 PHÚT SAU…"
        im = Image.new('RGB', (OW, OH), (20, 17, 15))
        d = ImageDraw.Draw(im)
        k = ease((t - 15.0) / 0.4)
        d.text((OW / 2, OH / 2), '20 PHÚT SAU…', font=ImageFont.truetype(FONT_B, int(72 * (0.8 + 0.2 * k))), fill=(243, 210, 122), anchor='mm')
        return im
    lt = t - 16.6
    if lt < 4.0:         # cả nhóm ngồi bệt chờ; Na nhảy quay TikTok, điện thoại dựng trên chai nước
        cv = V.BG['gym'].copy()
        H(cv, 'khang', 420, 860, t, sit=True, sit_drop=0.95, mouth='flat', eyes='open', lid=0.6, gaze=(1, 0), arm_to={'L': (-60, -150), 'R': (60, -150)})
        H(cv, 'tung', 600, 870, t, sit=True, sit_drop=0.9, mouth='flat', eyes='open', lid=0.5, gaze=(1, 0), sweat=True)
        G(cv, 280, 880, t, s=0.48, mouth='flat', lid=(0.5, 0.5), gaze=(1, 0))
        # điện thoại trên chai
        prop(cv, 'bottle', (1180, 870), 0.5, 0, skin='#A8DCEC')
        prop(cv, 'phone', (1180, 812), 0.5, 0, skin='#2A2A30')
        beat = lt * 2 * math.pi * 1.6
        hop = abs(math.sin(beat)) * 16
        H(cv, 'na', 920, 860 - hop, t, lean=8 * math.sin(beat / 2), mouth='D', eyes='happy',
          arm_to={'R': (110 + 30 * math.sin(beat), -520 + 120 * abs(math.cos(beat))), 'L': (-110 - 30 * math.sin(beat), -300 - 160 * abs(math.sin(beat)))},
          feet={'L': (-30, -18 - 20 * max(0, math.sin(beat))), 'R': (30, -18 - 20 * max(0, -math.sin(beat)))})
        z = kf(lt, [(0, 1.15), (4.0, 1.25)])
        im = cam(cv, z, 760, 600)
        V.clock_hands  # (đồng hồ treo tường có sẵn trong nền)
        return im
    # zoom vào điện thoại: story ảnh nhóm + caption
    k = ease((lt - 4.0) / 1.2)
    cv = V.BG['gym'].copy()
    prop(cv, 'bottle', (1180, 870), 0.5, 0, skin='#A8DCEC')
    prop(cv, 'phone', (1180, 812), 0.5, 0, skin='#2A2A30')
    bg = cam(cv, 1.25 + 2.0 * k, 760 + (1180 - 760) * k, 600 + (790 - 600) * k).convert('RGB')
    return story(bg, ease((lt - 4.0) / 0.5), lt - 4.0)


def polaroid(photo, k, bg=None):
    bg = bg or cam(V.BG['gym'].copy(), 1.5, 760, 610).convert('RGB')
    sz = (int(OW * (1 - 0.35 * k)), int(OH * (1 - 0.35 * k)))
    fr = Image.new('RGB', (sz[0] + 24, sz[1] + 24), (255, 255, 255))
    fr.paste(photo.resize(sz), (12, 12))
    fr = fr.convert('RGBA').rotate(-4 * k, expand=True, resample=Image.BICUBIC)
    bg = bg.copy()
    bg.paste(fr, ((OW - fr.size[0]) // 2, (OH - fr.size[1]) // 2), fr)
    return bg


def story(bg, k, lt):
    """Màn hình điện thoại phóng to: story ảnh chụp chung + caption + tim."""
    if k <= 0:
        return bg
    im = bg.copy()
    pw, ph_ = int(330 * k), int(600 * k)
    if pw < 10:
        return im
    ph = Image.new('RGB', (330, 600), (24, 24, 28))
    if 'p1' not in SNAP:
        SNAP['p1'] = D.selfie_raw(3.19).convert('RGB')
    pic = SNAP['p1'].crop((280, 60, 1000, 720)).resize((300, 275))
    d = ImageDraw.Draw(ph)
    d.rounded_rectangle([6, 6, 324, 594], 30, fill=(250, 250, 250))
    d.rectangle([20, 60, 316, 72], fill=(220, 220, 225))
    d.rectangle([20, 60, 20 + int(296 * min(1, lt / 3)), 72], fill=(240, 120, 140))
    ph.paste(pic, (15, 90))
    f = ImageFont.truetype(V.FONT, 22)
    fb = ImageFont.truetype(FONT_B, 24)
    d.text((24, 24), 'na.caulong', font=fb, fill=(30, 30, 30))
    d.text((24, 380), 'Buổi tập thứ 100.', font=fb, fill=(30, 30, 30))
    d.text((24, 412), 'Chăm chỉ là chìa khóa!', font=f, fill=(30, 30, 30))
    d.text((24, 444), '#caulong #tapluyen', font=f, fill=(40, 110, 200))
    hearts = int(min(1, lt / 2.5) * 1280)
    hx_, hy_ = 40, 520
    pts = [(hx_, hy_ + 14), (hx_ - 16, hy_), (hx_ - 14, hy_ - 10), (hx_ - 6, hy_ - 13), (hx_, hy_ - 6), (hx_ + 6, hy_ - 13), (hx_ + 14, hy_ - 10),
           (hx_ + 16, hy_)]
    d.polygon(pts, fill=(232, 80, 91))
    d.text((68, 506), '%d lượt thích' % hearts, font=fb, fill=(30, 30, 30))
    ph = ph.resize((pw, ph_), Image.LANCZOS)
    im.paste(ph, ((OW - pw) // 2, (OH - ph_) // 2 + 10))
    return im


# ================================================================== CẢNH 3: trọng tài kiêm luật sư (20s)
def gau_swing(lt, keys):
    """Khoá tay vợt Gâu: keys = [(t, (hx,hy), góc)]"""
    hd = kf(lt, [(k[0], k[1]) for k in keys])
    an = kf(lt, [(k[0], k[2]) for k in keys])
    return hd, an


def s3(t):
    cv = V.BG['gym'].copy()
    T1, T2, T3, T4, T5, TL = 1.4, 2.9, 4.1, 5.2, 6.4, 7.3
    # Gâu (trái) – Tùng (phải): đánh qua lại thật, rồi Gâu đập, cầu rơi GIỮA sân Tùng
    gxs = [(0, 460), (2.9, 460), (3.6, 560), (4.3, 520), (5.0, 460), (20, 460)]
    gw = Walker(gxs)
    gx = gw.x(t)
    gph = gw.phase(t) / 40 * math.pi
    gmv = min(1, abs(gw.x(t + 1 / 60) - gx) * 60 / 30)
    gfeet, gbob = dog_gait(gph, gmv)
    gjump = 0
    if 5.9 <= t <= 6.8:
        k = (t - 5.9) / 0.9
        gjump = 150 * 4 * k * (1 - k)
    ghand, gang = gau_swing(t, [(0, (90, -230), 30.0), (1.1, (40, -260), 200.0), (T1, (100, -230), 20.0), (1.7, (90, -200), 60.0),
                                (2.6, (40, -260), 200.0), (T2, (100, -230), 20.0), (3.6, (110, -120), 150.0), (T3, (110, -170), 60.0),
                                (4.8, (40, -260), 200.0), (T4, (100, -230), 20.0), (5.9, (30, -270), 210.0), (T5, (90, -260), 15.0),
                                (6.7, (60, -100), 170.0)])
    # Tùng
    txs = [(0, 1180), (1.6, 1180), (2.2, 1260), (3.2, 1180), (3.8, 1100), (4.4, 1100), (5.0, 1240), (7.6, 1240), (8.1, 1085), (20, 1085)]
    tw = Walker(txs, stride=20, lift=14, fat=True)
    tx, tst, _, _ = tw.pose(t, 0.5, 30)
    tst.pop('arms')
    thand = kf(t, [(0, (110, -300)), (2.5, (130, -400)), (T2 - 0.0, (120, -380)), (2.0, (130, -400)), (2.6, (60, -450)),
                   (T2, (120, -470), ein), (3.2, (-60, -230)), (3.8, (150, -180)), (T3, (170, -280), ein), (4.4, (110, -360)),
                   (5.6, (110, -330))])
    tang = kf(t, [(0, 30.0), (2.6, 210.0), (T2, 15.0, ein), (3.2, -160.0), (3.8, 120.0), (T3, 60.0, ein), (4.4, -10.0), (5.6, 30.0)])
    look = t > T5
    kneel = kf(t, [(8.1, 0.0), (8.5, 1.0), (12.6, 1.0), (13.0, 0.0)])
    point_up = kf(t, [(13.0, 0.0), (13.4, 1.0), (15.0, 1.0), (15.4, 0.0)])
    if t < 8.1:
        tst.update(hold={'R': 'racket'}, prop_ang={'R': tang}, arm_to={'R': thand, 'L': (-90, -260)}, gaze=(-1, -0.4) if not look else (-0.6, 0.8),
                   mouth='o' if look else 'smile', eyes='wide' if look else 'open')
    else:
        tst.update(hold={'L': 'magnifier'}, prop_ang={'L': -150}, crouch=tst['crouch'] + 1.3 * kneel, lean=-14 * kneel, gaze=(-0.7, 0.9) if kneel > 0.5 else (0, -1),
                   arm_to={'L': (-120, -150) if kneel > 0.5 else (-90, -220), 'R': (120, -240) if point_up < 0.5 else (60, -560)},
                   eyes='wide', mouth='open', mo=0.5)
    # cầu
    gh = lambda tt: _gau_rh(tt, gw, ghand, gang)   # noqa: E731
    th = lambda tt: _tung_rh(tt, tw, txs)           # noqa: E731
    LAND = (975, 846)
    shots = [(T1, T2, lambda: gh(T1), lambda: th(T2), 220), (T2, T3, lambda: th(T2), lambda: gh(T3), 200),
             (T3, T4, lambda: gh(T3), lambda: th(T4), 60), (T4, T5, lambda: th(T4), lambda: gh(T5), 230),
             (T5, TL, lambda: gh(T5), LAND, -30)]
    # nhịp: 6.5–7.5 chậm lại 0.35x (quay chậm cú rơi)
    G(cv, gx, 880 - gbob * 0.5 - gjump, t, s=0.5, feet=gfeet, gaze=(1, -0.6) if t < TL else (1, 0.3), hand_to={'R': ghand},
      arms=((18, 8), (18, 8)), mouth='D' if 5.9 < t < 6.6 else 'smirk', racket=gang)
    V.net(cv)
    H(cv, 'tung', tx, 860, t, **tst)
    if T1 - 0.5 < t < T1:            # cầu trong tay Gâu trước khi giao
        pass
    r = None
    for a, b, p0, p1, hh in shots:
        if a <= t < b:
            p0_ = p0() if callable(p0) else p0
            p1_ = p1() if callable(p1) else p1
            r = arc(t, a, b, p0_, p1_, hh)
            pts = [arc(t - i * 0.016, a, b, p0_, p1_, hh)[0] for i in range(7, 0, -1)]
            trail(cv, pts + [r[0]])
            V.shuttle(cv, r[0][0], r[0][1], r[1], 1.0)
    if t >= TL:
        V.shuttle(cv, LAND[0], LAND[1] - 10 * max(0, 1 - (t - TL) * 4), -30, 1.0)
        k = ease((t - TL - 0.2) / 0.4)
        if k > 0:
            d = ImageDraw.Draw(cv)
            rr = 52 * k
            d.ellipse([(LAND[0] - rr) * SS, (LAND[1] - rr * 0.55) * SS, (LAND[0] + rr) * SS, (LAND[1] + rr * 0.55) * SS],
                      outline=hx('#E8202A') + (255,), width=6 * SS)
    if kneel > 0.5 and 8.4 < t < 12.8:   # kính lúp: thấy trái cầu to bên trong
        pass
    # máy quay
    if t < 6.4:
        im = cam(cv, 1.15, 820, 600)
    elif t < 7.9:
        im = cam(cv, kf(t, [(6.4, 1.15), (7.3, 2.2)]), kf(t, [(6.4, 820), (7.3, LAND[0])]), kf(t, [(6.4, 600), (7.3, 760)]))
    elif t < 15.4:
        im = cam(cv, kf(t, [(7.9, 1.6), (13.0, 1.6), (13.5, 1.4)]), kf(t, [(7.9, 960), (10.5, 900)]), kf(t, [(7.9, 700), (13.0, 700), (13.5, 620)]))
    elif t < 17.3:                       # lia lên: cửa sổ đóng kín
        k = ease((t - 15.4) / 0.8)
        im = cam(cv, 1.6, 1000, 700 - 560 * k)
        tag(im, ease((t - 16.1) / 0.3), 'CỬA SỔ: ĐÓNG KÍN', 640, 520, rot=-3, col='#FFD34D')
    else:                                # cận mặt Gâu đơ
        cv2 = V.BG['gym'].copy()
        G(cv2, 900, 880, t, s=0.55, mouth='flat', lid=(0.55, 0.55), gaze=(1, 0))
        im = cam(cv2, kf(t, [(17.3, 2.5), (20, 2.9)]), 900, 700)
    card(im, kf(t, [(0.1, 0.0), (0.6, 1.0)], lin) * (1 if t < 1.0 else max(0, 1 - (t - 1.0) * 3)), 'KIỂU 3', 'Trọng tài kiêm luật sư')
    if 8.4 < t < 12.8 and t < 15.4:      # chèn ô cận kính lúp
        k = ease((t - 8.4) / 0.4) * (1 - ease((t - 12.4) / 0.4))
        if k > 0.02:
            lens_inset(im, k)
    return im


def lens_inset(im, k):
    r = int(130 * k)
    if r < 4:
        return
    lay = Image.new('RGBA', (2 * r + 20, 2 * r + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse([10, 10, 10 + 2 * r, 10 + 2 * r], fill=(214, 240, 248, 255), outline=(20, 17, 15, 255), width=max(2, int(14 * k)))
    # vạch sân + trái cầu to ở GIỮA, cách vạch xa
    d.line([(10, 10 + int(1.7 * r)), (10 + 2 * r, 10 + int(1.55 * r))], fill=(250, 250, 250, 255), width=max(1, int(8 * k)))
    sub = Image.new('RGBA', (300, 300), (0, 0, 0, 0))
    tmp = Image.new('RGBA', (300 * SS, 300 * SS), (0, 0, 0, 0))
    V.shuttle(tmp, 150, 170, -30, 4.0)
    sub = tmp.resize((int(1.4 * r), int(1.4 * r)), Image.LANCZOS)
    lay.alpha_composite(sub, (10 + int(0.3 * r), 10 + int(0.2 * r)))
    m = Image.new('L', lay.size, 0)
    ImageDraw.Draw(m).ellipse([10, 10, 10 + 2 * r, 10 + 2 * r], fill=255)
    arr = np.asarray(lay).copy()
    arr[..., 3] = np.minimum(arr[..., 3], np.asarray(m))
    lay = Image.fromarray(arr)
    ImageDraw.Draw(lay).ellipse([10, 10, 10 + 2 * r, 10 + 2 * r], outline=(20, 17, 15, 255), width=max(2, int(14 * k)))
    im.paste(lay, (OW - 2 * r - 60, 120), lay)


def _gau_rh(tt, gw, ghand, gang):
    tmp = Image.new('RGBA', (8, 8))
    from gau_nghe_van import Dog
    hd, an = gau_swing(tt, [])if False else (None, None)
    return _gau_rh_at(tt, gw)


GAU_KEYS = None


def _gau_rh_at(tt, gw):
    """Mặt vợt của Gâu ở thời điểm tt (tính lại khoá tay)."""
    from gau_nghe_van import Dog
    hd, an = gau_swing(tt, S3_GKEYS)
    x = gw.x(tt)
    gj = 150 * 4 * ((tt - 5.9) / 0.9) * (1 - (tt - 5.9) / 0.9) if 5.9 <= tt <= 6.8 else 0
    dg = Dog(Image.new('RGBA', (8, 8)), x, 880 - gj, 0.5, dict(flat=True))
    p = dg.P(*dg.arm_to(1, hd)[-1])
    a = math.radians(an)
    return (p[0] + math.sin(a) * 120 * 0.5, p[1] - math.cos(a) * 120 * 0.5)


S3_GKEYS = [(0, (90, -230), 30.0), (1.1, (40, -260), 200.0), (1.4, (100, -230), 20.0), (1.7, (90, -200), 60.0),
            (2.6, (40, -260), 200.0), (2.9, (100, -230), 20.0), (3.6, (110, -120), 150.0), (4.1, (110, -170), 60.0),
            (4.8, (40, -260), 200.0), (5.2, (100, -230), 20.0), (5.9, (30, -270), 210.0), (6.4, (90, -260), 15.0),
            (6.7, (60, -100), 170.0)]


def _tung_rh(tt, tw, txs):
    x, st, _, _ = tw.pose(tt, 0.5, 30)
    st.pop('arms')
    hand = kf(tt, [(0, (110, -300)), (2.0, (130, -400)), (2.6, (60, -450)), (2.9, (120, -470), ein), (3.2, (-60, -230)), (3.8, (150, -180)),
                   (4.1, (170, -280), ein), (4.4, (110, -360)), (5.6, (110, -330))])
    ang = kf(tt, [(0, 30.0), (2.6, 210.0), (2.9, 15.0, ein), (3.2, -160.0), (3.8, 120.0), (4.1, 60.0, ein), (4.4, -10.0), (5.6, 30.0)])
    st.update(arm_to={'R': hand}, prop_ang={'R': ang})
    return racket_head(Human(Image.new('RGBA', (8, 8)), x, 860, 0.5, CAST['tung'], st))


# ================================================================== CẢNH 4: chuyên gia nghỉ giải lao (22s)
def s4(t):
    cv = V.BG['gym'].copy()
    # đồng hồ chạy: 17:00 → 17:25 (uống) → 18:05 (bánh mì) → 18:40 (ngủ)
    mins = 17 * 60 + kf(t, [(5.5, 0.0), (7.2, 25.0), (11.5, 25.0), (13.5, 65.0), (16.8, 65.0), (18.4, 100.0)])
    hits = 1 + (t > 9.6) + (t > 15.2)
    rests = int(kf(t, [(2.6, 0.0), (7.2, 3.0), (11.5, 3.0), (13.5, 6.0), (16.8, 6.0), (18.4, 9.0)]))
    # Tùng: đánh 1 trái (1.2) → "nghỉ xíu" → lạch bạch ra mép sân → ngồi uống → về → đánh 1 trái (9.6) → ra ăn bánh mì → ...
    tw = Walker([(0, 560), (2.7, 560), (4.4, 230), (7.6, 230), (9.0, 560), (10.2, 560), (11.4, 230), (30, 230)], stride=22, lift=16, fat=True)
    tx, tst, _, _ = tw.pose(t, 0.5, 30)
    sitting = (4.6 < t < 7.4) or t > 11.6
    hit = lambda tt, th: kf(tt, [(th - 0.5, (140, -150)), (th, (75, -210), ein), (th + 0.25, (130, -380)), (th + 0.6, (110, -260))])  # noqa
    if sitting:
        tst = dict(sit=True, sit_drop=0.9, gaze=(1, 0), mouth='smile', eyes='open')
        if 4.6 < t < 7.4:                                  # uống nước ừng ực
            lt = t - 4.6
            tst.update(hold={'R': 'bottle'}, prop_k=1.4, elbow={'R': 'out'},
                       arm_to={'R': kf(lt, [(0, (120, -170)), (0.5, (110, -330)), (2.2, (100, -360)), (2.6, (120, -190))])},
                       prop_ang={'R': kf(lt, [(0, 0.0), (0.5, -107.0), (2.2, -122.0), (2.6, 0.0)])},
                       tilt=kf(lt, [(0.3, 0.0), (0.6, -17.0), (2.2, -19.0), (2.6, 0.0)]),
                       eyes='closed' if 0.5 < lt < 2.3 else 'happy', mouth='o' if lt < 2.3 else 'D')
        elif 11.6 < t < 14.8:                              # ăn bánh mì: đưa lên cắn 3 miếng
            lt = t - 11.6
            bite = (math.sin(lt * 7) > 0.3)
            tst.update(hold={'R': 'banhmi'}, arm_to={'R': (30 + 10 * bite, -300 + 12 * bite)}, eyes='happy', mouth='o' if bite else 'smile')
        elif 14.8 <= t < 16.6:                             # vỗ tay cổ vũ
            c = abs(math.sin((t - 14.8) * 12))
            tst.update(arm_to={'R': (20 + 40 * c, -250), 'L': (-20 - 40 * c, -250)}, mouth='D', eyes='happy')
        else:                                              # ngủ gật, Z Z Z
            tst.update(eyes='closed', mouth='o', tilt=10 * math.sin((t - 16.6) * 1.2), arm_to={'R': (70, -150), 'L': (-70, -150)})
    else:
        tst.pop('arms')
        th = 1.2 if t < 4 else 9.6
        tst.update(hold={'R': 'racket'}, arm_to={'R': hit(t, th), 'L': (-90, -220)},
                   prop_ang={'R': kf(t, [(th - 0.5, 175.0), (th, -122.0, ein), (th + 0.25, 20.0), (th + 0.6, 40.0)])},
                   gaze=(1, -0.2) if abs(t - th) < 1 else (-1, 0), mouth='smile', sweat=True)
    ht = H(cv, 'tung', tx, 860, t, **tst)
    if t > 16.8:
        V.zzz(cv, tx + 40, 860 - 230, t)
    # Khang chờ: gõ chân, khoanh tay; sau đó đánh với Gâu
    if t < 14.6:
        tap = max(0, math.sin(t * 8)) * 34 if (3 < t < 9 or 11 < t < 14.6) else 0
        H(cv, 'khang', 1180, 870, t, hold={'R': 'racket'}, prop_ang={'R': 165}, mouth='flat', lid=0.5, gaze=(-1, 0),
          arm_to={'L': (40, -270), 'R': (110, -190)}, feet={'L': (-24, -18), 'R': (24, -18 - tap)},
          brow=(14, 14) if tap else 0)
        G(cv, 760, 880, t, s=0.48, mouth='flat', lid=(0.4, 0.4), gaze=(-1, 0))
    else:                                                  # Gâu & Khang tự đánh với nhau
        lt = t - 14.6
        sw = math.sin(lt * 2 * math.pi / 1.4)
        H(cv, 'khang', 1180, 870, t, hold={'R': 'racket'}, prop_ang={'R': 40 * sw}, arm_to={'R': (110 + 30 * sw, -420 - 40 * sw)},
          mouth='grin', gear=True, gaze=(-1, -0.5), crouch=0.1 + 0.1 * abs(sw))
        G(cv, 700, 880, t, s=0.5, hand_to={'R': (80 + 20 * sw, -230 - 30 * sw)}, gaze=(1, -0.5), racket=30 * sw, mouth='tongue')
        k = (lt % 1.4) / 1.4
        (sx, sy), sa = arc(k, 0, 1, (790, 690) if int(lt / 1.4) % 2 == 0 else (1230, 600),
                           (1230, 600) if int(lt / 1.4) % 2 == 0 else (790, 690), 170)
        V.shuttle(cv, sx, sy, sa, 1.0)
    if 0 < t < 2.2:
        pass
    V.net(cv)
    im = cam(cv, kf(t, [(0, 1.2), (4.0, 1.3), (14.6, 1.3), (16.8, 1.15), (17.6, 1.7)]),
             kf(t, [(0, 820), (4.0, 700), (14.6, 700), (16.8, 820), (17.6, 360)]), kf(t, [(0, 600), (16.8, 600), (17.6, 680)]))
    clock_overlay(im, hhmm(mins), 'ĐÁNH: %d · NGHỈ: %d' % (hits, rests))
    card(im, kf(t, [(0.1, 0.0), (0.6, 1.0)], lin) * (1 if t < 2.4 else max(0, 1 - (t - 2.4) * 3)), 'KIỂU 4', 'Chuyên gia nghỉ giải lao')
    return im


# ================================================================== CẢNH 5: chuyên gia tám dóc (15s)
def s5(t):
    cv = V.BG['gym'].copy()
    wn = Walker([(0, 300), (0.8, 300), (3.0, 730), (30, 730)], stride=14, lift=14)
    nx, nst, ph, _ = wn.pose(t, 0.5, 17)
    wt = Walker([(0, 1450), (0.8, 1450), (3.0, 1000), (30, 1000)], stride=20, lift=14, fat=True)
    tx, tst, _, _ = wt.pose(t, 0.5, 30)
    chat = t > 3.0
    g = math.sin(t * 6)
    if chat:
        nst.pop('arms')
        nst.update(arm_to={'R': (100 + 30 * g, -330 - 40 * g), 'L': (-60, -230)}, gaze=(1, 0), mouth='D', eyes='open')
        shock = kf(t, [(7.0, 0.0), (7.3, 1.0), (8.8, 1.0), (9.2, 0.0)])
        tst.pop('arms')
        tst.update(gaze=(-1, 0), eyes='wide' if shock > 0.5 else 'open', mouth='o' if shock > 0.5 else 'smile',
                   arm_to={'L': (-50, -330), 'R': (50, -330)} if shock > 0.5 else {'L': (-90 - 30 * g, -260), 'R': (100, -220)})
    # cầu rơi trúng đầu Tùng (10.6) → Tùng gạt như đuổi ruồi (10.9) → vẫn tám
    swat = kf(t, [(10.8, 0.0), (11.0, 1.0), (11.25, 0.0)])
    if swat > 0:
        tst['arm_to'] = {'R': (60 + 80 * swat, -480), 'L': (-90, -260)}
    H(cv, 'na', nx, 860, t, **nst)
    V.net(cv)
    H(cv, 'tung', tx, 870, t, **tst)
    if chat:
        k = (t - 3.0)
        for i, (kind, bx, by, tt0) in enumerate((('tra', nx - 40, 470, 3.4), ('u', nx + 30, 440, 5.0), ('tim', tx + 30, 450, 7.4),
                                                  ('!', tx - 30, 430, 7.2))):
            a = kf(t, [(tt0, 0.0), (tt0 + 0.3, 1.0), (tt0 + 2.6, 1.0), (tt0 + 2.9, 0.0)])
            bubble(cv, bx, by - 8 * math.sin(t * 3 + i), kind, a)
    # Gâu chờ phát cầu: tâng cầu, chờ, ngáp, phát
    yawn = 8.2 < t < 9.0
    bounce = abs(math.sin(t * 5)) if 3.0 < t < 8.0 else 0
    G(cv, 330, 880, t, s=0.5, hand_to={'R': (104, -150 - 14 * bounce)}, racket=10 + 10 * bounce, gaze=(1, -0.3) if t < 9.4 else (1, -0.6),
      mouth='open' if yawn else 'flat', mo=1.0, lid=(0.5, 0.5) if yawn else (0.2, 0.2))
    if 3.0 < t < 9.4:
        V.shuttle(cv, 395, 735 - 70 * bounce, 0, 1.0)
    T0, T1 = 9.6, 10.6
    head = (tx + 4, 870 - 450 * 0.5)
    if T0 <= t < T1:
        (sx, sy), sa = arc(t, T0, T1, (395, 730), head, 300)
        V.shuttle(cv, sx, sy, sa, 1.0)
    elif t >= T1:
        q = t - T1
        if q < 0.35:
            V.shuttle(cv, head[0] + 120 * q, head[1] - 140 * q + 500 * q * q, 180 + 400 * q, 1.0)
            if q < 0.12:
                V.stars(cv, head[0], head[1] - 10, 30, t)
        else:
            V.shuttle(cv, head[0] + 42, 846, -70, 1.0)
    if t < 11.8:
        im = cam(cv, kf(t, [(0, 1.15), (3.0, 1.35)]), kf(t, [(0, 820), (3.0, 720)]), kf(t, [(0, 560), (3.0, 600)]))
    else:
        cv2 = V.BG['gym'].copy()
        G(cv2, 330, 880, t, s=0.55, mouth='flat', lid=(0.55, 0.55), gaze=(1, 0), racket=10)
        im = cam(cv2, 2.5, 360, 700)
    card(im, kf(t, [(0.1, 0.0), (0.6, 1.0)], lin) * (1 if t < 2.2 else max(0, 1 - (t - 2.2) * 3)), 'KIỂU 5', 'Chuyên gia tám dóc')
    return im


# ================================================================== CẢNH 6: … là Gâu Nghệ (15s)
def s6(t):
    cv = V.BG['gym'].copy()
    T_HIT, T_SEE, T_DROP, T_RUN, T_JUMP, T_CATCH, T_LAND = 2.2, 2.9, 3.8, 4.6, 5.6, 5.9, 6.25
    # Khang (phải) đánh cầu bổng thật cao
    ka = kf(t, [(1.6, 0.0), (T_HIT, 1.0, ein)])
    H(cv, 'khang', 1250, 870, t, hold={'R': 'racket'}, gear=True, gaze=(-1, -0.8) if t < 7 else (-1, 0.4),
      arm_to={'R': kf(t, [(0, (110, -300)), (1.6, (140, -150)), (T_HIT, (80, -470), ein), (T_HIT + 0.3, (40, -480)), (3.2, (110, -230))])},
      prop_ang={'R': kf(t, [(0, 20.0), (1.6, 170.0), (T_HIT, -20.0, ein), (T_HIT + 0.3, -30.0), (3.2, 30.0)])}, mouth='grin' if t < 7.5 else 'o',
      eyes='open' if t < 7.5 else 'wide')
    # Thầy Ba đi nhanh vào, thổi còi, chỉ tay
    if t > 9.4:
        tw = Walker([(9.4, 1700), (10.6, 1440), (30, 1440)], stride=26, lift=18)
        tx, tst, _, _ = tw.pose(t, 0.5, 23)
        tst.pop('arms')
        blow = 9.6 < t < 10.4
        tst.update(hold={'R': 'whistle'} if blow else {}, arm_to={'R': (54, -345)} if blow else {'R': (-200, -330), 'L': (-80, -200)},
                   mouth='o' if blow else 'frown', eyes='angry', gaze=(-1, 0.3))
        H(cv, 'thay', tx, 860, t, **tst)
    V.net(cv)
    # Gâu: nhìn cầu bay lên, mắt sáng, vợt tuột, lấy đà, chạy, nhảy ngậm cầu, chạy về đặt dưới chân Khang
    def gx(tt):
        return kf(tt, [(0, 420), (T_RUN, 420), (T_JUMP, 900, lin), (T_LAND, 1010, eout), (7.4, 1010), (8.6, 1150), (30, 1150)])

    def gy(tt):
        y = 880 + kf(tt, [(4.1, 0.0), (4.45, 14.0), (4.6, 0.0)]) + kf(tt, [(5.35, 0.0), (5.56, 34.0), (5.62, 0.0)])
        if T_JUMP <= tt <= T_LAND:
            k = (tt - T_JUMP) / (T_LAND - T_JUMP)
            y -= 300 * 4 * k * (1 - k)
        return y + kf(tt, [(T_LAND, 0.0), (T_LAND + 0.1, 18.0), (T_LAND + 0.35, 0.0)])
    x = gx(t)
    w = Walker([(0, 420), (T_RUN, 420), (T_JUMP, 900, lin), (T_LAND, 1010, eout), (7.4, 1010), (8.6, 1150), (30, 1150)], run=True)
    ph = w.phase(t) / 0.5 / 70 * math.pi
    running = T_RUN < t < T_JUMP or 7.4 < t < 8.6
    mv = min(1, abs(gx(t + 1 / 60) - x) * 60 / 40) if running else 0
    feet, bob = dog_gait(ph, mv, run=True)
    flying = T_JUMP <= t <= T_LAND
    if flying:
        feet = ((-26, 34), (-10, 30))
    mouth_at = lambda tt: (gx(tt) + 9, gy(tt) - 111)   # noqa: E731
    see = kf(t, [(T_SEE, 0.0), (T_SEE + 0.5, 1.0)])
    wag = math.sin(t * 14) if t > T_LAND + 0.3 else 0
    st = dict(eyes='wide' if see > 0.5 else 'open', big=1 + 0.3 * see, gaze=(1, -1) if t < T_JUMP else (1, -0.4) if t < 7.4 else (1, 0),
              mouth='tongue' if T_RUN < t < T_JUMP else ('open' if t < T_CATCH and t > T_SEE else 'smirk'), mo=1.0, feet=feet,
              arms=((50 + 80 * math.sin(ph) * mv, 90), (50 - 80 * math.sin(ph) * mv, 90)) if not flying else ((150, 30), (150, 30)))
    lean = 22 * mv + (18 * (1 - 2 * (t - T_JUMP) / (T_LAND - T_JUMP)) if flying else 0) + 4 * wag
    sq = kf(t, [(5.35, 1.0), (5.56, 0.84), (5.64, 1.18), (5.8, 1.04), (T_LAND - 0.05, 1.08), (T_LAND + 0.06, 0.8), (T_LAND + 0.2, 1.06),
                (T_LAND + 0.32, 1.0)])
    if running:
        sq = 1 + 0.08 * math.cos(2 * ph)
        run_fx(cv, x, gy(t), t, ph)
    if T_SEE < t < T_SEE + 0.9:
        V.sparkles(cv, [(x - 30, 880 - 160), (x + 40, 880 - 170)], t)
    y = gy(t) - bob
    G(cv, x, y, t, s=0.5, lean=lean, sq=sq, racket=-60 if t < T_DROP else None, **st)
    if T_DROP <= t:                       # vợt tuột tay rơi xuống sàn
        q = min(1, (t - T_DROP) / 0.35)
        prop(cv, 'racket', (420 + 40 * q, 780 + 80 * q * q), 0.5, -60 + 150 * q, hand=False)
    # cầu
    p0 = (1300, 380)
    if T_HIT <= t < T_CATCH:
        (sx, sy), sa = arc(t, T_HIT, T_CATCH, p0, mouth_at(T_CATCH), 360, drag=1.2)
        pts = [arc(t - i * 0.016, T_HIT, T_CATCH, p0, mouth_at(T_CATCH), 360, drag=1.2)[0] for i in range(7, 0, -1)]
        trail(cv, pts + [(sx, sy)])
        V.shuttle(cv, sx, sy, sa, 1.0)
    elif t >= T_CATCH and t < 8.9:
        V.shuttle(cv, x + 9 + 18, y - 111 + 2, 90, 1.0)
    elif t >= 8.9:
        V.shuttle(cv, 1150 + 40, 870, -70, 1.0)
    # máy quay
    if t < T_SEE:
        im = cam(cv, kf(t, [(0, 1.15), (T_HIT, 1.15), (T_SEE, 1.25)]), kf(t, [(0, 820), (T_SEE, 720)]), kf(t, [(0, 560), (T_SEE, 480)]))
    elif t < 9.2:
        cx = x + 90
        im = cam(cv, kf(t, [(T_SEE, 1.25), (3.4, 1.9), (T_RUN, 1.7)]), cx, kf(t, [(3.4, 700), (5.4, 690), (5.75, 540), (6.0, 560), (6.6, 700)]))
    else:
        im = cam(cv, kf(t, [(9.2, 1.4), (11.0, 1.4), (12.0, 1.9)]), kf(t, [(9.2, 1250), (12.0, 1180)]), kf(t, [(9.2, 620), (12.0, 680)]))
    card(im, kf(t, [(0.1, 0.0), (0.6, 1.0)], lin) * (1 if t < 1.6 else max(0, 1 - (t - 1.6) * 3)), 'KIỂU 6', '…là Gâu Nghệ')
    return im


# ================================================================== CẢNH 7: kết (9s) – chụp chung lần nữa, có cả Thầy
def s7(t):
    if t < 2.4:
        cv = V.BG['gym'].copy()
        k = ease(t / 1.6)
        H(cv, 'thay', 1300 - 740 * k, 860, t, mouth='frown', eyes='angry' if t < 1.8 else 'wide', gaze=(1, 0),
          arm_to={'R': (120, -300), 'L': (-80, -200)}, lean=-10 * (1 - k))
        H(cv, 'khang', 700, 870, t, arm_to={'R': (128, -262), 'L': (-80, -300)}, mouth='grin', lean=6)
        H(cv, 'tung', 990, 880, t, arm_to={'L': (-130, -380), 'R': (110, -200)}, mouth='D', eyes='happy', lean=-8)
        H(cv, 'na', 800, 860, t, hold={'R': 'phone'}, arm_to={'R': (130, -560), 'L': (-60, -330)}, gaze=(0.5, -1), mouth='D', eyes='happy')
        G(cv, 900, 900, t, s=0.46, mouth='tongue', eyes='happy', gaze=(0, -1), hand_to={'R': (60, -230)})
        return cam(cv, 1.5, 760, 610)
    if 'p2' not in SNAP:
        SNAP['p2'] = group_photo(0, with_thay=True).convert('RGB')
    if t < 2.55:
        return flash(SNAP['p2'], 1 - (t - 2.4) / 0.15)
    im = polaroid(SNAP['p2'], ease((t - 2.55) / 0.6))
    tag(im, ease((t - 3.3) / 0.4), 'BẠN LÀ KIỂU NÀO?', 640, 650, rot=-2, col='#FFD34D', size=44)
    return im


# ================================================================== dòng thời gian
SEGS = [  # (tên, độ dài, hàm, thoại [(t, nguồn, chỉ số, ai)], tiếng động [(t, loại)])
    ('mo', 8.0, s0, [(4.2, 'A', 0, 'gau')], [(0.6, 'step'), (1.4, 'step'), (2.2, 'step'), (3.0, 'step')]),
    ('trang-bi', S1_DUR, s1, [(0.3, 'A', 1, 'gau'), (4.6, 'A', 2, 'gau'), (8.4 + 1.0, 'A', 3, 'tung'), (8.4 + 8.0, 'A', 4, 'gau')],
     [(4.2, 'thud'), (4.5, 'zip'), (6.85, 'slap'), (8.4 + 2.6, 'hit'), (8.4 + 3.6, 'squeak'), (8.4 + 4.35, 'whoosh'), (8.4 + 4.95, 'pich'),
      (8.4 + 7.4, 'sigh')]),
    ('chup-hinh', 26.0, s2, [(0.3, 'A', 5, 'gau'), (2.2, 'A', 6, 'gau'), (4.3, 'A', 7, 'na'), (6.0 + 5.0, 'B', 2, 'na'),
                             (16.6 + 5.2, 'A', 8, 'gau')],
     [(6.0 + 3.2, 'shutter'), (6.0 + 4.8 + 2.8, 'shutter'), (6.0 + 4.8 + 3.4, 'shutter'), (15.0, 'whoosh')]),
    ('trong-tai', 20.0, s3, [(0.2, 'A', 9, 'gau'), (8.3, 'A', 10, 'tung'), (11.0, 'A', 11, 'gau'), (13.2, 'A', 12, 'tung'), (17.8, 'A', 13, 'gau')],
     [(1.4, 'hit'), (2.9, 'hit'), (4.1, 'hit'), (5.2, 'hit'), (6.4, 'smash'), (7.3, 'pich'), (7.6, 'ding'), (8.0, 'step'), (8.3, 'step')]),
    ('nghi', 21.0, s4, [(0.3, 'B', 0, 'gau'), (2.2, 'B', 3, 'tung'), (15.0, 'A', 18, 'tung'), (18.6, 'A', 19, 'gau')],
     [(1.2, 'hit'), (9.6, 'hit'), (5.2, 'gulp'), (5.6, 'gulp'), (6.0, 'gulp'), (6.5, 'ahh'), (12.0, 'bite'), (12.9, 'bite'), (13.8, 'bite')]),
    ('tam', 15.0, s5, [(0.3, 'B', 1, 'gau'), (3.5, 'A', 21, 'na'), (7.2, 'A', 22, 'tung'), (12.4, 'A', 23, 'gau')],
     [(9.6, 'hit'), (10.6, 'bonk'), (11.0, 'whoosh')]),
    ('gau', 14.5, s6, [(0.2, 'A', 24, 'gau'), (10.6, 'A', 25, 'thay'), (12.4, 'A', 26, 'gau')],
     [(2.2, 'hit'), (3.8, 'clack'), (5.6, 'whoosh'), (5.9, 'catch'), (9.6, 'whistle'), (10.1, 'whistle')]),
    ('ket', 9.0, s7, [(4.0, 'A', 27, 'gau')], [(2.4, 'shutter')]),
]
T0S = []
acc = 0.0
for name, dur, fn, cues, sfx in SEGS:
    T0S.append(acc)
    acc += dur
DUR = acc


def build_lines():
    LINES.clear()
    for (name, dur, fn, cues, sfx), t0 in zip(SEGS, T0S):
        for tl, src, i, who in cues:
            ln = voices()[src][0]['lines'][i]
            LINES.append((t0 + tl, t0 + tl + ln['end'] - ln['start'], who, src, i))


def render(t):
    V.build()
    if not LINES:
        build_lines()
    for (name, dur, fn, cues, sfx), t0 in zip(SEGS, T0S):
        if t < t0 + dur or name == SEGS[-1][0]:
            return _render_seg(fn, t - t0, t)
    return None


TABS = 0.0


def _render_seg(fn, lt, tabs):
    # hàm cảnh nhận thời gian CỤC BỘ; khẩu hình cần thời gian TUYỆT ĐỐI → bù qua biến toàn cục
    global TOFF
    TOFF = tabs - lt
    im = fn(lt)
    return im.convert('RGB')


TOFF = 0.0
_talk = talk


def talk(who, t):  # noqa: F811  (thời gian cục bộ → tuyệt đối)
    return _talk(who, t + TOFF)


# ================================================================== âm thanh
def make_audio(path):
    sr = 48000
    n = int(DUR * sr)
    out = np.zeros(n, np.float32)
    rng = np.random.default_rng(7)

    def add(at, sig, g=1.0):
        s0 = int(at * sr)
        m = min(n - s0, sig.size)
        if m > 0 and s0 >= 0:
            out[s0:s0 + m] += sig[:m] * g
    tone, noise, mix = V.tone, V.noise, V.mix
    voice = np.zeros(n, np.float32)
    for t0, t1, who, src, i in LINES:
        j, w, ssr = voices()[src]
        ln = j['lines'][i]
        clip = w[int(ln['start'] * ssr):int(ln['end'] * ssr)]
        if clip.ndim > 1:
            clip = clip.mean(axis=1)
        s0 = int(t0 * sr)
        m = min(n - s0, clip.size)
        voice[s0:s0 + m] += clip[:m]
    # nhạc nền nhẹ (ngũ cung), né lời thoại
    music = np.zeros(n, np.float32)
    beat = 60 / 120
    scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33]
    mel = [0, 2, 4, 2, 5, 4, 2, 4, 3, 1, 0, 1, 2, 4, 5, 6]
    bass = [130.81, 110.0, 98.0, 87.31]
    for k in range(int(DUR / beat) + 1):
        at = k * beat
        if k % 2 == 0:
            s0 = int(at * sr)
            sig = tone(bass[(k // 8) % 4], 0.45, sr, 'sin', 5)
            m = min(n - s0, sig.size)
            if m > 0:
                music[s0:s0 + m] += sig[:m] * 0.2
        sig = tone(scale[mel[k % 16]] * 2, 0.3, sr, 'pluck', 10)
        s0 = int(at * sr)
        m = min(n - s0, sig.size)
        if m > 0:
            music[s0:s0 + m] += sig[:m] * 0.06
    env = np.abs(voice)
    k_ = sr // 10
    sm = np.convolve(env, np.ones(k_) / k_, 'same')
    duck = 1 - 0.65 * np.clip(sm * 12, 0, 1)
    out += voice + music * duck
    tw = np.arange(int(0.25 * sr)) / sr
    S = dict(
        whoosh=(np.convolve(rng.normal(0, 1, tw.size), np.ones(30) / 30, 'same') * np.sin(np.pi * tw / 0.25) ** 2).astype(np.float32) * 0.5,
        hit=mix(tone(900, 0.08, sr, 'sin', 40), noise(0.05, sr, rng, 60)) * 0.5,
        smash=mix(tone(600, 0.12, sr, 'sin', 25), noise(0.12, sr, rng, 30)) * 0.8,
        pich=mix(tone(320, 0.12, sr, 'sin', 40), noise(0.04, sr, rng, 80)) * 0.6,
        bonk=mix(tone(220, 0.25, sr, 'sin', 14), noise(0.08, sr, rng, 40) * 0.5) * 0.7,
        shutter=mix(noise(0.03, sr, rng, 150), noise(0.05, sr, rng, 90)[::-1]) * 0.5,
        step=noise(0.04, sr, rng, 80, 3) * 0.3,
        thud=mix(tone(90, 0.25, sr, 'sin', 12), noise(0.06, sr, rng, 50)) * 0.6,
        zip=noise(0.35, sr, rng, 4, 2) * 0.25,
        slap=noise(0.06, sr, rng, 70) * 0.7,
        squeak=(np.sin(2 * np.pi * (1800 + 600 * np.sin(np.arange(int(0.18 * sr)) / sr * 40)) * np.arange(int(0.18 * sr)) / sr)
                * np.sin(np.pi * np.arange(int(0.18 * sr)) / sr / 0.18)).astype(np.float32) * 0.15,
        sigh=noise(0.8, sr, rng, 3, 60) * 0.35,
        ding=tone(1320, 0.5, sr, 'pluck', 6) * 0.3,
        gulp=mix(tone(180, 0.12, sr, 'sin', 30), tone(240, 0.1, sr, 'sin', 35)) * 0.5,
        ahh=tone(420, 0.4, sr, 'sin', 5) * 0.15,
        bite=noise(0.06, sr, rng, 60, 2) * 0.5,
        clack=tone(400, 0.15, sr, 'sin', 20) * 0.4,
        catch=tone(1200, 0.3, sr, 'pluck', 8) * 0.3,
    )
    tt = np.arange(int(0.45 * sr)) / sr
    S['whistle'] = (np.sin(2 * np.pi * 2900 * tt + 8 * np.sin(2 * np.pi * 38 * tt)) * np.minimum(1, tt * 40) * np.exp(-tt * 2)).astype(np.float32) * 0.25
    for (name, dur, fn, cues, sfx), t0 in zip(SEGS, T0S):
        add(t0, S['whoosh'], 0.4)
        for tl, kind in sfx:
            add(t0 + tl, S[kind])
    out = np.tanh(out / max(1e-6, np.percentile(np.abs(out), 99.7)) * 0.9) * 0.88
    sf.write(path, out, sr)


# ================================================================== chạy
GG = {}


def init(d):
    V.build()
    build_lines()
    GG['d'] = d


def job(i):
    render(i / FPS).save(os.path.join(GG['d'], 'f%05d.jpg' % i), quality=92)


def main():
    os.makedirs(OUT, exist_ok=True)
    V.build()
    build_lines()
    if '--khung' in sys.argv or '--canh' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--khung') + 1:]] if '--khung' in sys.argv else []
        if '--canh' in sys.argv:
            for (name, dur, fn, cues, sfx), t0 in zip(SEGS, T0S):
                ts += [t0 + dur * k / 6 for k in range(6)]
        cols = 6
        ims = [render(t).resize((320, 180)) for t in ts]
        sh = Image.new('RGB', (cols * 320, ((len(ims) + cols - 1) // cols) * 180))
        d = ImageDraw.Draw(sh)
        for k, im in enumerate(ims):
            sh.paste(im, ((k % cols) * 320, (k // cols) * 180))
            d.text(((k % cols) * 320 + 4, (k // cols) * 180 + 164), '%.1fs' % ts[k], fill=(255, 255, 0))
        p = os.path.join(OUT, 'bang-khung.jpg')
        sh.save(p, quality=88)
        print(p, 'DUR=%.1f' % DUR)
        return
    fdir = tempfile.mkdtemp(prefix='cl3-')
    n = int(DUR * FPS)
    print('Thời lượng %.1fs, %d khung' % (DUR, n), flush=True)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n), chunksize=4)):
            if k % 300 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    wav = os.path.join(fdir, 'a.wav')
    make_audio(wav)
    out = os.path.join(OUT, 'cau-long-v3.mp4')
    subprocess.run([V.ffmpeg(), '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, 'f%05d.jpg'), '-i', wav,
                    '-c:v', 'libx264', '-crf', '19', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', out], check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
