"""KHUNG CHUNG cho mọi nhân vật chibi – 4 hàm: dau(), than(), ban_tay(), khuon_mat().

Mọi số đo tính theo R = bán kính đầu (ví dụ 0.3 = 0.3×R) → đổi R là cả nhân vật co giãn đúng tỉ lệ.
Phong cách (đo từ ảnh mẫu người dùng gửi 19/11/2026):
- Đầu tròn tuyệt đối, ngồi ngay trên thân, LỆCH PHẢI so với thân (mặt quay 3/4 sang phải).
- Thân "bia mộ": khối chữ nhật hơi loe đáy, bo góc nhỏ, không tay chân.
- Bàn tay = 1 hình tròn tách khỏi thân, chỉ có khi cầm đồ; đồ vật vẽ ĐÈ lên tay.
- Mặt: mắt tròn nhỏ + lông mày ngắn, nằm lệch về phía mặt đang nhìn.
- Viền đều ~0.07R, màu phẳng.
"""
import math

from ve import circle, ellipse, catmull


def rbox(cx, y0, y1, half_top, half_bot, r_top, r_bot, n=10):
    """Hình thang bo góc riêng trên/dưới (thân)."""
    P = [(cx - half_top, y0), (cx + half_top, y0), (cx + half_bot, y1), (cx - half_bot, y1)]
    rs = [r_top, r_top, r_bot, r_bot]
    out = []
    m = len(P)
    for i in range(m):
        p0, p1, p2 = P[i - 1], P[i], P[(i + 1) % m]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        rr = min(rs[i], l1 / 2, l2 / 2)
        a = (p1[0] + v1[0] / l1 * rr, p1[1] + v1[1] / l1 * rr)
        b = (p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr)
        for k in range(n + 1):
            t = k / n
            out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * p1[0] + t * t * b[0],
                        (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * p1[1] + t * t * b[1]))
    return out


class Khung:
    """Toạ độ khung từ tâm đầu + R + tỉ lệ K."""

    def __init__(self, head_c, R, K):
        self.hx, self.hy = head_c
        self.R = R
        self.K = K
        self.bx = self.hx + K['than_lech_x'] * R           # tâm thân (âm = thân nằm bên trái đầu)
        self.top = self.hy + K['than_tren_y'] * R          # mép trên thân
        self.bot = self.top + K['than_cao'] * R
        self.ht = K['than_rong_tren'] * R / 2
        self.hb = K['than_rong_duoi'] * R / 2

    def H(self, dx, dy):
        """Điểm theo đầu: (dx, dy) tính bằng R so với tâm đầu."""
        return (self.hx + dx * self.R, self.hy + dy * self.R)

    def B(self, dx, dy):
        """Điểm theo thân: dx so với tâm thân, dy so với mép trên thân (bằng R)."""
        return (self.bx + dx * self.R, self.top + dy * self.R)

    def half_at(self, y):
        t = (y - self.top) / (self.bot - self.top)
        return self.ht + (self.hb - self.ht) * t


def vien_dau(k, toc=None):
    """Đường viền đầu: KHÔNG phải vòng tròn liền – phần dưới/hai bên là cung tròn,
    phần TRÊN thay bằng các mũi chỏm lông (toc) nên silhouette gồ ghề như lông thật.
    toc = [(dx, dy), ...] trái→phải (toạ độ R so với tâm đầu). Không có toc thì trả vòng tròn."""
    R, hx, hy = k.R, k.hx, k.hy
    if not toc:
        return circle(hx, hy, R, n=200)
    tp = [k.H(dx, dy) for dx, dy in toc]
    aR = math.degrees(math.atan2(tp[-1][1] - hy, tp[-1][0] - hx))   # gốc chỏm bên phải
    aL = math.degrees(math.atan2(tp[0][1] - hy, tp[0][0] - hx))     # gốc chỏm bên trái
    while aL <= aR:
        aL += 360
    arc = []                                                        # cung tròn phần dưới (phải→bụng→trái)
    N = 170
    for i in range(N + 1):
        a = math.radians(aR + (aL - aR) * i / N)
        arc.append((hx + R * math.cos(a), hy + R * math.sin(a)))
    # Làm mượt NHẸ các rãnh nhưng GIỮ ĐỈNH NHỌN: nhân đôi điểm đỉnh (y nhỏ nhất) → spline tạo mũi nhọn
    sharp = []
    for i, pt in enumerate(tp):
        sharp.append(pt)
        if 0 < i < len(tp) - 1 and pt[1] < tp[i - 1][1] and pt[1] < tp[i + 1][1]:
            sharp.append(pt)
    return arc + catmull(sharp, 6)


def dau(cv, k, mau, tai=None, mau_tai_trong=None, ld=5, mau_tai=None, net_tai=None, toc=None):
    """Đầu: tai (sau) + vòng đầu (gồ ghề theo chỏm lông toc). tai = [(dx, dy, r, r_trong), ...] theo R.
    mau_tai = màu vành tai ngoài. net_tai = nét gập '<' trong tai trái. toc = mũi chỏm lông."""
    R = k.R
    ct = mau_tai or mau
    for (dx, dy, r, ri) in (tai or []):
        x, y = k.H(dx, dy)
        cv.part([circle(x, y, r * R)], ct)
        if ri:
            s = 1 if dx > 0 else -1
            cv.part([circle(x + s * 0.03 * R, y, ri * R)], mau_tai_trong, line=ld)
    if net_tai:
        cv.stroke([k.H(*p) for p in net_tai], ld)
    head = vien_dau(k, toc)
    cv.part([head], mau)
    return head


def than(cv, k, mau):
    K = k.K
    body = rbox(k.bx, k.top, k.bot, k.ht, k.hb, K['than_bo_tren'] * k.R, K['than_bo_duoi'] * k.R)
    cv.part([body], mau)
    return body


def ban_tay(cv, k, mau):
    K = k.K
    x, y = k.B(K['tay_x'], K['tay_y'])
    cv.part([circle(x, y, K['tay_r'] * k.R)], mau)
    return (x, y)


def duoi_xoan(cv, k, D, mau, n=120):
    """Đuôi = DẢI XOẮN TRƠN, bề dày đều/thuôn nhẹ, viền đều (vẽ viền cả dải rồi tô → không gãy).
    D: root (gốc, toạ độ thân) · c (tâm xoắn, toạ độ thân) · a0 (độ, góc bắt đầu ở vành ngoài)
       turns (số vòng, >0 = thuận kim đồng hồ) · r0,r1 (bán kính ngoài→trong, R) · w0,w1 (bề dày gốc→chóp, R)."""
    R = k.R
    cx, cy = k.B(*D['c'])
    rx, ry = k.B(*D['root'])
    a0 = math.radians(D['a0'])
    sx, sy = cx + D['r0'] * R * math.cos(a0), cy + D['r0'] * R * math.sin(a0)
    center = [(rx + (sx - rx) * (i / 9), ry + (sy - ry) * (i / 9)) for i in range(9)]   # gốc → đầu xoắn
    for i in range(n + 1):
        t = i / n
        ang = a0 + D['turns'] * 2 * math.pi * t
        r = (D['r0'] * (1 - t) + D['r1'] * t) * R
        center.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    m = len(center)
    left, right = [], []
    for i, (x, y) in enumerate(center):
        a = center[max(i - 1, 0)]
        b = center[min(i + 1, m - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        tt = i / (m - 1)
        hw = (D['w0'] * (1 - tt) + D['w1'] * tt) * R / 2
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    cv.part([left + right[::-1]], mau)
    cv.dot(center[-1][0], center[-1][1], D['w1'] * R / 2, mau)   # bo tròn chóp đuôi
    if D.get('sang'):                                            # nét sáng trong cuộn (nửa trong của đuôi)
        seg = center[int(len(center) * 0.55):]
        cv.stroke(seg, D['w1'] * R * 0.45, color=D['sang'])
    return center


def khuon_mat(cv, k, M, ink):
    """Thứ tự: quầng hồng (dưới) → mắt → lông mày → (miệng nếu có). Mắt kiểu 'oval' có đốm trắng đứng giữa."""
    R = k.R
    # 1) quầng hồng vẽ TRƯỚC (dưới mắt)
    if M.get('ma_hong'):
        for (dx, dy) in M['ma_hong_vt']:
            x, y = k.H(dx, dy)
            cv.part([ellipse(x, y, M['ma_hong'][0] * R, M['ma_hong'][1] * R)], M['mau_ma'], line=0)
    # 2) mắt + lông mày
    for (dx, dy) in M['mat']:
        x, y = k.H(dx, dy)
        if M.get('kieu_mat') == 'oval':          # mắt đen bầu dục đứng + đốm trắng đứng giữa
            rx, ry = M['mat_rx'] * R, M['mat_ry'] * R
            cv.part([ellipse(x, y, rx, ry)], ink, line=0)
            gx, gy = M.get('glint', (0.05, 0.09))
            cv.part([ellipse(x, y, gx * R, gy * R)], '#FFFFFF', line=0)
        else:                                     # mắt trắng + con ngươi
            cv.part([circle(x, y, M['mat_r'] * R)], '#FFFFFF', line=M['vien_mat'])
            px, py = x + M['nhin'][0] * R, y + M['nhin'][1] * R
            cv.dot(px, py, M['con_nguoi_r'] * R, ink)
            cv.dot(px + 0.35 * M['con_nguoi_r'] * R, py - 0.4 * M['con_nguoi_r'] * R, 0.35 * M['con_nguoi_r'] * R, '#FFFFFF')
        bx, by = x, y + M['may_y'] * R
        w, a, ng = M['may_rong'] * R, M['may_cong'] * R, M.get('may_nghieng', 0) * R
        s = 1 if dx > 0 else -1          # đầu phía TRONG (gần giữa mặt) hạ xuống = vẻ quyết tâm
        pts = []
        for i in range(11):
            t = i / 10
            yy = by - a * math.sin(math.pi * t) + ng * (t if s < 0 else 1 - t)
            pts.append((bx - w / 2 + w * t, yy))
        cv.stroke(pts, M['may_day'] * R)
    if M.get('mieng'):
        (dx, dy), w, h = M['mieng'], M['mieng_rong'] * R, M['mieng_sau'] * R
        x, y = k.H(dx, dy)
        cv.stroke([(x - w / 2 + w * i / 12, y + h * math.sin(math.pi * i / 12)) for i in range(13)], M['vien_mat'])
