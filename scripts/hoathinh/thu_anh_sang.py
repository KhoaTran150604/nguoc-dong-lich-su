"""Thử nhiều kiểu ánh sáng trên cùng nền bến sông → bảng so sánh.
Chạy: python scripts/hoathinh/thu_anh_sang.py  →  build/thu-hoathinh/sitcom-20s/anh-sang/*.jpg + bang-anh-sang.jpg
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ben_song as bs  # noqa: E402
import anhsang  # noqa: E402

ROOT = bs.cc.ROOT
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'sitcom-20s', 'anh-sang')
W, H = 1920, 1080

# mỗi kiểu: preset ánh sáng + màu nhân lên nền (tint) + độ sáng
KIEU = {
    'A-diu':        ('Chiều dịu (mặc định mới)', dict(), (1.00, 1.00, 1.00), 1.00),
    'B-som-suong':  ('Sáng sớm sương mờ', dict(sun=(236, 236, 228), shadow=(70, 76, 96), light_dir=(0.7, -0.7), sun_k=0.12,
                     dark_k=0.24, haze=(222, 226, 226), haze_k=0.55, split_lo=(60, 70, 100), split_hi=(236, 232, 214),
                     split_k=0.18, contrast=0.96, sat=0.62, vignette=0.30), (0.96, 1.00, 1.02), 1.02),
    'C-trua-nang':  ('Trưa nắng gắt', dict(sun=(255, 246, 220), shadow=(40, 36, 60), light_dir=(-0.2, -0.98), sun_k=0.22,
                     dark_k=0.30, haze=(232, 228, 214), haze_k=0.18, split_lo=(40, 40, 80), split_hi=(255, 236, 196),
                     split_k=0.14, contrast=1.14, sat=0.85, vignette=0.30), (1.0, 1.0, 0.97), 1.0),
    'D-hoang-hon':  ('Hoàng hôn cam', dict(sun=(255, 170, 100), shadow=(70, 30, 70), light_dir=(-0.9, -0.42), sun_k=0.34,
                     dark_k=0.40, haze=(236, 170, 130), haze_k=0.34, split_lo=(80, 30, 90), split_hi=(255, 180, 110),
                     split_k=0.28, contrast=1.08, sat=0.80, vignette=0.50), (1.04, 0.86, 0.74), 0.92),
    'E-xe-chieu':   ('Xế chiều trầm (kiểu phim cũ)', dict(sun=(232, 200, 150), shadow=(50, 40, 50), light_dir=(-0.62, -0.78),
                     sun_k=0.16, dark_k=0.42, haze=(200, 184, 160), haze_k=0.30, split_lo=(52, 44, 60),
                     split_hi=(226, 196, 150), split_k=0.30, contrast=1.02, sat=0.58, vignette=0.55),
                     (0.98, 0.94, 0.86), 0.90),
    'F-dem-trang':  ('Đêm trăng + đèn lồng', dict(sun=(190, 210, 255), shadow=(14, 18, 44), light_dir=(-0.4, -0.9),
                     sun_k=0.10, dark_k=0.40, haze=(70, 84, 120), haze_k=0.25, split_lo=(14, 22, 64), split_hi=(196, 210, 255),
                     split_k=0.26, contrast=1.06, sat=0.70, vignette=0.55), (0.42, 0.50, 0.72), 0.80),
}


def base():
    L = bs.build()
    cv = L['sky'].copy()
    cv.alpha_composite(L['mud'])
    bs.water(cv, 452, 0)
    bs.boat(cv, 1450, 492, 0.9)
    cv.alpha_composite(L['mid'])
    cv.alpha_composite(L['fg'])
    return cv.resize((W, H), Image.LANCZOS)


def lantern_glow(im, k):
    """Quầng sáng đèn lồng (chỉ rõ khi tối)."""
    a = np.asarray(im, np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-((xx - 452) ** 2 + (yy - 395) ** 2) / (2 * 150 ** 2))[..., None]
    a = a + g * np.array([1.0, 0.62, 0.30], np.float32) * k
    return Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))


def main():
    os.makedirs(OUT, exist_ok=True)
    b = base()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    thumbs = []
    for key, (name, pre, tint, gain) in KIEU.items():
        p = dict(anhsang.PRESETS['diu'])
        p.update(pre)
        anhsang.PRESETS[key] = p
        arr = np.asarray(b.convert('RGB'), np.float32) * np.array(tint, np.float32) * gain
        bb = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
        im = anhsang.ap_dung(bb, ov, key)
        if key == 'F-dem-trang':
            im = lantern_glow(im, 0.55)
        if key == 'D-hoang-hon':
            im = lantern_glow(im, 0.15)
        im.save(os.path.join(OUT, key + '.jpg'), quality=92)
        thumbs.append((key, name, im.resize((W // 2, H // 2), Image.LANCZOS)))
        print(key, flush=True)
    sheet = Image.new('RGB', (W, H // 2 * 3 + 3 * 56), (24, 20, 18))
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 34)
    for i, (key, name, t) in enumerate(thumbs):
        x, y = (i % 2) * W // 2, (i // 2) * (H // 2 + 56)
        ImageDraw.Draw(sheet).text((x + 20, y + 10), '%s · %s' % (key[0], name), font=f, fill=(242, 230, 204))
        sheet.paste(t, (x, y + 56))
    p = os.path.join(OUT, 'bang-anh-sang.jpg')
    sheet.save(p, quality=90)
    print(p)


if __name__ == '__main__':
    main()
