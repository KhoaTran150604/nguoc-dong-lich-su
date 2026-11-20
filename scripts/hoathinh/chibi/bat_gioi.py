"""Trư Bát Giới – vẽ theo HỒ SƠ TẠO HÌNH (docs/nhan-vat/bat-gioi-hoso.md) + ảnh mẫu chibi dễ thương.
Kế thừa THÔNG SỐ GỐC (goc.py), giữ nguyên TI_LE. Riêng:
- Mặt heo hiền/híp cười: mõm + 2 lỗ mũi, má ửng, mắt cười, tai quạt to.
- Mũ mềm tối màu + dải vàng cuộn trán (fillet).
- Áo ĐEN/chàm hở ngực + bụng tròn có rốn; khăn cổ vàng + đai lưng vàng.
- Tay phải cầm ĐINH BA chín răng, VÁC VAI – gọn sát thân.

Chạy:  python scripts/hoathinh/chibi/bat_gioi.py
Ra:    build/thu-hoathinh/nhan-vat/bat-gioi.png + bat-gioi-bang.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bang import sheet  # noqa: E402
from goc import tao_P  # noqa: E402
from khung import Khung, dau, than, ban_tay  # noqa: E402
from ve import Canvas, circle, ellipse, bar, lerp, catmull  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'nhan-vat')

P = tao_P(
    dang='map',                                                      # DÁNG MẬP chuẩn hoá (chung mọi NV mập); vẫn cùng chiều cao khung gốc
    head_c=(413, 399),
    c_bg='#F6F3EC',
    # màu (theo ảnh mẫu người dùng chọn)
    c_da='#F4BAB1', c_da_hi='#FBD9D2', c_da_in='#D99089', c_nostril='#7A4E48', c_snout='#EDA69D',
    c_hat='#202827', c_hat2='#151B1A', c_gold='#E6B23C', c_fillet='#F2CE63',
    c_robe='#26302E', c_robe2='#1C2322', c_sash='#E6B23C', c_sash_dk='#A5812F',
    c_mane='#4A3B2E', c_cheek='#F0A39E',
    c_pole='#B9BDC4', c_pole_hi='#D8DBE0', c_rake='#CDD2D8', c_rake_dk='#9CA2AB',

    # tai heo quạt: (gốc, đỉnh cụp, bề ngang gốc) theo R
    tai_heo=[dict(goc=(-0.78, -0.10), tip=(-1.62, 0.62), w=0.95),     # tai trái (quạt TO, cụp rõ)
             dict(goc=(0.92, -0.10), tip=(1.56, 0.56), w=0.84)],      # tai phải (to, hiện rõ)
    # bờm lông cứng sau gáy (sau đầu, trái)
    bom=[(-0.86, 0.30, -1.16, 0.46), (-0.92, 0.52, -1.20, 0.72)],     # (gx,gy, tx,ty)
    # mũ mềm: viền chỏm (trái→đỉnh→phải) + dải vàng trán
    mu=[(-0.80, -0.42), (-0.92, -0.86), (-0.70, -1.18), (-0.30, -1.36),
        (0.12, -1.36), (0.52, -1.18), (0.78, -0.86), (0.84, -0.46), (0.80, -0.42)],
    fillet_y=-0.42, fillet_x=(-0.78, 0.80),                           # dải vàng mép mũ (ngang trán, dưới mũ)
    mu_num=[(0.0, -1.14), (0.18, -1.13)],                            # 2 núm BÚP vàng (sát nhau, có đế)
    may=[(-0.03, -0.33), (0.56, -0.33)], may_w=0.30, may_a=0.08,     # lông mày DÀY cong vòm
    mat_rx=0.155, mat_ry=0.165, glint=0.06,                          # mắt TO TRÒN đen + đốm sáng TO (ảnh 7)
    # mõm + lỗ mũi + miệng cười (toạ độ đầu)
    mom=dict(c=(0.27, 0.31), rx=0.40, ry=0.29), mom_hi=(0.19, 0.22, 0.14, 0.08),  # mõm NHỎ lại (ảnh 6)
    mui=[(0.18, 0.30, 0.060), (0.37, 0.30, 0.060)],                  # 2 lỗ mũi OVAL ĐỨNG, gần nhau (ảnh 6)
    mieng=(0.27, 0.62, 0.18, 0.06),                                  # miệng cười nhỏ dưới mõm
    # mắt + má
    mat=[(-0.03, -0.10), (0.56, -0.10)], mat_w=0.13, mat_d=0.07,
    ma=[(-0.13, 0.06), (0.63, 0.06)], ma_r=(0.17, 0.12),

    # áo: hở ngực nối xuống BỤNG TRÒN + rốn; khăn cổ + đai lưng (toạ độ thân)
    nguc=dict(c=(0.09, 0.86), r=0.40),                                # ngực hở (nối nơ ↔ bụng)
    nguc_bung=dict(c=(0.12, 1.46), rx=0.66, ry=0.56),                 # bụng hở – LỆCH PHẢI (góc 3/4, không trực diện)
    lapel=[((-0.26, 0.10), (-0.46, 0.92)), ((0.40, 0.10), (0.62, 0.92))],  # cổ V gọn
    ron=(0.0, 1.58),                                                  # rốn lệch TRÁI bụng (3/4)
    khan=dict(y=0.14),                                                # khăn cổ: NƠ THẮT (vẽ ở draw)
    dai=(1.86, 2.02), dai_no=(0.05, 2.02, 0.12),                      # đai lưng vắt ngang bụng
    gau=(2.00, 0.0),

    # ĐINH BA chín răng – vác vai, khép sát thân; bàn tay nắm cán
    gay_tren=(1.55, -1.00), gay_duoi=(0.90, 3.00), gay_day=0.15,      # cán xám nghiêng phải, qua bàn tay gốc
    rake=dict(ngang=0.98, rang=9, cao=0.44, day_rang=0.095),          # răng cào dày/đặc
)


def draw(P):
    R = P['R']
    W, H = P['canvas']
    cv = Canvas(W, H, bg=P['c_bg'], ink=P['c_ink'], line=P['vien'] * R)
    ld = P['vien_ct'] * R
    k = Khung(P['head_c'], R, P['K'])
    B = k.B

    # 1) BỜM lông gáy (sau đầu)
    for gx, gy, tx, ty in P['bom']:
        g, t = k.H(gx, gy), k.H(tx, ty)
        dx, dy = t[0] - g[0], t[1] - g[1]
        L = math.hypot(dx, dy) or 1.0
        px, py = -dy / L * 0.14 * R, dx / L * 0.14 * R
        cv.part([[(g[0] - px, g[1] - py), (g[0] + px, g[1] + py), t]], P['c_mane'], line=P['vien'] * R)

    # 2) THÂN áo đen + hở ngực/bụng + khăn + đai
    body = than(cv, k, P['c_robe'])
    x0, x1 = k.bx - k.hb - 30, k.bx + k.hb + 30

    def ao(lay):
        cv.part([[(k.bx + 0.5 * R, k.top - 10), (x1, k.top - 10), (x1, k.bot + 10), (k.bx + 0.6 * R, k.bot + 10)]],
                P['c_robe2'], line=0, img=lay)                         # mảng tối rìa phải (nhẹ, không chia đôi)
        cv.part([circle(*B(*P['nguc']['c']), P['nguc']['r'] * R)], P['c_da'], line=0, img=lay)   # ngực hở
        for a, b in P['lapel']:                                       # viền vàng mép áo mở (cổ V gọn)
            cv.stroke([B(*a), B(*b)], ld * 1.1, color=P['c_gold'], img=lay)
        cy = P['khan']['y']                                           # khăn cổ: NƠ THẮT 2 cánh + nút + 2 đuôi
        for s in (-1, 1):
            cv.part([[B(0.07, cy), B(0.07 + s * 0.24, cy - 0.08), B(0.07 + s * 0.24, cy + 0.15)]],
                    P['c_sash'], line=ld, img=lay)                    # cánh nơ
            cv.part([[B(0.07 + s * 0.03, cy + 0.08), B(0.07 + s * 0.12, cy + 0.44), B(0.07 + s * 0.01, cy + 0.42)]],
                    P['c_sash'], line=ld, img=lay)                    # đuôi nơ
        cv.part([circle(*B(0.07, cy + 0.03), 0.09 * R)], P['c_sash_dk'], line=ld, img=lay)   # nút giữa
    cv.clip_layer(ao, [body])
    cv.stroke(body + body[:2], P['vien'] * R)

    # 3) BỤNG PHỆ lồi ra ngoài mép áo + sáng + rốn + đai lưng vắt ngang
    nb = P['nguc_bung']
    bc = B(*nb['c'])
    cv.part([ellipse(*bc, nb['rx'] * R, nb['ry'] * R)], P['c_da'], line=P['vien'] * R)
    cv.part([ellipse(bc[0] - 0.16 * R, bc[1] + 0.12 * R, nb['rx'] * 0.5 * R, nb['ry'] * 0.42 * R)], P['c_da_hi'], line=0)
    rx, ry = B(*P['ron'])
    cv.stroke([(rx - 0.05 * R, ry - 0.045 * R), (rx + 0.05 * R, ry + 0.045 * R)], ld * 0.8, color=P['c_da_in'])
    cv.stroke([(rx + 0.05 * R, ry - 0.045 * R), (rx - 0.05 * R, ry + 0.045 * R)], ld * 0.8, color=P['c_da_in'])
    d0, d1 = P['dai']                                                 # đai lưng vàng vắt ngang bụng
    xb0, xb1 = bc[0] - nb['rx'] * R, bc[0] + nb['rx'] * R
    cv.part([[(xb0, k.top + d0 * R), (xb1, k.top + d0 * R), (xb1, k.top + d1 * R), (xb0, k.top + d1 * R)]],
            P['c_sash'], line=ld)
    nx, ny, nr = P['dai_no']
    cv.part([circle(*B(nx, ny), nr * R)], P['c_sash_dk'], line=ld)

    # 4) TAI HEO quạt (sau đầu) + lòng hồng
    for ti in P['tai_heo']:
        g, t = k.H(*ti['goc']), k.H(*ti['tip'])
        dx, dy = t[0] - g[0], t[1] - g[1]
        L = math.hypot(dx, dy) or 1.0
        px, py = -dy / L * ti['w'] * R / 2, dx / L * ti['w'] * R / 2
        mid = lerp(g, t, 0.5)
        tri = [(g[0] - px, g[1] - py), (g[0] + px, g[1] + py),
               (t[0] + px * 0.35, t[1] + py * 0.35), (t[0] - px * 0.35, t[1] - py * 0.35)]
        cv.part([catmull([tri[0], (mid[0] + px, mid[1] + py), tri[2], tri[3], (mid[0] - px, mid[1] - py), tri[0]], 6)],
                P['c_da'], line=P['vien'] * R)
        gi = lerp(g, t, 0.16)
        cv.part([[(gi[0] - px * 0.5, gi[1] - py * 0.5), (gi[0] + px * 0.5, gi[1] + py * 0.5), lerp(gi, t, 0.6)]],
                P['c_da_in'], line=0)

    # 5) ĐẦU (tròn, da heo)
    head = dau(cv, k, P['c_da'], tai=None, toc=None)

    # 6) MŨ mềm tối dome CAO + dải vàng mép mũ + 2 núm vàng trên đỉnh (theo ảnh mẫu)
    mu = catmull([k.H(*p) for p in P['mu']], 6)
    cv.part([mu], P['c_hat'])
    fy, (fl, fr) = P['fillet_y'], P['fillet_x']
    rim = [k.H(fl, fy + 0.01), k.H((fl + fr) / 2, fy + 0.035), k.H(fr, fy + 0.01)]
    cv.stroke(rim, 0.16 * R, color=P['c_fillet'])                     # dải vàng ngang mép mũ (dày rõ)
    nk = [k.H(*p) for p in P['mu_num']]
    cv.part([bar(nk[0], nk[1], 0.045 * R)], P['c_gold'], line=ld)          # đế vàng nối 2 núm
    for xk, yk in nk:
        cv.part([ellipse(xk, yk - 0.04 * R, 0.07 * R, 0.105 * R)], P['c_gold'], line=ld)   # núm BÚP vàng
    cv.stroke(head + head[:2], P['vien'] * R)

    # 7) MẶT heo hiền: má → mõm → mũi → mắt cười → mày → miệng
    for (dx, dy) in P['ma']:
        cv.part([ellipse(*k.H(dx, dy), P['ma_r'][0] * R, P['ma_r'][1] * R)], P['c_cheek'], line=0)
    mc = P['mom']
    cv.part([ellipse(*k.H(*mc['c']), mc['rx'] * R, mc['ry'] * R)], P['c_snout'], line=ld)
    hx_, hy_, hrx, hry = P['mom_hi']
    cv.part([ellipse(*k.H(hx_, hy_), hrx * R, hry * R)], P['c_da_hi'], line=0)
    cv.stroke([k.H(mc['c'][0] + 0.02, mc['c'][1] - mc['ry'] * 0.5), k.H(mc['c'][0] + 0.02, mc['c'][1] + mc['ry'] * 0.35)],
              ld * 0.7, color=P['c_nostril'])
    for dx, dy, r in P['mui']:
        cv.part([ellipse(*k.H(dx, dy), r * 0.82 * R, r * 1.35 * R)], P['c_nostril'], line=0)   # lỗ mũi OVAL ĐỨNG
    for (dx, dy) in P['mat']:                                        # mắt HÍP CƯỜI (cung cong lên) – theo ảnh mẫu
        x, y = k.H(dx, dy)
        ew = P['mat_rx'] * R * 1.15
        cv.stroke(catmull([(x - ew, y + 0.03 * R), (x, y - P['mat_ry'] * R * 0.7), (x + ew, y + 0.03 * R)], 10), 0.06 * R)
    mw, ma_ = P['may_w'] * R, P['may_a'] * R                          # lông mày mảnh cong (trên mắt híp)
    for (dx, dy) in P['may']:
        x, y = k.H(dx, dy)
        cv.stroke(catmull([(x - mw / 2, y), (x, y - ma_), (x + mw / 2, y)], 10), 0.07 * R)
    mx, my, mrw, mrh = P['mieng']                                    # miệng cười nhỏ
    x, y = k.H(mx, my)
    cv.stroke([(x - mrw * R, y - 0.01 * R), (x, y + mrh * R), (x + mrw * R, y - 0.01 * R)], 0.05 * R)

    # 8) ĐINH BA chín răng – vác vai (cán đè lên bàn tay)
    t0, t1 = k.H(*P['gay_tren']), k.H(*P['gay_duoi'])
    h = P['gay_day'] * R / 2
    ux, uy = (t0[0] - t1[0]), (t0[1] - t1[1])
    L = math.hypot(ux, uy) or 1.0
    ux, uy = ux / L, uy / L
    nx, ny = -uy, ux
    cv.part([bar(t0, t1, h)], P['c_pole'])
    cv.part([circle(*t1, 0.16 * R)], P['c_da'], line=P['vien'] * R)   # chuôi tròn HỒNG cuối cán (theo mẫu)
    cv.stroke([lerp(t0, t1, 0.1), t1], h * 0.45, color=P['c_pole_hi'])
    for j in range(3):                                               # 3 KHÂU VÀNG
        o = (0.10 + j * 0.085) * R
        g0 = (t0[0] - ux * o, t0[1] - uy * o)
        g1 = (t0[0] - ux * (o + 0.045 * R), t0[1] - uy * (o + 0.045 * R))
        cv.part([bar(g0, g1, h + 2)], P['c_gold'], line=ld)
    rk = P['rake']                                                    # lưỡi + RĂNG BO TRÒN (ngón)
    hw = rk['ngang'] * R / 2
    base = (t0[0] + ux * 0.04 * R, t0[1] + uy * 0.04 * R)
    bl = (base[0] + nx * hw, base[1] + ny * hw)
    br = (base[0] - nx * hw, base[1] - ny * hw)
    thick = 0.15 * R
    cv.part([[bl, br, (br[0] + ux * thick, br[1] + uy * thick), (bl[0] + ux * thick, bl[1] + uy * thick)]], P['c_rake'])
    cao, dr = rk['cao'] * R, rk['day_rang'] * R
    teeth = []
    for i in range(rk['rang']):
        t = (i + 0.5) / rk['rang']
        cxp = lerp(bl, br, t)
        rootc = (cxp[0] + ux * thick * 0.5, cxp[1] + uy * thick * 0.5)
        tipc = (cxp[0] + ux * (thick + cao), cxp[1] + uy * (thick + cao))
        teeth.append(bar(rootc, tipc, dr * 0.55))                    # ngón bo tròn
        teeth.append(circle(*tipc, dr * 0.55))
    cv.part(teeth, P['c_rake'])

    # 9) BÀN TAY nắm cán (đè lên cán) + khe ngón + ngón cái
    hand = ban_tay(cv, k, P['c_da'])
    hx0, hy0 = hand
    for i in (-1, 0, 1):
        yy = hy0 + i * 0.12 * R
        cv.stroke([(hx0 - 0.17 * R, yy), (hx0 + 0.17 * R, yy)], ld * 0.55)   # khe ngón
    cv.part([circle(hx0 - 0.2 * R, hy0 + 0.22 * R, 0.1 * R)], P['c_da'], line=ld)   # ngón cái
    return cv, k, hand


def chi_so(P, k, hand):
    R = P['R']
    t0, t1 = k.H(*P['gay_tren']), k.H(*P['gay_duoi'])
    ang = math.degrees(math.atan2(t0[0] - t1[0], t1[1] - t0[1]))
    mc = P['mom']
    return [
        ('A. Khung (gốc – giữ nguyên)', [
            ('A1', (k.hx - R + 12, k.hy + 20), f"Đầu R={R}px · viền {P['vien']}R · KẾ THỪA goc.py"),
            ('A3', (k.bx - k.hb + 6, k.bot - 40), f"Thân cao {P['K']['than_cao']}R · tỉ lệ gốc không đổi"),
            ('A5', (hand[0] + 0.24 * R, hand[1] + 10), 'Bàn tay cầm cán đinh ba (vác vai)'),
        ]),
        ('B. Mặt heo hiền (riêng)', [
            ('B1', k.H(*P['tai_heo'][0]['tip']), f"Tai heo quạt to cụp: w {P['tai_heo'][0]['w']}R / {P['tai_heo'][1]['w']}R"),
            ('B2', k.H(0.08, -1.05), f"Mũ mềm tối {P['c_hat']} + dải vàng trán {P['c_fillet']}"),
            ('B3', k.H(*mc['c']), f"Mõm heo elip {2 * mc['rx']:.2f}×{2 * mc['ry']:.2f}R + 2 lỗ mũi"),
            ('B5', k.H(P['mat'][1][0], P['mat'][1][1]), 'Mắt híp cười (cung lõm) + má ửng → hiền, không gian xấu'),
            ('B7', k.H(P['mieng'][0], P['mieng'][1]), 'Miệng cười nhỏ'),
        ]),
        ('C. Áo đen hở bụng (riêng)', [
            ('C1', k.B(-0.3, 0.6), f"Áo thầy tu ĐEN/chàm {P['c_robe']} · hở ngực V viền vàng"),
            ('C2', k.B(*P['nguc_bung']['c']), 'Bụng tròn phệ, HỞ BỤNG + rốn'),
            ('C3', k.B(0.06, P['dai'][0] + 0.1), f"Khăn cổ + đai lưng vàng {P['c_sash']}"),
        ]),
        ('D. Đinh ba chín răng – vác vai', [
            ('D2', (t0[0] - 10, t0[1] + 10), f"Cửu xỉ đinh ba: cán gỗ + {P['rake']['rang']} răng thép + khâu vàng · vác vai (nghiêng {ang:.0f}°), sát thân"),
        ]),
    ]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cv, k, hand = draw(P)
    img = cv.save(os.path.join(OUT, 'bat-gioi.png'))
    sheet(img, chi_so(P, k, hand), 'Trư Bát Giới – theo hồ sơ', os.path.join(OUT, 'bat-gioi-bang.png'),
          note='Theo docs/nhan-vat/bat-gioi-hoso.md. Áo đen hở bụng, mũ + dải vàng, đinh ba vác vai.')
    print('xong:', OUT)
