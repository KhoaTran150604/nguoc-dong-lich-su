"""THỬ CHUYỂN ĐỘNG 4 – Ngộ Không ĐỨNG · THỞ · NÓI · BIỂU CẢM (động tác nền của phim hội thoại).

Khác 3 clip di chuyển: phần NÓI và BIỂU CẢM phải RENDER LẠI MẶT (đổi miệng + mắt) bằng engine,
không chỉ biến hình sprite. Cách làm:
  - render sẵn vài TRẠNG THÁI MẶT (miệng mim/cuoi/o/noi/cuoi_mo; biểu cảm hien/ngac/vui) trên cùng khung,
    cắt theo CHUNG một khung để mặt không lệch
  - mỗi khung: chọn trạng thái theo đoạn (đứng → nói → ngạc nhiên → vui) + áp NHỊP THỞ (phình nhẹ)
Nền tĩnh (không cuộn).

Chạy:  python scripts/hoathinh/but/dung_tho_noi.py [--ma ngo-khong] [--khung 30]
Ra:    build/thu-hoathinh/but-noi/khung_00.png ... + contact-sheet.jpg
"""
import argparse
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ve as V
import luot_toi as L

W, H, GY = L.W, L.H, L.GY
N = 30
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'but-noi')
FONT = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 26)

# các trạng thái mặt: (biểu cảm, miệng)
STATES = {
    'calm':  ('hien', 'cuoi'),
    'm_mim': ('hien', 'mim'),
    'm_cuoi':('hien', 'cuoi'),
    'm_o':   ('hien', 'o'),
    'm_noi': ('hien', 'noi'),
    'm_mo':  ('hien', 'cuoi_mo'),
    'ngac':  ('ngac', 'o'),
    'vui':   ('vui',  'cuoi_mo'),
}
TALK = ['m_mim', 'm_o', 'm_noi', 'm_mo', 'm_noi', 'm_o', 'm_cuoi', 'm_o', 'm_noi', 'm_mo', 'm_cuoi']


def render_states(ma, h_target=306):
    """Render mọi trạng thái trên cùng khung, cắt CHUNG một khung → mặt khớp nhau."""
    raw = {}
    for key, (bc, mi) in STATES.items():
        NV = V.nap(ma)
        NV['mat']['bieu_cam'] = bc
        NV['mat']['mieng'] = mi
        tmp = os.path.join(OUT, f'_{key}.png')
        V.ve(NV, tmp, canvas=(800, 1000), nen=None)
        raw[key] = Image.open(tmp).convert('RGBA')
        os.remove(tmp)
    # khung cắt chung = hợp mọi bbox
    L_, T_, R_, B_ = 10**9, 10**9, 0, 0
    for im in raw.values():
        a, b, c, d = im.getbbox()
        L_, T_, R_, B_ = min(L_, a), min(T_, b), max(R_, c), max(B_, d)
    scale = h_target / (B_ - T_)
    out = {}
    for key, im in raw.items():
        c = im.crop((L_, T_, R_, B_))
        out[key] = c.resize((round(c.width * scale), h_target), Image.LANCZOS)
    return out


def than_day(sp):
    """hàng thấp nhất có bề rộng lớn (mép áo) – để chạm đất, bỏ qua đuôi gậy mảnh."""
    al = np.array(sp.split()[-1])
    rong = (al > 10).sum(axis=1)
    hang = np.where(rong >= 44)[0]
    return int(hang.max()) if len(hang) else sp.height


def phase(frame):
    if frame < 9:   return 'calm', 'Đứng · thở'
    if frame < 20:  return TALK[(frame - 9) % len(TALK)], 'Đang nói…'
    if frame < 25:  return 'ngac', 'Ngạc nhiên!'
    return 'vui', 'Cười vui'


def label(bg, text):
    d = ImageDraw.Draw(bg, 'RGBA')
    tw = d.textlength(text, font=FONT)
    d.rounded_rectangle([18, 16, 18 + tw + 28, 58], radius=10, fill=(186, 65, 57, 235))
    d.text((32, 22), text, font=FONT, fill=(255, 255, 255))


def khung_anh(states, frame):
    bg = L.scene(0)                                    # nền tĩnh
    key, lab = phase(frame)
    sp = states[key]
    # nhịp thở: phình nhẹ theo chiều dọc, thon nhẹ chiều ngang (2 nhịp/vòng)
    b = math.sin(2 * math.pi * frame / N * 2)
    sy = 1 + 0.012 * b
    sx = 1 - 0.006 * b
    s = sp.resize((max(1, round(sp.width * sx)), max(1, round(sp.height * sy))), Image.LANCZOS)
    # bóng + đặt chạm đất
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([L.CX - 74, GY - 6, L.CX + 74, GY + 13], fill=(40, 35, 25, 85))
    bg.alpha_composite(sh)
    px = int(L.CX - s.width / 2)
    py = int(GY + 4 - than_day(s))
    bg.alpha_composite(s, (px, py))
    label(bg, lab)
    return bg.convert('RGB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--ma', default='ngo-khong')
    ap.add_argument('--khung', type=int, default=N)
    a = ap.parse_args()
    N = a.khung
    os.makedirs(OUT, exist_ok=True)
    states = render_states(a.ma)
    frames = []
    for i in range(N):
        f = khung_anh(states, i)
        f.save(os.path.join(OUT, f'khung_{i:02d}.png'))
        frames.append(f)
    print('khung:', N, '→', OUT)
    print('contact sheet:', L.contact_sheet(frames, os.path.join(OUT, 'contact-sheet.jpg')))
