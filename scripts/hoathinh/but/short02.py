# -*- coding: utf-8 -*-
"""SHORT 02 — "Trư Bát Giới: Nguyên soái nhà Trời hay kẻ ăn hại?" — dọc 9:16 (720x1280), 24fps.

Chuẩn theo short01.py (giữ NGUYÊN tên helper để storyboard02 import lại). Cú lật:
cào cỏ 5.048 cân → Thiên Bồng Nguyên Soái 8 vạn thủy quân → ghẹo Hằng Nga bị đày → dưới nước
thắng Ngộ Không → thành Phật phong Tịnh Đàn Sứ Giả (ăn cả đời). CTA chia phe.

Chạy:  PYTHONUTF8=1 HF_HUB_DISABLE_XET=1 python scripts/hoathinh/but/short02.py
Ra:    du-an/tay-du-ky/output/short/short02-full.mp4
"""
import os
import subprocess
import sys
import math
import random

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import soundfile as sf
import scipy.signal as S
import ve as V

W, H = 720, 1280
FPS = 24
SR = 44100
OUTDIR = os.path.join(ROOT, 'du-an', 'tay-du-ky', 'output', 'short')
WORK = os.path.join(ROOT, 'build', 'thu-hoathinh', 'short02')
ASSET = os.path.join(ROOT, 'assets', 'nhan-vat', 'but')
FD = os.path.join(ROOT, 'fonts')

def font(sz, bold=True):
    return ImageFont.truetype(os.path.join(FD, 'BeVietnamPro-%s.ttf' % ('SemiBold' if bold else 'Medium')), sz)

F_TITLE = font(52); F_BIG = font(44); F_SUB = font(30, False); F_LAB = font(26); F_SMALL = font(23, False)

# màu chữ trên nền sáng: KEM (không nâu đậm — bị chìm)
KEM = (255, 240, 205)

# ───────────────────────── KỊCH BẢN (câu dẫn, người nói, shot) ─────────────────────────
# speaker: 'dan'=giahuy · 'bat'=quangminh (Bát Giới) · 'tb'=huuduc (Thiên Bồng) · 'ngo'=tiendat (Ngộ Không)
LINES = [
    ('dan', 'Cả Tây Du gọi hắn là kẻ ăn hại: tham ăn, mê ngủ, gặp yêu quái là đòi giải tán.', 'ngunga'),
    ('dan', 'Nhưng cái cào cỏ hắn vác, nặng hơn năm nghìn cân. Tám trăm năm trước, hắn chỉ huy cả đạo quân nhà Trời.', 'hooklat'),
    ('dan', 'Lười thì khó ai bằng: việc nặng đùn sư đệ, ăn thì giành phần hơn.', 'luoi'),
    ('bat', 'Thôi đi sư huynh! Chia hành lý, lão Trư về Cao Lão Trang với vợ cho rồi!', 'doigiaitan'),
    ('dan', 'Nhưng khoan. Cái cào ấy do Thái Thượng Lão Quân rèn, nặng đúng bằng số ngày đi thỉnh kinh.', 'dinhba'),
    ('dan', 'Vì hắn từng là Thiên Bồng Nguyên Soái, thống lĩnh thủy quân Thiên Hà.', 'thienbong'),
    ('tb', 'Nàng Hằng Nga… lại đây với bản soái một chén nào…', 'gheohang'),
    ('dan', 'Chỉ một lần say rượu ghẹo Hằng Nga, hắn mất tất cả: bị đày xuống trần, đầu thai nhầm vào bụng lợn.', 'bibat'),
    ('ngo', 'Lão Trư… xuống nước thì ta thua ngươi. Lần này thôi đấy!', 'duoinuoc'),
    ('dan', 'Đừng tưởng hắn hết thời. Dưới nước, đến Ngộ Không cũng phải chịu thua, giỏi nhất nhì cả đoàn.', 'duoinuoc2'),
    ('dan', 'Còn cái kết? Thành Phật, phong Tịnh Đàn Sứ Giả, hưởng đồ cúng thiên hạ. Kẻ ham ăn, được Phật cho ăn cả đời.', 'tinhdan'),
    ('dan', 'Vậy hắn là gì? Kẻ ăn hại tham lười sợ? Hay kẻ duy nhất dám đòi về nhà, mà mười bốn năm chưa từng về thật?', 'chot'),
    ('dan', 'Kẻ ăn hại, hay người thật nhất Tây Du? Chọn phe đi, đừng ngồi im như Sa Tăng!', 'cta'),
]
SUBS = [t for _, t, _ in LINES]

# ───────────────────────── SPRITE (nhân vật Bộ Bút) ─────────────────────────
_cache = {}
def sprite(ma, bc='hien', mi='cuoi', h=460, flip=False, drop=()):
    key = (ma, bc, mi, h, flip, drop)
    if key in _cache:
        return _cache[key]
    NV = V.nap(ma); NV['mat']['bieu_cam'] = bc; NV['mat']['mieng'] = mi
    for dk in drop:
        NV.pop(dk, None)
    tmp = os.path.join(WORK, '_%s_%s_%s.png' % (ma, bc, mi))
    V.ve(NV, tmp, canvas=(800, 1000), nen=None)
    im = Image.open(tmp).convert('RGBA'); im = im.crop(im.getbbox())
    s = h / im.height
    im = im.resize((max(1, round(im.width * s)), h), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    try: os.remove(tmp)
    except OSError: pass
    _cache[key] = im
    return im

def silhouette(im, col=(26, 22, 34)):
    a = im.split()[-1]
    solid = Image.new('RGBA', im.size, col + (255,))
    solid.putalpha(a)
    return solid

def paste_mid(bg, spr, cx, by, sc=1.0):
    if sc != 1.0:
        spr = spr.resize((max(1, round(spr.width * sc)), max(1, round(spr.height * sc))), Image.LANCZOS)
    x = int(cx - spr.width / 2); y = int(by - spr.height)
    bg.alpha_composite(spr, (x, y))

def soft_shadow(bg, cx, by, w=120, a=90):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - w, by - 14, cx + w, by + 16], fill=(10, 8, 6, a))
    bg.alpha_composite(sh)

# ───────────────────────── NỀN ─────────────────────────
def bg_duongxa(off=0.0):
    """Đường thiên lý lúc xế chiều."""
    im = Image.new('RGBA', (W, H), (236, 200, 150, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.34)], fill=(242, 206, 150, 255))
    d.rectangle([0, int(H * 0.34), W, int(H * 0.40)], fill=(236, 188, 138, 255))
    d.ellipse([W * 0.62, H * 0.12, W * 0.82, H * 0.24], fill=(250, 232, 180, 255))
    gy = int(H * 0.62)
    for j, (cy, col) in enumerate([(gy - 40, (176, 170, 132)), (gy - 14, (150, 150, 110))]):
        ox = (off * (0.3 + j * 0.3)) % 320
        for hx in range(-320, W + 320, 320):
            d.ellipse([hx - ox, cy - 70, hx - ox + 300, cy + 90], fill=col + (255,))
    d.rectangle([0, gy, W, H], fill=(150, 128, 92, 255))
    d.line([0, gy, W, gy], fill=(120, 100, 70, 255), width=5)
    d.polygon([(W * 0.42, gy), (W * 0.58, gy), (W * 0.78, H), (W * 0.22, H)], fill=(178, 156, 116, 255))
    ox = (off * 0.9) % 90
    for yy in range(gy + 20, H, 90):
        t = (yy - gy) / (H - gy)
        w = 6 + 14 * t
        d.line([W * 0.5 - w, yy - ox, W * 0.5 + w, yy - ox], fill=(150, 130, 96, 255), width=int(3 + 4 * t))
    return im

def bg_toi(vign=True):
    im = Image.new('RGBA', (W, H), (21, 17, 24, 255))
    d = ImageDraw.Draw(im)
    for i in range(0, H, 48):
        d.line([0, i, W, i], fill=(26, 21, 29, 255), width=1)
    if vign:
        v = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(v).rectangle([0, 0, W, H], outline=(0, 0, 0, 150), width=90)
        im.alpha_composite(v)
    return im

def bg_thientinh(off=0.0):
    """Thiên đình: trời vàng cát tường + mây tầng phẳng + cột cung điện đỏ hai bên (flat)."""
    im = Image.new('RGBA', (W, H), (243, 223, 170, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.30)], fill=(247, 230, 182, 255))
    # cột cung điện đỏ hai bên
    for cx in (W * 0.06, W * 0.94):
        d.rectangle([cx - 26, 0, cx + 26, H], fill=(168, 54, 44, 255))
        d.rectangle([cx - 26, 0, cx - 14, H], fill=(196, 78, 60, 255))
    # xà ngang đỏ trên
    d.rectangle([0, int(H * 0.10), W, int(H * 0.16)], fill=(150, 46, 38, 255))
    d.rectangle([0, int(H * 0.10), W, int(H * 0.12)], fill=(224, 180, 90, 255))
    # mây tầng phẳng (cuộn nhẹ)
    for j, (cy, col) in enumerate([(H * 0.40, (255, 246, 222)), (H * 0.56, (250, 234, 198)), (H * 0.72, (244, 222, 176))]):
        ox = (off * (0.4 + j * 0.3)) % 360
        for hx in range(-360, W + 360, 360):
            x = hx - ox
            d.ellipse([x, cy - 40, x + 200, cy + 40], fill=col + (255,))
            d.ellipse([x + 110, cy - 58, x + 330, cy + 30], fill=col + (255,))
    # nền sàn vàng
    d.rectangle([0, int(H * 0.86), W, H], fill=(224, 188, 116, 255))
    d.line([0, int(H * 0.86), W, int(H * 0.86)], fill=(180, 140, 80, 255), width=5)
    return im

def bg_nuoc(off=0.0):
    """Dưới nước: lam lục tầng, vệt sáng caustic THẲNG (flat), không blur."""
    im = Image.new('RGBA', (W, H), (26, 92, 104, 255))
    d = ImageDraw.Draw(im)
    for j, (y0, col) in enumerate([(0, (40, 120, 130)), (int(H * 0.30), (30, 100, 112)), (int(H * 0.60), (22, 80, 92))]):
        d.rectangle([0, y0, W, H], fill=col + (255,))
    # caustic: tia sáng xiên thẳng từ trên
    for i in range(-2, 10):
        x = int(W * 0.12 * i + (off * 0.4) % (W * 0.12))
        d.polygon([(x, 0), (x + 40, 0), (x - 120, H), (x - 160, H)], fill=(120, 190, 190, 26))
    # đáy cát
    d.rectangle([0, int(H * 0.88), W, H], fill=(60, 110, 110, 255))
    d.line([0, int(H * 0.88), W, int(H * 0.88)], fill=(40, 84, 86, 255), width=5)
    return im

def bubbles(bg, t, n=18, seed=7):
    """bọt khí trắng nổi lên (vòng tròn rỗng mảnh), dùng cho cảnh dưới nước."""
    d = ImageDraw.Draw(bg, 'RGBA')
    random.seed(seed)
    for _ in range(n):
        bx = random.randint(40, W - 40)
        rise = (random.random() + t * 1.4) % 1.0
        by = int(H * (0.95 - rise * 0.9))
        r = random.randint(4, 13)
        d.ellipse([bx - r, by - r, bx + r, by + r], outline=(220, 245, 245, 150), width=3)

def bg_cung(off=0.0):
    """Điện thờ ấm: tường đỏ + xà vàng + bàn cúng gỗ (cho cảnh Tịnh Đàn Sứ Giả)."""
    im = Image.new('RGBA', (W, H), (176, 72, 58, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.16)], fill=(150, 56, 46, 255))
    d.rectangle([0, int(H * 0.14), W, int(H * 0.20)], fill=(224, 180, 90, 255))   # xà vàng
    for cx in (W * 0.16, W * 0.84):
        d.rectangle([cx - 20, 0, cx + 20, int(H * 0.80)], fill=(140, 48, 40, 255))
    # bàn cúng gỗ
    ty = int(H * 0.80)
    d.rectangle([0, ty, W, H], fill=(120, 72, 44, 255))
    d.rectangle([0, ty, W, ty + 12], fill=(156, 100, 60, 255))
    return im

def offerings(bg, ty):
    """mâm đồ cúng trên bàn (bát/đĩa/quả) — flat."""
    d = ImageDraw.Draw(bg, 'RGBA')
    items = [(W * 0.20, (236, 220, 180), 46), (W * 0.36, (210, 90, 70), 34),
             (W * 0.64, (210, 90, 70), 34), (W * 0.80, (236, 220, 180), 46)]
    for cx, col, r in items:
        d.ellipse([cx - r, ty - r * 0.5, cx + r, ty + r * 0.5], fill=col + (255,))
        d.ellipse([cx - r, ty - r * 0.5, cx + r, ty - r * 0.5 + 10], fill=(255, 255, 255, 60))
    # quả tròn đỏ trên 2 đĩa
    for cx in (W * 0.36, W * 0.64):
        d.ellipse([cx - 16, ty - 44, cx + 16, ty - 12], fill=(200, 70, 56, 255))

def halo_flat(bg, cx, cy, r, t):
    """Vành hào quang FLAT tia toả (sun-burst viền đều) — KHÔNG glow/blur (luật kênh)."""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    for ang in range(0, 360, 15):
        a = math.radians(ang + t * 10)
        p1 = (cx + math.cos(a) * r, cy + math.sin(a) * r)
        p2 = (cx + math.cos(a + 0.09) * r * 1.9, cy + math.sin(a + 0.09) * r * 1.9)
        p3 = (cx + math.cos(a + 0.18) * r, cy + math.sin(a + 0.18) * r)
        dl.polygon([p1, p2, p3], fill=(246, 206, 96, 210))
    dl.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 226, 140, 255))
    dl.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(214, 160, 60, 255), width=6)
    bg.alpha_composite(layer)

# ───────────────────────── CHỮ ─────────────────────────
def wrap(draw, text, fnt, maxw):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur: out.append(cur)
            cur = w
    if cur: out.append(cur)
    return out

def badge(bg, text, color=(150, 58, 44)):
    d = ImageDraw.Draw(bg, 'RGBA')
    tw = d.textlength(text, font=F_LAB)
    d.rounded_rectangle([30, 44, 30 + tw + 34, 90], radius=12, fill=color + (235,))
    d.text((47, 50), text, font=F_LAB, fill=(255, 255, 255))

def pop_text(bg, text, cy, prog, color=(248, 224, 120), fnt=None, box=True):
    fnt = fnt or F_BIG
    prog = max(0.0, min(1.0, prog))
    if prog <= 0.0:
        return
    e = min(1.0, prog * 1.35)
    sc = max(0.15, 0.6 + 0.4 * (1 - (1 - e) ** 3))
    al = int(255 * min(1.0, prog * 2))
    d = ImageDraw.Draw(bg, 'RGBA')
    lines = wrap(d, text, fnt, int((W - 80) / sc)) if '\n' not in text else text.split('\n')
    lh = int(fnt.size * 1.26)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    toth = lh * len(lines)
    for i, ln in enumerate(lines):
        tw = dl.textlength(ln, font=fnt)
        x = (W - tw) / 2; y = cy - toth / 2 + i * lh
        if box:
            dl.rounded_rectangle([x - 20, y - 6, x + tw + 20, y + fnt.size + 12], radius=12, fill=(20, 16, 24, 220))
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            dl.text((x + ox, y + oy), ln, font=fnt, fill=(14, 11, 16, al))
        dl.text((x, y), ln, font=fnt, fill=color + (al,))
    if sc != 1.0:
        nl = layer.resize((int(W * sc), int(H * sc)), Image.LANCZOS)
        tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        tmp.alpha_composite(nl, (int((W - nl.width) / 2), int((H - nl.height) / 2)))
        layer = tmp
    if al < 255:
        layer.putalpha(layer.split()[-1].point(lambda p: int(p * al / 255)))
    bg.alpha_composite(layer)

def chip(bg, text, cx, cy, col=(150, 50, 55)):
    d = ImageDraw.Draw(bg, 'RGBA')
    tw = d.textlength(text, font=F_SMALL)
    d.rounded_rectangle([cx - tw / 2 - 12, cy, cx + tw / 2 + 12, cy + 36], radius=9, fill=col + (235,))
    d.text((cx - tw / 2, cy + 4), text, font=F_SMALL, fill=(255, 255, 255))

# ───────────────────────── KEN BURNS / CỬ ĐỘNG ─────────────────────────
def ken(frame_img, z, dx=0.0, dy=0.0):
    if z <= 1.0001 and dx == 0 and dy == 0:
        return frame_img
    nw, nh = int(W * z), int(H * z)
    big = frame_img.resize((nw, nh), Image.LANCZOS)
    mx, my = nw - W, nh - H
    x = int(mx * (0.5 + dx / 2)); y = int(my * (0.5 + dy / 2))
    return big.crop((x, y, x + W, y + H))

def shake(amt):
    return (random.uniform(-amt, amt), random.uniform(-amt, amt))

def walk_tf(spr, p, hop=14):
    hpp = (p * 2) % 1.0
    bob = abs(math.sin(math.pi * hpp))
    sy = 1 - 0.03 * bob
    sx = 1 + 0.02 * bob
    waddle = 3.0 * math.sin(2 * math.pi * p)
    w2, h2 = max(1, round(spr.width * sx)), max(1, round(spr.height * sy))
    s = spr.resize((w2, h2), Image.LANCZOS).rotate(-waddle, expand=True, resample=Image.BICUBIC)
    return s, int(bob * hop)

# ───────────────────────── RENDER SHOT (1 khung) ─────────────────────────
def render_frame(shot, t, extra):
    br = math.sin(2 * math.pi * t * 1.3)

    if shot == 'ngunga':
        # Bát Giới ngủ ngáp ôm đinh ba, bụng phập phồng (thở), Zzz
        bg = bg_duongxa(off=0)
        gy = int(H * 0.88)
        snore = math.sin(2 * math.pi * t * 1.0)                 # nhịp ngáy
        bgi = sprite('bat-gioi', 'cuoi_nham', 'mim', h=600)
        soft_shadow(bg, int(W * 0.46), gy, w=170, a=95)
        paste_mid(bg, bgi, int(W * 0.46), gy + 4, sc=1 + 0.02 * snore)
        d = ImageDraw.Draw(bg, 'RGBA')
        for i in range(3):                                      # Zzz nổi lên
            zp = (t * 1.2 + i * 0.33) % 1.0
            zx = int(W * 0.66 + 26 * i + 10 * zp)
            zy = int(H * 0.34 - 90 * zp)
            d.text((zx, zy), 'z', font=font(28 + i * 10), fill=(90, 70, 50, int(230 * (1 - zp))))
        pop_text(bg, 'Kẻ ăn hại nhất Tây Du?', int(H * 0.16), min(1, t * 1.8), color=KEM, fnt=F_BIG)
        return ken(bg.convert('RGB'), 1.0 + 0.05 * t)

    if shot == 'hooklat':
        # lia sang: Bát Giới nhỏ góc dưới-trái, BÓNG sau lưng hoá Thiên Bồng oai phong + 5.048 CÂN
        bg = bg_thientinh(off=t * 120)
        gy = int(H * 0.88)
        rev = min(1.0, t * 1.6)                                 # Thiên Bồng hiện dần
        tb = sprite('thien-bong', 'quyet', 'thang', h=int(620 * (0.7 + 0.3 * rev)))
        soft_shadow(bg, int(W * 0.56), gy, w=150, a=90)
        paste_mid(bg, tb, int(W * 0.56), gy)
        bgi = sprite('bat-gioi', 'cuoi_nham', 'mim', h=240)
        paste_mid(bg, bgi, int(W * 0.17), int(H * 0.92))
        pop_text(bg, '5.048 CÂN', int(H * 0.15), min(1, t * 2.2), color=(255, 226, 120), fnt=F_TITLE)
        return ken(bg.convert('RGB'), 1.06 - 0.05 * t)

    if shot == 'luoi':
        # Sa Tăng gánh đồ nặng (nghiêng), Bát Giới nằm chơi
        bg = bg_duongxa(off=80)
        gy = int(H * 0.90)
        st = sprite('sa-tang', 'buon', 'mim', h=430)
        soft_shadow(bg, int(W * 0.28), gy, w=110, a=90)
        paste_mid(bg, st.rotate(-7, expand=True, resample=Image.BICUBIC), int(W * 0.28), gy)
        d = ImageDraw.Draw(bg, 'RGBA')
        d.rectangle([int(W * 0.18), int(H * 0.44), int(W * 0.40), int(H * 0.58)], fill=(150, 110, 66, 255))  # kiện hàng
        d.rectangle([int(W * 0.18), int(H * 0.44), int(W * 0.40), int(H * 0.47)], fill=(120, 86, 50, 255))
        bgi = sprite('bat-gioi', 'cuoi_nham', 'cuoi', h=360)
        soft_shadow(bg, int(W * 0.72), gy, w=120, a=90)
        paste_mid(bg, bgi, int(W * 0.72), gy)
        pop_text(bg, 'Việc nặng đùn sư đệ', int(H * 0.16), min(1, t * 1.8), color=KEM, fnt=F_BIG)
        return bg.convert('RGB')

    if shot == 'doigiaitan':
        bg = bg_duongxa(off=60)
        gy = int(H * 0.88)
        bgi = sprite('bat-gioi', 'buon', extra.get('mouth', 'noi'), h=600)
        soft_shadow(bg, int(W * 0.5), gy, w=150, a=80)
        paste_mid(bg, bgi, int(W * 0.5), gy + int(3 * br))
        pop_text(bg, 'Chia hành lý — ai về nhà nấy!', int(H * 0.16), min(1, t * 1.7), color=KEM, fnt=font(36))
        return bg.convert('RGB')

    if shot == 'dinhba':
        # cận cây đinh ba (qua Thiên Bồng) + thẻ 5.048 CÂN = MỘT TẠNG
        bg = bg_toi(vign=True)
        tb = sprite('thien-bong', 'quyet', 'thang', h=900)
        paste_mid(bg, tb, int(W * 0.40), int(H * 1.12))
        pop_text(bg, '5.048 CÂN', int(H * 0.14), min(1, t * 2.4), color=(255, 226, 120), fnt=F_TITLE)
        pop_text(bg, '= "một tạng" — Thái Thượng Lão Quân rèn', int(H * 0.24), min(1, (t - 0.3) * 3),
                 color=(250, 232, 200), fnt=font(28), box=False)
        return ken(bg.convert('RGB'), 1.0 + 0.06 * t, dx=0.3)

    if shot == 'thienbong':
        # FLASHBACK: Thiên Bồng oai phong + bóng binh lính + 8 VẠN THỦY QUÂN + tia flat
        bg = bg_thientinh(off=t * 90)
        gy = int(H * 0.88)
        # tia sáng toả (flat) sau tướng
        ray = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ray)
        cx0, cy0 = int(W * 0.5), int(H * 0.44)
        for ang in range(0, 360, 20):
            a = math.radians(ang + t * 12)
            p1 = (cx0 + math.cos(a) * 950, cy0 + math.sin(a) * 950)
            p2 = (cx0 + math.cos(a + 0.09) * 950, cy0 + math.sin(a + 0.09) * 950)
            dr.polygon([(cx0, cy0), p1, p2], fill=(252, 214, 120, 16))
        bg.alpha_composite(ray)
        # hàng binh lính (bóng) phía sau
        for i, px in enumerate([0.18, 0.30, 0.70, 0.82]):
            sil = silhouette(sprite('tieu-yeu', h=200), col=(150, 60, 48))
            paste_mid(bg, sil, int(W * px), int(H * 0.80))
        tb = sprite('thien-bong', 'quyet', 'thang', h=560)
        soft_shadow(bg, int(W * 0.5), gy, w=150, a=90)
        paste_mid(bg, tb, int(W * 0.5), gy + int(3 * br))
        pop_text(bg, '8 VẠN THỦY QUÂN THIÊN HÀ', int(H * 0.15), min(1, t * 1.9), color=(255, 226, 130), fnt=F_BIG)
        return ken(bg.convert('RGB'), 1.05 - 0.04 * t)

    if shot == 'gheohang':
        # Thiên Bồng say nghiêng về Hằng Nga (nu-vuong) đang né
        bg = bg_thientinh(off=160)
        gy = int(H * 0.88)
        hn = sprite('nu-vuong', 'ngac', 'o', h=520, flip=True)
        soft_shadow(bg, int(W * 0.74), gy, w=110, a=85)
        paste_mid(bg, hn, int(W * 0.74), gy)
        tb = sprite('thien-bong', 'cuoi_nham', extra.get('mouth', 'noi'), h=560)
        soft_shadow(bg, int(W * 0.34), gy, w=140, a=90)
        paste_mid(bg, tb.rotate(-8, expand=True, resample=Image.BICUBIC), int(W * 0.34), gy)
        d = ImageDraw.Draw(bg, 'RGBA')
        d.ellipse([int(W * 0.50), int(H * 0.46), int(W * 0.56), int(H * 0.52)], fill=(236, 220, 180, 255))  # chén rượu
        pop_text(bg, 'Một phút buông tuồng…', int(H * 0.16), min(1, t * 1.8), color=KEM, fnt=F_BIG)
        return ken(bg.convert('RGB'), 1.0 + 0.04 * t)

    if shot == 'bibat':
        # sấm chớp, bóng Thiên Bồng rơi; thẻ phạt
        bg = bg_toi(vign=True)
        p = min(1.0, t / 0.9)
        tb = silhouette(sprite('thien-bong', 'buon', 'thang', h=440), col=(18, 14, 22))
        fallen = tb.rotate(60 * p, expand=True, resample=Image.BICUBIC)
        x = int(W * 0.5 - fallen.width / 2 + 120 * p)
        y = int(H * 0.30 + 240 * p * p)
        bg.alpha_composite(fallen, (x, y))
        # chớp
        if (t * 10) % 2 < 0.7:
            bg.alpha_composite(Image.new('RGBA', (W, H), (255, 246, 214, 70)))
        d = ImageDraw.Draw(bg, 'RGBA')
        d.line([(W * 0.2, 0), (W * 0.3, H * 0.3), (W * 0.22, H * 0.36), (W * 0.34, H * 0.6)],
               fill=(255, 240, 180, 230), width=5)
        pop_text(bg, '2.000 CHÙY · ĐÀY XUỐNG TRẦN', int(H * 0.14), min(1, t * 2.2), color=(255, 170, 120), fnt=font(34))
        pop_text(bg, 'ĐẦU THAI NHẦM VÀO BỤNG LỢN', int(H * 0.72), min(1, (t - 0.4) * 3), color=(255, 150, 120), fnt=font(32))
        return bg.convert('RGB')

    if shot == 'duoinuoc':
        # dưới nước: Ngộ Không trên bờ (trên), Bát Giới rẽ nước lao tới (nói)
        bg = bg_nuoc(off=t * 400)
        gy = int(H * 0.90)
        # Ngộ Không trên mép bờ (góc trên) bắt quyết, nhìn xuống
        kh = sprite('ngo-khong', 'quyet', extra.get('mouth', 'noi'), h=300)
        paste_mid(bg, kh, int(W * 0.74), int(H * 0.30))
        chip(bg, 'tị thủy', int(W * 0.74), int(H * 0.31))
        # Bát Giới lao tới dưới nước
        bgi = sprite('bat-gioi', 'quyet', 'mim', h=520)
        soft_shadow(bg, int(W * 0.38), gy, w=130, a=70)
        paste_mid(bg, bgi, int(W * 0.38), gy + int(6 * br))
        bubbles(bg, t)
        pop_text(bg, 'Dưới nước là phần lão Trư', int(H * 0.15), min(1, t * 1.8), color=(235, 245, 230), fnt=F_BIG)
        return ken(bg.convert('RGB'), 1.0 + 0.05 * t)

    if shot == 'duoinuoc2':
        bg = bg_nuoc(off=200 + t * 360)
        gy = int(H * 0.90)
        bgi = sprite('bat-gioi', 'cuoi_nham', 'cuoi_mo', h=560)
        soft_shadow(bg, int(W * 0.5), gy, w=140, a=70)
        paste_mid(bg, bgi, int(W * 0.5), gy + int(6 * br))
        bubbles(bg, t, n=22, seed=11)
        pop_text(bg, 'Thủy chiến: trên tài Ngộ Không', int(H * 0.15), min(1, t * 1.8), color=(235, 245, 230), fnt=F_BIG)
        return bg.convert('RGB')

    if shot == 'tinhdan':
        # Bát Giới hào quang FLAT + mâm cúng → Tịnh Đàn Sứ Giả
        bg = bg_cung()
        ty = int(H * 0.80)
        halo_flat(bg, int(W * 0.5), int(H * 0.44), int(W * 0.22), t)
        bgi = sprite('bat-gioi', 'cuoi_nham', 'cuoi_mo', h=520)
        soft_shadow(bg, int(W * 0.5), int(H * 0.82), w=130, a=80)
        paste_mid(bg, bgi, int(W * 0.5), int(H * 0.82))
        offerings(bg, ty + 6)
        pop_text(bg, 'TỊNH ĐÀN SỨ GIẢ', int(H * 0.14), min(1, t * 2.0), color=(255, 226, 120), fnt=F_TITLE)
        pop_text(bg, 'Phần thưởng, hay cú tát?', int(H * 0.235), min(1, (t - 0.35) * 3), color=KEM, fnt=font(30), box=False)
        return ken(bg.convert('RGB'), 1.0 + 0.03 * t)

    if shot == 'chot':
        # cả đoàn đi, đội hình chuẩn trái→phải (Sa Tăng·ngựa·Đường Tăng·Bát Giới·Ngộ Không)
        bg = bg_duongxa(off=300 + t * 300); gy = int(H * 0.90)
        team = [('sa-tang', 'hien', 'mim', 262, False), ('bach-long-ma', 'hien', 'mim', 236, False),
                ('duong-tang', 'hien', 'mim', 272, False), ('bat-gioi', 'cuoi_nham', 'mim', 258, False),
                ('ngo-khong', 'quyet', 'mim', 270, False)]
        base, step = W * 0.08, W * 0.21; cyc = t * 2.0
        for i in sorted(range(len(team)), key=lambda i: team[i][3]):
            ma, bc, mi, hh, fl = team[i]
            spr = sprite(ma, bc, mi, h=hh, flip=fl)
            s, lift = walk_tf(spr, (cyc + i * 0.42) % 1.0)
            x = int(base + i * step); foot = gy - lift
            soft_shadow(bg, x, gy, w=max(30, int(56 - lift * 0.3)), a=78)
            bg.alpha_composite(s, (x - s.width // 2, foot - s.height))
        pop_text(bg, 'Ăn hại — hay người thật nhất?', int(H * 0.14), min(1, t * 1.5), color=KEM, fnt=font(32))
        return bg.convert('RGB')

    if shot == 'cta':
        bg = bg_toi()
        bgi = sprite('bat-gioi', 'cuoi_nham', 'cuoi', h=560)
        paste_mid(bg, bgi, int(W * 0.5), int(H * 0.62))
        d = ImageDraw.Draw(bg, 'RGBA')
        btns = [('KẺ ĂN HẠI', (150, 60, 55)), ('NGƯỜI THẬT NHẤT', (46, 125, 107))]
        y0 = int(H * 0.70)
        for i, (lab, col) in enumerate(btns):
            if t < 0.18 + i * 0.18:
                continue
            hy = y0 + i * 96
            d.rounded_rectangle([int(W * 0.08), hy, int(W * 0.92), hy + 76], radius=18, fill=col + (240,))
            tw = d.textlength(lab, font=F_LAB)
            d.text(((W - tw) / 2, hy + 22), lab, font=F_LAB, fill=(255, 255, 255))
        pop_text(bg, 'Bạn chọn phe nào?', int(H * 0.15), min(1, t * 1.8), color=(248, 224, 150), fnt=F_BIG)
        return bg.convert('RGB')
    raise ValueError(shot)

# ───────────────────────── GIỌNG ─────────────────────────
VOICE = {'dan': 'giahuy', 'bat': 'quangminh', 'tb': 'huuduc', 'ngo': 'tiendat'}

def gen_voices():
    import hashlib
    cache = os.path.join(WORK, 'voices.npz')
    sig = hashlib.md5('|'.join(t for _, t, _ in LINES).encode('utf-8')).hexdigest()
    if os.path.exists(cache):
        try:
            z = np.load(cache, allow_pickle=True)
            if z['sig'].item() == sig:
                outs = [z['a%d' % i].astype(np.float32) for i in range(len(LINES))]
                for i, a in enumerate(outs):
                    print('  câu %d (cache) %.2fs' % (i + 1, a.size / SR), flush=True)
                return outs
        except Exception as e:
            print('  (cache giọng hỏng, tạo lại:', e, ')', flush=True)
    from zerotts import ZeroTTS, normalize_vi_text
    tts = ZeroTTS.from_pretrained('zeroweight-ai/ZeroTTS')
    sr = tts.sample_rate
    outs = []
    for i, (who, text, shot) in enumerate(LINES):
        best = None
        for k in range(2):
            np.random.seed(11 + k)
            a = tts.synthesize(normalize_vi_text(text), voice=VOICE[who], cfg_scale=1.0).reshape(-1).astype(np.float32)
            idx = np.where(np.abs(a) > 0.012)[0]
            if idx.size:
                a = a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.05 * sr)]
            if best is None or a.size > best.size:
                best = a
        a44 = S.resample_poly(best, SR, sr).astype(np.float32)
        outs.append(a44)
        print('  câu %d [%s] %.2fs' % (i + 1, who, a44.size / SR), flush=True)
    try:
        np.savez(cache, sig=sig, **{'a%d' % i: a for i, a in enumerate(outs)})
    except Exception as e:
        print('  (không lưu được cache giọng:', e, ')', flush=True)
    return outs

# ───────────────────────── TIẾNG ĐỘNG ─────────────────────────
def env(n, a=0.01, r=0.1):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def tone(f, dur, amp=0.3, a=0.01, r=0.1):
    n = int(dur * SR); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return amp * w * env(n, a, r)

def clash(amp=0.4):
    n = int(0.2 * SR); t = np.arange(n) / SR
    w = np.random.randn(n) * np.exp(-t * 26) + np.sin(2 * np.pi * np.linspace(1300, 480, n) * t) * np.exp(-t * 16)
    return amp * w

def whoosh(amp=0.3, dur=0.26):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(180, 760, n)
    w = np.sin(2 * np.pi * f * t) * np.sin(np.pi * t / dur) + 0.4 * np.random.randn(n) * np.exp(-((t - dur / 2) ** 2) / (2 * 0.02 ** 2))
    return amp * w

def thud(amp=0.5):
    n = int(0.28 * SR); t = np.arange(n) / SR
    f = np.linspace(160, 55, n)
    return amp * (np.sin(2 * np.pi * f * t) + 0.4 * np.random.randn(n)) * env(n, 0.002, 0.22)

def splash(amp=0.3):
    n = int(0.3 * SR); t = np.arange(n) / SR
    return amp * np.random.randn(n) * np.exp(-t * 7) * (0.5 + 0.5 * np.sin(2 * np.pi * 600 * t))

def put(buf, start_s, wave, g=1.0):
    i = int(start_s * SR); j = min(len(buf), i + len(wave))
    if i < len(buf):
        buf[i:j] += g * wave[:j - i]

def build_audio(voices, seg_starts, seg_shot, total_s):
    buf = np.zeros(int(total_s * SR) + SR)
    penta = [329.63, 392.0, 440.0, 523.25, 587.33]
    tt, i = 0.0, 0
    while tt < total_s:
        put(buf, tt, tone(penta[i % 5] / 2, 0.9, amp=0.035, r=0.6))
        tt += 0.85; i += 1
    n = int(total_s * SR); t = np.arange(n) / SR
    buf[:n] += 0.03 * np.sin(2 * np.pi * 110 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t))
    for st, shot, v in zip(seg_starts, seg_shot, voices):
        dur = v.size / SR
        put(buf, st, whoosh(0.30))
        if shot in ('hooklat', 'thienbong', 'tinhdan'):
            put(buf, st + 0.08, tone(293.66, 1.0, amp=0.06, r=0.7))     # hào quang ngân
        if shot == 'bibat':
            put(buf, st + 0.15, thud(0.6)); put(buf, st + 0.15, clash(0.35))
        if shot in ('duoinuoc', 'duoinuoc2'):
            put(buf, st + 0.05, splash(0.28))
        if shot in ('ngunga',):
            put(buf, st + 0.1, tone(90, 0.5, amp=0.05, r=0.4))          # tiếng ngáy trầm
    for st, v in zip(seg_starts, voices):
        i0 = int(st * SR); i1 = min(len(buf), i0 + v.size)
        buf[i0:i1] *= 0.4
        put(buf, st, v, g=0.98)
    buf = 0.92 * buf / (np.max(np.abs(buf)) or 1)
    return buf

def mouths_for(v):
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(v[k:k + hop] ** 2)) for k in range(0, v.size, hop)])
    rms = rms / (rms.max() or 1)
    keys = []
    for a in rms:
        keys.append('mim' if a < 0.12 else 'o' if a < 0.34 else 'noi' if a < 0.6 else 'cuoi_mo')
    return keys

# ───────────────────────── MAIN ─────────────────────────
def main():
    os.makedirs(WORK, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)
    import glob
    for old in glob.glob(os.path.join(WORK, 'f_*.png')):
        try: os.remove(old)
        except OSError: pass
    print('• Tạo giọng ZeroTTS…', flush=True)
    voices = gen_voices()
    GAP = 0.22
    seg_frames = [int(round((v.size / SR + GAP) * FPS)) for v in voices]
    seg_starts = []
    acc = 0.0
    for v in voices:
        seg_starts.append(acc); acc += v.size / SR + GAP
    total_f = sum(seg_frames); total_s = total_f / FPS
    seg_shot = [s for _, _, s in LINES]
    print('• Tổng: %.1fs · %d khung @ %dfps' % (total_s, total_f, FPS), flush=True)

    char_idx = [i for i, (w, _, _) in enumerate(LINES) if w != 'dan']
    mouth_seq = {i: mouths_for(voices[i]) for i in char_idx}

    print('• Render khung…', flush=True)
    gi = 0
    for li, (nf, shot) in enumerate(zip(seg_frames, seg_shot)):
        for k in range(nf):
            t = k / max(1, nf - 1)
            extra = {}
            if li in mouth_seq:
                ms = mouth_seq[li]
                extra['mouth'] = ms[min(len(ms) - 1, int(t * (len(ms))))]
            img = render_frame(shot, t, extra)
            bg = img.convert('RGBA')
            badge(bg, 'BÁT GIỚI · Short 02')
            fade = 1.0
            if k < 3: fade = (k + 1) / 4
            elif k > nf - 4: fade = (nf - k) / 4
            if fade < 1.0:
                black = Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - fade))))
                bg.alpha_composite(black)
            bg.convert('RGB').save(os.path.join(WORK, 'f_%04d.png' % gi))
            gi += 1
        print('\r  shot %d/%d (%s)      ' % (li + 1, len(LINES), shot), end='', flush=True)
    print()

    print('• Tổng hợp tiếng…', flush=True)
    buf = build_audio(voices, seg_starts, seg_shot, total_s)
    wav = os.path.join(WORK, 'tieng.wav')
    sf.write(wav, buf.astype(np.float32), SR)

    print('• Ghép video + mux…', flush=True)
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    silent = os.path.join(WORK, 'silent.mp4')
    subprocess.run([ff, '-y', '-framerate', str(FPS), '-i', os.path.join(WORK, 'f_%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent],
                   check=True, capture_output=True)
    out = os.path.join(OUTDIR, 'short02-full.mp4')
    subprocess.run([ff, '-y', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', out], check=True, capture_output=True)
    print('XONG →', out, '|', total_f, 'khung ·', '%.1fs' % total_s)

if __name__ == '__main__':
    main()
