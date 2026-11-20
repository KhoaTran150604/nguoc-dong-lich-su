"""Gâu Nghệ – avatar toàn thân nhỏ, có động tác, đổ bóng mềm + nền đồng cỏ (tham khảo cách bố cục kiểu sitcom VN).
Chạy: python scripts/hoathinh/gau_nghe_avatar.py  → build/thu-hoathinh/gau-nghe/avatar-dong-tac.jpg
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gau_nghe_van import card, hx, OUT, ROOT  # noqa: E402

BASE = dict(soft=True, full=True)
POSES = [
    ('Vẫy chào', dict(eyes='happy', mouth='tongue', arms=((18, 8), (112, 162)))),
    ('Chỉ tay lém lỉnh', dict(mouth='smirk', lid=(0.42, 0.34), gaze=(1, 0), arms=((18, 8), (80, 122)))),
    ('Ôm sách kể sử', dict(book=True, mouth='open', gaze=(0, 1))),
    ('Hai tay "yeah"', dict(mouth='open', big=1.15, arms=((112, 162), (112, 162)))),
]
ROWS = [('Mặt đen – sọc trắng (bản B)', {}),
        ('Mặt nạ trắng – mắt chấm, má hồng', dict(mask='wide', eyes='dot', blush=True))]


def main():
    A, LAB, TOP, HL = 400, 40, 80, 46
    W = A * len(POSES)
    H = TOP + len(ROWS) * (HL + A + LAB)
    img = Image.new('RGB', (W, H), hx('#F2E6CC'))
    dr = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf'), 40)
    f_h = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 24)
    f_n = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 20)
    dr.text((20, 18), 'GÂU NGHỆ – avatar có động tác, đổ bóng', font=f_t, fill=hx('#14110F'))
    y = TOP
    n = 0
    for rname, rst in ROWS:
        dr.text((20, y + 10), rname, font=f_h, fill=hx('#B3261E'))
        y += HL
        for i, (pname, pst) in enumerate(POSES):
            n += 1
            st = {**BASE, **pst, **rst}
            av = card(st, 800, 800, avatar=True, bg='ngay')
            av.save(os.path.join(OUT, f'avatar-dong-tac-{n}.png'))
            img.paste(av.resize((A, A), Image.LANCZOS), (i * A, y))
            dr.text((i * A + A / 2, y + A + 18), f'{n} · {pname}', font=f_n, fill=hx('#14110F'), anchor='mm')
        y += A + LAB
    p = os.path.join(OUT, 'avatar-dong-tac.jpg')
    img.save(p, quality=92)
    print(p)


if __name__ == '__main__':
    main()
