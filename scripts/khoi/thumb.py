"""Thumbnail / ảnh bìa cho Short (1080x1920) và video dài (1280x720).
python3 scripts/khoi/thumb.py --part P1 --line1 "VUA ĐẤT GIAO" --line2 "…CHƯA CÓ ĐẤT?" --seal "GIAO|VƯƠNG" --out assets/e2/thumb-P1.png
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

def build(part, line1, line2, seal_lines, foot, size):
    W0, H0 = size; im = R.make_bg().resize((1080, 1920)).copy()
    d = ImageDraw.Draw(im, 'RGBA')
    # vầng sáng đỏ phía sau con dấu
    glow = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse([190, 520, 890, 1220], fill=R.RED + (90,)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    R.seal(im, 10, 540, 860, 520, seal_lines)
    def fit(txt, mx, start):
        s = start
        while d.textlength(txt, font=R.F_TITLE(s)) > mx: s -= 4
        return R.F_TITLE(s)
    R.text_center(d, 230, line1, fit(line1, 980, 150), R.GOLD2 + (255,))
    R.text_center(d, 1200, line2, fit(line2, 980, 140), R.CREAM + (255,))
    d.rounded_rectangle([340, 1430, 740, 1530], radius=50, fill=R.RED + (255,))
    R.text_center(d, 1445, part, R.F_TITLE(62), R.CREAM + (255,))
    R.text_center(d, 1580, foot, R.F_SEMI(52), R.GOLD + (255,), spacing=3)
    av = R.avatar_layers()[2].resize((150, 150))
    im.alpha_composite(av, (465, 1690))
    if size != (1080, 1920):  # khung ngang: cắt phần giữa rồi đặt cạnh chữ
        im2 = R.make_bg().resize((W0, H0)); d2 = ImageDraw.Draw(im2, 'RGBA')
        crop = im.crop((0, 560, 1080, 1560)).resize((int(1080 * H0 / 1000 * 0.95), int(H0 * 0.95)))
        im2.alpha_composite(crop, (W0 - crop.width, int(H0 * 0.025)))
        f1 = R.F_TITLE(110); f2 = R.F_TITLE(80)
        d2.text((60, 120), line1, font=f1, fill=R.GOLD2 + (255,)); d2.text((60, 280), line2, font=f2, fill=R.CREAM + (255,))
        d2.text((60, 560), foot, font=R.F_SEMI(44), fill=R.GOLD + (255,))
        return im2
    return im

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--part', default='P1'); ap.add_argument('--line1', required=True); ap.add_argument('--line2', required=True)
    ap.add_argument('--seal', default='GIAO|VƯƠNG'); ap.add_argument('--foot', default='BẠCH ĐẰNG 938')
    ap.add_argument('--out', required=True); ap.add_argument('--wide', action='store_true')
    a = ap.parse_args()
    build(a.part, a.line1, a.line2, a.seal.split('|'), a.foot, (1280, 720) if a.wide else (1080, 1920)).convert('RGB').save(a.out, quality=92)
    print('OK', a.out)
