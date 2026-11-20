"""Bạch Long Mã (ngựa trắng của Đường Tăng) – chibi, bám ẢNH MẪU Gemini
(assets/nhan-vat/gemini/bach-long-ma/mau.png).

KHÁC bộ người (Ngộ Không/Bát Giới/Đường Tăng): đây là CON VẬT 4 CHÂN NẰM NGANG,
nên KHÔNG kế thừa goc.py (khung "bia mộ" đứng). Dựng KHUNG THÚ NGANG riêng ở đây
(sau này tái dùng cho chó Gâu Nghệ, linh vật khác). Mượn bộ bút ve.py + màu mực/nền
+ kiểu mắt cong hiền để ĐỒNG BỘ phong cách bộ.

Hướng: ĐẦU bên PHẢI nhìn NGHIÊNG (profile), MÔNG bên TRÁI (đồng bộ bộ nhân vật).

Vòng sửa (chấm agent 70→ ...): lộ CỔ trắng rõ, thân THON lại, tách khăn/yên,
tai nhỏ bớt nhọn, thêm lọn bờm trán xõa, mõm bo, thêm đuôi xù.

Chạy:  python scripts/hoathinh/chibi/bach_long_ma.py
Ra:    build/thu-hoathinh/nhan-vat/bach-long-ma.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ve import Canvas, circle, ellipse, rrect, round_poly, bar, catmull, lerp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'nhan-vat')

# ── BẢNG MÀU (lấy từ ảnh mẫu) ─────────────────────────────────────────────────
C = dict(
    bg='#F1EDE2', ink='#15120F',
    white='#FDFDFB', white_dk='#ECEAE3',
    black='#28252C', black_dk='#1A181E',
    gold='#C3A763', gold_dk='#9C8446',
    tai_in='#E7D2CC', hoof='#EDEAE1', shadow='#E6E0D4',
)

# ── KHUNG THÚ NGANG (px / canvas 1000×1000) – ĐẦU PHẢI, MÔNG TRÁI ──────────────
P = dict(
    canvas=(1000, 1000), line=10, ld=6,
    # ĐẦU: sọ + mõm (bo tròn hơn)
    skull=(672, 366, 126),
    muzzle=(778, 436, 98, 90),
    # MẶT (profile phải): 1 mắt cười + 1 lỗ mũi
    eye=(714, 392), eye_w=29, eye_h=9,
    brow_dy=-46, brow_w=18,
    nostril=((846, 452),),
    mouth=(812, 500, 25),
    # TAI: nhỏ hơn, thấp hơn, bớt nhọn (gốc_trái, gốc_phải, chóp)
    earN=((636, 288), (688, 278), (652, 198)),
    earF=((696, 282), (742, 294), (758, 210)),
    # BỜM trán (lọn chính) + CỔ + bờm gáy
    forelock=[(688, 270), (718, 252), (746, 276), (738, 334), (716, 360), (692, 332)],
    neck=[(582, 402), (650, 446), (632, 552), (556, 570), (506, 520), (542, 440)],
    mane=[(578, 398), (610, 392), (556, 552), (518, 568), (538, 452), (552, 416)],
    # THÂN – THON & dài hơn (bớt mập)
    body=(414, 616, 182, 140),
    # ĐUÔI xù (mông trái, ló ra ngoài thân) – khối liền
    tail=[(236, 542), (204, 586), (190, 650), (200, 708), (226, 726), (246, 706),
          (238, 648), (260, 588), (270, 546)],
    # CHÂN: (x, y_trên, y_dưới, nửa_rộng)
    legs_far=[(300, 660, 808, 22), (548, 654, 808, 22)],
    legs_near=[(332, 672, 824, 26), (574, 668, 824, 26)],
    hoof_h=28,
    # YÊN LƯNG (đen) – miếng NHỎ trên sống lưng
    saddle=(372, 456, 478, 528),
    # KHĂN/YẾM NGỰC (đen) – quấn phần DƯỚI cổ, chừa cổ trắng phía trên
    scarf=[(548, 502), (636, 504), (650, 560), (602, 592), (544, 582), (528, 530)],
    cloud=(594, 548),
    # DÂY ĐAI vàng
    girth=[(452, 524), (470, 568), (470, 612)], girth_w=12,
    strap=[(490, 514), (524, 522), (556, 526)], strap_w=11,
)


def draw(P):
    W, H = P['canvas']
    cv = Canvas(W, H, bg=C['bg'], ink=C['ink'], line=P['line'])
    vn, ld = P['line'], P['ld']

    def leg(x, yt, yb, hw, far=False):
        col = C['white_dk'] if far else C['white']
        cv.part([rrect(x - hw, yt, x + hw, yb, 18)], col, line=vn)
        hh = P['hoof_h']
        cv.stroke([(x - hw, yb - hh), (x + hw, yb - hh)], ld)
        cv.part([rrect(x - hw - 1, yb - hh + 2, x + hw + 1, yb, 9)], C['hoof'], line=vn)

    # 1) BÓNG
    cv.part([ellipse(430, 862, 290, 40)], C['shadow'], line=0)
    # 2) ĐUÔI xù (sau thân) – khối trắng liền + 1 nếp mềm
    cv.part([catmull(P['tail'], 10)], C['white'], line=vn)
    cv.stroke([(224, 578), (214, 648), (222, 706)], ld * 0.6)
    # 3) CHÂN XA
    for x, yt, yb, hw in P['legs_far']:
        leg(x, yt, yb, hw, far=True)
    # 4) THÂN (thon)
    bx, by, brx, bry = P['body']
    cv.part([ellipse(bx, by, brx, bry)], C['white'], line=vn)
    # 5) CHÂN GẦN
    for x, yt, yb, hw in P['legs_near']:
        leg(x, yt, yb, hw)
    # 6) CỔ trắng (nổi rõ, nối đầu→vai)
    cv.part([catmull(P['neck'] + P['neck'][:1], 10)], C['white'], line=vn)
    # 7) BỜM GÁY (trắng lượn sóng, sau cổ)
    cv.part([catmull(P['mane'] + P['mane'][:1], 10)], C['white'], line=vn)
    # 8) YÊN LƯNG (đen) – miếng nhỏ
    sx0, sy0, sx1, sy1 = P['saddle']
    cv.part([round_poly([(sx0 - 4, sy0 + 6), (sx1, sy0 - 4), (sx1 + 4, sy1), (sx0 - 4, sy1 + 4)], 22, 10)],
            C['black'], line=vn)
    cv.stroke([(sx0, sy0 + 22), (sx1, sy0 + 8)], ld * 0.8, color=C['black_dk'])
    # 9) ĐẦU + MÕM
    sk, mz = P['skull'], P['muzzle']
    cv.part([circle(sk[0], sk[1], sk[2]), ellipse(mz[0], mz[1], mz[2], mz[3])], C['white'], line=vn)
    # 10) TAI
    def ear(g0, g1, tip, far=False):
        col = C['white_dk'] if far else C['white']
        cv.part([round_poly([g0, g1, tip], 20, 8)], col, line=vn)
        ix, iy = (g0[0] + g1[0] + 2 * tip[0]) / 4, (g0[1] + g1[1] + 2 * tip[1]) / 4
        cv.part([round_poly([lerp(g0, (ix, iy), 0.34), lerp(g1, (ix, iy), 0.34), lerp(tip, (ix, iy), 0.3)], 10, 6)],
                C['tai_in'], line=0)
    ear(*P['earF'], far=True)
    ear(*P['earN'])
    # 11) BỜM TRƯỚC TRÁN – cụm 3 lọn khối trắng (không kẻ sọc)
    for cx0, cy0, w0, h0 in [(706, 300, 22, 58), (724, 292, 24, 64), (742, 300, 20, 54)]:
        lock = [(cx0 - w0, cy0 - h0 * 0.5), (cx0 - w0 * 0.3, cy0 - h0), (cx0 + w0 * 0.3, cy0 - h0),
                (cx0 + w0, cy0 - h0 * 0.4), (cx0 + w0 * 0.2, cy0 + h0), (cx0 - w0 * 0.5, cy0 + h0 * 0.8)]
        cv.part([catmull(lock + lock[:1], 8)], C['white'], line=vn)
    # 12) KHĂN NGỰC (đen) + MÂY vàng
    cv.part([catmull(P['scarf'] + P['scarf'][:1], 10)], C['black'], line=vn)
    cxx, cyy = P['cloud']
    for ox in (-20, 20):
        sp = []
        for i in range(24):
            a = math.radians(i * 21)
            r = 5 + i * 1.05
            sp.append((cxx + ox + r * math.cos(a), cyy + r * math.sin(a) * 0.9))
        cv.stroke(catmull(sp, 6), ld * 0.9, color=C['gold'])
    # 13) DÂY ĐAI vàng
    def band(pts, hw, col):
        q = catmull(pts, 12)
        cv.part([bar(q[i], q[i + 1], hw) for i in range(len(q) - 1)], col, line=vn * 0.7)
    band(P['girth'], P['girth_w'], C['gold'])
    band(P['strap'], P['strap_w'], C['gold'])
    # 14) MẶT
    def smile_eye(cx, cy, w, h):
        cv.stroke(catmull([(cx - w, cy - h * 0.45), (cx, cy + h), (cx + w, cy - h * 0.45)], 10), ld * 1.15)

    def brow(cx, cy, w):
        cv.stroke(catmull([(cx - w, cy + 1), (cx, cy - 2), (cx + w, cy + 1)], 10), ld * 0.8)

    smile_eye(*P['eye'], P['eye_w'], P['eye_h'])
    brow(P['eye'][0], P['eye'][1] + P['brow_dy'], P['brow_w'])
    for nx, ny in P['nostril']:
        cv.stroke([(nx - 5, ny - 8), (nx - 9, ny + 2), (nx + 1, ny + 9)], ld * 0.95)
    mx, my, mw = P['mouth']
    cv.stroke(catmull([(mx - mw, my - 3), (mx, my + 7), (mx + mw, my - 4)], 10), ld * 0.9)
    return cv


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cv = draw(P)
    cv.save(os.path.join(OUT, 'bach-long-ma.png'))
    print('xong:', os.path.join(OUT, 'bach-long-ma.png'))
