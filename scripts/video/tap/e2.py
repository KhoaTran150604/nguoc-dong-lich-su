"""Tập E2 – Bạch Đằng 938. Kịch bản: docs/long/E2-bach-dang-938.md · lời đọc: docs/videos/E2-loi-doc.txt
Dữ kiện: kb/E2-bach-dang-938.md. Bản đồ, chân dung, trang phục, vị trí Hải Môn và bãi cọc là MINH HỌA.
"""
import math
import os
from dung import (W, H, U, TA, DICH, GIAN, DONG2, KEM, MUC, DO, seg, lerp, ease, L, NV, ROOT, soldiers, bg_anh, subscribe_card,
                  bg_tran, bg_vung, bg_den, dim, flag, small_flags, clash, xmark, glow, tint, link, quote, clock, logo_card, saban)
import bando_tran as BT
from bando_vung import BanDoVung, lerp_cam

DEPS = (BT.__file__,)
TAIL = 7.0          # giữ cảnh cuối cho màn hình đăng ký kênh
FADE = {'s05': (0, 0.4), 's53': (0, 0.8), 's55': (0.5, 0)}
BANNER = os.path.join(ROOT, 'assets', 'brand', 'song-tu', 'BANNER-YouTube-2560x1440.png')
AVATAR = os.path.join(ROOT, 'assets', 'brand', 'song-tu', 'AVATAR-YouTube-800x800.png')

# ---------------- Bản đồ vùng của tập (dùng chung style series) ----------------
DAILA, AICHAU, DUONGLAM, COLOA = (105.85, 21.03), (105.75, 19.85), (105.45, 21.2), (105.88, 21.13)
QCHAU, HAIMON, BACHDANG = (113.26, 23.13), (112.3, 21.95), (106.85, 20.85)
VUNG = dict(bbox=(101.0, 16.5, 118.0, 26.0), seed=3,
    vung=[dict(poly=[(102, 23.4), (104.6, 23.1), (106.6, 22.6), (108.0, 21.6), (108.2, 17.5), (102, 17.5)], mau='#D9B44A', ten='GIAO CHÂU', o=(103.9, 22.25), co=72),
          dict(poly=[(108.3, 21.7), (106.9, 22.9), (105.6, 24.0), (107.3, 25.3), (110.3, 26.0), (113.6, 25.6), (116.0, 24.7), (117.4, 23.9), (117.4, 21), (111.6, 17.6), (108.4, 17.6)],
               mau='#B5503A', ten='NAM HÁN', o=(111.6, 24.5), co=110)],
    song=[[(103.6, 22.6), (104.6, 21.9), (105.3, 21.3), (105.9, 20.9), (106.5, 20.3)], [(106.2, 21.6), (106.5, 21.2), (106.85, 20.85)]],
    diadanh=[dict(ten='Đại La', o=DAILA, loai='thanh'), dict(ten='Cổ Loa', o=COLOA, loai='cham', co=40, lech=(0.55, 0.42)),
             dict(ten='Ái Châu', o=AICHAU, loai='cham'), dict(ten='Đường Lâm', o=DUONGLAM, loai='cham', co=40, lech=(-0.55, 0.32)),
             dict(ten='Quảng Châu', o=QCHAU, loai='kinh'), dict(ten='Hải Môn', o=HAIMON, loai='cham'),
             dict(ten='Bạch Đằng', o=(107.1, 20.65), loai='chu', co=42)],
    bien=[dict(ten='BIỂN ĐÔNG', o=(112.5, 19.0), co=110)])
M = BanDoVung(VUNG)
CAM_ALL, CAM_GIAO, CAM_HM = (109.3, 21.6, 14.5), (105.9, 20.7, 5.5), (112.6, 22.6, 5.5)
def P(pt, cam): return M.to_screen(pt[0], pt[1], W, H, cam)
def DAT(cam): return lambda x, y: M.is_land(x, y, W, H, cam)      # lính chỉ đứng trên đất liền
def V(cam): return bg_vung(M, cam)
def go(a, b, u): return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
def along(pts, u): return L.path_at(pts, u)
SEA_ROUTE = [(112.6, 21.7), (111.2, 21.2), (110.7, 20.6), (110.1, 20.2), (109.2, 20.55), (108.1, 20.85), (107.2, 20.75)]

def fleet_vung(u, cam, n=5, leader=True, op=1.0):
    """Đoàn chiến thuyền Nam Hán trên bản đồ vùng, cờ Hoằng Tháo dẫn đầu."""
    o, top = [], ''
    for j in range(n):
        x, y = P(along(SEA_ROUTE, max(0, u - j * 0.02)), cam); y += ((j % 3) - 1) * 9 * U
        o.append(f'<g opacity="{op:.2f}">{L.boat(x, y, 180, DICH, 0.32)}</g>')
        if leader and j == 0: top = f'<g opacity="{op:.2f}">' + flag('hoang-thao', DICH, x, y - 6 * U, 0.2) + '</g>'
    return ''.join(o) + top

# ---------------- Bản đồ trận (cửa sông) ----------------
RIVER = BT.RIVER
def on_river(u): x, y = L.path_at(RIVER, u); return x * U, y * U
def river_y(x):
    for (x0, y0), (x1, y1) in zip(RIVER, RIVER[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return RIVER[-1][1]
STAKES = [(x, river_y(x) + dy) for x in range(556, 631, 8) for dy in (-14, -7, 0, 7, 14)]

def stakes(vis, ghost=0.0):
    o = []
    for i, (x, y) in enumerate(STAKES):
        a = max(0, min(1, vis * 1.7 - ((i * 7) % 11) * 0.06))
        if a > 0:
            o.append(f'<g opacity="{a:.2f}" transform="translate({x*U:.1f} {y*U:.1f}) scale({U*(0.55+0.45*a):.2f})"><circle r="2.6" fill="#4A2E18" stroke="#1E120A" stroke-width="0.8"/><circle r="1.1" fill="#D6DCE0"/></g>')
            if a < 1: o.append(f'<circle cx="{x*U:.1f}" cy="{y*U:.1f}" r="{(2+7*a)*U:.1f}" fill="none" stroke="#E8F0F2" stroke-width="{0.7*U:.1f}" opacity="{0.8*(1-a):.2f}"/>')
        elif ghost > 0:
            o.append(f'<circle cx="{x*U:.1f}" cy="{y*U:.1f}" r="{2.2*U:.1f}" fill="none" stroke="#E8F0F2" stroke-width="{0.6*U:.1f}" opacity="{ghost:.2f}"/>')
    return ''.join(o)

FLEET = [(0.0, 0, 0), (0.025, -5, 7), (0.025, 6, -6), (0.05, 0, 11), (0.05, 2, -11), (0.075, -4, 3), (0.09, 5, 8)]
def fleet(u, sink=0.0, stuck=0.0, t=0.0, facing=170, leader=True):
    o, top = [], ''
    for j, (lag, dx, dy) in enumerate(FLEET):
        x, y = on_river(min(1.15, u + lag)); x += dx * U; y += dy * U
        jit = math.sin(t * 22 + j) * 1.2 * U * stuck
        s = max(0, min(1, sink * 1.6 - j * 0.1))
        g = f'<g opacity="{1 - 0.85*s:.2f}" transform="translate({jit:.1f} {s*5*U:.1f}) rotate({s*(25 if j%2 else -22):.1f} {x:.1f} {y:.1f})">'
        o.append(g + L.boat(x, y, facing, DICH, 0.34) + '</g>')
        if leader and j == 1: top = g + flag('hoang-thao', DICH, x, y - 6 * U, 0.17) + '</g>'
    return ''.join(o) + top

def light_boats(u, facing=0, op=1.0, leader=True):
    o, top = [], ''
    for j, (lag, dy) in enumerate([(0, -5), (0.02, 6), (0.04, -1)]):
        x, y = on_river(max(-0.1, u - lag)); y += dy * U
        o.append(f'<g opacity="{op:.2f}">{L.boat(x, y, facing, TA, 0.24)}</g>')
        if leader and j == (0 if facing < 90 else 2): top = f'<g opacity="{op:.2f}">' + flag('quan-ta', TA, x, y - 4 * U, 0.13) + '</g>'
    return ''.join(o) + top

def tran(v): return bg_tran(BT, v)

# ======================= 0. MỞ ĐẦU =======================
def s01(tl, d):                       # đồng hồ năm chạy lùi, bản đồ co dần về vùng câu chuyện
    u = seg(tl, 0.2, d - 0.4)
    return V(lerp_cam((108.5, 21.0, 17.0), CAM_ALL, u)) + dim(0.45 * (1 - seg(tl, d - 0.6, d))) + \
        f'<g opacity="{1 - seg(tl, d - 0.5, d):.2f}">' + clock(int(round(lerp(2026, 938, ease(u)))), tl, u) + '</g>'

def s02(tl, d):
    return tran(1) + stakes(0) + fleet(lerp(1.12, 0.98, seg(tl, 0, d)))

def s03(tl, d):                       # sa bàn: cọc ẩn dưới mặt nước, thuyền giặc phía trên
    return bg_den() + saban(1.0, boats=[(0.3 + 0.1 * seg(tl, 0, d), DICH, 0), (0.62 + 0.1 * seg(tl, 0, d), DICH, 0)])

def s04(tl, d):
    c = CAM_ALL; u = seg(tl, 0, d)
    o = V(c) + fleet_vung(lerp(0.55, 0.85, u), c)
    o += flag('luu-cung', DICH, *P(HAIMON, c), 0.26) + glow(*P(HAIMON, c), tl, 40, DO)
    x, y = P(DAILA, c); o += flag('ngo-quyen', TA, x, y, 0.26 * (1 + 0.15 * seg(tl, d * 0.5, d * 0.7)))
    return o

def s05(tl, d):
    x, y = W / 2, H * 0.86
    return V(CAM_GIAO) + dim(0.5) + flag('ngo-quyen', TA, x, y, 0.62 + 0.04 * seg(tl, 0, d))      # bỏ thẻ tên kênh: mạch truyện liền

# ======================= 1. GIAO CHÂU HỖN LOẠN =======================
def s06(tl, d): return V(lerp_cam(CAM_ALL, (108.6, 21.4, 13.0), seg(tl, 0, d)))
def s07(tl, d):
    c = CAM_GIAO; x, y = P(DAILA, c)
    return V(c) + tint(x, y - 20 * U, seg(tl, 0.2, 1.5), 150, '#D9B44A', 0.25) + f'<g opacity="{seg(tl, 0.3, 1.0):.2f}">' + flag('khuc-thua-my', TA, x, y, 0.32, ten='HỌ KHÚC') + '</g>'
def s08(tl, d):
    c = CAM_ALL; x, y = P(QCHAU, c)
    return V(c) + glow(x, y, tl, 60, DO) + f'<g opacity="{seg(tl, 0.3, 1.0):.2f}">' + flag('luu-cung', DICH, x, y, 0.3, ten='LƯU NHAM') + '</g>'
def s09(tl, d):
    c = CAM_ALL; u = seg(tl, 0, d * 0.45); v = seg(tl, d * 0.55, d)
    o = V(c) + flag('luu-cung', DICH, *P(QCHAU, c), 0.24, ten='LƯU NHAM')
    tg = go(QCHAU, DAILA, u) if v == 0 else go(DAILA, QCHAU, v)
    xd, yd = P(DAILA, c)
    o += tint(xd, yd, seg(tl, d * 0.4, d * 0.7), 90, '#B5503A', 0.35)
    if v == 0: o += flag('khuc-thua-my', TA, xd, yd, 0.24, ten='KHÚC THỪA MỸ')
    else: o += flag('khuc-thua-my', TA, *P(go(DAILA, QCHAU, v * 0.97), c), 0.22, ten='KHÚC THỪA MỸ', grey=0.7, tilt=-12)
    return o + flag('tuong-nam-han', DICH, *P(tg, c), 0.26)
def s10(tl, d):
    c = CAM_GIAO; x, y = P(AICHAU, c)
    return V(c) + glow(x, y, tl, 70) + f'<g opacity="{seg(tl, 0.4, 1.2):.2f}">' + flag('duong-dinh-nghe', TA, x, y, 0.34) + '</g>'
def s11(tl, d):
    c = CAM_GIAO; x, y = P(AICHAU, c)
    return V(c) + soldiers(x, y + 20 * U, 22, TA, tl, r=150, seed=4, appear=(0.2, d * 0.7), ok=DAT(c)) + flag('duong-dinh-nghe', TA, x, y, 0.34)
def s12(tl, d):
    c = CAM_GIAO; u = seg(tl, 0, d * 0.6); r = seg(tl, d * 0.5, d)
    o = V(c) + soldiers(*P(go(AICHAU, DAILA, u), c), 14, TA, tl, r=110, seed=4, appear=(0, 0.01), ok=DAT(c))
    o += flag('tuong-nam-han', DICH, *P(go(DAILA, (106.6, 22.3), r), c), 0.28, ten='LÝ TIẾN', tilt=-14 * r, op=1 - 0.8 * r)
    return o + flag('duong-dinh-nghe', TA, *P(go(AICHAU, (105.85, 20.8), u), c), 0.34)
def s13(tl, d):
    c = CAM_GIAO; u = seg(tl, 0, d * 0.4); xd, yd = P(DAILA, c)
    o = V(c) + flag('duong-dinh-nghe', TA, *P((105.85, 20.8), c), 0.34)
    o += flag('tuong-nam-han', DICH, *P(go((106.7, 22.4), (106.05, 21.25), u), c), 0.3, tilt=80 * seg(tl, d * 0.7, d * 0.9), grey=seg(tl, d * 0.75, d))
    return o + clash(xd + 30 * U, yd - 80 * U, tl - d * 0.4, 0.7)
def s14(tl, d):
    c = CAM_GIAO; x, y = P(DAILA, c); u = seg(tl, 0, d * 0.5)
    return V(c) + tint(x, y - 20 * U, seg(tl, 0.3, d * 0.8), 160, '#D9B44A', 0.3) + flag('duong-dinh-nghe', TA, *P(go((105.85, 20.8), DAILA, u), c), 0.36)
def s15(tl, d):
    c = CAM_GIAO; x, y = P(DAILA, c)
    return V(c) + flag('duong-dinh-nghe', TA, x - 60 * U, y, 0.36) + f'<g opacity="{seg(tl, 0.3, 1.0):.2f}">' + flag('kieu-cong-tien', GIAN, x + 70 * U, y, 0.3) + '</g>'
def s16(tl, d):
    c = CAM_GIAO; x, y = P(DAILA, c); f = seg(tl, d * 0.35, d * 0.6); m = seg(tl, d * 0.6, d)
    return V(c) + flag('duong-dinh-nghe', TA, x - 60 * U, y, 0.36, tilt=80 * f, grey=f) + flag('kieu-cong-tien', GIAN, lerp(x + 70 * U, x, m), y, 0.3 + 0.06 * m)

# ======================= 2. NGƯỜI CON RỂ Ở ÁI CHÂU =======================
def s17(tl, d):
    c = CAM_GIAO; x, y = P(AICHAU, c)
    return V(c) + flag('kieu-cong-tien', GIAN, *P(DAILA, c), 0.36) + glow(x, y, tl, 80) + f'<g opacity="{seg(tl, 0.5, 1.3):.2f}">' + flag('ngo-quyen', TA, x, y, 0.4) + '</g>'
def s18(tl, d):
    c = CAM_GIAO
    return V(c) + glow(*P(DUONGLAM, c), tl, 60) + flag('ngo-quyen', TA, *P(AICHAU, c), 0.4) + flag('kieu-cong-tien', GIAN, *P(DAILA, c), 0.36)
def s19(tl, d):
    return V(CAM_GIAO) + dim(0.55) + flag('ngo-quyen', TA, W / 2, H * 0.93, 0.95 + 0.04 * seg(tl, 0, d))
def s20(tl, d):
    c = CAM_GIAO; a, b = P(AICHAU, c), P(DAILA, c)
    o = V(c) + flag('duong-dinh-nghe', TA, b[0] - 70 * U, b[1], 0.3, op=0.55, grey=0.6)
    o += link(a[0], a[1] - 90 * U, b[0] - 70 * U, b[1] - 80 * U, seg(tl, 0.3, d * 0.6))
    return o + flag('ngo-quyen', TA, *a, 0.4)
def s21(tl, d):
    c = CAM_GIAO; a, b = P(AICHAU, c), P(DAILA, c); br = seg(tl, 0.2, 0.9)
    o = V(c) + link(a[0], a[1] - 90 * U, b[0] - 70 * U, b[1] - 80 * U, 1, broken=br)
    o += flag('duong-dinh-nghe', TA, b[0] - 70 * U, b[1], 0.3, op=0.55, grey=0.6, tilt=80 * br)
    return o + flag('kieu-cong-tien', GIAN, b[0] + 40 * U, b[1], 0.36) + glow(b[0] + 40 * U, b[1] - 60 * U, tl, 70, DO) + flag('ngo-quyen', TA, *a, 0.4)
def s22(tl, d):
    c = CAM_GIAO; u = seg(tl, 0.2, d)
    return V(c) + flag('kieu-cong-tien', GIAN, *P(DAILA, c), 0.36) + soldiers(*P(go(AICHAU, (105.82, 20.55), u), c), 12, TA, tl, r=100, seed=2, appear=(0, 0.01), ok=DAT(c)) + \
        flag('ngo-quyen', TA, *P(go(AICHAU, (105.82, 20.55), u), c), 0.4)

# ======================= 3. NƯỚC CỜ CỦA NAM HÁN =======================
def s23(tl, d):
    c = CAM_ALL; u = seg(tl, 0.2, d * 0.85)
    return V(c) + flag('kieu-cong-tien', GIAN, *P(DAILA, c), 0.26) + flag('luu-cung', DICH, *P(QCHAU, c), 0.26) + flag('su-gia', GIAN, *P(go(DAILA, QCHAU, u), c), 0.2)
def s24(tl, d):
    c = CAM_ALL; x, y = P(QCHAU, c)
    return V(c) + flag('kieu-cong-tien', GIAN, *P(DAILA, c), 0.26) + glow(x, y - 50 * U, tl, 80, DO) + flag('luu-cung', DICH, x, y, 0.34)
def s25(tl, d):
    c = CAM_ALL; x, y = P(QCHAU, c)
    return V(c) + flag('luu-cung', DICH, x - 50 * U, y, 0.32) + f'<g opacity="{seg(tl, 0.3, 1.1):.2f}">' + flag('hoang-thao', DICH, x + 55 * U, y + 10 * U, 0.3 * (0.8 + 0.2 * seg(tl, 0.3, 1.1))) + '</g>'
def s26(tl, d):
    c = CAM_ALL; u = seg(tl, 0.2, d * 0.8)
    return V(c) + flag('hoang-thao', DICH, *P(QCHAU, c), 0.28) + flag('luu-cung', DICH, *P(go(QCHAU, HAIMON, u), c), 0.3)
TIEU_ICH = 'Hiện nay mưa dầm mấy tuần, đường biển hiểm và xa. Ngô Quyền là người kiệt hiệt, chưa thể coi thường. Đại quân nên thận trọng, dùng nhiều người dẫn đường, rồi mới có thể tiến.'
def s27(tl, d):
    c = CAM_ALL; a = seg(tl, d * 0.25, d * 0.35)
    return V(c) + flag('luu-cung', DICH, *P(HAIMON, c), 0.3) + quote(TIEU_ICH, 'Tư trị thông giám, quyển 281', a, ma='tieu-ich', side=DICH)
def s28(tl, d):
    c = CAM_ALL
    return V(c) + flag('luu-cung', DICH, *P(HAIMON, c), 0.26) + fleet_vung(lerp(0.0, 0.45, seg(tl, 0, d)), c)

# ======================= 4. KẾ CỦA NGÔ QUYỀN =======================
def s29(tl, d):
    c = lerp_cam(CAM_ALL, (107.8, 21.2, 9.0), seg(tl, 0, d))
    return V(c) + flag('luu-cung', DICH, *P(HAIMON, c), 0.26) + fleet_vung(0.45 + 0.05 * seg(tl, 0, d), c) + flag('kieu-cong-tien', GIAN, *P(DAILA, c), 0.28)
def s30(tl, d):
    c = CAM_GIAO; x, y = P(DAILA, c); u = seg(tl, 0, d * 0.4)
    o = V(c) + flag('kieu-cong-tien', GIAN, x + 30 * U, y, 0.36, tilt=70 * seg(tl, d * 0.55, d * 0.7), grey=seg(tl, d * 0.55, d * 0.8))
    o += clash(x + 10 * U, y - 90 * U, tl - d * 0.3, 0.6) + xmark(x + 30 * U, y - 70 * U, seg(tl, d * 0.5, d * 0.7))
    return o + flag('ngo-quyen', TA, *P(go((105.82, 20.55), (105.8, 20.95), u), c), 0.42)
NQ1 = 'Hoằng Tháo chỉ là đứa trẻ khờ. Quân từ xa tới, lính tráng mệt mỏi. Lại nghe Công Tiễn đã chết, không có người làm nội ứng, khí thế đã nhụt trước rồi. Ta lấy quân khỏe đợi quân mệt, tất phá được.'
NQ2 = 'Nó lợi vì có thuyền. Không phòng trước thì chưa biết được thua.'
def s31(tl, d): return V(CAM_GIAO) + quote(NQ1, 'Đại Việt sử ký toàn thư (đại ý)', seg(tl, 0.3, 0.9), ma='ngo-quyen')
def s32(tl, d): return V(CAM_GIAO) + quote(NQ2, 'Đại Việt sử ký toàn thư (đại ý)', 1, ma='ngo-quyen')
def s33(tl, d): return bg_den() + saban(0.05, stakes_up=seg(tl, 0.3, d * 0.85))
def s34(tl, d):
    lv = seg(tl, 0.2, d * 0.45) - seg(tl, d * 0.55, d * 0.9)
    return bg_den() + saban(lv)

# ======================= 5. CAO TRÀO =======================
def s35(tl, d):
    v = seg(tl, 0, d * 0.8)
    return tran(0.25 + 0.75 * v) + stakes(1 - v, ghost=0.45 * v) + fleet(1.02)
def s36(tl, d):
    return tran(1) + stakes(0, 0.3) + light_boats(lerp(0.35, 0.74, seg(tl, 0, d)), 0) + fleet(lerp(1.02, 0.94, seg(tl, 0, d)))
def s37(tl, d):
    x, y = on_river(0.82)
    return tran(1) + stakes(0, 0.3) + light_boats(0.78, 0) + fleet(lerp(0.94, 0.88, seg(tl, 0, d))) + clash(x, y - 14 * U, tl - 0.1)
def s38(tl, d):
    u = seg(tl, 0, d)
    return tran(1) + stakes(0, 0.3) + light_boats(lerp(0.78, 0.55, u), 180) + fleet(lerp(0.88, 0.80, u))
def s39(tl, d):
    u = seg(tl, 0, d * 0.9)
    return tran(1) + stakes(0, 0.45) + light_boats(lerp(0.55, 0.22, u), 180) + fleet(lerp(0.80, 0.42, u))
def s40(tl, d):
    return tran(1 - 0.08 * seg(tl, 0, d)) + stakes(0, 0.45) + light_boats(0.22, 180) + fleet(lerp(0.42, 0.40, seg(tl, 0, d)))
def s41(tl, d):
    fall = seg(tl, d * 0.15, d * 0.85)
    return tran(0.92 * (1 - fall)) + stakes(fall, 0.45 * (1 - fall)) + light_boats(0.22, 180) + fleet(lerp(0.40, 0.36, seg(tl, 0, d * 0.6)))
def s42(tl, d):
    u = seg(tl, 0, d)
    o = tran(0) + stakes(1) + fleet(0.36) + light_boats(lerp(0.10, 0.28, u), 0)
    for j, (uu, dy) in enumerate([(0.30, 34), (0.40, -40)]):
        x, y = on_river(lerp(uu - 0.1, uu, u)); o += flag('ngo-quyen' if j == 0 else 'quan-ta', TA, x, y + dy * U, 0.22)
    return o
def s43(tl, d):
    o = tran(0) + stakes(1) + fleet(lerp(0.40, 0.62, seg(tl, 0, d * 0.35)), stuck=seg(tl, d * 0.3, d * 0.4), t=tl, facing=0)
    o += light_boats(lerp(0.30, 0.50, seg(tl, 0, 2.0)), 0)
    for j, (uu, dy) in enumerate([(0.42, 34), (0.52, -40)]):
        x, y = on_river(uu); o += flag('ngo-quyen' if j == 0 else 'quan-ta', TA, x, y + dy * U, 0.22)
    for k, uu in enumerate([0.64, 0.70, 0.75]):
        x, y = on_river(uu); o += clash(x, y - 12 * U, tl - d * 0.25 - d * 0.15 * k)
    return o
def s44(tl, d):
    return tran(0) + stakes(1) + fleet(0.62, sink=seg(tl, 0.2, d * 0.9), stuck=0.4, t=tl, facing=0) + light_boats(0.52, 0)
def s45(tl, d):
    x, y = on_river(0.68); fall = seg(tl, 0.6, 1.8)
    return tran(0) + stakes(1) + fleet(0.62, sink=1, facing=0, leader=False) + light_boats(0.52, 0) + \
        flag('hoang-thao', DICH, x, y - 4 * U, 0.32, tilt=80 * fall, grey=seg(tl, 1.4, 2.6))
def s46(tl, d):
    c = CAM_HM; u = seg(tl, 0.8, d)
    return V(c) + flag('luu-cung', DICH, *P(go(HAIMON, QCHAU, u), c), 0.42, tilt=-15 * seg(tl, 0.2, 0.8), op=1 - 0.5 * seg(tl, d * 0.6, d))

# ======================= 6. VÌ SAO THẮNG =======================
def s47(tl, d):
    w, h, gap = 290 * U, 190 * U, 20 * U; y0 = (H - h) / 2; o = [bg_den()]
    for i, (lv, bx, side) in enumerate([(1, 0.5, DICH), (1, 0.75, DICH), (0, 0.5, DICH)]):
        x0 = (W - 3 * w - 2 * gap) / 2 + i * (w + gap); a = seg(tl, 0.3 + i * d * 0.22, 0.8 + i * d * 0.22)
        o.append(f'<g opacity="{a:.2f}">' + saban(lv, boats=[(bx, side, 12 if lv == 0 else 0)], x0=x0, y0=y0, w=w, h=h) + '</g>')
    return ''.join(o)
def s48(tl, d):
    c = CAM_ALL
    return V(c) + flag('luu-cung', DICH, *P(QCHAU, c), 0.3, grey=0.3) + flag('tieu-ich', DICH, *P((114.3, 23.0), c), 0.26) + glow(*P((114.3, 22.8), c), tl, 50)

# ======================= 7. SAU BẠCH ĐẰNG =======================
def s49(tl, d):
    c = CAM_GIAO; x, y = P(COLOA, c); u = seg(tl, 0, d * 0.5)
    return V(c) + tint(x, y - 20 * U, seg(tl, 0.3, d), 170, '#D9B44A', 0.3) + flag('ngo-quyen', TA, *P(go(DAILA, COLOA, u), c), 0.44)
def s50(tl, d):
    c = CAM_GIAO; x, y = P(COLOA, c)
    return V(c) + tint(x, y - 20 * U, 1, 170, '#D9B44A', 0.3) + small_flags(x, y + 40 * U, 22, TA, tl, r=170, seed=9, appear=(0.1, d * 0.7)) + \
        flag('ngo-quyen', TA, x, y, 0.44)
LVH = 'Tiền Ngô vương … mở đất, xưng vương, khiến người Tầu không dám lại sang, có thể gọi là người mưu giỏi, đánh giỏi, một giận mà yên được muôn dân.'
def s51(tl, d): return V(CAM_GIAO) + quote(LVH, 'Đại Việt sử ký toàn thư – lời bàn của Lê Văn Hưu', seg(tl, 0.2, 0.8))
def s52(tl, d):
    return tran(0) + stakes(1) + f'<g opacity="{seg(tl, 0.3, 1.2):.2f}">' + flag('tran-hung-dao', TA, *on_river(0.5), 0.3) + '</g>'
def s53(tl, d):
    c = lerp_cam(CAM_GIAO, CAM_ALL, seg(tl, 0, d))
    return V(c) + flag('ngo-quyen', TA, *P(COLOA, c), 0.36)

# ======================= 8. KẾT =======================
def s54(tl, d):
    u = seg(tl, 0.2, d)
    return V(lerp_cam(CAM_ALL, (107.0, 21.0, 17.0), u)) + dim(0.45) + clock(int(round(lerp(938, 544, ease(u)))), tl, u)
def s55(tl, d):          # banner kênh + "Lùi tiếp", rồi màn hình đăng ký (7 giây cuối)
    end = 7.0
    if tl < d - end:
        a = seg(tl, 0.2, 0.8)
        return bg_anh(BANNER) + f'<g opacity="{a:.2f}"><rect x="{W/2-190*U:.0f}" y="{H*0.80:.0f}" width="{380*U:.0f}" height="{58*U:.0f}" rx="{29*U:.0f}" fill="{MUC}" stroke="#C9A24A" stroke-width="{3*U:.1f}"/>' \
            f'<text x="{W/2:.0f}" y="{H*0.80+39*U:.0f}" font-family="Be Vietnam Pro SemiBold" font-size="{28*U:.0f}" fill="{DONG2}" text-anchor="middle">LÙI TIẾP: NĂM 544</text></g>'
    return bg_den() + subscribe_card(tl - (d - end), AVATAR)

SCENES = {k: v for k, v in globals().items() if k[:1] == 's' and k[1:].isdigit() and len(k) == 3}

# ---------------- Âm thanh (âm tổng hợp; file thật đặt ở assets/sfx/<tên>.wav sẽ được ưu tiên) ----------------
def SFX(code, d):
    if code == 's01': return [(0.2, 'rut', 0.5, None)]
    if code == 's13': return [(d * 0.4, 'lua', 0.35, d * 0.6), (d * 0.4 + 0.5, 'kiem', 0.8, None), (d * 0.4 + 1.0, 'kiem', 0.6, None), (d * 0.75, 'roi', 0.5, None)]
    if code in ('s16', 's21'): return [(d * 0.4, 'roi', 0.5, None)]
    if code == 's30': return [(d * 0.3, 'lua', 0.3, d * 0.4), (d * 0.3 + 0.5, 'kiem', 0.8, None), (d * 0.6, 'roi', 0.5, None)]
    if code == 's33': return [(0.3 + k * 0.6, 'roi', 0.35, None) for k in range(int((d - 0.6) / 0.6))]
    if code == 's34': return [(0.2, 'rut', 0.6, None), (d * 0.55, 'rut', 0.6, None)]
    if code == 's37': return [(0.1, 'lua', 0.45, d - 0.1), (0.6, 'kiem', 0.9, None), (1.1, 'kiem', 0.7, None), (1.7, 'kiem', 0.8, None)]
    if code == 's41': return [(0.15 * d, 'rut', 0.8, None)]
    if code == 's42': return [(0.2, 'trong_b', 1.0, None)]
    if code == 's43':
        ev = [(d * 0.35, 'roi', 0.5, None)]
        for k in range(3):
            c = d * 0.25 + d * 0.15 * k
            ev += [(c, 'lua', 0.35, d - c), (c + 0.5, 'kiem', 0.8, None), (c + 0.9, 'kiem', 0.6, None)]
        return ev
    if code == 's44': return [(0.3, 'vo_a', 1.0, None), (0.3 + d * 0.35, 'vo_a', 0.8, None)]
    if code == 's45': return [(1.6, 'roi', 0.8, None)]
    if code == 's54': return [(0.2, 'rut', 0.5, None)]
    if code == 's55': return [(0.3, 'trong_a', 0.7, None), (d - 7.0 + 1.05, 'kiem', 0.25, None), (d - 7.0 + 1.65, 'kiem', 0.3, None), (d - 7.0 + 3.3, 'kiem', 0.2, None)]
    return []
