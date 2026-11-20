"""THỬ CHUYỂN ĐỘNG – Ngộ Không nhún bước đi ngang (chibi không chân → bước nhảy nhún).

Cách làm: render MỘT sprite trong suốt bằng Bộ Bút (nen=None), rồi hoạt hoạ bằng PIL:
  - trượt ngang x: trái → phải
  - nhún (hop): 2 bước mỗi vòng, chân chạm đất đầu/cuối mỗi bước, đỉnh giữa bước
  - ép/giãn (squash & stretch): bay lên thì cao–thon, chạm đất thì thấp–bè
  - nghiêng nhẹ theo đà
  - bóng dưới chân co lại khi bay

Chạy:  python scripts/hoathinh/but/di_chuyen.py [--ma ngo-khong] [--khung 14]
Ra:    build/thu-hoathinh/but-dichuyen/khung_00.png ... + contact-sheet.jpg
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

W, H = 900, 520          # khung cảnh
GY = 452                 # cao độ mặt đất (chân chạm)
SKY = (234, 242, 244)    # trời phẳng (không gradient – đúng luật sitcom)
GROUND = (214, 201, 166)
GROUND_LINE = (150, 135, 100)


def sprite(ma, h_target=300):
    """Render nhân vật nền trong suốt, cắt sát theo alpha, thu về cao h_target."""
    tmp = os.path.join(OUT, '_sprite.png')
    NV = V.nap(ma)
    V.ve(NV, tmp, canvas=(800, 1000), nen=None)
    im = Image.open(tmp).convert('RGBA')
    im = im.crop(im.getbbox())                       # cắt sát
    s = h_target / im.height
    im = im.resize((max(1, round(im.width * s)), h_target), Image.LANCZOS)
    os.remove(tmp)
    return im


def scene():
    bg = Image.new('RGBA', (W, H), SKY + (255,))
    d = ImageDraw.Draw(bg)
    d.rectangle([0, GY, W, H], fill=GROUND + (255,))
    d.line([0, GY, W, GY], fill=GROUND_LINE, width=4)
    # vài vệt cỏ phẳng cho đỡ trống
    for gx in range(40, W, 120):
        d.line([gx, GY, gx - 6, GY - 14], fill=(120, 150, 90), width=3)
        d.line([gx + 6, GY, gx + 6, GY - 11], fill=(120, 150, 90), width=3)
    return bg


def khung_anh(spr, p):
    """p ∈ [0,1): một vòng đi (2 bước nhảy). Trả ảnh cảnh đã ghép."""
    bg = scene().copy()
    x = int(W * 0.12 + (W * 0.76) * p)               # trượt ngang

    hp = (p * 2) % 1.0                               # pha trong một bước nhảy
    air = math.sin(math.pi * hp)                     # 0 ở chạm đất, 1 ở đỉnh
    land = max(0.0, math.cos(math.pi * hp)) ** 3     # xung chạm đất (đầu bước)
    sy = 1 + 0.13 * air - 0.12 * land                # cao khi bay, lùn khi chạm
    sx = 1 - 0.07 * air + 0.10 * land                # thon khi bay, bè khi chạm
    lean = 7 * math.sin(2 * math.pi * p)             # nghiêng theo đà

    w2, h2 = max(1, round(spr.width * sx)), max(1, round(spr.height * sy))
    s = spr.resize((w2, h2), Image.LANCZOS).rotate(-lean, expand=True, resample=Image.BICUBIC)

    foot_y = GY - int(air * 70)                      # bay lên 70px ở đỉnh
    px, py = x - s.width // 2, foot_y - s.height

    # bóng co theo độ cao
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    bw = int((70 - air * 34) * (s.width / 180))
    bh = int(14 - air * 6)
    sd.ellipse([x - bw, GY - bh, x + bw, GY + bh], fill=(40, 35, 25, int(90 - air * 55)))
    bg.alpha_composite(sh)
    bg.alpha_composite(s, (px, py))
    return bg.convert('RGB')


def contact_sheet(frames, ra, cols=7):
    rows = math.ceil(len(frames) / cols)
    tw, th = W // 3, H // 3
    sheet = Image.new('RGB', (tw * cols, th * rows), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(frames):
        t = f.resize((tw, th), Image.LANCZOS)
        cx, cy = (i % cols) * tw, (i // cols) * th
        sheet.paste(t, (cx, cy))
        d.rectangle([cx, cy, cx + tw - 1, cy + th - 1], outline=(200, 200, 200))
        d.text((cx + 6, cy + 4), f'{i:02d}', fill=(200, 60, 60))
    sheet.save(ra, quality=90)
    return ra


OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'but-dichuyen')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--ma', default='ngo-khong')
    ap.add_argument('--khung', type=int, default=14)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    spr = sprite(a.ma)
    frames = []
    for i in range(a.khung):
        f = khung_anh(spr, i / a.khung)
        f.save(os.path.join(OUT, f'khung_{i:02d}.png'))
        frames.append(f)
    print('khung:', a.khung, '→', OUT)
    print('contact sheet:', contact_sheet(frames, os.path.join(OUT, 'contact-sheet.jpg')))
