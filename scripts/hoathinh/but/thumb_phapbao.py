"""Thumbnail 16:9 (1920×1080) cho video 'Top 15 Pháp Bảo Tây Du'.
Chia đôi: Gậy Như Ý (9.0) ⟷ Kim Cang Trác (9.5) + dấu '?' + Ngộ Không sốc.
Chạy: python scripts/hoathinh/but/thumb_phapbao.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import phap_bao as pb  # noqa: E402
import ve as ve_mod  # noqa: E402
from but import Buc  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H = 1920, 1080
TMP = os.path.join(ROOT, 'build', 'thu-hoathinh', 'phap-bao', '_tmp')
os.makedirs(TMP, exist_ok=True)
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')


def _item_png(fn, name, scale=3):
    b = Buc(pb.W, pb.H, nen=None, D=dict(ngoai=9.0, trong=5.0, ct=3.4), scale=scale)
    fn(b)
    b.chot_vien()
    p = os.path.join(TMP, name + '.png')
    return b.luu(p)


def _trim(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def _paste_h(base, im, cx, cy, target_h):
    im = _trim(im)
    w = int(im.width * target_h / im.height)
    im = im.resize((w, target_h), Image.LANCZOS)
    base.alpha_composite(im, (int(cx - w / 2), int(cy - target_h / 2)))


def _text(d, xy, s, size, fill, anchor='la', stroke=0, sfill=(0, 0, 0)):
    d.text(xy, s, font=ImageFont.truetype(FONT, size), fill=fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=sfill)


def main():
    gay = _item_png(pb.gay_nhu_y, 'gay')
    trac = _item_png(pb.kim_cang_trac, 'trac')
    # Ngộ Không sốc (nền trong suốt)
    NV = ve_mod.nap('ngo_khong')
    NV['mat']['bieu_cam'], NV['mat']['mieng'] = 'ngac', 'o'
    nk = os.path.join(TMP, 'nk.png')
    ve_mod.ve(NV, nk, scale=2.0, nen=None)

    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # nền chia đôi (phẳng, không gradient) + đường xé sáng chéo
    GOLD, COLD = (232, 196, 70), (34, 58, 86)
    seam_top, seam_bot = 880, 1060
    d.polygon([(0, 0), (seam_top, 0), (seam_bot, H), (0, H)], fill=GOLD)
    d.polygon([(seam_top, 0), (W, 0), (W, H), (seam_bot, H)], fill=COLD)
    d.line([(seam_top, 0), (seam_bot, H)], fill=(255, 255, 255), width=22)

    _paste_h(img, Image.open(gay).convert('RGBA'), 430, 540, 760)
    _paste_h(img, Image.open(trac).convert('RGBA'), 1440, 520, 640)
    _paste_h(img, Image.open(nk).convert('RGBA'), 960, 850, 460)

    # chữ
    _text(d, (60, 70), '#TÂY DU · PHÁP BẢO', 46, (60, 40, 20), stroke=0)
    _text(d, (56, 110), 'TOP 15', 150, (255, 255, 255), stroke=10, sfill=(60, 40, 10))
    _text(d, (960, 420), '?', 360, (255, 240, 150), anchor='mm', stroke=16, sfill=(30, 20, 0))
    # điểm
    _text(d, (235, 560), '9.0', 140, (255, 255, 255), anchor='mm', stroke=11, sfill=(150, 60, 20))
    _text(d, (1600, 240), '9.5', 150, (255, 245, 180), anchor='mm', stroke=11, sfill=(10, 30, 50))
    # nhãn 2 phe (band dưới)
    d.rounded_rectangle([70, 930, 700, 1030], 20, fill=(40, 28, 10))
    _text(d, (385, 980), 'GẬY NHƯ Ý', 56, (255, 230, 120), anchor='mm')
    d.rounded_rectangle([1150, 930, 1850, 1030], 20, fill=(240, 235, 225))
    _text(d, (1500, 980), 'CÁI VÒNG CON TRÂU?', 50, (170, 50, 40), anchor='mm')

    out = os.path.join(ROOT, 'build', 'thu-hoathinh', 'phap-bao', 'thumbnail-16x9.png')
    img.convert('RGB').save(out)
    print('xong:', out)


if __name__ == '__main__':
    main()
