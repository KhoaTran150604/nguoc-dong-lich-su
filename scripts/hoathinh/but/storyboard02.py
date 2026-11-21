# -*- coding: utf-8 -*-
"""STORYBOARD Short 02 (Bát Giới) — mỗi cảnh 1 hình tĩnh + lời dẫn DƯỚI hình (duyệt mạch trước).
Tái dùng short02.render_frame. Chạy:
  python scripts/hoathinh/but/storyboard02.py [--web <thư mục xuất JPG 480px>]
Ra: build/thu-hoathinh/storyboard02/<sid>.png
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import short02 as S
from PIL import Image, ImageDraw

OUT = os.path.join(S.ROOT, 'build', 'thu-hoathinh', 'storyboard02')

# (act, timecode, sid, lời dẫn hiển thị dưới hình)
SCENES = [
    ('HOOK', '0:00', 'ngunga', 'Cả Tây Du gọi hắn là kẻ ăn hại: tham ăn, mê ngủ, gặp yêu quái là đòi giải tán.'),
    ('HOOK', '0:05', 'hooklat', 'Nhưng cái cào cỏ hắn vác nặng hơn 5.000 cân — 800 năm trước hắn chỉ huy cả đạo quân nhà Trời.'),
    ('HỒI 1', '0:11', 'luoi', 'Lười thì khó ai bằng: việc nặng đùn sư đệ, ăn thì giành phần hơn.'),
    ('HỒI 1', '0:18', 'doigiaitan', '[Bát Giới] Chia hành lý, lão Trư về Cao Lão Trang với vợ cho rồi!'),
    ('HỒI 2', '0:26', 'dinhba', 'Cào do Thái Thượng Lão Quân rèn — nặng đúng 5.048 cân = "một tạng" (số ngày thỉnh kinh).'),
    ('HỒI 2', '0:33', 'thienbong', 'Hắn từng là Thiên Bồng Nguyên Soái, thống lĩnh 8 vạn thủy quân Thiên Hà.'),
    ('HỒI 2', '0:40', 'gheohang', '[Thiên Bồng, say] Nàng Hằng Nga… lại đây với bản soái một chén…'),
    ('HỒI 2', '0:47', 'bibat', 'Một lần ghẹo Hằng Nga: 2.000 chùy, đày xuống trần, đầu thai nhầm vào bụng lợn.'),
    ('HỒI 2', '0:55', 'duoinuoc', '[Ngộ Không] Lão Trư… xuống nước thì ta thua ngươi. Lần này thôi đấy!'),
    ('HỒI 2', '1:02', 'duoinuoc2', 'Dưới nước, đến Ngộ Không cũng chịu thua — giỏi nhất nhì cả đoàn.'),
    ('ĐIỂM NỔ', '1:09', 'tinhdan', 'Thành Phật, phong Tịnh Đàn Sứ Giả — kẻ ham ăn được Phật cho ăn cả đời.'),
    ('CHỐT', '1:18', 'chot', 'Kẻ ăn hại, hay kẻ duy nhất dám đòi về nhà mà 14 năm chưa từng về thật?'),
    ('CTA', '1:27', 'cta', 'Kẻ ăn hại hay người thật nhất Tây Du? Chọn phe đi 👇'),
]


def card(sid, loi, act, tc):
    img = S.render_frame(sid, 0.6, {'mouth': 'noi'}).convert('RGB')
    pad = 150
    canvas = Image.new('RGB', (S.W, S.H + pad), (248, 245, 238))
    canvas.paste(img, (0, 0))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, 260, 34], fill=(0, 0, 0))
    d.text((6, 4), '%s · %s · %s' % (act, tc, sid), fill=(255, 230, 120), font=S.font(20))
    for i, ln in enumerate(S.wrap(d, loi, S.font(26, False), S.W - 48)):
        d.text((24, S.H + 14 + i * 36), ln, fill=(40, 34, 30), font=S.font(26, False))
    return canvas


def main():
    web = None
    if '--web' in sys.argv:
        web = sys.argv[sys.argv.index('--web') + 1]
        os.makedirs(web, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    for act, tc, sid, loi in SCENES:
        c = card(sid, loi, act, tc)
        c.save(os.path.join(OUT, '%s.png' % sid))
        if web:
            w = 480
            c.resize((w, round(c.height * w / c.width)), Image.LANCZOS).save(os.path.join(web, '%s.jpg' % sid), quality=86)
        print('  ', sid)
    print('XONG storyboard →', OUT)


if __name__ == '__main__':
    main()
