"""Bạch Long Mã (ngựa trắng của Đường Tăng) – chibi, bám ẢNH MẪU Gemini
(assets/nhan-vat/gemini/bach-long-ma/mau.png).

KHÁC bộ người (Ngộ Không/Bát Giới/Đường Tăng): đây là CON VẬT 4 CHÂN NẰM NGANG,
nên KHÔNG kế thừa goc.py (khung "bia mộ" đứng). Dựng KHUNG THÚ NGANG riêng ở đây
(sau này tái dùng cho chó Gâu Nghệ, các linh vật khác). Vẫn mượn bộ bút ve.py +
màu mực/nền + kiểu mắt–mày cong hiền để ĐỒNG BỘ phong cách bộ.

Hướng: ĐẦU bên PHẢI, MÔNG bên TRÁI (đồng bộ mặt 3/4 phải của bộ nhân vật).

Đặc điểm bám mẫu:
- Thân trắng khối ngang mập; đầu to, mõm dài bo tròn, 2 lỗ mũi; mắt nhắm cười; tai lá.
- Bờm trắng: lọn trước trán + bờm gáy lượn sóng.
- Yên cương: KHĂN/YẾM ĐEN ở ngực (họa tiết MÂY vàng đồng) + YÊN ĐEN trên lưng
  + DÂY ĐAI vàng đồng vòng bụng.
- 4 chân trụ ngắn, cổ chân có "tất" (vạch ngang) + móng.

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
    tai_in='#DFC4BD', hoof='#EDEAE1', shadow='#E6E0D4',
)

# ── KHUNG THÚ NGANG (px trên canvas 1000×1000) – ĐẦU PHẢI, MÔNG TRÁI ───────────
P = dict(
    canvas=(1000, 1000), line=10, ld=6,
    # ĐẦU: sọ tròn + mõm nhô phải–xuống
    skull=(662, 376, 132),
    muzzle=(772, 440, 104, 86),
    # MẶT (nhìn NGHIÊNG profile phải): 1 mắt nhắm cười + 1 lỗ mũi
    eye=(708, 396), eye_w=30, eye_h=9,
    brow_dy=-48, brow_w=19,
    nostril=((844, 456),),
    mouth=(808, 504, 26),
    # TAI: (gốc_trái, gốc_phải, chóp) – 2 tai dựng gần nhau, nghiêng phải
    earN=((640, 270), (698, 258), (654, 152)),
    earF=((706, 262), (754, 276), (776, 178)),
    # BỜM
    forelock=[(682, 250), (714, 230), (744, 256), (736, 322), (714, 352), (690, 320)],
    mane=[(596, 312), (628, 300), (566, 540), (520, 566), (548, 440), (556, 338)],
    # CỔ (polygon trắng nối đầu→vai)
    neck=[(600, 352), (654, 376), (636, 474), (598, 528), (520, 548), (544, 426)],
    # THÂN
    body=(420, 606, 214, 152),
    # CHÂN: (x, y_trên, y_dưới, nửa_rộng) – 2 xa vẽ trước
    legs_far=[(300, 652, 806, 23), (548, 648, 806, 23)],
    legs_near=[(330, 668, 822, 27), (576, 664, 822, 27)],
    hoof_h=30,
    # YÊN LƯNG (đen) trên sống lưng
    saddle=(356, 452, 510, 544),
    # KHĂN/YẾM NGỰC (đen)
    scarf=[(556, 452), (648, 462), (666, 522), (622, 584), (556, 582), (536, 500)],
    cloud=(600, 520),
    # DÂY ĐAI vàng (girth quanh bụng) + dây nối vai
    girth=[(486, 512), (512, 570), (520, 628), (512, 668)], girth_w=13,
    strap=[(508, 500), (542, 512), (574, 516)], strap_w=12,
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
    cv.part([ellipse(430, 862, 300, 42)], C['shadow'], line=0)
    # 2) CHÂN XA
    for x, yt, yb, hw in P['legs_far']:
        leg(x, yt, yb, hw, far=True)
    # 3) THÂN
    bx, by, brx, bry = P['body']
    cv.part([ellipse(bx, by, brx, bry)], C['white'], line=vn)
    # 4) CHÂN GẦN
    for x, yt, yb, hw in P['legs_near']:
        leg(x, yt, yb, hw)
    # 5) CỔ
    cv.part([catmull(P['neck'] + P['neck'][:1], 10)], C['white'], line=vn)
    # 6) BỜM GÁY
    cv.part([catmull(P['mane'] + P['mane'][:1], 10)], C['white'], line=vn)
    cv.stroke([(592, 338), (560, 470), (556, 546)], ld * 0.8)
    cv.stroke([(610, 320), (580, 450), (574, 520)], ld * 0.7)
    # 7) YÊN LƯNG (đen)
    sx0, sy0, sx1, sy1 = P['saddle']
    cv.part([round_poly([(sx0 - 6, sy0 + 8), (sx1, sy0 - 6), (sx1 + 6, sy1), (sx0 - 6, sy1 + 6)], 26, 10)],
            C['black'], line=vn)
    cv.stroke([(sx0, sy0 + 26), (sx1, sy0 + 10)], ld * 0.8, color=C['black_dk'])
    # 8) ĐẦU + MÕM
    sk, mz = P['skull'], P['muzzle']
    cv.part([circle(sk[0], sk[1], sk[2]), ellipse(mz[0], mz[1], mz[2], mz[3])], C['white'], line=vn)
    # 9) TAI
    def ear(g0, g1, tip, far=False):
        col = C['white_dk'] if far else C['white']
        cv.part([round_poly([g0, g1, tip], 16, 8)], col, line=vn)
        ix, iy = (g0[0] + g1[0] + 2 * tip[0]) / 4, (g0[1] + g1[1] + 2 * tip[1]) / 4
        cv.part([round_poly([lerp(g0, (ix, iy), 0.3), lerp(g1, (ix, iy), 0.3), lerp(tip, (ix, iy), 0.22)], 10, 6)],
                C['tai_in'], line=0)
    ear(*P['earF'], far=True)
    ear(*P['earN'])
    # 10) BỜM TRƯỚC TRÁN
    cv.part([catmull(P['forelock'] + P['forelock'][:1], 10)], C['white'], line=vn)
    cv.stroke([(714, 256), (720, 316)], ld * 0.7)
    # 11) KHĂN NGỰC (đen) + MÂY vàng
    cv.part([catmull(P['scarf'] + P['scarf'][:1], 10)], C['black'], line=vn)
    cxx, cyy = P['cloud']                                  # vân mây RUYI = 2 xoắn ốc nhỏ
    for ox in (-22, 22):
        sp = []
        for i in range(26):
            a = math.radians(i * 20)
            r = 5 + i * 1.1
            sp.append((cxx + ox + r * math.cos(a), cyy + r * math.sin(a) * 0.9))
        cv.stroke(catmull(sp, 6), ld * 0.95, color=C['gold'])
    # 12) DÂY ĐAI vàng
    def band(pts, hw, col):
        q = catmull(pts, 12)
        cv.part([bar(q[i], q[i + 1], hw) for i in range(len(q) - 1)], col, line=vn * 0.7)
    band(P['girth'], P['girth_w'], C['gold'])
    band(P['strap'], P['strap_w'], C['gold'])
    # 13) MẶT
    def smile_eye(cx, cy, w, h):   # cong CƯỜI (võng giữa, hai đuôi hất lên) → hiền
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
