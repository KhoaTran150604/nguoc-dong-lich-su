"""Tôn Ngộ Không – nhân vật chibi đầu tiên theo phong cách 'đầu tròn to, thân ống ngắn, màu phẳng, viền đều'.

Mọi con số nằm trong bảng P bên dưới (toạ độ px trên khung 800×1000, gốc trên-trái).
Sửa số → chạy lại → xem ảnh. Bảng giải thích: docs/nhan-vat/ngo-khong-chi-so.md

Chạy:  python scripts/hoathinh/chibi/ngo_khong.py
Ra:    build/thu-hoathinh/nhan-vat/ngo-khong.png          (nhân vật)
       build/thu-hoathinh/nhan-vat/ngo-khong-chi-so.png   (có đường gióng + số đo)
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bang import sheet  # noqa: E402
from ve import Canvas, circle, ellipse, scallop, trapezoid, rrect, bar, lerp, hx  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, 'build', 'thu-hoathinh', 'nhan-vat')

# =====================================================================================
# BẢNG CHỈ SỐ (sửa ở đây)
# =====================================================================================
P = dict(
    # --- Khung & nét ---
    canvas=(800, 1000),
    line=7,                 # độ dày viền ngoài (px)
    line_detail=5,          # viền chi tiết nhỏ (mắt, cổ áo, nút)

    # --- Màu (phẳng) ---
    c_bg='#F6F3EC', c_ink='#2A211E',
    c_fur='#C98244',        # lông nâu
    c_fur_in='#F1C49B',     # trong tai
    c_face='#F7E0D2',       # mặt nạ mặt (kem hồng)
    c_eye='#E0575E',        # tròng mắt đỏ (hỏa nhãn kim tinh)
    c_gold='#F3C232', c_gold_dk='#C8961E',
    c_robe='#F2A33A', c_robe_dk='#D9852A', c_collar='#FBD27A',
    c_belt='#C9362E',
    c_pants='#3B3550',
    c_staff='#B8322A', c_staff_dk='#8E2620',
    c_shadow='#E2DCCF',

    # --- ĐẦU ---
    # Mọi số đo đầu/mặt bên dưới viết theo đầu chuẩn R=160 (head_ref_r) và TỰ CO GIÃN theo head_r.
    head_c=(430, 432), head_r=120, head_ref_r=160,  # đầu TRÒN TUYỆT ĐỐI, lệch phải 38 so với thân (về phía gậy)
    
    # Tai
    ear_dx=165, ear_dy=25, ear_r=44, ear_in_r=26,   # tai cách tâm đầu dx, thấp hơn dy

    # Chỏm lông trên đầu (răng cưa)
    hair=[(-74, -95), (-70, -173), (-34, -137), (-6, -213), (24, -143), (62, -181), (74, -95)],  # so với tâm đầu

    # Vòng kim cô
    band_dy=-77, band_h=28, band_bend=0.00035,  # mép trên cao hơn tâm đầu 77, bề dày, độ cong (∪)
    stud_r=(12, 15, 12), stud_dx=34,           # 3 nút vàng: bán kính trái/giữa/phải, khoảng cách

    # Mặt nạ (2 thùy mắt + cằm, mép lông)
    face_lobe_dx=44, face_lobe_dy=26, face_lobe_r=64,   # mặt nạ nằm TRỌN trong vòng đầu, mép trơn
    face_chin=(0, 78, 112, 62),                # (dx, dy, rx, ry) so với tâm đầu

    # Mắt: đen tròn bình thường, 2 đốm sáng (thân thiện)
    eye_dx=40, eye_dy=34, eye_rx=15, eye_ry=19, glint_r=6, glint2_r=3,
    # Lông mày: cung cong nhướn lên (vui), không nhíu
    brow_dy=-36, brow_w=34, brow_arc=7, brow_t=8,
    # Mũi, miệng cười mở, má hồng
    nose_dx=7, nose_dy=62, nose_r=4.5,
    mouth_dy=78, mouth_w=46, mouth_h=26, c_mouth='#8A2E2B', c_tongue='#EE8C8C',
    blush_dx=74, blush_dy=66, blush_rx=17, blush_ry=10, c_blush='#F3A6A0',

    # --- THÂN ---
    body_cx=392, body_top=528, body_bot=872, body_half_top=98, body_half_bot=120, body_round=26,
    hem_y=812, hem_teeth=7, hem_depth=26,      # gấu áo răng cưa
    collar_w=22,
    collar_A=((330, 535), (430, 705)),         # vạt áo phải đè sang trái
    collar_B=((458, 535), (392, 640)),
    belt_y=700, belt_h=34, knot_r=18, knot_dx=-6,
    ribbons=[((-6, 0), (-32, 84), 14), ((-6, 0), (16, 90), 14)],  # dải thắt lưng: (từ, đến) so với nút, bề ngang
    robe_shade_x=0.45,                         # mảng tối áo bắt đầu từ 45% nửa thân bên phải
    neck_shadow=dict(dy=150, rx=120, ry=40),   # bóng đầu đổ xuống áo

    # Tay: KHÔNG có cánh tay – chỉ 1 bàn tay tròn lơ lửng cách thân, cầm gậy
    hand=(565, 708), hand_r=28,

    # Đuôi (từ hông trái, cong ra rồi cuộn tròn)
    tail_base=[(330, 800), (262, 806), (205, 780)],
    tail_curl=dict(c=(196, 726), r0=54, r1=24, a0=100, turns=0.95),
    tail_thick=24,

    # --- GẬY NHƯ Ý ---
    staff_top=(666, 160), staff_bot=(520, 950), staff_half=13, staff_cap=58,
    grip=dict(len=40, half=14),                # ngón tay quấn qua gậy

    ground_y=876, shadow_rx=190, shadow_ry=22,
)


HEAD_KEYS = ('ear_dx', 'ear_dy', 'ear_r', 'ear_in_r', 'hair', 'band_dy', 'band_h', 'stud_r', 'stud_dx',
             'face_lobe_dx', 'face_lobe_dy', 'face_lobe_r', 'face_chin', 'eye_dx', 'eye_dy',
             'eye_rx', 'eye_ry', 'glint_r', 'glint2_r', 'brow_dy', 'brow_w', 'brow_arc', 'brow_t', 'nose_dx', 'nose_dy',
             'nose_r', 'mouth_dy', 'mouth_w', 'mouth_h', 'blush_dx', 'blush_dy', 'blush_rx', 'blush_ry', 'neck_shadow')


def scaled(P):
    """Co giãn mọi số đo đầu theo head_r / head_ref_r; trả bảng với toạ độ tuyệt đối dùng để vẽ."""
    k = P['head_r'] / P['head_ref_r']

    def sc(v):
        if isinstance(v, (int, float)):
            return v * k
        if isinstance(v, (list, tuple)):
            return type(v)(sc(x) for x in v)
        if isinstance(v, dict):
            return {a: sc(b) for a, b in v.items()}
        return v
    Q = dict(P)
    for key in HEAD_KEYS:
        Q[key] = sc(P[key])
    hcx, hcy = P['head_c']
    Q['hair'] = [(hcx + x, hcy + y) for x, y in Q['hair']]
    Q['band_y'] = hcy + Q['band_dy']
    Q['band_bend'] = P['band_bend'] / k
    return Q


def draw(P):
    P = scaled(P)
    W, H = P['canvas']
    cv = Canvas(W, H, bg=P['c_bg'], ink=P['c_ink'], line=P['line'])
    ld = P['line_detail']
    hcx, hcy = P['head_c']
    R = P['head_r']

    # 0) bóng đất
    cv.part([ellipse(P['body_cx'] + 20, P['ground_y'], P['shadow_rx'], P['shadow_ry'])], P['c_shadow'], line=0)

    # 1) ĐUÔI (sau thân)
    tc = P['tail_curl']
    curl = []
    steps = 60
    for i in range(steps + 1):
        t = i / steps
        a = math.radians(tc['a0'] + 360 * tc['turns'] * t)
        r = tc['r0'] + (tc['r1'] - tc['r0']) * t
        curl.append((tc['c'][0] + r * math.cos(a), tc['c'][1] + r * math.sin(a)))
    cv.tube(P['tail_base'] + curl, P['tail_thick'], P['c_fur'])

    # 3) THÂN: quần (tối) là cả khối, áo phủ lên phần trên có gấu răng cưa
    body = trapezoid(P['body_cx'], P['body_top'], P['body_bot'], P['body_half_top'], P['body_half_bot'], P['body_round'])
    cv.part([body], P['c_pants'])
    x0 = P['body_cx'] - P['body_half_bot'] - 20
    x1 = P['body_cx'] + P['body_half_bot'] + 20
    n = P['hem_teeth']
    hem = []
    for i in range(n * 2 + 1):
        x = x0 + (x1 - x0) * i / (n * 2)
        hem.append((x, P['hem_y'] + (P['hem_depth'] if i % 2 else 0)))
    robe = [(x0, P['body_top'] - 10), (x1, P['body_top'] - 10)] + hem[::-1]

    def robe_layer(lay):
        cv.part([robe], P['c_robe'], line=0, img=lay)
        # mảng tối phẳng bên phải thân
        sx = P['body_cx'] + P['body_half_top'] * P['robe_shade_x']
        cv.part([[(max(x, sx), y) for x, y in robe]], P['c_robe_dk'], line=0, img=lay)
        cv.stroke(hem, P['line'], img=lay)
        # bóng đầu đổ xuống cổ áo
        ns = P['neck_shadow']
        cv.part([ellipse(hcx, hcy + ns['dy'], ns['rx'], ns['ry'])], P['c_robe_dk'], line=0, img=lay)
        # cổ áo chéo
        for (a, b) in (P['collar_B'], P['collar_A']):
            cv.part([bar(a, b, P['collar_w'] / 2)], P['c_collar'], line=ld * 0.5, img=lay)
        # thắt lưng
        by = P['belt_y']
        cv.part([[(x0, by), (x1, by), (x1, by + P['belt_h']), (x0, by + P['belt_h'])]], P['c_belt'], line=ld * 0.5, img=lay)
        # khe chân
        cv.stroke([(P['body_cx'], P['hem_y'] + 34), (P['body_cx'], P['body_bot'] - 2)], ld, img=lay)
    cv.clip_layer(robe_layer, [body])
    # vẽ lại viền thân (bị lớp áo che) – chỉ nét
    cv.stroke(body + body[:2], P['line'] * 2)
    # dải & nút thắt lưng (tràn ra ngoài thân)
    kx, ky = P['body_cx'] + P['knot_dx'], P['belt_y'] + P['belt_h'] / 2
    for (a, b, w) in P['ribbons']:
        cv.part([bar((kx + a[0], ky + a[1]), (kx + b[0], ky + b[1]), w / 2)], P['c_belt'], line=ld)
    cv.part([circle(kx, ky, P['knot_r'])], P['c_belt'], line=ld)

    # 4) BÀN TAY (tròn, tách khỏi thân) – vẽ sau gậy ở bước 10 phần ngón
    cv.part([circle(*P['hand'], P['hand_r'])], P['c_fur'])

    # 5) TAI
    for s in (-1, 1):
        ex, ey = hcx + s * P['ear_dx'], hcy + P['ear_dy']
        cv.part([circle(ex, ey, P['ear_r'])], P['c_fur'])
        cv.part([circle(ex + s * 4, ey + 2, P['ear_in_r'])], P['c_fur_in'], line=ld)
        arc = [(ex + s * 4 + s * 13 * math.cos(math.radians(a)), ey + 2 + 13 * math.sin(math.radians(a))) for a in range(-70, 71, 10)]
        cv.stroke(arc, ld, color=P['c_fur'])

    # 6) ĐẦU + chỏm lông (một khối)
    head = circle(hcx, hcy, R, n=180)
    cv.part([head, P['hair']], P['c_fur'])

    # 7) MẶT NẠ (cắt trong đầu)
    lob = [circle(hcx + s * P['face_lobe_dx'], hcy + P['face_lobe_dy'], P['face_lobe_r']) for s in (-1, 1)]
    dx, dy, rx, ry = P['face_chin']
    chin = ellipse(hcx + dx, hcy + dy, rx, ry)
    cv.clip_layer(lambda lay: cv.part(lob + [chin], P['c_face'], line=ld, img=lay), [head])

    # 8) KIM CÔ (cắt trong đầu)
    def band_layer(lay):
        y0, h, k = P['band_y'], P['band_h'], P['band_bend']
        xs = range(int(hcx - R - 20), int(hcx + R + 21), 4)
        top = [(x, y0 - k * (x - hcx) ** 2) for x in xs]
        bot = [(x, y0 + h - k * (x - hcx) ** 2) for x in xs][::-1]
        cv.part([top + bot], P['c_gold'], line=ld, img=lay)
    cv.clip_layer(band_layer, [head])
    cv.stroke(head + head[:2], P['line'] * 2)        # vẽ lại viền đầu qua chỗ kim cô
    by = P['band_y'] + P['band_h'] / 2
    for i, r in zip((-1, 0, 1), P['stud_r']):
        cv.part([circle(hcx + i * P['stud_dx'], by, r)], P['c_gold'], line=ld)
        cv.dot(hcx + i * P['stud_dx'] - r * 0.3, by - r * 0.3, r * 0.3, '#FFF3C2')

    # 9) NÉT MẶT (thân thiện)
    for sgn in (-1, 1):
        bx, by_ = hcx + sgn * P['blush_dx'], hcy + P['blush_dy']
        cv.part([ellipse(bx, by_, P['blush_rx'], P['blush_ry'])], P['c_blush'], line=0)
    for sgn in (-1, 1):
        ex, ey = hcx + sgn * P['eye_dx'], hcy + P['eye_dy']
        cv.part([ellipse(ex, ey, P['eye_rx'], P['eye_ry'])], P['c_ink'], line=0)
        cv.dot(ex + P['eye_rx'] * 0.3, ey - P['eye_ry'] * 0.35, P['glint_r'], '#FFFFFF')
        cv.dot(ex - P['eye_rx'] * 0.35, ey + P['eye_ry'] * 0.4, P['glint2_r'], '#FFFFFF')
        w, a_ = P['brow_w'], P['brow_arc']
        brow = [(ex - w / 2 + w * i / 10, ey + P['brow_dy'] - a_ * math.sin(math.pi * i / 10)) for i in range(11)]
        cv.stroke(brow, P['brow_t'])
    for sgn in (-1, 1):
        cv.dot(hcx + sgn * P['nose_dx'], hcy + P['nose_dy'], P['nose_r'], P['c_ink'])
    my, mw, mh = hcy + P['mouth_dy'], P['mouth_w'], P['mouth_h']
    mouth = [(hcx - mw / 2 + mw * i / 20, my + mh * math.sin(math.pi * i / 20) ** 0.8) for i in range(21)]
    cv.part([mouth], P['c_mouth'], line=ld * 0.8)
    tongue = [p for p in ellipse(hcx, my + mh * 0.95, mw * 0.24, mh * 0.42) if p[1] < my + mh * 0.95]
    cv.part([tongue + [(hcx + mw * 0.24, my + mh * 0.95)]], P['c_tongue'], line=0)

    # 10) GẬY NHƯ Ý (qua bàn tay phải)
    t0, t1, h = P['staff_top'], P['staff_bot'], P['staff_half']
    L = math.hypot(t1[0] - t0[0], t1[1] - t0[1])
    c = P['staff_cap'] / L
    cv.part([bar(t0, t1, h)], P['c_staff'])
    cv.part([bar(lerp(t0, t1, c * 0.45), lerp(t0, t1, 1 - c * 0.45), h * 0.35)], P['c_staff_dk'], line=0)  # sọc tối
    for a, b in ((0, c), (1 - c, 1)):
        cv.part([bar(lerp(t0, t1, a), lerp(t0, t1, b), h + 3)], P['c_gold'], line=ld)
        m = (a + b) / 2
        cv.part([bar(lerp(t0, t1, m - 0.004), lerp(t0, t1, m + 0.004), h + 3)], P['c_gold_dk'], line=0)
    # ngón tay quấn qua gậy
    hx_, hy_ = P['hand']
    g = P['grip']
    ux, uy = (t1[0] - t0[0]) / L, (t1[1] - t0[1]) / L
    nx, ny = -uy, ux
    rr = rrect(-g['len'] / 2, -g['half'], g['len'] / 2, g['half'], g['half'] - 1)
    cv.part([[(hx_ + x * nx + y * ux, hy_ + x * ny + y * uy) for x, y in rr]], P['c_fur'], line=ld)
    return cv


def guides(img, P):
    """Ảnh phụ: đường gióng + số đo chính để cùng đánh giá."""
    P = scaled(P)
    im = img.convert('RGB').copy()
    d = ImageDraw.Draw(im)
    fp = os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf')
    f = ImageFont.truetype(fp, 18)
    red, blue = (214, 48, 49), (40, 110, 200)
    hcx, hcy = P['head_c']
    R = P['head_r']
    d.ellipse([hcx - R, hcy - R, hcx + R, hcy + R], outline=blue, width=2)
    d.line([hcx, hcy - R - 60, hcx, P['ground_y']], fill=blue, width=1)
    for y, lab in ((hcy - R, f'đỉnh đầu y={hcy - R}'), (hcy, f'tâm đầu y={hcy}  R={R}'),
                   (P['band_y'], f"kim cô y={P['band_y']:.0f} dày {P['band_h']:.0f}"),
                   (hcy + P['eye_dy'], f"mắt y={hcy + P['eye_dy']:.0f}"),
                   (P['body_top'], f"vai y={P['body_top']}"), (P['belt_y'], f"thắt lưng y={P['belt_y']}"),
                   (P['hem_y'], f"gấu áo y={P['hem_y']}"), (P['body_bot'], f"chân y={P['body_bot']}")):
        d.line([20, y, 780, y], fill=red, width=1)
        d.text((24, y - 22), lab, font=f, fill=red)
    head_h = 2 * R
    body_h = P['body_bot'] - (hcy + R)
    total = P['body_bot'] - min(y for _, y in P['hair'])
    txt = (f"Tỉ lệ: đầu 2R={head_h}  ·  thân lộ ra={body_h} (={body_h / head_h:.2f}×đầu)  ·  "
           f"cao tổng={total:.0f} (đầu chiếm {head_h / total:.0%})")
    d.rectangle([0, 960, 800, 1000], fill=(255, 255, 255))
    d.text((14, 970), txt, font=ImageFont.truetype(fp, 17), fill=(30, 30, 30))
    return im


def chi_so(P):
    """Danh sách chỉ số theo mã + điểm chỉ trên ảnh (lấy thẳng từ P → luôn khớp hình)."""
    Q = scaled(P)
    hcx, hcy = Q['head_c']
    R = Q['head_r']
    f = lambda v: f'{v:.0f}'  # noqa: E731
    head_h = 2 * R
    body_h = Q['body_bot'] - (hcy + R)
    top = min(y for _, y in Q['hair'])
    total = Q['body_bot'] - top
    t0, t1 = Q['staff_top'], Q['staff_bot']
    ang = math.degrees(math.atan2(t0[0] - t1[0], t1[1] - t0[1]))
    gap = Q['hand'][0] - Q['hand_r'] - (Q['body_cx'] + Q['body_half_top'] + (Q['body_half_bot'] - Q['body_half_top'])
                                         * (Q['hand'][1] - Q['body_top']) / (Q['body_bot'] - Q['body_top']))
    ex, ey = hcx - Q['eye_dx'], hcy + Q['eye_dy']
    return [
        ('A. Luật chung', [
            ('A1', None, f"Viền ngoài {Q['line']}px · màu {Q['c_ink']}"),
            ('A2', None, f"Viền chi tiết {Q['line_detail']}px (mắt, cổ áo, nút)"),
            ('A3', None, 'Màu phẳng, bóng = 1 mảng tối mép cứng, không gradient'),
            ('A4', (hcx - R + 10, hcy + R - 20), f"Đầu : thân = {f(head_h)} : {f(body_h)} (1 : {body_h / head_h:.2f}) · đầu chiếm {head_h / total:.0%} chiều cao"),
            ('A5', (Q['body_cx'] - Q['body_half_bot'] + 4, Q['body_bot'] - 60), f"Thân hình thang: vai {2 * Q['body_half_top']} · đáy {2 * Q['body_half_bot']} · cao {Q['body_bot'] - Q['body_top']} · bo {Q['body_round']}"),
            ('A7', None, 'Không cánh tay – chỉ bàn tay tròn khi cầm đồ'),
        ]),
        ('B. Đầu & mặt', [
            ('B1', (hcx + R - 8, hcy - 40), f"Đầu TRÒN R={f(R)} · tâm ({f(hcx)}, {f(hcy)}) · lệch phải {f(hcx - Q['body_cx'])} so với thân"),
            ('B3', (hcx - Q['ear_dx'] - Q['ear_r'] + 6, hcy + Q['ear_dy']), f"Tai r={f(Q['ear_r'])} · lòng r={f(Q['ear_in_r'])} · cách tâm {f(Q['ear_dx'])}, thấp {f(Q['ear_dy'])}"),
            ('B4', (hcx - 6, top + 14), f"Chỏm lông 3 mũi · đỉnh cao hơn tâm đầu {f(hcy - top)}"),
            ('B5', (hcx + R * 0.7, Q['band_y'] + Q['band_h'] / 2), f"Kim cô dày {f(Q['band_h'])}, cao hơn tâm {f(-Q['band_dy'])} · 3 nút r={'/'.join(f(r) for r in Q['stud_r'])}"),
            ('B6', (hcx + 40, hcy + Q['face_chin'][1] + Q['face_chin'][3] - 8), f"Mặt nạ: 2 thùy r={f(Q['face_lobe_r'])} + cằm {f(2 * Q['face_chin'][2])}×{f(2 * Q['face_chin'][3])}"),
            ('B7', (ex - Q['eye_rx'], ey), f"Mắt đen bầu dục {f(2 * Q['eye_rx'])}×{f(2 * Q['eye_ry'])} · 2 đốm sáng · cách giữa {f(Q['eye_dx'])}"),
            ('B8', (hcx + Q['eye_dx'] + Q['brow_w'] / 2, ey + Q['brow_dy']), f"Lông mày cung nhướn: dài {f(Q['brow_w'])} · cong {f(Q['brow_arc'])} · dày {f(Q['brow_t'])}"),
            ('B9', (hcx + Q['mouth_w'] / 2, hcy + Q['mouth_dy'] + 4), f"Miệng cười mở {f(Q['mouth_w'])}×{f(Q['mouth_h'])} có lưỡi · mũi 2 chấm"),
            ('B10', (hcx - Q['blush_dx'] - Q['blush_rx'], hcy + Q['blush_dy']), f"Má hồng {f(2 * Q['blush_rx'])}×{f(2 * Q['blush_ry'])} · {Q['c_blush']}"),
        ]),
        ('C. Trang phục', [
            ('C1', (Q['body_cx'] + 70, 610), f"Áo {Q['c_robe']} · mảng tối {Q['c_robe_dk']}"),
            ('C2', (Q['collar_A'][0][0] + 12, Q['collar_A'][0][1] + 30), f"Cổ áo chéo rộng {Q['collar_w']} · {Q['c_collar']}"),
            ('C3', (Q['body_cx'] + Q['knot_dx'] - Q['knot_r'], Q['belt_y'] + 10), f"Thắt lưng y={Q['belt_y']} cao {Q['belt_h']} · nút r={Q['knot_r']} · {Q['c_belt']}"),
            ('C4', (Q['body_cx'] - 80, Q['hem_y'] + 6), f"Gấu áo y={Q['hem_y']} · {Q['hem_teeth']} răng sâu {Q['hem_depth']}"),
            ('C5', (Q['body_cx'] + 60, Q['body_bot'] - 18), f"Quần {Q['c_pants']} · lộ {Q['body_bot'] - Q['hem_y']}px"),
        ]),
        ('D. Tay · đuôi · gậy', [
            ('D1', (Q['hand'][0] + Q['hand_r'], Q['hand'][1]), f"Bàn tay r={Q['hand_r']} tại {Q['hand']} · cách thân {f(gap)}"),
            ('D3', (Q['tail_curl']['c'][0] - Q['tail_curl']['r0'], Q['tail_curl']['c'][1]), f"Đuôi dày {Q['tail_thick']} · cuộn {Q['tail_curl']['turns']} vòng"),
            ('D4', (t0[0] - 6, t0[1] + 30), f"Gậy dài {f(math.hypot(t1[0] - t0[0], t1[1] - t0[1]))} · nghiêng {ang:.0f}° · dày {2 * Q['staff_half']} · đầu vàng {Q['staff_cap']}"),
        ]),
    ]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    cv = draw(P)
    img = cv.save(os.path.join(OUT, 'ngo-khong.png'))
    guides(img, P).save(os.path.join(OUT, 'ngo-khong-chi-so.png'))
    sheet(img, chi_so(P), 'Tôn Ngộ Không – chỉ số', os.path.join(OUT, 'ngo-khong-bang.png'),
          note='Góp ý theo mã, vd "B7 mắt to lên 22". Khung 800×1000, gốc trên-trái.')
    print('xong:', OUT)
