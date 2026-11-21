# -*- coding: utf-8 -*-
"""Bộ NỀN (background) cho SHORT 01 — "Đường Tăng: Lãnh đạo hay gánh nặng?".

Vẽ 100% bằng code (PIL), màu phẳng, dọc 9:16 (720x1280) khớp khung Short.
KHÔNG nhân vật — chỉ cảnh nền để người dùng duyệt look.

6 nền theo kịch bản:
  01 hang-yeu          HOOK + Hồi 1 (Đường Tăng bị trói trong hang)
  02 the-chu-toi       Montage "chữ hiện" (nền tối)
  03 cung-nu-nhi-quoc  Hồi 2 (Nữ Nhi Quốc dâng ngai vàng)
  04 khoi-lua          Hồi 2 (điềm tĩnh giữa khói lửa / Hồng Hài Nhi nướng)
  05 duong-thien-ly    Hồi 1 cuối + Hồi 3 chốt (đường xế chiều)
  06 cta-2-phe         CTA (ĐỨC ĐỘ / VÒNG KIM CÔ)

Chạy:  python backgrounds.py
Ra:    ./out/<ma>.png  +  ./out/_contact-sheet.png (xem tất cả)
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
W, H = 720, 1280

# font (tùy chọn — chỉ dùng cho nhãn góc để dễ duyệt)
FD = os.path.join(HERE, '..', '..', '..', 'fonts')
def font(sz, bold=True):
    try:
        return ImageFont.truetype(os.path.join(FD, 'BeVietnamPro-%s.ttf' % ('SemiBold' if bold else 'Medium')), sz)
    except Exception:
        return ImageFont.load_default()


# ───────────────────────── tiện ích ─────────────────────────
def canvas(top, bot):
    """nền phủ dọc 2 màu (dải phẳng, không gradient mịn — hợp style chibi)."""
    im = Image.new('RGBA', (W, H), top + (255,))
    d = ImageDraw.Draw(im)
    bands = 7
    for i in range(bands):
        y0 = int(H * i / bands); y1 = int(H * (i + 1) / bands)
        f = i / (bands - 1)
        col = tuple(int(top[k] + (bot[k] - top[k]) * f) for k in range(3))
        d.rectangle([0, y0, W, y1], fill=col + (255,))
    return im


def vignette(im, a=120, w=100):
    v = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(v).rectangle([0, 0, W, H], outline=(0, 0, 0, a), width=w)
    v = v.filter(ImageFilter.GaussianBlur(40))
    im.alpha_composite(v)
    return im


def tag(im, text):
    """nhãn góc nhỏ để duyệt (không thuộc nền cuối, có thể bỏ)."""
    d = ImageDraw.Draw(im, 'RGBA')
    f = font(22)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([20, 20, 20 + tw + 28, 62], radius=10, fill=(0, 0, 0, 150))
    d.text((34, 27), text, font=f, fill=(255, 255, 255))


# ───────────────────────── 01 · HANG YÊU ─────────────────────────
def hang_yeu():
    im = Image.new('RGBA', (W, H), (40, 30, 36, 255))
    d = ImageDraw.Draw(im)
    # vòm trần tối
    d.rectangle([0, 0, W, int(H * 0.32)], fill=(28, 21, 26, 255))
    # cửa hang sáng mờ (góc trên phải) — nơi 3 đệ tử đánh nhau
    for r, c in [(1.18, (56, 62, 78)), (1.08, (82, 90, 108)), (0.98, (120, 128, 146))]:
        d.ellipse([W * 0.50, -130, W * r, H * 0.33], fill=c + (255,))
    # thạch nhũ rủ từ trần
    random.seed(3)
    for x in range(6, W, 78):
        hgt = random.randint(70, 170)
        d.polygon([(x, 0), (x + 34, 0), (x + 16, hgt)], fill=(50, 39, 44, 255))
        d.polygon([(x + 18, 0), (x + 34, 0), (x + 27, hgt - 30)], fill=(64, 50, 56, 255))
    # vệt tường sẫm 2 bên
    d.polygon([(0, 0), (W * 0.16, 0), (0, H)], fill=(31, 23, 28, 255))
    d.polygon([(W, int(H * 0.34)), (W, H), (W * 0.80, H)], fill=(33, 25, 30, 255))
    # nền đá
    gy = int(H * 0.80)
    d.rectangle([0, gy, W, H], fill=(52, 41, 38, 255))
    d.line([0, gy, W, gy], fill=(32, 25, 23, 255), width=7)
    for _ in range(40):
        x = random.randint(0, W); y = random.randint(gy + 12, H - 10)
        r = random.randint(6, 20)
        d.ellipse([x, y, x + r, y + r * 0.6], fill=(42, 33, 31, 255))
    # vũng nước phản chiếu mờ
    d.ellipse([W * 0.30, H * 0.90, W * 0.70, H * 0.97], fill=(70, 80, 92, 90))
    # 2 đuốc trên tường
    for tx, ty in [(64, int(H * 0.46)), (W - 78, int(H * 0.50))]:
        d.line([tx, ty, tx + 8, ty + 130], fill=(78, 56, 38, 255), width=13)
        d.polygon([(tx - 18, ty), (tx + 26, ty), (tx + 4, ty - 64)], fill=(232, 146, 46, 255))
        d.polygon([(tx - 9, ty), (tx + 17, ty), (tx + 4, ty - 40)], fill=(250, 210, 100, 255))
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([tx - 170, ty - 190, tx + 190, ty + 170], fill=(235, 150, 60, 42))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))
    return vignette(im, a=150, w=120)


# ───────────────────────── 01c · HANG YÊU 1 + gai nhọn + mạng/kén nhện ─────────────────────────
def _mang_nhen(d, cx, cy, R, a0, a1, n=9, col=(206, 206, 218, 55)):
    """mạng nhện ở 1 góc: nan toả + vòng cung."""
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        d.line([cx, cy, cx + R * math.cos(a), cy + R * math.sin(a)], fill=col, width=1)
    for r in range(1, 6):
        rr = R * r / 6
        pts = [(cx + rr * math.cos(a0 + (a1 - a0) * i / n),
                cy + rr * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
        d.line(pts, fill=col, width=1)


def _ken_nhen(d, cx, topy, h, dim=1.0):
    """kén nhện (bọc con mồi) treo bằng tơ: khối trứng + vằn tơ + bóng con mồi."""
    w = h * 0.42
    d.line([cx, 0, cx, topy], fill=(198, 198, 210, int(130 * dim)), width=2)
    body = [(cx, topy), (cx + w * 0.5, topy + h * 0.18), (cx + w * 0.45, topy + h * 0.72),
            (cx, topy + h), (cx - w * 0.45, topy + h * 0.72), (cx - w * 0.5, topy + h * 0.18)]
    col = tuple(int(c * dim) for c in (170, 166, 174))
    d.polygon(body, fill=col + (255,))
    d.line(list(body) + [body[0]], fill=(34, 30, 36), width=3, joint='curve')
    # bóng con mồi bên trong
    d.ellipse([cx - w * 0.22, topy + h * 0.30, cx + w * 0.22, topy + h * 0.64], fill=(60, 54, 62, 130))
    # vằn tơ chéo
    for yy in range(int(topy + 8), int(topy + h - 8), 11):
        t = (yy - topy) / h
        ww = w * (0.5 - abs(t - 0.5) * 0.45)
        d.line([cx - ww, yy, cx + ww, yy + 6], fill=(200, 198, 208, int(150 * dim)), width=2)


def hang_yeu_1b():
    im = hang_yeu()                      # nền bản 1
    d = ImageDraw.Draw(im, 'RGBA')
    OC = (16, 11, 11)
    # kén nhện treo PHÍA SAU (vẽ trước gai để gai đè lên = lùi vào)
    _ken_nhen(d, W * 0.21, H * 0.12, 150, dim=0.78)
    _ken_nhen(d, W * 0.52, H * 0.16, 118, dim=0.66)
    _ken_nhen(d, W * 0.83, H * 0.11, 134, dim=0.74)
    # gai nhọn trần dày (đậm, như hàm răng)
    random.seed(21); xs = -6
    while xs < W:
        w = random.randint(18, 44); ln = random.randint(72, 178)
        d.polygon([(xs, 0), (xs + w, 0), (xs + w * 0.5, ln)], fill=(16, 12, 14, 255))
        d.line([(xs, 0), (xs + w * 0.5, ln)], fill=(72, 60, 62, 170), width=2)   # cạnh sáng trái
        d.line([(xs + w, 0), (xs + w * 0.5, ln)], fill=OC, width=2)
        xs += w + random.randint(2, 16)
    # mạng nhện 2 góc trên
    _mang_nhen(d, 2, 2, 270, 0.06, 1.50)        # góc trái
    _mang_nhen(d, W - 2, 2, 250, 1.64, 3.08)    # góc phải
    return im


# ───────────────────────── 01b · HANG YÊU (bám bố cục Gemini, flat) ─────────────────────────
def _poly_out(d, pts, fill, oc=(20, 13, 11), ow=4):
    d.polygon(pts, fill=fill)
    d.line(list(pts) + [pts[0]], fill=oc, width=ow, joint='curve')


def _thachnhu(d, x, top, w, length, base, light, oc=(20, 13, 11)):
    """1 thạch nhũ rủ xuống: khối cộng 2 tông + viền."""
    _poly_out(d, [(x - w / 2, top), (x + w / 2, top), (x, top + length)], base, oc, 4)
    d.polygon([(x - w / 2, top), (x, top), (x, top + length * 0.82)], fill=light)  # mặt sáng trái


def _stalac(d, x, top, w, length, base, light, oc, ow=4):
    """thạch nhũ rủ: tam giác 2 tông + viền đậm."""
    _poly_out(d, [(x - w / 2, top), (x + w / 2, top), (x, top + length)], base, oc, ow)
    d.polygon([(x - w / 2, top), (x - w * 0.1, top), (x - w * 0.05, top + length * 0.7)], fill=light)


def hang_yeu_v2():
    im = Image.new('RGBA', (W, H), (40, 28, 24, 255))
    d = ImageDraw.Draw(im, 'RGBA')
    RK = (104, 72, 52); RKL = (138, 98, 70); RKD = (70, 48, 36); OC = (26, 16, 13)

    # ── toàn khung là đá nâu ấm ──
    d.rectangle([0, 0, W, H], fill=RK + (255,))
    # ── hốc hang (không gian trong) nâu sẫm vừa, để vách 2 bên nổi ──
    cav = [(W * 0.10, H * 0.16), (W * 0.28, H * 0.09), (W * 0.52, H * 0.07),
           (W * 0.74, H * 0.10), (W * 0.90, H * 0.20), (W * 0.90, H * 0.56),
           (W * 0.5, H * 0.66), (W * 0.10, H * 0.56)]
    _poly_out(d, cav, (58, 40, 34), OC, 6)

    # ── mảng đá facet 2 vách (cel sáng/tối + viền) ──
    facets = [
        ([(0, 0), (W * 0.26, 0), (W * 0.18, H * 0.26), (0, H * 0.33)], RKL),
        ([(0, H * 0.30), (W * 0.19, H * 0.24), (W * 0.22, H * 0.52), (0, H * 0.60)], RK),
        ([(0, H * 0.57), (W * 0.23, H * 0.50), (W * 0.26, H * 0.72), (0, H * 0.80)], RKD),
        ([(W, 0), (W * 0.74, 0), (W * 0.82, H * 0.26), (W, H * 0.30)], RKL),
        ([(W, H * 0.28), (W * 0.81, H * 0.24), (W * 0.80, H * 0.54), (W, H * 0.58)], RK),
        ([(W, H * 0.56), (W * 0.79, H * 0.52), (W * 0.78, H * 0.74), (W, H * 0.80)], RKD),
    ]
    for fc, col in facets:
        _poly_out(d, fc, col, OC, 6)

    # ── trần: dải đá + thạch nhũ nâu ấm rủ dày ──
    _poly_out(d, [(0, 0), (W, 0), (W, H * 0.11), (W * 0.5, H * 0.14), (0, H * 0.11)], RK, OC, 6)
    random.seed(5); xs = 10
    while xs < W - 10:
        w = random.randint(28, 56); ln = random.randint(60, 180)
        _stalac(d, xs + w / 2, random.randint(-4, 8), w, ln, RKD, RKL, OC, 5)
        xs += w + random.randint(6, 24)

    # ── ngách hang XANH (giữa–phải): vòm cung lồng, dải phẳng ──
    pcx, pcy = W * 0.64, H * 0.33
    def arch(sx, sy, k):  # vòm cung (teardrop) quanh tâm
        return [(pcx - sx * k, pcy + sy * 0.2 * k), (pcx - sx * 0.7 * k, pcy - sy * k),
                (pcx, pcy - sy * 1.15 * k), (pcx + sx * 0.7 * k, pcy - sy * k),
                (pcx + sx * k, pcy + sy * 0.2 * k), (pcx + sx * 0.5 * k, pcy + sy * k),
                (pcx, pcy + sy * 1.1 * k), (pcx - sx * 0.5 * k, pcy + sy * k)]
    for k, c in [(1.0, (28, 44, 66)), (0.78, (46, 72, 104)), (0.56, (78, 118, 156)),
                 (0.34, (126, 166, 198))]:
        d.polygon(arch(150, 200, k), fill=c + (255,))
    d.polygon(arch(150, 200, 1.0), fill=None, outline=OC, width=6)
    # lõi sáng nhỏ (1 khối, không blur)
    d.ellipse([pcx - 40, pcy - 30, pcx + 40, pcy + 40], fill=(168, 200, 226, 255))
    # thạch nhũ xanh trong ngách
    for i in range(5):
        tx = pcx - 66 + i * 33
        _stalac(d, tx, pcy - 140 + random.randint(-4, 6), 16, random.randint(44, 96),
                (46, 72, 102), (156, 190, 216), OC, 3)

    # ── sàn đá ──
    gy = int(H * 0.63)
    _poly_out(d, [(0, gy + 8), (W, gy - 4), (W, H * 0.80), (0, H * 0.83)], (84, 58, 46), OC, 6)
    random.seed(9)
    for _ in range(22):
        x = random.randint(0, W); y = random.randint(gy + 14, int(H * 0.80))
        r = random.randint(8, 20)
        d.ellipse([x, y, x + r, y + r * 0.5], fill=(64, 44, 35, 255))

    # ── vũng nước phản chiếu (foreground), dải phẳng ──
    pool = [(W * 0.14, H * 0.83), (W * 0.42, H * 0.795), (W * 0.68, H * 0.805),
            (W * 0.88, H * 0.845), (W * 0.82, H * 0.945), (W * 0.5, H * 0.975),
            (W * 0.20, H * 0.93)]
    _poly_out(d, pool, (34, 56, 80), OC, 6)
    for i, c in enumerate([(44, 70, 98), (64, 98, 130), (92, 132, 166)]):
        d.polygon([(W * (0.22 + i * 0.03), H * (0.845 + i * 0.016)),
                   (W * (0.78 - i * 0.03), H * (0.845 + i * 0.016)),
                   (W * (0.72 - i * 0.03), H * (0.90 + i * 0.012)),
                   (W * (0.28 + i * 0.03), H * (0.90 + i * 0.012))], fill=c + (255,))
    # phản chiếu ngách xanh + ánh đuốc (vệt dọc)
    d.line([pcx * 0.92, H * 0.85, pcx * 0.92, H * 0.95], fill=(150, 186, 214, 150), width=10)
    d.line([W * 0.42, H * 0.85, W * 0.40, H * 0.95], fill=(236, 150, 60, 150), width=9)

    # ── 2 đuốc bên trái (cao + giữa thấp) — quầng mờ nhẹ khớp map 1&3 ──
    for tx, ty in [(W * 0.11, int(H * 0.40)), (W * 0.40, int(H * 0.46))]:
        d.line([tx, ty, tx + 5, ty + 86], fill=(66, 44, 30, 255), width=11)
        _poly_out(d, [(tx - 15, ty), (tx + 21, ty), (tx + 3, ty - 54)], (236, 146, 46), (150, 70, 20), 3)
        d.polygon([(tx - 7, ty), (tx + 13, ty), (tx + 3, ty - 32)], fill=(250, 212, 104, 255))
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([tx - 70, ty - 80, tx + 80, ty + 70], fill=(240, 160, 66, 46))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(30)))

    return vignette(im, a=140, w=100)


# ───────────────────────── 02 · THẺ CHỮ NỀN TỐI ─────────────────────────
def the_chu_toi():
    im = canvas((26, 20, 30), (16, 12, 18))
    d = ImageDraw.Draw(im, 'RGBA')
    # lưới mờ gợi "hồ sơ"
    for i in range(0, H, 46):
        d.line([0, i, W, i], fill=(40, 32, 44, 70), width=1)
    for i in range(0, W, 46):
        d.line([i, 0, i, H], fill=(40, 32, 44, 50), width=1)
    # vòng tròn ánh sáng trung tâm (đèn rọi hồ sơ)
    spot = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(spot).ellipse([W * 0.12, H * 0.22, W * 0.88, H * 0.74],
                                 fill=(120, 96, 150, 46))
    im.alpha_composite(spot.filter(ImageFilter.GaussianBlur(90)))
    # vệt mực đỏ gợi "đóng dấu / cảnh báo"
    d.rounded_rectangle([W * 0.60, H * 0.08, W * 0.92, H * 0.15], radius=8,
                        outline=(176, 60, 56, 130), width=5)
    return vignette(im, a=170, w=130)


# ───────────────────────── 03 · CUNG ĐIỆN NỮ NHI QUỐC ─────────────────────────
def cung_nu_nhi_quoc():
    im = canvas((120, 44, 60), (70, 24, 40))  # tường son đỏ
    d = ImageDraw.Draw(im, 'RGBA')
    # sàn gạch phối cảnh
    fy = int(H * 0.70)
    d.rectangle([0, fy, W, H], fill=(60, 30, 34, 255))
    for i in range(-6, 7):
        x = W * 0.5 + i * 120
        d.line([W * 0.5, fy, x, H], fill=(96, 52, 54, 180), width=3)
    for j, yy in enumerate(range(fy + 24, H, 56)):
        d.line([0, yy, W, yy], fill=(96, 52, 54, 150), width=2)
    # thảm đỏ chính giữa chạy tới ngai
    d.polygon([(W * 0.40, fy), (W * 0.60, fy), (W * 0.74, H), (W * 0.26, H)], fill=(168, 46, 48, 255))
    d.polygon([(W * 0.40, fy), (W * 0.60, fy), (W * 0.74, H), (W * 0.26, H)],
              outline=(226, 190, 110, 255), width=4)
    # bậc thềm + ngai vàng phía xa
    d.rectangle([W * 0.30, fy - 70, W * 0.70, fy], fill=(150, 40, 44, 255))
    d.rectangle([W * 0.34, fy - 118, W * 0.66, fy - 60], fill=(120, 32, 38, 255))
    # ngai
    tx0, tx1, ty = W * 0.42, W * 0.58, fy - 118
    d.rounded_rectangle([tx0, ty - 110, tx1, ty], radius=14, fill=(196, 150, 56, 255))
    d.rounded_rectangle([tx0, ty - 160, tx1, ty - 96], radius=18, fill=(214, 168, 70, 255))
    d.ellipse([W * 0.47, ty - 190, W * 0.53, ty - 150], fill=(236, 196, 96, 255))  # chóp ngai
    # cột son 2 bên + xà vàng
    for cx in [W * 0.12, W * 0.88]:
        d.rectangle([cx - 34, 0, cx + 34, fy], fill=(150, 36, 40, 255))
        d.rectangle([cx - 34, 0, cx + 34, fy], outline=(214, 170, 90, 255), width=4)
        d.rectangle([cx - 46, int(H * 0.10), cx + 46, int(H * 0.16)], fill=(206, 160, 72, 255))
    # xà ngang trần vàng
    d.rectangle([0, int(H * 0.08), W, int(H * 0.12)], fill=(196, 150, 56, 255))
    d.rectangle([0, int(H * 0.12), W, int(H * 0.135)], fill=(150, 110, 44, 255))
    # 2 đèn lồng đỏ treo
    for lx in [W * 0.26, W * 0.74]:
        ly = int(H * 0.22)
        d.line([lx, int(H * 0.135), lx, ly - 30], fill=(60, 30, 30, 255), width=3)
        d.ellipse([lx - 34, ly - 30, lx + 34, ly + 54], fill=(214, 54, 48, 255))
        d.ellipse([lx - 34, ly - 30, lx + 34, ly + 54], outline=(236, 196, 96, 255), width=3)
        d.rectangle([lx - 14, ly + 50, lx + 14, ly + 70], fill=(226, 190, 110, 255))
        glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([lx - 90, ly - 70, lx + 90, ly + 110], fill=(240, 120, 80, 50))
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(26)))
    return vignette(im, a=120, w=110)


# ───────────────────────── 04 · KHÓI LỬA ─────────────────────────
def khoi_lua():
    im = canvas((120, 40, 24), (40, 16, 14))  # đỏ cam → sẫm
    d = ImageDraw.Draw(im, 'RGBA')
    random.seed(7)
    # khói cuộn phía trên (đám xám mờ)
    smoke = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for _ in range(26):
        x = random.randint(-40, W + 40); y = random.randint(-40, int(H * 0.45))
        r = random.randint(60, 150)
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(40, 30, 34, 60))
    im.alpha_composite(smoke.filter(ImageFilter.GaussianBlur(28)))
    # nền đất than
    gy = int(H * 0.78)
    d.rectangle([0, gy, W, H], fill=(46, 22, 18, 255))
    # đống lửa lớn dưới giữa
    cx, base = W * 0.5, int(H * 0.86)
    fire = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fire)
    for r, c in [(1.0, (170, 50, 24)), (0.72, (226, 120, 36)), (0.46, (248, 196, 86)), (0.24, (255, 240, 170))]:
        hh = int(240 * r); ww = int(150 * r)
        fd.polygon([(cx - ww, base), (cx + ww, base),
                    (cx + ww * 0.3, base - hh * 0.7), (cx, base - hh),
                    (cx - ww * 0.3, base - hh * 0.7)], fill=c + (255,))
    im.alpha_composite(fire)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - 320, base - 420, cx + 320, base + 60], fill=(250, 140, 50, 70))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
    # tàn lửa bay
    for _ in range(60):
        x = random.randint(int(cx - 220), int(cx + 220)); y = random.randint(int(H * 0.45), base)
        r = random.randint(2, 5)
        d.ellipse([x, y, x + r, y + r], fill=(255, 206, 110, random.randint(120, 220)))
    # củi than
    for i in range(-2, 3):
        d.line([cx + i * 46 - 30, base + 4, cx + i * 46 + 30, base - 10],
               fill=(30, 18, 16, 255), width=12)
    return vignette(im, a=150, w=120)


# ───────────────────────── 05 · ĐƯỜNG THIÊN LÝ XẾ CHIỀU ─────────────────────────
def duong_thien_ly():
    im = canvas((248, 212, 150), (236, 176, 120))  # trời ấm xế chiều
    d = ImageDraw.Draw(im, 'RGBA')
    # mặt trời mờ
    sx, sy = W * 0.70, H * 0.18
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([sx - 150, sy - 150, sx + 150, sy + 150], fill=(255, 238, 180, 110))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
    d.ellipse([sx - 60, sy - 60, sx + 60, sy + 60], fill=(255, 244, 198, 255))
    # mây dải phẳng
    for mx, my, mw in [(W * 0.2, H * 0.12, 180), (W * 0.55, H * 0.26, 220), (W * 0.1, H * 0.30, 150)]:
        d.ellipse([mx - mw, my - 22, mx + mw, my + 22], fill=(255, 232, 196, 180))
    # đồi xa nhiều lớp
    gy = int(H * 0.60)
    for cy, col in [(gy - 70, (196, 170, 118)), (gy - 30, (168, 150, 104)), (gy + 2, (142, 128, 86))]:
        for hx in range(-200, W + 200, 300):
            d.ellipse([hx, cy - 80, hx + 300, cy + 120], fill=col + (255,))
    # đất
    d.rectangle([0, gy, W, H], fill=(150, 126, 88, 255))
    d.line([0, gy, W, gy], fill=(120, 98, 66, 255), width=5)
    # cây xa (bóng phẳng)
    for tx in [W * 0.12, W * 0.86, W * 0.30]:
        th = random.Random(int(tx)).randint(70, 120)
        d.line([tx, gy, tx, gy - th], fill=(96, 78, 54, 255), width=7)
        d.ellipse([tx - 36, gy - th - 44, tx + 36, gy - th + 20], fill=(118, 132, 78, 255))
    # lối mòn hình thang (xa → gần)
    d.polygon([(W * 0.43, gy), (W * 0.57, gy), (W * 0.80, H), (W * 0.20, H)], fill=(182, 158, 116, 255))
    d.polygon([(W * 0.43, gy), (W * 0.57, gy), (W * 0.80, H), (W * 0.20, H)],
              outline=(150, 128, 92, 200), width=3)
    for yy in range(gy + 24, H, 92):
        t = (yy - gy) / (H - gy)
        w = 6 + 16 * t
        d.line([W * 0.5 - w, yy, W * 0.5 + w, yy], fill=(150, 128, 94, 255), width=int(3 + 5 * t))
    return vignette(im, a=90, w=90)


# ───────────────────────── 06 · CTA 2 PHE ─────────────────────────
def cta_2_phe():
    im = Image.new('RGBA', (W, H), (24, 20, 28, 255))
    d = ImageDraw.Draw(im, 'RGBA')
    # chia đôi màn: trái ấm (đức độ) / phải lạnh (vòng kim cô)
    d.polygon([(0, 0), (W * 0.54, 0), (W * 0.46, H), (0, H)], fill=(150, 96, 40, 255))
    d.polygon([(W * 0.54, 0), (W, 0), (W, H), (W * 0.46, H)], fill=(44, 74, 104, 255))
    # dải phân cách sáng
    d.line([(W * 0.54, 0), (W * 0.46, H)], fill=(248, 236, 200, 230), width=6)
    # họa tiết nhẹ 2 bên
    for i in range(6):
        y = int(H * (0.12 + i * 0.14))
        d.arc([W * 0.02, y - 40, W * 0.36, y + 40], 300, 60, fill=(236, 200, 120, 60), width=3)
        d.arc([W * 0.64, y - 40, W * 0.98, y + 40], 120, 240, fill=(150, 190, 230, 60), width=3)
    # 2 khung nút trống (chữ thêm ở bước dựng video)
    d.rounded_rectangle([W * 0.08, H * 0.70, W * 0.44, H * 0.80], radius=18,
                        fill=(214, 168, 70, 255), outline=(255, 240, 200, 255), width=4)
    d.rounded_rectangle([W * 0.56, H * 0.70, W * 0.92, H * 0.80], radius=18,
                        fill=(70, 120, 170, 255), outline=(210, 232, 255, 255), width=4)
    return vignette(im, a=120, w=100)


# ───────────────────────── XUẤT ─────────────────────────
SCENES = [
    ('01-hang-yeu', 'HOOK · Hồi 1 — Hang yêu', hang_yeu),
    ('02-the-chu-toi', 'Montage — Thẻ chữ nền tối', the_chu_toi),
    ('03-cung-nu-nhi-quoc', 'Hồi 2 — Cung Nữ Nhi Quốc', cung_nu_nhi_quoc),
    ('04-khoi-lua', 'Hồi 2 — Khói lửa', khoi_lua),
    ('05-duong-thien-ly', 'Hồi 1/3 — Đường thiên lý xế chiều', duong_thien_ly),
    ('06-cta-2-phe', 'CTA — Đức độ / Vòng kim cô', cta_2_phe),
]


def main():
    thumbs = []
    for ma, nhan, fn in SCENES:
        im = fn()
        clean = im.copy()
        clean.convert('RGB').save(os.path.join(OUT, ma + '.png'))
        # bản có nhãn để duyệt
        lab = im.copy(); tag(lab, nhan)
        thumbs.append((nhan, lab))
        print('✓', ma)
    # contact sheet 2 cột x 3 hàng
    cols, rows = 2, 3
    tw, th = W // 3, H // 3
    pad = 16
    sheet = Image.new('RGB', (cols * tw + pad * (cols + 1), rows * th + pad * (rows + 1)), (18, 16, 20))
    for i, (nhan, lab) in enumerate(thumbs):
        r, c = divmod(i, cols)
        t = lab.convert('RGB').resize((tw, th), Image.LANCZOS)
        sheet.paste(t, (pad + c * (tw + pad), pad + r * (th + pad)))
    sheet.save(os.path.join(OUT, '_contact-sheet.png'))
    print('→', os.path.join(OUT, '_contact-sheet.png'))


if __name__ == '__main__':
    main()
