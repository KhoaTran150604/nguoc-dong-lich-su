"""Bạch Long Mã (ngựa trắng của Đường Tăng) – chibi, bám ẢNH MẪU 2 (người dùng gửi
20/11, rõ & đúng hướng ĐẦU PHẢI – MÔNG TRÁI) + feedback Gemini (50→ sửa).

KHÁC bộ người: CON VẬT 4 CHÂN NGANG → KHUNG THÚ NGANG riêng (không kế thừa goc.py).
Mượn bộ bút ve.py + màu mực/nền để đồng bộ phong cách.

Sửa theo feedback Gemini:
- CỔ NGẮN & MẬP (stubby), đầu liền thân (bỏ cổ dài mỏng gãy góc).
- Tai + bờm trán TÁCH RÕ (bỏ cụm chồng lớp "bánh kẹp"); bờm trán răng cưa.
- MẶT 3/4: 2 mắt cười đúng vị trí (không tụt xuống má); 2 lỗ mũi + miệng gọn.
- THÂN hộp bo góc vững (bớt phệ bóng dẹt).
- Yên + yếm ôm sát thân; chân/đuôi bo mềm.

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

C = dict(
    bg='#F1EDE2', ink='#15120F',
    white='#FDFDFB', white_dk='#ECEAE3',
    navy='#272A3A', navy_dk='#1B1D2A',     # yên + yếm (navy đậm như mẫu)
    gold='#C9A24A', gold_dk='#9C7C30',
    tai_in='#E7CBC4', hoof='#EDEAE1', shadow='#E6E0D4',
)

P = dict(
    canvas=(1000, 1000), line=10, ld=6,
    # ĐẦU – NHỎ lại (bớt trống mặt) + mõm bo tròn mềm
    skull=(684, 356, 112),
    muzzle=(768, 398, 86, 81),
    # MẶT 3/4: 2 mắt cười gần mõm (xa=trái, gần=phải)
    eyeF=(656, 356), eyeN=(726, 364), eye_w=24, eye_h=8,
    brow_dy=-38, brow_w=16,
    nostril=((820, 388), (816, 412)),           # lùi vào trong + nhích lên (mõm tròn đầy)
    mouth=(802, 430, 21),
    # TAI tách RÕ 2 bên đỉnh đầu (không chụm như nơ) + trong tai hồng
    earN=((618, 260), (660, 254), (626, 194)),
    earF=((708, 254), (750, 262), (748, 198)),
    # CỔ ngắn-mập, ĐẦY ĐẶN (base rộng liền thân – tránh "thắt cổ chai")
    neck=[(580, 430), (662, 456), (648, 526), (540, 544), (514, 498), (552, 446)],
    # THÂN hộp bo góc (vững, bớt phệ)
    body_poly=[(262, 506), (560, 492), (570, 712), (252, 726)], body_r=74,
    # ĐUÔI cong thuôn – vươn ra TRÁI, tách rõ khỏi mông (centerline + bề rộng)
    tail=[(258, 516), (224, 552), (200, 606), (192, 664), (204, 712), (228, 734)],
    tail_w=(30, 13),
    # CHÂN 4 trụ bo (x, y_trên, y_dưới, nửa_rộng)
    legs_far=[(306, 688, 814, 25), (476, 688, 814, 25)],
    legs_near=[(350, 698, 826, 29), (520, 698, 826, 29)],
    hoof_h=30,
    # YÊN LƯNG (navy) ôm lưng
    saddle=[(330, 474), (476, 462), (488, 534), (326, 548)], saddle_r=34,
    # YẾM NGỰC (navy) ôm cổ/ngực + MÂY vàng
    scarf=[(560, 476), (650, 472), (666, 538), (616, 588), (556, 580), (532, 516)],
    cloud=(602, 540),
    # DÂY ĐAI vàng ôm bụng
    girth=[(452, 520), (466, 578), (462, 640), (452, 676)], girth_w=13,
    strap=[(470, 490), (506, 498), (540, 504)], strap_w=12,
)


def draw(P):
    W, H = P['canvas']
    cv = Canvas(W, H, bg=C['bg'], ink=C['ink'], line=P['line'])
    vn, ld = P['line'], P['ld']

    def leg(x, yt, yb, hw, far=False):
        col = C['white_dk'] if far else C['white']
        cv.part([rrect(x - hw, yt, x + hw, yb, 20)], col, line=vn)
        hh = P['hoof_h']
        cv.stroke([(x - hw, yb - hh), (x + hw, yb - hh)], ld * 0.9)           # vạch cổ chân
        cv.stroke([(x - hw, yb - hh * 1.9), (x + hw, yb - hh * 1.9)], ld * 0.7)
        cv.part([rrect(x - hw - 1, yb - hh + 2, x + hw + 1, yb, 10)], C['hoof'], line=vn)

    # 1) BÓNG
    cv.part([ellipse(430, 858, 300, 40)], C['shadow'], line=0)
    # 2) ĐUÔI cong thuôn mềm (gốc to → đuôi nhỏ)
    def tail_shape(pts, hw0, hw1):
        q = catmull(pts, 16)
        n = len(q)
        left, right = [], []
        for i in range(n):
            hw = hw0 + (hw1 - hw0) * (i / (n - 1))
            if i == 0:
                dx, dy = q[1][0] - q[0][0], q[1][1] - q[0][1]
            elif i == n - 1:
                dx, dy = q[-1][0] - q[-2][0], q[-1][1] - q[-2][1]
            else:
                dx, dy = q[i + 1][0] - q[i - 1][0], q[i + 1][1] - q[i - 1][1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L * hw, dx / L * hw
            left.append((q[i][0] + nx, q[i][1] + ny))
            right.append((q[i][0] - nx, q[i][1] - ny))
        return left + right[::-1]
    cv.part([tail_shape(P['tail'], *P['tail_w'])], C['white'], line=vn)
    # 1–2 nét cong bên trong tạo độ phồng / lọn đuôi
    cv.stroke(catmull([(238, 550), (210, 606), (202, 664), (214, 712)], 12), ld * 0.65)
    cv.stroke(catmull([(256, 560), (230, 610), (224, 662), (236, 706)], 12), ld * 0.55)
    # 3) CHÂN XA
    for x, yt, yb, hw in P['legs_far']:
        leg(x, yt, yb, hw, far=True)
    # 4) THÂN hộp bo góc
    body = round_poly(P['body_poly'], P['body_r'], 14)
    cv.part([body], C['white'], line=vn)
    # 5) CHÂN GẦN
    for x, yt, yb, hw in P['legs_near']:
        leg(x, yt, yb, hw)
    # 6) CỔ ngắn-mập (liền đầu–thân)
    cv.part([catmull(P['neck'] + P['neck'][:1], 10)], C['white'], line=vn)
    # 7) (bỏ mảng bờm gáy trắng lồi) – chỉ 1 nét gợi bờm trên gáy
    cv.stroke(catmull([(600, 452), (578, 496), (560, 524)], 10), ld * 0.6)
    # 8) YÊN LƯNG (navy)
    cv.part([round_poly(P['saddle'], P['saddle_r'], 12)], C['navy'], line=vn)
    cv.stroke([(338, 486), (470, 476)], ld * 0.8, color=C['navy_dk'])
    # 9) ĐẦU + MÕM
    sk, mz = P['skull'], P['muzzle']
    cv.part([circle(sk[0], sk[1], sk[2]), ellipse(mz[0], mz[1], mz[2], mz[3])], C['white'], line=vn)
    # 10) TAI
    def ear(g0, g1, tip, far=False):
        col = C['white_dk'] if far else C['white']
        cv.part([round_poly([g0, g1, tip], 18, 8)], col, line=vn)
        ix, iy = (g0[0] + g1[0] + 2 * tip[0]) / 4, (g0[1] + g1[1] + 2 * tip[1]) / 4
        cv.part([round_poly([lerp(g0, (ix, iy), 0.32), lerp(g1, (ix, iy), 0.32), lerp(tip, (ix, iy), 0.26)], 10, 6)],
                C['tai_in'], line=0)
    ear(*P['earF'], far=True)
    ear(*P['earN'])
    # 11) BỜM TRƯỚC TRÁN – lọn mềm rủ nhẹ xuống trán (giữa 2 tai đã tách)
    fl = [(660, 264), (678, 252), (698, 252), (712, 266), (706, 300), (692, 324),
          (676, 324), (662, 300)]
    cv.part([catmull(fl + fl[:1], 14)], C['white'], line=vn)
    # 12) YẾM NGỰC (navy) + MÂY vàng
    cv.part([catmull(P['scarf'] + P['scarf'][:1], 10)], C['navy'], line=vn)
    cxx, cyy = P['cloud']
    for ox in (-20, 20):
        sp = []
        for i in range(24):
            a = math.radians(i * 21)
            r = 5 + i * 1.05
            sp.append((cxx + ox + r * math.cos(a), cyy + r * math.sin(a) * 0.9))
        cv.stroke(catmull(sp, 6), ld * 0.9, color=C['gold'])
    # 13) DÂY ĐAI vàng – dải LIỀN MẠCH (1 viền, không vạch nối "thước kẻ")
    def band(pts, hw, col):
        q = catmull(pts, 16)
        left, right = [], []
        for i in range(len(q)):
            if i == 0:
                dx, dy = q[1][0] - q[0][0], q[1][1] - q[0][1]
            elif i == len(q) - 1:
                dx, dy = q[-1][0] - q[-2][0], q[-1][1] - q[-2][1]
            else:
                dx, dy = q[i + 1][0] - q[i - 1][0], q[i + 1][1] - q[i - 1][1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L * hw, dx / L * hw
            left.append((q[i][0] + nx, q[i][1] + ny))
            right.append((q[i][0] - nx, q[i][1] - ny))
        cv.part([left + right[::-1]], col, line=vn * 0.7)
    band(P['girth'], P['girth_w'], C['gold'])
    band(P['strap'], P['strap_w'], C['gold'])
    # 14) MẶT: 2 mắt cười + mày + 2 lỗ mũi + miệng
    def smile_eye(cx, cy, w, h):
        cv.stroke(catmull([(cx - w, cy - h * 0.4), (cx, cy + h), (cx + w, cy - h * 0.4)], 10), ld * 1.1)

    def brow(cx, cy, w):
        cv.stroke(catmull([(cx - w, cy + 1), (cx, cy - 2), (cx + w, cy + 1)], 10), ld * 0.75)

    for ex, ey, scale in ((P['eyeF'][0], P['eyeF'][1], 0.92), (P['eyeN'][0], P['eyeN'][1], 1.0)):
        smile_eye(ex, ey, P['eye_w'] * scale, P['eye_h'])
        brow(ex, ey + P['brow_dy'], P['brow_w'] * scale)
    for nx, ny in P['nostril']:
        cv.stroke([(nx - 4, ny - 7), (nx - 8, ny + 2), (nx, ny + 8)], ld * 0.9)
    mx, my, mw = P['mouth']
    cv.stroke(catmull([(mx - mw, my - 3), (mx, my + 7), (mx + mw, my - 4)], 10), ld * 0.9)
    return cv


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cv = draw(P)
    cv.save(os.path.join(OUT, 'bach-long-ma.png'))
    print('xong:', os.path.join(OUT, 'bach-long-ma.png'))
