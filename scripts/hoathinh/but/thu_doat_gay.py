"""THỬ TRẬN ĐẤU — Hồ Lô Tử Kim HÚT Gậy Như Ý (giằng co ~10s, 16:9).

Beat: hồ lô mở nắp hút → gió xoáy → Ngộ Không gồng giữ gậy → bị kéo gần →
      kéo lại được một chút → thua, gậy tuột bay vào hồ lô "tụp" → ngã ngửa + X đỏ.

Cách làm: render sprite Ngộ Không TRONG SUỐT (4 biểu cảm) + hồ lô (item) bằng Bộ Bút,
gậy vẽ thẳng bằng PIL để điều khiển vị trí/xoay tự do; hoạt hoạ bằng PIL; gió = nét cong
phẳng (KHÔNG glow) + hạt bay; âm = gió + "tụp" tổng hợp numpy.

Chạy:  python scripts/hoathinh/but/thu_doat_gay.py
Ra:    du-an/tay-du-ky/output/long/thu-doat-gay.mp4
"""
import math
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ve as V
import phap_bao as PB

W, H = 1280, 720
FPS = 24
DUR = 10.0
NFR = int(DUR * FPS)
GY = 628                       # mặt đất
SKY_TOP = (238, 228, 205)      # kem sáng (đấu trường)
SKY_BOT = (230, 214, 178)
GROUND = (206, 190, 150)
GLINE = (150, 132, 96)

OUT = os.path.join(ROOT, 'du-an', 'tay-du-ky', 'output', 'long', 'thu-doat-gay.mp4')
WORK = os.path.join(ROOT, 'build', 'thu-hoathinh', 'doat-gay')
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')


# ───────── helpers ─────────
def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(s, s0, s1):
    """tiến độ mượt trong khoảng giây [s0,s1]."""
    if s1 <= s0:
        return 1.0 if s >= s1 else 0.0
    return smooth((s - s0) / (s1 - s0))


# ───────── render sprite + item (trong suốt) ─────────
def sprite_ngo(bc, mi, h_target=330):
    NV = V.nap('ngo-khong')
    NV.pop('vu_khi', None)          # gỡ gậy mặc định của sprite (tránh 2 gậy)
    NV['mat']['bieu_cam'] = bc
    NV['mat']['mieng'] = mi
    tmp = os.path.join(WORK, f'_ngo_{bc}_{mi}.png')
    V.ve(NV, tmp, canvas=(800, 1000), nen=None)
    im = Image.open(tmp).convert('RGBA')
    im = im.crop(im.getbbox())
    s = h_target / im.height
    im = im.resize((max(1, round(im.width * s)), h_target), Image.LANCZOS)
    return im


def item_holo(h_target=300):
    b = PB._card(nen=None, scale=2.0)
    PB.ho_lo(b)
    b.chot_vien()
    tmp = os.path.join(WORK, '_holo.png')
    b.luu(tmp)
    im = Image.open(tmp).convert('RGBA')
    im = im.crop(im.getbbox())
    s = h_target / im.height
    return im.resize((max(1, round(im.width * s)), h_target), Image.LANCZOS)


def make_gay(L=250):
    """Gậy Như Ý nằm ngang: thân đỏ + 2 đầu bịt vàng + vạch đen. RGBA, gậy chạy theo trục x."""
    wn = 20
    pad = 8
    im = Image.new('RGBA', (L + pad * 2, wn + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y0, y1 = pad, pad + wn
    # viền đen ngoài
    d.rounded_rectangle([pad - 2, y0 - 2, pad + L + 2, y1 + 2], radius=wn // 2 + 2, fill=(30, 26, 24, 255))
    # thân đỏ
    d.rounded_rectangle([pad, y0, pad + L, y1], radius=wn // 2, fill=(192, 69, 60, 255))
    # vệt sáng trên
    d.rounded_rectangle([pad + 10, y0 + 3, pad + L - 10, y0 + 7], radius=2, fill=(220, 120, 110, 180))
    # 2 đầu bịt vàng + vạch đen
    for ex in (pad, pad + L - 34):
        d.rounded_rectangle([ex, y0 - 1, ex + 34, y1 + 1], radius=wn // 2, fill=(240, 194, 58, 255))
        d.line([ex + 17, y0, ex + 17, y1], fill=(40, 34, 20, 255), width=3)
    return im


# ───────── nền ─────────
def make_bg():
    bg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    for y in range(GY):
        t = y / GY
        c = tuple(round(lerp(SKY_TOP[i], SKY_BOT[i], t)) for i in range(3))
        d.line([0, y, W, y], fill=c + (255,))
    d.rectangle([0, GY, W, H], fill=GROUND + (255,))
    d.line([0, GY, W, GY], fill=GLINE, width=5)
    for gx in range(60, W, 150):
        d.line([gx, GY, gx - 7, GY - 15], fill=(120, 150, 90, 255), width=3)
        d.line([gx + 7, GY, gx + 7, GY - 12], fill=(120, 150, 90, 255), width=3)
    return bg


def rot(im, ang):
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


def paste_feet(bg, spr, cx, feet_y, ang=0.0):
    s = rot(spr, ang) if ang else spr
    bg.alpha_composite(s, (int(cx - s.width / 2), int(feet_y - s.height)))


def shadow(bg, cx, w, a=90):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - w, GY - 12, cx + w, GY + 12], fill=(40, 35, 25, a))
    bg.alpha_composite(sh)


# ───────── gió + hạt ─────────
def wind(bg, src_x, src_y, dst_x, dst_y, inten, phase):
    """Nét gió cong phẳng chảy về miệng hồ lô + hạt bay. inten∈[0,1]."""
    if inten <= 0.01:
        return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    n = 7
    for i in range(n):
        off = (i / n + phase) % 1.0
        fy = (i - n / 2) / n
        pts = []
        for k in range(13):
            u = k / 12
            x = lerp(src_x, dst_x, u)
            amp = (1 - u) * 60 * fy + 26 * math.sin((u * 3 + off * 6.28) * 1.2)
            y = lerp(src_y, dst_y, u) + amp * (0.4 + 0.6 * u)
            pts.append((x, y))
        a = int(150 * inten * (0.4 + 0.6 * (off)))
        d.line(pts, fill=(255, 255, 255, a), width=max(2, int(4 * inten)))
    # hạt bụi/lá bay vào
    rng = np.random.default_rng(7)
    for i in range(16):
        base = rng.random()
        u = (base + phase * 1.3 + i * 0.06) % 1.0
        x = lerp(src_x - 40, dst_x, u) + rng.uniform(-30, 30)
        y = lerp(src_y + rng.uniform(-70, 70), dst_y, u)
        r = lerp(5, 1, u) * (0.6 + inten)
        col = (150, 120, 70) if i % 3 else (120, 150, 90)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(170 * inten),))
    bg.alpha_composite(lay)


def draw_hand(bg, cx, cy, a=255, r=19):
    """MỘT bàn tay tròn (da khỉ) đè lên cán gậy, có ngón cái gợi đang nắm. a = độ mờ."""
    if a <= 2:
        return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    da = (247, 213, 194)
    vien = (120, 78, 58)
    sh = (214, 176, 150)
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=vien + (a,))   # viền ngoài
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=da + (a,))                     # lòng tay
    d.ellipse([cx - r * 0.3, cy + r * 0.1, cx + r, cy + r], fill=sh + (int(a * 0.6),))  # bóng dưới-phải
    # ngón cái cong (nét nắm)
    d.arc([cx - r * 0.5, cy - r * 1.0, cx + r * 0.9, cy + r * 0.2], 200, 350, fill=vien + (a,), width=4)
    bg.alpha_composite(lay)


def holo_mouth(bg, cx, cy, glow):
    """Miệng hồ lô mở sáng (flat), pulse theo glow∈[0,1]."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = 20 + 14 * glow
    d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=(250, 232, 150, int(200 * (0.5 + 0.5 * glow))))
    d.ellipse([cx - r * 0.5, cy - r * 0.3, cx + r * 0.5, cy + r * 0.3], fill=(255, 250, 220, 255))
    bg.alpha_composite(lay)


# ───────── âm thanh ─────────
def build_audio(path):
    sr = 44100
    n = int(DUR * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    rng = np.random.default_rng(3)
    noise = rng.standard_normal(n)
    # lowpass đơn giản (gió)
    k = 90
    ker = np.ones(k) / k
    wind_n = np.convolve(noise, ker, mode='same')
    # envelope gió theo phase: lên ở B/C, dịu ở D, bùng ở E, tắt F
    env = np.interp(t, [0, 1.3, 3.6, 5.2, 6.8, 7.9, 8.4, 10.0],
                    [0.0, 0.25, 0.55, 0.35, 0.22, 0.9, 0.7, 0.0])
    out += wind_n * env * 0.5
    # "tụp" khi gậy vào (≈8.4s): pop trầm
    tp = 8.42
    i0 = int(tp * sr)
    dur = int(0.22 * sr)
    tt = np.arange(dur) / sr
    pop = np.sin(2 * np.pi * np.linspace(220, 70, dur) * tt) * np.exp(-tt * 22) * 0.6
    out[i0:i0 + dur] += pop
    # "ting" hy vọng (≈5.6s)
    tg = 5.6
    i1 = int(tg * sr)
    d2 = int(0.5 * sr)
    t2 = np.arange(d2) / sr
    ting = (np.sin(2 * np.pi * 880 * t2) + 0.5 * np.sin(2 * np.pi * 1320 * t2)) * np.exp(-t2 * 6) * 0.18
    out[i1:i1 + d2] += ting
    out = np.clip(out, -1, 1)
    pcm = (out * 32767).astype('<i2')
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ───────── frame ─────────
def render():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bg0 = make_bg()
    S_brace = sprite_ngo('quyet', 'mim')
    S_strain = sprite_ngo('quyet', 'o')
    S_hope = sprite_ngo('vui', 'cuoi_mo')
    S_shock = sprite_ngo('ngac', 'o')
    holo = item_holo(300)
    gay = make_gay(250)

    holo_cx, holo_feet = 1040, GY
    holo_top = holo_feet - holo.height
    mouth_x, mouth_y = holo_cx, holo_top + 34

    ft = ImageFont.truetype(FONT, 34)
    ftb = ImageFont.truetype(FONT, 60)
    fts = ImageFont.truetype(FONT, 26)

    for f in range(NFR):
        s = f / FPS
        bg = bg0.copy()

        # hồ lô (bob nhẹ)
        bob = math.sin(s * 2.2) * 4
        shadow(bg, holo_cx, 120, 80)
        bg.alpha_composite(holo, (int(holo_cx - holo.width / 2), int(holo_top + bob)))
        glow = seg(s, 0.4, 1.3) * (0.4 + 0.6 * (0.5 + 0.5 * math.sin(s * 5)))
        glow = max(glow, seg(s, 6.8, 7.9))      # bùng lúc E
        holo_mouth(bg, mouth_x, mouth_y + bob, min(1, glow))

        # tiến độ các pha
        pull = (seg(s, 1.3, 3.6) * 0.5 + seg(s, 3.6, 5.2) * 0.5)          # kéo phải
        recover = seg(s, 5.2, 6.6)                                        # kéo lại
        lose = seg(s, 6.8, 7.9)                                           # mất đà, lurch
        fall = seg(s, 7.9, 10.0)                                          # ngã ngửa
        wind_i = max(seg(s, 1.0, 2.2) * 0.55,
                     0.55 + 0.15 * math.sin(s * 4)) * (1 - seg(s, 8.4, 9.2))
        if s < 1.0:
            wind_i = seg(s, 0.5, 1.0) * 0.3
        if 6.8 <= s < 8.4:
            wind_i = max(wind_i, lerp(0.6, 1.0, seg(s, 6.8, 7.8)))

        # Ngộ Không x: base→kéo phải→kéo lại→lurch→ngã lùi trái
        ngo_x = 360 + 170 * pull - 70 * recover + 40 * lose - 150 * fall
        feet = GY                                         # bám đất khi gồng (không nhảy)
        # nghiêng: gồng ngả sau (+), lurch trước (−), ngã ngửa mạnh (−)
        lean = 13 * (pull - 0.4 * recover) - 8 * lose - 72 * fall
        feet_fall = feet + 30 * fall

        # chọn biểu cảm
        if fall > 0.05 or lose > 0.3:
            spr = S_shock
        elif recover > 0.35 and lose < 0.05:
            spr = S_hope
        elif pull > 0.45:
            spr = S_strain
        elif s > 0.8:
            spr = S_brace
        else:
            spr = S_brace

        # rung khi gồng
        jx = (1 - fall) * (0.6 + pull) * math.sin(s * 40) * 2.2
        shadow(bg, ngo_x, 90 + 20 * fall, 90)

        # GẬY: bám tay khi còn giữ; tuột bay vào hồ lô khi lose/fall
        hand_x = ngo_x + 22 + jx          # gậy mọc ra từ tay (trước thân)
        hand_y = feet - 150
        detach = seg(s, 7.4, 8.4)      # 0→1: gậy rời tay bay vào miệng hồ lô
        gx = lerp(hand_x, mouth_x, smooth(detach))
        gyy = lerp(hand_y, mouth_y + bob, smooth(detach))
        gscale = lerp(1.0, 0.16, detach)
        gang = lerp(0 + 10 * pull, -35, detach)     # hơi chếch khi bị kéo
        if s < 8.42:                                 # sau "tụp" thì gậy biến mất
            g = gay.resize((max(1, int(gay.width * gscale)), max(1, int(gay.height * gscale))), Image.LANCZOS)
            g = rot(g, gang)
            bg.alpha_composite(g, (int(gx - g.width * 0.06), int(gyy - g.height / 2)))
        # bàn tay nắm cán (đè lên gậy, mờ dần khi tuột tay)
        if fall < 0.1:
            hand_a = int(255 * (1 - smooth(max(0.0, (detach - 0.15) / 0.5))))
            draw_hand(bg, hand_x, hand_y, hand_a)

        # Ngộ Không
        paste_feet(bg, spr, ngo_x + jx, feet_fall, ang=lean)

        # gió (vẽ ĐÈ nhẹ phía trước để thấy luồng hút)
        wind(bg, hand_x, hand_y, mouth_x, mouth_y + bob, wind_i * (1 - seg(s, 9.0, 9.6)), s * 0.9)

        d = ImageDraw.Draw(bg)
        # tiêu đề trận (trên)
        d.rounded_rectangle([W / 2 - 300, 24, W / 2 + 300, 78], radius=16, fill=(60, 44, 32, 230))
        d.text((W / 2, 51), 'TỨ KẾT · Gậy Như Ý  🆚  Hồ Lô Tử Kim', font=ft, fill=(245, 235, 210), anchor='mm')

        # kết quả cuối: X đỏ + HỒ LÔ THẮNG
        if s > 8.6:
            a = int(255 * seg(s, 8.6, 9.3))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            dl = ImageDraw.Draw(lay)
            # X đỏ trên vị trí Ngộ Không
            cx, cy, r = 360, 300, 70
            dl.line([cx - r, cy - r, cx + r, cy + r], fill=(206, 50, 40, a), width=14)
            dl.line([cx - r, cy + r, cx + r, cy - r], fill=(206, 50, 40, a), width=14)
            dl.text((360, 400), 'GẬY BỊ LOẠI', font=fts, fill=(206, 50, 40, a), anchor='mm')
            if s > 9.0:
                a2 = int(255 * seg(s, 9.0, 9.6))
                dl.text((holo_cx, holo_top - 30), 'HỒ LÔ THẮNG!', font=ftb, fill=(224, 160, 44, a2), anchor='mm')
            bg.alpha_composite(lay)

        bg.convert('RGB').save(os.path.join(WORK, 'f_%04d.png' % f))

    # âm
    wav = os.path.join(WORK, 'a.wav')
    build_audio(wav)

    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    silent = os.path.join(WORK, 'silent.mp4')
    subprocess.run([ff, '-y', '-framerate', str(FPS), '-i', os.path.join(WORK, 'f_%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', silent],
                   check=True, capture_output=True)
    subprocess.run([ff, '-y', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac',
                    '-b:a', '160k', '-shortest', OUT], check=True, capture_output=True)
    print('XONG:', OUT)


if __name__ == '__main__':
    render()
