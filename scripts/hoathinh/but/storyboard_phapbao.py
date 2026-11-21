# -*- coding: utf-8 -*-
"""STORYBOARD video dài 'Top 15 Pháp Bảo' — mỗi cảnh 1 khung hình TĨNH 16:9 + lời thoại.
Duyệt bố cục + mạch kể TRƯỚC khi render video. Tái dùng sprite Bộ Bút + item phap_bao. Nền 16:9 vẽ mới.

Chạy:  python scripts/hoathinh/but/storyboard_phapbao.py        # render tất cả khung → PNG + JPG web
"""
import argparse
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

from PIL import Image, ImageDraw
import short01 as S          # sprite(), font()
import phap_bao as pb        # item pháp bảo
from but import Buc

W, H = 1920, 1080
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'storyboard-phapbao')
WEB = os.path.join(ROOT, 'du-an', 'tay-du-ky', 'output', '_prev', 'sb')
CREAM = (255, 240, 205)


def font(sz, bold=True):
    return S.font(sz, bold)


# ───────── helper ─────────
def paste_mid(bg, spr, cx, by, sc=1.0):
    if sc != 1.0:
        spr = spr.resize((max(1, round(spr.width * sc)), max(1, round(spr.height * sc))), Image.LANCZOS)
    bg.alpha_composite(spr, (int(cx - spr.width / 2), int(by - spr.height)))


def soft_shadow(bg, cx, by, w=150, a=84):
    sh = Image.new('RGBA', bg.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - w, by - 18, cx + w, by + 22], fill=(10, 8, 6, a))
    bg.alpha_composite(sh)


def pop_text(bg, text, cx, y, size=56, color=CREAM, stroke=8, sfill=(30, 20, 10), anchor='ma'):
    ImageDraw.Draw(bg).text((cx, y), text, font=font(size), fill=color, anchor=anchor,
                            stroke_width=stroke, stroke_fill=sfill, align='center')


def title_card(bg, big, small=None):
    d = ImageDraw.Draw(bg)
    d.rectangle([0, int(H * 0.30), W, int(H * 0.56)], fill=(20, 16, 24, 205))
    pop_text(bg, big, W // 2, int(H * 0.33), 104, (255, 236, 150), 10, (40, 24, 6))
    if small:
        pop_text(bg, small, W // 2, int(H * 0.49), 42, CREAM, 6)


_titem = {}
def treasure_img(ma, h=320):
    key = (ma, h)
    if key in _titem:
        return _titem[key]
    fn = pb.ITEMS[ma][0]
    b = Buc(pb.W, pb.H, nen=None, D=dict(ngoai=9.0, trong=5.0, ct=3.4), scale=3.0)
    fn(b)
    b.chot_vien()
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, '_t_%s.png' % ma)
    b.luu(tmp)
    im = Image.open(tmp).convert('RGBA')
    im = im.crop(im.getbbox())
    s = h / im.height
    im = im.resize((max(1, round(im.width * s)), h), Image.LANCZOS)
    _titem[key] = im
    return im


def memory_card(bg, ma, cx, cy, size=430):
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2
    d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y1 + 14], 30, fill=(0, 0, 0, 70))
    d.rounded_rectangle([x0, y0, x1, y1], 30, fill=(250, 245, 233, 255), outline=(40, 32, 22, 255), width=8)
    it = treasure_img(ma, h=int(size * 0.72))
    bg.alpha_composite(it, (int(cx - it.width / 2), int(cy - it.height / 2)))


def tier_of(diem):
    v = float(diem)
    return 'do' if v >= 8.5 else ('cam' if v >= 7.0 else 'vang')


def score_badge(bg, cx, cy, diem):
    col = {'do': (190, 55, 44), 'cam': (196, 140, 24), 'vang': (150, 130, 60)}[tier_of(diem)]
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle([cx - 120, cy - 50, cx + 120, cy + 50], 18, fill=col + (255,))
    pop_text(bg, diem, cx, cy - 42, 70, (255, 255, 255), 0)


# ───────── NỀN 16:9 ─────────
def _band(d, y0, y1, c):
    d.rectangle([0, y0, W, y1], fill=c + (255,))


def bg_quan_tra(light='xe'):
    sky = {'trua': (178, 214, 230), 'xe': (242, 214, 158), 'chieu': (238, 176, 128)}[light]
    im = Image.new('RGBA', (W, H), sky + (255,))
    d = ImageDraw.Draw(im)
    _band(d, 0, int(H * 0.30), tuple(min(255, c + 12) for c in sky))
    d.ellipse([W * 0.70, H * 0.06, W * 0.84, H * 0.22], fill=(252, 236, 182, 255))
    for cx, cw, col in [(W * 0.2, 520, (150, 170, 128)), (W * 0.65, 640, (138, 158, 118)), (W * 0.9, 460, (150, 170, 128))]:
        d.ellipse([cx - cw / 2, H * 0.52 - 150, cx + cw / 2, H * 0.52 + 160], fill=col + (255,))
    gy = int(H * 0.66)
    d.rectangle([0, gy, W, H], fill=(196, 168, 112, 255))
    d.line([0, gy, W, gy], fill=(150, 126, 80, 255), width=6)
    d.rectangle([W * 0.10, gy - 300, W * 0.10 + 46, gy], fill=(120, 86, 48, 255))
    for cx, cy, r in [(W * 0.09, gy - 360, 180), (W * 0.17, gy - 410, 160), (W * 0.03, gy - 300, 140)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(84, 142, 86, 255))
    d.rounded_rectangle([W * 0.40, gy - 30, W * 0.60, gy + 40], 16, fill=(150, 104, 58, 255), outline=(104, 70, 36, 255), width=6)
    d.line([W * 0.82, 0, W * 0.82, H * 0.22], fill=(90, 60, 40, 255), width=5)
    d.ellipse([W * 0.80, H * 0.20, W * 0.84, H * 0.30], fill=(214, 92, 70, 255), outline=(150, 50, 40, 255), width=4)
    return im


def bg_troi(*_):
    im = Image.new('RGBA', (W, H), (176, 206, 228, 255))
    d = ImageDraw.Draw(im)
    _band(d, 0, int(H * 0.4), (196, 220, 236))
    for cx, cy, r in [(W * 0.2, H * 0.3, 120), (W * 0.33, H * 0.26, 90), (W * 0.7, H * 0.2, 140), (W * 0.82, H * 0.3, 100)]:
        for dx in (-r * 0.7, 0, r * 0.7):
            d.ellipse([cx + dx - r * 0.7, cy - r * 0.55, cx + dx + r * 0.7, cy + r * 0.55], fill=(248, 250, 253, 255))
    d.ellipse([-200, H * 0.72, W + 200, H * 1.4], fill=(226, 236, 246, 255))
    return im


def bg_hang(tint=(44, 34, 46)):
    im = Image.new('RGBA', (W, H), tint + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, int(H * 0.26)], fill=tuple(max(0, c - 10) for c in tint) + (255,))
    for x in range(40, W, 150):
        d.polygon([(x, 0), (x + 48, 0), (x + 24, 110)], fill=tuple(c + 14 for c in tint) + (255,))
    gy = int(H * 0.72)
    d.rectangle([0, gy, W, H], fill=tuple(c + 10 for c in tint) + (255,))
    d.line([0, gy, W, gy], fill=tuple(max(0, c - 8) for c in tint) + (255,), width=6)
    for tx in (90, W - 90):
        d.polygon([(tx - 20, H * 0.42), (tx + 20, H * 0.42), (tx, H * 0.42 - 64)], fill=(232, 150, 50, 255))
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse([tx - 160, H * 0.42 - 170, tx + 160, H * 0.42 + 150], fill=(230, 150, 60, 26))
        im.alpha_composite(gl)
    return im


def bg_nui(*_):
    im = Image.new('RGBA', (W, H), (236, 204, 152, 255))
    d = ImageDraw.Draw(im)
    _band(d, 0, int(H * 0.32), (242, 210, 154))
    d.ellipse([W * 0.66, H * 0.10, W * 0.80, H * 0.24], fill=(250, 232, 180, 255))
    for cy, col in [(H * 0.50, (150, 150, 112)), (H * 0.56, (128, 132, 96))]:
        for hx in range(-200, W + 200, 360):
            d.polygon([(hx, cy + 120), (hx + 180, cy - 120), (hx + 360, cy + 120)], fill=col + (255,))
    gy = int(H * 0.66)
    d.rectangle([0, gy, W, H], fill=(176, 150, 104, 255))
    d.line([0, gy, W, gy], fill=(140, 118, 78, 255), width=6)
    d.polygon([(W * 0.42, gy), (W * 0.58, gy), (W * 0.82, H), (W * 0.18, H)], fill=(198, 172, 120, 255))
    return im


def bg_lua(arg=None):
    smoke = (arg == 'khoi')
    sky = (74, 64, 70) if smoke else (122, 42, 32)
    im = Image.new('RGBA', (W, H), sky + (255,))
    d = ImageDraw.Draw(im)
    _band(d, 0, int(H * 0.30), tuple(min(255, c + 18) for c in sky))
    d.polygon([(0, H), (W * 0.30, H * 0.30), (W * 0.60, H)], fill=(50, 30, 30, 255))
    d.polygon([(W * 0.40, H), (W * 0.72, H * 0.26), (W, H)], fill=(44, 26, 26, 255))
    gy = int(H * 0.72)
    d.rectangle([0, gy, W, H], fill=(60, 32, 28, 255))
    base = (96, 90, 86) if smoke else (232, 120, 40)
    tip = (158, 156, 148) if smoke else (248, 202, 92)
    for x in range(0, W, 150):
        d.polygon([(x, H), (x + 40, H - 118), (x + 80, H)], fill=base + (255,))
        d.polygon([(x + 22, H), (x + 40, H - 66), (x + 58, H)], fill=tip + (255,))
    if not smoke:
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse([-200, H * 0.6, W + 200, H * 1.3], fill=(240, 120, 40, 40))
        im.alpha_composite(gl)
    return im


def bg_song(*_):
    im = Image.new('RGBA', (W, H), (200, 216, 214, 255))
    d = ImageDraw.Draw(im)
    _band(d, 0, int(H * 0.34), (212, 226, 222))
    wy = int(H * 0.44)
    for i, c in enumerate([(120, 160, 162), (104, 146, 150), (90, 132, 138)]):
        d.rectangle([0, wy + i * 44, W, wy + (i + 1) * 44 + 44], fill=c + (255,))
    gy = int(H * 0.66)
    d.rectangle([0, gy, W, H], fill=(206, 186, 140, 255))
    d.line([0, gy, W, gy], fill=(170, 150, 108, 255), width=6)
    return im


BG = {'quan_tra': bg_quan_tra, 'troi': bg_troi, 'hang': bg_hang, 'nui': bg_nui, 'lua': bg_lua, 'song': bg_song}


def make_bg(spec):
    return BG[spec[0]](*spec[1:])


# ───────── DỰNG 1 KHUNG ─────────
def build(scn):
    bg = make_bg(scn['bg'])
    gy = int(H * 0.96)
    for ma, bc, mi, xf, hh in scn.get('chars', []):
        spr = S.sprite(ma, bc, mi, h=hh)
        soft_shadow(bg, int(W * xf), gy, w=int(hh * 0.33))
        paste_mid(bg, spr, int(W * xf), gy)
    if scn.get('card'):
        cx = int(W * scn.get('cardx', 0.70))
        memory_card(bg, scn['card'], cx, int(H * 0.45), scn.get('cardsz', 440))
        if scn.get('diem'):
            score_badge(bg, cx, int(H * 0.80), scn['diem'])
    if scn.get('big'):
        title_card(bg, scn['big'], scn.get('small'))
    elif scn.get('title'):
        pop_text(bg, scn['title'], W // 2, int(H * 0.055), scn.get('tsize', 54), (255, 234, 150), 8)
    return bg.convert('RGB')


# ───────── DANH SÁCH KHUNG (act, timecode, id, cfg, thoại) ─────────
T = [
('HOOK', '0:00–0:45', 's01',
 {'bg': ('quan_tra', 'xe'),
  'chars': [('sa-tang', 'hien', 'mim', 0.13, 330), ('bach-long-ma', 'hien', 'mim', 0.30, 300),
            ('duong-tang', 'hien', 'cuoi', 0.49, 340), ('bat-gioi', 'quyet', 'noi', 0.67, 330),
            ('ngo-khong', 'quyet', 'noi', 0.85, 350)],
  'big': 'TOP 15 PHÁP BẢO', 'small': 'Thầy trò tranh luận — pháp bảo nào MẠNH NHẤT Tây Du?'},
 'Ngộ Không: "Gậy Như Ý của lão Tôn, một gậy sập cả Thiên Cung!" — Sa Tăng: "Ta xếp hạng đàng hoàng. '
 'Đại sư huynh… e là hôm nay gậy của ngươi KHÔNG đứng số một đâu." — Ngộ Không: "HẢ?! Món nào dám?!"'),
('① ② Vũ khí thầy trò', '~1:00', 's02',
 {'bg': ('song',), 'chars': [('sa-tang', 'hien', 'noi', 0.18, 480), ('bat-gioi', 'vui', 'noi', 0.37, 490)],
  'card': 'dinh_ba', 'cardx': 0.74, 'diem': '6.0', 'title': '① Bảo Trượng 5.0  ·  ② Đinh Ba 6.0'},
 'Sa Tăng: "Bảo Trượng — Lỗ Ban đẽo từ gỗ sa-la cung trăng, 5.048 cân." Bát Giới: "Đinh Ba cũng Lão Quân rèn! '
 'Nhưng cả hai là đồ giữ nhà thôi — so đồ đỉnh phía sau thì xách dép."'),
('③ Gậy Như Ý', '~2:05', 's03',
 {'bg': ('troi',), 'chars': [('ngo-khong', 'vui', 'cuoi_mo', 0.26, 560)],
  'card': 'gay_nhu_y', 'cardx': 0.70, 'diem': '9.0', 'title': 'GẬY NHƯ Ý — 13.500 cân'},
 'Ngộ Không: "Định Hải Thần Châm trấn đáy Đông Hải — một vạn ba nghìn năm trăm cân!" '
 'Sa Tăng: "Toàn đỉnh, nhưng trục khắc chế yếu — chín, không phải mười." (FANFARE)'),
('④ Vòng Kim Cô', '~3:00', 's04',
 {'bg': ('quan_tra', 'xe'), 'chars': [('duong-tang', 'quyet', 'noi', 0.22, 520), ('ngo-khong', 'buon', 'o', 0.42, 470)],
  'card': 'vong_kim_co', 'cardx': 0.74, 'diem': '7.5', 'title': '④ Vòng Kim Cô'},
 'Bát Giới: "Sư phụ chỉ cần lẩm bẩm ba câu — đại sư huynh lăn ra ôm đầu! Pháp bảo mạnh nhất Tây Du nè!" '
 'Đường Tăng: "Vũ khí lợi hại nhất, đôi khi để GIỮ người lại."'),
('⑤ Tịnh Bình Dương Liễu', '~3:55', 's05',
 {'bg': ('troi',), 'chars': [('sa-tang', 'hien', 'noi', 0.24, 540)],
  'card': 'tinh_binh', 'cardx': 0.70, 'diem': '8.0', 'title': '⑤ Tịnh Bình Dương Liễu'},
 'Sa Tăng: "Một giọt cam lồ — cải tử hoàn sinh." Ngộ Không: "Bình đó chứa cả một biển nước, thu Hồng Hài Nhi. '
 'Nhỏ mà chứa cả đại dương!"'),
('⑥ Kim Nhiêu', '~4:55', 's06',
 {'bg': ('hang', (58, 46, 20)), 'chars': [('ngo-khong', 'buon', 'o', 0.24, 540)],
  'card': 'kim_nhieu', 'cardx': 0.70, 'diem': '8.5', 'title': '⑥ Kim Nhiêu — úp kín'},
 'Ngộ Không: "Kim Nhiêu úp ta kín mít, gậy chọc không thủng." Bát Giới: "Phải mời hăm tám tinh tú, Kháng Kim Long '
 'lấy sừng chọc thủng mới lôi được đại sư huynh ra!"'),
('⑦ ⑧ Lý Thiên Vương', '~6:05', 's07',
 {'bg': ('troi',), 'chars': [('sa-tang', 'hien', 'noi', 0.20, 500), ('ngo-khong', 'quyet', 'noi', 0.40, 470)],
  'card': 'chieu_yeu_kinh', 'cardx': 0.74, 'diem': '6.5', 'title': '⑦ Gương 6.5  vs  ⑧ Tháp 6.0'},
 'Sa Tăng: "Gương soi mọi yêu lộ nguyên hình; tháp thu người vào trong." Ngộ Không: "Sáu rưỡi cho cái gương soi '
 'thật–giả cả thiên hạ? Oan cho nó! Để khán giả phân xử."'),
('⑨ Hoảng Kim Thằng', '~7:15', 's09',
 {'bg': ('nui',), 'chars': [('ngo-khong', 'buon', 'noi', 0.22, 520), ('bat-gioi', 'vui', 'noi', 0.42, 500)],
  'card': 'hoang_kim_thang', 'cardx': 0.74, 'diem': '7.0', 'title': '⑨ Hoảng Kim Thằng'},
 'Ngộ Không: "Dây vàng trói cả thần tiên, càng giãy càng chặt." Bát Giới (ghi sổ): "Bị trói — một lần nữa!" '
 'Ngộ Không: "Còn ngươi? Bị Hồng Hài Nhi tóm bỏ bao, đòi hấp chín!"'),
('⑩ Hồ Lô gọi tên', '~8:20', 's10',
 {'bg': ('hang', (52, 36, 58)), 'chars': [('bat-gioi', 'vui', 'noi', 0.22, 500), ('ngo-khong', 'buon', 'o', 0.42, 470)],
  'card': 'ho_lo', 'cardx': 0.74, 'diem': '8.5', 'title': '⑩ Hồ Lô Tử Kim'},
 'Bát Giới: "Gọi đúng tên, ngươi dạ một tiếng là bị hút tọt vào, một lát hoá nước!" Ngộ Không: "Ta tráo hồ lô giả, '
 'xưng tên đảo Giả Hành Tôn mới thoát — đấu TRÍ chứ bộ!"'),
('⑪ Quạt Ba Tiêu', '~9:15', 's11',
 {'bg': ('lua',), 'chars': [('sa-tang', 'hien', 'noi', 0.22, 520), ('ngo-khong', 'ngac', 'o', 0.42, 470)],
  'card': 'quat_ba_tieu', 'cardx': 0.74, 'diem': '8.0', 'title': '⑪ Quạt Ba Tiêu'},
 'Sa Tăng: "Một phẩy dập tám trăm dặm lửa Hoả Diệm Sơn." Ngộ Không: "Phẩy vào người thì bay tám vạn bốn nghìn dặm! '
 'Phải nuốt Định Phong Đan mới đứng yên."'),
('⑫ Tam Muội Chân Hoả', '~10:05', 's12',
 {'bg': ('lua',), 'chars': [('ngo-khong', 'buon', 'noi', 0.26, 540)],
  'card': 'tam_muoi', 'cardx': 0.70, 'diem': '7.5', 'title': '⑫ Tam Muội Chân Hoả'},
 'Ngộ Không: "Lửa tam muội, nước dội càng cháy — ta suýt toi mạng, phải cầu Bồ Tát." Bát Giới: "Một đứa con nít mà '
 'hành đại sư huynh — hay tại đại ca già rồi ha?"'),
('⑬ Nhân Sâm Quả', '~11:00', 's13',
 {'bg': ('quan_tra', 'trua'), 'chars': [('duong-tang', 'hien', 'noi', 0.22, 520), ('bat-gioi', 'vui', 'cuoi_mo', 0.42, 500)],
  'card': 'nhan_sam', 'cardx': 0.74, 'diem': '7.0', 'title': '⑬ Nhân Sâm Quả'},
 'Đường Tăng: "Nhân Sâm Quả của Trấn Nguyên Đại Tiên — Địa Tiên chi tổ." Bát Giới: "Ăn một quả bốn vạn bảy nghìn năm! '
 'Mà con nuốt chửng, tiếc đứt ruột!"'),
('⑭ Cẩm Lan Cà Sa', '~11:40', 's14',
 {'bg': ('lua', 'khoi'), 'chars': [('duong-tang', 'hien', 'noi', 0.22, 520), ('bat-gioi', 'vui', 'noi', 0.42, 500)],
  'card': 'ca_sa', 'cardx': 0.74, 'diem': '4.0', 'title': '⑭ Cẩm Lan Cà Sa (nghỉ hài)'},
 'Bát Giới: "Cà sa khoe một phát, ông sư già tham đốt cả thiền viện để cướp!" Ngộ Không: "Bốn điểm! Đồ mạnh kiểu '
 'phá hoại nội bộ ha!"'),
('⑮ Kim Cang Trác · CÚ LẬT', '~13:30', 's15',
 {'bg': ('hang', (40, 46, 58)), 'chars': [('ngo-khong', 'buon', 'o', 0.24, 540)],
  'card': 'kim_cang_trac', 'cardx': 0.70, 'diem': '9.5', 'title': 'CÚ LẬT: KIM CANG TRÁC SỐ 1'},
 'Ngộ Không: "Kim Cang Trác hút bay gậy Như Ý của ta — ta trơ tay!" Sa Tăng: "Con trâu xanh Lão Quân cưỡi. Chín rưỡi, '
 'cao nhất bảng!" Ngộ Không (lặng người): "Kẻ hạ ta năm xưa… là một cái vòng của con trâu."'),
('CHUNG KẾT · CTA', '~15:00', 's16',
 {'bg': ('quan_tra', 'chieu'),
  'chars': [('sa-tang', 'hien', 'mim', 0.13, 320), ('bach-long-ma', 'hien', 'mim', 0.30, 290),
            ('duong-tang', 'hien', 'cuoi', 0.49, 330), ('bat-gioi', 'vui', 'cuoi_mo', 0.67, 320),
            ('ngo-khong', 'quyet', 'mim', 0.85, 340)],
  'big': 'SỐ 1 LÀ MÓN NÀO?', 'small': 'Kim Cang Trác · Gậy Như Ý · hay Hồ Lô? — Gõ phe của bạn 👇'},
 'Bát Giới (đọc sổ): "Đại sư huynh bị: niệm chú, úp chuông, hút hồ lô, trói dây, thổi bay, thiêu, hút mất gậy — '
 'BẢY LẦN!" Đường Tăng: "Thứ hợp cảnh, mới là thứ mạnh nhất." Sa Tăng: "Theo bạn số 1 là món nào?"'),
]


# ───────── HIỆU ỨNG MINH HỌA SỨC MẠNH (khung action sau mỗi pháp bảo) ─────────
def _pop(bg, text, size=54, color=(255, 230, 120)):
    pop_text(bg, text, W // 2, int(H * 0.055), size, color, 9)


def _rings(d, cx, cy, radii, col, w=8, flat=0.4):
    for r in radii:
        d.ellipse([cx - r, cy - r * flat, cx + r, cy + r * flat], outline=col, width=w)


def _speed(d, x0, y0, ux, uy, n=12, gap=28, L=160, col=(255, 255, 255, 140), w=6):
    nx, ny = -uy, ux
    for i in range(-n // 2, n // 2):
        ox, oy = nx * i * gap, ny * i * gap
        d.line([(x0 + ox, y0 + oy), (x0 + ox - ux * L, y0 + oy - uy * L)], fill=col, width=w)


def _tre(ma, h):
    return treasure_img(ma, h)


def demo_gay():
    bg = bg_troi(); d = ImageDraw.Draw(bg, 'RGBA')
    p0, p1 = (360, 1010), (1480, 150)
    ux, uy = (p1[0] - p0[0]) / 1400.0, (p1[1] - p0[1]) / 1400.0
    _speed(d, 920, 560, ux, uy, n=10, gap=36, L=190, col=(255, 255, 255, 120))
    d.line([p0, p1], fill=(196, 66, 58), width=34)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); dx, dy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    for t0, t1 in ((0, 0.10), (0.90, 1.0)):
        d.line([(p0[0] + dx * L * t0, p0[1] + dy * L * t0), (p0[0] + dx * L * t1, p0[1] + dy * L * t1)], fill=(240, 194, 58), width=40)
    _rings(d, 360, 1010, [90, 160, 240, 330], (90, 150, 170, 210), 9)
    paste_mid(bg, S.sprite('ngo-khong', 'quyet', 'noi', h=360), 300, int(H * 0.99))
    _pop(bg, 'DÀI RA CHỌC TRỜI · ĐẬP TRẤN ĐÔNG HẢI', 50)
    return bg.convert('RGB')


def demo_vong():
    bg = bg_quan_tra('xe'); d = ImageDraw.Draw(bg, 'RGBA'); gy = int(H * 0.96)
    dt = S.sprite('duong-tang', 'quyet', 'noi', h=520); soft_shadow(bg, int(W * 0.26), gy); paste_mid(bg, dt, int(W * 0.26), gy)
    nk = S.sprite('ngo-khong', 'buon', 'o', h=430, flip=True); soft_shadow(bg, int(W * 0.68), gy); paste_mid(bg, nk, int(W * 0.68), gy)
    hx, hy = int(W * 0.26), int(gy - 520 * 0.82)
    for r in (70, 120, 180):
        d.arc([hx - r, hy - r, hx + r, hy + r], 300, 60, fill=(120, 90, 160, 150), width=6)
    kx, ky = int(W * 0.68), int(gy - 430 * 0.84)
    # vòng kim cô SIẾT đầu: vòng vàng sáng, dày, nhiều lớp + chớp sáng
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dgl = ImageDraw.Draw(glow)
    dgl.ellipse([kx - 150, ky - 150, kx + 150, ky + 150], fill=(255, 220, 90, 46))
    bg.alpha_composite(glow)
    for r, al, wd in ((96, 150, 10), (74, 210, 12), (52, 255, 14)):
        d.ellipse([kx - r, ky - r * 0.55, kx + r, ky + r * 0.55], outline=(255, 214, 80, al), width=wd)
    # tia đau toả ra + chấm than
    for a in range(0, 360, 30):
        an = math.radians(a)
        d.line([kx + math.cos(an) * 60, ky + math.sin(an) * 36, kx + math.cos(an) * 104, ky + math.sin(an) * 62],
               fill=(255, 120, 70, 230), width=7)
    for sx in (-170, 170):
        d.text((kx + sx, ky - 120), '!', font=font(90), fill=(255, 70, 60), stroke_width=6, stroke_fill=(60, 10, 10))
    _pop(bg, 'TỤNG CHÚ · SIẾT ĐẦU KHUẤT PHỤC', 52)
    return bg.convert('RGB')


def demo_tinhbinh():
    bg = bg_troi(); d = ImageDraw.Draw(bg, 'RGBA')
    tb = _tre('tinh_binh', 340).rotate(-50, expand=True); bg.alpha_composite(tb, (int(W * 0.18), int(H * 0.12)))
    d.polygon([(int(W * 0.34), int(H * 0.30)), (int(W * 0.44), int(H * 0.30)), (W, int(H * 0.78)), (W, H), (0, H), (0, int(H * 0.74))], fill=(120, 170, 200, 185))
    for yy in (0.66, 0.80, 0.92):
        d.arc([int(W * 0.15), int(H * yy) - 40, int(W * 1.1), int(H * yy) + 130], 180, 360, fill=(205, 228, 238, 190), width=8)
    _pop(bg, 'NGHIÊNG TAY · ĐỔ RA CẢ BIỂN', 52)
    return bg.convert('RGB')


def demo_kimnhieu():
    bg = bg_hang((58, 46, 20)); d = ImageDraw.Draw(bg, 'RGBA'); cx, cy = int(W * 0.5), int(H * 0.5)
    kn = _tre('kim_nhieu', 560); bg.alpha_composite(kn, (int(cx - kn.width / 2), int(cy - kn.height / 2)))
    for a in (-44, -22, 0, 22, 44):
        an = math.radians(a - 90)
        d.line([cx + math.cos(an) * 300, cy + math.sin(an) * 300, cx + math.cos(an) * 362, cy + math.sin(an) * 362], fill=(255, 230, 120, 150), width=5)
    _pop(bg, 'ÚP KÍN · GẬY CHỌC KHÔNG THỦNG', 50)
    return bg.convert('RGB')


def demo_guong():
    bg = bg_troi(); d = ImageDraw.Draw(bg, 'RGBA')
    g = _tre('chieu_yeu_kinh', 360); bg.alpha_composite(g, (int(W * 0.08), int(H * 0.30)))
    d.polygon([(int(W * 0.26), int(H * 0.42)), (W, int(H * 0.20)), (W, int(H * 0.82))], fill=(255, 245, 200, 85))
    sil = S.silhouette(S.sprite('bach-cot-tinh', 'quyet', 'mim', h=470), col=(30, 26, 36))
    paste_mid(bg, sil, int(W * 0.78), int(H * 0.96))
    _pop(bg, 'CHIẾU MỘT CÁI · LỘ NGUYÊN HÌNH', 52)
    return bg.convert('RGB')


def demo_thang():
    bg = bg_nui(); d = ImageDraw.Draw(bg, 'RGBA'); gy = int(H * 0.96)
    nk = S.sprite('ngo-khong', 'buon', 'o', h=540); soft_shadow(bg, int(W * 0.5), gy); paste_mid(bg, nk, int(W * 0.5), gy)
    cx = int(W * 0.5)
    for yy in (0.50, 0.62, 0.74):
        d.ellipse([cx - 155, int(H * yy) - 26, cx + 155, int(H * yy) + 26], outline=(236, 196, 60), width=14)
    _pop(bg, 'TRÓI CẢ THẦN TIÊN · CÀNG GIÃY CÀNG CHẶT', 46)
    return bg.convert('RGB')


def demo_holo():
    bg = bg_hang((52, 36, 58)); d = ImageDraw.Draw(bg, 'RGBA')
    hl = _tre('ho_lo', 460); cx, cy = int(W * 0.66), int(H * 0.5); bg.alpha_composite(hl, (int(cx - hl.width / 2), int(cy - hl.height / 2)))
    sp = [(cx - 250 + math.cos(i * 0.6) * (120 - i * 5), int(H * 0.30) + math.sin(i * 0.6) * (90 - i * 4) + i * 7) for i in range(16)]
    d.line(sp, fill=(230, 200, 120, 210), width=6)
    nk = S.sprite('ngo-khong', 'ngac', 'o', h=150).rotate(35, expand=True); bg.alpha_composite(nk, (cx - 150, cy - 60))
    _pop(bg, 'GỌI TÊN — HÚT TỌT VÀO TRONG', 50)
    return bg.convert('RGB')


def demo_quat():
    bg = bg_lua(); d = ImageDraw.Draw(bg, 'RGBA'); gy = int(H * 0.96)
    q = _tre('quat_ba_tieu', 360); bg.alpha_composite(q, (int(W * 0.12), int(gy - 360)))
    for yy in (0.30, 0.45, 0.60):
        for x in range(int(W * 0.30), int(W * 0.92), 120):
            d.arc([x, int(H * yy) - 44, x + 190, int(H * yy) + 44], 200, 340, fill=(255, 255, 255, 120), width=6)
    nk = S.sprite('ngo-khong', 'ngac', 'o', h=300, flip=True).rotate(-28, expand=True)
    bg.alpha_composite(nk, (int(W * 0.74), int(H * 0.38)))
    _speed(d, int(W * 0.82), int(H * 0.50), 1, -0.18, n=6, gap=32, L=200, col=(255, 255, 255, 110))
    _pop(bg, 'QUẠT MỘT PHÁT · BAY 84.000 DẶM', 50)
    return bg.convert('RGB')


def demo_tammuoi():
    bg = bg_lua(); d = ImageDraw.Draw(bg, 'RGBA'); gy = int(H * 0.96)
    for x in range(int(W * 0.5), W, 90):
        d.polygon([(x, H), (x + 30, int(H * 0.48)), (x + 60, H)], fill=(240, 120, 40, 225))
        d.polygon([(x + 18, H), (x + 30, int(H * 0.60)), (x + 42, H)], fill=(250, 205, 90, 235))
    nk = S.sprite('ngo-khong', 'buon', 'noi', h=480); soft_shadow(bg, int(W * 0.24), gy); paste_mid(bg, nk, int(W * 0.24), gy)
    _pop(bg, 'NƯỚC DỘI CÀNG CHÁY', 56)
    return bg.convert('RGB')


def demo_nhansam():
    bg = bg_quan_tra('trua'); gy = int(H * 0.96)
    bgi = S.sprite('bat-gioi', 'vui', 'cuoi_mo', h=560); soft_shadow(bg, int(W * 0.4), gy); paste_mid(bg, bgi, int(W * 0.4), gy)
    ns = _tre('nhan_sam', 240); bg.alpha_composite(ns, (int(W * 0.58), int(H * 0.38)))
    _pop(bg, 'NUỐT MỘT QUẢ · +47.000 NĂM', 52)
    return bg.convert('RGB')


def demo_casa():
    bg = bg_lua('khoi'); d = ImageDraw.Draw(bg, 'RGBA')
    for x in range(0, W, 110):
        d.polygon([(x, H), (x + 34, int(H * 0.54)), (x + 68, H)], fill=(240, 120, 40, 220))
    cs = _tre('ca_sa', 300); bg.alpha_composite(cs, (int(W * 0.44), int(H * 0.26)))
    _pop(bg, 'KHOE ÁO LÀ CHÁY CẢ CHÙA', 54)
    return bg.convert('RGB')


def demo_trac():
    bg = bg_hang((40, 46, 58)); d = ImageDraw.Draw(bg, 'RGBA'); gy = int(H * 0.96)
    nk = S.sprite('ngo-khong', 'ngac', 'o', h=520); soft_shadow(bg, int(W * 0.24), gy); paste_mid(bg, nk, int(W * 0.24), gy)
    tr = _tre('kim_cang_trac', 400); cx, cy = int(W * 0.68), int(H * 0.45); bg.alpha_composite(tr, (int(cx - tr.width / 2), int(cy - tr.height / 2)))
    for sx, sy in ((-270, -120), (250, -160), (-210, 160), (270, 120)):
        d.line([(cx + sx, cy + sy), (cx + sx * 0.4, cy + sy * 0.4)], fill=(210, 210, 215, 200), width=8)
    _pop(bg, 'HÚT SẠCH MỌI BINH KHÍ', 54)
    return bg.convert('RGB')


# main_sid → (hàm vẽ demo, lời minh họa)
DEMOS = {
    's03': (demo_gay, 'Gậy biến dài chọc thủng trời, thu nhỏ giấu trong tai; đập xuống — Định Hải Thần Châm trấn đáy Đông Hải.'),
    's04': (demo_vong, 'Đường Tăng niệm chú — vòng kim cô siết đầu, Ngộ Không ôm đầu quỳ sụp, khuất phục.'),
    's05': (demo_tinhbinh, 'Nghiêng tịnh bình — đổ ra cả một biển nước (lúc thu Hồng Hài Nhi).'),
    's06': (demo_kimnhieu, 'Chũm choẹ úp kín thành cầu — biến hoá gì cũng không thoát, gậy chọc không thủng.'),
    's07': (demo_guong, 'Gương chiếu một luồng sáng — yêu quái đẹp hiện nguyên hình bộ xương.'),
    's09': (demo_thang, 'Dây vàng tự quấn trói cả thần tiên — càng giãy càng siết chặt.'),
    's10': (demo_holo, 'Gọi đúng tên, Ngộ Không dạ một tiếng là bị hút xoáy tọt vào hồ lô.'),
    's11': (demo_quat, 'Quạt phẩy một cái — luồng gió khổng lồ thổi Ngộ Không bay tám vạn tư dặm.'),
    's12': (demo_tammuoi, 'Tam Muội Chân Hoả phun biển lửa — nước dội càng cháy, Ngộ Không ho khói.'),
    's13': (demo_nhansam, 'Bát Giới nuốt chửng một quả nhân sâm — cộng bốn vạn bảy nghìn năm tuổi thọ.'),
    's14': (demo_casa, 'Khoe cà sa gấm — ông sư tham đốt cả thiền viện để cướp, suýt toi cả đoàn.'),
    's15': (demo_trac, 'Kim Cang Trác bay ra hút sạch binh khí — gậy Như Ý cũng bị hút, Ngộ Không trơ tay.'),
}


def main():
    argparse.ArgumentParser().parse_args()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(WEB, exist_ok=True)
    for act, tc, sid, scn, loi in T:
        build(scn).resize((880, int(880 * H / W)), Image.LANCZOS).save(os.path.join(WEB, '%s.jpg' % sid), quality=84)
        if sid in DEMOS:
            DEMOS[sid][0]().resize((880, int(880 * H / W)), Image.LANCZOS).save(os.path.join(WEB, '%sd.jpg' % sid), quality=84)
        print('  ✓ %s  %s' % (sid, act), flush=True)
    print('XONG %d khung + %d demo → %s' % (len(T), len(DEMOS), WEB))


if __name__ == '__main__':
    main()
