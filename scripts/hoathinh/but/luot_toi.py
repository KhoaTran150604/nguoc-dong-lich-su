"""THỬ CHUYỂN ĐỘNG 2 – Ngộ Không LƯỚT tiến về phía trước (KHÔNG thêm chân).

Người dùng chốt: GIỮ NGUYÊN nhân vật, không vẽ chân. Cảm giác "đi tới" tạo bằng CẢ KHUNG CẢNH TRÔI:
  - nền XA (tre/đồi) cuộn NHANH, đất GẦN cuộn chậm hơn (parallax) → đang tiến về phía trước
  - nhân vật đứng gần giữa, LƯỚT nhẹ: nhún lên xuống êm + đung đưa ngang nhẹ (trôi), bóng phập phồng
Không nhảy, không chân — chuyển động mượt kiểu lướt.

Chạy:  python scripts/hoathinh/but/luot_toi.py [--ma ngo-khong] [--khung 16]
Ra:    build/thu-hoathinh/but-luot/khung_00.png ... + contact-sheet.jpg
"""
import argparse
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

from PIL import Image, ImageDraw
import ve as V

W, H = 900, 520
GY = 470                      # mặt đất (mép dưới nhân vật)
SKY = (233, 242, 243)
GROUND = (210, 196, 158)

N = 16
FAR = 14.0                    # px/khung – nền xa cuộn nhanh (đi tới)
NEAR = 6.0                    # px/khung – đất gần cuộn chậm hơn (parallax)
CX = int(W * 0.46)


def sprite(ma, h_target=306):
    tmp = os.path.join(OUT, '_sprite.png')
    V.ve(V.nap(ma), tmp, canvas=(800, 1000), nen=None)
    im = Image.open(tmp).convert('RGBA')
    im = im.crop(im.getbbox())
    s = h_target / im.height
    im = im.resize((max(1, round(im.width * s)), h_target), Image.LANCZOS)
    os.remove(tmp)
    return im


def bamboo(d, x, base, col=(150, 175, 120)):
    d.line([x, base, x, base - 150], fill=col, width=7)
    d.line([x + 22, base, x + 22, base - 120], fill=(135, 162, 108), width=6)
    for yy in range(base - 30, base - 150, -34):
        d.line([x - 14, yy, x + 14, yy - 8], fill=(120, 150, 95), width=4)


def scene(frame):
    bg = Image.new('RGBA', (W, H), SKY + (255,))
    d = ImageDraw.Draw(bg)
    # đồi xa rất nhạt cuộn chậm nhất
    off_hill = (frame * FAR * 0.4) % 300
    for hx in range(-300, W + 300, 300):
        d.ellipse([hx - off_hill, GY - 70, hx - off_hill + 260, GY + 60], fill=(205, 219, 196))
    # tre xa cuộn nhanh
    off_far = (frame * FAR) % 180
    for bx in range(-180, W + 180, 180):
        bamboo(d, int(bx - off_far), GY - 6)
    # đất
    d.rectangle([0, GY, W, H], fill=GROUND + (255,))
    d.line([0, GY, W, GY], fill=(150, 135, 100), width=4)
    # cỏ/đá gần cuộn chậm hơn (parallax so với tre)
    off_near = (frame * NEAR) % 60
    for gx in range(-60, W + 60, 60):
        x = int(gx - off_near)
        d.line([x, GY + 12, x - 7, GY - 6], fill=(120, 150, 90), width=3)
        d.line([x + 7, GY + 12, x + 7, GY - 4], fill=(120, 150, 90), width=3)
        d.ellipse([x + 26, GY + 16, x + 42, GY + 24], fill=(168, 154, 120))
    return bg


def khung_anh(spr, frame):
    bg = scene(frame)
    p = frame / N
    bob = 2 * math.sin(2 * math.pi * p)              # nhún rất nhẹ, vẫn bám đất
    sway = 3 * math.sin(2 * math.pi * p + 1.0)       # đung đưa ngang nhẹ (trôi)
    # bóng dưới chân, đậm nhẹ theo bob
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([CX - 74, GY - 6, CX + 74, GY + 14], fill=(40, 35, 25, 85))
    bg.alpha_composite(sh)
    # nhân vật mẫu LƯỚT TRÊN ĐẤT: mép dưới chạm mặt đất (GY), trôi ngang nhờ nền cuộn
    px = int(CX + sway - spr.width / 2)
    py = int(GY + 4 - int(bob) - spr.height)          # +4: hem lún nhẹ vào đất cho bám
    bg.alpha_composite(spr, (px, py))
    return bg.convert('RGB')


def contact_sheet(frames, ra, cols=8):
    rows = math.ceil(len(frames) / cols)
    tw, th = W // 3, H // 3
    sheet = Image.new('RGB', (tw * cols, th * rows), (255, 255, 255))
    dd = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        sheet.paste(f.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
        cx, cy = (i % cols) * tw, (i // cols) * th
        dd.rectangle([cx, cy, cx + tw - 1, cy + th - 1], outline=(200, 200, 200))
        dd.text((cx + 6, cy + 4), f'{i:02d}', fill=(200, 60, 60))
    sheet.save(ra, quality=90)
    return ra


OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'but-luot')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--ma', default='ngo-khong')
    ap.add_argument('--khung', type=int, default=N)
    a = ap.parse_args()
    N = a.khung
    os.makedirs(OUT, exist_ok=True)
    spr = sprite(a.ma)
    frames = []
    for i in range(N):
        f = khung_anh(spr, i)
        f.save(os.path.join(OUT, f'khung_{i:02d}.png'))
        frames.append(f)
    print('khung:', N, '→', OUT)
    print('contact sheet:', contact_sheet(frames, os.path.join(OUT, 'contact-sheet.jpg')))
