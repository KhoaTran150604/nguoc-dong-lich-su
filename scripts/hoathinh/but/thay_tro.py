"""Ghép 4 thầy trò (Bộ Bút) thành một ảnh: assets/nhan-vat/but/thay-tro.png"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = os.path.join(ROOT, 'assets', 'nhan-vat', 'but')
DS = [('duong-tang', 'Đường Tăng'), ('ngo-khong', 'Ngộ Không'), ('bat-gioi', 'Bát Giới'), ('sa-tang', 'Sa Tăng')]
W, H = 560, 650
out = Image.new('RGB', (W * 4, H + 70), (246, 243, 236))
d = ImageDraw.Draw(out)
f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 40)
for i, (ma, ten) in enumerate(DS):
    im = Image.open(os.path.join(D, ma + '.png')).convert('RGB').crop((160, 160, 720, 810))
    out.paste(im, (i * W, 0))
    tw = d.textlength(ten, font=f)
    d.text((i * W + (W - tw) / 2, H + 8), ten, font=f, fill=(60, 50, 40))
out.save(os.path.join(D, 'thay-tro.png'))
print('xong', os.path.join(D, 'thay-tro.png'))
