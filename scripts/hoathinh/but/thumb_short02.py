# -*- coding: utf-8 -*-
"""THUMBNAIL dọc 9:16 (1080x1920) cho Short 02 — concept "HÀO QUANG ĐỔ BÓNG":
Bát Giới chibi (màu) ngáp lười phía trước, sau lưng là BÓNG Thiên Bồng Nguyên Soái oai phong
(tia hào quang FLAT) → tương phản "tướng trời ↔ kẻ ăn hại". KHÁC khuôn tập 1 (không chia đôi + dấu ?).

Chạy: python scripts/hoathinh/but/thumb_short02.py
Ra:   du-an/tay-du-ky/output/banner/short02-thumbnail-doc.png (+ bản web 540x960)
"""
import os
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import short02 as S
from PIL import Image, ImageDraw, ImageFont

TW, TH = 1080, 1920
FD = S.FD
OUTDIR = os.path.join(S.ROOT, 'du-an', 'tay-du-ky', 'output', 'banner')


def font(sz, bold=True):
    return ImageFont.truetype(os.path.join(FD, 'BeVietnamPro-%s.ttf' % ('SemiBold' if bold else 'Medium')), sz)


def txt(d, xy, s, f, fill, anchor='la', stroke=10, sc=(14, 11, 16)):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sc)


def sprite_h(ma, bc, mi, h, flip=False):
    """render sprite ở chiều cao h px cho thumbnail."""
    return S.sprite(ma, bc, mi, h=h, flip=flip)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    im = Image.new('RGBA', (TW, TH), (24, 20, 28, 255))
    d = ImageDraw.Draw(im)

    # nền: trời chiều ấm phía trên (flat) + đất tối dưới
    d.rectangle([0, 0, TW, int(TH * 0.60)], fill=(40, 30, 40, 255))
    d.rectangle([0, int(TH * 0.60), TW, TH], fill=(26, 20, 26, 255))

    # HÀO QUANG FLAT tia toả sau Thiên Bồng (không glow/blur)
    cx, cy = int(TW * 0.5), int(TH * 0.34)
    ray = Image.new('RGBA', (TW, TH), (0, 0, 0, 0)); dr = ImageDraw.Draw(ray)
    for ang in range(0, 360, 12):
        a = math.radians(ang)
        p1 = (cx + math.cos(a) * 60, cy + math.sin(a) * 60)
        p2 = (cx + math.cos(a + 0.05) * 1500, cy + math.sin(a + 0.05) * 1500)
        p3 = (cx + math.cos(a + 0.10) * 60, cy + math.sin(a + 0.10) * 60)
        dr.polygon([p1, p2, p3], fill=(236, 190, 84, 42))
    im.alpha_composite(ray)

    # BÓNG Thiên Bồng oai phong (lớn, phía sau, hơi lệch phải) — viền vàng cho đọc "hào quang"
    tb = sprite_h('thien-bong', 'quyet', 'thang', 1250)
    rim = S.silhouette(tb, col=(236, 190, 84))        # viền vàng
    dark = S.silhouette(tb, col=(12, 9, 14))          # thân bóng tối
    bx, by = int(TW * 0.60), int(TH * 0.70)
    for ox, oy in [(-10, 0), (10, 0), (0, -10), (0, 10)]:
        im.alpha_composite(rim, (bx - rim.width // 2 + ox, by - rim.height + oy))
    im.alpha_composite(dark, (bx - dark.width // 2, by - dark.height))

    # BÁT GIỚI màu (trước, lớn, lệch trái) — ngáp lười
    bgi = sprite_h('bat-gioi', 'cuoi_nham', 'cuoi', 1180)
    gx, gy = int(TW * 0.37), int(TH * 0.98)
    # bệ bóng dưới chân
    d.ellipse([gx - 240, gy - 60, gx + 240, gy + 30], fill=(0, 0, 0, 120))
    im.alpha_composite(bgi, (gx - bgi.width // 2, gy - bgi.height))

    d = ImageDraw.Draw(im)
    # (đã bỏ chip "#Du Ký 2 · BÁT GIỚI" góc trên trái — khi đăng Short bị UI che)

    # CHỮ CHÍNH — hook giật, không chắn mặt
    txt(d, (TW // 2, int(TH * 0.075)), 'TƯỚNG TRỜI?', font(126), (255, 214, 96), anchor='ma', stroke=14)
    # band dưới: 2 nhãn hai phe
    d.rounded_rectangle([40, int(TH * 0.845), TW - 40, int(TH * 0.925)], radius=28, fill=(16, 12, 18, 235))
    txt(d, (int(TW * 0.29), int(TH * 0.885)), 'KẺ ĂN HẠI', font(64), (255, 150, 120), anchor='mm', stroke=9)
    txt(d, (int(TW * 0.545), int(TH * 0.883)), 'VS', font(52), (255, 90, 70), anchor='mm', stroke=7)
    txt(d, (int(TW * 0.775), int(TH * 0.885)), 'TƯỚNG TRỜI', font(56), (255, 224, 130), anchor='mm', stroke=8)
    # câu phụ nhỏ dưới cùng
    d.text((TW // 2, int(TH * 0.95)), 'Bí mật 800 năm của gã heo lười', font=font(40, False),
           fill=(240, 228, 206), anchor='mm')

    out = os.path.join(OUTDIR, 'short02-thumbnail-doc.png')
    im.convert('RGB').save(out)
    web = im.convert('RGB').resize((540, 960), Image.LANCZOS)
    web.save(os.path.join(OUTDIR, 'short02-thumbnail-doc-web.jpg'), quality=88)
    print('XONG →', out)


if __name__ == '__main__':
    main()
