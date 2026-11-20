"""Trư Bát Giới – bản theo MẪU GEMINI (20/11/2026).

TỈ LỆ: giữ KHUNG GỐC Ngộ Không (goc.py, dang='map') – đầu R, thân bia mộ, bàn tay lơ lửng.
MÀU + CHI TIẾT: lấy từ ảnh mẫu Gemini assets/nhan-vat/gemini/bat-gioi/mau.png + spec.json
  - mũ tròn đen, viền vàng, mây vàng trước trán
  - mặt heo hồng: mắt cười ^_^, mày cong, má hồng, mõm oval 2 lỗ mũi, miệng cười lệch trái
  - tai quạt to cụp ra hai bên
  - áo đen hở ngực → bụng tròn + rốn; khăn cổ vàng thắt nút; đai vàng ngang thân, nút + 2 đuôi
  - đinh ba 9 răng bạc dựng gần thẳng đứng, 2 khâu vàng dưới lưỡi; bàn tay tròn hồng trơn

Chạy:  python scripts/hoathinh/chibi/bat_gioi_gemini.py
Ra:    build/thu-hoathinh/nhan-vat/bat-gioi-gemini.png
Chấm:  python scripts/hoathinh/gemini_nv.py cham bat-gioi build/thu-hoathinh/nhan-vat/bat-gioi-gemini.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from goc import tao_P  # noqa: E402
from khung import Khung, dau, than  # noqa: E402
from ve import Canvas, circle, ellipse, bar, lerp, catmull  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'nhan-vat')

P = tao_P(
    dang='map', head_c=(413, 399),
    c_bg='#F5F0E6',
    # ── màu theo mẫu Gemini (spec.json + đo ảnh) ──
    c_da='#FBBEC4', c_da_in='#F29AA8', c_ma='#F79AAA',
    c_mom='#F590A2', c_mui='#B94458',
    c_hat='#29282C', c_gold='#D3A85B', c_gold_dk='#A88040',
    c_robe='#29282C', c_robe_hi='#34333A',
    c_rake='#E0E0E2', c_pole='#C9CACF', c_bong='#E6DFD2',
    # ── chi tiết (toạ độ theo R) ──
    tai=[dict(goc=(-0.70, -0.40), tip=(-1.62, 0.50), w=1.18),        # tai trái quạt cụp ra ngoài
         dict(goc=(0.76, -0.46), tip=(1.56, 0.40), w=1.06)],         # tai phải
    mu=[(-0.95, -0.52), (-0.92, -0.86), (-0.68, -1.16), (-0.25, -1.32), (0.20, -1.32),
        (0.60, -1.15), (0.84, -0.86), (0.92, -0.58)],                 # mũ tròn dẹt đỉnh đội sát đầu
    vanh_y=(-0.52, -0.50, -0.58),                                     # mép mũ (trái, giữa, phải) – viền vàng
    may_van=(0.06, -0.92),                                            # mây vàng trước trán
    mat=[(-0.20, -0.10), (0.44, -0.12)], mat_w=0.15,
    may=[(-0.24, -0.40), (0.48, -0.42)],
    ma=[(-0.46, 0.12), (0.80, 0.06)],
    mom=dict(c=(0.26, 0.22), rx=0.38, ry=0.22),
    mui=[(0.13, 0.23), (0.39, 0.22)],
    mieng=[(-0.22, 0.56), (-0.04, 0.66), (0.14, 0.61), (0.20, 0.56)],
    bung=dict(c=(0.12, 1.28), rx=0.64, ry=0.62),                      # bụng hở (theo thân)
    ron=(0.10, 1.55),
    dai_y=1.78, dai_day=0.13,
    gay=dict(xien=8.0, tren=-0.62, duoi=0.75),                       # đinh ba: nghiêng 8°, đỉnh/đáy theo R
    lưỡi=dict(rong=1.06, rang=9, cao=0.26),
)


def la(g, t, w, n=8):
    """Hình lá/tai quạt từ gốc g tới chóp t, bề ngang w (px)."""
    dx, dy = t[0] - g[0], t[1] - g[1]
    L = math.hypot(dx, dy) or 1.0
    px, py = -dy / L * w / 2, dx / L * w / 2
    m = lerp(g, t, 0.45)
    q = lerp(g, t, 0.88)                                             # gần chóp: còn bè → chóp tròn
    return catmull([(g[0] - px * 0.7, g[1] - py * 0.7), (m[0] - px, m[1] - py), (q[0] - px * 0.6, q[1] - py * 0.6),
                    t, (q[0] + px * 0.6, q[1] + py * 0.6), (m[0] + px, m[1] + py),
                    (g[0] + px * 0.7, g[1] + py * 0.7)], n)


def may_cuon(cv, cx, cy, s, mau, ink, ld):
    """Mây cuộn tường vân: khối 3 bướu + đế, viền ngoài, 2 xoắn cuộn bên trong."""
    kh = may_vang(cx, cy, s)
    cv.part(kh, mau, line=ld)
    cv.part(kh, mau, line=0)
    for sx, r in ((-0.55, 0.22), (0.0, 0.30), (0.55, 0.22)):
        x0, y0 = cx + sx * s, cy + (0.05 if sx else -0.15) * s
        pts = [(x0 + r * s * t / 6.3 * math.cos(t), y0 + r * s * t / 6.3 * math.sin(t))
               for t in [i * 0.35 for i in range(19)]]
        cv.stroke(pts, ld * 0.55, color=ink)


def may_vang(cx, cy, s):
    """Mây vàng nhỏ: 3 cung tròn + đế."""
    return [circle(cx - 0.55 * s, cy + 0.10 * s, 0.36 * s, n=48), circle(cx, cy - 0.12 * s, 0.46 * s, n=48),
            circle(cx + 0.55 * s, cy + 0.10 * s, 0.36 * s, n=48),
            ellipse(cx, cy + 0.26 * s, 0.86 * s, 0.20 * s, n=48)]


def draw(P):
    R = P['R']
    W, H = P['canvas']
    cv = Canvas(W, H, bg=P['c_bg'], ink=P['c_ink'], line=P['vien'] * R)
    lw, ld = P['vien'] * R, P['vien_ct'] * R
    k = Khung(P['head_c'], R, P['K'])
    B = k.B

    # 0) bóng đổ dưới chân
    cv.part([ellipse(k.bx + 0.1 * R, k.bot + 0.02 * R, k.hb + 0.35 * R, 0.10 * R)], P['c_bong'], line=0)

    # 1) THÂN áo đen + phần hở ngực/bụng + đai vàng (cắt trong thân)
    body = than(cv, k, P['c_robe'])
    bg = P['bung']
    bc = B(*bg['c'])

    def ao(lay):
        # dải sáng nhẹ mép trái áo (mẫu có 2 tông đen)
        cv.part([[(k.bx - k.hb - 20, k.top), (k.bx - 0.55 * R, k.top), (k.bx - 0.7 * R, k.bot),
                  (k.bx - k.hb - 20, k.bot)]], P['c_robe_hi'], line=0, img=lay)
        # khe hở áo: MỘT đường cong mượt từ cổ ôm quanh bụng tròn (như mẫu)
        rx, ry = bg['rx'] * R, bg['ry'] * R
        ho = catmull([B(-0.22, -0.05), B(-0.26, 0.45), (bc[0] - rx * 0.92, bc[1] - ry * 0.35),
                      (bc[0] - rx, bc[1] + ry * 0.25), (bc[0] - rx * 0.6, bc[1] + ry * 0.85), (bc[0], bc[1] + ry),
                      (bc[0] + rx * 0.6, bc[1] + ry * 0.85), (bc[0] + rx, bc[1] + ry * 0.25),
                      (bc[0] + rx * 0.92, bc[1] - ry * 0.35), B(0.50, 0.45), B(0.46, -0.05)], 10)
        cv.part([ho], P['c_da'], line=ld, img=lay)
        # đai lưng vàng ngang cả thân
        y0, y1 = k.top + P['dai_y'] * R, k.top + (P['dai_y'] + P['dai_day']) * R
        cv.part([[(k.bx - k.hb - 30, y0), (k.bx + k.hb + 30, y0 - 0.04 * R),
                  (k.bx + k.hb + 30, y1 - 0.04 * R), (k.bx - k.hb - 30, y1)]], P['c_gold'], line=ld, img=lay)
    cv.clip_layer(ao, [body])
    cv.stroke(body + body[:2], lw)

    # rốn
    rx_, ry_ = B(*P['ron'])
    cv.part([circle(rx_, ry_, 0.035 * R)], P['c_ink'], line=0)
    cv.stroke(catmull([(rx_ - 0.06 * R, ry_ - 0.05 * R), (rx_, ry_ - 0.08 * R), (rx_ + 0.06 * R, ry_ - 0.05 * R)], 6),
              ld * 0.6, color=P['c_da_in'])
    # nút đai + 2 đuôi
    ny = k.top + (P['dai_y'] + P['dai_day'] / 2) * R
    nx = bc[0]
    for s in (-1, 1):
        cv.part([catmull([(nx + s * 0.03 * R, ny), (nx + s * 0.16 * R, ny + 0.12 * R), (nx + s * 0.22 * R, ny + 0.36 * R),
                          (nx + s * 0.10 * R, ny + 0.32 * R), (nx + s * 0.03 * R, ny)], 8)],
                P['c_gold'], line=ld)
    cv.part([ellipse(nx, ny, 0.12 * R, 0.10 * R)], P['c_gold'], line=ld)

    # 2) TAI quạt (sau đầu) + lòng tai
    for ti in P['tai']:
        g, t = k.H(*ti['goc']), k.H(*ti['tip'])
        cv.part([la(g, t, ti['w'] * R)], P['c_da'], line=lw)
        gi = lerp(g, t, 0.18)
        cv.part([la(gi, lerp(g, t, 0.85), ti['w'] * R * 0.5)], P['c_da_in'], line=0)

    # 3) ĐẦU tròn
    head = dau(cv, k, P['c_da'])
    cv.stroke(head + head[:2], lw)                                   # viền đầu TRƯỚC mũ

    # 4) MŨ đen + viền vàng + mây vàng
    mu = [k.H(*p) for p in P['mu']]
    yl, ym, yr = P['vanh_y']
    vanh = catmull([k.H(0.90, yr), k.H(0.0, ym - 0.02), k.H(-0.93, yl)], 10)
    cv.part([catmull(mu, 8) + vanh], P['c_hat'], line=lw)
    cv.stroke(catmull([k.H(-0.90, yl - 0.07), k.H(0.0, ym - 0.10), k.H(0.87, yr - 0.07)], 10), 0.085 * R,
              color=P['c_gold'])
    may_cuon(cv, *k.H(*P['may_van']), 0.27 * R, P['c_gold'], P['c_gold_dk'], ld)

    # 5) MẶT: má → mõm → lỗ mũi → mắt cười → mày → miệng
    for p in P['ma']:
        cv.part([ellipse(*k.H(*p), 0.17 * R, 0.11 * R)], P['c_ma'], line=0)
    mc = P['mom']
    cv.part([ellipse(*k.H(*mc['c']), mc['rx'] * R, mc['ry'] * R)], P['c_mom'], line=ld * 1.2)
    for p in P['mui']:
        cv.part([ellipse(*k.H(*p), 0.055 * R, 0.085 * R)], P['c_mui'], line=0)
    for p in P['mat']:                                               # mắt cười ^ ^
        x, y = k.H(*p)
        ew = P['mat_w'] * R
        arc = [(x + ew * math.cos(math.radians(t)), y + 0.04 * R - ew * 0.8 * math.sin(math.radians(t)))
               for t in range(10, 171, 8)]                            # cung tròn mềm ∩
        cv.stroke(arc, 0.06 * R)
    for p in P['may']:                                               # mày cong mảnh
        x, y = k.H(*p)
        cv.stroke(catmull([(x - 0.10 * R, y + 0.02 * R), (x, y - 0.045 * R), (x + 0.10 * R, y + 0.02 * R)], 8),
                  0.05 * R)
    cv.stroke(catmull([k.H(*p) for p in P['mieng']], 10), 0.055 * R)

    # 6) KHĂN CỔ vàng: dải quanh cổ + nút thắt + 2 vạt tam giác
    c0, c1 = B(-0.62, -0.02), B(0.80, -0.06)
    cv.part([catmull([c0, B(0.1, 0.16), c1], 8) + catmull([B(0.80, 0.08), B(0.1, 0.30), B(-0.62, 0.12)], 8)],
            P['c_gold'], line=ld)
    kx, ky = B(0.12, 0.22)
    for s in (-1, 1):
        cv.part([catmull([(kx, ky), (kx + s * 0.20 * R, ky + 0.02 * R), (kx + s * 0.36 * R, ky + 0.16 * R),
                          (kx + s * 0.28 * R, ky + 0.40 * R), (kx + s * 0.06 * R, ky + 0.16 * R), (kx, ky)], 8)],
                P['c_gold'], line=ld)
    cv.part([ellipse(kx, ky + 0.02 * R, 0.105 * R, 0.095 * R)], P['c_gold_dk'], line=ld)

    # 7) ĐINH BA: cán bạc gần thẳng đứng qua bàn tay, lưỡi 9 răng hướng lên, 2 khâu vàng
    K = P['K']
    hx_, hy_ = B(K['tay_x'], K['tay_y'])
    g = P['gay']
    a = math.radians(g['xien'])
    ux, uy = math.sin(a), -math.cos(a)                               # hướng lên (nghiêng phải)
    top = k.hy + g['tren'] * R
    bot = k.bot - 0.02 * R
    t0 = (hx_ + ux * (hy_ - top) / -uy, top)
    t1 = (hx_ - ux * (bot - hy_) / -uy, bot)
    hpole = 0.07 * R
    cv.part([bar((t0[0] - ux * 0.1 * R, t0[1] - uy * 0.1 * R), t1, hpole)], P['c_pole'], line=ld)
    lw_ = P['lưỡi']
    nx_, ny_ = -uy, ux
    hw = lw_['rong'] * R / 2
    th = 0.12 * R                                                    # thanh ngang trên cùng
    cao = lw_['cao'] * R                                             # răng chĩa XUỐNG từ thanh ngang
    tl = (t0[0] - nx_ * hw, t0[1] - ny_ * hw)
    tr = (t0[0] + nx_ * hw, t0[1] + ny_ * hw)
    d = lambda q, o: (q[0] - ux * o, q[1] - uy * o)                  # dịch xuống dọc cán
    # lưỡi cào LIỀN MỘT KHỐI (như mẫu): thanh ngang dày + răng to bo tròn + cổ nối cán hình chữ T
    rt = 0.032 * R                                                   # nửa bề ngang răng (răng to, khe hẹp)
    ex = 0.03 * R
    a0 = (tl[0] - nx_ * ex, tl[1] - ny_ * ex)
    a1 = (tr[0] + nx_ * ex, tr[1] + ny_ * ex)
    khoi = [bar(d(a0, th / 2), d(a1, th / 2), th / 2 + 0.01 * R)]
    for i in range(lw_['rang']):
        c = lerp(tl, tr, i / (lw_['rang'] - 1))
        r0, r1 = d(c, th * 0.5), d(c, th + cao - rt)
        khoi += [bar(r0, r1, rt), circle(*r1, rt, n=20)]
    khoi.append(bar(t0, d(t0, th + cao + 0.05 * R), hpole))          # cổ nối cán
    cv.part(khoi, P['c_rake'], line=ld * 0.5)                            # viền từng mảnh…
    cv.part(khoi, P['c_rake'], line=0)                               # …rồi tô lại → chỉ còn viền ngoài
    for j in range(2):                                               # 2 khâu vàng dưới lưỡi cào
        o = th + cao + (0.06 + j * 0.12) * R
        cv.part([bar(d(t0, o), d(t0, o + 0.07 * R), hpole * 1.6)], P['c_gold'], line=ld)

    # 8) BÀN TAY tròn hồng trơn đè lên cán
    cv.part([circle(hx_, hy_, K['tay_r'] * R)], P['c_da'], line=lw)
    return cv


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, sys.argv[1] if len(sys.argv) > 1 else 'bat-gioi-gemini.png')
    draw(P).save(out)
    print('xong:', out)
