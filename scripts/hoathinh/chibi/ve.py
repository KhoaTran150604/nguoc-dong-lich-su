"""Bộ bút chung cho nhân vật chibi (phong cách: màu phẳng, viền đều, đầu tròn to, thân ống ngắn).

Nguyên tắc vẽ:
- Mỗi BỘ PHẬN = một nhóm hình. Vẽ VIỀN của cả nhóm trước (nét dày 2×viền, đầu nét tròn),
  rồi TÔ MÀU cả nhóm sau → các hình trong nhóm tự liền khối, đường nối bên trong biến mất.
- Vẽ ở độ phân giải ×SS rồi thu nhỏ → nét mịn, không răng cưa.
- Không gradient / blur / glow. Bóng = 1 mảng màu tối phẳng, mép cứng.
"""
import math

from PIL import Image, ImageDraw

SS = 4  # siêu lấy mẫu


def hx(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


class Canvas:
    def __init__(self, w, h, bg='#F6F3EC', ink='#2A211E', line=7):
        self.w, self.h = w, h
        self.ink = hx(ink)
        self.lw = line                       # độ dày viền ở cỡ 1×
        self.img = Image.new('RGBA', (w * SS, h * SS), hx(bg) if bg else (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    # ---- toạ độ ----
    @staticmethod
    def S(pts):
        return [(x * SS, y * SS) for x, y in pts]

    # ---- bộ phận liền khối ----
    def part(self, shapes, fill, line=None, img=None):
        """shapes: list các đa giác (list điểm, toạ độ 1×). Viền ngoài đều, bên trong liền."""
        lw = (self.lw if line is None else line) * SS
        d = ImageDraw.Draw(img) if img is not None else self.d
        fill = hx(fill) if isinstance(fill, str) else fill
        if lw > 0:
            for p in shapes:
                q = self.S(p)
                d.line(q + q[:2], fill=self.ink, width=int(lw * 2), joint='curve')
                r = lw
                for x, y in q:
                    d.ellipse([x - r, y - r, x + r, y + r], fill=self.ink)
        for p in shapes:
            d.polygon(self.S(p), fill=fill)

    def stroke(self, pts, width=None, color=None, img=None):
        """Nét vẽ chi tiết bên trong (lông mày, nếp áo...). Đầu nét tròn."""
        w = (self.lw if width is None else width) * SS
        c = self.ink if color is None else (hx(color) if isinstance(color, str) else color)
        d = ImageDraw.Draw(img) if img is not None else self.d
        q = self.S(pts)
        if len(q) > 1:
            d.line(q, fill=c, width=int(w), joint='curve')
        for x, y in (q[0], q[-1]):
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=c)

    def tube(self, pts, thick, fill):
        """Ống cong (đuôi, tay) có viền: nét mực dày rồi nét màu mảnh hơn."""
        self.stroke(pts, thick + 2 * self.lw)
        self.stroke(pts, thick, fill)

    def dot(self, x, y, r, fill, line=0):
        self.part([circle(x, y, r)], fill, line=line)

    def clip_layer(self, draw_fn, mask_shapes):
        """Vẽ vào lớp riêng rồi chỉ giữ phần nằm trong mask_shapes (vd mặt nằm trong đầu)."""
        lay = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        draw_fn(lay)
        m = Image.new('L', self.img.size, 0)
        md = ImageDraw.Draw(m)
        for p in mask_shapes:
            md.polygon(self.S(p), fill=255)
        lay.putalpha(Image.fromarray(__import__('numpy').minimum(
            __import__('numpy').asarray(lay.split()[3]), __import__('numpy').asarray(m))))
        self.img.alpha_composite(lay)

    def save(self, path, size=None):
        out = self.img.resize((self.w, self.h), Image.LANCZOS)
        if size:
            out = out.resize(size, Image.LANCZOS)
        out.save(path)
        return out


# ---- hình cơ bản (toạ độ 1×) ----
def circle(cx, cy, r, n=96):
    return ellipse(cx, cy, r, r, n)


def ellipse(cx, cy, rx, ry, n=96, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def scallop(cx, cy, rx, ry, arcs, bumps=6, amp=0.06, n=240):
    """Elip có mép lông lượn sóng trên các cung arcs=[(độ_từ, độ_đến)] (0°=phải, 90°=dưới)."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        deg = math.degrees(a) % 360
        k = 1.0
        for a0, a1 in arcs:
            if a0 <= deg <= a1:
                t = (deg - a0) / (a1 - a0)
                k = 1.0 + amp * abs(math.sin(math.pi * t * bumps))
        out.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return out


def rrect(x0, y0, x1, y1, r, n=10):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def trapezoid(cx, y0, y1, half_top, half_bot, r=18, n=8):
    """Thân hình thang bo góc: đỉnh rộng half_top, đáy rộng half_bot."""
    P = [(cx - half_top, y0), (cx + half_top, y0), (cx + half_bot, y1), (cx - half_bot, y1)]
    return round_poly(P, r, n)


def round_poly(P, r, n=8):
    out = []
    m = len(P)
    for i in range(m):
        p0, p1, p2 = P[i - 1], P[i], P[(i + 1) % m]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        rr = min(r, l1 / 2, l2 / 2)
        a = (p1[0] + v1[0] / l1 * rr, p1[1] + v1[1] / l1 * rr)
        b = (p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr)
        for k in range(n + 1):
            t = k / n
            # Bezier bậc 2 a → p1 → b
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * p1[0] + t * t * b[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * p1[1] + t * t * b[1]
            out.append((x, y))
    return out


def bar(p0, p1, half):
    """Hình chữ nhật xoay từ p0 tới p1, nửa bề ngang = half."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * half, dx / L * half
    return [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]


def lerp(p0, p1, t):
    return (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)


def catmull(pts, k=10):
    """Làm mượt chuỗi điểm bằng spline Catmull-Rom (giữ nguyên hai đầu) → cụm bo tròn thay vì nhọn gãy."""
    if len(pts) < 3:
        return list(pts)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out
