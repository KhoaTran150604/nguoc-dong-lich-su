"""Vẽ ITEM CARD pháp bảo Tây Du Ký bằng Bộ Bút (skia) — item độc lập, không cần khung nhân vật.

Phong cách giữ đúng kênh: nét 3 cấp (viền ngoài dày = chot_vien), bóng phẳng cel-shading (bong),
vàng/bạc/đỏ, KHÔNG gradient/blur/glow.

Chạy:
    python scripts/hoathinh/but/phap_bao.py gay_nhu_y            # 1 món → build/thu-hoathinh/phap-bao/
    python scripts/hoathinh/but/phap_bao.py --lo thanhkhi        # lô 4 món Thần khí → ảnh lưới
    python scripts/hoathinh/but/phap_bao.py --tatca              # tất cả món đã có
"""
import argparse
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

from but import (Buc, cong, da_giac, duong, elip, gop, Hinh, hop, mau, net_thuon,  # noqa: E402
                 sang, thanh, toi, tron)

W, H = 520, 540
CX, CY = W / 2, H / 2
VANG = '#F0C23A'      # vàng kim
VANG2 = '#E0A72C'     # vàng đậm
BAC = '#D7DCE2'       # bạc
DO = '#C0453C'        # đỏ son
TIM = '#7E4FA6'       # tím hồ lô
NEN = '#F4EFE3'       # nền thẻ (kem)


def _card(nen=NEN, scale=2.0):
    b = Buc(W, H, nen=nen, D=dict(ngoai=9.0, trong=5.0, ct=3.4), scale=scale)
    return b


def _fill(b, h, col, sx=7, sy=9, hi=0.10, shad=0.13):
    """Tô khối + bóng phẳng (dưới-phải) + vệt sáng (trên-trái), kiểu chuẩn kênh."""
    b.khoi(h, col)
    with b.cat(h):
        b.bong(h, toi(col, shad), sx, sy)
        b.to(h - h.dich(sx * 0.7, sy * 0.7), sang(col, hi))


def _rod(b, p0, p1, wn, col):
    g = thanh(p0, p1, wn, bo=False)
    _fill(b, g, col, sx=wn * 0.5, sy=wn * 0.5)
    return g


def _tia(b, x, y, r, col, n=4, w=4.0):
    """Tia sáng 4 cánh (ánh kim) — nét mảnh, không glow."""
    for i in range(n):
        a = math.pi / 2 * i + math.pi / 4 * (n == 4 and 0)
        dx, dy = math.cos(a) * r, math.sin(a) * r
        b.net([(x - dx, y - dy), (x, y), (x + dx, y + dy)], w, col, thuon=True)


# ═══════════════════════ CÁC PHÁP BẢO ═══════════════════════
def gay_nhu_y(b):
    """Gậy Như Ý: thân đỏ chéo, 2 đầu bịt vàng + vạch đen, hào quang tia."""
    p0, p1 = (150, 452), (372, 96)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    wn = 17
    g = _rod(b, p0, p1, wn, DO)
    for t0, t1 in ((0.0, 0.16), (0.84, 1.0)):      # 2 đầu bịt vàng
        a = (p0[0] + ux * L * t0, p0[1] + uy * L * t0)
        c = (p0[0] + ux * L * t1, p0[1] + uy * L * t1)
        bit = thanh(a, c, wn + 2, bo=False)
        _fill(b, bit, VANG, sx=6, sy=6)
        mid = ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2)
        b.to(thanh((mid[0] - ux * 5, mid[1] - uy * 5), (mid[0] + ux * 5, mid[1] + uy * 5), wn + 6, bo=False), b.muc)


def kim_cang_trac(b):
    """Kim Cang Trác: vòng kim cương vàng, hút binh khí (gậy/đao nhỏ bay vào) + tia sáng."""
    r, ri = 136, 96
    ring = tron(CX, CY, r) - tron(CX, CY, ri)
    # binh khí bị hút vào (vẽ trước, nằm NGOÀI vòng, có vệt hút)
    st = thanh((CX + 208, CY - 170), (CX + 122, CY - 98), 7, bo=True)     # gậy nhỏ
    b.khoi(st, '#C7CBD2', 'ct', dang=False)
    bl = da_giac([(CX - 212, CY + 150), (CX - 150, CY + 92), (CX - 150, CY + 168)])  # lưỡi đao
    b.khoi(bl, '#C7CBD2', 'ct', dang=False)
    for (x0, y0) in ((CX + 150, CY - 128), (CX - 150, CY + 118), (CX + 118, CY + 150), (CX - 118, CY - 140)):
        b.net([(x0, y0), (CX + (x0 - CX) * 0.6, CY + (y0 - CY) * 0.6)], 5.0, toi(VANG, 0.08))  # vệt hút
    _fill(b, ring, VANG, sx=8, sy=9)
    b.khoi(tron(CX, CY, r) - tron(CX, CY, r - 7), VANG2, dang=False)   # viền trong ánh đậm
    _tia(b, CX - 70, CY - 78, 16, sang(VANG, 0.2))


def kim_nhieu(b):
    """Kim Nhiêu (chũm choẹ vàng) úp kín thành cầu + núm trên + đường ghép giữa."""
    cau = tron(CX, CY + 14, 150)
    _fill(b, cau, VANG, sx=9, sy=11, hi=0.12)
    b.to(elip(CX, CY + 14, 150, 18), toi(VANG, 0.16))            # đường ghép 2 mảnh (giữa)
    b.to(elip(CX, CY + 14, 150, 9), VANG2)
    num = hop(CX - 26, CY - 150, CX + 26, CY - 120, 10)          # núm cầm trên
    _fill(b, num, VANG2, sx=5, sy=5)
    b.to(elip(CX - 56, CY - 60, 32, 48, -24), sang(VANG, 0.14))  # vệt sáng cong trên-trái


def ho_lo(b):
    """Hồ Lô Tử Kim: bầu đôi tím, nút vàng, vòng xoáy hút ở miệng."""
    body = cong([(CX, 150, 0), (CX + 58, 180), (CX + 70, 250), (CX + 40, 300),
                 (CX + 96, 360), (CX + 104, 440), (CX + 40, 500), (CX - 40, 500),
                 (CX - 104, 440), (CX - 96, 360), (CX - 40, 300), (CX - 70, 250),
                 (CX - 58, 180)], cang=1.05)
    _fill(b, body, TIM, sx=8, sy=10, hi=0.12)
    b.to(elip(CX, 322, 92, 20), toi(TIM, 0.14))                  # eo thắt giữa
    nut = hop(CX - 34, 110, CX + 34, 156, 12)                    # nút vàng
    _fill(b, nut, VANG, sx=5, sy=6)
    sp = [(CX + 46 * math.cos(i * 0.6) * (1 - i / 22), 128 - 30 + 34 * math.sin(i * 0.6) * (1 - i / 22) - i * 1.1)
          for i in range(16)]
    b.net(sp, 4.5, VANG2)                                        # xoáy hút ở miệng
    b.to(elip(CX - 44, 400, 26, 46, -18), sang(TIM, 0.14))       # vệt sáng bầu dưới


def dinh_ba(b):
    """Cửu Xỉ Đinh Ba: thanh ngang + 9 răng bạc chĩa xuống, 2 khâu vàng, cán bạc."""
    bac = '#D9DEE4'
    _rod(b, (CX, 486), (CX, 198), 11, '#C6CAD1')
    teeth = [cong([(CX - 104 + i * 26 - 7, 198, 0), (CX - 104 + i * 26 + 7, 198, 0),
                   (CX - 104 + i * 26 + 5, 252), (CX - 104 + i * 26, 270, 0),
                   (CX - 104 + i * 26 - 5, 252)]) for i in range(9)]
    rang = gop(*teeth)
    b.khoi(rang, bac, 'trong', dang=False)
    with b.cat(rang):
        b.bong(rang, toi(bac, 0.14), 4, 0)
    bar = thanh((CX - 118, 196), (CX + 118, 196), 15, bo=True)
    _fill(b, bar, bac, sx=0, sy=6)
    for y in (210, 240):
        _fill(b, thanh((CX - 14, y), (CX + 14, y), 14, bo=False), VANG, sx=4, sy=4)
    b.khoi(tron(CX, 486, 12), VANG)


def bao_truong(b):
    """Hàng Yêu Bảo Trượng: mũi giáo + lưỡi liềm trăng bạc, khâu vàng, cán vàng."""
    bac = '#D5DBE1'
    _rod(b, (CX, 500), (CX, 250), 9, '#D1A83C')
    cx, cy, rr = CX, 196, 66
    liem = elip(cx, cy, rr * 1.2, rr * 0.95) - elip(cx, cy - rr * 0.52, rr * 1.12, rr * 0.95)
    _fill(b, liem, bac, sx=5, sy=6)
    mui = cong([(CX, 96, 0), (CX + 16, 150), (CX + 10, 186, 0), (CX - 10, 186, 0), (CX - 16, 150)])
    _fill(b, mui, bac, sx=5, sy=0)
    _fill(b, thanh((CX, 236), (CX, 258), 15, bo=False), VANG, sx=4, sy=4)
    b.khoi(tron(CX, 500, 11), VANG)


def vong_kim_co(b):
    """Vòng Kim Cô: vòng vàng MẢNH + bướu nhỏ phía trước, tia 'chú' quanh vòng."""
    r, ri = 120, 98
    cy = CY + 8
    ring = tron(CX, cy, r) - tron(CX, cy, ri)
    bump = hop(CX - 15, cy - r - 18, CX + 15, cy - r + 8, 8) - tron(CX, cy, ri)
    _fill(b, ring + bump, VANG, sx=6, sy=7)
    for i in range(12):
        a = 2 * math.pi * i / 12
        b.net([(CX + math.cos(a) * (r + 12), cy + math.sin(a) * (r + 12)),
               (CX + math.cos(a) * (r + 26), cy + math.sin(a) * (r + 26))], 3.4, toi(VANG, 0.08))
    _tia(b, CX - 58, cy - 64, 12, sang(VANG, 0.2))


def tinh_binh(b):
    """Tịnh Bình Dương Liễu: bình ngọc, miệng vàng, nhành dương liễu, giọt cam lồ."""
    ngoc, luc = '#D7EBE2', '#4E9C6E'
    body = cong([(CX, 252, 0), (CX + 34, 270), (CX + 60, 332), (CX + 56, 412),
                 (CX + 20, 472), (CX - 20, 472), (CX - 56, 412), (CX - 60, 332), (CX - 34, 270)], cang=1.0)
    vase = body + hop(CX - 18, 198, CX + 18, 264, 8)
    _fill(b, vase, ngoc, sx=7, sy=9, hi=0.14)
    _fill(b, hop(CX - 26, 188, CX + 26, 208, 8), VANG, sx=4, sy=4)
    b.net([(CX + 6, 198), (CX + 40, 150), (CX + 70, 110), (CX + 92, 72)], 5, luc)
    for lx, ly in ((CX + 34, 150), (CX + 56, 120), (CX + 78, 92), (CX + 22, 172)):
        b.khoi(elip(lx, ly, 16, 7, -35), luc, 'ct', dang=False)
    b.khoi(cong([(CX, 500, 0), (CX + 9, 515), (CX, 530, 0), (CX - 9, 515)]), '#BFE0F2', 'ct', dang=False)


def quat_ba_tieu(b):
    """Quạt Ba Tiêu: lá chuối lớn (gân giữa + gân bên) + cán gỗ."""
    luc, luc2, nau = '#4E9C6E', '#397A52', '#9A7328'
    leaf = cong([(CX, 118, 0), (CX + 120, 210), (CX + 150, 342), (CX + 70, 432),
                 (CX, 454, 0), (CX - 70, 432), (CX - 150, 342), (CX - 120, 210)], cang=0.95)
    _fill(b, leaf, luc, sx=8, sy=10, hi=0.12)
    b.net([(CX, 140), (CX, 442)], 6, luc2)
    for s in (1, -1):
        for yy in (212, 272, 332, 392):
            b.net([(CX, yy), (CX + s * 0.58 * (454 - yy), yy - 28)], 3.4, luc2)
    _rod(b, (CX, 452), (CX, 502), 8, nau)


def chieu_yeu_kinh(b):
    """Chiếu Yêu Kính: gương tròn khung vàng, mặt lam, cán vàng, tia soi."""
    lam = '#AFD4E8'
    cy = CY - 24
    frame = tron(CX, cy, 130)
    b.khoi(frame, VANG)
    with b.cat(frame):
        b.bong(frame, toi(VANG, 0.14), 7, 8)
    face = tron(CX, cy, 104)
    b.khoi(face, lam, 'trong', dang=False)
    with b.cat(face):
        b.bong(face, toi(lam, 0.10), 8, 9)
        b.to(face - face.dich(44, 44), sang(lam, 0.12))
    _rod(b, (CX, cy + 118), (CX, cy + 200), 13, VANG)
    _tia(b, CX - 40, cy - 56, 18, '#FFFFFF')


def thap_linh_lung(b):
    """Tháp Linh Lung: tháp vàng nhiều tầng + mái + chóp."""
    data = [(98, 432, 474), (80, 360, 400), (62, 296, 332), (46, 238, 270)]
    body = Hinh()
    for hw, ty, by in data:
        body = body + da_giac([(CX - hw, by), (CX + hw, by), (CX + hw * 0.82, ty), (CX - hw * 0.82, ty)])
    _fill(b, body, VANG, sx=7, sy=9)
    for hw, ty, _ in data:
        _fill(b, da_giac([(CX - hw * 1.18, ty), (CX + hw * 1.18, ty),
                          (CX + hw * 0.5, ty - 26), (CX - hw * 0.5, ty - 26)]), VANG2, sx=4, sy=4)
    _fill(b, cong([(CX, 182, 0), (CX + 15, 232), (CX - 15, 232)]), VANG2, sx=3, sy=3)
    b.khoi(tron(CX, 180, 10), VANG2)
    for hw, ty, by in data:
        b.to(hop(CX - 10, by - 34, CX + 10, by - 6, 6), toi(VANG, 0.3))


def hoang_kim_thang(b):
    """Hoảng Kim Thằng: vòng dây vàng + đuôi dây uốn + nét bện xoắn."""
    cy = CY - 12
    loop = tron(CX, cy, 118) - tron(CX, cy, 96)
    _fill(b, loop, VANG, sx=7, sy=8)
    tail = net_thuon([(CX + 96, cy + 58), (CX + 150, cy + 96), (CX + 156, cy + 158),
                      (CX + 96, cy + 184), (CX + 48, cy + 150), (CX + 78, cy + 112)], 15, 17, 13)
    b.khoi(tail, VANG, 'trong', dang=False)
    with b.cat(tail):
        b.bong(tail, toi(VANG, 0.13), 5, 6)
    for i in range(14):
        a = 2 * math.pi * i / 14
        x, y = CX + math.cos(a) * 107, cy + math.sin(a) * 107
        b.net([(x - 6, y - 7), (x + 6, y + 7)], 2.4, toi(VANG, 0.22))


def tam_muoi(b):
    """Tam Muội Chân Hoả + Hoả Tiêm Thương: giáo gỗ + cụm lửa 3 lớp (đỏ/cam/vàng)."""
    do, cam, vg = '#D23B2A', '#F0892E', '#F6C94A'
    _rod(b, (CX - 118, 476), (CX + 28, 168), 9, '#9A7328')

    def flame(fx, fy, s):
        return cong([(fx, fy - 80 * s, 0), (fx + 30 * s, fy - 20 * s), (fx + 16 * s, fy + 10 * s),
                     (fx + 34 * s, fy + 2 * s), (fx, fy + 40 * s, 0), (fx - 34 * s, fy + 2 * s),
                     (fx - 16 * s, fy + 10 * s), (fx - 30 * s, fy - 20 * s)], cang=1.1)
    _fill(b, flame(CX + 38, CY - 118, 1.6), do, sx=6, sy=6)
    b.khoi(flame(CX + 38, CY - 112, 1.05), cam, 'ct', dang=False)
    b.khoi(flame(CX + 38, CY - 104, 0.58), vg, None, dang=False)
    for fx, fy, fs in ((CX - 34, CY + 42, 0.8), (CX + 92, CY + 8, 0.66)):
        _fill(b, flame(fx, fy, fs), do, sx=4, sy=4)


def nhan_sam(b):
    """Nhân Sâm Quả: quả hình hài nhi treo trên cành lá."""
    kem, luc, nau = '#E6D3A6', '#4E9C6E', '#8A6A24'
    b.net([(CX - 120, 150), (CX + 10, 182), (CX + 122, 150)], 6, nau)
    for lx, ly in ((CX - 82, 148), (CX + 72, 150), (CX + 112, 162)):
        b.khoi(elip(lx, ly, 24, 10, -20), luc, 'ct', dang=False)
    cx, cy = CX, 332
    fruit = gop(tron(cx, cy - 70, 40), elip(cx, cy + 10, 54, 80),
                thanh((cx - 54, cy - 8), (cx + 54, cy - 8), 16, bo=True),
                thanh((cx - 20, cy + 78), (cx - 26, cy + 132), 15, bo=True),
                thanh((cx + 20, cy + 78), (cx + 26, cy + 132), 15, bo=True))
    b.net([(cx, cy - 108), (cx, 184)], 5, nau)
    _fill(b, fruit, kem, sx=7, sy=9, hi=0.1)
    b.khoi(tron(cx - 13, cy - 74, 4), b.muc, None, dang=False)
    b.khoi(tron(cx + 13, cy - 74, 4), b.muc, None, dang=False)
    b.net([(cx - 8, cy - 58), (cx, cy - 54), (cx + 8, cy - 58)], 3, toi(kem, 0.3))


def ca_sa(b):
    """Cẩm Lan Cà Sa: áo gấm đỏ ô vuông vàng + viền vàng + minh châu sáng."""
    do = '#B83A3A'
    robe = cong([(CX - 110, 182, 0), (CX + 110, 182, 0), (CX + 140, 470),
                 (CX + 70, 500), (CX, 476), (CX - 70, 500), (CX - 140, 470)], cang=0.95)
    _fill(b, robe, do, sx=8, sy=10, hi=0.1)
    with b.cat(robe):
        for yy in (250, 320, 390):
            b.net([(CX - 132, yy), (CX + 132, yy)], 4, VANG)
        for xx in (CX - 60, CX, CX + 60):
            b.net([(xx, 192), (xx, 492)], 4, VANG)
    b.khoi(hop(CX - 112, 178, CX + 112, 198, 8), VANG, 'ct', dang=False)
    b.khoi(tron(CX, 224, 16), '#F2E6C2')
    _tia(b, CX, 224, 22, sang(VANG, 0.2))


# ma: (hàm vẽ, 'Tên', điểm, nền-riêng)
ITEMS = {
    'kim_cang_trac': (kim_cang_trac, 'Kim Cang Trác', '9.5', None),
    'gay_nhu_y':     (gay_nhu_y, 'Gậy Như Ý', '9.0', None),
    'kim_nhieu':     (kim_nhieu, 'Kim Nhiêu', '8.5', None),
    'ho_lo':         (ho_lo, 'Hồ Lô Tử Kim', '8.5', None),
    'tinh_binh':     (tinh_binh, 'Tịnh Bình Dương Liễu', '8.0', None),
    'quat_ba_tieu':  (quat_ba_tieu, 'Quạt Ba Tiêu', '8.0', None),
    'vong_kim_co':   (vong_kim_co, 'Vòng Kim Cô', '7.5', None),
    'tam_muoi':      (tam_muoi, 'Tam Muội Chân Hoả', '7.5', None),
    'hoang_kim_thang': (hoang_kim_thang, 'Hoảng Kim Thằng', '7.0', None),
    'nhan_sam':      (nhan_sam, 'Nhân Sâm Quả', '7.0', None),
    'chieu_yeu_kinh': (chieu_yeu_kinh, 'Chiếu Yêu Kính', '6.5', None),
    'dinh_ba':       (dinh_ba, 'Cửu Xỉ Đinh Ba', '6.0', None),
    'thap_linh_lung': (thap_linh_lung, 'Tháp Linh Lung', '6.0', None),
    'bao_truong':    (bao_truong, 'Hàng Yêu Bảo Trượng', '5.0', None),
    'ca_sa':         (ca_sa, 'Cẩm Lan Cà Sa', '4.0', None),
}
XEP = list(ITEMS)   # đã theo thứ tự xếp hạng
LO = {'thanhkhi': ['kim_cang_trac', 'gay_nhu_y', 'kim_nhieu', 'ho_lo']}


def render_one(ma, scale=2.0):
    fn, ten, diem, nen = ITEMS[ma]
    b = _card(nen or NEN, scale)
    fn(b)
    b.chot_vien()
    out = os.path.join(ROOT, 'build', 'thu-hoathinh', 'phap-bao', f'{ma}.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return b.luu(out)


def contact(mas, ra, cols=2):
    from PIL import Image, ImageDraw, ImageFont
    paths = [render_one(m) for m in mas]
    f = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 34)
    fs = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 30)
    cw, ch = Image.open(paths[0]).size
    lab = 56
    rows = (len(mas) + cols - 1) // cols
    out = Image.new('RGB', (cw * cols, (ch + lab) * rows), (255, 255, 255))
    d = ImageDraw.Draw(out)
    for i, (m, p) in enumerate(zip(mas, paths)):
        im = Image.open(p).convert('RGB')
        x, y = (i % cols) * cw, (i // cols) * (ch + lab)
        out.paste(im, (x, y))
        _, ten, diem, _ = ITEMS[m]
        d.text((x + 20, y + ch + 10), ten, font=f, fill=(40, 40, 40))
        d.text((x + cw - 90, y + ch + 12), diem, font=fs, fill=(190, 70, 60))
    out.save(ra)
    return ra


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('ma', nargs='?')
    ap.add_argument('--lo')
    ap.add_argument('--tatca', action='store_true')
    a = ap.parse_args()
    od = os.path.join(ROOT, 'build', 'thu-hoathinh', 'phap-bao')
    os.makedirs(od, exist_ok=True)
    if a.tatca:
        print('lưới:', contact(XEP, os.path.join(od, 'luoi-tatca.png'), cols=3))
    elif a.lo:
        mas = LO.get(a.lo.lower().replace('-', '').replace('_', ''), list(ITEMS))
        print('lưới:', contact(mas, os.path.join(od, f'luoi-{a.lo}.png')))
    elif a.ma:
        print('xong:', render_one(a.ma))
    else:
        print('lưới:', contact(list(ITEMS), os.path.join(od, 'luoi-thanhkhi.png')))
