"""Thumbnail E2 – Bạch Đằng 938 (đồ họa riêng, không lấy hình trong video).

Chạy:  python scripts/thumbnail/e2.py [-o out.jpg]
Bố cục: nhãn series góc trái · tiêu đề SÔNG BẠCH ĐẰNG · hàng cọc nhô lên khi nước rút
        · thẻ HOẰNG THÁO bị gạch chéo đỏ.
"""
import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "fonts"
S = 2  # vẽ gấp đôi rồi thu nhỏ cho nét mịn
W, H = 1280 * S, 720 * S

MUC = (20, 17, 15)
DONG = (201, 162, 74)
DONG_SANG = (243, 210, 122)
DO = (179, 38, 30)
KEM = (242, 230, 204)
NUOC_TOI = (14, 38, 48)
NUOC = (28, 72, 86)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size * S)


def text_outline(d, xy, txt, f, fill, stroke=6, stroke_fill=MUC, anchor="la"):
    d.text(xy, txt, font=f, fill=fill, stroke_width=stroke * S,
           stroke_fill=stroke_fill, anchor=anchor)


def nen(img):
    """Nền mực có vầng sáng đồng phía sau tiêu đề."""
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(MUC[i] * (1 - t * 0.3) + NUOC_TOI[i] * t * 0.3) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([-200 * S, -260 * S, 760 * S, 420 * S], fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(160 * S))
    img.paste(Image.new("RGB", (W, H), (120, 84, 30)), (0, 0), glow)


def song(img, top):
    """Mặt sông: nước rút, sóng ngang."""
    d = ImageDraw.Draw(img)
    for y in range(top, H):
        t = (y - top) / (H - top)
        c = tuple(int(NUOC[i] * (1 - t) + NUOC_TOI[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    rnd = random.Random(7)
    for k in range(70):
        y = rnd.randint(top + 10 * S, H - 10 * S)
        x = rnd.randint(-100 * S, W)
        L = rnd.randint(60, 180) * S
        pts = [(x + i * S * 4, y + math.sin(i / 4) * 3 * S) for i in range(L // (4 * S))]
        d.line(pts, fill=(70, 120, 132), width=2 * S)
    # vạch mực nước cũ (nước đã rút xuống)
    y0 = top - 70 * S
    d.line([(0, y0), (W, y0)], fill=(90, 140, 150), width=2 * S)
    for x in range(0, W, 36 * S):
        d.line([(x, y0), (x + 18 * S, y0)], fill=MUC, width=3 * S)


def coc(d, x, base, h, w, nghieng):
    """Một cọc gỗ đầu bịt sắt nhọn."""
    dx = nghieng * h
    top = base - h
    tip_h = w * 1.6
    # thân gỗ
    d.polygon([(x - w / 2, base), (x + w / 2, base),
               (x + w / 2 + dx, top + tip_h), (x - w / 2 + dx, top + tip_h)],
              fill=(92, 60, 34), outline=MUC, width=3 * S)
    # vân gỗ
    d.line([(x, base), (x + dx, top + tip_h)], fill=(120, 82, 46), width=2 * S)
    # mũi sắt
    d.polygon([(x - w / 2 + dx, top + tip_h), (x + w / 2 + dx, top + tip_h),
               (x + dx * 1.04, top)], fill=(150, 156, 160), outline=MUC, width=3 * S)
    d.line([(x + dx * 1.02 - w * 0.15, top + tip_h * 0.75), (x + dx * 1.04, top + 4 * S)],
           fill=(225, 230, 232), width=2 * S)


def hang_coc(img, mat_nuoc):
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    x = 40 * S
    while x < 860 * S:
        h = rnd.randint(105, 150) * S
        w = rnd.randint(26, 34) * S
        coc(d, x, mat_nuoc + 30 * S, h, w, rnd.uniform(-0.12, 0.18))
        x += rnd.randint(52, 70) * S
    # nước vỗ quanh chân cọc
    for k in range(40):
        cx = rnd.randint(0, 840) * S
        d.ellipse([cx - 30 * S, mat_nuoc + 18 * S, cx + 30 * S, mat_nuoc + 34 * S],
                  outline=(150, 190, 196), width=2 * S)


def tuong(img, box):
    """Thẻ HOẰNG THÁO: bóng tướng Nam Hán + dấu X đỏ."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=18 * S, fill=(222, 200, 156), outline=DONG, width=6 * S)
    d.rounded_rectangle([x0 + 14 * S, y0 + 14 * S, x1 - 14 * S, y1 - 14 * S],
                        radius=12 * S, outline=(160, 120, 60), width=3 * S)
    cx = (x0 + x1) / 2
    # bóng người: vai, đầu, mũ trụ, chùm lông
    sil = (16, 12, 10)
    vai_y = y1 - 140 * S
    d.polygon([(x0 + 40 * S, y1 - 80 * S), (cx - 70 * S, vai_y), (cx + 70 * S, vai_y),
               (x1 - 40 * S, y1 - 80 * S)], fill=sil)
    d.rectangle([x0 + 40 * S, y1 - 82 * S, x1 - 40 * S, y1 - 70 * S], fill=sil)
    d.rectangle([cx - 26 * S, vai_y - 40 * S, cx + 26 * S, vai_y + 6 * S], fill=sil)
    d.ellipse([cx - 58 * S, vai_y - 150 * S, cx + 58 * S, vai_y - 22 * S], fill=sil)
    d.pieslice([cx - 70 * S, vai_y - 175 * S, cx + 70 * S, vai_y - 55 * S], 180, 360, fill=sil)
    d.polygon([(cx - 90 * S, vai_y - 112 * S), (cx + 90 * S, vai_y - 112 * S),
               (cx + 70 * S, vai_y - 98 * S), (cx - 70 * S, vai_y - 98 * S)], fill=sil)
    d.line([(cx, vai_y - 175 * S), (cx, vai_y - 215 * S)], fill=sil, width=8 * S)
    d.polygon([(cx, vai_y - 215 * S), (cx - 28 * S, vai_y - 245 * S), (cx + 6 * S, vai_y - 230 * S),
               (cx + 30 * S, vai_y - 250 * S), (cx + 10 * S, vai_y - 205 * S)], fill=DO)
    # tên
    f = font("PlayfairDisplay-ExtraBold.ttf", 40)
    d.rectangle([x0 + 6 * S, y1 - 72 * S, x1 - 6 * S, y1 - 8 * S], fill=MUC)
    d.text((cx, y1 - 40 * S), "HOẰNG THÁO", font=f, fill=DONG_SANG, anchor="mm")
    # dấu X đỏ kiểu nét cọ
    pad = 26 * S
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for (a, b) in [((x0 + pad, y0 + pad), (x1 - pad, y1 - pad - 40 * S)),
                   ((x1 - pad, y0 + pad), (x0 + pad, y1 - pad - 40 * S))]:
        ld.line([a, b], fill=MUC + (235,), width=30 * S)
        ld.line([a, b], fill=DO + (240,), width=22 * S)
    img.paste(layer, (0, 0), layer)


def thuyen_chim(img, x, y):
    """Mũi thuyền Nam Hán chúi xuống nước, buồm đỏ."""
    d = ImageDraw.Draw(img)
    d.polygon([(x - 120 * S, y - 40 * S), (x + 110 * S, y - 90 * S), (x + 140 * S, y + 10 * S),
               (x - 90 * S, y + 40 * S)], fill=(70, 46, 28), outline=MUC, width=4 * S)
    d.line([(x + 10 * S, y - 60 * S), (x + 60 * S, y - 230 * S)], fill=MUC, width=8 * S)
    d.polygon([(x + 20 * S, y - 90 * S), (x + 58 * S, y - 222 * S), (x + 150 * S, y - 190 * S),
               (x + 120 * S, y - 70 * S)], fill=DO, outline=MUC, width=4 * S)
    for k in range(1, 4):
        t = k / 4
        d.line([(x + 20 * S + 38 * S * t, y - 90 * S - 132 * S * t),
                (x + 120 * S + 30 * S * t, y - 70 * S - 120 * S * t)], fill=(120, 24, 20), width=3 * S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=str(
        ROOT / "video/nguoc-dong-su-viet/938-Ngo-Quyen/thumbnail-E2.jpg"))
    a = ap.parse_args()

    img = Image.new("RGB", (W, H), MUC)
    nen(img)
    mat_nuoc = 600 * S
    song(img, mat_nuoc)
    thuyen_chim(img, 700 * S, mat_nuoc + 20 * S)
    hang_coc(img, mat_nuoc)
    d = ImageDraw.Draw(img)

    # nhãn series
    f_tag = font("BeVietnamPro-SemiBold.ttf", 30)
    tag = "NGƯỢC DÒNG SỬ VIỆT #1"
    tw = d.textlength(tag, font=f_tag)
    d.rounded_rectangle([40 * S, 34 * S, 40 * S + tw + 44 * S, 34 * S + 58 * S],
                        radius=29 * S, fill=DO, outline=DONG_SANG, width=3 * S)
    d.text((40 * S + 22 * S, 34 * S + 29 * S), tag, font=f_tag, fill=KEM, anchor="lm")

    # tiêu đề
    f_big = font("PlayfairDisplay-ExtraBold.ttf", 118)
    text_outline(d, (40 * S, 112 * S), "SÔNG", f_big, DONG_SANG, stroke=8)
    text_outline(d, (40 * S, 238 * S), "BẠCH ĐẰNG", f_big, DONG_SANG, stroke=8)
    f_mid = font("BeVietnamPro-SemiBold.ttf", 46)
    text_outline(d, (46 * S, 394 * S), "NĂM 938", f_mid, KEM, stroke=5)

    # nhãn CỌC chỉ vào hàng cọc
    f_coc = font("PlayfairDisplay-ExtraBold.ttf", 64)
    cx, cy = 470 * S, 418 * S
    d.rounded_rectangle([cx - 90 * S, cy - 44 * S, cx + 90 * S, cy + 40 * S], radius=12 * S,
                        fill=KEM, outline=MUC, width=4 * S)
    d.text((cx, cy - 2 * S), "CỌC!", font=f_coc, fill=DO, anchor="mm")
    d.polygon([(cx - 16 * S, cy + 38 * S), (cx + 16 * S, cy + 38 * S), (cx, cy + 66 * S)], fill=KEM, outline=MUC)
    d.line([(cx - 15 * S, cy + 38 * S), (cx + 15 * S, cy + 38 * S)], fill=KEM, width=5 * S)

    tuong(img, (900 * S, 70 * S, 1240 * S, 520 * S))

    # chân trang nhỏ
    f_s = font("BeVietnamPro-Regular.ttf", 20)
    d.text((W - 24 * S, H - 18 * S), "Minh họa", font=f_s, fill=(170, 190, 196), anchor="rs")

    out = img.resize((1280, 720), Image.LANCZOS)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.save(a.out, quality=92)
    print(a.out)


if __name__ == "__main__":
    main()
