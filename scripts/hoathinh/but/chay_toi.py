"""THỬ CHUYỂN ĐỘNG 3 – Ngộ Không CHẠY tới (ngả người về phía trước + lướt nhanh, KHÔNG chân).

Giữ nguyên nhân vật mẫu (không thêm chân). Chạy = :
  - NGẢ NGƯỜI về phía trước (nghiêng sprite ~12°, dao động nhẹ)
  - nền cuộn NHANH hơn clip đi lướt (tre/đồi xa phóng nhanh)
  - VỆT TỐC ĐỘ kẻ ngang sau lưng (mờ, phẳng) cho cảm giác lao tới
  - nhún nảy 2 nhịp/vòng (chạy bật hơn đi)
Dùng lại nền + sprite của luot_toi.py.

Chạy:  python scripts/hoathinh/but/chay_toi.py [--ma ngo-khong] [--khung 14]
Ra:    build/thu-hoathinh/but-chay/khung_00.png ... + contact-sheet.jpg
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
from PIL import Image, ImageDraw
import luot_toi as L

W, H, GY = L.W, L.H, L.GY
N = 14
LEAN = 12.0                   # độ ngả người về trước
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'but-chay')


def speed_lines(bg, frame, cx):
    """vệt tốc độ ngang, mờ & phẳng (không glow), chạy nhanh sau lưng."""
    d = ImageDraw.Draw(bg, 'RGBA')
    rng = [(0.34, 150), (0.46, 220), (0.58, 110), (0.70, 190), (0.82, 140)]
    for k, (yf, ln) in enumerate(rng):
        y = int(GY - 220 * (1 - yf))
        off = (frame * 46 + k * 73) % 300
        x1 = int(cx - 70 - off)
        d.line([x1, y, x1 + ln, y], fill=(255, 255, 255, 120), width=3)
        d.line([x1 - 30, y, x1 - 8, y], fill=(255, 255, 255, 70), width=3)


def khung_anh(spr, frame):
    bg = L.scene(frame)
    p = frame / N
    speed_lines(bg, frame, L.CX)
    lean = LEAN + 2.0 * math.sin(2 * math.pi * p)     # ngả tới, lắc nhẹ
    # bóng dưới chân (thân luôn chạm đất)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([L.CX - 72, GY - 6, L.CX + 72, GY + 13], fill=(40, 35, 25, 85))
    bg.alpha_composite(sh)
    # ngả người về trước (đỉnh ngả sang phải = hướng đi) → xoay theo chiều kim đồng hồ
    s = spr.rotate(-lean, expand=True, resample=Image.BICUBIC)
    bb = s.getbbox()
    cxp = (bb[0] + bb[2]) / 2                           # tâm ngang phần vẽ
    # ĐÁY THÂN = hàng thấp nhất CÓ BỀ RỘNG LỚN (mép áo), bỏ qua đuôi gậy mảnh chọc xuống
    al = np.array(s.split()[-1])
    rong = (al > 10).sum(axis=1)
    hang = np.where(rong >= 44)[0]
    than_day = int(hang.max()) if len(hang) else bb[3]
    px = int(L.CX + lean * 0.5 - cxp)                  # canh giữa, dồn tới trước chút
    py = int(GY + 4 - than_day)                         # mép áo chạm mặt đất (lún 4px)
    bg.alpha_composite(s, (px, py))
    return bg.convert('RGB')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--ma', default='ngo-khong')
    ap.add_argument('--khung', type=int, default=N)
    a = ap.parse_args()
    N = a.khung
    L.FAR, L.NEAR = 26.0, 11.0                          # chạy: nền cuộn nhanh
    os.makedirs(OUT, exist_ok=True)
    spr = L.sprite(a.ma)
    frames = []
    for i in range(N):
        f = khung_anh(spr, i)
        f.save(os.path.join(OUT, f'khung_{i:02d}.png'))
        frames.append(f)
    print('khung:', N, '→', OUT)
    print('contact sheet:', L.contact_sheet(frames, os.path.join(OUT, 'contact-sheet.jpg')))
