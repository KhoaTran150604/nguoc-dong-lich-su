"""Sa Tăng (Sa Ngộ Tịnh) – vẽ bám ẢNH MẪU Gemini (assets/nhan-vat/gemini/sa-tang/).
Dựng trên THÔNG SỐ GỐC (goc.py) + KHUNG CHUNG (khung.py), cùng khung Ngộ Không/
Đường Tăng/Bát Giới (dáng 'chuan') để ĐỒNG TÔNG. KHÔNG trace – code tự vẽ.

Riêng:
- TÓC nâu đỏ phủ đỉnh + VÒNG TRÁN vàng (hoạ tiết xoắn mây).
- RÂU QUAI NÓN nâu đỏ ôm hàm + ria mép.
- CHUỖI SỌ "cute" quanh cổ/ngực (ngà, mắt chấm).
- ÁO xanh rêu + cổ V kem + đai nút.
- HÀNG YÊU BẢO TRƯỢNG: gậy vàng + LƯỠI LIỀM TRĂNG bạc trên đỉnh + quả cầu giữa.

Chạy:  python scripts/hoathinh/chibi/sa_tang.py
Ra:    build/thu-hoathinh/nhan-vat/sa-tang.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goc import tao_P  # noqa: E402
from khung import Khung, dau, than, ban_tay, khuon_mat  # noqa: E402
from ve import Canvas, circle, ellipse, bar, lerp, catmull  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'nhan-vat')


def crescent_poly(cx, cy, r1, r2, ox, oy, n=44):
    """Lưỡi liềm ĐẶC = đĩa O1(r1) trừ đĩa O2(r2) lệch (ox,oy). Trả polygon liền (outer arc O1
    phía xa O2 + inner arc O2 phía trong O1) → part() tô đặc + viền chỉ quanh liềm."""
    d = math.hypot(ox, oy) or 1e-6
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    ux, uy = ox / d, oy / d
    px, py = -uy, ux
    mx, my = cx + a * ux, cy + a * uy
    A = (mx + h * px, my + h * py)
    Bp = (mx - h * px, my - h * py)

    def arc(ccx, ccy, r, p0, p1, ref, far):
        a0 = math.atan2(p0[1] - ccy, p0[0] - ccx)
        a1 = math.atan2(p1[1] - ccy, p1[0] - ccx)
        da = (a1 - a0) % (2 * math.pi)
        s1 = [(ccx + r * math.cos(a0 + da * i / n), ccy + r * math.sin(a0 + da * i / n)) for i in range(n + 1)]
        s2 = [(ccx + r * math.cos(a0 + (da - 2 * math.pi) * i / n), ccy + r * math.sin(a0 + (da - 2 * math.pi) * i / n)) for i in range(n + 1)]
        def dref(s):
            m = s[len(s) // 2]
            return (m[0] - ref[0]) ** 2 + (m[1] - ref[1]) ** 2
        pick = (s1 if dref(s1) > dref(s2) else s2) if far else (s1 if dref(s1) < dref(s2) else s2)
        return pick
    O2 = (cx + ox, cy + oy)
    outer = arc(cx, cy, r1, A, Bp, O2, far=True)      # cung O1 xa O2
    inner = arc(cx + ox, cy + oy, r2, Bp, A, (cx, cy), far=False)  # cung O2 trong O1
    return outer + inner

P = tao_P(
    dang='chuan',
    head_c=(413, 399),
    K=dict(tay_x=1.45, tay_y=0.90, tay_r=0.20),    # bàn tay nắm gọn vào gậy
    c_bg='#F6F3EC',
    c_da='#BE9268', c_da_in='#9C7348',             # da ngăm nâu
    c_toc='#6E3B2E', c_toc_dk='#552C22',           # tóc + râu nâu đỏ
    c_band='#CFA64E', c_band_dk='#A8863A',         # vòng trán vàng
    c_robe='#49563C', c_robe2='#3A4531',           # áo xanh rêu + mảng tối
    c_collar='#EFE4CC', c_belt='#EFE4CC', c_belt2='#D4C08A',   # cổ/đai kem
    c_sku='#ECE3D0',                               # sọ ngà
    c_staff='#C9A24A', c_staff_dk='#A8863A', c_staff_pole='#B8923F',
    c_blade='#CFD4DA', c_blade_dk='#A9B0B8',       # lưỡi liềm bạc
    # mặt: mắt oval đen + đốm sáng; mày dày; cười nhỏ (đồng bộ bộ)
    M=dict(mat=[(-0.05, -0.03), (0.59, -0.03)], ma_hong_vt=[(-0.10, 0.07), (0.60, 0.07)],
           kieu_mat='oval', mat_rx=0.145, mat_ry=0.165, glint=(0.055, 0.095),
           may_y=-0.13, may_cong=0.045, may_nghieng=0.0, may_day=0.08, mau_ma='#C98A6A',   # mày gần PHẲNG → hiền
           ma_hong=(0.11, 0.085),
           mieng=(0.22, 0.41), mieng_rong=0.20, mieng_sau=0.03),   # cười mỉm nhẹ cân đối
    tai=[(-1.00, 0.14, 0.20, 0.11), (1.00, 0.12, 0.14, 0.07)],
    # TÓC: mép ngoài bám đỉnh đầu + chân tóc (chừa TRÁN lộ da)
    toc_out=[(-0.96, -0.26), (-0.72, -0.78), (-0.30, -1.00), (0.12, -1.00), (0.52, -0.90), (0.84, -0.60), (0.97, -0.16)],
    toc_in=[(0.80, -0.20), (0.46, -0.42), (0.12, -0.50), (-0.26, -0.48), (-0.56, -0.36), (-0.82, -0.16)],
    # VÒNG TRÁN vàng (cung ngang trán, dưới chân tóc) – dày + hoa văn mây
    band_y=-0.33, band_dy=0.15,
    # RÂU QUAI NÓN: CHỈ ôm cằm/hàm dưới (chừa MÁ + TRÁN lộ da rộng)
    rau_out=[(-0.86, 0.16), (-0.74, 0.48), (-0.42, 0.78), (0.02, 0.90), (0.46, 0.78), (0.76, 0.46), (0.86, 0.14)],
    rau_in=[(0.56, 0.30), (0.36, 0.56), (0.12, 0.66), (-0.16, 0.62), (-0.40, 0.54), (-0.56, 0.30)],
    ria=[(-0.16, 0.28), (0.02, 0.33), (0.28, 0.28)],
    # CHUỖI SỌ (toạ độ thân B): MỘT vòng liền ôm quanh cổ (sọ nhỏ đều sát nhau)
    sku_path=[(-0.60, 0.14), (-0.42, 0.26), (-0.22, 0.34), (0.0, 0.37), (0.22, 0.34), (0.42, 0.26), (0.60, 0.14)],
    sku_r=0.098,
    # ÁO
    ao_trong=[(-0.12, 0.0), (0.46, 0.0), (0.17, 0.44)],
    co_trai=((-0.26, 0.0), (0.42, 0.52)), co_phai=((0.52, 0.0), (0.16, 0.44)), co_day=0.12,
    belt=(1.24, 1.46),
    # BẢO TRƯỢNG (tay phải) – căn gậy qua bàn tay
    gay_tren=(1.54, -1.46), gay_duoi=(1.06, 2.56), gay_day=0.19,
    crescent=(1.58, -1.78, 0.42),     # (dx, dy, r) lưỡi liềm trăng
    ball=(1.24, 0.90, 0.19),          # (dx, dy, r) quả cầu giữa gậy
)


def draw(P):
    R = P['R']
    W, H = P['canvas']
    cv = Canvas(W, H, bg=P['c_bg'], ink=P['c_ink'], line=P['vien'] * R)
    vn = P['vien'] * R
    ld = P['vien_ct'] * R
    k = Khung(P['head_c'], R, P['K'])
    B = k.B

    # 1) THÂN áo xanh rêu + cổ V + đai nút
    body = than(cv, k, P['c_robe'])
    x0, x1 = k.bx - k.hb - 30, k.bx + k.hb + 30

    def ao(lay):
        cv.part([[(k.bx + 0.1 * R, k.top - 10), (x1, k.top - 10), (x1, k.bot + 10), (k.bx + 0.2 * R, k.bot + 10)]],
                P['c_robe2'], line=0, img=lay)                           # mảng tối phải
        cv.part([[B(*p) for p in P['ao_trong']]], P['c_collar'], line=ld * 0.6, img=lay)
        for u, v in (P['co_phai'], P['co_trai']):
            cv.part([bar(B(*u), B(*v), P['co_day'] * R / 2)], P['c_collar'], line=ld * 0.6, img=lay)
        b0, b1 = P['belt']
        cv.part([[(x0, k.top + b0 * R), (x1, k.top + b0 * R), (x1, k.top + b1 * R), (x0, k.top + b1 * R)]],
                P['c_belt'], line=ld * 0.6, img=lay)
        cy = (b0 + b1) / 2
        for s in (-1, 1):
            cv.part([[B(0.02, cy), B(0.02 + s * 0.2, cy - 0.1), B(0.02 + s * 0.2, cy + 0.12)]],
                    P['c_belt'], line=ld, img=lay)
            cv.part([[B(0.02 + s * 0.03, cy + 0.07), B(0.02 + s * 0.1, cy + 0.4), B(0.02, cy + 0.38)]],
                    P['c_belt'], line=ld, img=lay)
        cv.part([circle(*B(0.02, cy + 0.02), 0.08 * R)], P['c_belt2'], line=ld, img=lay)
    cv.clip_layer(ao, [body])
    cv.stroke(body + body[:2], vn)

    # 2) BÀN TAY (bảo trượng đè lên)
    hand = ban_tay(cv, k, P['c_da'])

    # 3) ĐẦU + tai
    head = dau(cv, k, P['c_da'], P['tai'], P['c_da_in'], ld, mau_tai=P['c_da'])
    cv.stroke(head + head[:2], vn)

    # 4) TÓC nâu đỏ + VÒNG TRÁN vàng
    toc = [k.H(*p) for p in P['toc_out']] + [k.H(*p) for p in P['toc_in']]
    cv.part([toc], P['c_toc'], line=vn)
    cv.stroke([k.H(-0.12, -0.80), k.H(-0.02, -0.60)], ld * 0.7, color=P['c_toc_dk'])   # nếp tóc (trong vùng tóc)
    cv.stroke([k.H(0.30, -0.76), k.H(0.40, -0.58)], ld * 0.6, color=P['c_toc_dk'])
    by = P['band_y']
    cxb = math.sqrt(max(0.0, 1 - by * by))
    a0, a1 = math.atan2(by, -cxb), math.atan2(by, cxb)
    bandL = [(k.hx + R * math.cos(a0 + (a1 - a0) * i / 40), k.hy + R * math.sin(a0 + (a1 - a0) * i / 40)) for i in range(41)]
    bandU = [(x, y + P['band_dy'] * R) for x, y in reversed(bandL)]
    cv.part([bandL + bandU], P['c_band'], line=vn)
    # hoạ tiết CUỘN MÂY (vân) giữa vòng trán – 2 xoắn đối, nét đậm rõ
    for ox in (-0.13, 0.13):
        sp = []
        for i in range(18):
            aa = math.radians(i * 24)
            rr = 0.016 + i * 0.0052
            sp.append(k.H(0.22 + ox + rr * math.cos(aa), by + 0.075 + rr * math.sin(aa) * 0.9))
        cv.stroke(catmull(sp, 6), ld * 1.0, color=P['c_band_dk'])

    # 5) RÂU QUAI NÓN + ria
    rau = [k.H(*p) for p in P['rau_out']] + [k.H(*p) for p in P['rau_in']]
    cv.part([rau], P['c_toc'], line=vn)
    cv.part([[k.H(*p) for p in P['ria']] + [k.H(P['ria'][1][0], P['ria'][1][1] + 0.1)]], P['c_toc'], line=ld)

    # 6) CHUỖI SỌ quanh cổ/ngực
    for dx, dy in P['sku_path']:
        x, y = B(dx, dy)
        r = P['sku_r'] * R
        cv.part([[*catmull([(x - r, y - r * 0.2), (x - r * 0.9, y - r), (x, y - r * 1.15),
                            (x + r * 0.9, y - r), (x + r, y - r * 0.2), (x + r * 0.7, y + r * 0.9),
                            (x - r * 0.7, y + r * 0.9)], 6)]], P['c_sku'], line=ld * 0.8)
        cv.dot(x - r * 0.4, y - r * 0.15, r * 0.22, P['c_ink'])       # 2 hốc mắt
        cv.dot(x + r * 0.4, y - r * 0.15, r * 0.22, P['c_ink'])
        cv.stroke([(x, y + r * 0.1), (x, y + r * 0.45)], ld * 0.5)    # mũi/răng

    # 7) KHUÔN MẶT
    khuon_mat(cv, k, P['M'], P['c_ink'])

    # 8) HÀNG YÊU BẢO TRƯỢNG
    t0, t1 = k.H(*P['gay_tren']), k.H(*P['gay_duoi'])
    h = P['gay_day'] * R / 2
    cv.part([bar(t0, t1, h)], P['c_staff_pole'])                         # cán gậy (màu phẳng, bỏ vân loang)
    # quả cầu giữa
    bx2, by2 = k.H(P['ball'][0], P['ball'][1])
    cv.part([circle(bx2, by2, P['ball'][2] * R)], P['c_staff'], line=vn * 0.7)
    # LƯỠI LIỀM TRĂNG bạc ĐẶC trên đỉnh gậy + chóp nhọn
    cxm, cym = k.H(P['crescent'][0], P['crescent'][1])
    rm = P['crescent'][2] * R
    lune = crescent_poly(cxm, cym, rm, rm * 0.84, rm * 0.60, -rm * 0.30)
    cv.part([lune], P['c_blade'], line=vn * 0.75)
    cv.stroke([lune[len(lune) // 4], lerp(lune[len(lune) // 4], (cxm, cym + rm), 0.3)], ld * 0.6, color=P['c_blade_dk'])
    tip = k.H(P['crescent'][0] - 0.02, P['crescent'][1] - P['crescent'][2] - 0.22)   # chóp nhọn mũi trên
    cv.part([[tip, (tip[0] - 0.06 * R, tip[1] + 0.22 * R), (tip[0] + 0.06 * R, tip[1] + 0.22 * R)]],
            P['c_blade'], line=vn * 0.7)
    return cv, k, hand


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cv, k, hand = draw(P)
    cv.save(os.path.join(OUT, 'sa-tang.png'))
    print('xong:', os.path.join(OUT, 'sa-tang.png'))
