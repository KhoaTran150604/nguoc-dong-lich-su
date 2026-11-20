"""CẢNH THỬ – nối 4 động tác nền thành một cảnh liên tục + xuất MP4.

Kịch bản (Ngộ Không): CHẠY VÀO (từ trái) → DỪNG, ĐỨNG THỞ → NÓI (khẩu hình) → NGẠC NHIÊN → CƯỜI.
Dùng lại: luot_toi.scene (nền cuộn), chay_toi.speed_lines (vệt tốc độ),
          dung_tho_noi.render_states/than_day/TALK (mặt + miệng + chạm đất).
Nền cuộn khi chạy, DỪNG LẠI khi đứng (giảm tốc mượt).

Chạy:  python scripts/hoathinh/but/canh_thu.py [--ma ngo-khong]
Ra:    build/thu-hoathinh/but-canh/khung_000.png ... + canh-thu.mp4
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
from PIL import Image, ImageDraw
import luot_toi as L
import chay_toi as C
import dung_tho_noi as D

W, H, GY, CX = L.W, L.H, L.GY, L.CX
FPS = 24                       # 24 fps cho mượt (12 bị giật). Thời lượng giữ nguyên nhờ nhân số khung.
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'but-canh')

# đoạn (tên, số khung) – tính theo FPS để giữ NGUYÊN thời lượng giây
_SEC = [('run', 1.5), ('settle', 0.83), ('stand', 0.67), ('talk', 1.33), ('ngac', 0.5), ('vui', 0.67)]
SEG = [(nm, max(2, round(s * FPS))) for nm, s in _SEC]


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ground_bottom(s):
    al = np.array(s.split()[-1])
    rong = (al > 10).sum(axis=1)
    hang = np.where(rong >= 44)[0]
    return int(hang.max()) if len(hang) else s.height


def plan(seg=SEG):
    """trả list mỗi khung: (tên đoạn, chỉ số trong đoạn k, số khung đoạn n)."""
    out = []
    for name, n in seg:
        for k in range(n):
            out.append((name, k, n))
    return out


def render(ma, states=None, talk_keys=None):
    """talk_keys: list state-key miệng cho đoạn NÓI (độ dài = số khung nói). None = nhịp mặc định."""
    if states is None:
        states = D.render_states(ma)
    seg = [(nm, len(talk_keys) if (nm == 'talk' and talk_keys) else n) for nm, n in SEG]
    seq = plan(seg)
    total = len(seq)
    frames = []

    d = 0.0            # quãng cuộn nền tích luỹ
    DPF = 288.0 / FPS  # nền cuộn/khung khi chạy (giữ px/giây cố định theo fps)
    for gi, (seg, k, n) in enumerate(seq):
        t = k / max(1, n - 1)
        # tốc độ cuộn nền theo đoạn
        if seg == 'run':
            spd = DPF
        elif seg == 'settle':
            spd = DPF * (1 - smooth(t))     # giảm tốc về 0
        else:
            spd = 0.0
        d += spd

        bg = L.scene(d / L.FAR)             # tái dùng nền cuộn, truyền quãng đã cuộn

        # vệt tốc độ khi chạy (mờ dần ở settle)
        if seg in ('run', 'settle'):
            C.speed_lines(bg, gi, CX)

        # tư thế + mặt theo đoạn
        lean = 0.0
        breath = seg in ('stand', 'talk', 'ngac', 'vui')
        if seg == 'run':
            lean = 12.0
            xpos = -140 + (CX + 140) * smooth(t)
            key = 'calm'
        elif seg == 'settle':
            lean = 12.0 * (1 - smooth(t))
            xpos = CX
            key = 'calm'
        elif seg == 'stand':
            xpos = CX; key = 'calm'
        elif seg == 'talk':
            xpos = CX
            key = talk_keys[k] if talk_keys else D.TALK[int(t * (len(D.TALK) - 1) * 2) % len(D.TALK)]
        elif seg == 'ngac':
            xpos = CX; key = 'ngac'
        else:
            xpos = CX; key = 'vui'

        sp = states[key]
        if breath:
            b = math.sin(2 * math.pi * gi / (FPS * 1.4))
            sp = sp.resize((max(1, round(sp.width * (1 - 0.006 * b))),
                            max(1, round(sp.height * (1 + 0.012 * b)))), Image.LANCZOS)
        s = sp.rotate(-lean, expand=True, resample=Image.BICUBIC) if lean else sp

        # bóng + đặt chạm đất
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([int(xpos) - 74, GY - 6, int(xpos) + 74, GY + 13], fill=(40, 35, 25, 85))
        bg.alpha_composite(sh)
        bb = s.getbbox()
        cxp = (bb[0] + bb[2]) / 2
        px = int(xpos + lean * 0.5 - cxp)
        py = int(GY + 4 - ground_bottom(s))
        bg.alpha_composite(s, (px, py))

        # nhãn + phụ đề
        lab = {'run': 'Chạy vào', 'settle': 'Dừng lại', 'stand': 'Đứng · thở',
               'talk': 'Nói', 'ngac': 'Ngạc nhiên!', 'vui': 'Cười'}[seg]
        D.label(bg, lab)
        if seg == 'talk':
            sub(bg, 'Ta là Tôn Ngộ Không!')

        frames.append(bg.convert('RGB'))
        print(f'\r khung {gi+1}/{total} [{seg}]', end='')
    print()
    return frames


def sub(bg, text):
    d = ImageDraw.Draw(bg, 'RGBA')
    tw = d.textlength(text, font=D.FONT)
    x0 = (W - tw) / 2 - 18
    d.rounded_rectangle([x0, H - 60, x0 + tw + 36, H - 18], radius=11, fill=(0, 0, 0, 170))
    d.text(((W - tw) / 2, H - 54), text, font=D.FONT, fill=(255, 255, 255))


def to_mp4(n, ra):
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ff = 'ffmpeg'
    cmd = [ff, '-y', '-framerate', str(FPS), '-i', os.path.join(OUT, 'khung_%03d.png'),
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', ra]
    subprocess.run(cmd, check=True, capture_output=True)
    return ra


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--ma', default='ngo-khong')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    L.FAR, L.NEAR = 22.0, 9.0
    frames = render(a.ma)
    for i, f in enumerate(frames):
        f.save(os.path.join(OUT, f'khung_{i:03d}.png'))
    mp4 = to_mp4(len(frames), os.path.join(OUT, 'canh-thu.mp4'))
    L.contact_sheet(frames[::4], os.path.join(OUT, 'contact-sheet.jpg'))
    print('MP4:', mp4, '| khung:', len(frames))
