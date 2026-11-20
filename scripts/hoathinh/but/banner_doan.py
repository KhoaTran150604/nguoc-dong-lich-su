# -*- coding: utf-8 -*-
"""BANNER 16:9 — cả đoàn Đường Tăng đi (đổi khung ngang từ cảnh đường xa).
Đội hình trái→phải: Sa Tăng · ngựa · Đường Tăng · Bát Giới · Ngộ Không.
Giãn đều — KHÔNG nhân vật nào bị che hay cắt mép.

Chạy:  PYTHONUTF8=1 python scripts/hoathinh/but/banner_doan.py
Ra:    du-an/tay-du-ky/output/banner/short01-doan-16x9.png
"""
import os, sys, math
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
import short01 as S

BW, BH = 1920, 1080

def bg_land():
    im = Image.new('RGBA', (BW, BH), (236, 200, 150, 255)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, BW, int(BH * 0.30)], fill=(242, 206, 150, 255))
    d.rectangle([0, int(BH * 0.30), BW, int(BH * 0.38)], fill=(236, 188, 138, 255))
    d.ellipse([BW * 0.80, BH * 0.10, BW * 0.80 + 180, BH * 0.10 + 180], fill=(250, 232, 180, 255))  # mặt trời
    gy = int(BH * 0.50)
    for cy, col in [(gy - 36, (176, 170, 132)), (gy - 6, (150, 150, 110))]:
        for hx in range(-240, BW + 240, 360):
            d.ellipse([hx, cy - 84, hx + 360, cy + 110], fill=col + (255,))
    d.rectangle([0, gy, BW, BH], fill=(150, 128, 92, 255))
    d.line([0, gy, BW, gy], fill=(120, 100, 70, 255), width=6)
    # lối mòn hình thang (xa → gần)
    d.polygon([(BW * 0.44, gy), (BW * 0.56, gy), (BW * 0.74, BH), (BW * 0.26, BH)], fill=(178, 156, 116, 255))
    for yy in range(gy + 24, BH, 110):
        t = (yy - gy) / (BH - gy); w = 8 + 20 * t
        d.line([BW * 0.5 - w, yy, BW * 0.5 + w, yy], fill=(150, 130, 96, 255), width=int(4 + 5 * t))
    return im

def shadow(bg, cx, by, w, a=80):
    sh = Image.new('RGBA', (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - w, by - 18, cx + w, by + 20], fill=(40, 32, 22, a))
    bg.alpha_composite(sh)

def paste(bg, spr, cx, by):
    bg.alpha_composite(spr, (int(cx - spr.width / 2), int(by - spr.height)))

def main():
    OUT = os.path.join(S.ROOT, 'du-an', 'tay-du-ky', 'output', 'banner')
    os.makedirs(OUT, exist_ok=True); os.makedirs(S.WORK, exist_ok=True)
    bg = bg_land()
    gy = int(BH * 0.90)
    # (mã, biểu cảm, miệng, cao px, lật, tâm_x tỉ lệ) — giãn đều, không chồng
    team = [('sa-tang',      'hien', 'cuoi', 430, False, 0.12),
            ('bach-long-ma', 'hien', 'mim',  330, False, 0.31),
            ('duong-tang',   'hien', 'cuoi', 450, False, 0.50),
            ('bat-gioi',     'hien', 'cuoi', 420, False, 0.69),
            ('ngo-khong',    'quyet','cuoi', 440, False, 0.88)]
    for ma, bc, mi, hh, fl, px in team:
        spr = S.sprite(ma, bc, mi, h=hh, flip=fl)
        cx = int(BW * px)
        shadow(bg, cx, gy, w=int(spr.width * 0.42))
        paste(bg, spr, cx, gy)
    ra = os.path.join(OUT, 'short01-doan-16x9.png')
    bg.convert('RGB').save(ra)
    # bản web nhẹ
    web = bg.convert('RGB').resize((1280, 720), Image.LANCZOS)
    web.save(os.path.join(OUT, 'short01-doan-16x9-web.jpg'), quality=88)
    print('XONG →', ra, '(%dx%d)' % (BW, BH))

if __name__ == '__main__':
    main()
