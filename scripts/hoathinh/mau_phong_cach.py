"""Bảng MẪU PHONG CÁCH hoạt hình 2D cho Anh Văn – Em Võ (để chọn cho series sau Bạch Đằng 938).

Mỗi mẫu là một khung 1920×1080 cùng một tình huống: hai anh em bên cửa sông Bạch Đằng / trên bản đồ.
Ra: build/thu-hoathinh/mau-phong-cach/S1…S6.jpg + bang-mau.jpg (ghép 2×3 có nhãn).
Chỉ học PHONG CÁCH chung của các kênh tham khảo – nhân vật, màu, bố cục đều của kênh mình.

Chạy:  python3 scripts/hoathinh/mau_phong_cach.py
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ngo_quyen_can_canh as cc  # noqa: E402
import song_tu_doi_thoai as st  # noqa: E402
from ngo_quyen_can_canh import cr, hx, mix, stroke  # noqa: E402

ROOT, SS, W, H = cc.ROOT, cc.SS, 1920, 1080
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'mau-phong-cach')
FONT = os.path.join(ROOT, 'fonts', 'BeVietnamPro-Medium.ttf')
FONTB = os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf') if os.path.exists(
    os.path.join(ROOT, 'fonts', 'PlayfairDisplay-ExtraBold.ttf')) else FONT
T0 = 1.0   # thời điểm lấy tư thế


def canvas(col):
    return Image.new('RGBA', (W * SS, H * SS), hx(col) + (255,))


def fin(cv):
    return cv.convert('RGB').resize((W, H), Image.LANCZOS)


def pose(who, talk=False, **kw):
    s = dict(blink=0.0, gaze=(4, 0), smile=0.6)
    if who == 'vo':
        s.update(arms=((150, 40), (40, 90)), brow=0.6, smile=0.9)
    else:
        s.update(arms=((30, 20), (55, 110)))
    s.update(kw)
    return s


def bubble(cv, x, y, w, h, text, tail, size=44, fill='#FFFFFF', ink='#2B2222'):
    d = ImageDraw.Draw(cv)
    d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], radius=28 * SS, fill=hx(fill) + (255,),
                        outline=hx(ink) + (255,), width=int(4 * SS))
    tx, ty = tail
    d.polygon([((x + w * 0.35) * SS, (y + h - 3) * SS), ((x + w * 0.5) * SS, (y + h - 3) * SS), (tx * SS, ty * SS)],
              fill=hx(fill) + (255,), outline=hx(ink) + (255,))
    d.line([((x + w * 0.35) * SS, (y + h - 2) * SS), ((x + w * 0.5) * SS, (y + h - 2) * SS)], fill=hx(fill) + (255,),
           width=int(5 * SS))
    f = ImageFont.truetype(FONT, int(size * SS))
    bb = d.textbbox((0, 0), text, font=f)
    d.text(((x + w / 2) * SS - (bb[2] - bb[0]) / 2, (y + h / 2) * SS - (bb[3] - bb[1]) / 2 - 6 * SS), text, font=f,
           fill=hx(ink) + (255,))


def two(cv, s=1.25, y=930, xs=(760, 1170), pv=None, pa=None):
    st.draw_char(cv, 'vo', xs[0], y, s, 1, T0, pv or pose('vo'))
    st.draw_char(cv, 'van', xs[1], y, s, -1, T0, pa or pose('van'))


def with_globals(**g):
    """Đổi tạm biến toàn cục (viền, màu) của bộ vẽ nhân vật."""
    old = {k: getattr(st, k) for k in g}
    oldink = cc.INK
    for k, v in g.items():
        setattr(st, k, v)
        if k == 'INKC':
            cc.INK = v
    return old, oldink


def restore(old, oldink):
    for k, v in old.items():
        setattr(st, k, v)
    cc.INK = oldink


# ------------------------------------------------------------------ S1 sitcom tối giản (bản đã làm)
def s1():
    cv = st.BG['wide'].copy()
    st.stakes(cv, 0.0)
    two(cv)
    bubble(cv, 520, 300, 420, 120, 'Rồi sao nữa anh?', (700, 560))
    return fin(cv)


# ------------------------------------------------------------------ S2 kiểu "minh họa sách sử" (học Extra History)
def s2():
    cv = canvas('#F4EEDF')
    d = ImageDraw.Draw(cv)
    # sàn phẳng + vài nét đạo cụ nền giản lược
    d.rectangle([0, 860 * SS, W * SS, H * SS], fill=hx('#E2D6BA') + (255,))
    for x in range(0, W, 140):
        d.line([(x * SS, 860 * SS), ((x - 60) * SS, H * SS)], fill=hx('#D4C6A6') + (255,), width=int(2 * SS))
    # bàn + bản đồ trải
    cc.shape(cv, [(1300, 700), (1760, 700), (1820, 860), (1240, 860)], st.S_('#8A5A3A', '#6A4228'), 2.2, 6, 0,
             light=False)
    cc.shape(cv, [(1340, 690), (1720, 680), (1760, 760), (1310, 770)], st.S_('#EAD9A8', '#CDB880'), 2.2, 4, 0,
             light=False, inner=[('line', [(1400, 700), (1450, 740), (1520, 720), (1600, 750)], hx('#4A7AA0') + (255,),
                                  4)])
    old = with_globals(OUTL=2.2, BLUSH=hx('#F6C8B0'), INKC=hx('#1A1414'))
    two(cv, s=1.35, y=900, xs=(620, 1060), pa=pose('van', arms=((30, 20), (90, 150)), book=False))
    restore(*old)
    f = ImageFont.truetype(FONTB, int(54 * SS))
    d.text((90 * SS, 80 * SS), 'NĂM 938', font=f, fill=hx('#B3261E') + (255,))
    return fin(cv)


# ------------------------------------------------------------------ S3 nhân vật đơn giản trên bản đồ (học Oversimplified / History Matters)
def map_bg(cv):
    reg = json.load(open(os.path.join(ROOT, 'data', 'region.json')))
    lon0, lon1, lat0, lat1 = 102.0, 113.0, 17.0, 24.5

    def P(lo, la):
        return ((lo - lon0) / (lon1 - lon0) * W * SS, (lat1 - la) / (lat1 - lat0) * H * SS)
    d = ImageDraw.Draw(cv)
    land = hx('#E6D9A8')
    for g in reg.values():   # chỉ vẽ đất liền, KHÔNG vẽ biên giới hiện đại
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for poly in polys:
            ring = [P(a, b) for a, b in poly[0]]
            d.polygon(ring, fill=land + (255,))
    m = np.asarray(cv.convert('RGB')).astype(np.int16)
    is_land = (np.abs(m - np.array(land)).sum(-1) < 6)
    mi = Image.fromarray((is_land * 255).astype(np.uint8))
    edge = np.asarray(mi.filter(ImageFilter.MaxFilter(9))) > 0
    a = np.asarray(cv).copy()
    a[edge & ~is_land] = hx('#2B2222') + (255,)
    cv.paste(Image.fromarray(a, 'RGBA'))
    # sông Bạch Đằng (gần đúng) + nhãn
    x, y = P(106.75, 20.9)
    d.ellipse([x - 26 * SS, y - 26 * SS, x + 26 * SS, y + 26 * SS], outline=hx('#B3261E') + (255,), width=int(6 * SS))
    f = ImageFont.truetype(FONT, int(30 * SS))
    d.text((x + 34 * SS, y - 20 * SS), 'cửa sông Bạch Đằng', font=f, fill=hx('#2B2222') + (255,))
    d.text((40 * SS, (H - 56) * SS), 'Bản đồ minh họa · bờ biển ngày nay, không phải ranh giới năm 938', font=ImageFont
           .truetype(FONT, int(24 * SS)), fill=hx('#2B2222') + (255,))
    return P


def simple_char(cv, x, y, s, col, hat, f=1, mouth='o'):
    """Người tối giản: đầu tròn da, thân chữ nhật, viền đen dày; mũ quyết định 'ai'."""
    ink = hx('#111111')
    lw = 5

    def C(pts):
        return [(x + f * a * s, y + b * s) for a, b in pts]
    cc.INK = ink
    cc.shape(cv, C([(-34, -120), (34, -120), (38, 0), (-38, 0)]), st.S_(col), lw, 0, 0, light=False)
    cc.shape(cv, C(cc.ellipse_pts(0, -170, 52, 50, 40)), st.S_('#FBE3C8'), lw, 0, 0, light=False)
    for ex in (-16, 18):
        cc.shape(cv, C(cc.ellipse_pts(ex, -176, 7, 9, 16)), dict(b=ink), 0, 0, 0, light=False)
    if mouth == 'o':
        cc.shape(cv, C(cc.ellipse_pts(4, -146, 10, 9, 16)), dict(b=hx('#5A1A1A')), 3, 0, 0, light=False)
    else:
        stroke(cv, C([(-12, -146), (2, -140), (16, -146)]), 4 * s, 4 * s, ink)
    if hat == 'turban':
        cc.shape(cv, C(cr([(-54, -184), (-46, -218), (0, -230), (46, -218), (54, -184), (0, -196)], n=6)),
                 st.S_('#231B18'), lw, 0, 0, light=False)
    elif hat == 'helmet':
        cc.shape(cv, C(cr([(-56, -186), (-48, -222), (0, -236), (48, -222), (56, -186), (0, -194)], n=6)),
                 st.S_('#8A6A2E'), lw, 0, 0, light=False)
        cc.shape(cv, C([(-4, -236), (4, -236), (2, -256), (-2, -256)]), st.S_('#B3261E'), 3, 0, 0, light=False)
    elif hat == 'han':
        cc.shape(cv, C(cr([(-56, -184), (-50, -226), (0, -238), (50, -226), (56, -184)], n=6)), st.S_('#5E5A66'), lw,
                 0, 0, light=False)


def s3():
    cv = canvas('#7EB6D6')
    P = map_bg(cv)
    simple_char(cv, 470, 1010, 1.7, '#E0B44A', 'turban', 1, 'line')
    simple_char(cv, 700, 1010, 1.7, '#C9342A', 'helmet', 1, 'o')
    for i, dx in enumerate((1480, 1600, 1720)):
        simple_char(cv, dx, 1000 + (i % 2) * 30, 1.0, '#33416A', 'han', -1, 'line')
    bubble(cv, 420, 340, 360, 110, 'Lùi tiếp!', (690, 600), size=46)
    cc.INK = hx('#2B2222')
    return fin(cv)


# ------------------------------------------------------------------ S4 nhân vật "bóng tròn" (học countryballs – không dùng cờ)
def ball(cv, x, y, r, col, hat, f=1, look=0.0, mood='calm'):
    ink = hx('#1A1414')
    cc.INK = ink
    pts = cc.ellipse_pts(x, y, r, r * 0.94, 48)
    cc.shape(cv, pts, dict(b=hx(col), s=mix(hx(col), hx('#2A1A20'), 0.25)), 4.5, 16, 0, light=False,
             inner=[('dot', (x - r * 0.35, y - r * 0.4), r * 0.18, (255, 255, 255, 90))])
    for ex in (-0.28, 0.22):
        ex_ = x + f * (ex + look) * r
        cc.shape(cv, cc.ellipse_pts(ex_, y - r * 0.1, r * 0.16, r * (0.2 if mood == 'calm' else 0.24), 24),
                 dict(b=(255, 255, 255)), 3.5, 0, 0, light=False)
    if hat == 'turban':
        cc.shape(cv, cr([(x - r * 1.02, y - r * 0.38), (x - r * 0.8, y - r * 0.95), (x, y - r * 1.12),
                         (x + r * 0.8, y - r * 0.95), (x + r * 1.02, y - r * 0.38), (x, y - r * 0.62)], n=6),
                 st.S_('#231B18'), 4.5, 6, 0, light=False,
                 inner=[('taper', cr([(x - r, y - r * 0.6 + k * r * 0.18), (x, y - r * 0.85 + k * r * 0.18),
                                      (x + r, y - r * 0.6 + k * r * 0.18)], closed=False, n=6), 4, 4,
                         hx('#4A3A34') + (255,)) for k in range(3)])
        stroke(cv, [(x - f * r * 0.9, y - r * 0.5), (x - f * r * 1.5, y - r * 1.1)], 10, 8, hx('#8A4A2A'))
    elif hat == 'helmet':
        cc.shape(cv, cr([(x - r * 1.05, y - r * 0.4), (x - r * 0.8, y - r * 1.0), (x, y - r * 1.18),
                         (x + r * 0.8, y - r * 1.0), (x + r * 1.05, y - r * 0.4), (x, y - r * 0.55)], n=6),
                 st.S_('#8A6A2E', '#62491C'), 4.5, 8, 0, light=False,
                 inner=[('taper', cr([(x - r, y - r * 0.5), (x, y - r * 0.68), (x + r, y - r * 0.5)], closed=False,
                                     n=6), 12, 12, hx('#F3D27A') + (255,))])
        for sg in (-1, 1):
            cc.shape(cv, cr([(x, y - r * 1.16), (x + sg * r * 0.4, y - r * 1.5), (x + sg * r * 0.62, y - r * 1.36),
                             (x + sg * r * 0.3, y - r * 1.22)], n=5), st.S_('#F3D27A'), 3, 2, 0, light=False)
    elif hat == 'han':
        cc.shape(cv, cr([(x - r * 1.04, y - r * 0.35), (x - r * 0.9, y - r * 1.0), (x, y - r * 1.12),
                         (x + r * 0.9, y - r * 1.0), (x + r * 1.04, y - r * 0.35)], n=6), st.S_('#5E5A66'), 4.5, 6, 0,
                 light=False)


def s4():
    cv = st.BG['wide'].copy()
    st.stakes(cv, 11.0)
    ball(cv, 800, 830, 120, '#C9342A', 'helmet', 1, 0.1, 'excited')
    ball(cv, 1120, 840, 110, '#E0B44A', 'turban', -1, 0.1)
    for i, (bx, by) in enumerate(((1440, 560), (1520, 575), (1600, 560))):
        ball(cv, bx, by, 34, '#33416A', 'han', -1)
    bubble(cv, 600, 420, 360, 110, 'Nước rút rồi!', (760, 690), size=46)
    cc.INK = hx('#2B2222')
    return fin(cv)


# ------------------------------------------------------------------ S5 sticker dễ thương viền dày
def s5():
    cv = canvas('#FFE9C8')
    d = ImageDraw.Draw(cv)
    for i in range(14):   # chấm bi nền
        for j in range(8):
            if (i + j) % 2 == 0:
                x, y = 80 + i * 140, 70 + j * 140
                d.ellipse([(x - 16) * SS, (y - 16) * SS, (x + 16) * SS, (y + 16) * SS], fill=hx('#FFD9A6') + (255,))
    lay = Image.new('RGBA', cv.size, (0, 0, 0, 0))
    old = with_globals(OUTL=6.0, BLUSH=hx('#FF8A9A'), INKC=hx('#5A3A2E'),
                       VAN=dict(tunic=st.S_('#F6C445', '#D9A022'), trim=st.S_('#FFF6E0'), belt=st.S_('#8A5A3A')),
                       VO=dict(tunic=st.S_('#FF6B5A', '#D94A3C'), trim=st.S_('#FFE08A'), belt=st.S_('#7A3A2A')))
    st.draw_char(lay, 'vo', 720, 960, 1.45, 1, T0, pose('vo', bigeye=1.0, bounce=0.6))
    st.draw_char(lay, 'van', 1200, 960, 1.45, -1, T0, pose('van', smile=1.0))
    restore(*old)
    # viền trắng kiểu sticker + bóng đổ
    a = lay.getchannel('A')
    halo = a.filter(ImageFilter.MaxFilter(int(14 * SS) * 2 + 1))
    shadow = Image.new('RGBA', cv.size, hx('#C89A6A') + (160,))
    cv.paste(shadow, (int(10 * SS), int(14 * SS)), halo)
    cv.paste(Image.new('RGBA', cv.size, (255, 255, 255, 255)), (0, 0), halo)
    cv.alpha_composite(lay)
    bubble(cv, 900, 160, 640, 130, 'Team Văn hay Team Võ?', (1080, 330), size=44, fill='#FFFFFF', ink='#5A3A2E')
    return fin(cv)


# ------------------------------------------------------------------ S6 chibi sơn mài (nhận diện kênh)
def s6():
    cc.BG.clear()
    cc.build_bg()
    cv = cc.BG['base'].resize((W * SS, H * SS)).copy()
    drum = cc.BG['drum']
    cc.paste(cv, np.asarray(drum), int(960 * SS - drum.width / 2), int(470 * SS - drum.height / 2))
    # vết rạn vỏ trứng (sơn mài)
    rng = np.random.default_rng(8)
    d = ImageDraw.Draw(cv)
    for _ in range(0):
        x, y = rng.uniform(0, W), rng.uniform(780, H)
        pts = [(x, y)]
        for k in range(4):
            x += rng.uniform(-14, 14)
            y += rng.uniform(-10, 10)
            pts.append((x, y))
        d.line([(a * SS, b * SS) for a, b in pts], fill=hx('#E8D6A8') + (150,), width=int(1.6 * SS))
    d.rectangle([0, 860 * SS, W * SS, 866 * SS], fill=hx('#C9A24A') + (255,))
    old = with_globals(OUTL=3.4, INKC=hx('#2A1810'), BLUSH=hx('#E06A5A'),
                       SKIN=st.S_('#F2D2AE', '#C89A70'),
                       VAN=dict(tunic=st.S_('#C9A24A', '#8A6A22'), trim=st.S_('#F2E6CC'), belt=st.S_('#14110F')),
                       VO=dict(tunic=st.S_('#B3261E', '#7A1410'), trim=st.S_('#F3D27A'), belt=st.S_('#14110F')))
    two(cv, s=1.3, y=900, xs=(740, 1180))
    restore(*old)
    f = ImageFont.truetype(FONTB, int(64 * SS))
    tx = 'Ngược Dòng Sử Việt'
    bb = d.textbbox((0, 0), tx, font=f)
    d.text((W * SS / 2 - (bb[2] - bb[0]) / 2, 70 * SS), tx, font=f, fill=hx('#F3D27A') + (255,))
    return fin(cv)


STYLES = [
    ('S1', 'Sitcom tối giản (học Thỏ Bảy Màu)', s1),
    ('S2', 'Minh họa sách sử (học Extra History)', s2),
    ('S3', 'Người tối giản trên bản đồ (học Oversimplified)', s3),
    ('S4', 'Bóng tròn (học Countryballs)', s4),
    ('S5', 'Sticker dễ thương viền dày', s5),
    ('S6', 'Chibi sơn mài (nhận diện kênh)', s6),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    st.build_bg()
    tiles = []
    for code, name, fn in STYLES:
        im = fn()
        im.save(os.path.join(OUT, '%s.jpg' % code), quality=92)
        tiles.append((code, name, im))
        print('xong', code, name, flush=True)
    tw, th = 960, 540
    sheet = Image.new('RGB', (tw * 2 + 30, (th + 64) * 3 + 10), hx('#14110F'))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(FONT, 30)
    for i, (code, name, im) in enumerate(tiles):
        x, y = 10 + (i % 2) * (tw + 10), 10 + (i // 2) * (th + 64)
        d.text((x + 6, y + 8), '%s · %s' % (code, name), font=f, fill=hx('#F3D27A'))
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 54))
    p = os.path.join(OUT, 'bang-mau.jpg')
    sheet.save(p, quality=90)
    print(p)


if __name__ == '__main__':
    main()
