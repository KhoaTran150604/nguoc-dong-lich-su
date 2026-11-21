# -*- coding: utf-8 -*-
"""THUMBNAIL / ẢNH MỞ ĐẦU Short 01 — DỌC 9:16 (vì là Short).
Đường Tăng CHIA ĐÔI: trái = BẤT TÀI (lạnh, xám) · phải = CHỈ HUY (vàng, uy) · giữa = dấu "?".
Chữ to + viền dày (giật gân, để thuật toán YouTube đọc). Góc trái: #Du Ký 1 + keyword ĐƯỜNG TĂNG.

Chạy:  PYTHONUTF8=1 python scripts/hoathinh/but/thumb_short01.py
Ra:    du-an/tay-du-ky/output/banner/short01-thumbnail-doc.png (1080x1920)
"""
import os, sys, math, random
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFont, ImageChops
import short01 as S

TW, TH = 1080, 1920
FD = os.path.join(S.ROOT, 'fonts')
def font(sz): return ImageFont.truetype(os.path.join(FD, 'BeVietnamPro-SemiBold.ttf'), sz)
CX = TW // 2
JAG = 46

def split_mask(side):
    m = Image.new('L', (TW, TH), 0); d = ImageDraw.Draw(m)
    random.seed(7); pts = []; y = 0
    while y <= TH:
        pts.append((CX + random.randint(-JAG, JAG), y)); y += 70
    if side == 'right':
        poly = [(TW, 0), (CX, 0)] + pts + [(TW, TH)]
    else:
        poly = [(0, 0), (CX, 0)] + pts + [(0, TH)]
    d.polygon(poly, fill=255)
    return m

def txt(d, xy, s, f, fill, anchor='mm', stroke=10, sc=(10, 8, 12)):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sc)

def main():
    OUT = os.path.join(S.ROOT, 'du-an', 'tay-du-ky', 'output', 'banner')
    os.makedirs(OUT, exist_ok=True); os.makedirs(S.WORK, exist_ok=True)

    # ── NỀN chia đôi ──
    base = Image.new('RGBA', (TW, TH), (0, 0, 0, 255))
    left = Image.new('RGBA', (TW, TH), (58, 66, 80, 255))
    dl = ImageDraw.Draw(left)
    for i in range(0, TH, 6):
        dl.line([0, i, TW, i], fill=(50, 58, 72, 255), width=2)
    right = Image.new('RGBA', (TW, TH), (150, 104, 30, 255))
    dr = ImageDraw.Draw(right)
    rc = (CX + 230, int(TH * 0.42))
    for a in range(0, 360, 13):
        ang = math.radians(a)
        dr.polygon([rc, (rc[0] + math.cos(ang) * 1700, rc[1] + math.sin(ang) * 1700),
                    (rc[0] + math.cos(ang + 0.06) * 1700, rc[1] + math.sin(ang + 0.06) * 1700)],
                   fill=(196, 150, 54, 255))
    base = Image.composite(left, base, split_mask('left'))
    base = Image.composite(right, base, split_mask('right'))

    # ── ĐƯỜNG TĂNG chia đôi ──
    buon = S.sprite('duong-tang', 'buon', 'buon', h=900, drop=('vu_khi',))
    quyet = S.sprite('duong-tang', 'quyet', 'cuoi', h=900, drop=('vu_khi',))
    foot = 1300
    halo = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([CX - 360, foot - 820, CX + 360, foot + 60], fill=(0, 0, 0, 80))
    base.alpha_composite(halo)
    lb = Image.new('RGBA', (TW, TH), (0, 0, 0, 0)); lb.alpha_composite(buon, (CX - buon.width // 2, foot - buon.height))
    la = ImageChops.multiply(lb.split()[-1], split_mask('left')); lb.putalpha(la)
    cold = Image.new('RGBA', (TW, TH), (70, 90, 120, 95)); cold.putalpha(ImageChops.multiply(cold.split()[-1], la)); lb.alpha_composite(cold)
    base.alpha_composite(lb)
    rb = Image.new('RGBA', (TW, TH), (0, 0, 0, 0)); rb.alpha_composite(quyet, (CX - quyet.width // 2, foot - quyet.height))
    ra_ = ImageChops.multiply(rb.split()[-1], split_mask('right')); rb.putalpha(ra_)
    warm = Image.new('RGBA', (TW, TH), (230, 170, 50, 80)); warm.putalpha(ImageChops.multiply(warm.split()[-1], ra_)); rb.alpha_composite(warm)
    base.alpha_composite(rb)

    d = ImageDraw.Draw(base, 'RGBA')
    # đường chia sáng
    random.seed(7); y = 0; prev = (CX, 0)
    while y <= TH:
        nx = CX + random.randint(-JAG, JAG); d.line([prev, (nx, y)], fill=(255, 226, 150, 230), width=7); prev = (nx, y); y += 70

    # ── CHỮ ──
    # góc trái: #Du Ký 1 + keyword
    txt(d, (44, 70), '#Du Ký 1', font(44), (222, 226, 232), anchor='lm', stroke=6)
    txt(d, (44, 148), 'ĐƯỜNG TĂNG', font(66), (255, 214, 120), anchor='lm', stroke=9)
    # dấu ? khổng lồ giữa (trên đầu)
    txt(d, (CX, 540), '?', font(400), (255, 236, 170), stroke=18, sc=(120, 60, 20))
    # nhãn hai phe (band dưới, dưới chân nhân vật)
    txt(d, (TW * 0.27, TH - 420), 'BẤT TÀI', font(104), (236, 232, 236), stroke=12)
    txt(d, (TW * 0.73, TH - 420), 'CHỈ HUY', font(104), (255, 206, 92), stroke=12)
    txt(d, (TW * 0.27, TH - 320), 'kẻ vô dụng?', font(46), (190, 198, 210), stroke=7)
    txt(d, (TW * 0.73, TH - 320), 'bằng cái vòng?', font(46), (250, 224, 150), stroke=7)

    ra = os.path.join(OUT, 'short01-thumbnail-doc.png')
    base.convert('RGB').save(ra)
    base.convert('RGB').resize((540, 960), Image.LANCZOS).save(os.path.join(OUT, 'short01-thumbnail-doc-web.jpg'), quality=90)
    print('XONG →', ra, '(%dx%d)' % (TW, TH))

if __name__ == '__main__':
    main()
