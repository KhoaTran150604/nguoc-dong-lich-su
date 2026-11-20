"""Đường Tăng – vẽ bám ẢNH MẪU (người dùng gen Gemini, ảnh 8). Dựng trên THÔNG SỐ GỐC (goc.py),
cùng khung với Ngộ Không & Bát Giới, dáng 'chuan'. Riêng:
- MŨ LOTUS đỏ + viền vàng (5 cánh) + 2 DẢI BUÔNG kem hai bên mặt.
- Áo VÀNG + CÀ SA ĐỎ ô vuông vàng (patchwork) + đai thắt NƠ kem.
- TÍCH TRƯỢNG vàng (cán vàng + vòng khoen vàng).
- Mặt hiền: mắt bầu dục đen + đốm sáng, mày dày, cười nhỏ (khuon_mat – đồng bộ Ngộ Không).

Chạy:  python scripts/hoathinh/chibi/duong_tang.py
Ra:    build/thu-hoathinh/nhan-vat/duong-tang.png + duong-tang-bang.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bang import sheet  # noqa: E402
from goc import tao_P  # noqa: E402
from khung import Khung, dau, than, ban_tay, khuon_mat  # noqa: E402
from ve import Canvas, circle, bar, lerp, catmull  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'nhan-vat')

P = tao_P(
    dang='chuan',
    head_c=(413, 399),
    c_bg='#F6F3EC',
    c_da='#F3D2A6', c_da_in='#DCAE86',             # da người sáng
    c_robe='#E6A91E', c_robe2='#C98A17',           # áo VÀNG + mảng tối
    c_kasaya='#B5362A', c_grid='#E6B23C',          # cà sa ĐỎ + lưới ô vuông VÀNG
    c_collar='#F2E6CC', c_belt='#EFE2C0', c_belt2='#D4C08A',   # cổ/đai kem + nút
    c_crown='#D23B2B', c_crown_gold='#E6B23C',     # mũ lotus ĐỎ TƯƠI + viền vàng
    c_ribbon='#EAD08A',                            # dải mũ buông
    c_staff='#E6B23C', c_staff_dk='#C9972E', c_staff_pole='#9A7328',  # đầu vàng + CÁN nâu gỗ sẫm
    # mặt hiền (mắt oval đen + đốm sáng; mày dày; cười nhỏ)
    M=dict(mat=[(-0.05, -0.06), (0.59, -0.06)], ma_hong_vt=[(-0.08, 0.03), (0.60, 0.03)],
           kieu_mat='oval', mat_rx=0.145, mat_ry=0.175, glint=(0.05, 0.095),
           may_y=-0.13, may_cong=0.11, may_nghieng=0.0, may_day=0.085, mau_ma='#EFA79D',  # mày PHẲNG hiền, không xếch
           ma_hong=(0.12, 0.10),                                      # má hồng nhỏ (tách khỏi mũ)
           mieng=(0.27, 0.45), mieng_rong=0.27, mieng_sau=0.06),   # cười rộng → hiền từ
    tai=[(-1.02, 0.10, 0.22, 0.12), (1.00, 0.10, 0.15, 0.08)],   # tai to bên trái
    # MŨ LOTUS (dịch phải theo mặt 3/4): dải đỏ base + 5 cánh sen đỏ viền vàng
    crown_band=(-0.82, 1.08, -0.52, 0.22),         # dải đỏ RỘNG, NÂNG CAO chừa trán (mép dưới ~-0.30, trên chân mày)
    crown_petal=[(-0.72, 0.54), (-0.35, 0.74), (0.02, 0.86), (0.39, 0.74), (0.76, 0.54)],  # cánh sen THẤP + loe RỘNG → bầu bĩnh
    crown_petal_w=0.31, crown_petal_nhon=True,     # cánh rộng bản, đỉnh hơi nhọn (plump), chạm nhau
    # 2 DẢI BUÔNG hai bên mặt: (dx_top, dx_bot) – kéo xa mặt
    ribbon=[(-0.72, -0.80), (0.92, 1.00)], ribbon_y=(-0.30, 1.26), ribbon_w=0.065,
    # CÀ SA đỏ: đường chéo gấu (trái cao → phải thấp) + lưới ô vuông
    kasaya_y=(0.46, 0.92), kasaya_bot=1.92,                          # mép cà sa DỐC (khoác chéo) + lộ vàng đáy
    grid_h=[1.08, 1.34, 1.60, 1.86], grid_step=0.52,   # hàng ngang + bước ô → gạch SO LE (không caro đều)
    ao_trong=[(-0.12, 0.0), (0.46, 0.0), (0.17, 0.42)],
    co_trai=((-0.26, 0.0), (0.42, 0.50)), co_phai=((0.52, 0.0), (0.16, 0.42)), co_day=0.12,
    belt=(1.20, 1.40),
    # TÍCH TRƯỢNG vàng (tay phải)
    gay_tren=(1.66, -1.50), gay_duoi=(1.08, 2.60), gay_day=0.185,
)


def draw(P):
    R = P['R']
    W, H = P['canvas']
    cv = Canvas(W, H, bg=P['c_bg'], ink=P['c_ink'], line=P['vien'] * R)
    vn = P['vien'] * R
    ld = P['vien_ct'] * R
    k = Khung(P['head_c'], R, P['K'])
    B = k.B

    # 1) THÂN áo VÀNG + cà sa đỏ patchwork + cổ + đai nơ
    body = than(cv, k, P['c_robe'])
    x0, x1 = k.bx - k.hb - 30, k.bx + k.hb + 30
    yL, yR = k.top + P['kasaya_y'][0] * R, k.top + P['kasaya_y'][1] * R

    def ao(lay):
        cv.part([[(k.bx + 0.1 * R, k.top - 10), (x1, k.top - 10), (x1, k.bot + 10), (k.bx + 0.2 * R, k.bot + 10)]],
                P['c_robe2'], line=0, img=lay)                           # mảng tối phải
        # CÀ SA ĐỎ (dưới đường chéo) + lưới ô vuông vàng
        ybot = k.top + P['kasaya_bot'] * R
        cv.part([[(x0, yL), (x1, yR), (x1, ybot), (x0, ybot)]], P['c_kasaya'], line=0, img=lay)
        # ô cà sa kiểu GẠCH SO LE: hàng ngang + vạch dọc lệch nửa ô mỗi hàng (nét vàng dày hơn 1.5×)
        rows = P['grid_h']
        for gy in rows:
            yy = k.top + gy * R
            cv.stroke([(x0, yy), (x1, yy)], ld * 1.2, color=P['c_grid'], img=lay)
        step = P['grid_step'] * R
        ys = [k.top + 0.96 * R] + [k.top + g * R for g in rows] + [k.top + P['kasaya_bot'] * R]
        for ri in range(len(ys) - 1):
            off = step / 2 if ri % 2 else 0
            gx = x0 + off
            while gx < x1:
                cv.stroke([(gx, ys[ri]), (gx, ys[ri + 1])], ld * 1.2, color=P['c_grid'], img=lay)
                gx += step
        cv.stroke([(x0, yL), (x1, yR)], ld * 1.3, color=P['c_grid'], img=lay)       # viền vàng mép TRÊN cà sa
        cv.stroke([(x0, ybot), (x1, ybot)], ld * 1.1, color=P['c_grid'], img=lay)   # viền vàng gấu (lộ vàng dưới)
        # cổ áo kem (V)
        cv.part([[B(*p) for p in P['ao_trong']]], P['c_collar'], line=ld * 0.6, img=lay)
        for u, v in (P['co_phai'], P['co_trai']):
            cv.part([bar(B(*u), B(*v), P['co_day'] * R / 2)], P['c_collar'], line=ld * 0.6, img=lay)
        # đai lưng kem + NƠ thắt
        b0, b1 = P['belt']
        cv.part([[(x0, k.top + b0 * R), (x1, k.top + b0 * R), (x1, k.top + b1 * R), (x0, k.top + b1 * R)]],
                P['c_belt'], line=ld * 0.6, img=lay)
        cy = (b0 + b1) / 2
        for s in (-1, 1):
            cv.part([[B(0.02, cy), B(0.02 + s * 0.22, cy - 0.11), B(0.02 + s * 0.22, cy + 0.13)]],
                    P['c_belt'], line=ld, img=lay)                      # cánh nơ
            cv.part([[B(0.02 + s * 0.04, cy + 0.08), B(0.02 + s * 0.12, cy + 0.44), B(0.02 + s * 0.0, cy + 0.42)]],
                    P['c_belt'], line=ld, img=lay)                      # đuôi nơ
        cv.part([circle(*B(0.02, cy + 0.02), 0.08 * R)], P['c_belt2'], line=ld, img=lay)   # nút giữa
    cv.clip_layer(ao, [body])
    cv.stroke(body + body[:2], vn)

    # 2) BÀN TAY (tích trượng đè lên)
    hand = ban_tay(cv, k, P['c_da'])

    # 3) ĐẦU + tai  (viền đầu vẽ NGAY để mũ đè lên trên → chóp đầu ẩn sau mũ, không cắt ngang cánh sen)
    head = dau(cv, k, P['c_da'], P['tai'], P['c_da_in'], ld, mau_tai=P['c_da'])
    cv.stroke(head + head[:2], vn)

    # 4) MŨ LOTUS (đỏ + viền vàng) ĐÈ LÊN đỉnh đầu
    bL, bR, by, bd = P['crown_band']
    cx = math.sqrt(max(0.0, 1 - by * by))                              # nền mũ đỏ phủ đỉnh đầu (che da + viền chóp)
    a0, a1 = math.atan2(by, -cx), math.atan2(by, cx)
    cap = [(k.hx + R * math.cos(a0 + (a1 - a0) * i / 48), k.hy + R * math.sin(a0 + (a1 - a0) * i / 48)) for i in range(49)]
    cv.part([cap], P['c_crown'])
    pw = P['crown_petal_w']
    nhon = P.get('crown_petal_nhon')
    for dx, cao in P['crown_petal']:                                   # cánh sen TO
        if nhon:                                                       # đỉnh NHỌN góc cạnh (như mẫu)
            ap = k.H(dx, by - cao)
            pts = [k.H(dx - pw, by), k.H(dx - pw * 0.62, by - cao * 0.52), ap, ap,
                   k.H(dx + pw * 0.62, by - cao * 0.52), k.H(dx + pw, by)]
        else:
            pts = [k.H(dx - pw, by), k.H(dx - pw * 0.95, by - cao * 0.45), k.H(dx - pw * 0.42, by - cao * 0.86),
                   k.H(dx, by - cao), k.H(dx + pw * 0.42, by - cao * 0.86), k.H(dx + pw * 0.95, by - cao * 0.45), k.H(dx + pw, by)]
        pet = catmull(pts, 8)
        cv.part([pet], P['c_crown'], line=vn)
        cv.stroke(pet, ld * 0.9, color=P['c_crown_gold'])               # viền vàng cánh
    cv.part([[k.H(bL, by), k.H(bR, by), k.H(bR, by + bd), k.H(bL, by + bd)]], P['c_crown'], line=vn)
    cv.stroke([k.H(bL, by), k.H(bR, by)], ld * 0.9, color=P['c_crown_gold'])
    cv.stroke([k.H(bL, by + bd), k.H(bR, by + bd)], ld * 0.9, color=P['c_crown_gold'])

    # 5) 2 DẢI MŨ BUÔNG hai bên mặt (trên áo)
    ry0, ry1 = P['ribbon_y']
    for dxt, dxb in P['ribbon']:
        a, b = k.H(dxt, ry0), k.H(dxb, ry1)
        cv.part([bar(a, b, P['ribbon_w'] * R)], P['c_ribbon'], line=vn)
        cv.stroke([lerp(a, b, 0.12), lerp(a, b, 0.95)], ld * 0.5, color='#D4B86A')   # nếp dọc

    # 6) KHUÔN MẶT
    khuon_mat(cv, k, P['M'], P['c_ink'])

    # 7) TÍCH TRƯỢNG vàng (tay phải)
    t0, t1 = k.H(*P['gay_tren']), k.H(*P['gay_duoi'])
    h = P['gay_day'] * R / 2
    cv.part([bar(t0, t1, h)], P['c_staff_pole'])                        # cán NÂU GỖ
    cv.stroke([lerp(t0, t1, 0.1), t1], h * 0.4, color='#7E5C1F')        # vân tối cán gỗ
    lwf = vn * 0.65                                                     # nét cụm đầu trượng MẢNH hơn (lỗ khoen rỗng thoáng)
    top = (t0[0], t0[1] - 0.30 * R)
    cv.part([[(top[0] - 0.12 * R, top[1] - 0.05 * R), (top[0], top[1] - 0.70 * R), (top[0] + 0.12 * R, top[1] - 0.05 * R)]],
            P['c_staff'], line=lwf)                                     # chóp nhọn liền vòng
    cv.part([circle(*top, 0.36 * R)], P['c_staff'], line=lwf)           # vòng khoen TO (0.36R)
    cv.part([circle(*top, 0.22 * R)], P['c_bg'], line=lwf)              # lỗ rỗng rộng
    for s in (-1, 1):                                                   # 2 khuyên nhỏ RỖNG hai bên
        c2 = (top[0] + s * 0.36 * R, top[1] + 0.12 * R)
        cv.part([circle(*c2, 0.12 * R)], P['c_staff'], line=lwf)
        cv.part([circle(*c2, 0.065 * R)], P['c_bg'], line=lwf)
    return cv, k, hand


def chi_so(P, k, hand):
    R = P['R']
    t0, t1 = k.H(*P['gay_tren']), k.H(*P['gay_duoi'])
    ang = math.degrees(math.atan2(t0[0] - t1[0], t1[1] - t0[1]))
    return [
        ('A. Khung (gốc – giữ nguyên)', [
            ('A1', (k.hx - R + 12, k.hy + 20), f"Đầu R={R}px · viền {P['vien']}R · KẾ THỪA goc.py · dáng {P['dang']}"),
            ('A3', (k.bx - k.hb + 6, k.bot - 40), f"Thân cao {P['K']['than_cao']}R · tỉ lệ gốc"),
            ('A5', (hand[0] + 0.24 * R, hand[1] + 10), 'Bàn tay cầm tích trượng'),
        ]),
        ('B. Đầu & mặt (theo ảnh mẫu)', [
            ('B2', k.H(0.2, -0.8), 'MŨ LOTUS đỏ + viền vàng (5 cánh) + dải buông'),
            ('B5', k.H(-0.05 - 0.14, -0.06), 'Mắt bầu dục đen + đốm sáng (đồng bộ bộ)'),
            ('B6', k.H(0.2, -0.36), f"Lông mày dày {P['M']['may_day']}R, cong hiền"),
            ('B7', k.H(0.27, 0.48), 'Nụ cười nhỏ'),
        ]),
        ('C. Áo + cà sa (theo ảnh mẫu)', [
            ('C1', k.B(-0.3, 0.3), f"Áo vàng {P['c_robe']}"),
            ('C2', k.B(0.1, 1.5), f"Cà sa đỏ {P['c_kasaya']} + lưới ô vuông vàng"),
            ('C3', k.B(0.3, 1.3), 'Đai kem thắt nơ'),
        ]),
        ('D. Tích trượng vàng', [
            ('D2', (t0[0] - 10, t0[1] + 10), f"Cán vàng + đầu vòng khoen · nghiêng {ang:.0f}°"),
        ]),
    ]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cv, k, hand = draw(P)
    img = cv.save(os.path.join(OUT, 'duong-tang.png'))
    sheet(img, chi_so(P, k, hand), 'Đường Tăng – theo ảnh mẫu', os.path.join(OUT, 'duong-tang-bang.png'),
          note='Bám ảnh mẫu 8: mũ lotus + dải buông, áo vàng + cà sa đỏ patchwork, tích trượng vàng.')
    print('xong:', OUT)
