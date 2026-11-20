# -*- coding: utf-8 -*-
"""STORYBOARD Short 01 — render MỖI CẢNH 1 HÌNH TĨNH cho trọn ~90 giây.
Mục đích: người dùng duyệt bố cục + mạch kể trước khi làm video.
KHÔNG phụ đề đen, KHÔNG fade — lời dẫn để dưới hình trong artifact.

Dùng lại 7 cảnh đã duyệt (hang, danhnhau, tieude, bachcot, duoi, chuhien, duongxa)
qua short01.render_frame + thêm cảnh HỒI 2 / HỒI 3 / CTA.

Chạy:  PYTHONUTF8=1 python scripts/hoathinh/but/storyboard01.py --web "<thư mục ảnh web>"
Ra:    build/thu-hoathinh/storyboard01/sc_XX.png  +  ảnh web .jpg (nếu có --web)
"""
import os, sys, math, argparse
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
import short01 as S

W, H = S.W, S.H
def _d(bg): return ImageDraw.Draw(bg, 'RGBA')
CREAM = (255, 238, 200)

# ───────── CẢNH DÙNG LẠI (short01.render_frame, không phụ đề/badge/fade) ─────────
def reuse(shot, t, extra=None):
    return S.render_frame(shot, t, extra or {})

# ───────── CẢNH MỚI (HỒI 1 cuối + HỒI 2 + HỒI 3 + CTA) ─────────
def sc_batcoc():
    """Chuỗi bị bắt: Đường Tăng giữa, 4 bóng đen yêu quái vây + nhãn."""
    bg = S.bg_hang(flick=0.3)
    gy = int(H * 0.80)
    spots = [('tieu-yeu', 0.16, 0.40, 'Kim–Ngân Giác'), ('tieu-yeu-lam', 0.84, 0.38, 'Hồng Hài Nhi'),
             ('nu-vuong', 0.20, 0.64, 'Nữ Nhi Quốc'), ('tieu-yeu-do', 0.82, 0.64, 'Bọ Cạp Tinh')]
    for ma, px, py, lab in spots:
        sil = S.silhouette(S.sprite(ma, h=250), col=(16, 12, 20))
        S.paste_mid(bg, sil, int(W * px), int(H * py) + 150)
        d = _d(bg); tw = d.textlength(lab, font=S.F_SMALL)
        d.rounded_rectangle([W * px - tw / 2 - 10, H * py + 150, W * px + tw / 2 + 10, H * py + 186],
                            radius=8, fill=(150, 50, 55, 235))
        d.text((W * px - tw / 2, H * py + 154), lab, font=S.F_SMALL, fill=(255, 255, 255))
    dt = S.sprite('duong-tang', 'buon', 'buon', h=360, drop=('vu_khi',))
    S.soft_shadow(bg, int(W * 0.5), gy, w=110, a=110)
    S.paste_mid(bg, dt, int(W * 0.5), gy)
    S.pop_text(bg, 'Bị bắt hơn 20 lần', int(H * 0.15), 1.0, color=(255, 150, 120), fnt=S.F_BIG)
    return bg.convert('RGB')

def sc_canhmat():
    """Cận mặt Đường Tăng điềm tĩnh giữa khói — mở cú lật."""
    bg = S.bg_hang(flick=0.2)
    dt = S.sprite('duong-tang', 'hien', 'mim', h=1150, drop=('vu_khi',))
    S.paste_mid(bg, dt, int(W * 0.5), int(H * 1.42))      # dán cao → chỉ thấy đầu/vai
    sm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sm)
    for i in range(7):
        ds.ellipse([W * 0.12 * i - 60, H * 0.55 + 26 * i, W * 0.12 * i + 240, H * 0.55 + 190 + 26 * i],
                   fill=(18, 14, 20, 55))
    bg.alpha_composite(sm)
    S.pop_text(bg, 'Kim Thiền Tử chuyển thế', int(H * 0.12), 1.0, color=(248, 224, 150), fnt=S.F_BIG)
    return bg.convert('RGB')

def sc_phanthuong():
    """Cú lật: Đường Tăng là PHẦN THƯỞNG — hào quang vàng."""
    bg = S.bg_toi()
    ray = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ray)
    cx, cy = int(W * 0.5), int(H * 0.56)
    for a in range(0, 360, 15):
        ang = math.radians(a)
        dr.polygon([(cx, cy), (cx + math.cos(ang) * 950, cy + math.sin(ang) * 950),
                    (cx + math.cos(ang + 0.075) * 950, cy + math.sin(ang + 0.075) * 950)],
                   fill=(240, 200, 110, 24))
    bg.alpha_composite(ray)
    dt = S.sprite('duong-tang', 'hien', 'cuoi', h=520)
    S.soft_shadow(bg, int(W * 0.5), int(H * 0.84), w=120, a=90)
    S.paste_mid(bg, dt, int(W * 0.5), int(H * 0.84))
    S.pop_text(bg, 'PHẦN THƯỞNG cả Tam Giới thèm khát', int(H * 0.19), 1.0,
               color=(250, 214, 110), fnt=S.F_BIG)
    return bg.convert('RGB')

def sc_tuchoi():
    """Nữ Nhi Quốc dâng ngai vàng — Đường Tăng từ chối."""
    bg = S.bg_toi(vign=True)
    gy = int(H * 0.84)
    nv = S.sprite('nu-vuong', 'hien', 'cuoi', h=470)
    dt = S.sprite('duong-tang', 'hien', 'mim', h=490)
    S.soft_shadow(bg, int(W * 0.30), gy, w=100, a=85); S.paste_mid(bg, nv, int(W * 0.30), gy)
    S.soft_shadow(bg, int(W * 0.72), gy, w=100, a=85); S.paste_mid(bg, dt, int(W * 0.72), gy)
    S.pop_text(bg, 'Dâng ngai vàng — ông từ chối', int(H * 0.17), 1.0,
               color=(255, 224, 150), fnt=S.F_BIG)
    return bg.convert('RGB')

def sc_kiencuong():
    """Thà chết không chịu — 14 năm, 108.000 dặm."""
    bg = S.bg_duongxa(off=120)
    dt = S.sprite('duong-tang', 'quyet', 'mim', h=560)
    S.soft_shadow(bg, int(W * 0.5), int(H * 0.86), w=130, a=70)
    S.paste_mid(bg, dt, int(W * 0.5), int(H * 0.86))
    S.pop_text(bg, '14 năm · 108.000 dặm\nchưa một lần quay đầu', int(H * 0.18), 1.0,
               color=CREAM, fnt=S.font(34))
    return bg.convert('RGB')

def sc_batgioi():
    """Bát Giới thực dụng: mất sư phụ là đòi giải tán (chứng tỏ sư phụ giữ cả đoàn)."""
    bg = S.bg_duongxa(off=60)
    bgi = S.sprite('bat-gioi', 'buon', 'noi', h=560)
    S.soft_shadow(bg, int(W * 0.5), int(H * 0.86), w=140, a=70)
    S.paste_mid(bg, bgi, int(W * 0.5), int(H * 0.86))
    S.pop_text(bg, 'Mất sư phụ rồi —\ncòn thỉnh kinh làm gì?', int(H * 0.17), 1.0, color=CREAM, fnt=S.font(33))
    return bg.convert('RGB')

def sc_satang():
    """Sa Tăng trung thành phản lại: sư phụ là cái đích, mất người cả đoàn mất hướng."""
    bg = S.bg_duongxa(off=200)
    st = S.sprite('sa-tang', 'quyet', 'noi', h=560)
    S.soft_shadow(bg, int(W * 0.5), int(H * 0.86), w=140, a=70)
    S.paste_mid(bg, st, int(W * 0.5), int(H * 0.86))
    S.pop_text(bg, 'Không sư phụ —\ncả đoàn mất hướng!', int(H * 0.17), 1.0, color=CREAM, fnt=S.font(33))
    return bg.convert('RGB')

def sc_vongkimco():
    """Đường Tăng niệm chú — Ngộ Không ôm đầu vì vòng kim cô siết."""
    bg = S.bg_hang(flick=0.3)
    gy = int(H * 0.84)
    dt = S.sprite('duong-tang', 'quyet', 'noi', h=500)
    kh = S.sprite('ngo-khong', 'buon', 'o', h=470, flip=True)
    S.soft_shadow(bg, int(W * 0.30), gy, w=100, a=95); S.paste_mid(bg, dt, int(W * 0.30), gy)
    S.soft_shadow(bg, int(W * 0.72), gy, w=100, a=95); S.paste_mid(bg, kh, int(W * 0.72), gy)
    # vòng kim cô phát sáng + tia đau trên đầu Ngộ Không
    hx, hy = int(W * 0.72), int(gy - 470 * 0.80)
    gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(gl)
    for r, al in [(84, 45), (58, 90), (42, 160)]:
        dg.ellipse([hx - r, hy - r * 0.5, hx + r, hy + r * 0.5], outline=(255, 220, 90, al), width=6)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        dg.line([hx + math.cos(ang) * 52, hy + math.sin(ang) * 30,
                 hx + math.cos(ang) * 82, hy + math.sin(ang) * 48], fill=(255, 210, 90, 170), width=5)
    bg.alpha_composite(gl)
    S.pop_text(bg, 'Đức độ — hay VÒNG KIM CÔ?', int(H * 0.15), 1.0, color=(255, 216, 110), fnt=S.F_BIG)
    return bg.convert('RGB')

def sc_chot():
    """Chốt: cả đoàn trên đường chiều — câu hỏi lãnh đạo."""
    bg = S.bg_duongxa(off=320)
    gy = int(H * 0.90)
    # trái→phải: Sa Tăng · ngựa · Đường Tăng · Bát Giới · Ngộ Không (người dùng chốt 21/11)
    team = [('sa-tang', 'hien', 'mim', 262, False), ('bach-long-ma', 'hien', 'mim', 236, False),
            ('duong-tang', 'hien', 'cuoi', 272, False), ('bat-gioi', 'hien', 'mim', 258, False),
            ('ngo-khong', 'quyet', 'mim', 270, False)]
    base, step = W * 0.08, W * 0.21
    for i in sorted(range(len(team)), key=lambda i: team[i][3]):
        ma, bc, mi, hh, fl = team[i]
        spr = S.sprite(ma, bc, mi, h=hh, flip=fl)
        x = int(base + i * step)
        S.soft_shadow(bg, x, gy, w=56, a=78)
        S.paste_mid(bg, spr, x, gy)
    S.pop_text(bg, 'Lãnh đạo bằng đức — hay bằng cái vòng?', int(H * 0.14), 1.0,
               color=CREAM, fnt=S.font(30))
    return bg.convert('RGB')

def sc_cta():
    """CTA: cận Đường Tăng + 2 nút ĐỨC ĐỘ / VÒNG KIM CÔ."""
    bg = S.bg_toi()
    dt = S.sprite('duong-tang', 'hien', 'mim', h=560)
    S.paste_mid(bg, dt, int(W * 0.5), int(H * 0.62))
    d = _d(bg)
    btns = [('ĐỨC ĐỘ', (46, 125, 107)), ('VÒNG KIM CÔ', (190, 60, 55))]
    y0 = int(H * 0.70)
    for i, (lab, col) in enumerate(btns):
        hy = y0 + i * 96
        d.rounded_rectangle([int(W * 0.08), hy, int(W * 0.92), hy + 76], radius=18, fill=col + (240,))
        tw = d.textlength(lab, font=S.F_LAB)
        d.text(((W - tw) / 2, hy + 22), lab, font=S.F_LAB, fill=(255, 255, 255))
    S.pop_text(bg, 'Bạn chọn phe nào?', int(H * 0.15), 1.0, color=(248, 224, 150), fnt=S.F_BIG)
    return bg.convert('RGB')

# ───────── DANH SÁCH CẢNH (act, timecode, id, hàm vẽ, lời dẫn) ─────────
SCENES = [
    ('HOOK', '0:00–0:05', 's01', lambda: reuse('hang', 0.6),
     'Một người không biết võ, mắt không nhìn ra yêu quái, bị bắt cóc hơn hai mươi lần.'),
    ('HOOK', '0:05–0:10', 's02', lambda: reuse('danhnhau', 0.85),
     'Vậy mà hắn là trưởng đoàn của đội mạnh nhất Tam Giới. Vì sao?'),
    ('HỒI 1 · Gánh nặng', '0:10–0:13', 's03', lambda: reuse('tieude', 0.9),
     'Nói về sự vô dụng thì… khó ai bằng.'),
    ('HỒI 1 · Gánh nặng', '0:13–0:18', 's04', lambda: reuse('bachcot', 0.97),
     'Bạch Cốt Tinh hóa ba lần — thiếu nữ, bà lão, ông lão — ông tin cả ba.'),
    ('HỒI 1 · Gánh nặng', '0:18–0:22', 's05', lambda: reuse('duoi', 0.7, {'mouth': 'noi'}),
     'Đường Tăng: "Ngộ Không! Con lại giết người, cút về đi!"'),
    ('HỒI 1 · Gánh nặng', '0:22–0:26', 's06', lambda: reuse('chuhien', 0.78),
     'Giết đúng yêu quái — lại bị đuổi đi.'),
    ('HỒI 1 · Gánh nặng', '0:26–0:34', 's07', sc_batcoc,
     'Kim–Ngân Giác nhốt vào bình. Hồng Hài Nhi treo lên nướng. Nữ Nhi Quốc đòi cưới. Bọ Cạp Tinh ép duyên.'),
    ('HỒI 1 · Gánh nặng', '0:34–0:42', 's08', lambda: reuse('duongxa', 0.5),
     'Cứ vài tập, ba đệ tử lại đi dọn hậu quả. Một người sếp như thế — ai mà không ức?'),
    ('HỒI 2 · Cú lật', '0:42–0:49', 's09', sc_canhmat,
     'Nhưng khoan — vì sao ai cũng muốn bắt ông? Vì ông là Kim Thiền Tử chuyển thế.'),
    ('HỒI 2 · Cú lật', '0:49–0:55', 's10', sc_phanthuong,
     'Ăn một miếng thịt ông: trường sinh bất lão. Hắn không yếu — hắn là phần thưởng cả Tam Giới thèm khát.'),
    ('HỒI 2 · Cú lật', '0:55–1:00', 's11', sc_tuchoi,
     'Nữ Nhi Quốc dâng cả ngai vàng lẫn sắc đẹp — ông từ chối.'),
    ('HỒI 2 · Cú lật', '1:00–1:05', 's12', sc_kiencuong,
     'Bọ Cạp Tinh ép chết — ông thà chết không chịu. 14 năm, 108.000 dặm, chưa một lần quay đầu.'),
    ('HỒI 2 · Cú lật', '1:05–1:09', 's13', sc_batgioi,
     '@Bát Giới: "Sư phụ lại bị bắt! Không có người, còn thỉnh kinh làm gì — chia hành lý, ai về nhà nấy cho rồi!"'),
    ('HỒI 2 · Cú lật', '1:09–1:13', 's14', sc_satang,
     '@Sa Tăng: "Nhị sư huynh! Sư phụ là cái đích. Mất người thì cả đoàn mất hướng — còn đi đâu nữa?"'),
    ('HỒI 2 · Cú lật', '1:13–1:17', 's15', sc_vongkimco,
     'Thấy chưa — bỏ sư phụ ra, đội mạnh nhất Tam Giới tan ngay. Nhưng ông giữ Ngộ Không bằng đức độ… hay bằng vòng kim cô?'),
    ('HỒI 3 · Chốt', '1:17–1:25', 's16', sc_chot,
     'Vậy Đường Tăng là gì? Kẻ vô dụng được bảo kê? Hay lãnh đạo cai trị bằng cái vòng trên đầu kẻ mạnh nhất?'),
    ('CTA', '1:25–1:32', 's17', sc_cta,
     'Theo bạn — ông lãnh đạo bằng đức, hay bằng vòng kim cô? Gõ phe bạn 👇'),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--web', default='')      # thư mục xuất ảnh web .jpg (cho artifact)
    a = ap.parse_args()
    ROOT = S.ROOT
    OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'storyboard01')
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(S.WORK, exist_ok=True)
    if a.web:
        os.makedirs(a.web, exist_ok=True)
    meta = []
    for act, tc, sid, fn, loi in SCENES:
        img = fn()
        full = os.path.join(OUT, '%s.png' % sid)
        img.save(full)
        if a.web:
            web = img.resize((480, int(480 * H / W)), Image.LANCZOS).convert('RGB')
            web.save(os.path.join(a.web, '%s.jpg' % sid), quality=82)
        meta.append((sid, act, tc, loi))
        print('  ✓ %s [%s] %s' % (sid, act, tc), flush=True)
    print('XONG %d cảnh → %s' % (len(SCENES), OUT))

if __name__ == '__main__':
    main()
