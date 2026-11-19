"""Tôn Ngộ Không – bản 4: vẽ lại theo ĐÚNG ảnh mẫu người dùng gửi (đo tỉ lệ trực tiếp từ ảnh).

Dựng bằng khung chung (khung.py): dau() – than() – ban_tay() – khuon_mat(), rồi thêm đồ riêng của Ngộ Không.
MỌI SỐ TÍNH THEO R (bán kính đầu). Ví dụ than_cao=2.77 nghĩa là thân cao 2.77×R.
Bản cũ (bản 3): ngo_khong_ban3.py

Chạy:  python scripts/hoathinh/chibi/ngo_khong.py
Ra:    build/thu-hoathinh/nhan-vat/ngo-khong.png  ·  ngo-khong-bang.png (ảnh + chỉ số)  ·  ngo-khong-so-mau.png (so với mẫu)
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bang import sheet  # noqa: E402
from khung import Khung, dau, than, ban_tay, khuon_mat, duoi_xoan  # noqa: E402
from goc import tao_P  # noqa: E402
from ve import Canvas, circle, ellipse, scallop, bar, lerp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'nhan-vat')

# =====================================================================================
# BẢNG CHỈ SỐ (đơn vị R, trừ khi ghi px)
# =====================================================================================
# Ngộ Không = THÔNG SỐ GỐC (goc.py) + phần riêng bên dưới. K và M (tỉ lệ) kế thừa nguyên từ gốc.
P = tao_P(
    head_c=(413, 399),
    # màu riêng
    c_fur='#D08A56', c_fur_in='#F3B5AE', c_face='#FBD9CF',
    c_gold='#F3C232', c_gold_dk='#B8861A',
    c_robe='#EBB24A', c_robe2='#E58E2E', c_trim='#BA4139', c_shirt='#F6E8CF', c_vay='#C9742A',
    c_belt='#BA4139', c_hem='#373545',
    c_staff='#B9413A', c_staff_dk='#B9413A',
    # mặt: chỉ đặt vị trí 2 mắt (kế thừa mắt/mày/má từ gốc)
    M=dict(mat=[(-0.05, -0.05), (0.59, -0.05)], ma_hong_vt=[(-0.05, -0.05), (0.59, -0.05)]),

    # ---------- ĐẦU ----------
    tai=[(-1.16, -0.14, 0.31, 0.17), (1.02, -0.12, 0.21, 0.09)],   # (dx, dy, r, r lòng); vành tai MÀU DA, lòng hồng; to & nâng cao
    tai_net=[(-1.10, -0.30), (-1.24, -0.10), (-1.08, 0.12)],       # nét gập '<' trong tai trái
    toc=[(-0.64, -0.50), (-0.54, -0.90), (-0.40, -1.04), (-0.18, -0.90),   # cụm trái (thấp) + khía V vừa
         (0.04, -1.05), (0.18, -0.92),                                       # gai giữa + khía vừa
         (0.30, -1.18), (0.44, -0.94),                                       # gai cao nhất lệch phải (mềm)
         (0.60, -1.08), (0.82, -0.84), (0.98, -0.56), (0.82, -0.46)],        # gai phải + vạt rủ
    toc_net=[[(-0.42, -0.92), (-0.40, -1.04)], [(0.06, -1.00), (0.04, -1.14)],
             [(0.32, -1.16), (0.30, -1.32)], [(0.60, -0.94), (0.62, -1.08)],
             [(0.70, -0.74), (0.86, -0.80)]],                                 # nét lông trong từng gai (đậm hơn)
    kimco_y=-0.80, kimco_sag=0.07, kimco_x=(-0.72, 0.82), kimco_day=0.12,   # dải VÕNG nhẹ ở giữa, hai đầu thuôn
    kimco_nut=[(0.20, 0.12), (0.42, 0.12)],                                  # 2 nút vòng khuyên SÁT nhau, dồn phải (dx, r)
    mat_na=dict(thuy=[(0.00, -0.18, 0.42), (0.62, -0.18, 0.42)], cam=(0.30, 0.30, 0.62, 0.56),
                long=dict(arcs=[(0, 360)], bumps=22, amp=0.045)),       # mép lông xù CHẠY CẢ VÒNG

    # ---------- ÁO (theo thân: dx từ tâm thân, dy từ mép trên thân) ----------
    co_trai=((-0.28, 0.0), (0.44, 0.99)), co_phai=((0.58, 0.0), (0.16, 0.42)), co_day=0.11,
    ao_trong=[(-0.14, 0.0), (0.53, 0.0), (0.17, 0.37)],
    that_lung=(0.92, 1.10), nut_lung=(0.24, 1.00, 0.09), dai_lung=[((0.24, 1.00), (0.06, 1.44)), ((0.24, 1.00), (0.26, 1.40))],
    gau=(1.82, 4, 0.18),          # (dy, số răng, độ sâu)
    vay_khia=[('L', 1.30, 0.13), ('L', 1.52, 0.13), ('R', 1.18, 0.13), ('R', 1.46, 0.13), ('R', 1.70, 0.12)],   # khía tam giác da hổ
    ao_net=[[(-0.30, 0.16), (-0.12, 0.60)], [(0.34, 0.20), (0.22, 0.58)]],   # nếp gấp áo trên
    vay_soc=[(-0.34, 1.26, 0.20), (-0.06, 1.30, 0.22), (0.24, 1.26, 0.20),   # sọc da hổ trên váy
             (-0.20, 1.52, 0.16), (0.10, 1.54, 0.16), (0.40, 1.50, 0.14)],
    vien_ao_duoi=[[(-0.44, 1.20), (0.46, 1.20)]],   # đường ngăn thắt lưng / váy

    # ---------- ĐUÔI (dải xoắn trơn, viền đều) ----------
    duoi=dict(root=(-0.55, 1.15), c=(-1.18, 0.82), a0=25, turns=1.35, r0=0.62, r1=0.11, w0=0.19, w1=0.10, sang='#E6A676'),

    # ---------- GẬY (theo đầu) ----------
    gay_tren=(1.78, -1.76), gay_duoi=(1.02, 3.20), gay_day=0.23, gay_dau=0.44,
)


def draw(P):
    R = P['R']
    W, H = P['canvas']
    cv = Canvas(W, H, bg=P['c_bg'], ink=P['c_ink'], line=P['vien'] * R)
    ld = P['vien_ct'] * R
    k = Khung(P['head_c'], R, P['K'])
    Bp = lambda dx, dy: k.B(dx, dy)  # noqa: E731

    # 1) ĐUÔI (sau thân) – dải xoắn trơn
    duoi_xoan(cv, k, P['duoi'], P['c_fur'])

    # 2) THÂN() + áo
    body = than(cv, k, P['c_hem'])
    x0, x1 = k.bx - k.hb - 30, k.bx + k.hb + 30
    gy, gn, gd = P['gau']
    hem = [(x0 + (x1 - x0) * i / (gn * 2), k.top + (gy + (gd if i % 2 else 0)) * R) for i in range(gn * 2 + 1)]
    lt0, lt1 = P['that_lung']

    def ao(lay):
        cv.part([[(x0, k.top - 10), (x1, k.top - 10)] + hem[::-1]], P['c_robe2'], line=0, img=lay)
        cv.part([[(x0, k.top - 10), (x1, k.top - 10), (x1, k.top + lt0 * R), (x0, k.top + lt0 * R)]], P['c_robe'], line=0, img=lay)
        cv.stroke(hem, P['vien'] * R, img=lay)
        for side, dy, sau in P['vay_khia']:                  # khía tam giác da hổ ăn vào từ mép
            s = -1 if side == 'L' else 1
            xe = k.bx + s * k.half_at(k.top + dy * R)
            tip = (xe - s * sau * R, k.top + dy * R)
            cv.part([[(xe, k.top + (dy - 0.14) * R), tip, (xe, k.top + (dy + 0.14) * R)]], P['c_vay'], line=0, img=lay)
        cv.part([[Bp(*p) for p in P['ao_trong']]], P['c_shirt'], line=ld * 0.6, img=lay)
        for a, b in (P['co_phai'], P['co_trai']):
            cv.part([bar(Bp(*a), Bp(*b), P['co_day'] * R / 2)], P['c_trim'], line=ld * 0.6, img=lay)
        cv.part([[(x0, k.top + lt0 * R), (x1, k.top + lt0 * R), (x1, k.top + lt1 * R), (x0, k.top + lt1 * R)]],
                P['c_belt'], line=ld * 0.6, img=lay)
        for seg in P.get('ao_net', []):                      # nếp gấp áo trên
            cv.stroke([Bp(*q) for q in seg], ld * 0.7, color=P['c_robe2'], img=lay)
        for dx, dy, h in P.get('vay_soc', []):               # sọc da hổ trên váy
            x, y = Bp(dx, dy)
            cv.stroke([(x, y), (x, y + h * R)], ld * 0.8, color=P['c_vay'], img=lay)
        for seg in P.get('vien_ao_duoi', []):                # nếp/đường gấp trên váy
            cv.stroke([Bp(*q) for q in seg], P['vien'] * R * 0.55, img=lay)
    cv.clip_layer(ao, [body])
    cv.stroke(body + body[:2], P['vien'] * R)
    nx, ny, nr = P['nut_lung']
    for a, b in P['dai_lung']:
        cv.part([bar(Bp(*a), Bp(*b), 0.06 * R)], P['c_belt'], line=ld)
    cv.part([circle(*Bp(nx, ny), nr * R)], P['c_belt'], line=ld)

    # 3) BÀN_TAY() – vẽ trước, gậy đè lên
    hand = ban_tay(cv, k, P['c_face'])

    # 4) ĐẦU() – viền trên gồ ghề theo chỏm lông (gộp luôn, không là vòng tròn liền)
    head = dau(cv, k, P['c_fur'], P['tai'], P['c_fur_in'], ld, mau_tai=P['c_face'],
               net_tai=P['tai_net'], toc=P['toc'])
    for seg in P['toc_net']:                            # nét lông mảnh trong chỏm
        cv.stroke([k.H(*q) for q in seg], ld)

    # 5) MẶT NẠ (lệch phải, cắt trong đầu) + KIM CÔ
    mn = P['mat_na']

    def mat_na(lay):
        shapes = [circle(*k.H(dx, dy), r * R) for dx, dy, r in mn['thuy']]
        cdx, cdy, rx, ry = mn['cam']
        lg = mn['long']
        shapes.append(scallop(*k.H(cdx, cdy), rx * R, ry * R, lg['arcs'], lg['bumps'], lg['amp']))
        cv.part(shapes, P['c_face'], line=ld, img=lay)

    xL, xR = P['kimco_x']
    yc = lambda dx: P['kimco_y'] + P['kimco_sag'] * math.sin(math.pi * (dx - xL) / (xR - xL))  # noqa: E731

    def kim_co(lay):
        xs = [xL + (xR - xL) * i / 60 for i in range(61)]
        hd = P['kimco_day'] / 2
        top = [k.H(dx, yc(dx) - hd) for dx in xs]
        bot = [k.H(dx, yc(dx) + hd) for dx in xs][::-1]
        cv.part([top + bot], P['c_gold'], line=ld, img=lay)
    cv.clip_layer(mat_na, [head])
    cv.clip_layer(kim_co, [head])
    cv.stroke(head + head[:2], P['vien'] * R)
    for dx, r in P['kimco_nut']:                       # nút = vòng khuyên: vành vàng + lõi tối + chấm vàng
        x, by = k.hx + dx * R, k.hy + yc(dx) * R
        cv.part([circle(x, by, r * R)], P['c_gold'], line=ld)
        cv.part([circle(x, by, r * 0.52 * R)], P['c_ink'], line=0)
        cv.dot(x, by, r * 0.22 * R, P['c_gold'])

    # 6) KHUÔN_MẶT()
    khuon_mat(cv, k, P['M'], P['c_ink'])

    # 7) GẬY (đè lên bàn tay)
    t0, t1 = k.H(*P['gay_tren']), k.H(*P['gay_duoi'])
    h = P['gay_day'] * R / 2
    L = math.hypot(t1[0] - t0[0], t1[1] - t0[1])
    c = P['gay_dau'] * R / L
    cv.part([bar(t0, t1, h)], P['c_staff'])
    cv.part([bar(lerp(t0, t1, c), lerp(t0, t1, 1 - c), h * 0.3)], P['c_staff_dk'], line=0)
    for a, b in ((0, c), (1 - c, 1)):
        cv.part([bar(lerp(t0, t1, a), lerp(t0, t1, b), h + 2)], P['c_gold'], line=ld)
        m = (a + b) / 2                                    # vạch đen chia đôi đầu vàng
        cv.part([bar(lerp(t0, t1, m - 0.006), lerp(t0, t1, m + 0.006), h + 2)], P['c_ink'], line=0)
    return cv, k, hand


def chi_so(P, k, hand):
    R = P['R']
    K, M = P['K'], P['M']
    f = lambda v: f'{v:.2f}R ({v * R:.0f}px)'  # noqa: E731
    t0, t1 = k.H(*P['gay_tren']), k.H(*P['gay_duoi'])
    ang = math.degrees(math.atan2(t0[0] - t1[0], t1[1] - t0[1]))
    gap = hand[0] - K['tay_r'] * R - (k.bx + k.half_at(hand[1]))
    ex, ey = k.H(*M['mat'][1])
    return [
        ('A. Khung chung', [
            ('A1', (k.hx - R + 12, k.hy + 20), f"Đầu TRÒN R={R}px · viền {P['vien']}R ({P['vien'] * R:.0f}px)"),
            ('A2', (k.bx, k.top + 4), f"Đầu lệch PHẢI {-K['than_lech_x']:.2f}R so với thân · đầu chạm thân"),
            ('A3', (k.bx - k.hb + 6, k.bot - 40), f"Thân cao {f(K['than_cao'])} · rộng {K['than_rong_tren']:.2f}–{K['than_rong_duoi']:.2f}R · bo {K['than_bo_tren']}R"),
            ('A4', None, f"Đầu : thân = 2R : {K['than_cao']}R = 1 : {K['than_cao'] / 2:.2f}"),
            ('A5', (hand[0] + K['tay_r'] * R, hand[1] + 10), f"Bàn tay r={f(K['tay_r'])} · cách thân {gap / R:.2f}R · gậy đè lên tay"),
        ]),
        ('B. Đầu & mặt (quay 3/4 sang phải)', [
            ('B1', k.H(P['tai'][0][0] - P['tai'][0][2] * 0.7, 0), f"Tai trái r={P['tai'][0][2]}R · tai phải r={P['tai'][1][2]}R (nhỏ hơn, bị khuất)"),
            ('B2', k.H(0.20, -1.30), 'Chỏm lông 4 cụm (phải rủ thành vạt) + nét lông trong'),
            ('B3', k.H(-0.6, P['kimco_y'] + 0.1), f"Kim cô võng giữa (sag {P['kimco_sag']}R), dày {P['kimco_day']}R · 2 nút vòng khuyên r={P['kimco_nut'][0][1]}R"),
            ('B4', k.H(0.6, 0.9), 'Mặt nạ lệch phải: 2 thùy + cằm, mép trái lông xù'),
            ('B5', (ex + M['mat_rx'] * R, ey), f"Mắt đen bầu dục {2 * M['mat_rx']:.2f}×{2 * M['mat_ry']:.2f}R (mắt thường, không đỏ)"),
            ('B6', (ex, ey + M['may_y'] * R), f"Lông mày cung dài {M['may_rong']}R · dày {M['may_day']}R"),
            ('B7', k.H(0.3, 0.55), 'Không vẽ miệng (đúng mẫu) · má hồng quầng mắt'),
        ]),
        ('C. Trang phục', [
            ('C1', k.B(0.45, 0.6), f"Áo trên {P['c_robe']} · cổ chéo viền {P['c_trim']} dày {P['co_day']}R"),
            ('C2', k.B(0.23 + P['nut_lung'][2], 1.30), f"Thắt lưng {P['that_lung'][0]}–{P['that_lung'][1]}R · nút + 2 dải"),
            ('C3', k.B(0.55, 1.9), f"Váy da hổ {P['c_robe2']} + vệt lông"),
            ('C4', k.B(-0.2, P['gau'][0] + 0.25), f"Gấu răng cưa ở {P['gau'][0]}R · {P['gau'][1]} răng · nền {P['c_hem']}"),
        ]),
        ('D. Đuôi · gậy', [
            ('D1', k.B(P['duoi']['c'][0] - P['duoi']['r0'], P['duoi']['c'][1]), f"Đuôi xoắn trơn: dày {P['duoi']['w0']}→{P['duoi']['w1']}R · {P['duoi']['turns']} vòng"),
            ('D2', (t0[0] - 10, t0[1] + 20), f"Gậy dày {P['gay_day']}R · dài {math.hypot(t1[0] - t0[0], t1[1] - t0[1]) / R:.1f}R · nghiêng {ang:.0f}° · đầu vàng {P['gay_dau']}R"),
        ]),
    ]


def so_mau(img):
    """Ảnh mẫu (phóng to) cạnh bản vẽ để so."""
    ref = os.path.join(ROOT, 'assets', 'nhan-vat', 'mau', 'ngo-khong-mau.png')
    if not os.path.exists(ref):
        return None
    a = Image.open(ref).convert('RGB')
    a = a.resize((int(a.width * 1000 / a.height), 1000), Image.LANCZOS)
    out = Image.new('RGB', (a.width + img.width + 20, 1060), (255, 255, 255))
    out.paste(a, (0, 60))
    out.paste(img.convert('RGB'), (a.width + 20, 60))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 30)
    d.text((20, 14), 'MẪU', font=f, fill=(200, 40, 40))
    d.text((a.width + 40, 14), 'BẢN VẼ (bản 9)', font=f, fill=(40, 110, 200))
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cv, k, hand = draw(P)
    img = cv.save(os.path.join(OUT, 'ngo-khong.png'))
    sheet(img, chi_so(P, k, hand), 'Tôn Ngộ Không – bản 9', os.path.join(OUT, 'ngo-khong-bang.png'),
          note='Mọi số theo R (bán kính đầu). Góp ý theo mã, vd "A2 đầu lệch phải 0.4R".')
    sm = so_mau(img)
    if sm:
        sm.save(os.path.join(OUT, 'ngo-khong-so-mau.png'))
    print('xong:', OUT)
