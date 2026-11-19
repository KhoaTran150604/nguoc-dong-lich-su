"""Bảng chỉ số kèm ảnh: nhân vật + nhãn mã (A1, B7…) chỉ vào đúng bộ phận + bảng giá trị bên phải.

LUẬT: mỗi lần đưa thông số cho người dùng, LUÔN xuất ảnh này (số lấy trực tiếp từ bảng P → luôn khớp hình).
Dùng:  sheet(img, groups, title, out_path)
  groups = [('A. Luật chung', [(mã, (x, y) hoặc None, 'mô tả = giá trị'), ...]), ...]
  (x, y) là điểm trên ảnh nhân vật để kéo đường chỉ; None = chỉ ghi trong bảng.
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FB = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')
FR = os.path.join(ROOT, 'fonts', 'BeVietnamPro-Regular.ttf')
COL = {'A': (90, 90, 90), 'B': (214, 48, 49), 'C': (40, 110, 200), 'D': (30, 140, 80), 'E': (150, 70, 170)}
GUT = 110          # lề hai bên ảnh nhân vật (chỗ đặt nhãn)
PANEL = 860


def _spread(ys, lo, hi, gap):
    """Dàn các nhãn theo y để không chồng nhau."""
    ys = sorted(ys, key=lambda t: t[0])
    out, last = [], lo - gap
    for y, k in ys:
        y = max(y, last + gap)
        out.append([y, k])
        last = y
    over = (out[-1][0] - hi) if out else 0
    if over > 0:
        for i in range(len(out) - 1, -1, -1):
            out[i][0] -= over
            if i and out[i][0] - out[i - 1][0] >= gap:
                break
            over = max(0, out[i - 1][0] + gap - out[i][0]) if i else 0
    return out


def sheet(img, groups, title, out_path, note=''):
    iw, ih = img.size
    W, H = GUT + iw + GUT + PANEL, max(ih, 1000)
    sh = Image.new('RGB', (W, H), (255, 255, 255))
    sh.paste(img.convert('RGB'), (GUT, 0))
    d = ImageDraw.Draw(sh)
    fb, fs, fr, ft = (ImageFont.truetype(FB, 17), ImageFont.truetype(FB, 15),
                      ImageFont.truetype(FR, 19), ImageFont.truetype(FB, 30))
    d.rectangle([0, 0, GUT - 1, H], fill=(250, 249, 246))
    d.rectangle([GUT + iw, 0, GUT * 2 + iw - 1, H], fill=(250, 249, 246))

    # --- nhãn trên ảnh ---
    pts = [(code, (GUT + p[0], p[1])) for _, items in groups for code, p, _ in items if p]
    mid = GUT + iw / 2
    for side, xs in (('L', GUT / 2), ('R', GUT * 1.5 + iw)):
        sel = [(p[1], (c, p)) for c, p in pts if (p[0] < mid) == (side == 'L')]
        for y, (c, p) in _spread(sel, 30, H - 30, 38):
            col = COL.get(c[0], (0, 0, 0))
            d.line([(xs, y), p], fill=col, width=2)
            d.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=col, outline=(255, 255, 255), width=2)
            d.rounded_rectangle([xs - 26, y - 15, xs + 26, y + 15], 8, fill=col)
            d.text((xs, y), c, font=fb, fill=(255, 255, 255), anchor='mm')

    # --- bảng bên phải ---
    x0 = GUT * 2 + iw + 26
    y = 26
    d.text((x0, y), title, font=ft, fill=(30, 30, 30))
    y += 48
    if note:
        d.text((x0, y), note, font=fs, fill=(120, 120, 120))
        y += 30
    for gname, items in groups:
        col = COL.get(gname[0], (0, 0, 0))
        d.text((x0, y), gname, font=fb, fill=col)
        y += 28
        for code, _, txt in items:
            d.rounded_rectangle([x0, y, x0 + 44, y + 24], 6, fill=col)
            d.text((x0 + 22, y + 12), code, font=fs, fill=(255, 255, 255), anchor='mm')
            d.text((x0 + 56, y + 1), txt, font=fr, fill=(35, 35, 35))
            y += 30
        y += 10
    sh.save(out_path, quality=92)
    return sh
