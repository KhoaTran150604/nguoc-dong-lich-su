# -*- coding: utf-8 -*-
"""BANNER ngang 16:9 (1920x1080) cả đoàn cho Short 02 — nhân vật KHÔNG che/cắt.
Đội hình chuẩn trái→phải: Sa Tăng · ngựa · Đường Tăng · Bát Giới · Ngộ Không. + Thiên Bồng (bóng) góc.
Chạy: python scripts/hoathinh/but/banner_doan02.py
Ra:   du-an/tay-du-ky/output/banner/short02-doan-16x9.png (+ web 1280x720)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import short02 as S
from PIL import Image, ImageDraw, ImageFont

BW, BH = 1920, 1080
OUTDIR = os.path.join(S.ROOT, 'du-an', 'tay-du-ky', 'output', 'banner')


def font(sz, bold=True):
    return ImageFont.truetype(os.path.join(S.FD, 'BeVietnamPro-%s.ttf' % ('SemiBold' if bold else 'Medium')), sz)


def bg_land():
    """đường thiên lý xế chiều — bản ngang."""
    im = Image.new('RGBA', (BW, BH), (236, 200, 150, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, BW, int(BH * 0.40)], fill=(242, 206, 150, 255))
    d.ellipse([BW * 0.70, BH * 0.10, BW * 0.80, BH * 0.28], fill=(250, 232, 180, 255))
    gy = int(BH * 0.56)
    for cy, col in [(gy - 46, (176, 170, 132)), (gy - 16, (150, 150, 110))]:
        for hx in range(-200, BW + 200, 360):
            d.ellipse([hx, cy - 80, hx + 340, cy + 100], fill=col + (255,))
    d.rectangle([0, gy, BW, BH], fill=(150, 128, 92, 255))
    d.line([0, gy, BW, gy], fill=(120, 100, 70, 255), width=6)
    return im


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    im = bg_land()
    gy = int(BH * 0.96)
    # bóng Thiên Bồng oai phong góc phải (tiền kiếp) — mờ, không che đoàn
    tb = S.silhouette(S.sprite('thien-bong', 'quyet', 'thang', h=820), col=(120, 70, 56))
    im.alpha_composite(tb, (int(BW * 0.84) - tb.width // 2, gy - tb.height))

    team = [('sa-tang', 'hien', 'mim', 520, False, 0.12),
            ('bach-long-ma', 'hien', 'mim', 470, False, 0.30),
            ('duong-tang', 'hien', 'cuoi', 540, False, 0.48),
            ('bat-gioi', 'cuoi_nham', 'cuoi', 520, False, 0.64),
            ('ngo-khong', 'quyet', 'mim', 540, False, 0.80)]
    for ma, bc, mi, hh, fl, px in team:
        spr = S.sprite(ma, bc, mi, h=hh, flip=fl)
        x = int(BW * px)
        d = ImageDraw.Draw(im)
        d.ellipse([x - 150, gy - 40, x + 150, gy + 24], fill=(0, 0, 0, 110))
        im.alpha_composite(spr, (x - spr.width // 2, gy - spr.height))

    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 36, 560, 128], radius=18, fill=(150, 58, 44, 240))
    d.text((60, 52), 'TÂY DU KÝ · #Du Ký 2', font=font(52), fill=(255, 240, 210))

    out = os.path.join(OUTDIR, 'short02-doan-16x9.png')
    im.convert('RGB').save(out)
    im.convert('RGB').resize((1280, 720), Image.LANCZOS).save(os.path.join(OUTDIR, 'short02-doan-16x9-web.jpg'), quality=88)
    print('XONG →', out)


if __name__ == '__main__':
    main()
