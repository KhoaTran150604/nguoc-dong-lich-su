"""Thử CHUYỂN ĐỘNG chậm, mượt (60 khung/giây) – cảnh kiểu 1: cầu bổng 'ngon ăn' → Khang nhún, bật nhảy, đập HỤT
→ cầu rơi sau lưng → Khang đơ, từ từ quay lại nhìn → Gâu thở dài, che mặt.

Nguyên tắc (góp ý 19/11): mỗi động tác 0.5–1.5s, có lấy đà (anticipation) + giảm tốc (ease) + giữ hình ở cú chốt.
Chạy:  python scripts/hoathinh/thu_chuyen_dong.py [--khung t ...]
Ra:    build/thu-hoathinh/cau-long-v2/thu-chuyen-dong.mp4
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cau_long_video as V  # noqa: E402  (nền nhà thi đấu, lưới, cầu, máy quay)
from nguoi2 import Human, CAST  # noqa: E402
from gau_nghe_van import Dog  # noqa: E402

OUT = os.path.join(V.ROOT, 'build', 'thu-hoathinh', 'cau-long-v2')
FPS = 60
DUR = 7.0


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def eout(x):          # giảm tốc
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def ein(x):           # tăng tốc
    x = min(1.0, max(0.0, x))
    return x ** 3


def seg(t, a, b):
    return (t - a) / (b - a)


def lerp(a, b, k):
    return a + (b - a) * k


def lerp2(p, q, k):
    return (lerp(p[0], q[0], k), lerp(p[1], q[1], k))


# ------------------------------------------------------------------ dòng thời gian (giây)
T_LOB0, T_LOB1 = 0.2, 2.35        # cầu bay bổng (Tùng → trên đầu Khang): chậm, đỉnh lơ lửng
T_CR0, T_CR1 = 1.25, 1.75         # Khang nhún lấy đà
T_JU0, T_JU1 = 1.75, 2.15         # bật lên
T_SW0, T_SW1 = 2.12, 2.42         # vung vợt (nhanh nhưng 18 khung)
T_LAND = 2.75                     # chạm đất
T_PICH = 3.05                     # cầu rơi "pịch" sau lưng
T_TURN0, T_TURN1 = 3.6, 4.4       # quay đầu nhìn cầu
T_CUT = 4.9                       # cắt sang Gâu
KX, KY = 1080, 840                # chỗ Khang đứng
TX = 360                          # Tùng
SHUT_LAND = (1235, 842)


def shuttle_pos(t):
    """Quỹ đạo cầu: bổng cao, đỉnh chậm (cầu lông giảm tốc nhanh), rơi gần thẳng đứng sau lưng Khang."""
    p0, peak, end = (TX + 70, 520), (900, 170), SHUT_LAND
    if t < T_LOB0:
        return p0, 160
    if t < T_LOB1:                          # đi lên + trôi ngang chậm dần tới đỉnh
        k = eout(seg(t, T_LOB0, T_LOB1))
        x = lerp(p0[0], peak[0] + 230, k)
        y = p0[1] - (p0[1] - peak[1]) * math.sin(min(1, k * 1.25) * math.pi / 2)
        ang = lerp(150, 200, k)
        return (x, y), ang
    k = ein(seg(t, T_LOB1, T_PICH))         # rơi: tăng tốc nhẹ, gần thẳng đứng
    x = lerp(peak[0] + 230, end[0], k)
    y = lerp(peak[1] + 10, end[1] - 10, k)
    return (x, y), 180 + 10 * (1 - k)


def khang(cv, t):
    st = dict(gaze=(0.5, -1), mouth='grin', eyes='open', hold={'R': 'racket'}, gear=True)
    y = KY
    # tay vợt: chờ (giơ ngang) → kéo ra sau khi nhún → vung qua đầu → kết thúc phía trước-dưới
    ready, back, top, follow = (120, -400), (150, -520), (40, -600), (110, -300)
    if t < T_CR0:
        hand, ang = ready, 30
    elif t < T_JU1:
        k = ease(seg(t, T_CR0, T_JU1))
        hand, ang = lerp2(ready, back, k), lerp(30, -60, k)
    elif t < T_SW1:
        k = ein(seg(t, T_SW0, T_SW1))
        hand = lerp2(back, top, min(1, k * 2)) if k < 0.5 else lerp2(top, follow, (k - 0.5) * 2)
        ang = lerp(-60, 160, k)
    else:
        hand, ang = follow, 160
    st['arm_to'] = {'R': hand, 'L': (-70, -470) if T_CR0 < t < T_LAND else (-80, -300)}   # tay trái chỉ cầu khi nhảy
    st['prop_ang'] = {'R': ang}
    # nhún – nhảy – tiếp đất
    if T_CR0 <= t < T_JU0:
        st['crouch'] = ease(seg(t, T_CR0, T_JU0)) * 0.9
    elif T_JU0 <= t < T_LAND:
        k = seg(t, T_JU0, T_LAND)
        y = KY - 150 * math.sin(math.pi * k) ** 0.8
        st['crouch'] = 0.9 * (1 - ease(k * 4)) if k < 0.25 else 0
    elif T_LAND <= t < T_LAND + 0.3:
        st['crouch'] = 0.6 * (1 - ease(seg(t, T_LAND, T_LAND + 0.3)))
    if t >= T_SW1:                         # hụt → đơ
        st.update(mouth='o', eyes='wide', gaze=(0, 0))
    if t >= T_TURN0:                       # từ từ quay lại nhìn cầu sau lưng
        k = ease(seg(t, T_TURN0, T_TURN1))
        st['gaze'] = (k, 0.6 * k)
        st['sweat'] = t > T_TURN1
        st['mouth'] = 'flat'
    Human(cv, KX, y, 0.5, CAST['khang'], st).draw()


def tung(cv, t):
    k = ease(seg(t, 0.0, 0.35))
    st = dict(hold={'R': 'racket'}, mouth='D' if t < 1.5 else 'smile', eyes='happy' if t < 1.5 else 'open', gaze=(1, -0.6))
    st['arm_to'] = {'R': lerp2((140, -200), (130, -420), k)}
    st['prop_ang'] = {'R': lerp(120, 20, k)}
    Human(cv, TX, 840, 0.5, CAST['tung'], st).draw()


def scene_court(t):
    cv = V.BG['gym'].copy()
    tung(cv, t)
    V.net(cv)
    (sx, sy), ang = shuttle_pos(t)
    if t > T_PICH:                          # nảy nhẹ rồi nằm
        q = t - T_PICH
        b = max(0, 1 - q * 2.5)
        sy = SHUT_LAND[1] - 10 - 22 * b * abs(math.sin(q * 9))
        ang = lerp(180, 100, ease(q * 3))
    if sx > KX:                             # rơi sau lưng: vẽ cầu TRƯỚC Khang
        V.shuttle(cv, sx, sy, ang, 1.1)
        khang(cv, t)
    else:
        khang(cv, t)
        V.shuttle(cv, sx, sy, ang, 1.1)
    # máy quay: theo cầu khi bay, đẩy nhẹ vào Khang khi nhảy, rồi vào mặt Khang lúc đơ
    if t < T_LOB1:
        k = ease(seg(t, 0, T_LOB1))
        z, cx, cy = lerp(1.15, 1.45, k), lerp(760, 960, k), lerp(560, 520, k)
    elif t < T_TURN0:
        k = ease(seg(t, T_LOB1, T_LOB1 + 0.6))
        z, cx, cy = lerp(1.45, 1.5, k), lerp(960, 1080, k), lerp(520, 600, k)
    else:
        k = ease(seg(t, T_TURN0, T_TURN1 + 0.3))
        z, cx, cy = lerp(1.5, 2.6, k), lerp(1080, 1100, k), lerp(600, 680, k)
    return V.cam(cv, z, cx, cy)


def scene_gau(t):
    cv = V.BG['gym'].copy()
    lt = t - T_CUT
    # thở dài (vai hạ) → đưa tay lên che mặt chậm
    k = ease(seg(lt, 0.5, 1.4))
    sigh = 6 * math.sin(min(1, lt / 0.6) * math.pi)
    st = dict(flat=True, mouth='flat', lid=(lerp(0.3, 0.75, ease(lt / 0.6)),) * 2, gaze=(-0.6, 0), brow=(-8, -8),
              arms=((14, 6), (lerp(14, 150, k), lerp(6, 178, k))))
    Dog(cv, 800, 860 + sigh, 0.52, st).draw()
    return V.cam(cv, 2.4, 800, 700)


def render(t):
    V.build()
    return scene_court(t) if t < T_CUT else scene_gau(t)


def init(d):
    global FDIR
    FDIR = d


def job(i):
    render(i / FPS).convert('RGB').save(os.path.join(FDIR, 'f%05d.jpg' % i), quality=92)


def main():
    os.makedirs(OUT, exist_ok=True)
    if '--khung' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--khung') + 1:]]
        ims = [render(t).convert('RGB').resize((480, 270)) for t in ts]
        sh = Image.new('RGB', (4 * 480, ((len(ims) + 3) // 4) * 270))
        d = ImageDraw.Draw(sh)
        for k, im in enumerate(ims):
            sh.paste(im, ((k % 4) * 480, (k // 4) * 270))
            d.text(((k % 4) * 480 + 6, (k // 4) * 270 + 4), '%.2fs' % ts[k], fill=(255, 255, 0))
        p = os.path.join(OUT, 'thu-chuyen-dong-khung.jpg')
        sh.save(p, quality=88)
        print(p)
        return
    fdir = tempfile.mkdtemp(prefix='cd-')
    n = int(DUR * FPS)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n), chunksize=4)):
            if k % 120 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    # âm: vút khi vung, pịch khi cầu rơi, thở dài
    sr = 24000
    au = np.zeros(int(DUR * sr), np.float32)
    rng = np.random.default_rng(3)

    def add(at, sig, g):
        s0 = int(at * sr)
        m = min(au.size - s0, sig.size)
        au[s0:s0 + m] += sig[:m] * g
    tt = np.arange(int(0.3 * sr)) / sr
    add(T_SW0, (np.convolve(rng.normal(0, 1, tt.size), np.ones(25) / 25, 'same') * np.sin(np.pi * tt / 0.3) ** 2).astype(np.float32), 0.5)
    tp = np.arange(int(0.12 * sr)) / sr
    add(T_PICH, (np.sin(2 * np.pi * 320 * tp) * np.exp(-tp * 40)).astype(np.float32), 0.5)
    add(0.2, (np.sin(2 * np.pi * 260 * tp) * np.exp(-tp * 40)).astype(np.float32), 0.35)
    ts_ = np.arange(int(0.9 * sr)) / sr
    add(T_CUT + 0.2, (np.convolve(rng.normal(0, 1, ts_.size), np.ones(60) / 60, 'same') * np.sin(np.pi * ts_ / 0.9)).astype(np.float32), 0.25)
    import soundfile as sf
    wav = os.path.join(fdir, 'a.wav')
    sf.write(wav, au, sr)
    out = os.path.join(OUT, 'thu-chuyen-dong.mp4')
    subprocess.run([V.ffmpeg(), '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, 'f%05d.jpg'), '-i', wav,
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out],
                   check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
