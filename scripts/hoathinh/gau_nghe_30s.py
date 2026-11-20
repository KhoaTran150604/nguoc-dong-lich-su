"""Video thử ~30s: Gâu Nghệ ở quán cà phê hóng chuyện Bạch Đằng (lối vẽ sitcom VN – docs/plan/hoc-phong-cach-sitcom-vn.md).
Giọng: build/thu-hoathinh/gau-nghe-30s/thoai.wav + thoai.json (tạo bằng thoai_song_tu.py từ loi.json, giọng Gia Huy).
Dữ kiện sử chỉ F17, F19 trong kb/E2-bach-dang-938.md.
Cảnh: A toàn cảnh quán vỉa hè → B trung cảnh sau quầy (nghiêng khung) → C cận mặt giật mình → B → A vẫy chào.
Chạy: python scripts/hoathinh/gau_nghe_30s.py [--khung 1.0 8.5 ...]
Ra:   build/thu-hoathinh/gau-nghe-30s/gau-nghe-30s.mp4
"""
import argparse
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
from ngo_quyen_can_canh import SS, INK, hx  # noqa: E402
from gau_nghe_van import Dog, ROOT  # noqa: E402
import gau_nghe_khung_thu as K  # noqa: E402

DIR = os.path.join(ROOT, 'build', 'thu-hoathinh', 'gau-nghe-30s')
FPS = 30
OW, OH = 1280, 720
PAUSE = [0.6, 0.6, 1.2, 0.8, 0.8]   # nghỉ thêm TRƯỚC mỗi câu (nhịp hài: mở cảnh, hút cà phê, giật mình…)
TAIL = 2.6


def load_voice():
    """Chèn khoảng lặng trước mỗi câu → kéo video ~30s; tính lại mốc câu + biên độ khẩu hình."""
    d = json.load(open(os.path.join(DIR, 'thoai.json'), encoding='utf-8'))
    v, sr = sf.read(os.path.join(DIR, 'thoai.wav'), dtype='float32')
    parts, prev, shift = [], 0, 0.0
    for ln, ps in zip(d['lines'], PAUSE):
        cut = int((ln['start'] - 0.05) * sr)
        parts += [v[prev:cut], np.zeros(int(ps * sr), np.float32)]
        prev = cut
        shift += ps
        ln['start'] = round(ln['start'] + shift, 3)
        ln['end'] = round(ln['end'] + shift, 3)
    parts.append(v[prev:])
    v2 = np.concatenate(parts)
    dur = d['lines'][-1]['end'] + TAIL
    v2 = np.concatenate([v2, np.zeros(max(0, int(dur * sr) - v2.size), np.float32)])[:int(dur * sr)]
    hop = sr // 30
    env = [float(np.sqrt(np.mean(v2[k:k + hop] ** 2))) for k in range(0, v2.size, hop)]
    mx = max(env) or 1
    return d['lines'], [e / mx for e in env], v2, sr, dur


L, ENV, VOICE, SR, DUR = load_voice()
DUR = round(DUR, 2)
CUTS = [0.0, L[1]['start'] - 0.5, L[2]['start'] - 1.0, L[3]['start'] - 0.5, L[4]['start'] - 0.5, DUR + 1]
SHOTS = ['A', 'B', 'C', 'B', 'A']
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')
FONT_B = os.path.join(ROOT, 'fonts', 'BeVietnamPro-Bold.ttf') if os.path.exists(
    os.path.join(ROOT, 'fonts', 'BeVietnamPro-Bold.ttf')) else FONT


def shot_at(t):
    for i in range(5):
        if CUTS[i] <= t < CUTS[i + 1]:
            return i, t - CUTS[i]
    return 4, t - CUTS[4]


def env_at(t):
    k = int(t * 30)
    if 0 <= k < len(ENV):
        return ENV[k]
    return 0.0


def talking(t):
    for ln in L:
        if ln['start'] <= t <= ln['end']:
            return True
    return False


def mouth_amt(t):
    if not talking(t):
        return 0.0
    e = max(env_at(t), 0.6 * env_at(t - 1 / 30))
    return min(1.0, e * 1.6)


def blink(t):
    ph = (t + 0.7) % 3.1
    return ph < 0.12


# ------------------------------------------------------------------ lớp nền dựng sẵn (mỗi tiến trình 1 lần)
BG = {}


def build():
    if BG:
        return
    BG['A'] = K.frame_a(dogfn=lambda cv: None)
    BG['B'] = K.b_back()
    fb = Image.new('RGBA', BG['B'].size, (0, 0, 0, 0))
    BG['Bf'] = K.b_front(fb)
    BG['C'] = K.c_back()
    fc = Image.new('RGBA', BG['C'].size, (0, 0, 0, 0))
    BG['Cf'] = K.c_front(fc)


def cam(cv, z, cx, cy, shake=0.0, t=0.0):
    """Cắt khung theo zoom z quanh tâm (cx, cy) – toạ độ 1600x900 – rồi thu về OW x OH."""
    w, h = K.W / z, K.H / z
    cx += shake * math.sin(t * 91)
    cy += shake * math.cos(t * 77)
    x0 = min(max(cx - w / 2, 0), K.W - w)
    y0 = min(max(cy - h / 2, 0), K.H - h)
    return cv.crop((int(x0 * SS), int(y0 * SS), int((x0 + w) * SS), int((y0 + h) * SS))).resize((OW, OH), Image.LANCZOS)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def render(t):
    build()
    i, lt = shot_at(t)
    kind = SHOTS[i]
    mo = mouth_amt(t)
    lid_blink = blink(t)
    bob = math.sin(t * 2 * math.pi * 0.6)
    if kind == 'A':
        cv = BG['A'].copy()
        if i == 0:      # mở đầu: nhìn vào máy quay, cầm ly, nói
            st = dict(cup=True, sip=not talking(t), mouth='talk', mo=mo, rest='smile', gaze=(0, 0), flat=True)
            z = 1.0 + 0.10 * ease(lt / (CUTS[1] - CUTS[0]))
            cx, cy = 800 + 160 * ease(lt / 6), 470 + 60 * ease(lt / 6)
        else:           # kết: vẫy tay, "Gâu!"
            end = L[4]['end']
            wave = math.sin(lt * 2 * math.pi * 2.2)
            st = dict(arms=((18, 8), (112, 150 + 18 * wave)), mouth='talk', mo=mo, rest='smile', gaze=(0, 0), flat=True)
            if t > end - 0.5:
                st.update(mouth='tongue', eyes='happy')
            z = 1.25 - 0.15 * ease(lt / 2.5)
            cx, cy = 1000, 600
        if lid_blink and st.get('eyes') != 'happy':
            st['lid'] = (1.0, 1.0)
        Dog(cv, 1090, 828 + 1.5 * bob, 0.62, st).draw()
        return cam(cv, z, cx, cy)
    if kind == 'B':
        cv = BG['B'].copy()
        smug = i == 3
        st = dict(cup=True, sip=not talking(t), mouth='talk', mo=mo, rest='smirk', flat=True,
                  lid=(0.42, 0.42) if not smug else (0.5, 0.5), gaze=(-1, 0) if not smug else (0, 1), brow=(8, 0))
        if lid_blink:
            st['lid'] = (1.0, 1.0)
        Dog(cv, 860 + 6 * math.sin(t * 1.3), 1000 + 4 * bob, 1.75, st).draw()
        cv.alpha_composite(BG['Bf'])
        cv = K.b_rotate(cv, 6 if i == 1 else -5)
        z = 1.0 + 0.06 * ease(lt / 4)
        return cam(cv, z, 800, 450)
    # C: cận mặt giật mình
    cv = BG['C'].copy()
    shock = lt < 0.9
    st = dict(mouth='open' if shock else 'talk', mo=mo, rest='open', big=1.3 if shock else 1.15, gaze=(-1, 0),
              brow=(18 if shock else 10, 0), flat=True)
    if lid_blink and not shock:
        st['lid'] = (1.0, 1.0)
    jump = -26 * math.exp(-lt * 6) * math.cos(lt * 30) if lt < 0.8 else 0
    Dog(cv, 860, 1250 + jump + 3 * bob, 2.45, st).draw()
    K.c_shock(cv, dy=min(60, lt * 40))
    cv.alpha_composite(BG['Cf'])
    z = 1.12 - 0.12 * ease(lt / 0.35)
    im = cam(cv, z, 800, 450, shake=10 * math.exp(-lt * 5), t=t)
    # thẻ "Sử cũ chép" bật lên khi nói F17
    t_card = L[2]['start'] + 1.0
    if t > t_card:
        card(im, ease((t - t_card) / 0.25))
    return im


def card(im, k):
    if k <= 0:
        return
    w, h = int(520 * k), int(150 * k)
    lay = Image.new('RGBA', (560, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([8, 8, 548, 178], 18, fill=hx('#F4EFE4') + (255,), outline=INK + (255,), width=5)
    d.rounded_rectangle([8, 8, 548, 58], 18, fill=hx('#B3261E') + (255,), outline=INK + (255,), width=5)
    d.text((278, 34), 'SỬ CŨ CHÉP', font=ImageFont.truetype(FONT_B, 30), fill=hx('#F4EFE4'), anchor='mm')
    d.text((278, 102), 'Cọc lớn · vót nhọn · bịt sắt', font=ImageFont.truetype(FONT, 32), fill=INK, anchor='mm')
    d.text((278, 148), 'cắm ở cửa biển (938)', font=ImageFont.truetype(FONT, 26), fill=hx('#5A4A40'), anchor='mm')
    lay = lay.resize((max(1, w), max(1, h)), Image.LANCZOS).rotate(-3, expand=True, resample=Image.BICUBIC)
    im.paste(lay, (int(1000 - lay.width / 2), int(110 - lay.height / 2)), lay)


# ------------------------------------------------------------------ âm thanh
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
    v, sr = VOICE, SR
    n = int(DUR * sr)
    out = np.zeros(n, np.float32)
    out[:min(n, v.size)] += v[:n]
    rng = np.random.default_rng(3)

    def add(buf, at, sig, g=1.0):
        s0 = int(at * sr)
        m = min(n - s0, sig.size)
        if m > 0 and s0 >= 0:
            buf[s0:s0 + m] += sig[:m] * g

    # nhạc nền: ngũ cung, 110 bpm, pluck + bass + tiếng "chụp" nhẹ; tắt ở cú giật mình rồi vào lại
    music = np.zeros(n, np.float32)
    beat = 60 / 110
    scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25]
    mel = [0, 2, 4, 5, 4, 2, 3, 1, 0, 2, 4, 2, 3, 4, 1, 0]
    bass = [130.81, 98.0, 110.0, 87.31]
    stop0, stop1 = CUTS[2], CUTS[2] + 1.0
    for k in range(int(DUR / beat) + 1):
        at = k * beat
        if stop0 <= at < stop1:
            continue
        if k % 2 == 0:
            add(music, at, tone(bass[(k // 4) % 4], 0.5, sr, 'sin', 5), 0.22)
        add(music, at, tone(scale[mel[k % 16]] * 2, 0.35, sr, 'pluck', 9), 0.08)
        tk = np.arange(int(0.05 * sr)) / sr
        add(music, at + beat / 2, (rng.normal(0, 1, tk.size) * np.exp(-tk * 90)).astype(np.float32), 0.03)
    hop = sr // 30
    envv = np.repeat(np.array(ENV + [0] * (int(DUR * 30) + 2 - len(ENV)), np.float32), hop)[:n]
    duck = 1 - 0.55 * np.clip(np.convolve(envv, np.ones(hop * 6) / (hop * 6), 'same') * 3, 0, 1)
    out += music * duck
    # tiếng phố nhẹ ở cảnh A (ồn nền lọc thấp)
    amb = np.convolve(rng.normal(0, 1, n), np.ones(80) / 80, 'same').astype(np.float32) * 0.05
    mask = np.zeros(n, np.float32)
    mask[:int(CUTS[1] * sr)] = 1
    mask[int(CUTS[4] * sr):] = 1
    out += amb * np.convolve(mask, np.ones(sr // 4) / (sr // 4), 'same')
    # tiếng động
    tw = np.arange(int(0.3 * sr)) / sr
    whoosh = np.convolve(rng.normal(0, 1, tw.size), np.ones(30) / 30, 'same').astype(np.float32) * np.sin(np.pi * tw / 0.3) ** 2
    for c in CUTS[1:5]:
        add(out, c - 0.1, whoosh, 0.2)
    add(out, CUTS[2], tone(90, 0.4, sr, 'sin', 8), 0.45)             # "bụp" giật mình
    tr = np.arange(int(0.2 * sr)) / sr
    add(out, CUTS[2] - 0.02, (rng.normal(0, 1, tr.size) * np.exp(-tr * 20)).astype(np.float32), 0.2)
    add(out, CUTS[2] + 0.3, tone(2600, 0.25, sr, 'sin', 14), 0.07)    # "tinh" mồ hôi
    tt = np.arange(int(0.12 * sr)) / sr
    blip = (np.sin(2 * np.pi * (700 + 900 * tt / 0.12) * tt) * np.exp(-tt * 30)).astype(np.float32)
    add(out, L[2]['start'] + 1.0, blip, 0.18)                          # thẻ bật
    for k, f in enumerate((523.25, 659.25, 783.99, 1046.5)):         # nhạc chốt cuối
        add(out, L[4]['end'] + 0.15 + k * 0.12, tone(f, 0.6, sr, 'pluck', 5), 0.1)
    out = out / max(1e-6, np.abs(out).max()) * 0.92
    p = os.path.join(DIR, 'tieng-tron.wav')
    sf.write(p, out, sr)
    return p


# ------------------------------------------------------------------ chạy
G = {}


def init_pool(d):
    build()
    G['dir'] = d


def job(i):
    render(i / FPS).convert('RGB').save(os.path.join(G['dir'], 'f%04d.jpg' % i), quality=92)
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
    if a.khung:
        ims = []
        for t in a.khung:
            ims.append(render(t).convert('RGB'))
        cols = 3
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 640, rows * 360), (0, 0, 0))
        for k, im in enumerate(ims):
            sheet.paste(im.resize((640, 360)), ((k % cols) * 640, (k // cols) * 360))
        p = os.path.join(DIR, 'bang-khung.jpg')
        sheet.save(p, quality=88)
        print(p)
        return
    fdir = tempfile.mkdtemp(prefix='gaunghe30-')
    n = int(DUR * FPS)
    print('Thời lượng %.2fs, %d khung' % (DUR, n), flush=True)
    with Pool(max(1, (os.cpu_count() or 4) - 2), initializer=init_pool, initargs=(fdir,)) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(n))):
            if k % 60 == 0:
                print('  khung %d/%d' % (k, n), flush=True)
    wav = make_audio()
    out = os.path.join(DIR, 'gau-nghe-30s.mp4')
    subprocess.run([ffmpeg(), '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(fdir, 'f%04d.jpg'),
                    '-i', wav, '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', out], check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print('xong:', out)


if __name__ == '__main__':
    main()
