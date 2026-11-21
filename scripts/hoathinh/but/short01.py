# -*- coding: utf-8 -*-
"""SHORT 01 — "Đường Tăng: Lãnh đạo hay gánh nặng?" — dựng 30s ĐẦU (Hook + đầu Hồi 1).

Dạng: LỜI DẪN (voiceover) + MONTAGE nhân vật Bộ Bút. Dọc 9:16 (720x1280), 24fps.
Pipeline: tạo giọng ZeroTTS từng câu -> đo giây -> dựng shot theo đúng mốc giây
         -> render khung 24fps (Ken Burns + chữ hiện + cử động nhẹ + lip-flap)
         -> tổng hợp nhạc nền + tiếng động theo cùng timeline -> mux ra MP4.

Chạy:  PYTHONUTF8=1 HF_HUB_DISABLE_XET=1 python scripts/hoathinh/but/short01.py
Ra:    du-an/tay-du-ky/output/short/short01-30s.mp4
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
WORK = os.path.join(ROOT, 'build', 'thu-hoathinh', 'short01')
ASSET = os.path.join(ROOT, 'assets', 'nhan-vat', 'but')
FD = os.path.join(ROOT, 'fonts')

def font(sz, bold=True):
    return ImageFont.truetype(os.path.join(FD, 'BeVietnamPro-%s.ttf' % ('SemiBold' if bold else 'Medium')), sz)

F_TITLE = font(52); F_BIG = font(44); F_SUB = font(30, False); F_LAB = font(26); F_SMALL = font(23, False)

# ───────────────────────── KỊCH BẢN (câu dẫn, người nói, shot) ─────────────────────────
# speaker: 'dan' = lời dẫn (giahuy), 'tang' = Đường Tăng (tiendat)
LINES = [
    ('dan',    'Một người không biết võ, mắt không nhìn ra yêu quái, bị bắt cóc hơn hai mươi lần.', 'hang'),
    ('dan',    'Vậy mà hắn là trưởng đoàn của đội mạnh nhất Tam Giới. Vì sao?', 'danhnhau'),
    ('dan',    'Nói về sự vô dụng thì... khó ai bằng.', 'tieude'),
    ('dan',    'Bạch Cốt Tinh hóa ba lần, ông tin cả ba.', 'bachcot'),
    ('tang',   'Ngộ Không! Con lại giết người, cút về đi!', 'duoi'),
    ('dan',    'Giết đúng yêu quái, lại bị đuổi đi.', 'chuhien'),
    ('dan',    'Kim Giác, Ngân Giác nhốt ông vào bình. Hồng Hài Nhi treo lên nướng. Nữ Nhi Quốc đòi cưới. Bọ Cạp Tinh ép duyên.', 'batcoc'),
    ('dan',    'Cứ vài tập, ba đệ tử lại đi dọn hậu quả. Một người sếp như thế, ai mà không ức?', 'duongxa'),
    ('dan',    'Nhưng khoan. Vì sao ai cũng muốn bắt ông? Vì ông là Kim Thiền Tử chuyển thế.', 'canhmat'),
    ('dan',    'Ăn một miếng thịt ông là trường sinh bất lão. Hắn không yếu, hắn là phần thưởng cả Tam Giới thèm khát.', 'phanthuong'),
    ('dan',    'Nữ Nhi Quốc dâng cả ngai vàng lẫn sắc đẹp, ông từ chối.', 'tuchoi'),
    ('dan',    'Bọ Cạp Tinh ép chết, ông thà chết không chịu. Mười bốn năm, mười vạn tám ngàn dặm, chưa một lần quay đầu.', 'kiencuong'),
    ('bat',    'Sư phụ lại bị bắt! Không có người, còn thỉnh kinh làm gì? Chia hành lý, ai về nhà nấy cho rồi!', 'batgioi'),
    ('satang', 'Nhị sư huynh! Sư phụ là cái đích. Mất người thì cả đoàn mất hướng, còn đi đâu nữa?', 'satang'),
    ('dan',    'Thấy chưa, bỏ sư phụ ra, đội mạnh nhất Tam Giới tan ngay. Nhưng ông giữ Ngộ Không bằng đức độ, hay bằng vòng kim cô siết đầu?', 'vongkimco'),
    ('dan',    'Vậy Đường Tăng là gì? Kẻ vô dụng được bảo kê, hay lãnh đạo cai trị bằng cái vòng trên đầu kẻ mạnh nhất?', 'chot'),
    ('dan',    'Theo bạn, ông lãnh đạo bằng đức, hay bằng vòng kim cô? Gõ phe bạn ở dưới.', 'cta'),
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
    """dán sprite, tâm ngang cx, mép dưới by."""
    if sc != 1.0:
        spr = spr.resize((max(1, round(spr.width * sc)), max(1, round(spr.height * sc))), Image.LANCZOS)
    x = int(cx - spr.width / 2); y = int(by - spr.height)
    bg.alpha_composite(spr, (x, y))

def soft_shadow(bg, cx, by, w=120, a=90):
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - w, by - 14, cx + w, by + 16], fill=(10, 8, 6, a))
    bg.alpha_composite(sh)

# ───────────────────────── NỀN ─────────────────────────
def bg_hang(flick=0.0):
    """Trong hang yêu: tường tối, thạch nhũ, đuốc chập chờn, cửa hang sáng mờ phía trên."""
    im = Image.new('RGBA', (W, H), (34, 27, 30, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.30)], fill=(26, 20, 24, 255))     # vòm trên tối hơn
    # cửa hang sáng mờ (góc trên phải) — nơi 3 đệ tử đánh nhau
    d.ellipse([W * 0.48, -120, W * 1.15, H * 0.34], fill=(70, 74, 86, 255))
    d.ellipse([W * 0.54, -70, W * 1.08, H * 0.30], fill=(104, 112, 126, 255))
    # thạch nhũ rủ từ trần
    random.seed(3)
    for x in range(10, W, 86):
        hgt = random.randint(70, 150)
        d.polygon([(x, 0), (x + 30, 0), (x + 15, hgt)], fill=(46, 37, 41, 255))
        d.polygon([(x + 15, 0), (x + 30, 0), (x + 24, hgt - 24)], fill=(58, 47, 51, 255))
    # nền đá
    gy = int(H * 0.80)
    d.rectangle([0, gy, W, H], fill=(44, 35, 33, 255))
    d.line([0, gy, W, gy], fill=(28, 22, 20, 255), width=6)
    for _ in range(26):
        x = random.randint(0, W); y = random.randint(gy + 10, H - 10)
        r = random.randint(5, 16)
        d.ellipse([x, y, x + r, y + r * 0.6], fill=(36, 29, 27, 255))
    # đuốc trên tường trái
    tx, ty = 70, int(H * 0.44)
    d.line([tx, ty, tx + 8, ty + 120], fill=(70, 50, 34, 255), width=12)
    fl = 1.0 + 0.18 * flick
    d.polygon([(tx - 18, ty), (tx + 26, ty), (tx + 4, ty - int(60 * fl))], fill=(224, 140, 44, 255))
    d.polygon([(tx - 9, ty), (tx + 17, ty), (tx + 4, ty - int(38 * fl))], fill=(248, 206, 96, 255))
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([tx - 150, ty - 170, tx + 180, ty + 150], fill=(230, 150, 60, 30))
    im.alpha_composite(glow)
    return im

def bg_toi(vign=True):
    """Nền tối cho thẻ chữ / cận chữ."""
    im = Image.new('RGBA', (W, H), (21, 17, 24, 255))
    d = ImageDraw.Draw(im)
    for i in range(0, H, 48):
        d.line([0, i, W, i], fill=(26, 21, 29, 255), width=1)
    if vign:
        v = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(v).rectangle([0, 0, W, H], outline=(0, 0, 0, 150), width=90)
        im.alpha_composite(v)
    return im

def bg_duongxa(off=0.0):
    """Đường thiên lý lúc xế chiều — trời ấm, đồi xa, lối mòn."""
    im = Image.new('RGBA', (W, H), (236, 200, 150, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.34)], fill=(242, 206, 150, 255))
    d.rectangle([0, int(H * 0.34), W, int(H * 0.40)], fill=(236, 188, 138, 255))
    d.ellipse([W * 0.62, H * 0.12, W * 0.82, H * 0.24], fill=(250, 232, 180, 255))  # mặt trời mờ
    gy = int(H * 0.62)
    # đồi xa nhiều lớp phẳng
    for j, (cy, col) in enumerate([(gy - 40, (176, 170, 132)), (gy - 14, (150, 150, 110))]):
        ox = (off * (0.3 + j * 0.3)) % 320
        for hx in range(-320, W + 320, 320):
            d.ellipse([hx - ox, cy - 70, hx - ox + 300, cy + 90], fill=col + (255,))
    d.rectangle([0, gy, W, H], fill=(150, 128, 92, 255))        # đất
    d.line([0, gy, W, gy], fill=(120, 100, 70, 255), width=5)
    # lối mòn hình thang (xa → gần)
    d.polygon([(W * 0.42, gy), (W * 0.58, gy), (W * 0.78, H), (W * 0.22, H)], fill=(178, 156, 116, 255))
    ox = (off * 0.9) % 90
    for yy in range(gy + 20, H, 90):
        t = (yy - gy) / (H - gy)
        w = 6 + 14 * t
        d.line([W * 0.5 - w, yy - ox, W * 0.5 + w, yy - ox], fill=(150, 130, 96, 255), width=int(3 + 4 * t))
    return im

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

def subtitle(bg, text):
    d = ImageDraw.Draw(bg, 'RGBA')
    lines = wrap(d, text, F_SUB, W - 90)
    lh = 40; bh = lh * len(lines) + 26
    y0 = H - 150 - bh
    d.rounded_rectangle([34, y0, W - 34, y0 + bh], radius=16, fill=(0, 0, 0, 165))
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=F_SUB)
        d.text(((W - tw) / 2, y0 + 13 + i * lh), ln, font=F_SUB, fill=(255, 245, 232))

def badge(bg, text, color=(186, 65, 57)):
    d = ImageDraw.Draw(bg, 'RGBA')
    tw = d.textlength(text, font=F_LAB)
    d.rounded_rectangle([30, 44, 30 + tw + 34, 90], radius=12, fill=color + (235,))
    d.text((47, 50), text, font=F_LAB, fill=(255, 255, 255))

def pop_text(bg, text, cy, prog, color=(248, 224, 120), fnt=None, box=True):
    """chữ bật lên: prog 0→1 (nảy nhẹ + hiện dần)."""
    fnt = fnt or F_BIG
    prog = max(0.0, min(1.0, prog))
    if prog <= 0.0:
        return
    e = min(1.0, prog * 1.35)
    sc = max(0.15, 0.6 + 0.4 * (1 - (1 - e) ** 3))
    al = int(255 * min(1.0, prog * 2))
    d = ImageDraw.Draw(bg, 'RGBA')
    lines = wrap(d, text, fnt, int((W - 80) / sc))
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

# ───────────────────────── KEN BURNS ─────────────────────────
def ken(frame_img, z, dx=0.0, dy=0.0):
    """phóng nhẹ + dời khung (z≥1). dx,dy theo tỉ lệ biên dư."""
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
    """PHA bước ĐI BỘ p∈[0,1) — thân gần như không nảy lên (KHÔNG phải nhảy):
    chỉ nhún nhẹ + đảo trọng tâm (waddle) trái↔phải cho ra dáng bước chân.
    (Người dùng chốt 21/11: cảnh 7 dùng ĐI, không nhảy.) Trả (ảnh, độ_nhấc_px nhỏ)."""
    hpp = (p * 2) % 1.0                              # 2 bước mỗi vòng
    bob = abs(math.sin(math.pi * hpp))              # nhún nhẹ mỗi bước (không bay)
    sy = 1 - 0.03 * bob                              # lún nhẹ giữa bước
    sx = 1 + 0.02 * bob
    waddle = 3.0 * math.sin(2 * math.pi * p)        # đảo người nhẹ trái/phải khi bước
    w2, h2 = max(1, round(spr.width * sx)), max(1, round(spr.height * sy))
    s = spr.resize((w2, h2), Image.LANCZOS).rotate(-waddle, expand=True, resample=Image.BICUBIC)
    return s, int(bob * hop)

# ───────────────────────── RENDER SHOT (1 khung) ─────────────────────────
def render_frame(shot, t, extra):
    """t: 0→1 trong shot. extra: dict (mouth key cho 'duoi', v.v.)"""
    br = math.sin(2 * math.pi * t * 1.3)        # nhịp thở nhẹ
    if shot == 'hang':
        bg = bg_hang(flick=math.sin(t * 22))
        dt = sprite('duong-tang', 'buon', 'buon' if (int(t * 6) % 2 == 0) else 'mim', h=520, drop=('vu_khi',))
        gy = int(H * 0.80)
        soft_shadow(bg, int(W * 0.5), gy, w=140, a=110)
        paste_mid(bg, dt, int(W * 0.5), gy + 6, sc=1 + 0.01 * br)
        # dây trói (vài vòng ngang thân)
        d = ImageDraw.Draw(bg, 'RGBA')
        for yy in range(int(H * 0.52), int(H * 0.72), 26):
            d.line([W * 0.5 - 110, yy, W * 0.5 + 110, yy + 4], fill=(150, 120, 70, 230), width=7)
        # bóng đệ tử đánh nhau nhỏ nơi cửa hang
        for k, (ma, fx) in enumerate([('ngo-khong', 0), ('bat-gioi', 70), ('sa-tang', 140)]):
            s = silhouette(sprite(ma, h=150))
            jx, jy = shake(5)
            paste_mid(bg, s, int(W * 0.72 + fx * 0.0 + k * 42 + jx), int(H * 0.30 + jy))
        img = ken(bg.convert('RGB'), 1.0 + 0.07 * t)
        return img

    if shot == 'danhnhau':
        # KHOE 3 HỌC TRÒ: đứng hàng oai phong, hướng ra trước (không đánh nhau, không loạn)
        bg = bg_hang(flick=math.sin(t * 10) * 0.5)
        # tia sáng toả sau đội hình cho hùng
        ray = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(ray)
        cx0, cy0 = int(W * 0.5), int(H * 0.34)
        for ang in range(0, 360, 22):
            a = math.radians(ang + t * 16)
            p1 = (cx0 + math.cos(a) * 950, cy0 + math.sin(a) * 950)
            p2 = (cx0 + math.cos(a + 0.11) * 950, cy0 + math.sin(a + 0.11) * 950)
            dr.polygon([(cx0, cy0), p1, p2], fill=(250, 212, 120, 15))
        bg.alpha_composite(ray)
        gy = int(H * 0.84)
        ins = min(1.0, t * 2.4)                          # bước vào gọn
        # Ngộ Không ở giữa to nhất (thủ lĩnh võ), Bát Giới trái, Sa Tăng phải
        poses = [('bat-gioi', 'hien', 0.22, 430, False),
                 ('ngo-khong', 'quyet', 0.5, 500, False),
                 ('sa-tang', 'quyet', 0.78, 440, True)]
        for ma, bc, px, hh, fl in poses:
            br2 = math.sin(2 * math.pi * t * 1.1 + px * 6)
            sp = sprite(ma, bc, 'mim', h=hh, flip=fl)
            xx = int(W * px)
            soft_shadow(bg, xx, gy, w=110, a=95)
            paste_mid(bg, sp, xx, gy + int(3 * br2), sc=0.62 + 0.38 * ins)
        img = ken(bg.convert('RGB'), 1.08 - 0.05 * t)   # lùi nhẹ để lộ cả đội
        return img

    if shot == 'tieude':
        bg = bg_toi()
        pop_text(bg, 'HỒI 1', int(H * 0.40), min(1, t * 2.2), color=(236, 196, 90), fnt=F_TITLE)
        pop_text(bg, 'Hồ sơ của một "gánh nặng"', int(H * 0.52), min(1, (t - 0.2) * 2.4),
                 color=(238, 232, 222), fnt=font(34), box=False)
        return bg.convert('RGB')

    if shot == 'bachcot':
        bg = bg_toi(vign=True)
        gy = int(H * 0.74)
        labs = ['Thiếu nữ', 'Bà lão', 'Ông lão']
        for i, px in enumerate([0.24, 0.5, 0.76]):
            show = t > i * 0.22
            if not show:
                continue
            lp = min(1.0, (t - i * 0.22) * 4)
            bc = ['hien', 'buon', 'cuoi_nham'][i]
            sp = sprite('bach-cot-tinh', bc, 'cuoi' if i != 1 else 'mim', h=int(300 + 30 * i))
            sh = sp if lp >= 1 else sp.resize((max(1, int(sp.width * (0.6 + 0.4 * lp))),
                                               max(1, int(sp.height * (0.6 + 0.4 * lp)))), Image.LANCZOS)
            soft_shadow(bg, int(W * px), gy, w=70, a=80)
            paste_mid(bg, sh, int(W * px), gy)
            d = ImageDraw.Draw(bg, 'RGBA')
            tw = d.textlength(labs[i], font=F_SMALL)
            d.rounded_rectangle([W * px - tw / 2 - 12, gy + 10, W * px + tw / 2 + 12, gy + 46],
                                radius=9, fill=(150, 60, 70, 230))
            d.text((W * px - tw / 2, gy + 14), labs[i], font=F_SMALL, fill=(255, 255, 255))
        pop_text(bg, 'Hóa 3 lần — ông tin cả ba', int(H * 0.26), min(1, t * 1.6),
                 color=(248, 210, 110), fnt=F_BIG)
        return bg.convert('RGB')

    if shot == 'duoi':
        bg = bg_hang(flick=math.sin(t * 18) * 0.4)
        gy = int(H * 0.80)
        mk = extra.get('mouth', 'mim')
        tang = sprite('duong-tang', 'quyet', mk, h=560)
        soft_shadow(bg, int(W * 0.34), gy, w=130, a=110)
        paste_mid(bg, tang, int(W * 0.34), gy + 6)
        # cánh tay chỉ tay (đường nhấn) + Ngộ Không quay lưng bỏ đi
        kh = sprite('ngo-khong', 'buon', 'mim', h=430, flip=True)
        soft_shadow(bg, int(W * 0.74), gy, w=110, a=90)
        paste_mid(bg, kh, int(W * 0.74 + 10 * t), gy)
        d = ImageDraw.Draw(bg, 'RGBA')
        d.line([W * 0.44, H * 0.50, W * 0.60, H * 0.50], fill=(255, 255, 255, 40), width=0)
        img = ken(bg.convert('RGB'), 1.0 + 0.05 * t, dx=-0.3)
        return img

    if shot == 'chuhien':
        # YÊU TINH BỊ ĐÁNH TRÚNG → NGÃ XUỐNG (giết đúng yêu quái)
        bg = bg_hang(flick=math.sin(t * 16) * 0.5)
        gy = int(H * 0.82)
        hit = 0.34                                       # mốc trúng đòn
        yeu = sprite('bach-cot-tinh', 'buon' if t > hit else 'hien', 'o', h=470)
        if t <= hit:
            paste_mid(bg, yeu, int(W * 0.5 + 4 * math.sin(t * 30)), gy)   # đứng, hơi chao
        else:
            p = min(1.0, (t - hit) / (1 - hit))          # 0→1 quá trình ngã
            fallen = yeu.rotate(84 * p, expand=True, resample=Image.BICUBIC)
            al = 1 - 0.65 * p
            fallen.putalpha(fallen.split()[-1].point(lambda q: int(q * al)))
            drop = int(95 * p * p)
            x = int(W * 0.5 - fallen.width / 2 + 80 * p)
            y = int(gy - yeu.height + drop)
            soft_shadow(bg, int(W * 0.5 + 60 * p), gy, w=int(90 + 70 * p), a=70)
            bg.alpha_composite(fallen, (x, y))
        # chớp + tia va chạm đúng lúc trúng đòn
        if hit < t < hit + 0.10:
            bg.alpha_composite(Image.new('RGBA', (W, H), (255, 246, 214, 140)))
        if hit - 0.03 < t < hit + 0.15:
            fx = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(fx).regular_polygon((int(W * 0.52), int(H * 0.44), 95), 10,
                                               fill=(255, 236, 168, 215))
            bg.alpha_composite(fx)
        pop_text(bg, 'GIẾT ĐÚNG YÊU QUÁI', int(H * 0.19), min(1, t * 2.4),
                 color=(255, 208, 120), fnt=F_BIG)
        pop_text(bg, '… nhưng lại bị đuổi đi', int(H * 0.29), min(1, (t - 0.45) * 3),
                 color=(255, 118, 104), fnt=font(34))
        return bg.convert('RGB')

    if shot == 'duongxa':
        # 5 THẦY TRÒ ĐI BỘ trải hàng ngang, nhún bước, NỀN CUỘN trái→phải
        bg = bg_duongxa(off=t * 560)
        gy = int(H * 0.90)
        # ĐỘI HÌNH chuẩn (người dùng chốt 21/11) — trái→phải:
        # Sa Tăng · ngựa · Đường Tăng (giữa) · Bát Giới · Ngộ Không (dẫn, đầu bên phải)
        team = [('sa-tang', 'hien', 'mim', 262, False),
                ('bach-long-ma', 'hien', 'mim', 236, False),
                ('duong-tang', 'hien', 'mim', 272, False),
                ('bat-gioi', 'hien', 'mim', 258, False),
                ('ngo-khong', 'quyet', 'mim', 270, False)]
        base = W * 0.08
        step = W * 0.21
        cyc = t * 2.3                                    # số vòng bước trong shot
        order = sorted(range(len(team)), key=lambda i: team[i][3])   # vẽ thấp (xa) trước
        for i in order:
            ma, bc, mi, hh, fl = team[i]
            spr = sprite(ma, bc, mi, h=hh, flip=fl)
            s, lift = walk_tf(spr, (cyc + i * 0.42) % 1.0)
            x = int(base + i * step)
            foot = gy - lift
            soft_shadow(bg, x, gy, w=max(30, int(60 - lift * 0.3)), a=max(20, int(78 - lift * 0.6)))
            bg.alpha_composite(s, (x - s.width // 2, foot - s.height))
        pop_text(bg, 'Ba đệ tử lại đi dọn hậu quả…', int(H * 0.15), min(1, t * 1.5),
                 color=(255, 238, 200), fnt=font(30))
        return bg.convert('RGB')

    if shot == 'batcoc':
        # chuỗi bị bắt: Đường Tăng giữa, 4 bóng đen yêu quái vây + nhãn
        bg = bg_hang(flick=math.sin(t * 16) * 0.5)
        gy = int(H * 0.80)
        d = ImageDraw.Draw(bg, 'RGBA')
        spots = [('tieu-yeu', 0.16, 0.40, 'Kim–Ngân Giác'), ('tieu-yeu-lam', 0.84, 0.38, 'Hồng Hài Nhi'),
                 ('nu-vuong', 0.20, 0.64, 'Nữ Nhi Quốc'), ('tieu-yeu-do', 0.82, 0.64, 'Bọ Cạp Tinh')]
        for i, (ma, px, py, lab) in enumerate(spots):
            if t < 0.08 + i * 0.12:
                continue
            sil = silhouette(sprite(ma, h=250), col=(16, 12, 20))
            paste_mid(bg, sil, int(W * px), int(H * py) + 150)
            tw = d.textlength(lab, font=F_SMALL)
            d.rounded_rectangle([W * px - tw / 2 - 10, H * py + 150, W * px + tw / 2 + 10, H * py + 186],
                                radius=8, fill=(150, 50, 55, 235))
            d.text((W * px - tw / 2, H * py + 154), lab, font=F_SMALL, fill=(255, 255, 255))
        dt = sprite('duong-tang', 'buon', 'buon', h=360, drop=('vu_khi',))
        soft_shadow(bg, int(W * 0.5), gy, w=110, a=110)
        paste_mid(bg, dt, int(W * 0.5), gy)
        pop_text(bg, 'Bị bắt hơn 20 lần', int(H * 0.15), min(1, t * 2), color=(255, 150, 120), fnt=F_BIG)
        return ken(bg.convert('RGB'), 1.0 + 0.06 * t)

    if shot == 'canhmat':
        # cận mặt Đường Tăng điềm tĩnh giữa khói
        bg = bg_hang(flick=0.2)
        dt = sprite('duong-tang', 'hien', 'mim', h=1150, drop=('vu_khi',))
        paste_mid(bg, dt, int(W * 0.5), int(H * 1.42))
        sm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sm)
        for i in range(7):
            ds.ellipse([W * 0.12 * i - 60, H * 0.55 + 26 * i, W * 0.12 * i + 240, H * 0.55 + 190 + 26 * i],
                       fill=(18, 14, 20, 55))
        bg.alpha_composite(sm)
        pop_text(bg, 'Kim Thiền Tử chuyển thế', int(H * 0.12), min(1, t * 2), color=(248, 224, 150), fnt=F_BIG)
        return ken(bg.convert('RGB'), 1.02 + 0.05 * t)

    if shot == 'phanthuong':
        bg = bg_toi()
        ray = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ray)
        cx, cy = int(W * 0.5), int(H * 0.56)
        for a in range(0, 360, 15):
            ang = math.radians(a + t * 20)
            dr.polygon([(cx, cy), (cx + math.cos(ang) * 950, cy + math.sin(ang) * 950),
                        (cx + math.cos(ang + 0.075) * 950, cy + math.sin(ang + 0.075) * 950)],
                       fill=(240, 200, 110, 24))
        bg.alpha_composite(ray)
        dt = sprite('duong-tang', 'hien', 'cuoi', h=520)
        soft_shadow(bg, int(W * 0.5), int(H * 0.84), w=120, a=90)
        paste_mid(bg, dt, int(W * 0.5), int(H * 0.84))
        pop_text(bg, 'PHẦN THƯỞNG cả Tam Giới thèm khát', int(H * 0.19), min(1, t * 1.8),
                 color=(250, 214, 110), fnt=F_BIG)
        return bg.convert('RGB')

    if shot == 'tuchoi':
        bg = bg_toi(vign=True); gy = int(H * 0.84)
        nv = sprite('nu-vuong', 'hien', 'cuoi', h=470)
        dt = sprite('duong-tang', 'hien', 'mim', h=490)
        soft_shadow(bg, int(W * 0.30), gy, w=100, a=85); paste_mid(bg, nv, int(W * 0.30), gy)
        soft_shadow(bg, int(W * 0.72), gy, w=100, a=85); paste_mid(bg, dt, int(W * 0.72), gy)
        pop_text(bg, 'Dâng ngai vàng — ông từ chối', int(H * 0.17), min(1, t * 1.8),
                 color=(255, 224, 150), fnt=F_BIG)
        return ken(bg.convert('RGB'), 1.0 + 0.04 * t)

    if shot == 'kiencuong':
        bg = bg_duongxa(off=120 + t * 60)
        dt = sprite('duong-tang', 'quyet', 'mim', h=560)
        soft_shadow(bg, int(W * 0.5), int(H * 0.86), w=130, a=70)
        paste_mid(bg, dt, int(W * 0.5), int(H * 0.86))
        pop_text(bg, '14 năm · 108.000 dặm\nchưa một lần quay đầu', int(H * 0.18), min(1, t * 1.6),
                 color=(255, 238, 200), fnt=font(34))
        return bg.convert('RGB')

    if shot == 'batgioi':
        bg = bg_duongxa(off=60)
        bgi = sprite('bat-gioi', 'buon', extra.get('mouth', 'noi'), h=560)
        soft_shadow(bg, int(W * 0.5), int(H * 0.86), w=140, a=70)
        paste_mid(bg, bgi, int(W * 0.5), int(H * 0.86))
        pop_text(bg, 'Mất sư phụ rồi —\ncòn thỉnh kinh làm gì?', int(H * 0.17), min(1, t * 1.6),
                 color=(255, 238, 200), fnt=font(33))
        return bg.convert('RGB')

    if shot == 'satang':
        bg = bg_duongxa(off=200)
        st = sprite('sa-tang', 'quyet', extra.get('mouth', 'noi'), h=560)
        soft_shadow(bg, int(W * 0.5), int(H * 0.86), w=140, a=70)
        paste_mid(bg, st, int(W * 0.5), int(H * 0.86))
        pop_text(bg, 'Không sư phụ —\ncả đoàn mất hướng!', int(H * 0.17), min(1, t * 1.6),
                 color=(255, 238, 200), fnt=font(33))
        return bg.convert('RGB')

    if shot == 'vongkimco':
        bg = bg_hang(flick=math.sin(t * 20) * 0.5); gy = int(H * 0.84)
        dt = sprite('duong-tang', 'quyet', 'noi', h=500)
        kh = sprite('ngo-khong', 'buon', 'o', h=470, flip=True)
        soft_shadow(bg, int(W * 0.30), gy, w=100, a=95); paste_mid(bg, dt, int(W * 0.30), gy)
        soft_shadow(bg, int(W * 0.72), gy, w=100, a=95); paste_mid(bg, kh, int(W * 0.72), gy)
        hx, hy = int(W * 0.72), int(gy - 470 * 0.80)
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(gl)
        pulse = 0.6 + 0.4 * abs(math.sin(t * 8))
        for r, al in [(84, 45), (58, 90), (42, 160)]:
            dg.ellipse([hx - r, hy - r * 0.5, hx + r, hy + r * 0.5], outline=(255, 220, 90, int(al * pulse)), width=6)
        for a in range(0, 360, 45):
            ang = math.radians(a)
            dg.line([hx + math.cos(ang) * 52, hy + math.sin(ang) * 30,
                     hx + math.cos(ang) * 82, hy + math.sin(ang) * 48], fill=(255, 210, 90, int(170 * pulse)), width=5)
        bg.alpha_composite(gl)
        pop_text(bg, 'Đức độ — hay VÒNG KIM CÔ?', int(H * 0.15), min(1, t * 1.8), color=(255, 216, 110), fnt=F_BIG)
        return bg.convert('RGB')

    if shot == 'chot':
        bg = bg_duongxa(off=320 + t * 300); gy = int(H * 0.90)
        team = [('sa-tang', 'hien', 'mim', 262, False), ('bach-long-ma', 'hien', 'mim', 236, False),
                ('duong-tang', 'hien', 'cuoi', 272, False), ('bat-gioi', 'hien', 'mim', 258, False),
                ('ngo-khong', 'quyet', 'mim', 270, False)]
        base, step = W * 0.08, W * 0.21; cyc = t * 2.0
        for i in sorted(range(len(team)), key=lambda i: team[i][3]):
            ma, bc, mi, hh, fl = team[i]
            spr = sprite(ma, bc, mi, h=hh, flip=fl)
            s, lift = walk_tf(spr, (cyc + i * 0.42) % 1.0)
            x = int(base + i * step); foot = gy - lift
            soft_shadow(bg, x, gy, w=max(30, int(56 - lift * 0.3)), a=78)
            bg.alpha_composite(s, (x - s.width // 2, foot - s.height))
        pop_text(bg, 'Lãnh đạo bằng đức — hay bằng cái vòng?', int(H * 0.14), min(1, t * 1.5),
                 color=(255, 238, 200), fnt=font(30))
        return bg.convert('RGB')

    if shot == 'cta':
        bg = bg_toi()
        dt = sprite('duong-tang', 'hien', 'mim', h=560)
        paste_mid(bg, dt, int(W * 0.5), int(H * 0.62))
        d = ImageDraw.Draw(bg, 'RGBA')
        btns = [('ĐỨC ĐỘ', (46, 125, 107)), ('VÒNG KIM CÔ', (190, 60, 55))]
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
VOICE = {'dan': 'giahuy', 'tang': 'tiendat', 'bat': 'quangminh', 'satang': 'huuduc'}

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

def drip(amp=0.22):
    n = int(0.22 * SR); t = np.arange(n) / SR
    f = np.linspace(950, 480, n)
    return amp * np.sin(2 * np.pi * f * t) * np.exp(-t * 11)

def thud(amp=0.5):
    n = int(0.28 * SR); t = np.arange(n) / SR
    f = np.linspace(160, 55, n)
    return amp * (np.sin(2 * np.pi * f * t) + 0.4 * np.random.randn(n)) * env(n, 0.002, 0.22)

def put(buf, start_s, wave, g=1.0):
    i = int(start_s * SR); j = min(len(buf), i + len(wave))
    if i < len(buf):
        buf[i:j] += g * wave[:j - i]

def build_audio(voices, seg_starts, seg_shot, total_s):
    buf = np.zeros(int(total_s * SR) + SR)
    # nhạc nền u tịch: drone trầm + ngũ cung thưa
    penta = [329.63, 392.0, 440.0, 523.25, 587.33]
    tt, i = 0.0, 0
    while tt < total_s:
        put(buf, tt, tone(penta[i % 5] / 2, 0.9, amp=0.035, r=0.6))
        tt += 0.85; i += 1
    # drone
    n = int(total_s * SR); t = np.arange(n) / SR
    buf[:n] += 0.03 * np.sin(2 * np.pi * 110 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t))
    # SFX theo shot
    for st, shot, v in zip(seg_starts, seg_shot, voices):
        dur = v.size / SR
        if shot == 'hang':
            k = st
            while k < st + dur:
                put(buf, k, drip()); k += 1.1
        if shot == 'danhnhau':
            # khoe đội hình: một luồng hơi hùng, bỏ loảng xoảng loạn
            put(buf, st, whoosh(0.34))
            put(buf, st + 0.08, tone(146.83, 0.85, amp=0.09, r=0.55))
            put(buf, st + 0.08, tone(220.0, 0.85, amp=0.05, r=0.55))
        if shot in ('tieude', 'bachcot', 'duongxa', 'batcoc', 'canhmat', 'phanthuong',
                    'tuchoi', 'kiencuong', 'vongkimco', 'chot', 'cta'):
            put(buf, st, whoosh(0.32))
            put(buf, st + 0.05, thud(0.35))
        if shot == 'phanthuong':
            put(buf, st + 0.1, tone(293.66, 1.0, amp=0.06, r=0.7))   # hào quang ngân nhẹ
        if shot == 'chuhien':
            # cú đấm trúng yêu quái đúng lúc nó ngã
            put(buf, st, whoosh(0.28))
            put(buf, st + 0.34 * dur, thud(0.6))
            put(buf, st + 0.34 * dur, clash(0.3))
        if shot in ('duoi', 'batgioi', 'satang'):
            put(buf, st, whoosh(0.3))
    # GIỌNG (duck nhạc dưới giọng)
    for st, v in zip(seg_starts, voices):
        # ducking: giảm mọi thứ đang có trong đoạn giọng
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
    for old in glob.glob(os.path.join(WORK, 'f_*.png')):   # xoá frame cũ
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

    # lip-flap cho mọi câu THOẠI nhân vật (Đường Tăng, Bát Giới, Sa Tăng)
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
            # (đã bỏ thanh phụ đề đen theo yêu cầu — lời dẫn chỉ ở storyboard)
            badge(bg, 'ĐƯỜNG TĂNG · Short 01')
            # fade vào/ra mỗi shot (3 khung đầu/cuối)
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
    out = os.path.join(OUTDIR, 'short01-full.mp4')
    subprocess.run([ff, '-y', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', out], check=True, capture_output=True)
    print('XONG →', out, '|', total_f, 'khung ·', '%.1fs' % total_s)

if __name__ == '__main__':
    main()
