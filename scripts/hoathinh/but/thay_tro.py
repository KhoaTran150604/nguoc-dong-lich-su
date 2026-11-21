"""Ghép thầy trò (Bộ Bút) thành một ảnh: assets/nhan-vat/but/thay-tro.png
Ngựa (dáng 'ngua') rộng hơn người → khung cắt riêng; mọi nhân vật cùng mặt đất, cùng cỡ đầu."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
D = os.path.join(ROOT, 'assets', 'nhan-vat', 'but')
NGUOI, NGUA = (160, 160, 720, 810), (110, 160, 730, 810)
DS = [('duong-tang', 'Đường Tăng', NGUOI), ('ngo-khong', 'Ngộ Không', NGUOI), ('bat-gioi', 'Bát Giới', NGUOI),
      ('sa-tang', 'Sa Tăng', NGUOI), ('bach-long-ma', 'Bạch Long Mã', NGUA)]
DS = [x for x in DS if os.path.exists(os.path.join(D, x[0] + '.png'))]
H = 650
out = Image.new('RGB', (sum(c[2] - c[0] for _, _, c in DS), H + 70), (246, 243, 236))
d = ImageDraw.Draw(out)
f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 40)
x = 0
for ma, ten, cat in DS:
    im = Image.open(os.path.join(D, ma + '.png')).convert('RGB').crop(cat)
    out.paste(im, (x, 0))
    W = cat[2] - cat[0]
    tw = d.textlength(ten, font=f)
    d.text((x + (W - tw) / 2, H + 8), ten, font=f, fill=(60, 50, 40))
    x += W
out.save(os.path.join(D, 'thay-tro.png'))
print('xong', os.path.join(D, 'thay-tro.png'))
